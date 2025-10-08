from builtin_funcs import funcs
from parser import parse_expr, get_type, vars
from typing import Any, cast
import sys
import threading

# Debug runtime support - will be set by debug_runtime module
debug_runtime_instance = None

# Track the actual current vars (updated when entering/exiting functions)
_current_runtime_vars = vars

# Runtime context for error formatting
_runtime_file: str | None = None
_runtime_source: str | None = None
_runtime_current_line: int = 0
_runtime_current_func: str = '<module>'
_runtime_current_char: int = 0  # Character position for error reporting

def set_debug_runtime(runtime):
    """Set the debug runtime instance (called from debug_runtime module)"""
    global debug_runtime_instance
    debug_runtime_instance = runtime

def get_debug_runtime():
    """Get the current debug runtime instance"""
    return debug_runtime_instance

def get_current_vars():
    """Get the current variable scope (for debugging)"""
    return _current_runtime_vars

def get_runtime_context():
    """Get the current runtime context for error formatting"""
    return {
        'file': _runtime_file,
        'source': _runtime_source,
        'line': _runtime_current_line,
        'func': _runtime_current_func,
        'char': _runtime_current_char
    }

def set_error_char(char: int):
    """Set the character position for the next error"""
    global _runtime_current_char
    _runtime_current_char = char

def format_runtime_exception(e: Exception) -> str:
    """Format a runtime exception similar to parse-time exceptions"""
    ctx = get_runtime_context()
    error_msg = str(e)
    char_pos = ctx['char']
    
    # Get the source line if available
    source_line = ""
    if ctx['source'] and ctx['line'] > 0:
        lines = ctx['source'].split('\n')
        if 0 < ctx['line'] <= len(lines):
            source_line = lines[ctx['line'] - 1]
    
    # Format location
    location = f"{ctx['file']}:{ctx['line']}:{char_pos}" if ctx['file'] else f"Line {ctx['line']}:{char_pos}"
    
    # Build error message in same format as parse errors
    if source_line:
        pointer = ' ' * char_pos + '^'
        formatted = f"Runtime Error\n  File \"{ctx['file']}\" line {ctx['line']} in {ctx['func']}\n      {source_line}\n      {pointer}\n    {location}: {error_msg}"
    else:
        formatted = f"Runtime Error\n  File \"{ctx['file']}\" line {ctx['line']} in {ctx['func']}\n    {location}: {error_msg}"
    
    return formatted

sys.setrecursionlimit(1000000000)
sys.set_int_max_str_digits(100000000)

runtime = False

AstType = list[dict[str, Any]]

# Save the initial builtin function NAMES to restore on each run
# This prevents user-defined functions from contaminating parallel test runs
builtin_func_names = set(funcs.keys())

# Lock for thread-safe access to global state during parallel test execution
_runtime_lock = threading.Lock()

# Track Python imports for alias resolution
# Maps alias/name -> {'module': str, 'type': 'module'|'name', 'name': str (optional)}
py_imports: dict[str, dict[str, Any]] = {}

# Constants for magic strings
NODE_TYPE_STRUCT_DEF = 'struct_def'
NODE_TYPE_BUILTIN = 'builtin'
NODE_TYPE_FUNCTION = 'function'
NODE_TYPE_VAR = 'var'
NODE_TYPE_CALL = 'call'
NODE_TYPE_IF = 'if'
NODE_TYPE_SWITCH = 'switch'
NODE_TYPE_FOR = 'for'
NODE_TYPE_FOR_IN = 'for_in'
NODE_TYPE_TRY = 'try'
NODE_TYPE_WHILE = 'while'
NODE_TYPE_BREAK = 'break'
NODE_TYPE_CONTINUE = 'continue'
NODE_TYPE_ASSERT = 'assert'
NODE_TYPE_RETURN = 'return'
NODE_TYPE_RAISE = 'raise'
NODE_TYPE_INDEX_ASSIGN = 'index_assign'
NODE_TYPE_FIELD_ASSIGN = 'field_assign'
NODE_TYPE_STRING = 'string'
NODE_TYPE_PY_IMPORT = 'py_import'

# Control flow exceptions for break/continue
class BreakException(Exception):
    def __init__(self, level=1):
        self.level = level
        super().__init__()

class ContinueException(Exception):
    def __init__(self, level=1):
        self.level = level
        super().__init__()

