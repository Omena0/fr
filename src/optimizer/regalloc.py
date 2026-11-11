"""Linear-scan register allocator for x86_64.

Uses all available registers:
- 14 GPRs: rax, rcx, rdx, rbx, rsi, rdi, r8-r15
  (rsp = stack pointer, rbp = frame pointer — reserved)
- 16 XMMs: xmm0-xmm15 (for float operations)

Assigns registers to SSA values based on live intervals, spilling to stack
when registers are exhausted. Respects the System V AMD64 calling convention.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from optimizer.ir import (
    Function,
    BasicBlock,
    Instruction,
    Value,
    Param,
    Op,
    IRType,
    StructType,
    ListType,
    ValueType,
)
from optimizer.analysis import LiveInterval, compute_live_intervals

# ── Register definitions ────────────────────────────────────────

# GPR registers (System V AMD64 ABI)
# Caller-saved: rax, rcx, rdx, rsi, rdi, r8-r11
# Callee-saved: rbx, r12-r15
# Reserved: rsp (stack), rbp (frame)

CALLER_SAVED_GPRS = ["rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11"]
CALLEE_SAVED_GPRS = ["rbx", "r12", "r13", "r14", "r15"]
ALL_GPRS = CALLER_SAVED_GPRS + CALLEE_SAVED_GPRS

# ABI: first 6 integer args in rdi, rsi, rdx, rcx, r8, r9
ARG_REGS = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
# ABI: return value in rax
RETURN_REG = "rax"

# Float registers
ALL_XMMS = [f"xmm{i}" for i in range(16)]
FLOAT_ARG_REGS = [f"xmm{i}" for i in range(8)]  # xmm0-xmm7 for float args
FLOAT_RETURN_REG = "xmm0"


def is_float_type(t: ValueType) -> bool:
    return t == IRType.FLOAT64


@dataclass
class RegAllocation:
    """Result of register allocation for a function."""

    # Value ID → register name
    reg_map: dict[int, str] = field(default_factory=dict)
    # Value ID → spill slot offset (from rbp)
    spill_map: dict[int, int] = field(default_factory=dict)
    # Total stack frame size
    frame_size: int = 0
    # Which callee-saved registers are used (need save/restore)
    used_callee_saved: list[str] = field(default_factory=list)
    # Live intervals for reference
    intervals: list[LiveInterval] = field(default_factory=list)

    def get_reg(self, value: Value) -> str | None:
        """Get the register assigned to a value."""
        return self.reg_map.get(value.id)

    def get_spill_slot(self, value: Value) -> int | None:
        """Get the spill slot for a value."""
        return self.spill_map.get(value.id)

    def is_spilled(self, value: Value) -> bool:
        return value.id in self.spill_map and value.id not in self.reg_map

    def location(self, value: Value) -> str:
        """Get the location string for a value (register or stack slot)."""
        if reg := self.reg_map.get(value.id):
            return reg
        slot = self.spill_map.get(value.id)
        return f"[rbp - {slot}]" if slot is not None else "???"


class LinearScanAllocator:
    """Linear scan register allocator.

    Algorithm:
    1. Compute live intervals for all SSA values
    2. Sort intervals by start point
    3. Walk intervals in order, assigning registers greedily
    4. When out of registers, spill the interval ending latest
    5. Handle calling convention (save/restore across calls)
    6. Coalesce copy-related values to eliminate move instructions
    """

    def __init__(self, func: Function):
        self.func = func
        self.result = RegAllocation()
        self._next_spill_offset = 0  # Start at 0; only grow if we actually spill
        self._active: list[LiveInterval] = []  # Currently active intervals
        self._free_gprs: list[str] = list(reversed(ALL_GPRS))
        self._free_xmms: list[str] = list(reversed(ALL_XMMS))
        # value_id -> [src value_ids] (ordered list of coalesce candidates)
        self._coalesce_map: dict[int, list[int]] = {}
        self._build_coalesce_map(func)

    def _build_coalesce_map(self, func: Function) -> None:
        """Map copy-dst value IDs to their source value IDs for coalescing.

        Scans all instructions for:
        1. Op.COPY (dst = src) — explicit copy instructions
        2. Binary ops where the first operand has a single use (last-use)
           — dst = op a b, where a is dead after this op, so dst can reuse
           a's register and avoid a move.
        3. PHI nodes — dst = phi(op1 from B1, op2 from B2, ...).
           Coalesce dst with the operand from the fall-through predecessor
           (the block that falls straight into this block), eliminating
           the copy on the most common edge into the PHI block.

        Coalescing eliminates the mov instruction that would otherwise be
        emitted between the source and destination.
        """
        # Build fall-through successor map: block -> block that falls into it
        fall_through_into: dict[int, BasicBlock] = {}
        for i, block in enumerate(func.blocks):
            if i + 1 < len(func.blocks):
                nxt = func.blocks[i + 1]
                term = block.terminator
                if (
                    term is not None
                    and term.op == Op.JUMP
                    and len(term.target_blocks) == 1
                    and term.target_blocks[0] is nxt
                ):
                    fall_through_into[id(nxt)] = block
                elif term is None:
                    fall_through_into[id(nxt)] = block

        for block in func.blocks:
            for inst in block.instructions:
                if not inst.result or not inst.operands:
                    continue
                dst = inst.result

                # Explicit COPY: dst = copy src
                if inst.op == Op.COPY:
                    src = inst.operands[0]
                    if isinstance(src, Value):
                        self._coalesce_map[dst.id] = [src.id]
                    continue

                # Binary ops where operands can be coalesced into dst.
                # For commutative ops, both operands are candidates (a op b == b op a).
                # _resolve_coalesce_reg checks at allocation time whether the
                # source's last use is at the current instruction (safe to steal).
                COMMUTATIVE = {
                    Op.ADD, Op.MUL, Op.AND, Op.OR, Op.BIT_AND, Op.BIT_OR, Op.BIT_XOR,
                    Op.FADD, Op.FMUL,
                }
                if inst.op in COMMUTATIVE | {
                    Op.SUB, Op.DIV, Op.MOD, Op.FSUB, Op.FDIV,
                }:
                    a = inst.operands[0]
                    b = inst.operands[1] if len(inst.operands) > 1 else None
                    candidates: list[int] = []
                    if isinstance(a, Value):
                        candidates.append(a.id)
                    if inst.op in COMMUTATIVE and isinstance(b, Value):
                        candidates.append(b.id)
                    if candidates:
                        self._coalesce_map[dst.id] = candidates

                # PHI node: coalesce result with fall-through operand
                if inst.op == Op.PHI:
                    ft_block = fall_through_into.get(id(block))
                    if ft_block is not None and inst.target_blocks:
                        for operand, pred_block in zip(inst.operands, inst.target_blocks):
                            if pred_block is ft_block and isinstance(operand, Value):
                                self._coalesce_map[dst.id] = [operand.id]
                                break
                    # Fallback: coalesce with first operand
                    if dst.id not in self._coalesce_map and inst.operands:
                        first = inst.operands[0]
                        if isinstance(first, Value):
                            self._coalesce_map[dst.id] = [first.id]

    def allocate(self) -> RegAllocation:
        """Run the register allocator."""
        interval_list = compute_live_intervals(self.func)
        self.result.intervals = interval_list
        # Build value_id -> interval lookup for coalesce resolution
        intervals = {iv.value.id: iv for iv in interval_list}

        # Pre-assign function parameters to ABI registers.
        # Parameter intervals are added to _active so their registers are
        # returned to the free list when they expire (enabling coalescing).
        int_arg_idx = 0
        float_arg_idx = 0
        for param in self.func.params:
            if is_float_type(param.type):
                if float_arg_idx < len(FLOAT_ARG_REGS):
                    reg = FLOAT_ARG_REGS[float_arg_idx]
                    self.result.reg_map[param.id] = reg
                    if reg in self._free_xmms:
                        self._free_xmms.remove(reg)
                    iv = intervals.get(param.id)
                    if iv is not None:
                        iv.reg = reg
                        self._active.append(iv)
                    float_arg_idx += 1
                else:
                    self._spill(param)
            elif int_arg_idx < len(ARG_REGS):
                reg = ARG_REGS[int_arg_idx]
                self.result.reg_map[param.id] = reg
                if reg in self._free_gprs:
                    self._free_gprs.remove(reg)
                iv = intervals.get(param.id)
                if iv is not None:
                    iv.reg = reg
                    self._active.append(iv)
                int_arg_idx += 1
            else:
                self._spill(param)
        self._active.sort(key=lambda iv: iv.end)

        # Process intervals in order of start point
        for interval in interval_list:
            # Skip already-assigned params
            if interval.value.id in self.result.reg_map:
                continue

            # Expire old intervals
            self._expire_old_intervals(interval.start)

            if needs_float := is_float_type(interval.value.type):
                if self._free_xmms:
                    pref_reg = self._resolve_coalesce_reg(interval.value.id, interval.start)
                    reg = self._pick_free_xmm(pref_reg)
                    self._assign(interval, reg)
                else:
                    self._spill_at_interval(interval, is_float=True)
            else:
                forbidden = interval.forbidden_regs
                pref_reg = self._resolve_coalesce_reg(interval.value.id, interval.start)
                if interval.crosses_call and (
                    reg := self._pick_callee_saved_gpr(forbidden, pref_reg)
                ):
                    self._assign(interval, reg)
                elif reg := self._pick_free_gpr(forbidden, pref_reg):
                    self._assign(interval, reg)
                else:
                    self._spill_at_interval(interval, is_float=False)
        # Track which callee-saved registers are used
        for reg in self.result.reg_map.values():
            if reg in CALLEE_SAVED_GPRS and reg not in self.result.used_callee_saved:
                self.result.used_callee_saved.append(reg)

        # Compute final frame size (aligned to 16 bytes)
        self.result.frame_size = (self._next_spill_offset + 15) & ~15

        return self.result

    def _pick_callee_saved_gpr(self, forbidden: set[str] = frozenset(),
                                prefer: str | None = None) -> str | None:
        """Pick a free callee-saved GPR not in forbidden set, or None."""
        if prefer and prefer in CALLEE_SAVED_GPRS and prefer not in forbidden:
            if prefer in self._free_gprs:
                self._free_gprs.remove(prefer)
                return prefer
        for i, reg in enumerate(self._free_gprs):
            if reg in CALLEE_SAVED_GPRS and reg not in forbidden:
                self._free_gprs.pop(i)
                return reg
        return None

    def _pick_free_gpr(self, forbidden: set[str] = frozenset(),
                       prefer: str | None = None) -> str | None:
        """Pick any free GPR not in forbidden set, or None."""
        if prefer and prefer not in forbidden and prefer in self._free_gprs:
            self._free_gprs.remove(prefer)
            return prefer
        for i, reg in enumerate(self._free_gprs):
            if reg not in forbidden:
                self._free_gprs.pop(i)
                return reg
        return None

    def _pick_free_xmm(self, prefer: str | None = None) -> str | None:
        """Pick any free XMM register, or None."""
        if prefer and prefer in self._free_xmms:
            self._free_xmms.remove(prefer)
            return prefer
        return self._free_xmms.pop()

    def _resolve_coalesce_reg(self, value_id: int, current_point: int) -> str | None:
        """Resolve a coalesce preference to a register name, or None.

        Looks up the candidate source value IDs in the coalesce map. Tries each
        candidate in order; returns the first source's register if either:
        - the register is currently free (source interval expired), or
        - the source's last use is at or before current_point (source and
          destination overlap by exactly one instruction point). In this
          case the register is "stolen" from the source: the source interval
          is removed from the active list and its register is returned to
          the free list. This is safe because the destination reads the
          source as an operand within the same instruction, so the read
          happens before the write.
        """
        candidates = self._coalesce_map.get(value_id)
        if not candidates:
            return None
        for src_id in candidates:
            src_reg = self.result.reg_map.get(src_id)
            if src_reg is None:
                continue

            is_xmm = src_reg.startswith("xmm")
            free_list = self._free_xmms if is_xmm else self._free_gprs

            if src_reg in free_list:
                return src_reg

            # Try to steal: source's last use is at current_point
            src_iv = None
            for iv in self.result.intervals:
                if iv.value.id == src_id:
                    src_iv = iv
                    break
            if src_iv is None or src_iv.end > current_point + 1:
                continue

            # Steal the register from the source.
            # Do NOT remove src from reg_map: codegen still needs to locate src
            # (it is read before dst is written within the same instruction).
            # Both src and dst will map to the same register, which is correct.
            self._active = [iv for iv in self._active if iv.value.id != src_id]
            free_list.append(src_reg)
            if src_iv.reg is not None:
                src_iv.reg = None
            return src_reg
        return None

    def _expire_old_intervals(self, current_point: int):
        """Remove intervals that have ended before current_point."""
        still_active = []
        for interval in self._active:
            if interval.end <= current_point:
                if reg := interval.reg:
                    if reg.startswith("xmm"):
                        self._free_xmms.append(reg)
                    else:
                        self._free_gprs.append(reg)
            else:
                still_active.append(interval)
        self._active = still_active

    def _assign(self, interval: LiveInterval, reg: str):
        """Assign a register to an interval."""
        interval.reg = reg
        self.result.reg_map[interval.value.id] = reg
        self._active.append(interval)
        self._active.sort(key=lambda iv: iv.end)

    def _spill(self, value: Value):
        """Assign a spill slot to a value."""
        slot = self._next_spill_offset
        self.result.spill_map[value.id] = slot
        self._next_spill_offset += 8

    def _spill_at_interval(self, interval: LiveInterval, is_float: bool):
        """Spill either the current interval or the one ending latest."""
        # Find the active interval ending latest
        if is_float:
            candidates = [
                iv for iv in self._active if iv.reg and iv.reg.startswith("xmm")
            ]
        else:
            candidates = [
                iv for iv in self._active if iv.reg and not iv.reg.startswith("xmm")
            ]

        if candidates:
            spill_candidate = max(candidates, key=lambda iv: iv.end)
            if spill_candidate.end > interval.end:
                # Spill the longest-lived active interval, use its register for current
                reg = spill_candidate.reg
                self._active.remove(spill_candidate)
                self._spill(spill_candidate.value)
                # Remove from reg_map
                if spill_candidate.value.id in self.result.reg_map:
                    del self.result.reg_map[spill_candidate.value.id]
                self._assign(interval, reg)
                return

        # Spill the current interval
        self._spill(interval.value)


def allocate_registers(func: Function) -> RegAllocation:
    """Run register allocation on a function."""
    allocator = LinearScanAllocator(func)
    return allocator.allocate()
