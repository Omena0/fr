from utils import InputStream, strip_all, split
from builtin_funcs import funcs
from typing import Any, cast
import ast
import sys
import threading

AstType = list[dict[str, Any]]
VarType = dict[str, dict[str, Any]]

# Base types
types = ['bool', 'int', 'float', 'string', 'str', 'set', 'list', 'dict', 'pyobject', 'pyobj', 'any']

# Const: Value will not change and cannot be changed
# If the parser cannot eval the value then an exception is thrown.
modifiers = ['const']

current_func = '<module>'

# Track loop depth for break/continue validation
loop_depth = 0

vars:VarType = {}

# Save the initial builtin function NAMES to restore on each parse
# This prevents user-defined functions from contaminating subsequent parses
builtin_func_names = set(funcs.keys())

class SkipNode: ...

def make_node(stream: InputStream, **kwargs) -> dict[str, Any]:
    """Create an AST node with line number information"""
    node = dict(kwargs)
    if 'line' not in node:
        node['line'] = stream.line
    return node

def is_literal(value):
    if not isinstance(value, dict):
        value = parse_literal(value)

    # Variable references are not literals (even if their value is known)
    if isinstance(value, str):
        return False

    if not isinstance(value, dict):
        return True

    return 'const' in value.get('mods', [])

def get_type(value:Any) -> str:
    return type(value).__name__

def parse_fstring(content: str) -> dict[str, Any]:
    """Parse an f-string and return a string concatenation expression.
    
    Example: f"Hello {name}, you are {age} years old"
    Becomes: "Hello " + str(name) + ", you are " + str(age) + " years old"
    """
    parts = []
    current = ""
    i = 0

    while i < len(content):
        if content[i] == '{':
            # Save the current literal part if any
            if current:
                parts.append({
                    "type": "string",
                    "value": current
                })
                current = ""

            # Find the matching closing brace
            depth = 1
            j = i + 1
            expr_str = ""
            while j < len(content) and depth > 0:
                if content[j] == '{':
                    depth += 1
                elif content[j] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                expr_str += content[j]
                j += 1

            if depth != 0:
                raise SyntaxError("Unclosed brace in f-string")

            # Parse the expression inside the braces
            expr_result = parse_expr(expr_str.strip())

            # Wrap the expression in str() conversion
            str_call = {
                "type": "call",
                "name": "str",
                "args": [expr_result]
            }
            parts.append(str_call)

            i = j + 1
        else:
            current += content[i]
            i += 1

    # Add any remaining literal part
    if current:
        parts.append({
            "type": "string",
            "value": current
        })

    # If only one part, return it directly
    if not parts:
        return {
            "type": "string",
            "value": ""
        }
    elif len(parts) == 1:
        return parts[0]

    # Build a chain of concatenations
    result = parts[0]
    for part in parts[1:]:
        result = {
            "type": "binop",
            "op": "+",
            "left": result,
            "right": part
        }

    return result

def _extract_value(elem: Any) -> Any:
    """Extract the actual value from a parsed element (dict with 'value' key or raw value)."""
    return elem['value'] if isinstance(elem, dict) and 'value' in elem else elem

def _parse_list_elements(list_content: str) -> list[Any]:
    """Parse comma-separated list elements, respecting nesting depth."""
    elements = []
    depth = 0
    current = ""
    
    for char in list_content:
        if char in '([{':
            depth += 1
            current += char
        elif char in ')]}':
            depth -= 1
            current += char
        elif char == ',' and depth == 0:
            if current.strip():
                elem = parse_literal(current.strip())
                elements.append(_extract_value(elem))
            current = ""
        else:
            current += char
    
    # Handle last element
    if current.strip():
        elem = parse_literal(current.strip())
        elements.append(_extract_value(elem))
    
    return elements

def _has_operators_outside_context(text: str) -> bool:
    """Check if text has operators outside of strings/parentheses (i.e., is an expression)."""
    in_string = False
    escape_next = False
    paren_depth = 0
    
    for i, c in enumerate(text):
        if escape_next:
            escape_next = False
            continue
            
        if c == '\\':
            escape_next = True
            continue
            
        if c == '"':
            in_string = not in_string
        elif not in_string:
            if c == '(':
                paren_depth += 1
            elif c == ')':
                paren_depth -= 1
            elif paren_depth == 0 and c in {'+', '-', '*', '/', '%', '<', '>', '=', '!', '&', '|'}:
                return True
    
    return False

def parse_literal(text: str) -> dict[str, str|Any] | Any:
    """Parse a literal value (string, number, bool, list) or return text if it's a variable/expression."""
    text = text.strip()

    # List literal: [1, 2, 3]
    if text.startswith('[') and text.endswith(']'):
        list_content = text[1:-1].strip()
        if not list_content:
            return {"type": "list", "value": []}

        elements = _parse_list_elements(list_content)
        return {"type": "list", "value": elements}

    # Check if this is an expression with operators
    if _has_operators_outside_context(text):
        return parse_expr(text)

    # F-String: f"Hello {name}"
    if text.startswith('f"') and text.endswith('"'):
        return parse_fstring(text[2:-1])

    # String literal: "hello"
    if text.startswith('"') and text.endswith('"'):
        return {"type": "string", "value": text[1:-1]}

    # Integer: 123
    if text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
        return {"type": "int", "value": int(text)}

    # Float: 123.456
    if '.' in text:
        try:
            return {"type": "float", "value": float(text)}
        except ValueError:
            pass  # Not a valid float, continue to other checks

    # Boolean: true/false
    if text in {'true', 'false'}:
        return {"type": "bool", "value": text}

    # Function call: func(args)
    if text.endswith(')') and '(' in text:
        potential_name = text.split('(')[0]
        if potential_name in funcs:
            func_stream = InputStream(text)
            name = func_stream.consume_word()
            return parse_func_call(func_stream, name)

    # Variable name or unparseable text
    return text