# Helper functions
def is_struct_def(obj: Any) -> bool:
    """Check if an object is a struct definition"""
    return isinstance(obj, dict) and obj.get('type') == NODE_TYPE_STRUCT_DEF

def is_ast_node(obj: Any) -> bool:
    """Check if an object is an AST node (dict with type/structure)"""
    return isinstance(obj, dict)

def extract_value(node: Any) -> Any:
    """Extract the actual value from an AST node or return the value as-is"""
    if isinstance(node, dict):
        return node['value'] if 'value' in node else node
    return node

def ensure_int(value: Any, context: str = "value") -> int:
    """Convert value to int, raising error if not possible"""
    if isinstance(value, int):
        return value
    if isinstance(value, (float, str, bool)):
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise RuntimeError(
                f"{context} must be numeric, got {type(value).__name__}"
            ) from e
    raise RuntimeError(f"{context} must be numeric, not {type(value).__name__}")

def _create_struct_instance(struct_def: dict, args: list) -> dict:
    """Create an instance of a struct from constructor arguments"""
    fields = struct_def['fields']
    return {
        field['name']: extract_value(args[i]) if i < len(args) else None
        for i, field in enumerate(fields)
    }

def _process_function_arg(arg: Any, old_vars: dict) -> Any:
    """Process a single function argument, extracting its value"""
    if isinstance(arg, str):
        return old_vars[arg]['value'] if arg in old_vars else arg
    elif isinstance(arg, dict):
        # Subscript expression (indexing)
        if 'slice' in arg:
            return eval_expr(arg)
        # Field access
        elif 'attr' in arg:
            return eval_expr_node(arg)
        # Regular dict with value
        else:
            return arg.get('value', eval_expr(arg))
    else:
        return arg

def _preserve_struct_definitions() -> dict:
    """Get all struct definitions from current vars"""
    return {k: v for k, v in vars.items() if is_struct_def(v)}

def _bind_function_args(func_args: list, arg_values: list):
    """Bind function arguments to variables in the current scope"""
    from parser import get_type
    
    for func_arg, arg_value in zip(func_args, arg_values):
        # Handle both tuple (name, type) and legacy string formats
        if isinstance(func_arg, tuple) and len(func_arg) == 2:
            arg_name, arg_type = func_arg
        elif isinstance(func_arg, str):
            arg_name = func_arg
        else:
            continue
        
        if isinstance(arg_name, str):
            vars[arg_name] = {
                "type": get_type(arg_value),
                "value": arg_value
            }

def run_func(name: str, args, level=0) -> int|float|bool|str|None|dict|list|Any:
    # sourcery skip: avoid-builtin-shadow
    from parser import cast_args
    global vars, runtime, _current_runtime_vars, _runtime_current_func, _runtime_current_line
    old_vars = vars
    old_func = _runtime_current_func
    old_line = _runtime_current_line  # Save calling line

    # Check if this is a struct constructor call
    if name in vars and is_struct_def(vars[name]):
        return _create_struct_instance(vars[name], args)
    if name not in funcs:
        raise RuntimeError(f'Function "{name}" is not defined.')

    func = funcs[name]

    if not runtime and not func.get('can_eval', True):
        raise SyntaxError(f'Cannot eval function {name} at runtime')

    args = cast_args(args, func)

    # Process all arguments to extract their values
    processed_args = [_process_function_arg(arg, old_vars) for arg in args]

    # Only notify debugger for user-defined functions (not built-ins)
    is_builtin = func['type'] == NODE_TYPE_BUILTIN
    debug_runtime = get_debug_runtime()
    if debug_runtime and not is_builtin:
        debug_runtime.notify_call(name)

    # Only clear vars for user-defined functions, preserving struct definitions
    if not is_builtin:
        vars = _preserve_struct_definitions()
        _current_runtime_vars = vars  # Update current vars for debugger
        _runtime_current_func = name  # Track function for error reporting

    # Bind function arguments to the scope
    if isinstance(func.get('args'), list):
        _bind_function_args(cast(list, func['args']), processed_args)

    # Execute builtin or user-defined function
    if func['type'] == NODE_TYPE_BUILTIN and callable(func['func']):
        out = func['func'](*processed_args)
    else:
        func_body = func['func']
        if not isinstance(func_body, list):
            raise RuntimeError('Invalid function definition.')

        if not all(isinstance(item, dict) for item in func_body):
            raise RuntimeError('Invalid function body.')

        out = run_scope(cast(AstType, func_body), level+1)

    vars = old_vars
    if not is_builtin:
        _current_runtime_vars = vars  # Only restore if we changed it
        _runtime_current_func = old_func  # Restore function name
    _runtime_current_line = old_line  # Always restore calling line

    # Notify debugger of function return (only for user-defined functions)
    debug_runtime = get_debug_runtime()
    if debug_runtime and not is_builtin:
        debug_runtime.notify_return()

    return out

