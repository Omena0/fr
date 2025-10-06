"""
AST to Bytecode Compiler for fr
Compiles typed functions to bytecode format specified in BYTECODE.md
"""

from typing import Any, Dict, List, Optional
from optimizer import BytecodeOptimizer
from parser import parse, AstType, VarType
import sys

flags = sys.argv[1:]

class CompilerError(Exception):
    """Raised when compilation fails"""
    pass

def escape_string_for_bytecode(s: str) -> str:
    """Escape a string for safe embedding in bytecode CONST_STR instructions."""
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('\n', '\\n')
             .replace('\r', '\\r')
             .replace('\t', '\\t')
             .replace('\0', '\\0'))

# Helper functions for AST node type checking
def is_literal_value(node):
    """Check if node is a literal value dict"""
    return (isinstance(node, dict) and 'value' in node and
            'mods' not in node and 'slice' not in node and 'attr' not in node)

def is_var_ref(node: Any) -> bool:
    """Check if node is a variable reference"""
    return isinstance(node, dict) and 'id' in node

def is_fstring(node: Any) -> bool:
    """Check if node is an f-string (JoinedStr)"""
    return isinstance(node, dict) and 'values' in node and 'value' not in node

def is_formatted_value(node: Any) -> bool:
    """Check if node is a FormattedValue (part of f-string)"""
    return isinstance(node, dict) and 'conversion' in node

def is_struct_instance(node: Any) -> bool:
    """Check if node is a struct instance"""
    return isinstance(node, dict) and 'value' in node and 'mods' in node

def is_function_call(node: Any) -> bool:
    """Check if node is a function call"""
    return isinstance(node, dict) and 'func' in node

def extract_func_name(func_node: Any) -> str:
    """Extract function name from function call node"""
    if isinstance(func_node, dict):
        return func_node.get('id', '')
    return str(func_node)

