"""Type system and lattice-based type inference for fr SSA IR.

The type lattice flows information forward through the IR, giving precise types
at every point. This enables type-specialized codegen (mov for int, movsd for float)
and drives escape analysis for struct allocation tier decisions.
"""
from __future__ import annotations
from optimizer.ir import (
    Module, Function, BasicBlock, Instruction, Value, Constant, Param,
    Op, IRType, StructType, ListType, ValueType,
)


class TypeLattice:
    """Forward type propagation over SSA IR.

    For each Value, determines the most precise type. Handles phi nodes by
    computing the join (least upper bound) of incoming types.
    """

    def __init__(self, module: Module):
        self.module = module
        # Map value id → resolved type
        self.types: dict[int, ValueType] = {}

    def run(self):
        """Run type inference on all functions."""
        for func in self.module.functions:
            self._infer_function(func)

    def _infer_function(self, func: Function):
        # Seed parameters
        for p in func.params:
            self.types[p.id] = p.type

        # Fixed-point iteration (needed for phi nodes in loops)
        changed = True
        while changed:
            changed = False
            for block in func.blocks:
                for inst in block.instructions:
                    if inst.result is None:
                        continue
                    new_type = self._infer_instruction(inst)
                    if new_type is not None:
                        old = self.types.get(inst.result.id)
                        if old != new_type:
                            self.types[inst.result.id] = new_type
                            inst.result.type = new_type
                            changed = True

    def _infer_instruction(self, inst: Instruction) -> ValueType | None:
        op = inst.op

        # Constants already have types
        if op == Op.CONST_INT:
            return IRType.INT64
        if op == Op.CONST_FLOAT:
            return IRType.FLOAT64
        if op == Op.CONST_STR:
            return IRType.STRING
        if op == Op.CONST_BOOL:
            return IRType.BOOL

        # Integer arithmetic → int
        if op in (Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.NEG,
                  Op.SHL, Op.SHR, Op.BIT_AND, Op.BIT_OR, Op.BIT_XOR):
            return IRType.INT64

        # Float arithmetic → float
        if op in (Op.FADD, Op.FSUB, Op.FMUL, Op.FDIV, Op.FNEG):
            return IRType.FLOAT64

        # Comparisons → bool
        if op in (Op.LT, Op.GT, Op.LE, Op.GE, Op.EQ, Op.NE):
            return IRType.BOOL

        # Logic → bool
        if op in (Op.AND, Op.OR, Op.NOT):
            return IRType.BOOL

        # Conversions
        if op == Op.INT_TO_FLOAT:
            return IRType.FLOAT64
        if op == Op.FLOAT_TO_INT:
            return IRType.INT64
        if op == Op.TO_STR:
            return IRType.STRING
        if op == Op.TO_BOOL:
            return IRType.BOOL

        # Struct operations
        if op == Op.ALLOC_STRUCT and inst.imm_str:
            st = self.module.struct_types.get(inst.imm_str)
            if st:
                return st
            return IRType.INT64  # fallback

        if op == Op.LOAD_FIELD:
            # Operand 0 is the struct pointer, imm_int is field index
            if inst.operands:
                struct_type = self._get_type(inst.operands[0])
                if isinstance(struct_type, StructType) and inst.imm_int is not None:
                    idx = inst.imm_int
                    if 0 <= idx < len(struct_type.field_types):
                        return struct_type.field_types[idx]
            return IRType.INT64  # fallback

        # List operations
        if op == Op.ALLOC_LIST:
            return ListType(IRType.INT64)  # default, refined by context
        if op == Op.LIST_GET:
            if inst.operands:
                list_type = self._get_type(inst.operands[0])
                if isinstance(list_type, ListType):
                    return list_type.elem_type
            return IRType.INT64
        if op == Op.LIST_LEN:
            return IRType.INT64

        # String
        if op == Op.STR_CONCAT:
            return IRType.STRING
        if op == Op.STR_LEN:
            return IRType.INT64

        # Function calls
        if op == Op.CALL:
            target = self.module.get_function(inst.imm_str) if inst.imm_str else None
            if target:
                return target.return_type
            return IRType.INT64
        if op in (Op.CALL_EXTERN, Op.CALL_BUILTIN):
            # Externals and builtins: type comes from imm metadata
            return inst.result.type if inst.result else IRType.VOID

        # Phi: join all incoming types
        if op == Op.PHI:
            return self._join_types([self._get_type(v) for v in inst.operands])

        # Copy
        if op == Op.COPY and inst.operands:
            return self._get_type(inst.operands[0])

        # Select
        if op == Op.SELECT and len(inst.operands) >= 3:
            return self._join_types([
                self._get_type(inst.operands[1]),
                self._get_type(inst.operands[2]),
            ])

        # Math
        if op in (Op.SQRT, Op.SIN, Op.COS, Op.TAN, Op.POW):
            return IRType.FLOAT64
        if op in (Op.ABS, Op.MIN, Op.MAX, Op.FLOOR, Op.CEIL, Op.ROUND):
            if inst.operands:
                return self._get_type(inst.operands[0])
            return IRType.INT64

        # Globals
        if op == Op.LOAD_GLOBAL and inst.imm_str:
            return self.module.global_vars.get(inst.imm_str, IRType.INT64)

        # I/O
        if op == Op.INPUT:
            return IRType.STRING
        if op in (Op.PRINT, Op.PRINTLN):
            return IRType.VOID

        return inst.result.type if inst.result else None

    def _get_type(self, v: Value) -> ValueType:
        if v.id in self.types:
            return self.types[v.id]
        return v.type

    def _join_types(self, types: list[ValueType]) -> ValueType:
        """Compute the least upper bound of a set of types."""
        types = [t for t in types if t is not None]
        if not types:
            return IRType.INT64

        result = types[0]
        for t in types[1:]:
            if t == result:
                continue
            # StructType join: if same struct, keep it; otherwise fall to INT64
            if isinstance(result, StructType) and isinstance(t, StructType):
                if result.name == t.name:
                    continue
                return IRType.INT64
            # ListType join
            if isinstance(result, ListType) and isinstance(t, ListType):
                result = ListType(self._join_types([result.elem_type, t.elem_type]))
                continue
            # Mixed numeric: int + float → float
            if {result, t} <= {IRType.INT64, IRType.FLOAT64}:
                result = IRType.FLOAT64
                continue
            # Incompatible → INT64 (conservative fallback)
            return IRType.INT64

        return result