class CompiletimeEvalException(Exception): ...

def _get_indexed_value(target: Any, index: Any) -> Any:
    """Get value from target at index, handling various types"""
    # Ensure index is numeric
    if not isinstance(index, int):
        index = ensure_int(index, "Index")

    if isinstance(target, (list, str)):
        try:
            return target[index]
        except (IndexError, TypeError) as e:
            # Try to find the index operation in the source for better error reporting
            ctx = get_runtime_context()
            if ctx['source'] and ctx['line'] > 0:
                lines = ctx['source'].split('\n')
                if 0 < ctx['line'] <= len(lines):
                    source_line = lines[ctx['line'] - 1]
                    # Try to find the specific index value in the source
                    # Look for patterns like [index] where index matches our error value
                    import re
                    # Handle negative indices - search for the literal value or the negative form
                    search_patterns = [f'[{index}]', f'[-{abs(index)}]'] if index < 0 else [f'[{index}]']

                    char_pos = None
                    for pattern in search_patterns:
                        pos = source_line.find(pattern)
                        if pos >= 0:
                            # Point to the last digit before ']'
                            char_pos = pos + len(pattern) - 2
                            break

                    # Fallback: if we can't find the exact index, look for any bracket pair
                    if char_pos is None:
                        bracket_pos = source_line.find('[')
                        if bracket_pos >= 0:
                            close_bracket = source_line.find(']', bracket_pos)
                            char_pos = close_bracket - 1 if close_bracket > bracket_pos else bracket_pos
                    if char_pos is not None:
                        set_error_char(char_pos)
            # Create detailed error message
            error_msg = f"Index error: list index out of range: {index}"
            if isinstance(target, list):
                error_msg += f" (length: {len(target)})"
            raise RuntimeError(error_msg) from e

    raise RuntimeError(f"Cannot index into type {type(target).__name__}")

def _handle_list_indexing(node: dict) -> Any:
    """Handle list/string indexing: arr[index]"""
    global _runtime_current_line
    
    # Update current line if this node has line info
    if 'line' in node:
        _runtime_current_line = node['line']
    
    target = eval_expr_node(node['value'])
    index = eval_expr_node(node['slice'])
    
    # Extract value if index is still a dict
    index = extract_value(index)
    
    # Handle variable references
    if isinstance(target, str) and target in vars:
        target_val = vars[target].get('value')
        return _get_indexed_value(target_val, index)
    
    return _get_indexed_value(target, index)

def _handle_field_access(node: dict) -> Any:
    """Handle struct field access or Python object attribute access: obj.field"""
    target = eval_expr_node(node['value'])
    field_name = node['attr']

    # If target is a variable name, look it up
    if isinstance(target, str) and target in vars:
        obj = vars[target].get('value')

        # Check if it's a Python object
        if hasattr(obj, '__dict__') or hasattr(obj, field_name):
            # Python object - use getattr
            try:
                return getattr(obj, field_name)
            except AttributeError as e:
                raise RuntimeError(f"Python object has no attribute '{field_name}'") from e

        # Struct field access
        if isinstance(obj, dict) and field_name in obj:
            return obj[field_name]
        raise RuntimeError(f"Object '{target}' has no field '{field_name}'")

    # If target is a Python object directly, access the attribute
    if hasattr(target, '__dict__') or hasattr(target, field_name):
        try:
            return getattr(target, field_name)
        except AttributeError as exc:
            raise RuntimeError(f"Python object has no attribute '{field_name}'") from exc

    # If target is already an object (dict), access the field
    if isinstance(target, dict) and field_name in target:
        return target[field_name]

    raise RuntimeError(f"Cannot access field '{field_name}' on {target}")

