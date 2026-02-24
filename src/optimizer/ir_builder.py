"""Convert fr bytecode to SSA IR.

The bytecode is a stack machine. This module simulates the stack, splits code
into basic blocks, builds a CFG, and constructs SSA form with phi nodes using
the dominance frontier algorithm.
"""
from __future__ import annotations
import shlex
from optimizer.ir import (
    Module, Function, BasicBlock, Instruction, Value, Constant, Param,
    Op, IRType, StructType, ListType, SetType, ValueType,
)


# Map bytecode type names to IR types
_TYPE_MAP = {
    'i64': IRType.INT64,
    'f64': IRType.FLOAT64,
    'bool': IRType.BOOL,
    'str': IRType.STRING,
    'void': IRType.VOID,
    'int': IRType.INT64,
    'float': IRType.FLOAT64,
    'string': IRType.STRING,
    'list': ListType(IRType.INT64),
    'set': SetType(),
}


def _parse_type(type_str: str, module: Module) -> ValueType:
    """Parse a type string from bytecode into an IR type."""
    if type_str.startswith('struct:'):
        name = type_str[7:]
        if name in module.struct_types:
            return module.struct_types[name]
        return StructType(name)
    return _TYPE_MAP.get(type_str, IRType.INT64)


def _parse_line(line: str) -> tuple[str, list[str]]:
    """Parse a bytecode line into (opcode, args)."""
    line = line.strip()
    if not line or line.startswith('#'):
        return ('', [])

    # Handle string arguments with shlex
    if '"' in line:
        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()
    else:
        parts = line.split()

    if not parts:
        return ('', [])

    return (parts[0], parts[1:])


