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
    """Extract just the error message from a full error string"""
    if not error_text:
        return ''
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
    code = '\n' + lines[1]
    
    # Extract expectation
    expect = expect_line.replace('//', '').strip()
    is_output_test = expect.startswith('!')
    if is_output_test:
        expect = expect[1:].strip().replace('\\n', '\n')
    else:
        expect = expect.rstrip('.')
    
    # Parse the code
    try:
        ast = parse(code)
    except Exception as e:
        err_msg = extract_error_message(str(e))
        
        if is_output_test:
            print(f"PY_ERROR:{err_msg}")
            print(f"VM_ERROR:{err_msg}")
        else:
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
        
        if result.returncode != 0:
            vm_error = result.stderr.strip() if result.stderr else f"VM exited with code {result.returncode}"
            vm_output = None
        else:
            vm_output = result.stdout.strip()
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
        print(f"PY_OUTPUT:{py_output}")
    
    if vm_error:
        print(f"VM_ERROR:{vm_error}")
    else:
        print(f"VM_OUTPUT:{vm_output}")
    
    print(f"EXPECT:{expect}")
    print(f"IS_OUTPUT:{is_output_test}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