def _handle_fstring(node: dict) -> str:
    """Handle f-string (JoinedStr node)"""
    result = ""
    for part in node['values']:
        if isinstance(part, dict):
            # FormattedValue (has 'conversion')
            if 'conversion' in part:
                expr_val = eval_expr_node(part.get('value', {}))
                result += str(expr_val)
            # Constant node (has 'value')
            elif 'value' in part:
                result += str(part['value'])
            else:
                result += str(eval_expr_node(part))
        else:
            result += str(part)
    return result

def _handle_unary_op(node: dict) -> Any:
    """Handle unary operations (-, +, not)"""
    operand = eval_expr_node(node.get('operand', {}))
    op = node['op']

    if op == 'Not':
        return not operand

    elif op == 'UAdd':
        if isinstance(operand, (int, float)):
            return +operand
        raise RuntimeError(f"Cannot apply unary + to {type(operand).__name__}")
    elif op == 'USub':
        if isinstance(operand, (int, float)):
            return -operand
        raise RuntimeError(f"Cannot negate {type(operand).__name__}")
    return operand

def eval_expr_node(node) -> int|float|bool|str|None|Any:
    from parser import get_type

    if not isinstance(node, dict):
        return node

    # Unary operations
    if 'op' in node and node['op'] in ('USub', 'UAdd', 'Not'):
        return _handle_unary_op(node)

    # List literal from Python AST
    if 'elts' in node:
        return [eval_expr_node(elem) for elem in node['elts']]

    # List/string indexing: arr[index]
    if 'value' in node and 'slice' in node:
        return _handle_list_indexing(node)

    # F-string (JoinedStr node)
    if 'values' in node and 'left' not in node and 'op' not in node:
        return _handle_fstring(node)

    # Variable reference
    if 'id' in node:
        value = node['id']
        if value in vars:
            var_value = vars[value].get('value')
            return var_value if var_value is not None else value
        return value
    
    # Function call (from parse_expr - has 'func' key)
    # OR call from f-string expansion (has 'name' key)
    if 'func' in node or ('name' in node and 'type' in node and node['type'] == 'call'):
        # Extract func and args based on node structure
        if 'func' in node:
            func = node['func']
            args = node['args']
        else:
            # F-string expansion format: {type: 'call', name: 'str', args: [...]}
            func = node['name']
            args = node.get('args', [])

        # Check if this is a method call (obj.method())
        if isinstance(func, dict) and 'attr' in func and 'value' in func:
            # This is a method call: obj.method(args)
            # Get the object
            obj = eval_expr_node(func['value'])
            method_name = func['attr']

            # If obj is a variable name, check if it's a module alias first
            if isinstance(obj, str):
                if obj in py_imports:
                    # This is a module function call: ui.Window() where ui is an imported module
                    # Convert to py_call
                    from builtin_funcs import funcs as builtin_funcs
                    py_call_func = builtin_funcs['py_call']['func']
                    return py_call_func(obj, method_name, *[eval_expr_node(arg) for arg in args]) # type: ignore
                elif obj in vars:
                    obj = vars[obj].get('value')

            if not hasattr(obj, '__dict__') and not hasattr(obj, method_name):
                raise RuntimeError(f"Object has no method '{method_name}'")

            # Python object - call method directly
            method = getattr(obj, method_name)
            if not callable(method):
                raise RuntimeError(f"'{method_name}' is not a callable method")
            evaluated_args = [eval_expr_node(arg) for arg in args]
            return method(*evaluated_args)
        # Regular function call
        # Prepare arguments
        new_args = []
        for arg in args:
            # Check if this is a complex expression that needs evaluation
            # (slice, attr, or other runtime expressions)
            if 'slice' in arg or 'attr' in arg or ('value' in arg and isinstance(arg.get('value'), dict)):
                # Evaluate the expression first
                arg = eval_expr_node(arg)
                arg = {"value": arg, "type": get_type(arg)}
            elif 'value' not in arg:
                arg = eval_expr_node(arg)
                arg = {"value": arg, "type": get_type(arg)}
            new_args.append({"value": arg['value'], "type": get_type(arg['value'])})

        # Get function name - could be 'func' or 'name' key
        func_id = None
        if isinstance(func, dict):
            func_id = func.get('id')
        elif isinstance(func, str):
            func_id = func
        else:
            # Check if node has 'name' key directly (from f-string expansion)
            func_id = node.get('name')
            
        if isinstance(func_id, str):
            return run_func(func_id, new_args)
        raise RuntimeError(f"Invalid function call: {func}")

    # Binary expression (left op right)
    if 'left' in node:
        return eval_expr(node)

    # Boolean operations (And, Or) with multiple values
    if 'op' in node and 'values' in node and node['op'] in ('And', 'Or'):
        return eval_expr(node)

    # Field access: obj.field
    if 'attr' in node and 'value' in node:
        return _handle_field_access(node)

    # String literal
    if 'type' in node and node['type'] == NODE_TYPE_STRING:
        return node.get('value', '')

    # Direct value
    if 'value' in node:
        return node['value']

    # AST node with type
    if 'type' in node:
        return run_scope([node])

    # Struct instance (has 'mods' or is a plain dict with simple values)
    if isinstance(node, dict):
        # Check if it looks like a struct instance (no AST keys like 'func', 'op', 'args', etc.)
        ast_keys = {'func', 'op', 'ops', 'left', 'right', 'args', 'type', 'id', 'attr', 'slice', 'value', 'values'}
        if all(key not in node for key in ast_keys):
            # Looks like a struct instance - return as-is
            return node
        if 'mods' in node:
            return node

    raise SyntaxError(f'Invalid node: {node}')

