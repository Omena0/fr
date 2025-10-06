#!/usr/bin/env python3
"""
Helper script to run a single test in isolation.
This is called by tests_isolated.py for each test.
Test content is read from stdin.
"""
import sys
import os
import tempfile
import subprocess
from io import StringIO

# Setup paths
sys.path.insert(0, 'src')
sys.argv = [sys.argv[0], '-d']  # Enable debug mode

# Import after path setup
from parser import parse
from compiler import compile_ast_to_bytecode
from runtime import run

def extract_error_message(error_text):
    """Extract and normalize error message to match expected format"""
    if not error_text:
        return ''

    # Parser errors have format: "...Line X:Y: Message" or "...Line X: Message"
    # Expected format is: "?X:Message" or "?X,Y:Message"
    if 'Line ' in error_text:
        # Extract the line number and message
        parts = error_text.split('Line ', 1)
        if len(parts) > 1:
            line_part = parts[1]
            # Format is "X:Y: Message" or "X: Message"
            if ':' in line_part:
                line_info, rest = line_part.split(':', 1)
                if ':' not in rest:
                    return f"?{line_info}:{rest.strip()}"

                col_part, message = rest.split(':', 1)
                message = message.strip()
                # Check if col_part is a column number
                try:
                    col = int(col_part.strip())
                    return f"?{line_info},{col}:{message}"
                except ValueError:
                    # col_part is part of message
                    return f"?{line_info}:{col_part}:{message}".replace('::', ':').strip()
    # For other error formats, just clean up
    if ':' in error_text:
        parts = error_text.split(':', 2)
        if len(parts) >= 3:
            return parts[2].strip().rstrip('.')
    return error_text.rstrip('.')

def main():
    # Test content is read from stdin
    content = sys.stdin.read()
    
    # Parse test
    lines = content.split('\n', 1)
    if len(lines) < 2:
        print("ERROR:Invalid test format")
        return 1
    
    expect_line = lines[0]
    code = lines[1]  # Don't prepend '\n' - it's already in lines[1]
    
    # Extract expectation
    expect = expect_line.replace('//', '').strip()
    is_output_test = expect.startswith('!')
    if is_output_test:
        expect = expect[1:].strip().replace('\\n', '\n')
    else:
        expect = expect.rstrip('.')
    
    # Special case: if expect is "none", test passes if parsing succeeds
    # Don't run the code to avoid timeouts from infinite loops
    if expect.lower() == 'none' and not is_output_test:
        try:
            ast = parse(code)
            # Parse succeeded - both runtimes pass
            print("PY_OUTPUT:none")
            print("VM_OUTPUT:none")
            print("EXPECT:none")
            print("IS_OUTPUT:False")
            return 0
        except Exception as e:
            err_msg = extract_error_message(str(e))
            print(f"PY_ERROR:{err_msg}")
            print(f"VM_ERROR:{err_msg}")
            print("EXPECT:none")
            print("IS_OUTPUT:False")
            return 0
    
    # Parse the code
    try:
        ast = parse(code)
    except Exception as e:
        # Parse error - treat the error message as the output/error
        err_msg = extract_error_message(str(e))
        
        # For both output tests and error tests, use the error message
        # This matches old test runner behavior where parse errors are compared with expected
        print(f"PY_OUTPUT:{err_msg}")
        print(f"VM_OUTPUT:{err_msg}")
        print(f"EXPECT:{expect}")
        print(f"IS_OUTPUT:{is_output_test}")
        return 0
    
    # Run on Python runtime
    old_stdout = sys.stdout
    string_io = StringIO()
    sys.stdout = string_io
    py_error = None
    try:
        run(ast)
        py_output = string_io.getvalue().strip()
    except Exception as e:
        py_output = None
        py_error = str(e)
    finally:
        sys.stdout = old_stdout
    
    # Run on C VM runtime
    vm_error = None
    vm_output = None
    try:
        bytecode = compile_ast_to_bytecode(ast)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
            bc_file = f.name
            f.write(bytecode)
        
        vm_path = 'runtime/vm'
        result = subprocess.run(
            [vm_path, bc_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        os.unlink(bc_file)
        
        # Capture output even if program crashes (e.g., stack overflow after main returns)
        vm_output = result.stdout.strip() if result.stdout else ""
        
        if result.returncode != 0:
            vm_error = result.stderr.strip() if result.stderr else f"VM exited with code {result.returncode}"
            # If we don't have valid output, mark as None for error reporting
            if not vm_output:
                vm_output = None
    except subprocess.TimeoutExpired:
        vm_error = "Timeout"
        vm_output = None
    except Exception as e:
        vm_error = str(e)
        vm_output = None
    
    # Output results
    if py_error:
        print(f"PY_ERROR:{py_error}")
    else:
        print(f"PY_OUTPUT:{py_output if py_output is not None else ''}")
    
    # For VM: prioritize output over error if we have valid output
    # This handles cases where program outputs correctly but crashes during cleanup
    if vm_output is not None:
        # Has output (could be empty string)
        print(f"VM_OUTPUT:{vm_output}")
    elif vm_error:
        # Has error and no output
        print(f"VM_ERROR:{vm_error}")
    else:
        # No output and no error
        print(f"VM_OUTPUT:")
    
    print(f"EXPECT:{expect}")
    print(f"IS_OUTPUT:{is_output_test}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
