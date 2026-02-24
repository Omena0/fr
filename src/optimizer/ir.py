"""SSA Intermediate Representation for fr.

Every value is assigned exactly once. Control flow is explicit via basic blocks
with phi nodes at merge points. Structs are direct pointers with field offsets.
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional


class IRType(Enum):
    INT64 = auto()
    FLOAT64 = auto()
    BOOL = auto()
    STRING = auto()
    VOID = auto()
    # Parameterized types use StructType / ListType wrappers below


@dataclass
class StructType:
    name: str
    field_names: list[str] = field(default_factory=list)
    field_types: list[IRType] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.field_names) * 8

    def field_offset(self, idx: int) -> int:
        return idx * 8

    def __hash__(self):
        return hash(('struct', self.name))

    def __eq__(self, other):
        return isinstance(other, StructType) and self.name == other.name


@dataclass
class ListType:
    elem_type: IRType | StructType

    def __hash__(self):
        return hash(('list', self.elem_type))

    def __eq__(self, other):
        return isinstance(other, ListType) and self.elem_type == other.elem_type


@dataclass
class SetType:
    elem_type: IRType | StructType = IRType.INT64

    def __hash__(self):
        return hash(('set', self.elem_type))

    def __eq__(self, other):
        return isinstance(other, SetType) and self.elem_type == other.elem_type


# A ValueType is the type of any SSA value
ValueType = IRType | StructType | ListType | SetType


class Op(Enum):
    # Constants
    CONST_INT = auto()
    CONST_FLOAT = auto()
    CONST_STR = auto()
    CONST_BOOL = auto()

    # Integer arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()

    # Float arithmetic
    FADD = auto()
    FSUB = auto()
    FMUL = auto()
    FDIV = auto()
    FNEG = auto()

    # Comparison
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    EQ = auto()
    NE = auto()

    # Logic
    AND = auto()
    OR = auto()
    NOT = auto()

    # Bitwise
    SHL = auto()
    SHR = auto()
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()

    # Struct (direct pointer model)
    ALLOC_STRUCT = auto()   # allocate struct, returns pointer
    LOAD_FIELD = auto()     # load field from struct pointer
    STORE_FIELD = auto()    # store field to struct pointer (void)

    # List
    ALLOC_LIST = auto()
    LIST_GET = auto()
    LIST_SET = auto()
    LIST_APPEND = auto()
    LIST_LEN = auto()

    # String
    STR_CONCAT = auto()
    STR_LEN = auto()

    # Type conversion
    INT_TO_FLOAT = auto()
    FLOAT_TO_INT = auto()
    TO_STR = auto()
    TO_BOOL = auto()

    # Function calls
    CALL = auto()           # direct call to fr function
    CALL_EXTERN = auto()    # C FFI call
    CALL_BUILTIN = auto()   # built-in (print, len, input, etc.)

    # Control flow (block terminators)
    BRANCH = auto()         # conditional: cond, true_label, false_label
    JUMP = auto()           # unconditional: target_label
    RETURN = auto()         # return value
    RETURN_VOID = auto()    # return nothing

    # SSA
    PHI = auto()            # phi(val_from_block_a, val_from_block_b, ...)

    # Special
    COPY = auto()           # %dst = %src (used during SSA construction, eliminated later)
    NOP = auto()            # no operation (placeholder, eliminated in DCE)

    # Math builtins
    SQRT = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    ABS = auto()
    MIN = auto()
    MAX = auto()
    FLOOR = auto()
    CEIL = auto()
    ROUND = auto()
    POW = auto()

    # Global variables
    LOAD_GLOBAL = auto()
    STORE_GLOBAL = auto()

    # I/O (side-effecting — never eliminated by DCE)
    PRINT = auto()
    PRINTLN = auto()
    INPUT = auto()

    # Select (branchless conditional: result = cond ? true_val : false_val)
    SELECT = auto()

    # Exception handling
    TRY_BEGIN = auto()    # push handler + setjmp + branch to except
    TRY_END = auto()      # pop exception handler
    RAISE = auto()        # raise exception (noreturn)


# Operations that have side effects and must not be eliminated by DCE
SIDE_EFFECT_OPS = frozenset({
    Op.STORE_FIELD, Op.LIST_SET, Op.LIST_APPEND,
    Op.CALL, Op.CALL_EXTERN, Op.CALL_BUILTIN,
    Op.BRANCH, Op.JUMP, Op.RETURN, Op.RETURN_VOID,
    Op.STORE_GLOBAL, Op.PRINT, Op.PRINTLN, Op.INPUT,
    Op.TRY_BEGIN, Op.TRY_END, Op.RAISE,
    Op.DIV, Op.MOD, Op.FDIV,  # division can raise ZeroDivisionError
})

# Operations that are terminators (must be last in a basic block)
TERMINATOR_OPS = frozenset({
    Op.BRANCH, Op.JUMP, Op.RETURN, Op.RETURN_VOID,
    Op.TRY_BEGIN,
})

# Commutative operations (operand order doesn't matter for CSE)
COMMUTATIVE_OPS = frozenset({
    Op.ADD, Op.MUL, Op.FADD, Op.FMUL,
    Op.EQ, Op.NE, Op.AND, Op.OR,
    Op.BIT_AND, Op.BIT_OR, Op.BIT_XOR,
    Op.MIN, Op.MAX,
})


class Value:
    """An SSA value. Defined by exactly one instruction."""

    __slots__ = ('id', 'type', 'defining_inst', 'uses')

    _next_id = 0

    def __init__(self, typ: ValueType, defining_inst: Optional[Instruction] = None):
        self.id = Value._next_id
        Value._next_id += 1
        self.type = typ
        self.defining_inst = defining_inst
        self.uses: list[Instruction] = []  # instructions that use this value

    def __repr__(self):
        return f'%{self.id}'

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, Value) and self.id == other.id

    @staticmethod
    def reset_counter():
        Value._next_id = 0


class Constant(Value):
    """A constant value known at compile time."""

    __slots__ = ('value',)

    def __init__(self, typ: ValueType, value):
        super().__init__(typ)
        self.value = value

    def __repr__(self):
        if self.type == IRType.STRING:
            return f'"{self.value}"'
        return str(self.value)


class Param(Value):
    """A function parameter."""

    __slots__ = ('name', 'index')

    def __init__(self, name: str, typ: ValueType, index: int):
        super().__init__(typ)
        self.name = name
        self.index = index

    def __repr__(self):
        return f'%{self.name}'


class Instruction:
    """A single SSA instruction. Produces at most one Value."""

    __slots__ = ('op', 'result', 'operands', 'block', 'source_line',
                 'imm_int', 'imm_str', 'imm_float', 'target_blocks')

    def __init__(self, op: Op, operands: list[Value] = None,
                 result_type: ValueType = None, source_line: int = None):
        self.op = op
        self.operands: list[Value] = operands or []
        self.block: Optional[BasicBlock] = None
        self.source_line = source_line

        # Immediates (for constants, field indices, function names, labels)
        self.imm_int: Optional[int] = None
        self.imm_str: Optional[str] = None
        self.imm_float: Optional[float] = None
        self.target_blocks: list[BasicBlock] = []  # for BRANCH/JUMP

        # Create result value if the instruction produces one
        if result_type is not None and result_type != IRType.VOID:
            self.result = Value(result_type, defining_inst=self)
        else:
            self.result = None

        # Register operand uses
        for v in self.operands:
            if isinstance(v, Value):
                v.uses.append(self)

    def replace_operand(self, old: Value, new: Value):
        """Replace all uses of old with new in this instruction."""
        for i, op in enumerate(self.operands):
            if op is old:
                self.operands[i] = new
                old.uses.remove(self)
                new.uses.append(self)

    def remove_from_uses(self):
        """Remove this instruction from all operand use lists."""
        for v in self.operands:
            if isinstance(v, Value) and self in v.uses:
                v.uses.remove(self)

    @property
    def is_terminator(self) -> bool:
        return self.op in TERMINATOR_OPS

    @property
    def has_side_effects(self) -> bool:
        return self.op in SIDE_EFFECT_OPS

    def __repr__(self):
        parts = []
        if self.result:
            parts.append(f'{self.result} =')
        parts.append(self.op.name)
        for op in self.operands:
            parts.append(str(op))
        if self.imm_int is not None:
            parts.append(str(self.imm_int))
        if self.imm_str is not None:
            parts.append(f'"{self.imm_str}"')
        if self.imm_float is not None:
            parts.append(str(self.imm_float))
        for blk in self.target_blocks:
            parts.append(blk.label)
        return ' '.join(parts)


class BasicBlock:
    """A basic block — straight-line code with a single entry and exit."""

    __slots__ = ('label', 'instructions', 'predecessors', 'successors', 'func')

    def __init__(self, label: str):
        self.label = label
        self.instructions: list[Instruction] = []
        self.predecessors: list[BasicBlock] = []
        self.successors: list[BasicBlock] = []
        self.func: Optional[Function] = None

    def append(self, inst: Instruction):
        inst.block = self
        self.instructions.append(inst)

    def insert_before_terminator(self, inst: Instruction):
        """Insert instruction before the block's terminator."""
        inst.block = self
        if self.instructions and self.instructions[-1].is_terminator:
            self.instructions.insert(len(self.instructions) - 1, inst)
        else:
            self.instructions.append(inst)

    @property
    def terminator(self) -> Optional[Instruction]:
        if self.instructions and self.instructions[-1].is_terminator:
            return self.instructions[-1]
        return None

    @property
    def phi_nodes(self) -> list[Instruction]:
        return [i for i in self.instructions if i.op == Op.PHI]

    def __repr__(self):
        return f'BB({self.label})'

    def __hash__(self):
        return hash(self.label)