def _try_parse_as_function_call(value_str: str, parent_stream: InputStream | None) -> dict | None:
    """Try to parse a string as a function call. Returns dict node or None if not a function call."""
    func_stream = InputStream(value_str, parent_stream=parent_stream, offset_in_parent=0) if parent_stream else InputStream(value_str)
    if parent_stream:
        func_stream.file_path = parent_stream.get_root_stream().file_path
    
    name = func_stream.consume_word()
    if func_stream.peek_char(1) != '(':
        return None
    
    if name not in funcs:
        error_msg = (parent_stream.format_error(f'Function {name}() is not defined.') 
                    if parent_stream 
                    else func_stream.format_error(f'Function {name}() is not defined.'))
        raise SyntaxError(error_msg)
    
    return parse_func_call(func_stream, name)

def parse_as_type(value: Any, target_type: str, can_be_func: bool = True, parent_stream: InputStream | None = None):
    """Convert a value to the specified type, handling expressions, function calls, and type casting."""
    # If value is already a dict (expression node), return it as-is
    if isinstance(value, dict):
        return value
    
    # Check if it's a variable reference
    if value and isinstance(value, str) and value in vars:
        return vars[value]

    # Try to parse as function call
    if can_be_func and isinstance(value, str):
        func_result = _try_parse_as_function_call(value.strip(), parent_stream)
        if func_result is not None:
            return func_result

    # Try to cast to the requested type
    try:
        if target_type == 'string':
            # Strip quotes if present
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return str(value)
        elif target_type == 'int':
            return int(value)
        elif target_type == 'float':
            return float(value)
        elif target_type == 'bool':
            return bool(value)
        else:
            # Unknown type, return as-is
            return value
    except (ValueError, TypeError) as e:
        value_type_name = value.__class__.__name__
        raise SyntaxError(f'Could not cast {value_type_name} -> {target_type}. [{value}]') from e

def _split_args(args_text: str) -> list[str]:
    """Split comma-separated arguments, respecting parentheses and string literals."""
    if not args_text.strip():
        return []
    
    # Use the split function from utils which handles strings and parentheses
    args = split(args_text, ',')
    
    # Strip whitespace from each argument
    return [arg.strip() for arg in args if arg.strip()]

def _parse_typed_arg(arg: str, check_comma: bool, stream: InputStream, line: int) -> tuple[str, str | None]:
    """Parse a single argument which may have a type annotation.
    
    Returns (name, type) where type is None if untyped.
    """
    parts = arg.split()
    
    if len(parts) == 1:
        # Untyped argument: "x"
        return (parts[0], None)
    elif len(parts) == 2 and parts[0] in types:
        # Typed argument: "int x"
        return (parts[1], parts[0])
    else:
        # Invalid format
        if check_comma and len(parts) >= 2:
            # Has space but not a valid type, probably missing comma
            orig = stream.orig_line(line)
            char = orig.find(arg) + len(parts[0]) + 1
            raise SyntaxError(f'?{line},{char}:Expected ",".')
        else:
            raise SyntaxError(f'Invalid argument "{arg}".')

def parse_args(stream: InputStream, check_comma: bool = True, parse_types: bool = False) -> list[tuple[str, str | None]]:
    """Parse function arguments. 
    
    Args:
        stream: Input stream positioned before '('
        check_comma: Whether to validate comma separation
        parse_types: If True, parse type annotations; if False, return raw values

    Returns:
        List of tuples: (name, type) where type is None if untyped or parse_types=False
    """
    stream.strip()
    if not stream.consume('('):
        raise SyntaxError(stream.format_error(f'Expected "(" but got "{stream.peek(10)}"'))

    line = stream.line
    
    # Read until matching closing parenthesis
    args_text = ''
    depth = 1
    new_arg = True
    
    while depth > 0 and stream.text:
        chr = stream.seek(1)
        
        if chr == '(':
            depth += 1
        elif chr == ')':
            depth -= 1
            if depth == 0:
                break
        elif chr == ',':
            new_arg = True
        else:
            new_arg = False
        
        if chr == '\n' and not new_arg:
            stream.seek_back_line()
            raise SyntaxError(stream.format_error('Expected ")"'))
        
        if depth > 0:  # Don't include the final ')'
            args_text += chr

    if depth != 0:
        raise SyntaxError(stream.format_error('Expected ")"'))

    stream.strip()

    if not args_text.strip():
        return []

    args = _split_args(args_text)

    # Parse arguments based on parse_types flag
    if not parse_types:
        return [(arg, None) for arg in args]
    
    return [_parse_typed_arg(arg, check_comma, stream, line) for arg in args]

def _normalize_operators(text: str) -> str:
    """Normalize custom operators to Python equivalents."""
    # Replace bitwise operators with logical operators
    # Note: This changes semantics but matches the language's intent
    # First replace double operators, then single ones
    result = text.replace('&&', ' and ').replace('||', ' or ')
    # Replace negation operator with 'not'
    # Handle cases like "!1" -> "not 1"
    import re
    result = re.sub(r'!(\w+|\()', r'not \1', result)
    # Replace remaining single operators
    result = result.replace('&', ' and ').replace('|', ' or ')
    result = result.replace('\n', ' ')
    return result