class IRBuilder:
    """Build SSA IR from fr bytecode."""

    def __init__(self):
        self.module = Module()
        self._block_counter = 0
        self._local_types: dict[str, dict[int, ValueType]] = {}  # func_name → {var_idx → type}
        self._block_maps: dict[str, dict[str, BasicBlock]] = {}  # func_name → {label → block}

    def build(self, bytecode_lines: list[str]) -> Module:
        """Convert bytecode lines to an IR Module."""
        Value.reset_counter()
        self._parse_metadata(bytecode_lines)
        self._parse_functions(bytecode_lines)
        return self.module

    def _new_block_label(self, hint: str = '') -> str:
        self._block_counter += 1
        return f'{hint}_{self._block_counter}' if hint else f'bb_{self._block_counter}'

    # ── Phase 1: Parse metadata ─────────────────────────────────

    def _parse_metadata(self, lines: list[str]):
        """Extract struct definitions, entry point, and source file from bytecode."""
        self._struct_id_map: dict[int, StructType] = {}

        for line in lines:
            op, args = _parse_line(line)

            if op == '.version':
                continue

            if op == '.struct' and args:
                # .struct <id> <field_count> <field_size> <name1> <name2> ... <type1> <type2> ...
                sid = int(args[0])
                nfields = int(args[1])
                # Skip field_size arg (args[2])
                field_names = args[3:3 + nfields]
                type_strs = args[3 + nfields:3 + 2 * nfields]
                field_types = []
                for ts in type_strs:
                    field_types.append(_TYPE_MAP.get(ts, IRType.INT64))

                st = StructType(name=f'__struct_{sid}', field_names=field_names,
                                field_types=field_types)
                self._struct_id_map[sid] = st

            elif op == '.struct_type' and len(args) >= 2:
                # .struct_type <name> <id>
                name = args[0]
                sid = int(args[1])
                if sid in self._struct_id_map:
                    self._struct_id_map[sid].name = name
                    self.module.add_struct(self._struct_id_map[sid])

            elif op == '.entry' and args:
                self.module.entry_func = args[0].rstrip('%')

            elif line.strip().startswith('# source:'):
                self.module.source_file = line.strip()[9:].strip()

        # Add any unnamed structs
        for sid, st in self._struct_id_map.items():
            if st.name not in self.module.struct_types:
                self.module.add_struct(st)

    # ── Phase 2: Parse functions ────────────────────────────────

    def _parse_functions(self, lines: list[str]):
        """Parse each function body and convert to SSA IR."""
        i = 0
        while i < len(lines):
            op, args = _parse_line(lines[i])
            if op == '.func':
                func, i = self._parse_one_function(lines, i)
                if func:
                    self.module.add_function(func)
            else:
                i += 1

    def _parse_one_function(self, lines: list[str], start: int) -> tuple[Function | None, int]:
        """Parse a single function from its .func to .end directive."""
        op, args = _parse_line(lines[start])
        if op != '.func' or len(args) < 3:
            return None, start + 1

        func_name = args[0]
        ret_type_str = args[1]
        param_count = int(args[2])

        ret_type = _parse_type(ret_type_str, self.module)
        func = Function(func_name, return_type=ret_type)

        # Collect function body lines (between .func and .end)
        body_lines = []
        i = start + 1
        while i < len(lines):
            bop, bargs = _parse_line(lines[i])
            if bop == '.end':
                i += 1
                break
            body_lines.append(lines[i])
            i += 1

        # Pass 1: Parse locals and args
        self._parse_locals_and_args(func, body_lines, param_count)

        # Pass 2: Build basic blocks from bytecode
        raw_blocks = self._split_into_blocks(func, body_lines)

        # Pass 3: Simulate stack and generate IR instructions
        self._simulate_and_build_ir(func, raw_blocks)

        # Pass 4: Build CFG edges
        self._build_cfg_edges(func)

        # Pass 5: Construct SSA (insert phi nodes, rename variables)
        self._construct_ssa(func)

        return func, i

    def _parse_locals_and_args(self, func: Function, body_lines: list[str],
                               param_count: int):
        """Extract .local and .arg declarations."""
        local_types: dict[int, ValueType] = {}  # var index → type
        arg_index = 0

        for line in body_lines:
            op, args = _parse_line(line)
            if op == '.arg' and len(args) >= 2:
                name = args[0]
                typ = _parse_type(args[1], self.module)
                param = Param(name, typ, arg_index)
                func.params.append(param)
                local_types[arg_index] = typ
                func.local_names[arg_index] = name
                arg_index += 1
            elif op == '.local' and len(args) >= 2:
                name = args[0]
                typ = _parse_type(args[1], self.module)
                var_idx = param_count + len([v for v in func.local_names
                                             if v >= param_count])
                # local_types assigns sequentially after args
                idx = len(local_types)
                local_types[idx] = typ
                func.local_names[idx] = name

        self._local_types[func.name] = local_types

    # ── Phase 3: Split bytecode into basic blocks ───────────────

    def _split_into_blocks(self, func: Function, body_lines: list[str]) -> list:
        """Split bytecode into raw basic blocks at labels and branches."""
        # First pass: find all label targets to know where blocks start
        label_set = set()
        for line in body_lines:
            op, args = _parse_line(line)
            if op == 'LABEL' and args:
                label_set.add(args[0])

        # Second pass: split into blocks
        blocks = []  # list of (label, [bytecode_lines])
        current_label = f'{func.name}_entry'
        current_lines = []

        for line in body_lines:
            op, args = _parse_line(line)

            if op in ('.local', '.arg', '.line', ''):
                if op == '.line' and args:
                    current_lines.append(line)
                continue

            if op == 'LABEL' and args:
                # End current block, start new one
                if current_lines:
                    blocks.append((current_label, current_lines))
                current_label = args[0]
                current_lines = []
                continue

            current_lines.append(line)

            # After a jump/branch/return, start a new block
            if op in ('JUMP', 'JUMP_IF_FALSE', 'JUMP_IF_TRUE',
                       'RETURN', 'RETURN_VOID', 'SWITCH_JUMP_TABLE',
                       'TRY_BEGIN'):
                blocks.append((current_label, current_lines))
                current_label = self._new_block_label('fall')
                current_lines = []

        if current_lines:
            blocks.append((current_label, current_lines))

        return blocks

    # ── Phase 4: Stack simulation and IR generation ─────────────

    def _simulate_and_build_ir(self, func: Function, raw_blocks: list):
        """Simulate the bytecode stack machine and emit SSA IR instructions."""
        block_map: dict[str, BasicBlock] = {}

        for label, bc_lines in raw_blocks:
            block = BasicBlock(label)
            func.add_block(block)
            block_map[label] = block

        self._block_maps[func.name] = block_map

        # Variable versions: track current SSA value for each local variable index
        # This is pre-SSA: we'll insert phi nodes later
        var_versions: dict[int, Value] = {}

        # Initialize params
        for p in func.params:
            var_versions[p.index] = p

        # Per-block entry and exit variable states (for PHI construction)
        block_entry_vars: dict[str, dict[int, Value]] = {}
        block_exit_vars: dict[str, dict[int, Value]] = {}

        # Process each block
        for label, bc_lines in raw_blocks:
            block = block_map[label]
            stack: list[Value] = []
            source_line = None

            block_entry_vars[label] = dict(var_versions)

            for line in bc_lines:
                op, args = _parse_line(line)

                if op == '.line':
                    source_line = int(args[0]) if args else None
                    continue
                if not op or op.startswith('#') or op.startswith('.'):
                    continue

                self._emit_instruction(
                    func, block, stack, var_versions,
                    op, args, source_line, block_map
                )

            block_exit_vars[label] = dict(var_versions)

        # Save for _construct_ssa
        if not hasattr(self, '_block_var_info'):
            self._block_var_info = {}
        self._block_var_info[func.name] = (block_entry_vars, block_exit_vars)

    def _emit_instruction(self, func, block, stack, var_versions,
                          op, args, source_line, block_map):
        """Emit IR instructions for a single bytecode instruction."""

        def _push(val):
            stack.append(val)

        def _pop():
            if stack:
                return stack.pop()
            # Empty stack — return a dummy value
            return self._make_const(IRType.INT64, 0, block, source_line)

        def _make_inst(ir_op, operands=None, result_type=None, **kwargs):
            inst = Instruction(ir_op, operands or [], result_type, source_line)
            for k, v in kwargs.items():
                setattr(inst, k, v)
            block.append(inst)
            return inst

        # ── Constants ──

        if op == 'CONST_I64':
            for a in args:
                v = self._make_const(IRType.INT64, int(a), block, source_line)
                _push(v)
            return

        if op == 'CONST_F64':
            for a in args:
                v = self._make_const(IRType.FLOAT64, float(a), block, source_line)
                _push(v)
            return

        if op == 'CONST_STR':
            for a in (args if args else ['']):
                v = self._make_const(IRType.STRING, a, block, source_line)
                _push(v)
            return

        if op == 'CONST_BOOL':
            val = args[0].lower() in ('true', '1') if args else False
            v = self._make_const(IRType.BOOL, val, block, source_line)
            _push(v)
            return

        # ── Memory ──

        if op == 'LOAD':
            for a in args:
                idx = int(a)
                val = var_versions.get(idx)
                if val is None:
                    typ = self._local_types.get(func.name, {}).get(idx, IRType.INT64)
                    val = self._make_const(typ, 0, block, source_line)
                    var_versions[idx] = val
                _push(val)
            return

        if op == 'STORE':
            for a in reversed(args):
                idx = int(a)
                val = _pop()
                var_versions[idx] = val
            return

        if op == 'STORE_CONST_I64':
            if len(args) >= 2:
                idx = int(args[0])
                val = self._make_const(IRType.INT64, int(args[1]), block, source_line)
                var_versions[idx] = val
            return

        if op == 'STORE_CONST_F64':
            if len(args) >= 2:
                idx = int(args[0])
                val = self._make_const(IRType.FLOAT64, float(args[1]), block, source_line)
                var_versions[idx] = val
            return

        if op == 'STORE_CONST_BOOL':
            if len(args) >= 2:
                idx = int(args[0])
                val = self._make_const(IRType.BOOL, args[1].lower() in ('true', '1'), block, source_line)
                var_versions[idx] = val
            return

        if op == 'STORE_CONST_STR':
            if len(args) >= 2:
                idx = int(args[0])
                val = self._make_const(IRType.STRING, args[1], block, source_line)
                var_versions[idx] = val
            return

        if op == 'FUSED_LOAD_STORE':
            # Alternating LOAD/STORE/LOAD/STORE... sequence
            # Starts with LOAD, so args[0] is load, args[1] is store, args[2] is load, etc.
            i = 0
            expect_load = True
            while i < len(args):
                idx = int(args[i])
                if expect_load:
                    # LOAD: push var onto stack
                    val = var_versions.get(idx)
                    if val is None:
                        typ = self._local_types.get(func.name, {}).get(idx, IRType.INT64)
                        val = self._make_const(typ, 0, block, source_line)
                    _push(val)
                else:
                    # STORE: pop from stack into var
                    val = _pop()
                    var_versions[idx] = val
                expect_load = not expect_load
                i += 1
            return

        if op == 'FUSED_STORE_LOAD':
            for i in range(0, len(args) - 1, 2):
                store_idx = int(args[i])
                load_idx = int(args[i + 1])
                val = _pop()
                var_versions[store_idx] = val
                load_val = var_versions.get(load_idx)
                if load_val is None:
                    load_val = self._make_const(IRType.INT64, 0, block, source_line)
                _push(load_val)
            return

        if op == 'FUSED_GET_STORE_LOAD':
            for i in range(0, len(args) - 2, 3):
                field_idx = int(args[i])
                store_idx = int(args[i + 1])
                load_idx = int(args[i + 2])
                struct_val = _pop()
                inst = _make_inst(Op.LOAD_FIELD, [struct_val], IRType.INT64,
                                  imm_int=field_idx)
                if inst.result:
                    var_versions[store_idx] = inst.result
                load_val = var_versions.get(load_idx)
                if load_val is None:
                    load_val = self._make_const(IRType.INT64, 0, block, source_line)
                _push(load_val)
            return

        if op in ('COPY_LOCAL', 'COPY_LOCAL_REF'):
            if len(args) >= 2:
                src = int(args[0])
                dst = int(args[1])
                val = var_versions.get(src)
                if val is None:
                    val = self._make_const(IRType.INT64, 0, block, source_line)
                var_versions[dst] = val
            return

        if op == 'INC_LOCAL' and args:
            idx = int(args[0])
            val = var_versions.get(idx)
            if val is None:
                val = self._make_const(IRType.INT64, 0, block, source_line)
            one = self._make_const(IRType.INT64, 1, block, source_line)
            inst = _make_inst(Op.ADD, [val, one], IRType.INT64)
            if inst.result:
                var_versions[idx] = inst.result
            return

        if op == 'DEC_LOCAL' and args:
            idx = int(args[0])
            val = var_versions.get(idx)
            if val is None:
                val = self._make_const(IRType.INT64, 0, block, source_line)
            one = self._make_const(IRType.INT64, 1, block, source_line)
            inst = _make_inst(Op.SUB, [val, one], IRType.INT64)
            if inst.result:
                var_versions[idx] = inst.result
            return

        # ── Stack manipulation ──

        if op == 'DUP':
            val = _pop()
            _push(val)
            _push(val)
            return

        if op == 'POP':
            _pop()
            return

        if op == 'SWAP':
            a = _pop()
            b = _pop()
            _push(a)
            _push(b)
            return

        # ── Integer arithmetic ──

        if op == 'ADD_I64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.ADD, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'SUB_I64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.SUB, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'MUL_I64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.MUL, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'DIV_I64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.DIV, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'MOD_I64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.MOD, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'NEG':
            a = _pop()
            inst = _make_inst(Op.NEG, [a], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        # ── Float arithmetic ──

        if op == 'ADD_F64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.FADD, [a, b], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'SUB_F64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.FSUB, [a, b], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'MUL_F64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.FMUL, [a, b], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'DIV_F64':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.FDIV, [a, b], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        # ── Const-fused arithmetic ──

        if op == 'ADD_CONST_I64' and args:
            a = _pop()
            if a.type == IRType.FLOAT64:
                c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
                inst = _make_inst(Op.FADD, [a, c], IRType.FLOAT64)
            else:
                c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
                inst = _make_inst(Op.ADD, [a, c], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'SUB_CONST_I64' and args:
            a = _pop()
            if a.type == IRType.FLOAT64:
                c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
                inst = _make_inst(Op.FSUB, [a, c], IRType.FLOAT64)
            else:
                c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
                inst = _make_inst(Op.SUB, [a, c], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'MUL_CONST_I64' and args:
            a = _pop()
            if a.type == IRType.FLOAT64:
                c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
                inst = _make_inst(Op.FMUL, [a, c], IRType.FLOAT64)
            else:
                c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
                inst = _make_inst(Op.MUL, [a, c], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'ADD_CONST_F64' and args:
            a = _pop()
            c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
            inst = _make_inst(Op.FADD, [a, c], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'SUB_CONST_F64' and args:
            a = _pop()
            c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
            inst = _make_inst(Op.FSUB, [a, c], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'MUL_CONST_F64' and args:
            a = _pop()
            c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
            inst = _make_inst(Op.FMUL, [a, c], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        # ── LOAD2 fused ops ──

        if op == 'LOAD2_ADD_I64' and len(args) >= 2:
            a = var_versions.get(int(args[0]))
            b = var_versions.get(int(args[1]))
            if a is None:
                a = self._make_const(IRType.INT64, 0, block, source_line)
            if b is None:
                b = self._make_const(IRType.INT64, 0, block, source_line)
            inst = _make_inst(Op.ADD, [a, b], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LOAD2_MUL_F64' and len(args) >= 2:
            a = var_versions.get(int(args[0]))
            b = var_versions.get(int(args[1]))
            if a is None:
                a = self._make_const(IRType.FLOAT64, 0.0, block, source_line)
            if b is None:
                b = self._make_const(IRType.FLOAT64, 0.0, block, source_line)
            inst = _make_inst(Op.FMUL, [a, b], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op.startswith('LOAD2_CMP_') and len(args) >= 2:
            a = var_versions.get(int(args[0]))
            b = var_versions.get(int(args[1]))
            if a is None:
                a = self._make_const(IRType.INT64, 0, block, source_line)
            if b is None:
                b = self._make_const(IRType.INT64, 0, block, source_line)
            cmp_map = {
                'LOAD2_CMP_LT': Op.LT, 'LOAD2_CMP_GT': Op.GT,
                'LOAD2_CMP_LE': Op.LE, 'LOAD2_CMP_GE': Op.GE,
                'LOAD2_CMP_EQ': Op.EQ, 'LOAD2_CMP_NE': Op.NE,
            }
            ir_op = cmp_map.get(op, Op.LT)
            inst = _make_inst(ir_op, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        # ── Comparison ──

        if op == 'CMP_LT':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.LT, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_GT':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.GT, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_LE':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.LE, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_GE':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.GE, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_EQ':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.EQ, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_NE':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.NE, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        # ── Const-fused comparison ──

        if op == 'CMP_LT_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.LT, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_GT_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.GT, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_LE_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.LE, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_GE_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.GE, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_EQ_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.EQ, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'CMP_NE_CONST' and args:
            a = _pop()
            c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
            inst = _make_inst(Op.NE, [a, c], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        # ── Logic ──

        if op == 'AND':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.AND, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'OR':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.OR, [a, b], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'NOT':
            a = _pop()
            inst = _make_inst(Op.NOT, [a], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        # ── String ──

        if op == 'ADD_STR':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.STR_CONCAT, [a, b], IRType.STRING)
            if inst.result:
                _push(inst.result)
            return

        # ── Type conversion ──

        if op == 'TO_INT':
            a = _pop()
            if a.type == IRType.STRING:
                # String-to-int conversion via runtime
                inst = _make_inst(Op.CALL_BUILTIN, [a], IRType.INT64,
                                  imm_str='str_to_int')
            else:
                inst = _make_inst(Op.FLOAT_TO_INT, [a], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'TO_FLOAT':
            a = _pop()
            if a.type == IRType.STRING:
                # String-to-float conversion via runtime
                inst = _make_inst(Op.CALL_BUILTIN, [a], IRType.FLOAT64,
                                  imm_str='str_to_float')
            else:
                inst = _make_inst(Op.INT_TO_FLOAT, [a], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'BUILTIN_STR':
            a = _pop()
            inst = _make_inst(Op.TO_STR, [a], IRType.STRING)
            if inst.result:
                _push(inst.result)
            return

        if op == 'TO_BOOL':
            a = _pop()
            inst = _make_inst(Op.TO_BOOL, [a], IRType.BOOL)
            if inst.result:
                _push(inst.result)
            return

        if op == 'STR_EQ':
            b, a = _pop(), _pop()
            inst = _make_inst(Op.CALL_BUILTIN, [a, b], IRType.BOOL,
                              imm_str='str_eq')
            if inst.result:
                _push(inst.result)
            return

        # ── Control flow ──

        if op == 'JUMP' and args:
            target_label = args[0]
            inst = Instruction(Op.JUMP, [], None, source_line)
            inst.imm_str = target_label
            block.append(inst)
            return

        if op == 'JUMP_IF_FALSE' and args:
            cond = _pop()
            target_label = args[0]
            inst = Instruction(Op.BRANCH, [cond], None, source_line)
            inst.imm_str = target_label  # false branch label
            block.append(inst)
            return

        if op == 'JUMP_IF_TRUE' and args:
            cond = _pop()
            target_label = args[0]
            # BRANCH does jz (jump when false). For JUMP_IF_TRUE we want to
            # jump when true, so negate the condition first.
            neg = _make_inst(Op.NOT, [cond], IRType.BOOL)
            branch_cond = neg.result if neg.result else cond
            inst = Instruction(Op.BRANCH, [branch_cond], None, source_line)
            inst.imm_str = target_label
            block.append(inst)
            return

        if op == 'RETURN':
            val = _pop()
            inst = Instruction(Op.RETURN, [val], None, source_line)
            block.append(inst)
            return

        if op == 'RETURN_VOID':
            inst = Instruction(Op.RETURN_VOID, [], None, source_line)
            block.append(inst)
            return

        # ── Struct operations ──

        if op == 'STRUCT_NEW' and args:
            struct_id = int(args[0])
            struct_type = self._struct_id_map.get(struct_id)
            n_fields = 0
            target_name = f'struct_{struct_id}'

            if struct_type:
                n_fields = len(struct_type.field_names)
                target_name = struct_type.name
            elif len(args) >= 2:
                # STRUCT_NEW <id> <field_count> form
                n_fields = int(args[1])

            field_vals = []
            for _ in range(n_fields):
                field_vals.insert(0, _pop())

            result_type = struct_type if struct_type else StructType(target_name)
            inst = _make_inst(Op.ALLOC_STRUCT, field_vals,
                              result_type, imm_str=target_name,
                              imm_int=struct_id)
            if inst.result:
                _push(inst.result)
            return

        if op == 'STRUCT_GET' and args:
            field_idx = int(args[0])
            struct_val = _pop()
            # Determine field type from struct type info
            field_type = IRType.INT64  # default
            if isinstance(struct_val.type, StructType):
                if field_idx < len(struct_val.type.field_types):
                    field_type = struct_val.type.field_types[field_idx]
            inst = _make_inst(Op.LOAD_FIELD, [struct_val], field_type,
                              imm_int=field_idx)
            if inst.result:
                _push(inst.result)
            return

        if op == 'STRUCT_SET' and args:
            field_idx = int(args[0])
            val = _pop()
            struct_val = _pop()
            _make_inst(Op.STORE_FIELD, [struct_val, val], None,
                       imm_int=field_idx)
            _push(struct_val)  # STRUCT_SET pushes struct back
            return

        # ── List operations ──

        if op == 'LIST_NEW':
            inst = _make_inst(Op.ALLOC_LIST, [], ListType(IRType.INT64))
            if inst.result:
                _push(inst.result)
            return

        if op in ('LIST_NEW_I64', 'LIST_NEW_F64', 'LIST_NEW_STR', 'LIST_NEW_BOOL'):
            elem_type = IRType.INT64
            if 'F64' in op:
                elem_type = IRType.FLOAT64
            elif 'STR' in op:
                elem_type = IRType.STRING
            elif 'BOOL' in op:
                elem_type = IRType.BOOL
            count = int(args[0]) if args else 0
            # Elements are inline in args[1:], not on the stack
            elems = []
            for i in range(count):
                val_str = args[1 + i] if (1 + i) < len(args) else '0'
                elems.append(self._make_const(elem_type, val_str if elem_type == IRType.STRING else (float(val_str) if elem_type == IRType.FLOAT64 else int(val_str)), block, source_line))
            inst = _make_inst(Op.ALLOC_LIST, elems, ListType(elem_type),
                              imm_int=count)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LIST_NEW_STACK' and args:
            count = int(args[0])
            elems = []
            for _ in range(count):
                elems.insert(0, _pop())
            inst = _make_inst(Op.ALLOC_LIST, elems, ListType(IRType.INT64),
                              imm_int=count)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LIST_APPEND':
            val = _pop()
            lst = _pop()
            _make_inst(Op.LIST_APPEND, [lst, val])
            _push(lst)
            return

        if op == 'LIST_GET':
            idx = _pop()
            lst = _pop()
            # String indexing returns a string character
            result_type = IRType.STRING if lst.type == IRType.STRING else IRType.INT64
            inst = _make_inst(Op.LIST_GET, [lst, idx], result_type)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LIST_SET':
            val = _pop()
            idx = _pop()
            lst = _pop()
            _make_inst(Op.LIST_SET, [lst, idx, val])
            _push(lst)
            return

        if op == 'LIST_LEN':
            lst = _pop()
            inst = _make_inst(Op.LIST_LEN, [lst], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LIST_POP':
            lst = _pop()
            inst = _make_inst(Op.CALL_BUILTIN, [lst], IRType.INT64,
                              imm_str='list_pop')
            # LIST_POP in bytecode pushes (modified_list, popped_value)
            # The list is modified in-place, so push list back first, then result
            _push(lst)
            if inst.result:
                _push(inst.result)
            return

        if op == 'LIST_PRINT':
            lst = _pop()
            _make_inst(Op.CALL_BUILTIN, [lst], IRType.VOID,
                       imm_str='list_print')
            return

        # ── Builtins ──

        if op == 'BUILTIN_PRINT':
            val = _pop()
            _make_inst(Op.PRINT, [val])
            return

        if op == 'BUILTIN_PRINTLN':
            val = _pop()
            _make_inst(Op.PRINTLN, [val])
            return

        if op == 'BUILTIN_LEN':
            val = _pop()
            # Dispatch based on operand type
            if isinstance(val.type, ListType):
                inst = _make_inst(Op.LIST_LEN, [val], IRType.INT64)
            elif isinstance(val.type, SetType):
                inst = _make_inst(Op.CALL_BUILTIN, [val], IRType.INT64,
                                  imm_str='set_len')
            else:
                inst = _make_inst(Op.CALL_BUILTIN, [val], IRType.INT64,
                                  imm_str='len')
            if inst.result:
                _push(inst.result)
            return

        if op == 'BUILTIN_INPUT':
            inst = _make_inst(Op.INPUT, [], IRType.STRING)
            if inst.result:
                _push(inst.result)
            return

        if op == 'ASSERT':
            msg = _pop()
            cond = _pop()
            _make_inst(Op.CALL_BUILTIN, [cond, msg], IRType.VOID,
                       imm_str='assert')
            return

        if op == 'BUILTIN_PI':
            import math
            v = self._make_const(IRType.FLOAT64, math.pi, block, source_line)
            _push(v)
            return

        if op == 'EXIT':
            val = _pop()
            _make_inst(Op.CALL_BUILTIN, [val], IRType.VOID, imm_str='exit')
            return

        if op == 'SLEEP':
            val = _pop()
            _make_inst(Op.CALL_BUILTIN, [val], IRType.VOID, imm_str='sleep')
            return

        if op == 'CONST_BYTES':
            # Treat as a string constant for now
            text = args[0] if args else ''
            v = self._make_const(IRType.STRING, text, block, source_line)
            _push(v)
            return

        if op == 'ENCODE':
            encoding = _pop()  # encoding argument (e.g. "utf-8")
            val = _pop()       # string to encode
            inst = _make_inst(Op.CALL_BUILTIN, [val, encoding], IRType.STRING,
                              imm_str='str_encode')
            if inst.result:
                _push(inst.result)
            return

        if op == 'DECODE':
            encoding = _pop()  # encoding argument (e.g. "utf-8")
            val = _pop()       # bytes to decode
            inst = _make_inst(Op.CALL_BUILTIN, [val, encoding], IRType.STRING,
                              imm_str='str_decode')
            if inst.result:
                _push(inst.result)
            return

        if op == 'MUL_STR':
            count = _pop()
            s = _pop()
            inst = _make_inst(Op.CALL_BUILTIN, [s, count], IRType.STRING,
                              imm_str='str_repeat')
            if inst.result:
                _push(inst.result)
            return

        if op in ('STR_STRIP', 'STR_LOWER', 'STR_UPPER'):
            val = _pop()
            func_map = {'STR_STRIP': 'str_strip', 'STR_LOWER': 'str_lower', 'STR_UPPER': 'str_upper'}
            inst = _make_inst(Op.CALL_BUILTIN, [val], IRType.STRING,
                              imm_str=func_map[op])
            if inst.result:
                _push(inst.result)
            return

        if op in ('STR_SPLIT', 'STR_JOIN', 'STR_REPLACE'):
            if op == 'STR_REPLACE':
                new = _pop()
                old = _pop()
                s = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [s, old, new], IRType.STRING,
                                  imm_str='str_replace')
            elif op == 'STR_SPLIT':
                delim = _pop()
                s = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [s, delim], ListType(IRType.STRING),
                                  imm_str='str_split')
            elif op == 'STR_JOIN':
                lst = _pop()
                delim = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [lst, delim], IRType.STRING,
                                  imm_str='str_join')
            if inst.result:
                _push(inst.result)
            return

        # ── Function calls ──

        if op == 'CALL' and len(args) >= 2:
            func_name = args[0]
            arg_count = int(args[1])
            call_args = []
            for _ in range(arg_count):
                call_args.insert(0, _pop())

            # Handle builtin functions that aren't user-defined
            if func_name == 'assert':
                # runtime_assert(condition, message) — if only 1 arg, add empty message
                if len(call_args) == 1:
                    empty = self._make_const(IRType.STRING, '', block, source_line)
                    call_args.append(empty)
                _make_inst(Op.CALL_BUILTIN, call_args, IRType.VOID,
                           imm_str='assert')
                return

            # Determine return type
            target_func = self.module.get_function(func_name)
            ret_type = target_func.return_type if target_func else IRType.INT64

            inst = _make_inst(Op.CALL, call_args, ret_type, imm_str=func_name,
                              imm_int=arg_count)
            if inst.result and ret_type != IRType.VOID:
                _push(inst.result)
            return

        # ── Global variables ──

        if op == 'LOAD_GLOBAL' and args:
            inst = _make_inst(Op.LOAD_GLOBAL, [], IRType.INT64, imm_str=args[0])
            if inst.result:
                _push(inst.result)
            return

        if op == 'STORE_GLOBAL' and args:
            val = _pop()
            _make_inst(Op.STORE_GLOBAL, [val], imm_str=args[0])
            return

        # ── Switch ──

        if op == 'SWITCH_JUMP_TABLE' and args:
            val = _pop()
            # args: min_val max_val label1 label2 ... labelN default_label
            min_val = int(args[0])
            max_val = int(args[1])
            n_entries = max_val - min_val
            labels = args[2:]  # n_entries case labels + default_label
            default_label = labels[-1]
            case_labels = labels[:n_entries]

            # Lower to chain of comparisons: each value checks EQ and branches
            default_block = block_map.get(default_label)
            if default_block is None:
                default_block = BasicBlock(default_label)
                func.add_block(default_block)
                block_map[default_label] = default_block

            for i, target_label in enumerate(case_labels):
                case_val = min_val + i
                target_block = block_map.get(target_label)
                if target_block is None:
                    target_block = BasicBlock(target_label)
                    func.add_block(target_block)
                    block_map[target_label] = target_block

                c = self._make_const(IRType.INT64, case_val, block, source_line)
                cmp_inst = _make_inst(Op.EQ, [val, c], IRType.BOOL)

                if i < len(case_labels) - 1:
                    # Create next check block
                    next_label = self._new_block_label('sw_check')
                    next_block = BasicBlock(next_label)
                    func.add_block(next_block)
                    block_map[next_label] = next_block

                    if cmp_inst.result:
                        _make_inst(Op.BRANCH, [cmp_inst.result], IRType.VOID,
                                   target_blocks=[target_block, next_block])
                    block.successors.append(target_block)
                    block.successors.append(next_block)
                    target_block.predecessors.append(block)
                    next_block.predecessors.append(block)

                    block = next_block
                    stack = []  # Stack is empty at start of new block
                else:
                    # Last case: branch to target or default
                    if cmp_inst.result:
                        _make_inst(Op.BRANCH, [cmp_inst.result], IRType.VOID,
                                   target_blocks=[target_block, default_block])
                    block.successors.append(target_block)
                    block.successors.append(default_block)
                    target_block.predecessors.append(block)
                    default_block.predecessors.append(block)
            return

        # ── Math builtins ──

        _math_ops = {
            'SQRT': (Op.SQRT, IRType.FLOAT64),
            'BUILTIN_SQRT': (Op.SQRT, IRType.FLOAT64),
            'SIN': (Op.SIN, IRType.FLOAT64),
            'BUILTIN_SIN': (Op.SIN, IRType.FLOAT64),
            'COS': (Op.COS, IRType.FLOAT64),
            'BUILTIN_COS': (Op.COS, IRType.FLOAT64),
            'TAN': (Op.TAN, IRType.FLOAT64),
            'BUILTIN_TAN': (Op.TAN, IRType.FLOAT64),
            'ABS': (Op.ABS, IRType.INT64),
            'BUILTIN_ABS': (Op.ABS, IRType.INT64),
            'FLOOR': (Op.FLOOR, IRType.INT64),
            'BUILTIN_FLOOR': (Op.FLOOR, IRType.INT64),
            'CEIL': (Op.CEIL, IRType.INT64),
            'BUILTIN_CEIL': (Op.CEIL, IRType.INT64),
            'BUILTIN_ROUND': (Op.ROUND, IRType.FLOAT64),
            'MIN': (Op.MIN, IRType.INT64),
            'BUILTIN_MIN': (Op.MIN, IRType.INT64),
            'MAX': (Op.MAX, IRType.INT64),
            'BUILTIN_MAX': (Op.MAX, IRType.INT64),
            'POW': (Op.POW, IRType.FLOAT64),
            'BUILTIN_POW': (Op.POW, IRType.FLOAT64),
        }

        if op in _math_ops:
            ir_op, ret = _math_ops[op]
            if op in ('MIN', 'MAX', 'POW'):
                b, a = _pop(), _pop()
                inst = _make_inst(ir_op, [a, b], ret)
            else:
                a = _pop()
                inst = _make_inst(ir_op, [a], ret)
            if inst.result:
                _push(inst.result)
            return

        # ── Fused arithmetic with constants ──

        if op in ('MUL_CONST_I64', 'DIV_CONST_I64', 'MOD_CONST_I64',
                   'ADD_CONST_I64', 'SUB_CONST_I64') and args:
            a = _pop()
            # If operand is float, use float arithmetic
            if a.type == IRType.FLOAT64:
                c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
                fop_map = {'MUL_CONST_I64': Op.FMUL, 'DIV_CONST_I64': Op.FDIV,
                           'MOD_CONST_I64': Op.MOD, 'ADD_CONST_I64': Op.FADD,
                           'SUB_CONST_I64': Op.FSUB}
                inst = _make_inst(fop_map[op], [a, c], IRType.FLOAT64)
            else:
                c = self._make_const(IRType.INT64, int(args[0]), block, source_line)
                op_map = {'MUL_CONST_I64': Op.MUL, 'DIV_CONST_I64': Op.DIV,
                          'MOD_CONST_I64': Op.MOD, 'ADD_CONST_I64': Op.ADD,
                          'SUB_CONST_I64': Op.SUB}
                inst = _make_inst(op_map[op], [a, c], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        if op in ('MUL_CONST_F64', 'DIV_CONST_F64', 'ADD_CONST_F64', 'SUB_CONST_F64') and args:
            a = _pop()
            c = self._make_const(IRType.FLOAT64, float(args[0]), block, source_line)
            op_map = {'MUL_CONST_F64': Op.FMUL, 'DIV_CONST_F64': Op.FDIV,
                      'ADD_CONST_F64': Op.FADD, 'SUB_CONST_F64': Op.FSUB}
            inst = _make_inst(op_map[op], [a, c], IRType.FLOAT64)
            if inst.result:
                _push(inst.result)
            return

        # ── Fused arithmetic ──

        if op == 'FUSED_ARITH_CONST' and len(args) >= 3:
            # FUSED_ARITH_CONST var_idx op_type const_val [repeat...]
            for i in range(0, len(args) - 2, 3):
                idx = int(args[i])
                arith_op = args[i + 1]
                const_val = args[i + 2]
                var_val = var_versions.get(idx)
                if var_val is None:
                    var_val = self._make_const(IRType.INT64, 0, block, source_line)
                c = self._make_const(IRType.INT64, int(const_val), block, source_line)
                ir_op = {'add': Op.ADD, 'sub': Op.SUB, 'mul': Op.MUL}.get(arith_op, Op.ADD)
                inst = _make_inst(ir_op, [var_val, c], IRType.INT64)
                if inst.result:
                    var_versions[idx] = inst.result
            return

        # ── File I/O, set, dict, etc. → CALL_BUILTIN ──

        if op.startswith('FILE_'):
            # Map to correct runtime function names
            file_map = {
                'FILE_OPEN': ('fopen', 2, IRType.INT64),
                'FILE_WRITE': ('fwrite', 2, IRType.INT64),
                'FILE_READ': ('fread', 2, IRType.STRING),
                'FILE_CLOSE': ('fclose', 1, IRType.VOID),
            }
            if op in file_map:
                name, n_args, ret_type = file_map[op]
                builtin_args = [_pop() for _ in range(n_args)]
                builtin_args.reverse()
                inst = _make_inst(Op.CALL_BUILTIN, builtin_args, ret_type,
                                  imm_str=name)
                if inst.result:
                    _push(inst.result)
            return

        if op.startswith('SET_') or op.startswith('DICT_'):
            builtin_name = op.lower()
            if op in ('SET_ADD', 'SET_REMOVE'):
                val = _pop()
                s = _pop()
                # void functions — don't use return value, re-push the set
                _make_inst(Op.CALL_BUILTIN, [s, val], IRType.VOID,
                           imm_str=builtin_name)
                _push(s)
            elif op == 'SET_CONTAINS':
                val = _pop()
                s = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [s, val], IRType.BOOL,
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            elif op == 'SET_LEN':
                s = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [s], IRType.INT64,
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            elif op == 'SET_NEW':
                inst = _make_inst(Op.CALL_BUILTIN, [], SetType(),
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            elif op == 'SET_PRINT':
                s = _pop()
                _make_inst(Op.CALL_BUILTIN, [s], IRType.VOID,
                           imm_str='set_print')
            elif op == 'DICT_NEW':
                inst = _make_inst(Op.CALL_BUILTIN, [], IRType.INT64,
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            elif op == 'DICT_SET':
                builtin_args = [_pop(), _pop()]
                _make_inst(Op.CALL_BUILTIN, builtin_args, IRType.VOID,
                           imm_str=builtin_name)
            elif op in ('DICT_GET', 'DICT_CONTAINS'):
                builtin_args = [_pop()]
                inst = _make_inst(Op.CALL_BUILTIN, builtin_args, IRType.INT64,
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            else:
                n = min(len(stack), 2)
                builtin_args = [_pop() for _ in range(n)]
                builtin_args.reverse()
                inst = _make_inst(Op.CALL_BUILTIN, builtin_args, IRType.INT64,
                                  imm_str=builtin_name)
                if inst.result:
                    _push(inst.result)
            return

        if op == 'CONTAINS':
            b, a = _pop(), _pop()
            # Choose runtime function based on type
            builtin_name = 'contains'
            if hasattr(a, 'type') and a.type == IRType.STRING:
                builtin_name = 'str_contains'
            inst = _make_inst(Op.CALL_BUILTIN, [a, b], IRType.BOOL,
                              imm_str=builtin_name)
            if inst.result:
                _push(inst.result)
            return

        # ── Exception handling ──

        if op == 'TRY_BEGIN' and len(args) >= 2:
            exc_type = args[0].strip('"')
            except_label = args[1]
            exc_str = self._make_const(IRType.STRING, exc_type, block, source_line)
            inst = Instruction(Op.TRY_BEGIN, [exc_str], None, source_line)
            inst.imm_str = except_label
            block.append(inst)
            return

        if op == 'TRY_END':
            inst = Instruction(Op.TRY_END, [], None, source_line)
            block.append(inst)
            return

        if op == 'RAISE' and len(args) >= 2:
            exc_type = args[0].strip('"')
            message = args[1].strip('"')
            type_str = self._make_const(IRType.STRING, exc_type, block, source_line)
            msg_str = self._make_const(IRType.STRING, message, block, source_line)
            inst = Instruction(Op.RAISE, [type_str, msg_str], None, source_line)
            block.append(inst)
            return

        # ── Fork/Join ──

        if op in ('FORK', 'JOIN', 'WAIT'):
            if op == 'FORK':
                inst = _make_inst(Op.CALL_BUILTIN, [], IRType.INT64,
                                  imm_str='fork')
                if inst.result:
                    _push(inst.result)
            elif op == 'JOIN':
                val = _pop()
                inst = _make_inst(Op.CALL_BUILTIN, [val], IRType.INT64,
                                  imm_str='join')
                if inst.result:
                    _push(inst.result)
            return

        if op == 'GOTO_CALL' and args:
            func_name = args[0]
            # Tail call: jump to function start
            inst = Instruction(Op.JUMP, [], None, source_line)
            inst.imm_str = f'{func_name}_entry'
            block.append(inst)
            return

        if op == 'SELECT':
            false_val = _pop()
            true_val = _pop()
            cond = _pop()
            inst = _make_inst(Op.SELECT, [cond, true_val, false_val], IRType.INT64)
            if inst.result:
                _push(inst.result)
            return

        # ── Extern calls (C FFI) ──
        # These are handled as CALL with extern flag; the native codegen
        # will detect c_import functions by name

        # Fallthrough: unknown op — emit as generic CALL_BUILTIN
        n_args_guess = min(len(stack), 2)
        builtin_args = [_pop() for _ in range(n_args_guess)]
        builtin_args.reverse()
        inst = _make_inst(Op.CALL_BUILTIN, builtin_args, IRType.INT64,
                          imm_str=op.lower())
        if inst.result:
            _push(inst.result)

    def _make_const(self, typ, value, block, source_line) -> Value:
        """Create a constant value instruction."""
        op_map = {
            IRType.INT64: Op.CONST_INT,
            IRType.FLOAT64: Op.CONST_FLOAT,
            IRType.STRING: Op.CONST_STR,
            IRType.BOOL: Op.CONST_BOOL,
        }
        ir_op = op_map.get(typ, Op.CONST_INT)
        inst = Instruction(ir_op, [], typ, source_line)
        if typ == IRType.INT64:
            inst.imm_int = int(value)
        elif typ == IRType.FLOAT64:
            inst.imm_float = float(value)
        elif typ == IRType.STRING:
            inst.imm_str = str(value)
            if value not in self.module.string_constants:
                self.module.string_constants.append(value)
        elif typ == IRType.BOOL:
            inst.imm_int = 1 if value else 0
        block.append(inst)
        return inst.result

    # ── Phase 5: Build CFG edges ────────────────────────────────

    def _build_cfg_edges(self, func: Function):
        """Connect basic blocks via control flow edges."""
        block_map = self._block_maps.get(func.name, {})
        blocks = func.blocks

        for i, block in enumerate(blocks):
            term = block.terminator
            if term is None:
                # No terminator — fall through to next block
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    block.successors.append(next_block)
                    next_block.predecessors.append(block)
                continue

            if term.op == Op.JUMP:
                target_label = term.imm_str
                if target_label in block_map:
                    target = block_map[target_label]
                    block.successors.append(target)
                    target.predecessors.append(block)
                    term.target_blocks = [target]

            elif term.op == Op.BRANCH:
                # BRANCH cond, false_label
                # True branch = fall through to next block
                # False branch = jump to label
                false_label = term.imm_str
                if i + 1 < len(blocks):
                    true_block = blocks[i + 1]
                    block.successors.append(true_block)
                    true_block.predecessors.append(block)
                if false_label in block_map:
                    false_block = block_map[false_label]
                    block.successors.append(false_block)
                    false_block.predecessors.append(block)
                    term.target_blocks = [
                        blocks[i + 1] if i + 1 < len(blocks) else false_block,
                        false_block,
                    ]

            elif term.op == Op.TRY_BEGIN:
                # TRY_BEGIN: fall through to try body, jump to except on exception
                except_label = term.imm_str
                if i + 1 < len(blocks):
                    try_body = blocks[i + 1]
                    block.successors.append(try_body)
                    try_body.predecessors.append(block)
                if except_label in block_map:
                    except_block = block_map[except_label]
                    block.successors.append(except_block)
                    except_block.predecessors.append(block)
                    term.target_blocks = [
                        blocks[i + 1] if i + 1 < len(blocks) else except_block,
                        except_block,
                    ]

            # RETURN/RETURN_VOID have no successors

    # ── Phase 6: SSA construction ───────────────────────────────

    def _construct_ssa(self, func: Function):
        """Insert phi nodes for variables that differ across predecessor blocks.

        After the initial stack simulation, loop variables are broken:
        the loop header uses the pre-loop value instead of a PHI that
        merges the initial value with the back-edge update.

        This method:
        1. Finds blocks with multiple predecessors
        2. Checks if any variable has different values from different preds
        3. Inserts PHI nodes and replaces stale uses
        """
        info = self._block_var_info.get(func.name)
        if not info:
            return
        block_entry_vars, block_exit_vars = info
        block_map = self._block_maps.get(func.name, {})

        # Build predecessor labels for each block
        pred_labels: dict[str, list[str]] = {b.label: [] for b in func.blocks}
        for block in func.blocks:
            for succ in block.successors:
                pred_labels[succ.label].append(block.label)

        # Collect all blocks that are part of each PHI's scope (loop body)
        changed = True
        iterations = 0
        while changed and iterations < 10:
            changed = False
            iterations += 1

            for block in func.blocks:
                preds = pred_labels[block.label]
                if len(preds) < 2:
                    continue

                # Collect all variable indices that exist in any predecessor's exit
                all_vars: set[int] = set()
                for pl in preds:
                    if pl in block_exit_vars:
                        all_vars.update(block_exit_vars[pl].keys())

                for var_idx in all_vars:
                    # Get the value from each predecessor's exit
                    pred_vals: dict[str, Value] = {}
                    for pl in preds:
                        ev = block_exit_vars.get(pl, {})
                        if var_idx in ev:
                            pred_vals[pl] = ev[var_idx]

                    if len(pred_vals) < 2:
                        continue

                    # Check if all predecessors provide the same value
                    vals = list(pred_vals.values())
                    if all(v is vals[0] for v in vals[1:]):
                        continue

                    # Different values — need a PHI node
                    # Check if we already inserted a PHI for this var in this block
                    existing_phi = None
                    for phi in block.phi_nodes:
                        if phi.imm_int == var_idx:
                            existing_phi = phi
                            break

                    if existing_phi:
                        # Update existing PHI operands
                        new_operands = []
                        new_target_blocks = []
                        for pl in preds:
                            if pl in pred_vals:
                                new_operands.append(pred_vals[pl])
                                new_target_blocks.append(block_map[pl])
                        if (new_operands != existing_phi.operands or
                                new_target_blocks != existing_phi.target_blocks):
                            # Update PHI
                            existing_phi.remove_from_uses()
                            existing_phi.operands = new_operands
                            existing_phi.target_blocks = new_target_blocks
                            for v in new_operands:
                                if isinstance(v, Value):
                                    v.uses.append(existing_phi)
                            phi_val = existing_phi.result
                        else:
                            continue
                    else:
                        # Create new PHI
                        phi_operands = []
                        phi_blocks = []
                        val_type = vals[0].type
                        for pl in preds:
                            if pl in pred_vals:
                                phi_operands.append(pred_vals[pl])
                                phi_blocks.append(block_map[pl])

                        phi_inst = Instruction(Op.PHI, phi_operands, val_type)
                        phi_inst.imm_int = var_idx
                        phi_inst.target_blocks = phi_blocks
                        # Insert PHI at the beginning of the block
                        phi_inst.block = block
                        block.instructions.insert(0, phi_inst)
                        phi_val = phi_inst.result
                        changed = True

                    if phi_val is None:
                        continue

                    # The value used during simulation for this var at this block
                    # was block_entry_vars[block.label][var_idx]
                    old_val = block_entry_vars.get(block.label, {}).get(var_idx)
                    if old_val is None or old_val is phi_val:
                        # Update exit vars for propagation
                        block_exit_vars.setdefault(block.label, {})[var_idx] = \
                            block_exit_vars.get(block.label, {}).get(var_idx, phi_val)
                        continue

                    # Replace uses of old_val with phi_val in this block
                    # and all blocks dominated by it (reachable before seeing old_val's def)
                    self._replace_val_in_block_and_succs(
                        func, block, old_val, phi_val, block_entry_vars, block_exit_vars
                    )
                    changed = True

    def _replace_val_in_block_and_succs(self, func, start_block, old_val, new_val,
                                         block_entry_vars, block_exit_vars):
        """Replace all uses of old_val with new_val in start_block
        and any successor blocks that inherited old_val."""
        visited = set()
        worklist = [start_block]

        while worklist:
            block = worklist.pop()
            if block.label in visited:
                continue
            visited.add(block.label)

            for inst in block.instructions:
                if inst.result is new_val:
                    continue  # Don't replace in the PHI itself
                inst.replace_operand(old_val, new_val)

            # Check if old_val is defined in this block — if so, the block
            # produces its own value so we must not overwrite its exit vars
            # or propagate further.
            defined_here = (hasattr(old_val, 'defining_inst') and
                            old_val.defining_inst is not None and
                            getattr(old_val.defining_inst, 'block', None) is block)
            if defined_here:
                continue

            # Update block entry/exit vars
            for var_idx, val in list(block_entry_vars.get(block.label, {}).items()):
                if val is old_val:
                    block_entry_vars[block.label][var_idx] = new_val
            for var_idx, val in list(block_exit_vars.get(block.label, {}).items()):
                if val is old_val:
                    block_exit_vars[block.label][var_idx] = new_val

            # Propagate to successors that used old_val
            for succ in block.successors:
                if succ.label not in visited:
                    worklist.append(succ)


def build_ir(bytecode_text: str) -> Module:
    """Convenience function: parse bytecode text and return IR module."""
    lines = bytecode_text.split('\n')
    builder = IRBuilder()
    return builder.build(lines)