class Function:
    """An SSA function with basic blocks."""

    __slots__ = ('name', 'params', 'return_type', 'blocks', 'entry',
                 'is_extern', 'source_file', 'local_names')

    def __init__(self, name: str, params: list[Param] = None,
                 return_type: ValueType = IRType.VOID):
        self.name = name
        self.params: list[Param] = params or []
        self.return_type = return_type
        self.blocks: list[BasicBlock] = []
        self.entry: Optional[BasicBlock] = None
        self.is_extern = False
        self.source_file: Optional[str] = None
        self.local_names: dict[int, str] = {}  # maps var index → name for debugging

    def add_block(self, block: BasicBlock) -> BasicBlock:
        block.func = self
        self.blocks.append(block)
        if self.entry is None:
            self.entry = block
        return block

    def all_instructions(self):
        """Iterate over all instructions in all blocks."""
        for block in self.blocks:
            yield from block.instructions

    def all_values(self):
        """Iterate over all Values defined in this function."""
        yield from self.params
        for inst in self.all_instructions():
            if inst.result is not None:
                yield inst.result

    def __repr__(self):
        return f'Function({self.name})'


class Module:
    """Top-level IR module containing all functions and struct definitions."""

    __slots__ = ('functions', 'struct_types', 'entry_func', 'source_file',
                 'string_constants', 'global_vars')

    def __init__(self):
        self.functions: list[Function] = []
        self.struct_types: dict[str, StructType] = {}
        self.entry_func: Optional[str] = None
        self.source_file: Optional[str] = None
        self.string_constants: list[str] = []  # pooled string literals
        self.global_vars: dict[str, ValueType] = {}

    def get_function(self, name: str) -> Optional[Function]:
        for f in self.functions:
            if f.name == name:
                return f
        return None

    def add_function(self, func: Function):
        self.functions.append(func)

    def add_struct(self, struct: StructType):
        self.struct_types[struct.name] = struct