def eval_expr_calc(left, op, right):
    # Comparisons
    if op == 'Eq':
        return left == right
    elif op == 'NotEq':
        return left != right
    elif op == 'NotQq':
        return left != right
    elif op == 'Gt':
        return left > right
    elif op == 'Lt':
        return left < right
    elif op == 'GtE':
        return left >= right
    elif op == 'LtE':
        return left <= right
    elif op == 'Or':
        return bool(left or right)
    elif op == 'And':
        return bool(left and right)
    elif op == 'Not':
        return not left
    elif op == 'BitXor':
        return left ^ right
    elif op == 'BitAnd':
        return left & right
    elif op == 'BitOr':
        return left | right

    elif op in ['Add', '+']:
        return left + right
    elif op in ['Sub', '-']:
        return left - right
    elif op in ['Mult', '*']:
        return left * right
    elif op in ['Div', '/']:
        return left / right
    elif op in ['Pow', '**']:
        return left** right
    elif op in ['Mod', '%']:
        return left % right
    else:
        raise RuntimeError(f'Invalid operator: {op}')

def eval_expr(expr, level=0) -> int|float|bool|str|None:
    # Handle non-dict expressions
    if not isinstance(expr, dict):
        if isinstance(expr, str) and runtime:
            if level < 10:
                return eval_expr(parse_expr(expr), level+1)
            if expr.startswith('"') and expr.endswith('"'):
                return str(expr)
            raise RuntimeError(f'{expr} is not defined.')
        return expr  # type: ignore[return-value]

    # Delegate to eval_expr_node if it's a value node
    if 'op' not in expr and 'ops' not in expr and (
        'id' in expr or 'func' in expr or 'left' in expr or 
        'value' in expr or 'type' in expr
    ):
        return eval_expr_node(expr)

    # Handle unary operations
    if 'left' not in expr:
        if 'op' not in expr:
            # No operator and no left operand - treat as node expression
            return eval_expr_node(expr)
        ops = [expr['op']]
        if 'operand' in expr:
            return _handle_unary_op(expr)
        left = eval_expr_node(expr['values'][0])
        comps = expr['values'][1:]
    elif 'ops' in expr:
        left = eval_expr_node(expr['left'])
        ops = expr['ops']
        comps = expr['comparators']
    elif 'op' in expr:
        left = eval_expr_node(expr['left'])
        ops = [expr['op']]
        comps = [expr.get('right', False)]
    else:
        raise RuntimeError('Invalid expression')

    # Evaluate comparison/operation chain
    for op, comp in zip(ops, comps):
        comp = eval_expr_node(comp)

        # Resolve variable references
        if isinstance(left, str) and left in vars:
            left_old = left
            left = vars[left]['value']
            if left is None:
                raise RuntimeError(f'{left_old} is defined but not set.')

        if left is None:
            raise RuntimeError(f'Invalid Expression: {expr}')

        try:
            left = eval_expr_calc(left, op, comp)
        except Exception as e:
            if isinstance(left, str):
                raise SyntaxError(f'{left} is not defined.') from e
            # Re-raise all other exceptions (ZeroDivisionError, etc.)
            raise

    return left