class BytecodeCompiler:
    def __init__(self):
        self.output: List[str] = []
        self.label_counter = 0
        self.var_mapping: Dict[str, int] = {}  # Maps var names to IDs
        self.var_types: Dict[str, str] = {}  # Maps var names to their types
        self.next_var_id = 0
        self.loop_stack: List[tuple] = []  # Stack of (loop_start_label, loop_end_label) for break/continue
        self.struct_defs: Dict[str, Dict[str, Any]] = {}  # Maps struct names to their definitions
        self.struct_id_counter = 0  # Unique ID for each struct type
        # Tracks Python imports: maps alias/name -> module info
        # For "py_import datetime as dt": {'dt': {'module': 'datetime', 'type': 'module'}}
        # For "from datetime py_import datetime": {'datetime': {'module': 'datetime', 'type': 'name', 'name': 'datetime'}}
        self.py_imports: Dict[str, Dict[str, Any]] = {}

    def get_label(self, prefix: str = "L") -> str:
        """Generate a unique label"""
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def emit(self, instruction: str):
        """Add an instruction to the current function's bytecode"""
        self.output.append(f"  {instruction}")

    def get_var_id(self, name: str) -> int:
        """Get or create variable ID"""
        if name not in self.var_mapping:
            self.var_mapping[name] = self.next_var_id
            self.next_var_id += 1
        return self.var_mapping[name]

    def check_function_typed(self, func_node: dict) -> bool:
        """Check if function has all arguments typed"""
        args = func_node.get('args', [])

        # Handle both formats: list of tuples/lists or list of strings
        for arg in args:
            if isinstance(arg, (tuple, list)) and len(arg) == 2:
                arg_name, type_annotation = arg
                if type_annotation is None:
                    return False
            elif isinstance(arg, str):
                # Old format - untyped
                return False

        return True

    def map_type(self, type_str: Optional[str]) -> str:
        """Map fr types to bytecode types"""
        if not type_str or type_str == 'none':
            return 'void'

        type_map = {
            'int': 'i64',
            'i64': 'i64',
            'float': 'f64',
            'f64': 'f64',
            'string': 'str',
            'str': 'str',
            'bool': 'bool',
            'void': 'void',
            'pyobject': 'i64',  # Python objects stored as generic value
            'pyobj': 'i64',     # Alias for pyobject
            'any': 'i64',
        }

        return type_map.get(type_str, 'i64')  # Default to i64

    def normalize_type(self, type_str: str) -> str:
        """Normalize type aliases to their canonical form"""
        type_aliases = {
            'str': 'string',
            'pyobj': 'pyobject',
        }
        return type_aliases.get(type_str, type_str)

    def compile_expr(self, expr: Any, expr_type: str = 'i64'):
        """Compile an expression node to bytecode (pushes result to stack)"""
        if expr is None:
            self.emit("CONST_I64 0")
            return

        # Literal list (Python list object)
        if isinstance(expr, list):
            # Create new list
            self.emit("LIST_NEW")
            # Append each element
            for elem in expr:
                self.compile_expr(elem, expr_type)  # Push element
                self.emit("LIST_APPEND")  # Append and push back list (list, elem -> list)
            return

        # Literal boolean (must be before int since bool is subclass of int in Python)
        if isinstance(expr, bool):
            bool_val = 1 if expr else 0
            self.emit(f"CONST_BOOL {bool_val}")
            return

        # Literal integer
        if isinstance(expr, int):
            self.emit(f"CONST_I64 {expr}")
            return

        # Literal float
        if isinstance(expr, float):
            self.emit(f"CONST_F64 {expr}")
            return

        # Literal string
        if isinstance(expr, str):
            # Check if it's a variable reference or a literal string
            if expr in self.var_mapping:
                var_id = self.get_var_id(expr)
                self.emit(f"LOAD {var_id}")
            else:
                # Treat as string literal
                value_str = escape_string_for_bytecode(str(expr))
                self.emit(f'CONST_STR "{value_str}"')
            return

        # Literal value in dict format
        if is_literal_value(expr):
            value = expr['value']

            # Check for list literal in dict format
            if isinstance(value, list):
                # Create new list
                self.emit("LIST_NEW")
                # Append each element
                for elem in value:
                    self.compile_expr(elem, expr_type)  # Push element
                    self.emit("LIST_APPEND")  # Append and push back list (list, elem -> list)
                return

            if isinstance(value, int):
                self.emit(f"CONST_I64 {value}")
            elif isinstance(value, float):
                self.emit(f"CONST_F64 {value}")
            elif isinstance(value, str):
                value_str = escape_string_for_bytecode(str(value))
                self.emit(f'CONST_STR "{value_str}"')
            elif isinstance(value, bool):
                bool_val = 1 if value else 0
                self.emit(f"CONST_BOOL {bool_val}")
            else:
                # Nested expression
                self.compile_expr(value, expr_type)
            return

        # Variable reference with 'id' key
        if is_var_ref(expr):
            var_name = expr['id']

            # Handle boolean literals 'true' and 'false' as keywords
            if var_name == 'true':
                self.emit("CONST_BOOL 1")
                return
            elif var_name == 'false':
                self.emit("CONST_BOOL 0")
                return

            var_id = self.get_var_id(var_name)
            self.emit(f"LOAD {var_id}")
            return

        # Complex expression
        if isinstance(expr, dict):
            # Boolean operations (And, Or): {'op': 'And'/'Or', 'values': [...]}
            # Must check before f-string since both have 'values' key
            if 'op' in expr and expr['op'] in ('And', 'Or') and 'values' in expr:
                op = expr['op']
                values = expr['values']

                # Compile first value
                self.compile_expr(values[0], expr_type)

                # For each subsequent value, compile and apply the operation
                for value in values[1:]:
                    self.compile_expr(value, expr_type)
                    if op == 'And':
                        self.emit("AND")
                    elif op == 'Or':
                        self.emit("OR")
                return

            # F-string (JoinedStr): {'values': [...]}
            if is_fstring(expr):
                # Compile each part and concatenate
                parts = expr['values']
                if not parts:
                    self.emit('CONST_STR ""')
                    return

                # Compile first part
                first_part = parts[0]
                if is_formatted_value(first_part):
                    # FormattedValue - compile expression and convert to string
                    self.compile_expr(first_part['value'], expr_type)
                    self.emit("BUILTIN_STR")
                elif is_literal_value(first_part):
                    # Constant string part
                    value_str = escape_string_for_bytecode(str(first_part['value']))
                    self.emit(f'CONST_STR "{value_str}"')
                else:
                    self.compile_expr(first_part, expr_type)

                # Compile and concatenate remaining parts
                for part in parts[1:]:
                    if is_formatted_value(part):
                        # FormattedValue - compile expression and convert to string
                        self.compile_expr(part['value'], expr_type)
                        self.emit("BUILTIN_STR")
                    elif is_literal_value(part):
                        # Constant string part
                        value_str = escape_string_for_bytecode(str(part['value']))
                        self.emit(f'CONST_STR "{value_str}"')
                    else:
                        self.compile_expr(part, expr_type)
                    # Concatenate with previous result
                    self.emit("ADD_STR")
                return

            # Field access (struct.field or pyobject.attr) - check before slice to avoid confusion
            if 'attr' in expr and 'value' in expr:
                field_name = expr['attr']

                # Check if this is a Python object attribute access
                # First, try to determine the type of the value being accessed
                value_node = expr['value']
                is_pyobject = False

                # If it's a variable reference, check if it's a pyobject
                if isinstance(value_node, dict) and 'id' in value_node:
                    var_name = value_node['id']
                    var_type = self.var_types.get(var_name)
                    if var_type == 'pyobject':
                        is_pyobject = True

                if is_pyobject:
                    # Python object attribute access
                    # Compile: obj, attr_name -> PY_GETATTR
                    self.compile_expr(expr['value'], expr_type)
                    self.emit(f'CONST_STR "{field_name}"')
                    self.emit('PY_GETATTR')
                    return

                # Regular struct field access
                # Compile the struct value (could be a variable, list element, etc.)
                self.compile_expr(expr['value'], expr_type)

                # Determine field index
                # Find first struct that has this field
                field_idx = -1
                for struct_name, struct_def in self.struct_defs.items():
                    if field_name in struct_def['field_map']:
                        field_idx = struct_def['field_map'][field_name]
                        break

                if field_idx < 0:
                    raise ValueError(f"Unknown field: {field_name}")

                self.emit(f"STRUCT_GET {field_idx}")
                return
            # List literal in AST format with 'elts'
            if 'elts' in expr:
                # Create new list
                self.emit("LIST_NEW")
                # Append each element
                for elem in expr['elts']:
                    self.compile_expr(elem, expr_type)  # Push element
                    self.emit("LIST_APPEND")  # Append: pops value and list, pushes modified list
                return

            # List/Array indexing (subscript): arr[index]
            if 'value' in expr and 'slice' in expr:
                # Compile array expression
                self.compile_expr(expr['value'], expr_type)
                # Compile index expression
                self.compile_expr(expr['slice'], 'i64')
                # Get element at index
                self.emit("LIST_GET")
                return

            # Binary operation (Python AST format: {left, ops, comparators})
            if 'ops' in expr and 'left' in expr and 'comparators' in expr:
                left = expr['left']
                ops = expr['ops']
                comparators = expr['comparators']

                # For simplicity, handle single comparison for now
                if len(ops) == 1 and len(comparators) == 1:
                    op = ops[0]
                    right = comparators[0]

                    # Compile operands
                    self.compile_expr(left, expr_type)
                    self.compile_expr(right, expr_type)

                    # Emit comparison
                    op_map = {
                        'Eq': 'CMP_EQ',
                        'NotEq': 'CMP_NE',
                        'Lt': 'CMP_LT',
                        'Gt': 'CMP_GT',
                        'LtE': 'CMP_LE',
                        'GtE': 'CMP_GE',
                    }

                    if op in op_map:
                        self.emit(op_map[op])
                    else:
                        raise CompilerError(f"Unknown comparison operator: {op}")
                    return

            # Unary operation (USub for -, UAdd for +, Not for not, Invert for ~): {op, operand}
            if 'op' in expr and 'operand' in expr:
                op = expr['op']
                operand = expr['operand']

                # Compile operand
                self.compile_expr(operand, expr_type)

                # Emit unary operation
                if op == 'USub':
                    self.emit('NEG')
                elif op == 'UAdd':
                    # UAdd is a no-op (unary plus), do nothing
                    pass
                elif op == 'Not':
                    self.emit('NOT')
                elif op == 'Invert':
                    # Bitwise NOT - can be implemented as XOR with -1
                    self.emit('CONST_I64 -1')
                    self.emit('XOR_I64')
                else:
                    raise CompilerError(f"Unknown unary operator: {op}")
                return

            # Binary operation (simplified AST format: {left, op, right})
            if 'op' in expr and 'left' in expr and 'right' in expr:
                op = expr['op']
                left = expr['left']
                right = expr['right']

                # Compile operands (push to stack)
                self.compile_expr(left, expr_type)
                self.compile_expr(right, expr_type)

                # Determine type suffix - check if either operand is a string
                # For string concatenation, we need ADD_STR
                is_string_op = False

                # Check if left is a string literal or string operation
                if isinstance(left, dict):
                    if left.get('type') in ('string', 'str'):
                        is_string_op = True
                    elif left.get('type') == 'call' and left.get('name') == 'str':
                        is_string_op = True
                    elif is_function_call(left) and extract_func_name(left.get('func', '')) == 'str':
                        is_string_op = True

                # Check if right is a string literal or string operation
                if isinstance(right, dict):
                    if right.get('type') in ('string', 'str'):
                        is_string_op = True
                    elif right.get('type') == 'call' and right.get('name') == 'str':
                        is_string_op = True
                    elif is_function_call(right) and extract_func_name(right.get('func', '')) == 'str':
                        is_string_op = True

                if is_string_op or expr_type in {'str', 'string'}:
                    type_suffix = '_STR'
                elif expr_type in {'i64', 'int'} or expr_type not in (
                    'f64',
                    'float',
                ):
                    type_suffix = '_I64'
                else:
                    type_suffix = '_F64'
                op_map = {
                    'Add': f'ADD{type_suffix}',
                    '+': f'ADD{type_suffix}',  # Support literal '+' operator
                    'Sub': f'SUB{type_suffix}',
                    '-': f'SUB{type_suffix}',  # Support literal '-' operator
                    'Mult': f'MUL{type_suffix}',
                    '*': f'MUL{type_suffix}',  # Support literal '*' operator
                    'Div': f'DIV{type_suffix}',
                    '/': f'DIV{type_suffix}',  # Support literal '/' operator
                    'Mod': 'MOD_I64',
                    '%': 'MOD_I64',  # Support literal '%' operator
                    'Eq': 'CMP_EQ',
                    '==': 'CMP_EQ',  # Support literal '==' operator
                    'NotEq': 'CMP_NE',
                    '!=': 'CMP_NE',  # Support literal '!=' operator
                    'Lt': 'CMP_LT',
                    '<': 'CMP_LT',  # Support literal '<' operator
                    'Gt': 'CMP_GT',
                    '>': 'CMP_GT',  # Support literal '>' operator
                    'LtE': 'CMP_LE',
                    '<=': 'CMP_LE',  # Support literal '<=' operator
                    'GtE': 'CMP_GE',
                    '>=': 'CMP_GE',  # Support literal '>=' operator
                }

                if op in op_map:
                    self.emit(op_map[op])
                else:
                    raise CompilerError(f"Unknown operator: {op}")
                return

            # Function call
            if expr.get('type') == 'call' or 'func' in expr:
                # Handle both formats
                if 'func' in expr:
                    func_info = expr['func']
                    args = expr.get('args', [])

                    # Check if it's a method call (obj.method())
                    if isinstance(func_info, dict) and 'attr' in func_info and 'value' in func_info:
                        # This is a method call: obj.method(args)
                        # Check if obj is a pyobject
                        value_node = func_info['value']
                        is_pyobject = False
                        is_module = False

                        if isinstance(value_node, dict) and 'id' in value_node:
                            var_name = value_node['id']
                            var_type = self.var_types.get(var_name)
                            if var_type == 'pyobject':
                                is_pyobject = True
                            # Check if it's a module alias or name
                            elif var_name in self.py_imports:
                                is_module = True

                        if is_module:
                            # Module function call: ui.Window() where ui is an imported module
                            # Convert to py_call(module_name, func_name, *args)
                            module_alias = value_node['id']
                            func_name = func_info['attr']
                            
                            # Resolve alias to actual module name
                            import_info = self.py_imports[module_alias]
                            actual_module = import_info['module']
                            
                            # Push actual module name (not alias) as string
                            escaped_module = escape_string_for_bytecode(actual_module)
                            self.emit(f'CONST_STR "{escaped_module}"')
                            
                            # Push function name as string
                            escaped_func = escape_string_for_bytecode(func_name)
                            self.emit(f'CONST_STR "{escaped_func}"')
                            
                            # Push arguments
                            for arg in args:
                                self.compile_expr(arg, expr_type)
                            
                            # Push num_args and call
                            self.emit(f"CONST_I64 {len(args)}")
                            self.emit('PY_CALL')
                            return

                        if is_pyobject:
                            # Python object method call
                            # Compile: obj, method_name, arg1, ..., argN, num_args -> PY_CALL_METHOD
                            self.compile_expr(func_info['value'], expr_type)  # Push object
                            self.emit(f'CONST_STR "{func_info["attr"]}"')     # Push method name
                            for arg in args:                                    # Push arguments
                                self.compile_expr(arg, expr_type)
                            self.emit(f"CONST_I64 {len(args)}")                # Push num_args
                            self.emit('PY_CALL_METHOD')
                            return

                    func_name = func_info.get('id', '') if isinstance(func_info, dict) else func_info
                else:
                    func_name = expr.get('name', '')
                    args = expr.get('args', [])

                # Special handling for py_call to resolve aliases
                if func_name == 'py_call' and len(args) >= 2:
                    # Check if first argument is a string literal (module name or alias)
                    first_arg = args[0]
                    module_ref = None
                    if isinstance(first_arg, str):
                        module_ref = first_arg
                    elif isinstance(first_arg, dict) and first_arg.get('type') == 'string':
                        module_ref = first_arg.get('value')
                    elif isinstance(first_arg, dict) and 'value' in first_arg and isinstance(first_arg['value'], str):
                        module_ref = first_arg['value']

                    # Resolve alias to actual module/function name
                    if module_ref and module_ref in self.py_imports:
                        import_info = self.py_imports[module_ref]
                        actual_module = import_info['module']
                        
                        if import_info.get('type') == 'name':
                            # For "from module import name", replace module arg with actual module
                            # and func arg with the imported name
                            import_name = import_info['name']
                            args[0] = {'value': actual_module}
                            args[1] = {'value': import_name}
                        elif module_ref != actual_module:
                            # For "import module as alias", just replace the module name
                            args[0] = {'value': actual_module}

                # Check if it's a struct constructor
                if func_name in self.struct_defs:
                    struct_def = self.struct_defs[func_name]
                    # Compile arguments (field values) in order
                    for arg in args:
                        self.compile_expr(arg, expr_type)
                    # Create struct instance
                    self.emit(f"STRUCT_NEW {struct_def['id']}")
                    return

                # Compile arguments (push to stack in order)
                for arg in args:
                    self.compile_expr(arg, expr_type)

                # Add default arguments for certain functions
                if func_name == 'fopen' and len(args) == 1:
                    # fopen with 1 arg needs default mode 'r'
                    self.emit('CONST_STR "r"')

                # Check if builtin
                builtin_map = {
                    'println': 'BUILTIN_PRINTLN',
                    'print': 'BUILTIN_PRINT',
                    'str': 'BUILTIN_STR',
                    'len': 'BUILTIN_LEN',
                    'sqrt': 'BUILTIN_SQRT',
                    'round': 'BUILTIN_ROUND',
                    'floor': 'BUILTIN_FLOOR',
                    'ceil': 'BUILTIN_CEIL',
                    'PI': 'BUILTIN_PI',
                    'int': 'TO_INT',
                    'float': 'TO_FLOAT',
                    'bool': 'TO_BOOL',
                    'upper': 'STR_UPPER',
                    'lower': 'STR_LOWER',
                    'strip': 'STR_STRIP',
                    'split': 'STR_SPLIT',
                    'join': 'STR_JOIN',
                    'replace': 'STR_REPLACE',
                    'abs': 'ABS',
                    'pow': 'POW',
                    'min': 'MIN',
                    'max': 'MAX',
                    # File I/O
                    'fopen': 'FILE_OPEN',
                    'fread': 'FILE_READ',
                    'fwrite': 'FILE_WRITE',
                    'fclose': 'FILE_CLOSE',
                    'exists': 'FILE_EXISTS',
                    'isfile': 'FILE_ISFILE',
                    'isdir': 'FILE_ISDIR',
                    'listdir': 'FILE_LISTDIR',
                    'mkdir': 'FILE_MKDIR',
                    'makedirs': 'FILE_MAKEDIRS',
                    'remove': 'FILE_REMOVE',
                    'rmdir': 'FILE_RMDIR',
                    'rename': 'FILE_RENAME',
                    'getsize': 'FILE_GETSIZE',
                    'getcwd': 'FILE_GETCWD',
                    'chdir': 'FILE_CHDIR',
                    'abspath': 'FILE_ABSPATH',
                    'basename': 'FILE_BASENAME',
                    'dirname': 'FILE_DIRNAME',
                    'pathjoin': 'FILE_JOIN',
                    # Socket I/O
                    'socket': 'SOCKET_CREATE',
                    'connect': 'SOCKET_CONNECT',
                    'bind': 'SOCKET_BIND',
                    'listen': 'SOCKET_LISTEN',
                    'accept': 'SOCKET_ACCEPT',
                    'send': 'SOCKET_SEND',
                    'recv': 'SOCKET_RECV',
                    'sclose': 'SOCKET_CLOSE',
                    'setsockopt': 'SOCKET_SETSOCKOPT',
                    # Python library integration
                    'py_import': 'PY_IMPORT',
                    'py_call': 'PY_CALL',
                    'py_getattr': 'PY_GETATTR',
                    'py_setattr': 'PY_SETATTR',
                    'py_call_method': 'PY_CALL_METHOD',
                }

                if func_name in builtin_map:
                    # Special handling for py_call which needs num_args at the end
                    if func_name == 'py_call':
                        # py_call(module_name, func_name, arg1, arg2, ...)
                        # Stack should be: module_name, func_name, arg1, ..., argN, num_args
                        if len(args) < 2:
                            raise CompilerError("py_call requires at least module_name and func_name")

                        # Check if first argument is a string literal (module name or alias)
                        first_arg = args[0]
                        module_ref = None
                        if isinstance(first_arg, str):
                            module_ref = first_arg
                        elif isinstance(first_arg, dict) and first_arg.get('type') == 'string':
                            module_ref = first_arg.get('value')
                        elif isinstance(first_arg, dict) and 'value' in first_arg and isinstance(first_arg['value'], str):
                            module_ref = first_arg['value']

                        # Check if module/alias was imported at top level
                        # Note: module_ref might be the actual module name after alias resolution
                        # Check both the original ref and the actual module
                        found_import = False
                        for key, import_info in self.py_imports.items():
                            if key == module_ref or import_info['module'] == module_ref:
                                found_import = True
                                break
                        
                        if not found_import and module_ref:
                            raise CompilerError(f"Module '{module_ref}' must be imported with py_import at the top of the file")

                        # Arguments are already compiled above, now push the count
                        num_py_args = len(args) - 2  # Subtract module_name and func_name
                        self.emit(f"CONST_I64 {num_py_args}")
                    elif func_name == 'py_call_method':
                        # py_call_method(obj, method_name, arg1, arg2, ...)
                        # Stack should be: obj, method_name, arg1, ..., argN, num_args
                        if len(args) < 2:
                            raise CompilerError("py_call_method requires at least obj and method_name")

                        # Arguments are already compiled above, now push the count
                        num_py_args = len(args) - 2  # Subtract obj and method_name
                        self.emit(f"CONST_I64 {num_py_args}")
                    elif func_name == 'py_getattr':
                        # py_getattr(obj, attr_name)
                        # Stack should be: obj, attr_name
                        if len(args) != 2:
                            raise CompilerError("py_getattr requires exactly 2 arguments: obj and attr_name")
                    elif func_name == 'py_setattr':
                        # py_setattr(obj, attr_name, value)
                        # Stack should be: obj, attr_name, value
                        if len(args) != 3:
                            raise CompilerError("py_setattr requires exactly 3 arguments: obj, attr_name, and value")
                    self.emit(builtin_map[func_name])
                elif func_name == 'append':
                    # append(list, value) - special handling
                    # Args are already on stack: list, value
                    self.emit("LIST_APPEND")
                elif func_name == 'pop':
                    # pop(list) - special handling
                    # List is already on stack
                    self.emit("LIST_POP")
                else:
                    self.emit(f"CALL {func_name} {len(args)}")
                return

        # Default: treat as constant 0
        self.emit("CONST_I64 0")

    def compile_statement(self, node: dict, func_return_type: str):
        """Compile a statement node"""
        node_type = node.get('type')

        # Variable declaration/assignment
        if node_type == 'var':
            name = node.get('name', '')
            value = node.get('value')
            var_id = self.get_var_id(name)

            if value_type_str := node.get('value_type', 'any'):
                self.var_types[name] = self.normalize_type(value_type_str)

            # Check if value has a nested 'value' field (happens with constants)
            if value and is_struct_instance(value):
                value = value['value']

            # Special handling for pop(list) which modifies the list
            if value and is_function_call(value):
                func_info = value.get('func', {})
                func_name = extract_func_name(func_info)
                args = value.get('args', [])

                if func_name == 'pop' and len(args) >= 1:
                    first_arg = args[0]
                    if is_var_ref(first_arg):
                        # v = pop(arr)
                        # Need to: LOAD arr; LIST_POP; STORE v; STORE arr
                        arr_var = first_arg['id']
                        arr_var_id = self.get_var_id(arr_var)

                        self.emit(f"LOAD {arr_var_id}")
                        self.emit("LIST_POP")  # Pushes [arr', elem]
                        self.emit(f"STORE {var_id}")  # Store elem to v, leaves arr' on stack
                        self.emit(f"STORE {arr_var_id}")  # Store arr' back
                        return

            # Compile value expression
            value_type = self.map_type(node.get('value_type'))
            self.compile_expr(value, value_type)

            # Store to variable
            self.emit(f"STORE {var_id}")

        elif node_type == 'index_assign':
            target_name = node.get('target', '')
            index = node.get('index')
            value = node.get('value')

            var_id = self.get_var_id(target_name)

            # Load the list
            self.emit(f"LOAD {var_id}")
            # Compile index
            self.compile_expr(index, 'i64')
            # Compile value
            self.compile_expr(value)
            # Set element and get modified list back
            self.emit("LIST_SET")
            # Store modified list back
            self.emit(f"STORE {var_id}")

        elif node_type == 'field_assign':
            target_name = node.get('target', '')
            field_name = node.get('field', '')
            value = node.get('value')

            # Check if target is a Python module import
            if target_name in self.py_imports:
                # Python module attribute assignment: ui.debug = False
                # Load the module object (stored as a variable)
                var_id = self.get_var_id(target_name)
                self.emit(f"LOAD {var_id}")
                
                # Push attribute name
                escaped_attr = escape_string_for_bytecode(field_name)
                self.emit(f'CONST_STR "{escaped_attr}"')
                
                # Push value
                self.compile_expr(value)
                
                # Call PY_SETATTR(module, attr_name, value)
                self.emit('PY_SETATTR')
                # PY_SETATTR leaves a none value on stack, pop it
                self.emit('POP')
                return

            var_id = self.get_var_id(target_name)
            
            # Check if target is a pyobject variable
            var_type = self.var_types.get(target_name, '')
            if var_type == 'pyobject':
                # Python object attribute assignment: window.debug = False
                # Load the pyobject
                self.emit(f"LOAD {var_id}")
                
                # Push attribute name
                escaped_attr = escape_string_for_bytecode(field_name)
                self.emit(f'CONST_STR "{escaped_attr}"')
                
                # Push value
                self.compile_expr(value)
                
                # Call PY_SETATTR(obj, attr_name, value)
                self.emit('PY_SETATTR')
                # PY_SETATTR leaves a none value on stack, pop it
                self.emit('POP')
                return

            # Load the struct
            self.emit(f"LOAD {var_id}")
            
            field_idx = next(
                (
                    struct_def['field_map'][field_name]
                    for struct_name, struct_def in self.struct_defs.items()
                    if field_name in struct_def['field_map']
                ),
                -1,
            )
            if field_idx < 0:
                raise ValueError(f"Unknown field: {field_name}")

            # Compile the value
            self.compile_expr(value)

            # Set field and get modified struct back
            self.emit(f"STRUCT_SET {field_idx}")

            # Store modified struct back
            self.emit(f"STORE {var_id}")

        elif node_type == 'return':
            value = node.get('value')

            if value is not None:
                self.compile_expr(value, func_return_type)
                self.emit("RETURN")
            else:
                self.emit("RETURN_VOID")

        elif node_type == 'if':
            condition = node.get('condition')
            scope = node.get('scope', [])
            elifs = node.get('elifs', [])
            else_scope = node.get('else', [])

            end_label = self.get_label("if_end")
            else_label = self.get_label("else")

            # Compile condition
            self.compile_expr(condition, 'bool')

            if else_scope or elifs:
                self.emit(f"JUMP_IF_FALSE {else_label}")
            else:
                self.emit(f"JUMP_IF_FALSE {end_label}")

            # Compile if body
            for stmt in scope:
                self.compile_statement(stmt, func_return_type)

            # Jump to end after if body
            if else_scope or elifs:
                self.emit(f"JUMP {end_label}")

            # Handle elifs
            for elif_node in elifs:
                self.emit(f"LABEL {else_label}")
                else_label = self.get_label("else")

                elif_cond = elif_node.get('condition')
                elif_scope = elif_node.get('scope', [])

                self.compile_expr(elif_cond, 'bool')
                self.emit(f"JUMP_IF_FALSE {else_label}")

                for stmt in elif_scope:
                    self.compile_statement(stmt, func_return_type)

                self.emit(f"JUMP {end_label}")

            # Handle else
            if else_scope:
                self.emit(f"LABEL {else_label}")
                for stmt in else_scope:
                    self.compile_statement(stmt, func_return_type)

            self.emit(f"LABEL {end_label}")

        elif node_type == 'switch':
            switch_expr = node.get('expr')
            cases = node.get('cases', [])
            default_case = node.get('default')

            end_label = self.get_label("switch_end")

            # Compile the switch expression and store it in a temp variable
            switch_var_id = self.get_var_id("__switch_temp")
            self.compile_expr(switch_expr, 'i64')  # Assume i64 for now, could be str too
            self.emit(f"STORE {switch_var_id}")

            # Generate labels for each case
            case_labels = [self.get_label(f"case_{i}") for i in range(len(cases))]
            default_label = self.get_label("default") if default_case else end_label

            # For each case, check if the value matches
            for i, case in enumerate(cases):
                case_label = case_labels[i]
                next_check = case_labels[i + 1] if i + 1 < len(cases) else default_label

                for case_value_node in case['values']:
                    # Load switch value
                    self.emit(f"LOAD {switch_var_id}")

                    # Load case value
                    if isinstance(case_value_node, dict):
                        if case_value_node.get('type') == 'string':
                            # String comparison
                            value_str = escape_string_for_bytecode(case_value_node.get('value', ''))
                            self.emit(f'CONST_STR "{value_str}"')
                            self.emit("STR_EQ")
                        else:
                            # Numeric or other literal
                            self.compile_expr(case_value_node, 'i64')
                            self.emit("CMP_EQ")
                    else:
                        # Direct value
                        self.emit(f"CONST_I64 {case_value_node}")
                        self.emit("CMP_EQ")

                    # If match, jump to case body
                    self.emit(f"JUMP_IF_TRUE {case_label}")

            # If no case matched, jump to default (or end)
            self.emit(f"JUMP {default_label}")

            # Compile each case body
            for i, case in enumerate(cases):
                self.emit(f"LABEL {case_labels[i]}")
                for stmt in case['body']:
                    self.compile_statement(stmt, func_return_type)
                # No fall-through - jump to end
                self.emit(f"JUMP {end_label}")

            # Compile default case if it exists
            if default_case:
                self.emit(f"LABEL {default_label}")
                for stmt in default_case:
                    self.compile_statement(stmt, func_return_type)

            self.emit(f"LABEL {end_label}")

        elif node_type == 'while':
            condition = node.get('condition')
            scope = node.get('scope', [])

            start_label = self.get_label("while_start")
            end_label = self.get_label("while_end")

            # Push loop labels onto stack for break/continue
            self.loop_stack.append((start_label, end_label))

            self.emit(f"LABEL {start_label}")

            # Compile condition
            self.compile_expr(condition, 'bool')
            self.emit(f"JUMP_IF_FALSE {end_label}")

            # Compile loop body
            for stmt in scope:
                self.compile_statement(stmt, func_return_type)

            # Jump back to start
            self.emit(f"JUMP {start_label}")
            self.emit(f"LABEL {end_label}")

            # Pop loop from stack
            self.loop_stack.pop()

        elif node_type == 'for':
            var_name = node.get('var', '')
            start_val = node.get('start', 0)
            end_expr = node.get('end')
            step_expr = node.get('step', 1)  # Default step is 1
            scope = node.get('scope', [])

            var_id = self.get_var_id(var_name)
            loop_start = self.get_label("for_start")
            loop_continue = self.get_label("for_continue")
            loop_end = self.get_label("for_end")

            # Push loop labels onto stack for break/continue
            # Continue should jump to the increment, not the start
            self.loop_stack.append((loop_continue, loop_end))

            # Initialize loop variable
            self.compile_expr(start_val, 'i64')
            self.emit(f"STORE {var_id}")

            self.emit(f"LABEL {loop_start}")

            # Check condition:
            # If step > 0: var < end
            # If step < 0: var > end
            # We need to evaluate step to determine which comparison to use
            # For simplicity, we'll compile the step expression and check at runtime

            # For now, detect if step is negative by checking if it's a dict with 'op': 'USub'
            step_is_negative = False
            if isinstance(step_expr, dict):
                if step_expr.get('op') == 'USub':
                    step_is_negative = True
            elif isinstance(step_expr, (int, float)):
                step_is_negative = step_expr < 0

            self.emit(f"LOAD {var_id}")
            self.compile_expr(end_expr, 'i64')

            if step_is_negative:
                self.emit("CMP_GT")  # Continue while var > end for negative step
            else:
                self.emit("CMP_LT")  # Continue while var < end for positive step

            self.emit(f"JUMP_IF_FALSE {loop_end}")

            # Compile loop body
            for stmt in scope:
                self.compile_statement(stmt, func_return_type)

            # Continue label - increment happens here
            self.emit(f"LABEL {loop_continue}")

            # Increment loop variable by step
            self.emit(f"LOAD {var_id}")
            self.compile_expr(step_expr, 'i64')
            self.emit("ADD_I64")  # Works for both positive and negative steps
            self.emit(f"STORE {var_id}")

            # Jump back to start
            self.emit(f"JUMP {loop_start}")
            self.emit(f"LABEL {loop_end}")

            # Pop loop from stack
            self.loop_stack.pop()

        elif node_type == 'for_in':
            var_name = node.get('var', '')
            iterable = node.get('iterable')
            scope = node.get('scope', [])

            # Create index variable (hidden from user)
            idx_var_name = f"_forin_idx_{self.label_counter}"
            var_id = self.get_var_id(var_name)
            idx_var_id = self.get_var_id(idx_var_name)

            # Determine if iterable is a variable reference
            iterable_var_id = None
            if isinstance(iterable, str):
                iterable_var_id = self.get_var_id(iterable)

            loop_start = self.get_label("forin_start")
            loop_continue = self.get_label("forin_continue")
            loop_end = self.get_label("forin_end")

            # Push loop labels onto stack for break/continue
            # continue should jump to the increment, not the start
            self.loop_stack.append((loop_continue, loop_end))

            # Initialize index to 0
            self.emit("CONST_I64 0")
            self.emit(f"STORE {idx_var_id}")

            self.emit(f"LABEL {loop_start}")

            # Check condition: idx < len(iterable)
            self.emit(f"LOAD {idx_var_id}")

            # Get iterable and compute its length
            if iterable_var_id is not None:
                # Variable reference
                self.emit(f"LOAD {iterable_var_id}")
            else:
                # Expression
                self.compile_expr(iterable)

            self.emit("BUILTIN_LEN")
            self.emit("CMP_LT")
            self.emit(f"JUMP_IF_FALSE {loop_end}")

            # Get current item: var = iterable[idx]
            if iterable_var_id is not None:
                self.emit(f"LOAD {iterable_var_id}")
            else:
                self.compile_expr(iterable)

            self.emit(f"LOAD {idx_var_id}")
            self.emit("LIST_GET")
            self.emit(f"STORE {var_id}")

            # Compile loop body
            for stmt in scope:
                self.compile_statement(stmt, func_return_type)

            # Continue label - increment happens here
            self.emit(f"LABEL {loop_continue}")

            # Increment index
            self.emit(f"LOAD {idx_var_id}")
            self.emit("CONST_I64 1")
            self.emit("ADD_I64")
            self.emit(f"STORE {idx_var_id}")

            # Jump back to start
            self.emit(f"JUMP {loop_start}")
            self.emit(f"LABEL {loop_end}")

            # Pop loop from stack
            self.loop_stack.pop()

        elif node_type == 'call':
            func_name = node.get('name', '')

            # Special handling for list-modifying functions
            if func_name == 'append' and len(node.get('args', [])) >= 1:
                # append(list, value) - modifies list in place
                first_arg = node['args'][0]
                if is_var_ref(first_arg):
                    # Get the variable name
                    var_name = first_arg['id']
                    var_id = self.get_var_id(var_name)

                    # Compile the expression (will generate LIST_APPEND)
                    self.compile_expr(node)

                    # Store result back to the variable
                    self.emit(f"STORE {var_id}")
                    return

            self.compile_expr(node)

            # Don't pop for void functions
            # Check both builtins and user-defined functions
            void_builtins = {'println', 'print'}
            return_type = node.get('return_type', '')

            # Skip POP if:
            # 1. It's a void builtin, OR
            # 2. The function has a void/None return type
            if func_name not in void_builtins and return_type not in ('void', 'None', 'none', ''):
                # Pop result since we're not using it
                self.emit("POP")

        elif 'func' in node and 'args' in node:
            # This is a call expression node from Python's AST
            self.compile_expr(node)
            # Always pop the result since we're using it as a statement
            self.emit("POP")

        elif node_type == 'break':
            level = node.get('level', 1)
            if level > len(self.loop_stack):
                raise CompilerError(f"break {level} used outside of {level} nested loop(s)")

            # Get the end label of the loop `level` levels up
            # loop_stack[-1] is innermost, loop_stack[-level] is the target
            _, end_label = self.loop_stack[-level]
            self.emit(f"JUMP {end_label}")

        elif node_type == 'continue':
            level = node.get('level', 1)
            if level > len(self.loop_stack):
                raise CompilerError(f"continue {level} used outside of {level} nested loop(s)")

            # Get the start label of the loop `level` levels up
            start_label, _ = self.loop_stack[-level]
            self.emit(f"JUMP {start_label}")

        elif node_type == 'assert':
            condition = node.get('condition')
            if message := node.get('message'):
                self.compile_expr(message, 'str')

            # Compile condition
            self.compile_expr(condition, 'bool')

            # Emit assert instruction
            self.emit("ASSERT")

    def infer_parameter_types(self, func_node: dict) -> dict:
        """Infer types for untyped parameters based on usage in function body.
        Returns a dict mapping parameter names to inferred types."""
        args = func_node.get('args', [])
        scope = func_node.get('scope', [])
        inferred_types = {}

        # Find untyped parameters
        untyped_params = []
        for arg in args:
            if isinstance(arg, (tuple, list)) and len(arg) == 2:
                arg_name, type_annotation = arg
                if type_annotation is None:
                    untyped_params.append(arg_name)

        if not untyped_params:
            return inferred_types

        # Analyze function body to infer types
        def analyze_expr(expr, param_name):
            """Analyze expression to infer type of param_name"""
            if isinstance(expr, dict):
                # Binary operations suggest numeric types
                if 'op' in expr and 'left' in expr and 'right' in expr:
                    op = expr.get('op')
                    if op in ('Mult', 'Div', 'Mod'):
                        # Multiplication, division suggest numeric (default to int)
                        if analyze_uses_param(expr, param_name):
                            return 'i64'
                    elif op in ('Add', 'Sub'):
                        # Could be int or string for Add
                        if analyze_uses_param(expr, param_name):
                            return 'i64'  # Default to int for now

                # Function calls can give hints
                if expr.get('type') == 'call' or 'func' in expr:
                    # Check arguments to see if param is used in specific positions
                    pass

                # Recursively check nested expressions
                for key, value in expr.items():
                    if key not in ('type', 'name', 'id'):
                        result = analyze_expr(value, param_name)
                        if result:
                            return result
            elif isinstance(expr, list):
                for item in expr:
                    result = analyze_expr(item, param_name)
                    if result:
                        return result
            return None

        def analyze_uses_param(expr, param_name):
            """Check if expression uses the parameter"""
            if isinstance(expr, dict):
                if expr.get('id') == param_name:
                    return True
                for value in expr.values():
                    if analyze_uses_param(value, param_name):
                        return True
            elif isinstance(expr, list):
                for item in expr:
                    if analyze_uses_param(item, param_name):
                        return True
            elif isinstance(expr, str) and expr == param_name:
                return True
            return False

        # Infer types for each untyped parameter
        for param_name in untyped_params:
            inferred_type = None

            # Look through all statements in function body
            for stmt in scope:
                if stmt.get('type') == 'return':
                    value = stmt.get('value')
                    result = analyze_expr(value, param_name)
                    if result:
                        inferred_type = result
                        break
                elif stmt.get('type') == 'var':
                    value = stmt.get('value')
                    result = analyze_expr(value, param_name)
                    if result:
                        inferred_type = result
                        break

            # Default to i64 if we couldn't infer
            inferred_types[param_name] = inferred_type or 'i64'

        return inferred_types

    def compile_function(self, func_node: dict) -> Optional[str]:
        """Compile a function node to bytecode. Returns bytecode string or None if can't compile."""
        func_name = func_node.get('name', 'unknown')

        if inferred_types := self.infer_parameter_types(func_node):
            args = func_node.get('args', [])
            new_args = []
            for arg in args:
                if isinstance(arg, (tuple, list)) and len(arg) == 2:
                    arg_name, type_annotation = arg
                    if type_annotation is None and arg_name in inferred_types:
                        # Apply inferred type
                        new_args.append((arg_name, inferred_types[arg_name]))
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            func_node['args'] = new_args

        # Check if function is fully typed
        if not self.check_function_typed(func_node):
            # Collect which arguments are missing types
            args = func_node.get('args', [])
            untyped_args = []

            for arg in args:
                if isinstance(arg, (tuple, list)) and len(arg) == 2:
                    arg_name, type_annotation = arg
                    if type_annotation is None:
                        untyped_args.append(arg_name)
                elif isinstance(arg, str):
                    untyped_args.append(arg)

            if untyped_args:
                args_str = ", ".join(untyped_args)
                # Create example with typed parameters
                example_params = ", ".join([f"int {arg}" for arg in untyped_args])
                return_type_hint = func_node.get('return', 'void')
                if return_type_hint is None:
                    return_type_hint = 'int'

                raise CompilerError(
                    f"Function '{func_name}' cannot be compiled to bytecode: "
                    f"missing type annotations for argument{'s' if len(untyped_args) > 1 else ''}: {args_str}\n\n"
                    f"Hint: Change function signature to:\n"
                    f"  {return_type_hint} {func_name}({example_params})"
                )
            return None

        # Reset state for new function
        self.output = []
        self.label_counter = 0
        self.var_mapping = {}
        self.next_var_id = 0

        # Extract function info (func_name already extracted above)
        return_type = self.map_type(func_node.get('return'))
        args = func_node.get('args', [])
        scope = func_node.get('scope', [])

        # Emit function header
        self.emit(f".func {func_name} {return_type} {len(args)}")

        # Emit argument declarations
        for arg in args:
            if isinstance(arg, (tuple, list)) and len(arg) == 2:
                arg_name, arg_type = arg
                mapped_type = self.map_type(arg_type)
                var_id = self.get_var_id(arg_name)
                self.emit(f"  .arg {arg_name} {mapped_type}")

        # Collect local variables (scan the function body)
        locals_found = set()
        for stmt in scope:
            if stmt.get('type') == 'var':
                var_name = stmt.get('name', '')
                if var_name not in self.var_mapping:
                    locals_found.add(var_name)

        # Emit local variable declarations
        for local_name in sorted(locals_found):
            var_id = self.get_var_id(local_name)
            local_type = next(
                (
                    self.map_type(stmt.get('value_type'))
                    for stmt in scope
                    if stmt.get('type') == 'var' and stmt.get('name') == local_name
                ),
                'i64',
            )
            self.emit(f"  .local {local_name} {local_type}")

        # If this is main function and we have Python imports, initialize them
        if func_name == 'main' and self.py_imports:
            for key, import_info in self.py_imports.items():
                module_name = import_info['module']
                escaped_module = escape_string_for_bytecode(module_name)
                self.emit(f'  CONST_STR "{escaped_module}"')
                self.emit('  PY_IMPORT')
                # Store the module object in a variable with the alias/key name
                # First, declare the variable if it doesn't exist
                if key not in self.var_mapping:
                    var_id = self.next_var_id
                    self.next_var_id += 1
                    self.var_mapping[key] = var_id
                    self.var_types[key] = 'pyobject'
                # Store the module object
                var_id = self.var_mapping[key]
                self.emit(f'  STORE {var_id}')

        # Compile function body
        for stmt in scope:
            self.compile_statement(stmt, return_type)

        # Ensure function returns
        if return_type == 'void':
            self.emit("RETURN_VOID")

        self.emit(".end")
        self.emit("")  # Blank line between functions

        # Optimize the function bytecode
        bytecode = '\n'.join(self.output)
        optimizer = BytecodeOptimizer()
        if '-O0' not in flags:
            bytecode = optimizer.optimize(bytecode)
        return bytecode

    def compile_ast(self, ast: AstType) -> str:
        """Compile entire AST to bytecode"""
        results = [".version 1", ""]

        # First pass: Register all struct definitions and Python imports
        for node in ast:
            if node.get('type') == 'struct_def':
                struct_name = node.get('name', '')
                fields = node.get('fields', [])

                # Assign unique ID to this struct
                struct_id = self.struct_id_counter
                self.struct_id_counter += 1

                # Store struct metadata
                self.struct_defs[struct_name] = {
                    'id': struct_id,
                    'fields': fields,
                    'field_map': {f['name']: i for i, f in enumerate(fields)}
                }
            elif node.get('type') == 'py_import':
                # Register Python import
                module_name = node.get('module', '')
                alias = node.get('alias')
                name = node.get('name')

                if not module_name:
                    continue

                # Determine the key to use in py_imports
                if name:
                    # "from datetime py_import datetime" or "from datetime py_import datetime as dt"
                    key = alias or name
                    if key not in self.py_imports:
                        self.py_imports[key] = {
                            'module': module_name,
                            'type': 'name',
                            'name': name
                        }
                else:
                    # "py_import datetime" or "py_import datetime as dt"
                    key = alias or module_name
                    if key not in self.py_imports:
                        self.py_imports[key] = {
                            'module': module_name,
                            'type': 'module'
                        }

        # Emit struct definitions as bytecode directives
        for struct_name, struct_def in self.struct_defs.items():
            struct_id = struct_def['id']
            fields = struct_def['fields']
            field_names = ' '.join(f['name'] for f in fields)
            results.append(f".struct {struct_id} {len(fields)} {field_names}")

        if self.struct_defs:
            results.append("")

        # Compile all functions
        entry_point = None
        for node in ast:
            if node.get('type') == 'function':
                func_name = node.get('name', '')

                if bytecode := self.compile_function(node):
                    results.append(bytecode)

                    # Mark 'main' as entry point
                    if func_name == 'main':
                        entry_point = func_name

        # Emit entry point
        if entry_point:
            results.append(f".entry {entry_point}")

        return '\n'.join(results)

def compile_ast_to_bytecode(ast: AstType) -> str:
    """Main entry point for compilation"""
    compiler = BytecodeCompiler()
    return compiler.compile_ast(ast)


if __name__ == '__main__':
    import json

    if len(sys.argv) < 2:
        print("Usage: python compiler.py <ast.json>")
        sys.exit(1)

    ast_file = sys.argv[1]

    try:
        with open(ast_file, 'r') as f:
            ast = json.load(f)

        bytecode = compile_ast_to_bytecode(ast)
        print(bytecode)

    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        sys.exit(1)