def _type_name(t: ValueType) -> str:
    """Get a concise type name for display."""
    if isinstance(t, IRType):
        return t.name.lower()
    if isinstance(t, StructType):
        return t.name
    if isinstance(t, ListType):
        return f'list[{_type_name(t.elem_type)}]'
    return str(t)


def dump_module(module: Module) -> str:
    """Dump the IR module as a human-readable text format (similar to LLVM IR)."""
    lines = []
    lines.append(f'; module: {module.source_file or "<unknown>"}')

    # Struct definitions
    for name, st in module.struct_types.items():
        fields = ', '.join(
            f'{_type_name(ft)} {fn}'
            for fn, ft in zip(st.field_names, st.field_types)
        )
        lines.append(f'struct {name} {{ {fields} }}  ; size={st.size}')

    lines.append('')

    # Functions
    for func in module.functions:
        ret = _type_name(func.return_type)
        params_str = ', '.join(
            f'{_type_name(p.type)} {p.name}'
            for p in func.params
        )
        lines.append(f'function {ret} @{func.name}({params_str}) {{')

        for block in func.blocks:
            preds = ', '.join(b.label for b in block.predecessors)
            lines.append(f'  {block.label}:{f"  ; preds: {preds}" if preds else ""}')

            for inst in block.instructions:
                line_info = f'  ; line {inst.source_line}' if inst.source_line else ''
                lines.append(f'    {inst}{line_info}')

            lines.append('')

        lines.append('}')
        lines.append('')

    if module.entry_func:
        lines.append(f'; entry: @{module.entry_func}')

    return '\n'.join(lines)