def parse_expr(text: str):
    """Parse an expression using Python's AST parser and optionally evaluate constants."""
    from runtime import eval_expr
    import runtime as runtime_module

    # Save and restore parse-time mode
    old_runtime = runtime_module.runtime
    runtime_module.runtime = False
    
    try:
        text = _normalize_operators(text)
        expr = ast.parse(text, mode='eval').body

        def _ast_to_dict(node):
            """Convert AST node to dictionary representation."""
            if not node._fields:
                return str(get_type(node))

            result = {}
            for field in node._fields:
                # Skip "ctx" field as it's not needed for execution
                if field == 'ctx':
                    continue

                value = getattr(node, field)
                
                # Recursively convert AST nodes
                if hasattr(value, '_fields'):
                    value = _ast_to_dict(value)
                elif isinstance(value, list):
                    value = [_ast_to_dict(item) for item in value]
                
                if value is not None:
                    result[field] = value

            return result

        expr_dict = _ast_to_dict(expr)

        # Try to evaluate constant expressions at parse time
        try:
            # Don't evaluate struct constructors at parse time
            if 'func' in expr_dict:
                func_name = expr_dict['func'].get('id') if isinstance(expr_dict['func'], dict) else None # type: ignore
                if func_name:
                    # Check if it's a direct struct constructor
                    if func_name in vars and vars[func_name].get('type') == 'struct_def':
                        return expr_dict
                    # Check if it's a function that returns a struct type
                    if func_name in funcs:
                        return_type = funcs[func_name].get('return_type')
                        if return_type and return_type in vars and vars[return_type].get('type') == 'struct_def': # type: ignore
                            return expr_dict
            
            evaluated = eval_expr(expr_dict)
            # Only use evaluated result if it's a proper constant (not a variable name)
            # and the expression doesn't contain operators (already constant)
            # Don't evaluate if it's just a variable reference ('id' key indicates a Name node)
            if (evaluated is not None 
                and not isinstance(evaluated, str) 
                and 'op' not in expr_dict 
                and 'ops' not in expr_dict
                and 'id' not in expr_dict):  # Variable reference - keep as expr_dict
                return evaluated
        except Exception:
            pass  # Can't evaluate at parse time, return the expression dict

        return expr_dict
    finally:
        runtime_module.runtime = old_runtime

def parse_scope(stream: InputStream, level: int = 0) -> AstType:
    """Parse a code block enclosed in braces { }."""
    stream.strip()
    if not stream.consume('{'):
        raise SyntaxError(stream.format_error('Expected "{".'))

    ast = parse(stream, level=level+1)

    stream.strip()
    if not stream.consume('}'):
        raise SyntaxError(stream.format_error('Expected "}".'))

    return ast

def parse_func(stream:InputStream, name:str, type:str, mods:list=[]) -> dict[str, str|Any] | type[SkipNode]:
    global current_func
    current_func = name

    args = parse_args(stream, parse_types=True)
    for arg_name, arg_type in args:
        vars[arg_name] = {
            "type": arg_type or "none",
            "value": None
        }

    scope = parse_scope(stream)
    stream.strip()


    funcs[name] = {
        "type": "func",
        "args": args,
        "func": scope,
        "mods": mods,
        "return_type": type
    }

    if 'const' in mods:
        return SkipNode

    return make_node(stream,
        type="function",
        name=name,
        **{"return": type},
        args=args,
        scope=scope,
        mods=mods
    )

def parse_var(stream: InputStream, var_type: str | None, name: str, mods: list = []) -> dict[str, Any] | type[SkipNode]:
    """Parse a variable declaration or assignment.
    
    Args:
        stream: Input stream positioned after variable name
        var_type: Type annotation (None for reassignments)
        name: Variable name
        mods: List of modifiers like 'const'
    
    Returns:
        Variable AST node or SkipNode if const
    """
    stream.strip()

    if not stream.consume('='):
        raise SyntaxError(stream.format_error('Expected "=".'))

    # Save line number before consuming the value
    value_line = stream.line
    
    # Parse the value expression
    value_text = stream.consume_until('\n').strip().rstrip(';')
    value = parse_expr(value_text)

    if var_type is None:
        var_type = vars[name].get('type', 'any') if name in vars else 'any'
    # Type check/cast for non-dict values (var_type is guaranteed to be str here)
    if not isinstance(value, dict):
        value = parse_as_type(value, var_type, parent_stream=stream) # type: ignore

    # Build the variable info dict
    var_info = {
        "type": var_type,
        "value": value,
        "mods": mods
    }

    # Store in global vars table
    vars[name] = var_info

    # Const variables are compile-time only
    if 'const' in mods:
        return SkipNode

    # Return AST node for runtime with correct line number
    node = make_node(stream,
        type="var",
        name=name,
        value_type=var_type,
        value=value,
        mods=mods
    )
    # Override with the line where the value starts
    node['line'] = value_line
    return node

def _is_runtime_expression(value: dict) -> bool:
    """Check if a dict represents an expression that must be evaluated at runtime."""
    # Subscript expressions (indexing): arr[i]
    if 'slice' in value:
        return True
    
    # Field access: obj.field
    if 'attr' in value:
        return True
    
    # F-strings or other complex expressions
    if 'values' in value and 'value' not in value:
        return True
    
    # Function calls that can't be evaluated at compile time
    if value.get('type') == 'call':
        func_name = value.get('name', '')
        return not funcs.get(func_name, {}).get('can_eval', False)
    
    return False