class EscapeAnalysis:
    """Determine which struct allocations can be stack-allocated or SROA'd.

    Escape states:
    - NO_ESCAPE: struct never leaves the function → SROA candidate
    - ARG_ESCAPE: struct passed to callee but not stored → stack allocate
    - FULL_ESCAPE: struct returned, stored in list/global → heap allocate
    """

    NO_ESCAPE = 0
    ARG_ESCAPE = 1
    FULL_ESCAPE = 2

    def __init__(self, module: Module):
        self.module = module
        # Map value id → escape state
        self.escape: dict[int, int] = {}

    def run(self):
        for func in self.module.functions:
            self._analyze_function(func)

    def _analyze_function(self, func: Function):
        # Initialize all ALLOC_STRUCT as non-escaping
        alloc_values = set()
        for inst in func.all_instructions():
            if inst.op == Op.ALLOC_STRUCT and inst.result:
                self.escape[inst.result.id] = self.NO_ESCAPE
                alloc_values.add(inst.result.id)

        # Propagate escape through uses
        changed = True
        while changed:
            changed = False
            for inst in func.all_instructions():
                for op_val in inst.operands:
                    if not isinstance(op_val, Value) or op_val.id not in alloc_values:
                        continue
                    vid = op_val.id
                    current = self.escape.get(vid, self.NO_ESCAPE)

                    new_state = current
                    if inst.op == Op.RETURN:
                        new_state = self.FULL_ESCAPE
                    elif inst.op in (Op.STORE_GLOBAL, Op.LIST_APPEND, Op.LIST_SET):
                        new_state = self.FULL_ESCAPE
                    elif inst.op in (Op.CALL, Op.CALL_EXTERN, Op.CALL_BUILTIN):
                        new_state = max(new_state, self.ARG_ESCAPE)
                    elif inst.op == Op.STORE_FIELD:
                        # Storing a struct into another struct's field → full escape
                        if op_val is not inst.operands[0]:  # it's the value, not the target
                            new_state = self.FULL_ESCAPE
                    elif inst.op == Op.PHI:
                        # Phi merges: if any incoming value escapes, the phi result escapes
                        # and the phi result should propagate back to sources
                        pass

                    if new_state > current:
                        self.escape[vid] = new_state
                        changed = True

    def get_escape(self, value: Value) -> int:
        return self.escape.get(value.id, self.FULL_ESCAPE)

    def can_sroa(self, value: Value) -> bool:
        """Can this allocation be replaced with scalar values?"""
        return self.get_escape(value) == self.NO_ESCAPE

    def can_stack_alloc(self, value: Value) -> bool:
        """Can this allocation be placed on the stack?"""
        return self.get_escape(value) <= self.ARG_ESCAPE
