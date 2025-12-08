from typing import List, Dict, Tuple, Optional

# Simple, local type analyzer used by WasmCompiler to compute per-instruction
# abstract stack shapes (i64/i32/f64/str/list/set/struct:ID). This file defines a
# minimal analyzer we can import from the Wasm compiler to keep things modular.


def merge_type(a: Optional[str], b: Optional[str]) -> str:
    """Merge two abstract types into one conservative result.

    Rules:
    - identical: keep
    - i32 vs i64 -> prefer i64
    - i64 vs f64 -> prefer i64 (conservative; could be improved)
    - str prefers str
    - list/set: keep as-is
    - None -> take other
    """
    if a == b:
        return a or 'i64'
    if a is None:
        return b or 'i64'
    if b is None:
        return a
    if ({a, b} <= {'i32', 'i64'}) or ({a, b} <= {'i64', 'i32'}):
        return 'i64'
    # Prefer semantic high level types when present
    if 'str' in {a, b}:
        return 'str'
    if 'list' in {a, b}:
        return 'list'
    if 'set' in {a, b}:
        return 'set'
    return 'bool' if 'bool' in {a, b} else 'i64'


def apply_instr_semantics(instr: str, args: List[str], stack: List[str], locals_types: Dict[int, str]) -> List[str]:
    """Apply opcode semantics to an abstract stack (list of slots) and return new stack.

    instr is opcode name, args are list of arguments (strings). stack is a list where stack[-1]
    is top. The function returns new stack list.
    """
    s = stack.copy()
    op = instr

    if op == 'CONST_I64':
        s.extend('i64' for _ in args)
        return s
    if op == 'CONST_F64':
        s.extend('f64' for _ in args)
        return s
    if op == 'CONST_STR':
        s.append('str')
        return s
    if op == 'CONST_BYTES':
        # Represent raw bytes as a string-like value for analysis
        s.append('str')
        return s
    if op == 'CONST_BOOL':
        s.append('bool')
        return s
    if op in {'LIST_NEW', 'LIST_NEW_STR', 'LIST_NEW_I64', 'LIST_NEW_LITERAL'}:
        s.append('list')
        return s
    if op == 'SET_NEW':
        s.append('set')
        return s
    if op == 'STRUCT_NEW':
        # STRUCT_NEW pops field values and pushes a struct reference
        # We can't concrete field counts here, so be conservative
        s.append('struct')
        return s
    if op == 'STRUCT_GET':
        # STRUCT_GET pops struct reference and pushes the selected field
        if s:
            s.pop()
        # Unknown field type; default to i64
        s.append('i64')
        return s
    if op == 'STRUCT_SET':
        # STRUCT_SET pops value and struct, pushes struct
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('struct')
        return s
    if op in {'LIST_APPEND', 'SET_ADD', 'SET_REMOVE'}:
        # consumes value and container, pushes container
        if len(s) >= 2:
            s.pop()
            s.pop()
        if op == 'LIST_APPEND' or not op.startswith('SET'):
            s.append('list')
        else:
            s.append('set')
        return s
    if op == 'LIST_GET':
        # consumes list and index
        if len(s) >= 2:
            s.pop()
            s.pop()
        # default to i64 return
        s.append('i64')
        return s
    if op == 'LIST_LEN':
        if s:
            s.pop()
        s.append('i64')
        return s
    if op == 'LIST_SET':
        # LIST_SET pops value, index, list and pushes list
        if len(s) >= 3:
            s.pop()
            s.pop()
            s.pop()
        s.append('list')
        return s
    if op == 'LIST_POP':
        # LIST_POP pops list and pushes list and value
        if s:
            s.pop()
        s.extend(('list', 'i64'))
        return s
    if op == 'SET_CONTAINS':
        # SET_CONTAINS pops value and set, pushes bool
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('bool')
        return s
    if op == 'LOAD':
        # LOAD idx1 [idx2 ...]
        for a in args:
            idx = int(a)
            if idx in locals_types:
                s.append(locals_types[idx])
            else:
                s.append('i64')
        return s

    if op in {
        'STR_SPLIT',
        'STR_JOIN',
        'STR_GET',
        'STR_CONTAINS',
        'STR_REPLACE',
    }:
        # Various string operations - handle conservatively
        # STR_SPLIT: pops string and sep -> push list
        if op == 'STR_SPLIT':
            # pop two strings if present
            if len(s) >= 2:
                s.pop()
                s.pop()
            s.append('list')
            return s
        # STR_JOIN: pop list and separator -> push str
        if op == 'STR_JOIN':
            if len(s) >= 2:
                s.pop()
                s.pop()
            s.append('str')
            return s
        # STR_GET: pop str and index -> push char (str)
        if op == 'STR_GET':
            if len(s) >= 2:
                s.pop()
                s.pop()
            s.append('str')
            return s
        # STR_CONTAINS/REPLACE: pop args and push bool or str
        if op == 'STR_CONTAINS':
            # pops the needle and haystack -> bool
            if len(s) >= 2:
                s.pop()
                s.pop()
            s.append('bool')
            return s
        # pops old,new,haystack -> push str
        for _ in range(min(3, len(s))):
            s.pop()
        s.append('str')
        return s
    if op in {'BUILTIN_PRINT', 'BUILTIN_PRINTLN'}:
        # Pop a value (string or primitive) and produce no result
        if s:
            s.pop()
        return s
    if op == 'BUILTIN_PI':
        # PI is a constant f64
        s.append('f64')
        return s
    if op == 'BUILTIN_SQRT':
        # consumes f64, returns f64
        if s:
            s.pop()
        s.append('f64')
        return s
    if op == 'BUILTIN_ROUND':
        # consumes f64, returns i64
        if s:
            s.pop()
        s.append('i64')
        return s
    if op.startswith('CMP_'):
        # Comparison operations: pop two operands (or one if CONST) and push a bool
        if 'CONST' in op:
            # CMP_*_CONST <const> - consumes top and pushes bool
            if s:
                s.pop()
            s.append('i32')
            return s
        # generic binary compare
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('i32')
        return s
    # Binary numeric ops
    if op in {
        'ADD_I64',
        'SUB_I64',
        'MUL_I64',
        'DIV_I64',
        'MOD_I64',
        'ADD_F64',
        'SUB_F64',
        'MUL_F64',
        'DIV_F64',
    }:
        if len(s) >= 2:
            s.pop()
            s.pop()
        # choose numeric return type based on op suffix
        if op.endswith('_F64'):
            s.append('f64')
        else:
            s.append('i64')
        return s
    if op == 'DUP':
        if s:
            s.append(s[-1])
        return s
    if op == 'NEG':
        # Negation: preserves numeric type; otherwise assume i64
        if s:
            top = s.pop()
            s.append(top if top in ('i64', 'f64') else 'i64')
        return s
    if op in {'AND', 'OR'}:
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('i32')
        return s
    if op == 'NOT':
        if s:
            s.pop()
        s.append('i32')
        return s
    if op in {'CONTAINS', 'STR_EQ'}:
        # These result in a bool for containment/test operations
        # Pop relevant args conservatively (2) and push bool
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('bool')
        return s
    if op in {'STR_LOWER', 'STR_UPPER', 'STR_STRIP'}:
        # These transform a string and return a string
        # Pop string and push string
        if s:
            s.pop()
        s.append('str')
        return s
    if op == 'ADD_STR':
        # ADD_STR semantics (matching C runtime):
        # - If both operands are i64: add as integers -> result is i64
        # - If both operands are f64: add as floats -> result is f64
        # - If both operands are str: concatenate -> result is str
        # - Otherwise: convert to strings and concat -> result is str
        if len(s) >= 2:
            top = s[-1]
            second = s[-2]
            s.pop()
            s.pop()
            if top == 'i64' and second == 'i64':
                s.append('i64')
            elif top == 'f64' and second == 'f64':
                s.append('f64')
            else:
                s.append('str')
        elif len(s) == 1:
            s.pop()
            s.append('str')
        else:
            s.append('str')
        return s
    if op == 'TO_BOOL':
        if s:
            s.pop()
        s.append('bool')
        return s
    if op == 'TO_INT':
        if s:
            s.pop()
        s.append('i64')
        return s
    if op == 'TO_FLOAT':
        if s:
            s.pop()
        s.append('f64')
        return s
    if op.startswith('STORE_CONST_'):
        # STORE_CONST_TYPE idx val [idx val ...] - does not modify stack but updates locals
        for i in range(0, len(args), 2):
            try:
                idx = int(args[i])
            except Exception:
                continue
            # Determine type from opcode suffix
            suffix = op.replace('STORE_CONST_', '')
            if suffix == 'I64':
                locals_types[idx] = 'i64'
            elif suffix == 'F64':
                locals_types[idx] = 'f64'
            elif suffix == 'STR':
                locals_types[idx] = 'str'
            elif suffix == 'BOOL':
                locals_types[idx] = 'bool'
        return s
    if op.startswith('ADD_CONST_'):
        # Pop nothing, but ensure top is correct type: i64 or f64
        suffix = op.replace('ADD_CONST_', '')
        if s:
            # If top is different, coerce to i64/f64 by mapping
            if suffix == 'I64':
                # top becomes i64
                s[-1] = 'i64'
            elif suffix == 'F64':
                s[-1] = 'f64'
        else:
            # stack empty, push a value of the correct type
            s.append('i64' if suffix == 'I64' else 'f64')
        return s
    if op.startswith('SUB_CONST_') or op.startswith('MUL_CONST_') or op.startswith('DIV_CONST_') or op.startswith('MOD_CONST_'):
        # Ensure top entry has the appropriate numeric type
        # We don't change stack height, just the type of the top entry
        if op.startswith('MOD_CONST_'):
            suffix = op.replace('MOD_CONST_', '')
        elif op.startswith('SUB_CONST_'):
            suffix = op.replace('SUB_CONST_', '')
        elif op.startswith('MUL_CONST_'):
            suffix = op.replace('MUL_CONST_', '')
        else:
            suffix = op.replace('DIV_CONST_', '')
        if s:
            s[-1] = 'i64' if suffix == 'I64' else 'f64'
        else:
            s.append('i64' if suffix == 'I64' else 'f64')
        return s
    if op in {'INC_LOCAL', 'DEC_LOCAL'}:
        # No stack change but ensure local type is numeric
        # arg is idx
        if args:
            try:
                idx = int(args[0])
                if idx in locals_types and locals_types[idx] == 'i32':
                    locals_types[idx] = 'i64'  # prefer i64 for arithmetic
                elif idx not in locals_types:
                    locals_types[idx] = 'i64'
            except Exception:
                pass
        return s
    if op == 'BUILTIN_LEN':
        # Conservatively consume one composite and return i64
        if s:
            s.pop()
        s.append('i64')
        return s
    if op == 'BUILTIN_STR':
        # Convert top of the stack to string (semantic slot)
        if s:
            s.pop()
        s.append('str')
        return s
    if op == 'FILE_READ':
        # pops fd and size -> pushes string
        if len(s) >= 2:
            s.pop()
            s.pop()
        s.append('str')
        return s
    if op == 'FILE_OPEN':
        # pops two strings (path, mode) -> returns fd (i64)
        for _ in range(min(2, len(s))):
            s.pop()
        s.append('i64')
        return s
    if op == 'FILE_CLOSE':
        if s:
            s.pop()
        return s
    if op == 'FILE_WRITE':
        # pops fd and string (content) -> returns bytes written (i64)
        for _ in range(min(2, len(s))):
            s.pop()
        s.append('i64')
        return s
    if op in {'SOCKET_CREATE', 'SOCKET_RECV', 'SOCKET_CLOSE', 'SOCKET_SEND', 'SOCKET_CONNECT'}:
        # network operations - conservative: pop args and possibly push result
        if op == 'SOCKET_CREATE':
            # Pops two strings (addr family, socket type), pushes socket handle i64
            for _ in range(min(2, len(s))):
                s.pop()
            s.append('i64')
            return s
        if op == 'SOCKET_RECV':
            # Pops socket (i64) and size (i64), pushes string
            for _ in range(min(2, len(s))):
                s.pop()
            s.append('str')
            return s
        if op == 'SOCKET_CONNECT':
            # Pops socket, host, port - pushes nothing
            for _ in range(min(3, len(s))):
                s.pop()
            return s
        if op == 'SOCKET_SEND':
            # Pops socket and message - pushes nothing
            for _ in range(min(2, len(s))):
                s.pop()
            return s
        if op == 'SOCKET_CLOSE':
            # Pops socket - pushes nothing
            if s:
                s.pop()
            return s
        return s
    if op == 'STORE':
        # STORE idx - pop corresponding value
        if s:
            s.pop()
        return s
    if op == 'CALL':
        # Generic call - unknown signature; do not change stack (conservative)
        return s
    if op in {'PY_CALL', 'PY_CALL_METHOD', 'PY_GETATTR', 'PY_SETATTR', 'PY_IMPORT'}:
        # Python interop - unknown semantics, preserve stack conservatively
        return s
    if op == 'FUSED_LOAD_STORE':
        # Compiler-managed op for merging loads/stores; no immediate stack change here
        return s
    if op == 'POP':
        if s:
            s.pop()
        return s
    if op == 'LABEL':
        # Labels don't affect the stack
        return s
    if op in {'JUMP', 'JUMP_IF_FALSE', 'JUMP_IF_TRUE', 'RETURN', 'RETURN_VOID'}:
        # JUMP: no stack effect
        if op == 'JUMP':
            return s
        # Conditional jumps consume a boolean
        if op in {'JUMP_IF_FALSE', 'JUMP_IF_TRUE'}:
            if s:
                s.pop()
            return s
        # For returns, clear the stack
        if op in {'RETURN', 'RETURN_VOID'}:
            return []
    return s