def cast_value(value: Any, required_type: str):
    """Cast a value to the required type, handling variables, expressions, and function calls."""
    # Handle string values (might be variables or expressions)
    if isinstance(value, str):
        # Variable reference
        if value in vars:
            var_info = vars[value]
            # Can't substitute non-literal variables
            return var_info if is_literal(value) else parse_expr(value)
        # Function call
        if '(' in value:
            func_stream = InputStream(value)
            func_name = func_stream.consume_word()
            try:
                return parse_func_call(func_stream, func_name)
            except SyntaxError:
                # Can't parse as function call, treat as expression
                return parse_expr(value)

        # General expression
        return parse_expr(value)

    # Handle dict values (AST nodes)
    if not isinstance(value, dict):
        # Primitive value, try to cast
        actual_type = get_type(value)
        if actual_type != required_type:
            new_value = parse_as_type(value, required_type, can_be_func=False)
            if new_value is None:
                raise SyntaxError(f'Cannot cast {actual_type} -> {required_type}')
            return {"type": required_type, "value": new_value}
        return value

    # Runtime expressions must be kept as-is
    if _is_runtime_expression(value):
        return value

    # Accept any type if required type is 'any'
    if required_type == 'any':
        return value

    # Extract type and value from dict
    value_type = value.get('type')
    actual_value = value.get('value')

    # If no value key, return as-is (complex expression)
    if 'value' not in value:
        return value

    # Type matches, return as-is
    if value_type == required_type:
        return value

    # Try to cast
    new_value = parse_as_type(actual_value, required_type, can_be_func=False)
    if new_value is None:
        raise SyntaxError(f'Cannot cast {value_type} -> {required_type}')

    return {"type": required_type, "value": new_value}

def cast_args(args: list, func: dict) -> list:
    """Cast function arguments to match the function's expected types."""
    func_args = func.get('args', [])
    
    # Handle both dict and list formats for function args
    if isinstance(func_args, dict):
        arg_types = list(func_args.values())
    elif isinstance(func_args, list):
        # List of tuples: [(name, type), ...]
        arg_types = [arg_type for _, arg_type in func_args]
    else:
        return args

    # Cast each argument to its required type
    for i, arg in enumerate(args):
        if i >= len(arg_types):
            continue  # No type requirement for this arg
        
        required_type = arg_types[i]
        if required_type is None:
            continue  # No type requirement
        
        casted = cast_value(arg, required_type)
        if casted != arg:
            args[i] = casted

    return args

def _can_eval_at_parse_time(func: dict, arg_values: list) -> bool:
    """Check if a function call can be evaluated at parse time."""
    func_mods = func.get('mods', [])
    is_const = isinstance(func_mods, list) and 'const' in func_mods
    
    # Const functions are always evaluated at parse time
    if is_const:
        return True
    
    # Don't evaluate functions that return struct types at parse time
    # (C VM needs runtime calls for struct constructors)
    return_type = func.get('return_type', 'none')
    if isinstance(return_type, str) and return_type in vars and vars[return_type].get('type') == 'struct_def':
        return False
    
    # Function must allow evaluation and all args must be literals
    return (func.get('can_eval', True) and 
            all(is_literal(arg) for arg in arg_values))

def _eval_func_at_parse_time(name: str, func: dict, arg_values: list) -> Any:
    """Evaluate a function call at parse time (compile time)."""
    func_type = func['type']
    
    # Extract actual values from argument nodes
    func_args = []
    for arg in arg_values:
        if isinstance(arg, dict):
            func_args.append(arg.get('value', arg))
        else:
            func_args.append(arg)
    
    # Evaluate builtin function
    if func_type == 'builtin':
        func_callable = func.get('func')
        if not callable(func_callable):
            raise SyntaxError(f"Function {name} is not callable")
        return func_callable(*func_args)
    
    # Evaluate user-defined const function
    from runtime import run_scope
    import runtime
    
    # Set up function arguments in vars
    func_arg_names = func.get('args', [])
    if isinstance(func_arg_names, list):
        for (arg_name, _), arg_value in zip(func_arg_names, func_args):
            if isinstance(arg_name, str):
                vars[arg_name] = {
                    "type": get_type(arg_value),
                    "value": arg_value
                }
    
    # Execute function body
    runtime.vars = vars
    runtime.runtime = False
    
    func_body = func.get('func')
    if not isinstance(func_body, list):
        raise SyntaxError(f"Function {name} has invalid body")
    
    return run_scope(cast(AstType, func_body))

def parse_func_call(stream: InputStream, name: str) -> dict:
    """Parse a function call and optionally evaluate it at compile time."""
    # Save line before parsing
    call_line = stream.line
    
    if name not in funcs:
        raise SyntaxError(stream.format_error(f'Function "{name}" is not defined.'))

    # Parse arguments
    args = parse_args(stream, check_comma=False)
    arg_values = [arg_name for arg_name, _ in args]
    arg_values = list(map(parse_literal, arg_values))

    func = funcs[name]

    # Type-cast arguments to match function signature
    arg_values = cast_args(arg_values, func)

    # Try to evaluate at parse time if possible
    if _can_eval_at_parse_time(func, arg_values):
        value = _eval_func_at_parse_time(name, func, arg_values)
        node = make_node(stream,
            type=get_type(value),
            value=value
        )
        node['line'] = call_line
        return node

    # Return runtime function call node
    node = make_node(stream,
        type="call",
        name=name,
        args=arg_values,
        return_type=str(func.get('return_type', 'none'))
    )
    node['line'] = call_line
    return node