def _handle_loop_control(e: BreakException | ContinueException, level_threshold: int = 1):
    """Handle break/continue exceptions, decrementing level if needed"""
    if e.level <= level_threshold:
        raise
    # Decrement level and re-raise for outer loop
    if isinstance(e, BreakException):
        raise BreakException(e.level - 1)
    else:
        raise ContinueException(e.level - 1)

def _execute_node_function(node: dict, level: int):
    """Handle function definition node"""
    if level >= 1:
        raise RuntimeError('Non-global level function declaration not allowed.')
    
    funcs[node['name']] = {
        "type": "func",
        "args": node['args'],
        "func": node['scope'],
        "return_type": node['return'],
        "can_eval": False
    }

def _execute_node_struct_def(node: dict):
    """Handle struct definition node"""
    vars[node['name']] = {
        "type": NODE_TYPE_STRUCT_DEF,
        "fields": node['fields']
    }

def _execute_node_py_import(node: dict):
    """Handle py_import node"""
    module_name = node.get('module', '')
    alias = node.get('alias')
    name = node.get('name')
    
    if not module_name:
        return
    
    # Call the py_import builtin to import the module
    run_func('py_import', [module_name])
    
    # Track the import for alias resolution
    if name:
        # "from module py_import name" or "from module py_import name as alias"
        key = alias or name
        py_imports[key] = {
            'module': module_name,
            'type': 'name',
            'name': name
        }
    else:
        # "py_import module" or "py_import module as alias"
        key = alias or module_name
        py_imports[key] = {
            'module': module_name,
            'type': 'module'
        }

def _execute_node_var(node: dict):
    """Handle variable declaration node"""
    from parser import cast_value
    import copy
    
    value = cast_value(node['value'], node['value_type'])
    
    # Evaluate f-strings and expressions
    if isinstance(value, dict):
        # Check if it's a runtime expression (has slice, attr, or other runtime features)
        if 'slice' in value or 'attr' in value or ('values' in value and 'value' not in value):
            value = eval_expr_node(value)
        elif 'value' not in value:
            value = eval_expr_node(value)
        else:
            value = value['value']
    
    # Make a deep copy of mutable objects to avoid mutating the AST
    if isinstance(value, (list, dict, set)):
        value = copy.deepcopy(value)

    vars[node['name']] = {
        "type": node['value_type'],
        "value": value
    }

def _execute_node_index_assign(node: dict):
    """Handle array/list index assignment: arr[i] = value"""
    target_name = node['target']
    if target_name not in vars:
        raise RuntimeError(f"Variable '{target_name}' is not defined")
    
    target = vars[target_name]['value']
    index = ensure_int(eval_expr(node['index']), "Index")
    value = eval_expr(node['value'])
    
    if isinstance(target, list):
        if index < 0 or index >= len(target):
            raise RuntimeError(f"Index {index} out of range for list of length {len(target)}")
        target[index] = value
    else:
        raise RuntimeError(f"Cannot index into type {type(target).__name__}")

def _execute_node_field_assign(node: dict):
    """Handle struct field assignment: obj.field = value"""
    target_name = node['target']
    
    # Check if it's a Python module import alias
    if target_name in py_imports:
        # Setting attribute on a Python module
        field_name = node['field']
        value = eval_expr(node['value'])
        # Use setattr to set the module attribute
        import sys
        import_info = py_imports[target_name]
        module_name = import_info['module']
        
        # Import the module to get reference
        if module_name not in sys.modules:
            __import__(module_name)
        module = sys.modules[module_name]
        setattr(module, field_name, value)
        return
    
    if target_name not in vars:
        raise RuntimeError(f"Variable '{target_name}' is not defined")
    
    target = vars[target_name]['value']
    target_type = vars[target_name]['type']
    field_name = node['field']
    value = eval_expr(node['value'])
    
    # Handle pyobject types using py_setattr
    if target_type in ('pyobject', 'pyobj'):
        from builtin_funcs import funcs as builtin_funcs
        py_setattr_func = cast(Any, builtin_funcs['py_setattr']['func'])
        py_setattr_func(target, field_name, value)
        return
    
    if isinstance(target, dict) and field_name in target:
        target[field_name] = value
    else:
        raise RuntimeError(f"Object '{target_name}' has no field '{field_name}'")

