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
    Function, BasicBlock, Instruction, Value, Param, Op, IRType,
    StructType, ListType, ValueType,
)
from optimizer.analysis import LiveInterval, compute_live_intervals


# ── Register definitions ────────────────────────────────────────

# GPR registers (System V AMD64 ABI)
# Caller-saved: rax, rcx, rdx, rsi, rdi, r8-r11
# Callee-saved: rbx, r12-r15
# Reserved: rsp (stack), rbp (frame)

CALLER_SAVED_GPRS = ['rax', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11']
CALLEE_SAVED_GPRS = ['rbx', 'r12', 'r13', 'r14', 'r15']
ALL_GPRS = CALLER_SAVED_GPRS + CALLEE_SAVED_GPRS

# ABI: first 6 integer args in rdi, rsi, rdx, rcx, r8, r9
ARG_REGS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
# ABI: return value in rax
RETURN_REG = 'rax'

# Float registers
ALL_XMMS = [f'xmm{i}' for i in range(16)]
FLOAT_ARG_REGS = [f'xmm{i}' for i in range(8)]  # xmm0-xmm7 for float args
FLOAT_RETURN_REG = 'xmm0'


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
        reg = self.reg_map.get(value.id)
        if reg:
            return reg
        slot = self.spill_map.get(value.id)
        if slot is not None:
            return f'[rbp - {slot}]'
        return '???'


class LinearScanAllocator:
    """Linear scan register allocator.

    Algorithm:
    1. Compute live intervals for all SSA values
    2. Sort intervals by start point
    3. Walk intervals in order, assigning registers greedily
    4. When out of registers, spill the interval ending latest
    5. Handle calling convention (save/restore across calls)
    """

    def __init__(self, func: Function):
        self.func = func
        self.result = RegAllocation()
        self._next_spill_offset = 8  # Start at [rbp-8]
        self._active: list[LiveInterval] = []  # Currently active intervals
        self._free_gprs: list[str] = list(reversed(ALL_GPRS))
        self._free_xmms: list[str] = list(reversed(ALL_XMMS))

    def allocate(self) -> RegAllocation:
        """Run the register allocator."""
        intervals = compute_live_intervals(self.func)
        self.result.intervals = intervals

        # Pre-assign function parameters to ABI registers
        int_arg_idx = 0
        float_arg_idx = 0
        for param in self.func.params:
            if is_float_type(param.type):
                if float_arg_idx < len(FLOAT_ARG_REGS):
                    reg = FLOAT_ARG_REGS[float_arg_idx]
                    self.result.reg_map[param.id] = reg
                    if reg in self._free_xmms:
                        self._free_xmms.remove(reg)
                    float_arg_idx += 1
                else:
                    self._spill(param)
            else:
                if int_arg_idx < len(ARG_REGS):
                    reg = ARG_REGS[int_arg_idx]
                    self.result.reg_map[param.id] = reg
                    if reg in self._free_gprs:
                        self._free_gprs.remove(reg)
                    int_arg_idx += 1
                else:
                    self._spill(param)

        # Process intervals in order of start point
        for interval in intervals:
            # Skip already-assigned params
            if interval.value.id in self.result.reg_map:
                continue

            # Expire old intervals
            self._expire_old_intervals(interval.start)

            # Determine register class
            needs_float = is_float_type(interval.value.type)

            if needs_float:
                if self._free_xmms:
                    reg = self._free_xmms.pop()
                    self._assign(interval, reg)
                else:
                    self._spill_at_interval(interval, is_float=True)
            else:
                if interval.crosses_call:
                    # Prefer callee-saved registers for values live across calls
                    reg = self._pick_callee_saved_gpr()
                    if reg:
                        self._assign(interval, reg)
                    elif self._free_gprs:
                        reg = self._free_gprs.pop()
                        self._assign(interval, reg)
                    else:
                        self._spill_at_interval(interval, is_float=False)
                elif self._free_gprs:
                    reg = self._free_gprs.pop()
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

    def _pick_callee_saved_gpr(self) -> str | None:
        """Pick a free callee-saved GPR, or None if none available."""
        for i, reg in enumerate(self._free_gprs):
            if reg in CALLEE_SAVED_GPRS:
                self._free_gprs.pop(i)
                return reg
        return None

    def _expire_old_intervals(self, current_point: int):
        """Remove intervals that have ended before current_point."""
        still_active = []
        for interval in self._active:
            if interval.end <= current_point:
                # Free the register
                reg = interval.reg
                if reg:
                    if reg.startswith('xmm'):
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
            candidates = [iv for iv in self._active
                          if iv.reg and iv.reg.startswith('xmm')]
        else:
            candidates = [iv for iv in self._active
                          if iv.reg and not iv.reg.startswith('xmm')]

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
