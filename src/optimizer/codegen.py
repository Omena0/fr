"""x86_64 code generator from register-allocated SSA IR.

Emits Intel-syntax assembly compatible with gcc/as. Uses:
- All 14 GPRs for integer values
- All 16 XMM registers for float values
- Direct-pointer struct model with bump allocator
- System V AMD64 ABI for all calls (internal + extern)
"""
from __future__ import annotations
from optimizer.ir import (
    Module, Function, BasicBlock, Instruction, Value, Param,
    Op, IRType, StructType, ListType, SetType, ValueType, _type_name,
)
from optimizer.regalloc import (
    RegAllocation, allocate_registers,
    ARG_REGS, FLOAT_ARG_REGS, RETURN_REG, FLOAT_RETURN_REG,
    CALLEE_SAVED_GPRS, CALLER_SAVED_GPRS, is_float_type,
)


class CodeGen:
    """Emit x86_64 assembly from register-allocated IR."""

    def __init__(self, module: Module, opt_level: int = 2):
        self.module = module
        self.opt_level = opt_level
        self.lines: list[str] = []
        self.string_labels: dict[str, str] = {}
        self.float_labels: dict[float, str] = {}
        self._label_counter = 0
        self._string_counter = 0
        self._float_counter = 0
        # Track extern functions
        self.externs: set[str] = set()
        # Link flags from module
        self.link_flags: list[str] = []

    def _asm_func_name(self, name: str) -> str:
        """Return the assembly label for a user function.

        Renames 'main' to '_fr_main' to avoid collision with the
        C-level main entry point we emit.
        """
        if name == 'main':
            return '_fr_main'
        return name

    def emit(self) -> str:
        """Generate complete assembly for the module."""
        self.lines = []

        self._emit('.intel_syntax noprefix')

        # Collect string and float constants
        self._collect_constants()

        # Emit text section
        self._emit('')
        self._emit('.section .text')
        self._emit('.global main')

        for func in self.module.functions:
            if func.is_extern:
                self.externs.add(func.name)
                continue
            self._emit_function(func)

        # Emit main (entry point)
        entry = self.module.entry_func
        if entry:
            asm_entry = self._asm_func_name(entry)
            self._emit('')
            self._emit('main:')
            self._emit('    push rbp')
            self._emit('    mov rbp, rsp')
            # Initialize bump allocator
            self._emit('    lea rax, [rip + _fr_heap]')
            self._emit('    mov [rip + _fr_heap_ptr], rax')
            # Initialize runtime (exception handling, struct heap)
            self._emit('    call runtime_init')
            self._emit(f'    call {asm_entry}')
            self._emit('    mov edi, eax')
            self._emit('    call exit')

        # Emit rodata
        self._emit_rodata()

        # Emit bss
        self._emit_bss()

        return '\n'.join(self.lines) + '\n'

    def _emit(self, line: str):
        self.lines.append(line)

    def _new_label(self, prefix: str = 'L') -> str:
        self._label_counter += 1
        return f'.{prefix}{self._label_counter}'

    # ── Constants ───────────────────────────────────────────────

    def _collect_constants(self):
        """Pre-scan all functions to collect string and float constants."""
        for func in self.module.functions:
            for block in func.blocks:
                for inst in block.instructions:
                    if inst.op == Op.CONST_STR and inst.imm_str is not None:
                        self._get_string_label(inst.imm_str)
                    if inst.op == Op.CONST_FLOAT and inst.imm_float is not None:
                        self._get_float_label(inst.imm_float)
                    # Also scan for float immediates in arithmetic
                    if inst.imm_float is not None and inst.op != Op.CONST_FLOAT:
                        self._get_float_label(inst.imm_float)

    def _get_string_label(self, s: str) -> str:
        if s not in self.string_labels:
            label = f'.STR{self._string_counter}'
            self._string_counter += 1
            self.string_labels[s] = label
        return self.string_labels[s]

    def _get_float_label(self, f: float) -> str:
        if f not in self.float_labels:
            label = f'.FLOAT{self._float_counter}'
            self._float_counter += 1
            self.float_labels[f] = label
        return self.float_labels[f]

    def _next_label(self) -> int:
        self._label_counter += 1
        return self._label_counter

    def _find_block(self, func: Function, label: str) -> BasicBlock | None:
        """Find a basic block by label within a function."""
        for b in func.blocks:
            if b.label == label:
                return b
        return None

    def _get_fall_through_block(self, func: Function, block: BasicBlock) -> BasicBlock | None:
        """Get the block that follows `block` in the function's block list."""
        blocks = func.blocks
        for i, b in enumerate(blocks):
            if b is block and i + 1 < len(blocks):
                return blocks[i + 1]
        return None

    def _emit_phi_copies(self, func: Function, from_block: BasicBlock,
                         to_block: BasicBlock, alloc: RegAllocation):
        """Emit register copies for PHI nodes when jumping from from_block to to_block.
        
        Uses parallel move resolution to handle cases where one PHI reads
        the old value of another PHI's destination register.
        """
        int_moves: list[tuple[str, str]] = []
        float_moves: list[tuple[str, str]] = []
        for phi in to_block.phi_nodes:
            if phi.result is None:
                continue
            dst = self._loc(phi.result, alloc)
            for operand, pred_block in zip(phi.operands, phi.target_blocks):
                if pred_block is from_block:
                    src = self._loc(operand, alloc)
                    if src != dst:
                        if is_float_type(phi.result.type):
                            float_moves.append((src, dst))
                        else:
                            int_moves.append((src, dst))
                    break
        if int_moves:
            self._emit_parallel_int_moves(int_moves)
        if float_moves:
            self._emit_parallel_float_moves(float_moves)

    # ── Function emission ───────────────────────────────────────

    def _emit_function(self, func: Function):
        """Emit a complete function with prologue, body, epilogue."""
        # Register allocation
        alloc = allocate_registers(func)
        asm_name = self._asm_func_name(func.name)

        # Pre-compute caller-save sets: for each call instruction, determine
        # which caller-saved GPRs hold live values and must be saved/restored.
        self._caller_save_map: dict[int, list[str]] = {}
        self._compute_caller_saves(func, alloc)

        # Compute total frame size upfront (spill slots + callee saves)
        callee_save_size = len(alloc.used_callee_saved) * 8
        total_frame = alloc.frame_size + callee_save_size
        total_frame = (total_frame + 15) & ~15  # 16-byte align

        self._emit('')
        self._emit(f'{asm_name}:')

        # Prologue
        self._emit('    push rbp')
        self._emit('    mov rbp, rsp')
        if total_frame > 0:
            self._emit(f'    sub rsp, {total_frame}')

        # Save callee-saved registers (within the allocated frame)
        save_offset = alloc.frame_size
        for reg in alloc.used_callee_saved:
            save_offset += 8
            self._emit(f'    mov [rbp - {save_offset}], {reg}')

        # Store callee save info for epilogue
        self._current_callee_saves = []
        save_offset = alloc.frame_size
        for reg in alloc.used_callee_saved:
            save_offset += 8
            self._current_callee_saves.append((reg, save_offset))

        # Emit blocks
        for block in func.blocks:
            self._emit_block(func, block, alloc)

        self._emit('')

    # ── Call-site analysis: caller-saved registers ────────────────

    # Ops that emit runtime/library calls
    _CALL_OPS = frozenset({
        Op.CALL, Op.CALL_EXTERN, Op.CALL_BUILTIN,
        Op.PRINT, Op.PRINTLN, Op.INPUT,
        Op.ALLOC_LIST, Op.LIST_GET, Op.LIST_SET,
        Op.LIST_APPEND, Op.LIST_LEN,
        Op.ALLOC_STRUCT, Op.STR_CONCAT, Op.TO_STR,
        Op.TO_BOOL,
        Op.SQRT, Op.SIN, Op.COS, Op.TAN, Op.ABS,
        Op.FLOOR, Op.CEIL, Op.ROUND, Op.POW,
        Op.MIN, Op.MAX,
        Op.TRY_BEGIN, Op.TRY_END, Op.RAISE,
    })

    def _compute_caller_saves(self, func: Function, alloc: RegAllocation):
        """Pre-compute, for each call instruction, which caller-saved GPRs
        hold values that are live across the call and must be pushed/popped."""
        caller_saved_set = frozenset(CALLER_SAVED_GPRS)

        # Build a mapping: value_id → assigned register (only caller-saved)
        val_to_cs_reg: dict[int, str] = {}
        for vid, reg in alloc.reg_map.items():
            if reg in caller_saved_set:
                val_to_cs_reg[vid] = reg

        if not val_to_cs_reg:
            return

        # Number instructions and compute live sets per instruction
        inst_num = 0
        inst_to_num: dict[int, int] = {}  # id(inst) → number
        for block in func.blocks:
            for inst in block.instructions:
                inst_to_num[id(inst)] = inst_num
                inst_num += 1

        # Use the live intervals from the allocation
        intervals = alloc.intervals

        for block in func.blocks:
            for inst in block.instructions:
                if inst.op not in self._CALL_OPS:
                    continue
                cp = inst_to_num.get(id(inst))
                if cp is None:
                    continue

                # Find all caller-saved GPRs that are live across this call
                save_regs = []
                for iv in intervals:
                    if iv.value.id not in val_to_cs_reg:
                        continue
                    # Value must be defined before this call and used after
                    if iv.start < cp and iv.end > cp + 1:
                        reg = val_to_cs_reg[iv.value.id]
                        # Don't save argument registers that are being passed
                        # to this call (they're already set up)
                        if reg not in save_regs:
                            save_regs.append(reg)

                if save_regs:
                    self._caller_save_map[id(inst)] = save_regs

    def _get_caller_saves(self, inst: Instruction) -> list[str]:
        """Get the list of caller-saved registers to save for a call instruction."""
        return self._caller_save_map.get(id(inst), [])

    def _emit_block(self, func: Function, block: BasicBlock, alloc: RegAllocation):
        """Emit a basic block."""
        asm_name = self._asm_func_name(func.name)
        self._emit(f'.{asm_name}_{block.label}:')

        for inst in block.instructions:
            # Save/restore caller-saved registers around call instructions
            save_regs = self._get_caller_saves(inst) if inst.op in self._CALL_OPS else []
            for reg in save_regs:
                self._emit(f'    push {reg}')
            self._emit_instruction(func, block, inst, alloc)
            for reg in reversed(save_regs):
                self._emit(f'    pop {reg}')

        # If this block doesn't end with a terminator (falls through to next),
        # emit PHI copies for the fall-through successor
        terminator = block.terminator
        if terminator is None:
            fall_through = self._get_fall_through_block(func, block)
            if fall_through and fall_through.phi_nodes:
                self._emit_phi_copies(func, block, fall_through, alloc)

    def _emit_instruction(self, func: Function, block: BasicBlock,
                          inst: Instruction, alloc: RegAllocation):
        """Emit assembly for one IR instruction."""
        op = inst.op

        # ── Constants ──

        if op == Op.CONST_INT:
            dst = self._loc(inst.result, alloc)
            val = inst.imm_int or 0
            if val == 0:
                if dst.startswith('['):
                    self._emit(f'    mov qword ptr {dst}, 0')
                else:
                    self._emit(f'    xor {_dword(dst)}, {_dword(dst)}')
            else:
                self._emit(f'    mov {dst}, {val}')
            return

        if op == Op.CONST_FLOAT:
            dst = self._loc(inst.result, alloc)
            label = self._get_float_label(inst.imm_float)
            if dst.startswith('xmm'):
                self._emit(f'    movsd {dst}, [rip + {label}]')
            else:
                # Float in GPR — move bits
                self._emit(f'    movsd xmm15, [rip + {label}]')
                self._emit(f'    movq {dst}, xmm15')
            return

        if op == Op.CONST_STR:
            dst = self._loc(inst.result, alloc)
            label = self._get_string_label(inst.imm_str or '')
            self._emit(f'    lea {dst}, [rip + {label}]')
            return

        if op == Op.CONST_BOOL:
            dst = self._loc(inst.result, alloc)
            val = inst.imm_int or 0
            if val == 0:
                self._emit(f'    xor {_dword(dst)}, {_dword(dst)}')
            else:
                self._emit(f'    mov {dst}, 1')
            return

        # ── Integer arithmetic ──

        if op == Op.ADD:
            self._emit_binop(inst, alloc, 'add')
            return
        if op == Op.SUB:
            self._emit_binop(inst, alloc, 'sub')
            return
        if op == Op.MUL:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            b = self._loc(inst.operands[1], alloc)
            if dst.startswith('['):
                # Spilled destination — use r11 as temp
                self._emit(f'    mov r11, {a}')
                self._emit(f'    imul r11, {b}')
                self._emit(f'    mov {dst}, r11')
            elif dst == b and dst != a:
                # dst already holds b; imul is commutative
                self._emit(f'    imul {dst}, {a}')
            else:
                if dst != a:
                    self._emit(f'    mov {dst}, {a}')
                self._emit(f'    imul {dst}, {b}')
            return
        if op == Op.DIV:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            b = self._loc(inst.operands[1], alloc)
            self._emit(f'    mov rax, {a}')
            self._emit(f'    cqo')
            # Can't idiv by memory with just register
            if b.startswith('['):
                self._emit(f'    mov r11, {b}')
                self._emit(f'    idiv r11')
            else:
                if b == 'rax' or b == 'rdx':
                    self._emit(f'    mov r11, {b}')
                    self._emit(f'    idiv r11')
                else:
                    self._emit(f'    idiv {b}')
            if dst != 'rax':
                self._emit(f'    mov {dst}, rax')
            return
        if op == Op.MOD:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            b = self._loc(inst.operands[1], alloc)
            self._emit(f'    mov rax, {a}')
            self._emit(f'    cqo')
            if b.startswith('[') or b in ('rax', 'rdx'):
                self._emit(f'    mov r11, {b}')
                self._emit(f'    idiv r11')
            else:
                self._emit(f'    idiv {b}')
            if dst != 'rdx':
                self._emit(f'    mov {dst}, rdx')
            return
        if op == Op.NEG:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            if dst != a:
                self._emit(f'    mov {dst}, {a}')
            self._emit(f'    neg {dst}')
            return

        # ── Float arithmetic ──

        if op == Op.FADD:
            self._emit_float_binop(inst, alloc, 'addsd')
            return
        if op == Op.FSUB:
            self._emit_float_binop(inst, alloc, 'subsd')
            return
        if op == Op.FMUL:
            self._emit_float_binop(inst, alloc, 'mulsd')
            return
        if op == Op.FDIV:
            # Check for division by zero — raise exception if divisor is 0.0
            b = self._loc(inst.operands[1], alloc)
            skip_label = self._new_label('fdiv_ok')
            self._emit(f'    xorpd xmm15, xmm15')
            if b.startswith('xmm'):
                self._emit(f'    ucomisd {b}, xmm15')
            else:
                self._emit(f'    movq xmm14, {b}')
                self._emit(f'    ucomisd xmm14, xmm15')
            self._emit(f'    jne {skip_label}')
            # Divisor is zero — raise ZeroDivisionError
            zdstr = self._get_string_label('ZeroDivisionError')
            msgstr = self._get_string_label('float division by zero')
            self._emit(f'    lea rdi, [rip + {zdstr}]')
            self._emit(f'    lea rsi, [rip + {msgstr}]')
            self._emit_call_aligned('runtime_exception_raise')
            self._emit(f'{skip_label}:')
            self._emit_float_binop(inst, alloc, 'divsd')
            return
        if op == Op.FNEG:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            # Negate float: xor with sign bit mask
            sign_label = self._get_float_label(-0.0)  # This actually gets the sign mask
            self._emit(f'    movsd {dst}, {a}')
            # XOR with sign bit
            self._emit(f'    mov r11, 0x8000000000000000')
            self._emit(f'    movq xmm15, r11')
            self._emit(f'    xorpd {dst}, xmm15')
            return

        # ── Shift / Bitwise ──

        if op == Op.SHL:
            self._emit_shift(inst, alloc, 'shl')
            return
        if op == Op.SHR:
            self._emit_shift(inst, alloc, 'sar')
            return
        if op == Op.BIT_AND:
            self._emit_binop(inst, alloc, 'and')
            return
        if op == Op.BIT_OR:
            self._emit_binop(inst, alloc, 'or')
            return
        if op == Op.BIT_XOR:
            self._emit_binop(inst, alloc, 'xor')
            return

        # ── Comparison ──

        if op in (Op.LT, Op.GT, Op.LE, Op.GE, Op.EQ, Op.NE):
            self._emit_compare(inst, alloc)
            return

        # ── Logic ──

        if op == Op.AND:
            self._emit_binop(inst, alloc, 'and')
            return
        if op == Op.OR:
            self._emit_binop(inst, alloc, 'or')
            return
        if op == Op.NOT:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            self._emit(f'    test {a}, {a}')
            self._emit(f'    setz al')
            self._emit(f'    movzx {dst}, al')
            return

        # ── String ──

        if op == Op.STR_CONCAT:
            self._emit_runtime_call('runtime_str_concat', inst, alloc, 2)
            return

        # ── Type conversion ──

        if op == Op.INT_TO_FLOAT:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            if a.startswith('xmm'):
                # Already a float — just move
                if dst != a:
                    if dst.startswith('xmm'):
                        self._emit(f'    movsd {dst}, {a}')
                    else:
                        self._emit(f'    movq {dst}, {a}')
            elif dst.startswith('xmm'):
                self._emit(f'    cvtsi2sd {dst}, {a}')
            else:
                self._emit(f'    cvtsi2sd xmm15, {a}')
                self._emit(f'    movq {dst}, xmm15')
            return

        if op == Op.FLOAT_TO_INT:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            if a.startswith('xmm'):
                self._emit(f'    cvttsd2si {dst}, {a}')
            else:
                self._emit(f'    movq xmm15, {a}')
                self._emit(f'    cvttsd2si {dst}, xmm15')
            return

        if op == Op.TO_STR:
            a = self._loc(inst.operands[0], alloc)
            a_type = inst.operands[0].type if inst.operands else IRType.INT64
            if isinstance(a_type, ListType):
                self._emit_runtime_call('runtime_list_to_str', inst, alloc, 1)
            elif isinstance(a_type, SetType):
                self._emit_runtime_call('runtime_set_to_str', inst, alloc, 1)
            elif a_type == IRType.FLOAT64:
                self._emit_runtime_call('runtime_float_to_str', inst, alloc, 1, float_args=[0])
            elif a_type == IRType.BOOL:
                self._emit_runtime_call('runtime_bool_to_str', inst, alloc, 1)
            elif a_type == IRType.STRING:
                # Already a string, just copy
                dst = self._loc(inst.result, alloc)
                if dst != a:
                    self._emit(f'    mov {dst}, {a}')
            else:
                self._emit_runtime_call('runtime_int_to_str', inst, alloc, 1)
            return

        if op == Op.TO_BOOL:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            self._emit(f'    test {a}, {a}')
            dst_byte = _byte(dst)
            self._emit(f'    setne {dst_byte}')
            self._emit(f'    movzx {dst}, {dst_byte}')
            return

        # ── Struct operations (direct pointer model) ──

        if op == Op.ALLOC_STRUCT:
            self._emit_struct_alloc(inst, alloc)
            return

        if op == Op.LOAD_FIELD:
            dst = self._loc(inst.result, alloc)
            base = self._loc(inst.operands[0], alloc)
            offset = (inst.imm_int or 0) * 8
            if base.startswith('['):
                self._emit(f'    mov r11, {base}')
                base_ref = 'r11'
            else:
                base_ref = base
            if dst.startswith('xmm'):
                self._emit(f'    movsd {dst}, [{base_ref} + {offset}]')
            else:
                self._emit(f'    mov {dst}, [{base_ref} + {offset}]')
            return

        if op == Op.STORE_FIELD:
            base = self._loc(inst.operands[0], alloc)
            val = self._loc(inst.operands[1], alloc) if len(inst.operands) > 1 else '0'
            offset = (inst.imm_int or 0) * 8
            if base.startswith('['):
                self._emit(f'    mov r11, {base}')
                base_ref = 'r11'
            else:
                base_ref = base
            if val.startswith('xmm'):
                self._emit(f'    movsd [{base_ref} + {offset}], {val}')
            else:
                self._emit(f'    mov [{base_ref} + {offset}], {val}')
            return

        # ── List operations ──

        if op == Op.ALLOC_LIST:
            if inst.operands:
                # List with initial elements — allocate array space on stack,
                # store elements, call runtime, then free the space.
                n = len(inst.operands)
                array_size = n * 8
                # Align to 16 bytes
                aligned_size = (array_size + 15) & ~15
                self._emit(f'    sub rsp, {aligned_size}')
                for i, v in enumerate(inst.operands):
                    loc = self._loc(v, alloc)
                    self._emit(f'    mov [rsp + {i * 8}], {loc}')
                self._emit(f'    mov rdi, rsp')
                self._emit(f'    mov rsi, {n}')
                self._emit_call_aligned('runtime_list_from_array')
                self._emit(f'    add rsp, {aligned_size}')
            else:
                self._emit_call_aligned('runtime_list_new')
            dst = self._loc(inst.result, alloc)
            if dst != 'rax':
                self._emit(f'    mov {dst}, rax')
            return

        if op == Op.LIST_APPEND:
            self._emit_runtime_call('runtime_list_append_int', inst, alloc, 2)
            return

        if op == Op.LIST_GET:
            # Check if indexing a string → use runtime_str_get_char
            list_type = inst.operands[0].type if inst.operands else None
            if list_type == IRType.STRING:
                self._emit_runtime_call('runtime_str_get_char', inst, alloc, 2)
            else:
                self._emit_runtime_call('runtime_list_get_int', inst, alloc, 2)
            return

        if op == Op.LIST_SET:
            self._emit_runtime_call('runtime_list_set_int', inst, alloc, 3)
            return

        if op == Op.LIST_LEN:
            self._emit_runtime_call('runtime_list_len', inst, alloc, 1)
            return

        # ── Control flow ──

        if op == Op.JUMP:
            target = inst.imm_str
            asm_name = self._asm_func_name(func.name)
            # Emit PHI copies for target block before jumping
            target_block = self._find_block(func, target)
            if target_block:
                self._emit_phi_copies(func, block, target_block, alloc)
            self._emit(f'    jmp .{asm_name}_{target}')
            return

        if op == Op.BRANCH:
            cond = self._loc(inst.operands[0], alloc)
            self._emit(f'    test {cond}, {cond}')
            # Branch: if false → jump to false label, else fall through to next block
            false_label = inst.imm_str
            asm_name = self._asm_func_name(func.name)
            # We need PHI copies for the false branch (jumped to) and the
            # true branch (fall-through to the next block).
            # For the false branch, emit copies before the jz:
            false_block = self._find_block(func, false_label)
            if false_block and false_block.phi_nodes:
                # Need to emit copies for false branch only when taking that path.
                # Use a trampoline: jump to a copy block, then to target
                tramp_label = f'.{asm_name}_phi_tramp_{self._next_label()}'
                done_label = f'.{asm_name}_phi_done_{self._next_label()}'
                self._emit(f'    jz {tramp_label}')
                # Fall-through (true) path — emit PHI copies for the next block
                true_block = self._get_fall_through_block(func, block)
                if true_block:
                    self._emit_phi_copies(func, block, true_block, alloc)
                self._emit(f'    jmp {done_label}')
                self._emit(f'{tramp_label}:')
                self._emit_phi_copies(func, block, false_block, alloc)
                self._emit(f'    jmp .{asm_name}_{false_label}')
                self._emit(f'{done_label}:')
            else:
                self._emit(f'    jz .{asm_name}_{false_label}')
                # Fall-through (true) path
                true_block = self._get_fall_through_block(func, block)
                if true_block:
                    self._emit_phi_copies(func, block, true_block, alloc)
            return

        if op == Op.RETURN:
            val = self._loc(inst.operands[0], alloc) if inst.operands else 'rax'
            val_type = inst.operands[0].type if inst.operands else IRType.INT64
            if is_float_type(val_type):
                if val != 'xmm0':
                    if val.startswith('xmm'):
                        self._emit(f'    movsd xmm0, {val}')
                    else:
                        self._emit(f'    movq xmm0, {val}')
            else:
                if val != 'rax':
                    self._emit(f'    mov rax, {val}')
            self._emit_epilogue(func, alloc)
            return

        if op == Op.RETURN_VOID:
            self._emit(f'    xor eax, eax')
            self._emit_epilogue(func, alloc)
            return

        # ── Exception handling ──

        if op == Op.TRY_BEGIN:
            exc_type_loc = self._loc(inst.operands[0], alloc)
            asm_name = self._asm_func_name(func.name)
            # Push exception handler
            self._emit(f'    mov rdi, {exc_type_loc}')
            self._emit_call_aligned('runtime_exception_push')
            # Get jump buffer
            self._emit_call_aligned('runtime_exception_get_jump_buffer')
            # Call _setjmp on jump buffer (returns 0 normally, non-zero on longjmp)
            self._emit(f'    mov rdi, rax')
            self._emit_call_aligned('_setjmp')
            # If setjmp returned non-zero → exception caught → jump to except
            self._emit(f'    test eax, eax')
            except_label = inst.imm_str
            self._emit(f'    jnz .{asm_name}_{except_label}')
            # Normal flow falls through to try body
            return

        if op == Op.TRY_END:
            self._emit_call_aligned('runtime_exception_pop')
            return

        if op == Op.RAISE:
            type_loc = self._loc(inst.operands[0], alloc)
            msg_loc = self._loc(inst.operands[1], alloc)
            # Use parallel move resolution in case type is in rsi or msg in rdi
            moves = []
            if type_loc != 'rdi':
                moves.append((type_loc, 'rdi'))
            if msg_loc != 'rsi':
                moves.append((msg_loc, 'rsi'))
            self._emit_parallel_int_moves(moves)
            self._emit_call_aligned('runtime_exception_raise')
            return

        # ── Function calls ──

        if op == Op.CALL:
            self._emit_call(inst, alloc)
            return

        if op == Op.CALL_EXTERN:
            self._emit_extern_call(inst, alloc)
            return

        if op == Op.CALL_BUILTIN:
            self._emit_builtin_call(inst, alloc)
            return

        # ── I/O ──

        if op == Op.PRINT:
            val_type = inst.operands[0].type if inst.operands else IRType.INT64
            if val_type == IRType.STRING:
                self._emit_runtime_call('runtime_print_str', inst, alloc, 1)
            elif val_type == IRType.FLOAT64:
                self._emit_runtime_call('runtime_print_float', inst, alloc, 1, float_args=[0])
            elif val_type == IRType.BOOL:
                # Convert to string "true"/"false" then print
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_bool_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_print_str')
            elif isinstance(val_type, ListType):
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_list_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_print_str')
            elif isinstance(val_type, SetType):
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_set_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_print_str')
            else:
                self._emit_runtime_call('runtime_print_int', inst, alloc, 1)
            return

        if op == Op.PRINTLN:
            val_type = inst.operands[0].type if inst.operands else IRType.INT64
            if val_type == IRType.STRING:
                self._emit_runtime_call('runtime_println_str', inst, alloc, 1)
            elif val_type == IRType.FLOAT64:
                self._emit_runtime_call('runtime_println_float', inst, alloc, 1, float_args=[0])
            elif val_type == IRType.BOOL:
                # Convert to string "true"/"false" then println
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_bool_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_println_str')
            elif isinstance(val_type, ListType):
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_list_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_println_str')
            elif isinstance(val_type, SetType):
                a = self._loc(inst.operands[0], alloc)
                if a != 'rdi':
                    self._emit(f'    mov rdi, {a}')
                self._emit_call_aligned('runtime_set_to_str')
                self._emit(f'    mov rdi, rax')
                self._emit_call_aligned('runtime_println_str')
            else:
                self._emit_runtime_call('runtime_println_int', inst, alloc, 1)
            return

        if op == Op.INPUT:
            self._emit_call_aligned('runtime_input')
            dst = self._loc(inst.result, alloc)
            if dst != 'rax':
                self._emit(f'    mov {dst}, rax')
            return

        # ── Math builtins ──

        if op == Op.SQRT:
            dst = self._loc(inst.result, alloc)
            a = self._loc(inst.operands[0], alloc)
            if a.startswith('xmm'):
                self._emit(f'    sqrtsd {dst}, {a}')
            else:
                self._emit(f'    movq xmm15, {a}')
                self._emit(f'    sqrtsd {dst}, xmm15')
            return

        if op in (Op.SIN, Op.COS, Op.TAN):
            name = {Op.SIN: 'runtime_sin', Op.COS: 'runtime_cos', Op.TAN: 'runtime_tan'}[op]
            self._emit_runtime_call(name, inst, alloc, 1, float_args=[0], float_ret=True)
            return

        if op == Op.ABS:
            self._emit_runtime_call('runtime_abs_int', inst, alloc, 1)
            return

        if op == Op.FLOOR:
            self._emit_runtime_call('runtime_floor', inst, alloc, 1, float_args=[0], float_ret=True)
            return

        if op == Op.CEIL:
            self._emit_runtime_call('runtime_ceil', inst, alloc, 1, float_args=[0], float_ret=True)
            return

        if op == Op.ROUND:
            self._emit_runtime_call('runtime_round', inst, alloc, 1, float_args=[0], float_ret=True)
            return

        if op == Op.POW:
            self._emit_runtime_call('runtime_pow', inst, alloc, 2, float_args=[0, 1], float_ret=True)
            return

        if op == Op.MIN:
            self._emit_runtime_call('runtime_min_int', inst, alloc, 2)
            return

        if op == Op.MAX:
            self._emit_runtime_call('runtime_max_int', inst, alloc, 2)
            return

        # ── Globals ──

        if op == Op.LOAD_GLOBAL:
            dst = self._loc(inst.result, alloc)
            name = inst.imm_str or 'unknown'
            self._emit(f'    mov {dst}, [rip + _fr_global_{name}]')
            self.module.global_vars[name] = IRType.INT64
            return

        if op == Op.STORE_GLOBAL:
            val = self._loc(inst.operands[0], alloc) if inst.operands else '0'
            name = inst.imm_str or 'unknown'
            self._emit(f'    mov [rip + _fr_global_{name}], {val}')
            self.module.global_vars[name] = IRType.INT64
            return

        # ── SELECT (branchless conditional) ──

        if op == Op.SELECT:
            dst = self._loc(inst.result, alloc)
            cond = self._loc(inst.operands[0], alloc)
            true_val = self._loc(inst.operands[1], alloc)
            false_val = self._loc(inst.operands[2], alloc)
            self._emit(f'    mov {dst}, {false_val}')
            self._emit(f'    test {cond}, {cond}')
            self._emit(f'    cmovnz {dst}, {true_val}')
            return

        # ── PHI (resolved during register allocation) ──

        if op == Op.PHI:
            # Phi nodes should be lowered to copies before codegen
            # For now, treat as NOP (copies handled by regalloc)
            return

        if op == Op.NOP or op == Op.COPY:
            return

        # Fallback: unknown op — emit as comment
        self._emit(f'    # unknown op: {inst}')

    # ── Helper emitters ─────────────────────────────────────────

    def _loc(self, value: Value | None, alloc: RegAllocation) -> str:
        """Get the assembly location (register or stack slot) for a value."""
        if value is None:
            return 'rax'
        return alloc.location(value)

    def _emit_binop(self, inst: Instruction, alloc: RegAllocation, mnemonic: str):
        """Emit a binary integer operation: dst = a op b."""
        dst = self._loc(inst.result, alloc)
        a = self._loc(inst.operands[0], alloc)
        b = self._loc(inst.operands[1], alloc)

        if dst == a:
            self._emit(f'    {mnemonic} {dst}, {b}')
        elif dst == b and mnemonic in ('add', 'and', 'or', 'xor'):
            # Commutative — swap
            self._emit(f'    {mnemonic} {dst}, {a}')
        else:
            self._emit(f'    mov {dst}, {a}')
            self._emit(f'    {mnemonic} {dst}, {b}')

    def _emit_float_binop(self, inst: Instruction, alloc: RegAllocation,
                          mnemonic: str):
        """Emit a binary float operation."""
        dst = self._loc(inst.result, alloc)
        a = self._loc(inst.operands[0], alloc)
        b = self._loc(inst.operands[1], alloc)

        # Ensure operands are in XMM registers
        a_xmm = a if a.startswith('xmm') else 'xmm14'
        b_xmm = b if b.startswith('xmm') else 'xmm15'

        if not a.startswith('xmm'):
            self._emit(f'    movq {a_xmm}, {a}')
        if not b.startswith('xmm'):
            self._emit(f'    movq {b_xmm}, {b}')

        if dst.startswith('xmm'):
            if dst != a_xmm:
                self._emit(f'    movsd {dst}, {a_xmm}')
            self._emit(f'    {mnemonic} {dst}, {b_xmm}')
        else:
            self._emit(f'    movsd xmm14, {a_xmm}')
            self._emit(f'    {mnemonic} xmm14, {b_xmm}')
            self._emit(f'    movq {dst}, xmm14')

    def _emit_shift(self, inst: Instruction, alloc: RegAllocation, mnemonic: str):
        """Emit shift operation (needs cl register for variable shifts)."""
        dst = self._loc(inst.result, alloc)
        a = self._loc(inst.operands[0], alloc)
        b = self._loc(inst.operands[1], alloc)

        if dst != a:
            self._emit(f'    mov {dst}, {a}')

        # Check if shift amount is a constant
        from optimizer.passes import _get_const_value
        shift_val = _get_const_value(inst.operands[1]) if len(inst.operands) > 1 else None
        if shift_val is not None:
            self._emit(f'    {mnemonic} {dst}, {shift_val}')
        else:
            # Variable shift needs cl register
            if b != 'rcx':
                self._emit(f'    mov rcx, {b}')
            self._emit(f'    {mnemonic} {dst}, cl')

    def _emit_compare(self, inst: Instruction, alloc: RegAllocation):
        """Emit a comparison operation."""
        dst = self._loc(inst.result, alloc)
        a = self._loc(inst.operands[0], alloc)
        b = self._loc(inst.operands[1], alloc)

        # Check if operands are float
        a_type = inst.operands[0].type if inst.operands else IRType.INT64
        b_type = inst.operands[1].type if len(inst.operands) > 1 else IRType.INT64

        if is_float_type(a_type) or is_float_type(b_type):
            # Float comparison
            a_xmm = a if a.startswith('xmm') else 'xmm14'
            b_xmm = b if b.startswith('xmm') else 'xmm15'
            if not a.startswith('xmm'):
                self._emit(f'    movq {a_xmm}, {a}')
            if not b.startswith('xmm'):
                self._emit(f'    movq {b_xmm}, {b}')
            self._emit(f'    ucomisd {a_xmm}, {b_xmm}')
        else:
            self._emit(f'    cmp {a}, {b}')

        cc_map = {
            Op.LT: 'setl', Op.GT: 'setg',
            Op.LE: 'setle', Op.GE: 'setge',
            Op.EQ: 'sete', Op.NE: 'setne',
        }
        # For float comparisons use unsigned conditions
        if is_float_type(a_type) or is_float_type(b_type):
            cc_map = {
                Op.LT: 'setb', Op.GT: 'seta',
                Op.LE: 'setbe', Op.GE: 'setae',
                Op.EQ: 'sete', Op.NE: 'setne',
            }

        cc = cc_map.get(inst.op, 'sete')
        dst_byte = _byte(dst)
        self._emit(f'    {cc} {dst_byte}')
        self._emit(f'    movzx {dst}, {dst_byte}')

    def _emit_struct_alloc(self, inst: Instruction, alloc: RegAllocation):
        """Emit struct allocation using bump allocator."""
        n_fields = len(inst.operands)
        size = n_fields * 8
        if size == 0:
            size = 8  # Minimum allocation

        dst = self._loc(inst.result, alloc)

        # Bump allocate: ptr = heap_ptr; heap_ptr += size
        self._emit(f'    mov {dst}, [rip + _fr_heap_ptr]')
        self._emit(f'    add qword ptr [rip + _fr_heap_ptr], {size}')

        # Store initial field values
        for i, field_val in enumerate(inst.operands):
            val_loc = self._loc(field_val, alloc)
            offset = i * 8
            if val_loc.startswith('xmm'):
                self._emit(f'    movsd [{dst} + {offset}], {val_loc}')
            elif dst.startswith('['):
                self._emit(f'    mov r11, {dst}')
                self._emit(f'    mov [r11 + {offset}], {val_loc}')
            else:
                self._emit(f'    mov [{dst} + {offset}], {val_loc}')

    def _emit_call(self, inst: Instruction, alloc: RegAllocation):
        """Emit a function call using System V AMD64 ABI."""
        func_name = self._asm_func_name(inst.imm_str)
        args = inst.operands

        # Set up arguments in ABI registers
        int_idx = 0
        float_idx = 0
        for arg in args:
            arg_loc = self._loc(arg, alloc)
            if is_float_type(arg.type):
                target = FLOAT_ARG_REGS[float_idx] if float_idx < len(FLOAT_ARG_REGS) else None
                if target:
                    if arg_loc.startswith('xmm'):
                        if arg_loc != target:
                            self._emit(f'    movsd {target}, {arg_loc}')
                    else:
                        self._emit(f'    movq {target}, {arg_loc}')
                float_idx += 1
            else:
                target = ARG_REGS[int_idx] if int_idx < len(ARG_REGS) else None
                if target:
                    if arg_loc != target:
                        self._emit(f'    mov {target}, {arg_loc}')
                int_idx += 1

        self._emit_call_aligned(func_name)

        # Move return value to destination
        if inst.result:
            dst = self._loc(inst.result, alloc)
            ret_type = inst.result.type
            if is_float_type(ret_type):
                if dst != 'xmm0':
                    if dst.startswith('xmm'):
                        self._emit(f'    movsd {dst}, xmm0')
                    else:
                        self._emit(f'    movq {dst}, xmm0')
            else:
                if dst != 'rax':
                    self._emit(f'    mov {dst}, rax')

    def _emit_extern_call(self, inst: Instruction, alloc: RegAllocation):
        """Emit an external C function call."""
        # Same as _emit_call but tracks the extern
        self.externs.add(inst.imm_str)
        self._emit_call(inst, alloc)

    def _emit_builtin_call(self, inst: Instruction, alloc: RegAllocation):
        """Emit a call to a builtin/runtime function."""
        name = inst.imm_str or ''

        # Map builtin names to runtime functions
        runtime_map = {
            'len': 'runtime_str_len',
            'contains': 'runtime_contains',
            'str_contains': 'runtime_str_contains',
            'raise': 'runtime_exception_raise',
            'fork': 'runtime_fork',
            'join': 'runtime_wait',
            'list_pop': 'runtime_list_pop',
            'list_print': 'runtime_list_to_str',
            'str_eq': 'runtime_str_eq',
            'str_encode': 'runtime_str_encode',
            'str_decode': 'runtime_str_decode',
            'str_strip': 'runtime_str_strip',
            'str_lower': 'runtime_str_lower',
            'str_upper': 'runtime_str_upper',
            'str_split': 'runtime_str_split',
            'str_join': 'runtime_str_join',
            'str_replace': 'runtime_str_replace',
            'str_repeat': 'runtime_str_repeat',
            'assert': 'runtime_assert',
            'exit': 'runtime_exit',
            'sleep': 'runtime_sleep',
            'fopen': 'runtime_fopen',
            'fwrite': 'runtime_fwrite',
            'fread': 'runtime_fread',
            'fclose': 'runtime_fclose',
            'set_new': 'runtime_set_new',
            'set_add': 'runtime_set_add',
            'set_remove': 'runtime_set_remove',
            'set_contains': 'runtime_set_contains',
            'set_len': 'runtime_set_len',
            'set_print': 'runtime_set_to_str',
            'str_to_int': 'runtime_str_to_int',
            'str_to_float': 'runtime_str_to_float',
        }

        rt_name = runtime_map.get(name, f'runtime_{name}')
        n_args = len(inst.operands)

        # Set up args — handle float/int register type mismatches
        for i, arg in enumerate(inst.operands):
            arg_loc = self._loc(arg, alloc)
            if i < len(ARG_REGS):
                target_reg = ARG_REGS[i]
                if arg_loc != target_reg:
                    if arg_loc.startswith('xmm'):
                        self._emit(f'    movq {target_reg}, {arg_loc}')
                    elif target_reg.startswith('xmm'):
                        self._emit(f'    movq {target_reg}, {arg_loc}')
                    else:
                        self._emit(f'    mov {target_reg}, {arg_loc}')

        self._emit_call_aligned(rt_name)

        if inst.result:
            dst = self._loc(inst.result, alloc)
            ret_type = inst.result.type
            if ret_type == IRType.FLOAT64:
                # Float return value comes in xmm0
                if dst != 'xmm0':
                    if dst.startswith('xmm'):
                        self._emit(f'    movsd {dst}, xmm0')
                    else:
                        self._emit(f'    movq {dst}, xmm0')
            elif dst != 'rax':
                if dst.startswith('xmm'):
                    self._emit(f'    movq {dst}, rax')
                else:
                    self._emit(f'    mov {dst}, rax')

    def _emit_runtime_call(self, name: str, inst: Instruction,
                           alloc: RegAllocation, n_args: int,
                           float_args: list[int] | None = None,
                           float_ret: bool = False):
        """Emit a call to a runtime library function."""
        float_args = float_args or []

        # Phase 1: Collect all (source, target) moves for integer args
        int_moves = []
        float_moves = []
        int_idx = 0
        float_idx = 0
        for i in range(min(n_args, len(inst.operands))):
            arg = inst.operands[i]
            arg_loc = self._loc(arg, alloc)
            if i in float_args:
                target = FLOAT_ARG_REGS[float_idx] if float_idx < len(FLOAT_ARG_REGS) else None
                if target and arg_loc != target:
                    float_moves.append((arg_loc, target))
                float_idx += 1
            else:
                target = ARG_REGS[int_idx] if int_idx < len(ARG_REGS) else None
                if target and arg_loc != target:
                    int_moves.append((arg_loc, target))
                int_idx += 1

        # Phase 2: Emit integer moves using parallel move resolution
        self._emit_parallel_int_moves(int_moves)

        # Phase 3: Emit float moves (no conflicts expected between xmm and gpr)
        for src, tgt in float_moves:
            if src.startswith('xmm'):
                self._emit(f'    movsd {tgt}, {src}')
            else:
                self._emit(f'    movq {tgt}, {src}')

        self._emit_call_aligned(name)

        if inst.result:
            dst = self._loc(inst.result, alloc)
            if float_ret:
                if dst != 'xmm0':
                    if dst.startswith('xmm'):
                        self._emit(f'    movsd {dst}, xmm0')
                    else:
                        self._emit(f'    movq {dst}, xmm0')
            else:
                if dst != 'rax':
                    if dst.startswith('xmm'):
                        self._emit(f'    movq {dst}, rax')
                    else:
                        self._emit(f'    mov {dst}, rax')

    def _emit_parallel_int_moves(self, moves: list[tuple[str, str]]):
        """Emit register moves handling conflicts where a target is another move's source."""
        remaining = [(s, d) for s, d in moves if s != d]
        while remaining:
            progress = False
            for i, (src, dst) in enumerate(remaining):
                # Safe to emit if dst is not a source of any other remaining move
                conflict = any(src2 == dst for j, (src2, _) in enumerate(remaining) if j != i)
                if not conflict:
                    self._emit(f'    mov {dst}, {src}')
                    remaining.pop(i)
                    progress = True
                    break
            if not progress:
                # Cycle detected — break with r11 temp
                src, dst = remaining[0]
                self._emit(f'    mov r11, {src}')
                remaining[0] = ('r11', dst)

    def _emit_parallel_float_moves(self, moves: list[tuple[str, str]]):
        """Emit XMM register moves handling conflicts where a target is another move's source."""
        remaining = [(s, d) for s, d in moves if s != d]
        while remaining:
            progress = False
            for i, (src, dst) in enumerate(remaining):
                conflict = any(src2 == dst for j, (src2, _) in enumerate(remaining) if j != i)
                if not conflict:
                    self._emit(f'    movsd {dst}, {src}')
                    remaining.pop(i)
                    progress = True
                    break
            if not progress:
                # Cycle detected — break with xmm15 temp
                src, dst = remaining[0]
                self._emit(f'    movsd xmm15, {src}')
                remaining[0] = ('xmm15', dst)

    def _emit_call_aligned(self, func_name: str):
        """Emit a call with 16-byte stack alignment."""
        label_aligned = self._new_label('aligned')
        label_done = self._new_label('done')
        self._emit(f'    test spl, 0xF')
        self._emit(f'    jz {label_aligned}')
        self._emit(f'    sub rsp, 8')
        self._emit(f'    call {func_name}')
        self._emit(f'    add rsp, 8')
        self._emit(f'    jmp {label_done}')
        self._emit(f'{label_aligned}:')
        self._emit(f'    call {func_name}')
        self._emit(f'{label_done}:')

    def _emit_epilogue(self, func: Function, alloc: RegAllocation):
        """Emit function epilogue: restore callee-saved regs and return."""
        # Restore callee-saved registers
        save_offset = alloc.frame_size
        for reg in alloc.used_callee_saved:
            save_offset += 8
            self._emit(f'    mov {reg}, [rbp - {save_offset}]')

        self._emit('    mov rsp, rbp')
        self._emit('    pop rbp')
        self._emit('    ret')

    # ── Sections ────────────────────────────────────────────────

    def _emit_rodata(self):
        """Emit read-only data section (strings, floats)."""
        self._emit('')
        self._emit('.section .rodata')

        for s, label in self.string_labels.items():
            escaped = s.replace('\\', '\\\\').replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')
            self._emit(f'{label}:')
            self._emit(f'    .asciz "{escaped}"')

        for f, label in self.float_labels.items():
            import struct
            # Emit float as raw bytes to avoid precision issues
            raw = struct.pack('<d', f)
            hex_val = '0x' + raw[::-1].hex()
            self._emit(f'{label}:')
            self._emit(f'    .quad {hex_val}')

    def _emit_bss(self):
        """Emit BSS section (heap, globals)."""
        self._emit('')
        self._emit('.section .bss')

        # Bump allocator heap (16MB)
        self._emit('.globl _fr_heap_ptr')
        self._emit('_fr_heap_ptr:')
        self._emit('    .quad 0')
        self._emit('.globl _fr_heap')
        self._emit('_fr_heap:')
        self._emit('    .space 16777216')

        # Global variables
        for name in self.module.global_vars:
            self._emit(f'_fr_global_{name}:')
            self._emit(f'    .quad 0')

        # Also emit the old-style struct_data for runtime lib compatibility
        self._emit('.globl struct_data')
        self._emit('struct_data:')
        self._emit('    .space 67108864')
        self._emit('.globl struct_heap_base')
        self._emit('struct_heap_base:')
        self._emit('    .quad 0')
        self._emit('.globl struct_heap_ptr')
        self._emit('struct_heap_ptr:')
        self._emit('    .quad 0')
        self._emit('.globl global_vars')
        self._emit('global_vars:')
        self._emit('    .space 2048')