def _execute_node_if(node: dict) -> Any:
    """Handle if/elif/else statement"""
    condition_result = eval_expr(node['condition'])
    
    if condition_result:
        return run_scope(node['scope'])

    # Try elif branches
    if node['elifs']:
        for elif_node in node['elifs']:
            if eval_expr(elif_node['condition']):
                return run_scope(elif_node['scope'])

    # Execute else if present
    if node['else']:
        return run_scope(node['else'])
    return None

def _execute_node_switch(node: dict) -> Any:
    """Handle switch statement"""
    switch_value = eval_expr(node['expr'])

    # Try to match against each case
    for case in node['cases']:
        for case_val_node in case['values']:
            case_val = extract_value(case_val_node)
            if switch_value == case_val:
                # Execute the case body and return immediately
                return run_scope(case['body'])

    # Execute default if no match
    return run_scope(node['default']) if node['default'] else None

def _execute_node_for(node: dict, level: int):
    """Handle for loop with range"""
    start_val = ensure_int(eval_expr(node['start']), "Start value")
    end_val = ensure_int(eval_expr(node['end']), "End value")
    step_val = ensure_int(eval_expr(node.get('step', 1)), "Step value") if 'step' in node else 1
    
    for i in range(start_val, end_val, step_val):
        vars[node['var']] = {"type": "int", "value": i}
        try:
            run_scope(node['scope'], level+1)
        except (BreakException, ContinueException) as e:
            if e.level <= 1:
                if isinstance(e, BreakException):
                    break
                continue
            _handle_loop_control(e, 1)

def _execute_node_for_in(node: dict, level: int):
    """Handle for-in loop (iterate over list/string)"""
    iterable_expr = node['iterable']
    iterable = eval_expr_node(iterable_expr) if isinstance(iterable_expr, dict) else iterable_expr
    
    # Handle variable references
    if isinstance(iterable, str) and iterable in vars:
        iterable = vars[iterable]['value']
    
    if not isinstance(iterable, (list, str)):
        raise RuntimeError(f'Cannot iterate over non-iterable type: {type(iterable).__name__}')
    
    for item in iterable:
        vars[node['var']] = {"type": get_type(item), "value": item}
        try:
            run_scope(node['scope'], level+1)
        except (BreakException, ContinueException) as e:
            if e.level <= 1:
                if isinstance(e, BreakException):
                    break
                continue
            _handle_loop_control(e, 1)

def _execute_node_while(node: dict):
    """Handle while loop"""
    while eval_expr(node['condition']):
        try:
            run_scope(node['scope'])
        except (BreakException, ContinueException) as e:
            if e.level <= 1:
                if isinstance(e, BreakException):
                    break
                continue
            _handle_loop_control(e, 1)

def _execute_node_assert(node: dict):
    """Handle assert statement"""
    result = eval_expr(node['condition'])
    if not result:
        if node.get('message'):
            message = eval_expr(node['message'])
            raise AssertionError(message)
        raise AssertionError('Assertion failed')

def _execute_node_try(node: dict, level: int) -> Any:
    """Handle try-except statement"""
    try:
        # Execute the try block
        result = run_scope(node['try_scope'], level+1)
        return result
    except Exception as e:
        # Get the exception type name
        exc_name = type(e).__name__
        expected_exc = node['exc_type']
        
        # Check if the exception type matches
        if exc_name == expected_exc:
            # Execute the except block
            result = run_scope(node['except_scope'], level+1)
            return result
        else:
            # Re-raise if it doesn't match
            raise

def _execute_node_raise(node: dict):
    """Handle raise statement"""
    global _runtime_current_char
    
    exc_type = node.get('exc_type')
    message = node.get('message', '')
    
    # Update character position for error reporting
    if 'char' in node:
        _runtime_current_char = node['char']
    
    if not exc_type:
        # Bare raise - re-raise current exception
        raise
    
    # Map exception type string to Python exception class
    exc_classes = {
        'ZeroDivisionError': ZeroDivisionError,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'IndexError': IndexError,
        'KeyError': KeyError,
        'AttributeError': AttributeError,
        'RuntimeError': RuntimeError,
        'AssertionError': AssertionError,
        'Exception': Exception,
    }
    
    exc_class = exc_classes.get(exc_type, RuntimeError)
    
    # Include exception type in message for better error reporting
    full_message = f"[{exc_type}] {message}" if message else f"[{exc_type}]"
    
    raise exc_class(full_message)

