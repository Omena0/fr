import os
import sys
import subprocess
import tempfile
from io import StringIO
from concurrent.futures import ProcessPoolExecutor, as_completed

debug = '-d' in sys.argv

# Enable debug mode BEFORE importing parser
# This makes parse() raise exceptions instead of calling exit()
if not debug:
    sys.argv.append('-d')

from parser import parse
from runtime import run
from compiler import compile_ast_to_bytecode

def run_python_runtime(ast):
    """Run AST with Python runtime and capture output"""
    old_stdout = sys.stdout
    string_io = StringIO()
    sys.stdout = string_io
    try:
        run(ast)
        output = string_io.getvalue().strip()
        return output, None
    except Exception as e:
        return None, str(e)
    finally:
        sys.stdout = old_stdout

def run_c_runtime(ast):
    """Run AST with C VM runtime and capture output"""
    bc_file = None
    try:
        # Compile AST to bytecode
        bytecode = compile_ast_to_bytecode(ast)
        
        # Write bytecode to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
            bc_file = f.name
            f.write(bytecode)
        
        # Run with C VM
        vm_path = os.path.join(os.path.dirname(__file__), '../runtime/vm')
        result = subprocess.run(
            [vm_path, bc_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Clean up
        os.unlink(bc_file)
        bc_file = None
        
        if result.returncode != 0:
            # VM error occurred
            error_msg = result.stderr.strip() if result.stderr else f"VM exited with code {result.returncode}"
            return None, error_msg
        
        output = result.stdout.strip()
        return output, None
        
    except subprocess.TimeoutExpired:
        if bc_file:
            os.unlink(bc_file)
        return None, "Timeout: Test took too long"
    except Exception as e:
        if bc_file:
            try:
                os.unlink(bc_file)
            except:
                pass
        return None, str(e)

cases = {}

for file in os.listdir('cases'):
    # Only process .fr files, skip .example files
    if not file.endswith('.fr') or file.endswith('.fr.example'):
        continue
    content = open(f'cases/{file}').read()
    cases[file] = content.split('\n',1)

def extract_message(s):
    """Extract error message from error string"""
    if s.startswith('?'):
        parts = s.removeprefix('?').split(':', 1)
        if len(parts) == 2:
            return parts[1]
    
    # Handle new multi-line format: last line has "Location: message"
    if 'Syntax Error' in s and '\n' in s:
        lines = s.strip().split('\n')
        # Last line should be "    Location: message"
        last_line = lines[-1].strip()
        if ': ' in last_line:
            # Extract message after the location prefix
            parts = last_line.split(': ', 1)
            if len(parts) == 2:
                return parts[1].strip()
    
    # Old format: "Line X:Y: message"
    if s.startswith('Line '):
        lines = s.split('\n')
        first_line = lines[0]
        parts = first_line.split(':', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    
    # Handle "Runtime error:" prefix
    if 'Runtime error:' in s:
        return s.split('Runtime error:', 1)[1].strip()
    
    return s

def run_single_test(file, expect, case):
    """Run a single test case on both runtimes"""
    # Clear global state between tests
    import parser
    parser.vars.clear()
    parser.current_func = '<module>'
    parser.loop_depth = 0
    
    is_output_test = expect.startswith('!')
    if is_output_test:
        expect = expect[1:].strip()
        expect = expect.replace('\\n', '\n')
    else:
        expect = expect.rstrip('.')

    case = '\n' + case
    
    result = {
        'file': file,
        'expect': expect,
        'is_output_test': is_output_test,
        'py_passed': False,
        'vm_passed': False,
        'mismatch': False,
        'py_error': None,
        'vm_error': None,
        'py_output': None,
        'vm_output': None
    }

    try:
        ast = parse(case)
    except Exception as e:
        # Parse error
        e_str = str(e)
        e_normalized = extract_message(e_str).rstrip('.')
        expect_normalized = extract_message(expect).rstrip('.')

        if e_normalized == expect_normalized:
            result['py_passed'] = True
            result['vm_passed'] = True
        else:
            result['py_error'] = f'Parse error "{e_normalized}" != expected "{expect_normalized}"'
            result['vm_error'] = result['py_error']
        return result

    # AST parsed successfully
    should_run = is_output_test or (expect.lower() != 'none')
    
    if not should_run:
        if expect.lower() == 'none':
            result['py_passed'] = True
            result['vm_passed'] = True
        return result

    # Run on Python runtime
    py_output, py_error = run_python_runtime(ast)
    result['py_output'] = py_output
    result['py_error'] = py_error
    
    # Run on C VM runtime
    vm_output, vm_error = run_c_runtime(ast)
    result['vm_output'] = vm_output
    result['vm_error'] = vm_error

    # Check Python runtime result
    if is_output_test:
        result['py_passed'] = (py_output == expect)
        if not result['py_passed']:
            result['py_error'] = f'Output "{py_output}" != expected "{expect}"'
    else:
        if py_error:
            py_msg = extract_message(py_error).rstrip('.')
            exp_msg = extract_message(expect).rstrip('.')
            result['py_passed'] = (py_msg == exp_msg)
            if not result['py_passed']:
                result['py_error'] = f'Error "{py_msg}" != expected "{exp_msg}"'
        else:
            result['py_error'] = f'No error but expected: {expect}'

    # Check C VM runtime result
    if is_output_test:
        result['vm_passed'] = (vm_output == expect)
        if not result['vm_passed']:
            result['vm_error'] = f'Output "{vm_output}" != expected "{expect}"'
    else:
        if vm_error:
            vm_msg = extract_message(vm_error).rstrip('.')
            exp_msg = extract_message(expect).rstrip('.')
            result['vm_passed'] = (vm_msg == exp_msg)
            if not result['vm_passed']:
                result['vm_error'] = f'Error "{vm_msg}" != expected "{exp_msg}"'
        else:
            result['vm_error'] = f'No error but expected: {expect}'

    # Check for runtime mismatch
    if is_output_test and py_output != vm_output and py_error is None and vm_error is None:
        result['mismatch'] = True

    return result

passed = 0
failed = 0
python_passed = 0
python_failed = 0
vm_passed = 0
vm_failed = 0
mismatch_count = 0

# Run tests sequentially to avoid any race conditions
print(f"Running {len(cases)} tests on both runtimes...")
results = []

for file, (expect, case) in cases.items():
    result = run_single_test(file, expect.removeprefix('//').strip(), case)
    results.append(result)

for result in results:
    if result['py_passed']:
        python_passed += 1
    else:
        python_failed += 1
        print(f'❌ {result["file"]} [Python]: {result["py_error"]}')
    
    if result['vm_passed']:
        vm_passed += 1
    else:
        vm_failed += 1
        print(f'❌ {result["file"]} [C VM]: {result["vm_error"]}')
    
    if result['mismatch']:
        mismatch_count += 1
        print(f'⚠️  {result["file"]}: Runtime mismatch! Python: "{result["py_output"]}" vs C VM: "{result["vm_output"]}"')

total_tests = python_passed + python_failed

print(f'\n{"="*60}')
print(f'Test Results:')
print(f'{"="*60}')
print(f'Python Runtime: {python_passed}/{total_tests} passed')
print(f'C VM Runtime:   {vm_passed}/{total_tests} passed')
if mismatch_count > 0:
    print(f'⚠️  Runtime Mismatches: {mismatch_count}')
print(f'{"="*60}')

if python_failed == 0 and vm_failed == 0 and mismatch_count == 0:
    print('✅ All tests passed on BOTH runtimes!')
    exit(0)
else:
    if python_failed > 0:
        print(f'❌ Python runtime has {python_failed} failure(s)')
    if vm_failed > 0:
        print(f'❌ C VM runtime has {vm_failed} failure(s)')
    if mismatch_count > 0:
        print(f'⚠️  {mismatch_count} test(s) have different outputs between runtimes')
    exit(1)