def _try_unroll_for_loop(loop_node: dict, max_iterations: int = 10) -> dict | None:
    """Try to unroll a for loop if bounds are constant and iteration count is small.
    Returns a scope node containing unrolled statements, or None if can't unroll."""
    
    # Extract loop components
    var_name = loop_node.get('var')
    start_node = loop_node.get('start')
    end_node = loop_node.get('end')
    step_node = loop_node.get('step', 1)
    scope = loop_node.get('scope', [])

    # Try to evaluate bounds as constants
    start_val = _eval_const_node(start_node)
    end_val = _eval_const_node(end_node)
    step_val = _eval_const_node(step_node)

    if start_val is None or end_val is None or step_val is None:
        return None  # Can't evaluate bounds

    # Check if iteration count is reasonable
    if step_val == 0:
        return None  # Infinite loop

    iterations = abs((end_val - start_val) // step_val)
    if iterations <= 0 or iterations > max_iterations:
        return None  # Too many iterations or invalid range

    # Unroll the loop into a sequence of statements
    unrolled_stmts = []

    for i in range(start_val, end_val, step_val):
        # Add loop variable assignment
        var_stmt = {
            "type": "var",
            "name": var_name,
            "value_type": "int",
            "value": i,
            "mods": []
        }
        unrolled_stmts.append(var_stmt)

        # Add each statement from the loop body
        # (they can reference the loop variable)
        unrolled_stmts.extend(iter(scope))
    # Return a special "unrolled" marker node that will be flattened into the parent scope
    return {
        "type": "unrolled_loop",
        "statements": unrolled_stmts
    }

def _eval_const_node(node: Any) -> Any:
    """Evaluate a node to a constant value if possible."""
    if node is None:
        return None
    if not isinstance(node, dict):
        return node

    # Direct value
    if 'value' in node and 'left' not in node and 'op' not in node:
        return node['value']

    # Simple operations
    if 'left' in node and 'op' in node and 'right' in node:
        left = _eval_const_node(node['left'])
        right = _eval_const_node(node['right'])

        if left is not None and right is not None:
            op = node['op']
            try:
                if op == 'Add':
                    return left + right
                elif op == 'Sub':
                    return left - right
                elif op == 'Mult':
                    return left * right
                elif op == 'Div':
                    return left // right if isinstance(left, int) else left / right
            except:
                return None

    return None

def parse_switch_body(stream:InputStream, level:int) -> AstType:
    """Parse statements in a switch case/default body until we hit case/default/}"""
    body = []
    while True:
        stream.strip()
        
        # Peek ahead to see if we're at the end of this case body
        next_word = stream.peek_word()
        # Check if next_word STARTS with case or default (since peek_word includes :)
        if next_word.startswith('case') or next_word.startswith('default'):
            break
        if stream.peek(1) == '}':
            break
        
        # Check if there's any text left
        if not stream.text:
            break
        
        stmt = parse_any(stream, level)
        if stmt is not None and stmt is not SkipNode:
            body.append(stmt)
    
    return body

def parse_any(stream:InputStream, level:int=0) -> dict[str, Any] | None | type[SkipNode]:
    global loop_depth
    stream.strip()

    # Either a variable or a function def
    if level == 0:
        # Save line after stripping, before consuming anything
        decl_line = stream.line
        # Check for "from <module> py_import <name>" statement
        if stream.peek_word() == 'from':
            stream.consume('from')
            stream.strip()

            # Get module name
            module_name = stream.consume_word()
            stream.strip()

            # Expect py_import keyword
            if stream.peek_word() != 'py_import':
                raise SyntaxError(stream.format_error(f'Expected "py_import" after "from {module_name}"'))
            stream.consume('py_import')
            stream.strip()

            # Get the specific name to import
            import_name = stream.consume_word()
            stream.strip()

            # Optional: check for 'as' alias
            alias = None
            if stream.peek_word() == 'as':
                stream.consume('as')
                stream.strip()
                alias = stream.consume_word()

            node = make_node(stream,
                type='py_import',
                module=module_name,
                name=import_name,
                alias=alias
            )
            node['line'] = decl_line
            return node

        # Check for "py_import <module>" or "py_import <module> as <alias>" statement
        if stream.peek_word() == 'py_import':
            stream.consume('py_import')
            stream.strip()

            # Get module name
            module_name = stream.consume_word()
            stream.strip()

            # Check for 'as' alias
            alias = None
            if stream.peek_word() == 'as':
                stream.consume('as')
                stream.strip()
                alias = stream.consume_word()

            node = make_node(stream,
                type='py_import',
                module=module_name,
                alias=alias
            )
            node['line'] = decl_line
            return node

        # Check for struct definition first
        if stream.peek_word() == 'struct':
            stream.consume('struct')
            stream.strip()

            # Get struct name
            struct_name = stream.consume_word()

            # Expect opening brace
            stream.strip()
            if not stream.consume('{'):
                raise SyntaxError(stream.format_error('Expected "{" after struct name'))

            # Parse struct fields
            fields = []
            while True:
                stream.strip()

                # Check for closing brace
                if stream.peek(1) == '}':
                    stream.consume('}')
                    break

                # Parse field type and name
                field_type = stream.consume_word()
                if field_type not in types and field_type not in vars:
                    # It might be another struct type - that's ok
                    pass

                stream.strip()
                field_name = stream.consume_word()

                fields.append({
                    'name': field_name,
                    'type': field_type
                })

            # Register the struct as a type
            if struct_name not in types:
                types.append(struct_name)

            # Store struct definition in vars so it can be used
            vars[struct_name] = {
                'type': 'struct_def',
                'fields': fields
            }

            node = make_node(stream,
                type='struct_def',
                name=struct_name,
                fields=fields
            )
            node['line'] = decl_line
            return node

        # Get type and name
        type = stream.consume_word()

        mods = []
        if type in modifiers:
            mods.append(type)
            type = stream.consume_word()

        name = stream.consume_word()

        if not (type and name):
            # Check if this is a function with missing name: "void () {"
            if type and not name and stream.peek(1) == '(':
                raise SyntaxError('Expected function name')
            return

        # Is func
        if stream.peek(1) == '(':
            node = parse_func(stream, name, type, mods)
            if node is not SkipNode and isinstance(node, dict):
                node['line'] = decl_line
            return node

        # Is var
        elif stream.peek(1) == '=':
            node = parse_var(stream, type, name, mods)
            if node is not SkipNode and isinstance(node, dict):
                node['line'] = decl_line
            return node

        # Augmented assignment with type - this is an error
        elif stream.peek_char(2) in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='] or stream.peek_char(3) in ['<<=', '>>=']:
            # Strip to get to the operator
            stream.strip()
            aug_op = stream.peek(3) if stream.peek(3) in ['<<=', '>>='] else stream.peek(2)
            raise SyntaxError(stream.format_error(
                f'Cannot use augmented assignment operator "{aug_op}" with type declaration. '
                f'Either declare the variable first with "{type} {name} = ...", or if it already exists, '
                f'use "{name} {aug_op} ..." without the type.'
            ))

        elif type == '//':
            stream.consume_until('\n')
            return parse_any(stream, level)

        else:
            raise SyntaxError(f'Invalid syntax: {stream.orig_line(stream.line-1)}')

    else:
        # Save line before consuming the first word
        stmt_line = stream.line
        word = stream.consume_word()

        # Ignore if empty (comment or blank line) - consume_word() already advanced the stream
        if not word.strip():
            #import sys; print(f'DEBUG: Skipping empty line at {stmt_line}, remaining: {repr(stream.text[:50])}', file=sys.stderr)
            return None

        # Field assignment: obj.field = value (word is "obj.field")
        if '.' in word and stream.peek(1) == '=':
            parts = word.split('.', 1)
            if len(parts) == 2:
                target, field = parts
                stream.consume('=')
                stream.strip()
                value = stream.consume_until('\n').strip()
                node = make_node(stream,
                    type="field_assign",
                    target=target,
                    field=field,
                    value=parse_expr(value)
                )
                node['line'] = stmt_line
                return node

        # Func call
        if word in funcs and stream.peek_char(1) == '(':
            return parse_func_call(stream, word)

        # Handle expression statements like obj.method() or obj.attr.method()
        elif '.' in word and stream.peek_char(1) == '(':
            # This is a method call on an object - parse the full expression
            full_expr = word + stream.consume_until('\n').strip()
            parsed = parse_expr(full_expr)
            # If it's a call expression (has 'func' key), return it as a statement
            if isinstance(parsed, dict) and 'func' in parsed:
                return parsed
            # Otherwise, this might be an error
            raise SyntaxError(stream.format_error(f'Invalid expression statement'))

        elif stream.peek(1) == '[':
            stream.consume('[')
            index_expr = stream.consume_until(']')
            stream.consume(']')  # Consume the closing bracket
            stream.strip()
            if not stream.consume('='):
                raise SyntaxError(stream.format_error('Expected "=" after index'))
            value = stream.consume_until('\n').strip()
            node = make_node(stream,
                type="index_assign",
                target=word,
                index=parse_expr(index_expr),
                value=parse_expr(value)
            )
            node['line'] = stmt_line
            return node

        elif stream.peek_char(1) == '=':
            # Reassignment without type def
            return parse_var(stream, None, word, [])

        elif stream.peek_char(2) in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='] or stream.peek_char(3) in ['<<=', '>>=']:
            # Strip whitespace to position at the operator
            stream.strip()

            # Check for 3-character operators first
            aug_op = stream.peek(3) if stream.peek(3) in ['<<=', '>>='] else stream.peek(2)
            stream.consume(aug_op)
            stream.strip()

            # Read the value expression
            value_text = stream.consume_until('\n').strip()
            value_expr = parse_expr(value_text)

            # Map augmented operators to their binary equivalents
            op_map = {
                '+=': 'Add',
                '-=': 'Sub',
                '*=': 'Mult',
                '/=': 'Div',
                '%=': 'Mod',
                '&=': 'BitAnd',
                '|=': 'BitOr',
                '^=': 'BitXor',
                '<<=': 'LShift',
                '>>=': 'RShift'
            }

            # Convert to: name = name op value
            binary_expr = {
                'left': {'id': word},
                'op': op_map[aug_op],
                'right': value_expr
            }

            # Get the variable type if it exists
            var_type = None
            if word in vars:
                var_type = vars[word].get('type', 'any')
            else:
                raise SyntaxError(stream.format_error(f'"{word}" is not defined.'))

            # Update vars table
            vars[word] = {
                "type": var_type,
                "value": binary_expr,
                "mods": []
            }

            node = make_node(stream,
                type="var",
                name=word,
                value_type=var_type,
                value=binary_expr,
                mods=[]
            )
            node['line'] = stmt_line
            return node

        elif word in types:
            name = stream.consume_word()

            node = parse_var(stream, word, name)
            if node is not SkipNode and isinstance(node, dict):
                node['line'] = stmt_line
            return node

        elif word == 'if':
            # Save line before parsing
            if_line = stream.line
            
            args = parse_args(stream, check_comma=False)
            # Extract first argument value (ignore type)
            arg_value = args[0][0] if args else ""
            args = parse_expr(arg_value)
            scope = parse_scope(stream, level+1)

            node = make_node(stream,
                type="if",
                condition=args,
                scope=scope,
                elifs=[],
                **{"else": {}}
            )
            node['line'] = if_line

            # Check if there are any elifs or an else.
            while True:
                stream.strip()
                word = stream.peek_word()
                if word == 'elif':
                    stream.consume('elif')
                    args = parse_args(stream)
                    # Extract argument values (ignore types) and join them
                    arg_values = [arg_name for arg_name, _ in args]
                    args = parse_expr(''.join(arg_values))
                    scope = parse_scope(stream, level+1)
                    node['elifs'].append(
                        {
                            "type": "elif",
                            "condition": args,
                            "scope": scope
                        }
                    )

                elif word == 'else':
                    if node['else']:
                        raise SyntaxError('The "else" clause has already been defined here.')

                    stream.consume('else')
                    scope = parse_scope(stream, level+1)
                    node['else'] = scope

                else:
                    break

            return node

        elif word in {"elif", "else"}:
            raise SyntaxError(f'?{stream.line},{stream.char}:Unexpected "{word}": {stream.orig_line()}')

        elif word == 'switch':
            # Save line before parsing
            switch_line = stream.line
            
            args = parse_args(stream, check_comma=False)
            if len(args) != 1:
                raise SyntaxError(stream.format_error(f'switch requires exactly 1 argument, got {len(args)}'))

            # Parse the expression to switch on
            switch_expr = parse_expr(args[0][0])

            # Expect opening brace
            stream.strip()
            if not stream.consume('{'):
                raise SyntaxError(stream.format_error('Expected "{" after switch condition'))

            cases = []
            default_case = None

            # Parse cases
            while True:
                stream.strip()

                # Check for closing brace
                if stream.peek(1) == '}':
                    stream.consume('}')
                    break

                word = stream.peek_word()

                if word == 'case':
                    stream.consume('case')
                    stream.strip()

                    # Parse case values (can be multiple: case 1, 2, 3:)
                    case_values = []
                    while True:
                        # Read until : or ,
                        value_text = ''
                        depth = 0
                        while stream.text:
                            ch = stream.peek(1)
                            if ch in '{[(':
                                depth += 1
                            elif ch in '}])':
                                depth -= 1

                            if depth == 0 and ch in ',:':
                                break

                            value_text += ch
                            stream._advance(1)

                        value_text = value_text.strip()
                        if value_text:
                            case_values.append(parse_literal(value_text))

                        stream.strip()
                        if stream.peek(1) == ',':
                            stream.consume(',')
                            stream.strip()
                        elif stream.peek(1) == ':':
                            stream.consume(':')
                            break
                        else:
                            raise SyntaxError(stream.format_error('Expected ":" or "," in case statement'))

                    # Parse case body using custom parsing that stops at case/default/}
                    case_body = parse_switch_body(stream, level+1)

                    cases.append({
                        'values': case_values,
                        'body': case_body
                    })

                elif word.startswith('default'):
                    stream.consume('default')
                    stream.strip()
                    if not stream.consume(':'):
                        raise SyntaxError(stream.format_error('Expected ":" after default'))

                    # Parse default body using custom parsing that stops at case/default/}
                    default_case = parse_switch_body(stream, level+1)

                else:
                    raise SyntaxError(stream.format_error(f'Expected "case" or "default" in switch statement, got "{word}"'))

            node = make_node(stream,
                type='switch',
                expr=switch_expr,
                cases=cases,
                default=default_case
            )
            node['line'] = switch_line
            return node

        elif word == 'assert':
            # Save line before parsing
            assert_line = stream.line
            
            args = parse_args(stream, False)
            if len(args) < 1 or len(args) > 2:
                raise SyntaxError(f'assert requires 1 or 2 arguments, got {len(args)}')
            # Extract argument values (ignore types)
            condition = parse_expr(args[0][0])
            message = parse_expr(args[1][0]) if len(args) == 2 else None

            node = make_node(stream,
                type="assert",
                condition=condition,
                message=message
            )
            node['line'] = assert_line
            return node

        elif word == 'for':
            # Save line before parsing
            for_line = stream.line
            
            loop_depth += 1

            args = parse_args(stream)
            if len(args) == 0 or len(args) > 2:
                raise SyntaxError(f'Invalid syntax: {stream.orig_line()}. Expected 1 or 2 arguments but got {len(args)}')

            # Check if this is a range-based for loop: for (i in 0..10) or for (item in list)
            if len(args) == 1:
                arg_text = args[0][0]

                if ' in ' not in arg_text:
                    raise SyntaxError(stream.format_error('Invalid for loop syntax. Expected "for (var in iterable)" or "for (var, count)"'))
                parts = arg_text.split(' in ', 1)
                if len(parts) != 2:
                    raise SyntaxError(stream.format_error('Invalid for loop syntax'))

                varname = parts[0].strip()
                iterable_expr = parts[1].strip()

                # Check if it's a range expression (start..end) or (start..end..step)
                if '..' in iterable_expr:
                    range_parts = iterable_expr.split('..')
                    if len(range_parts) < 2 or len(range_parts) > 3:
                        raise SyntaxError(stream.format_error('Invalid range syntax'))

                    start_expr = range_parts[0].strip()
                    end_expr = range_parts[1].strip()
                    step_expr = range_parts[2].strip() if len(range_parts) == 3 else None

                    scope = parse_scope(stream, level+1)
                    
                    loop_depth -= 1
                    
                    result = make_node(stream,
                        type="for",
                        var=varname,
                        start=parse_expr(start_expr) if start_expr else 0,
                        end=parse_expr(end_expr),
                        scope=scope
                    )
                    result['line'] = for_line

                    # Add step if provided
                    if step_expr:
                        result["step"] = parse_expr(step_expr)

                    # Try to unroll loop if bounds are constant (with -O flag)
                    if '-O' in sys.argv or '--optimize' in sys.argv:
                        unrolled = _try_unroll_for_loop(result, max_iterations=10)
                        if unrolled is not None:
                            return unrolled

                    return result
                else:
                    # It's iterating over a list/iterable
                    scope = parse_scope(stream, level+1)
                    
                    loop_depth -= 1
                    
                    return {
                        "type": "for_in",
                        "var": varname,
                        "iterable": parse_literal(iterable_expr),
                        "scope": scope,
                        "line": for_line
                    }
            else:
                # Old syntax: for (var, count)
                varname = args[0][0]
                end = args[1][0]

                scope = parse_scope(stream, level+1)

                loop_depth -= 1

                return {
                    "type": "for",
                    "var": varname,
                    "start": 0,
                    "end": parse_expr(end),
                    "scope": scope,
                    "line": for_line
                }

        elif word == 'while':
            # Save line before parsing
            while_line = stream.line
            
            loop_depth += 1

            args = parse_args(stream, False)
            # Extract first argument value (ignore type)
            arg_value = args[0][0] if args else ""
            args = parse_expr(arg_value)
            scope = parse_scope(stream, level+1)

            loop_depth -= 1

            node = make_node(stream,
                type=word,
                condition=args,
                scope=scope
            )
            node['line'] = while_line
            return node

        elif word == 'break':
            # Save line before parsing
            break_line = stream.line
            
            if loop_depth == 0:
                raise SyntaxError(stream.format_error('"break" outside loop'))

            # Check if there's a number after break
            stream.strip()
            level_str = ""
            if stream.peek(1).isdigit():
                level_str = stream.consume_word()

            break_level = int(level_str) if level_str else 1

            if break_level > loop_depth:
                raise SyntaxError(stream.format_error(f'"break {break_level}" exceeds loop depth {loop_depth}'))

            node = make_node(stream,
                type="break",
                level=break_level
            )
            node['line'] = break_line
            return node

        elif word == 'continue':
            # Save line before parsing
            continue_line = stream.line
            
            if loop_depth == 0:
                raise SyntaxError(stream.format_error('"continue" outside loop'))

            # Check if there's a number after continue
            stream.strip()
            level_str = ""
            if stream.peek(1).isdigit():
                level_str = stream.consume_word()

            continue_level = int(level_str) if level_str else 1

            if continue_level > loop_depth:
                raise SyntaxError(stream.format_error(f'"continue {continue_level}" exceeds loop depth {loop_depth}'))

            node = make_node(stream,
                type="continue",
                level=continue_level
            )
            node['line'] = continue_line
            return node

        elif word == 'return':
            # Save line before parsing
            return_line = stream.line
            
            rest = stream.consume_until('\n')
            expr = parse_expr(rest)

            node = make_node(stream,
                type="return",
                value=expr
            )
            node['line'] = return_line
            return node

        elif stream.peek_char(1) == '}':
            return

        else:
            raise SyntaxError(stream.format_error(f'"{word}" is not defined.'))

def parse(text:str|InputStream, level:int=0, file:str='') -> AstType:
    global loop_depth, vars, types

    # Reset global state for top-level parse
    if level == 0:
        loop_depth = 0
        vars = {}

    if not isinstance(text, InputStream):
        # Remove comments but preserve line numbers by replacing comment content with spaces
        lines = text.split('\n')
        processed_lines = []
        for line in lines:
            comment_start = line.find('//')
            if comment_start != -1:
                # Keep text before comment, replace comment with spaces to preserve length
                before_comment = line[:comment_start]
                comment_part = line[comment_start:]
                processed_lines.append(before_comment + ' ' * len(comment_part))
            else:
                processed_lines.append(line)
        
        text = '\n'.join(processed_lines)  # Don't strip - preserve line numbers!
        stream = InputStream(text)
        stream.file_path = file
    else:
        stream = text
        # Comments are already removed at the top level, don't recreate stream

    try:
        ast:AstType = []

        while stream.text:
            # Strip whitespace before checking for scope end
            stream.strip()
            
            # If we hit a closing brace, we're done with this scope
            if stream.text.startswith('}'):
                break
                
            node = parse_any(stream, level)
            if node is None:
                # Empty line/comment, continue parsing
                continue

            if node is SkipNode:
                continue

            # After filtering None and SkipNode, node must be dict[str, Any]
            assert isinstance(node, dict), "Node should be a dict at this point"
            
            # Handle unrolled loops - flatten their statements into the parent scope
            if node.get('type') == 'unrolled_loop':
                ast.extend(node.get('statements', []))
            else:
                ast.append(node)

        return ast

    except SyntaxError as e:
        if level != 0:
            raise

        char = None
        error_text = str(e)
        
        # If error already has location prefix from format_error, extract just the message
        # Format is either "Line X:Y: message" or "file:X:Y: message"
        if ':' in error_text and '\n' not in error_text.split(':')[0]:
            # Split and look for the pattern
            first_line = error_text.split('\n')[0]
            # Try to find where the actual message starts (after "Line X:Y:" or "file:X:Y:")
            parts = first_line.split(': ', 1)
            if len(parts) == 2:
                error_text = parts[1]
        
        if error_text.startswith('?'):
            line_num, error_text = error_text.removeprefix('?').split(':',1)
            if ',' in line_num:
                line_num, char = line_num.split(',',1)
                char = int(char)

            line_num = int(line_num)
            if line_num < 0:
                line_num = stream.line + line_num
        else:
            line_num = stream.line

        line = stream.orig_line(line_num-1)

        if char is not None and char < 0:
            char = len(line)+char

        # Format the error message with location info
        location = f'{file}:{line_num}:{char or len(line)}' if file else f'Line {line_num}:{char or len(line)}'
        error_msg = f'Syntax Error\n  File "{file}" line {line_num} in {current_func}\n      {line}\n      {' '*(char or len(line)) + '^'}\n    {location}: {error_text}'
        
        # Always raise the exception so it can be caught by test framework or CLI
        raise SyntaxError(error_msg)

debug = '-d' in sys.argv or '--debug' in sys.argv