def run_scope(ast: AstType, level=0):
    """Execute a scope (list of AST nodes)"""
    global _runtime_current_line
    result = None

    for idx, node in enumerate(ast):
        # Update current line for error context
        if isinstance(node, dict):
            _runtime_current_line = node.get('line', idx + 1)
        else:
            _runtime_current_line = idx + 1
            
        if debug_runtime := get_debug_runtime():
            debug_runtime.notify_line(_runtime_current_line)

        # Handle call expressions from AST first (e.g. method calls like obj.method())
        # These don't have a 'type' key, just 'func' and 'args'
        if 'func' in node and 'args' in node and 'type' not in node:
            # Execute the expression but discard the result since this is used as a statement
            result = eval_expr(node)
            continue

        node_type = node['type']

        # Handle each node type
        if node_type == NODE_TYPE_FUNCTION:
            _execute_node_function(node, level)
        elif node_type == NODE_TYPE_STRUCT_DEF:
            _execute_node_struct_def(node)
        elif node_type == NODE_TYPE_PY_IMPORT:
            _execute_node_py_import(node)
        elif node_type == NODE_TYPE_VAR:
            _execute_node_var(node)
        elif node_type == NODE_TYPE_INDEX_ASSIGN:
            _execute_node_index_assign(node)
        elif node_type == NODE_TYPE_FIELD_ASSIGN:
            _execute_node_field_assign(node)
        elif node_type == NODE_TYPE_CALL:
            result = run_func(node['name'], node['args'], level)
            if len(ast) == 1:
                return result
        elif node_type == NODE_TYPE_IF:
            result = _execute_node_if(node)
            if result is not None:
                return result
        elif node_type == NODE_TYPE_SWITCH:
            result = _execute_node_switch(node)
            if result is not None:
                return result
        elif node_type == NODE_TYPE_FOR:
            _execute_node_for(node, level)
        elif node_type == NODE_TYPE_FOR_IN:
            _execute_node_for_in(node, level)
        elif node_type == NODE_TYPE_WHILE:
            _execute_node_while(node)
        elif node_type == NODE_TYPE_TRY:
            result = _execute_node_try(node, level)
            if result is not None:
                return result
        elif node_type == NODE_TYPE_BREAK:
            raise BreakException(node.get('level', 1))
        elif node_type == NODE_TYPE_CONTINUE:
            raise ContinueException(node.get('level', 1))
        elif node_type == NODE_TYPE_ASSERT:
            _execute_node_assert(node)
        elif node_type == NODE_TYPE_RETURN:
            return eval_expr(node['value'])
        elif node_type == NODE_TYPE_RAISE:
            _execute_node_raise(node)
        else:
            raise RuntimeError(f'Unknown node type: {node_type}')

    return result

def run(ast:AstType, file:str='', source:str=''):
    # Use lock to prevent race conditions in parallel test execution
    with _runtime_lock:
        global vars, runtime, funcs, py_imports, _current_runtime_vars
        global _runtime_file, _runtime_source, _runtime_current_func
        
        # Initialize runtime context for error formatting
        _runtime_file = file
        _runtime_source = source
        _runtime_current_func = '<module>'
        
        runtime = True
        # Reset vars to clear any state from previous runs (critical for parallel test execution)
        vars.clear()
        _current_runtime_vars = vars  # Initialize current vars tracking
        # Reset py_imports to clear any import aliases from previous runs
        py_imports.clear()
        # Reset funcs to only include builtin functions (remove user-defined functions from previous runs)
        # Remove any functions that are not in the original builtin set
        user_func_names = [name for name in funcs.keys() if name not in builtin_func_names]
        for name in user_func_names:
            del funcs[name]

        run_scope(ast)

        if 'main' not in funcs:
            raise RuntimeError('Missing main function')

        run_func('main', sys.argv[3:])
__all__ = [
    'run',
    'eval_expr',
    'run_scope',
    'vars',
    'runtime'
]