def _dword(reg: str) -> str:
    """Convert 64-bit register to 32-bit for xor zeroing."""
    dword_map = {
        'rax': 'eax', 'rbx': 'ebx', 'rcx': 'ecx', 'rdx': 'edx',
        'rsi': 'esi', 'rdi': 'edi', 'r8': 'r8d', 'r9': 'r9d',
        'r10': 'r10d', 'r11': 'r11d', 'r12': 'r12d', 'r13': 'r13d',
        'r14': 'r14d', 'r15': 'r15d',
    }
    return dword_map.get(reg, reg)


def _byte(reg: str) -> str:
    """Convert 64-bit register to 8-bit low byte for setcc."""
    byte_map = {
        'rax': 'al', 'rbx': 'bl', 'rcx': 'cl', 'rdx': 'dl',
        'rsi': 'sil', 'rdi': 'dil', 'r8': 'r8b', 'r9': 'r9b',
        'r10': 'r10b', 'r11': 'r11b', 'r12': 'r12b', 'r13': 'r13b',
        'r14': 'r14b', 'r15': 'r15b',
    }
    return byte_map.get(reg, 'al')


def generate_asm(module: Module, opt_level: int = 2) -> str:
    """Generate x86_64 assembly from an IR module."""
    gen = CodeGen(module, opt_level)
    return gen.emit()
