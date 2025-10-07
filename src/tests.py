#!/usr/bin/env python3
"""
Isolated test runner - runs each test in a separate subprocess for complete isolation.
This prevents any state pollution between tests.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
import glob
import sys
import os

def run_test_isolated(test_file, test_content):
    """Run a single test in complete isolation via subprocess"""
    repo_root = Path(__file__).parent.parent
    helper_script = repo_root / 'src' / 'run_single_test.py'

    # Run the helper script with test content via stdin
    result = subprocess.run(
        [sys.executable, str(helper_script)],
        input=test_content,
        capture_output=True,
        text=True,
        timeout=5,  # Reduced from 10 to 5 seconds
        cwd=str(repo_root)
    )

    # Parse results
    py_output = vm_output = expect = None
    py_error = vm_error = None
    is_output_test = False

    for line in result.stdout.strip().split('\n'):
        if line.startswith('PY_OUTPUT:'):
            py_output = line[10:]
        elif line.startswith('PY_ERROR:'):
            py_error = line[9:]
        elif line.startswith('VM_OUTPUT:'):
            vm_output = line[10:]
        elif line.startswith('VM_ERROR:'):
            vm_error = line[9:]
        elif line.startswith('EXPECT:'):
            expect = line[7:]
        elif line.startswith('IS_OUTPUT:'):
            is_output_test = line[10:] == 'True'
        elif line.startswith('ERROR:'):
            # Test script error
            return {
                'file': test_file,
                'py_passed': False,
                'vm_passed': False,
                'py_error': line[6:],
                'vm_error': line[6:],
                'mismatch': False
            }

    # Define helper functions for error message comparison
    def extract_msg(text):
        """Extract error message and normalize line numbers for comparison"""
        if not text:
            return ''

        # If message starts with ?N: or ?N,M: it's a normalized error with line numbers
        # Replace actual line numbers with ? for comparison
        if text.startswith('?'):
            # Format is ?N:Message or ?N,M:Message
            # Extract just the message part for comparison
            parts = text.split(':', 1)
            if len(parts) > 1:
                # Keep the ? prefix but use for comparison
                return text

        # For other formats, extract the message
        if ':' in text:
            parts = text.split(':', 2)
            if len(parts) >= 3:
                return parts[2].strip().rstrip('.')
        return text.rstrip('.')

    def normalize_line_numbers(msg1, msg2):
        """Check if two error messages match, ignoring line/column numbers after ?"""
        # If expected (msg2) doesn't have line numbers, strip them from actual (msg1)
        if not msg2.startswith('?') and msg1.startswith('?'):
            # Extract just the message part from msg1
            idx = msg1.find(':', 1)
            if idx > 0:
                msg1 = msg1[idx+1:]  # Remove ?N: or ?N,M: prefix

        # If expected has line numbers but actual doesn't, that's OK too
        if msg2.startswith('?') and not msg1.startswith('?'):
            idx = msg2.find(':', 1)
            if idx > 0:
                msg2 = msg2[idx+1:]

        # Both should be in format ?N:Message or ?N,M:Message
        # Or one/both might not have line numbers
        if not msg1.startswith('?') and not msg2.startswith('?'):
            # Neither has line numbers, direct comparison
            # Remove trailing periods for comparison
            return msg1.rstrip('.') == msg2.rstrip('.')

        # Extract message parts after the line number
        def get_message_part(text):
            if text.startswith('?'):
                # Find the : that separates line info from message
                idx = text.find(':', 1)  # Skip first ? when searching
                if idx > 0:
                    return text[idx+1:].rstrip('.')  # Return everything after the :, strip periods
            return text.rstrip('.')

        return get_message_part(msg1) == get_message_part(msg2)

    # Determine if tests passed
    if is_output_test:
        # For output tests, compare output directly
        # Use normalized comparison for error-like output (with line numbers)
        py_passed = normalize_line_numbers(py_output or '', expect)
        vm_passed = normalize_line_numbers(vm_output or '', expect)

        return {
            'file': test_file,
            'py_passed': py_passed,
            'vm_passed': vm_passed,
            'py_output': py_output,
            'vm_output': vm_output,
            'py_error': None if py_passed else f'Output "{py_output}" != expected "{expect}"',
            'vm_error': None if vm_passed else f'Output "{vm_output}" != expected "{expect}"',
            'mismatch': py_passed and not vm_passed and py_output != vm_output
        }
    else:
        # Error test or "none" test
        # Check if this is a "none" test (parsing succeeded)
        if py_output == 'none' and vm_output == 'none' and expect.lower() == 'none': # type: ignore
            py_passed = True
            vm_passed = True
        else:
            py_msg = extract_msg(py_error) if py_error else extract_msg(py_output) if py_output else ''
            vm_msg = extract_msg(vm_error) if vm_error else extract_msg(vm_output) if vm_output else ''
            exp_msg = extract_msg(expect)

            # Use normalized comparison for line numbers
            py_passed = normalize_line_numbers(py_msg, exp_msg)
            vm_passed = normalize_line_numbers(vm_msg, exp_msg)

        return {
            'file': test_file,
            'py_passed': py_passed,
            'vm_passed': vm_passed,
            'py_error': None if py_passed else f'Error "{py_msg if "py_msg" in locals() else py_output}" != expected "{expect}"', # type: ignore
            'vm_error': None if vm_passed else f'Error "{vm_msg if "vm_msg" in locals() else vm_output}" != expected "{expect}"', # type: ignore
            'mismatch': False
        }

def run_single_test_wrapper(args):
    """Wrapper for parallel execution"""
    test_path, _repo_root = args
    # Keep relative path for better readability
    test_file = test_path.replace('cases/', '')
    try:
        with open(test_path, 'r') as f:
            content = f.read()
        result = run_test_isolated(test_file, content)
        result['file'] = test_file  # Use relative path
        return result
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'py_passed': False,
            'vm_passed': False,
            'py_error': 'Test timeout',
            'vm_error': 'Test timeout',
            'mismatch': False
        }
    except Exception as e:
        return {
            'file': test_file,
            'py_passed': False,
            'vm_passed': False,
            'py_error': f'Test runner error: {e}',
            'vm_error': f'Test runner error: {e}',
            'mismatch': False
        }

def main():
    # Change to repository root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)

    # Load all test files recursively from cases/ and subdirectories
    test_files = sorted(glob.glob('cases/**/*.fr', recursive=True))

    if not test_files:
        print("Error: No test files found in cases/")
        return 1

    print(f"Running {len(test_files)} tests...")
    print()

    # Run tests in parallel
    max_workers = min(os.cpu_count() or 4, len(test_files))
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tests
        future_to_test = {
            executor.submit(run_single_test_wrapper, (test_path, str(repo_root))): test_path
            for test_path in test_files
        }

        for completed, future in enumerate(as_completed(future_to_test), start=1):
            result = future.result()
            results.append(result)
            print(f'[{completed}/{len(test_files)}]                 \r', end='', flush=True)

    print()  # New line after progress indicator

    # Print failures
    python_passed = 0
    vm_passed = 0
    mismatch_count = 0

    for result in results:
        if result['py_passed']:
            python_passed += 1
        elif result['py_error']:
            print(f"❌ {result['file']} [Python]: {result['py_error']}")

        if result['vm_passed']:
            vm_passed += 1
        elif result['vm_error']:
            print(f"❌ {result['file']} [C VM]: {result['vm_error']}")

        if result.get('mismatch'):
            mismatch_count += 1
            print(f"⚠️  {result['file']}: Runtime mismatch! "
                  f"Python: \"{result.get('py_output')}\" vs C VM: \"{result.get('vm_output')}\"")

    # Print summary
    total = len(results)
    print()
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"Python Runtime: {python_passed}/{total} passed")
    print(f"C VM Runtime:   {vm_passed}/{total} passed")
    if mismatch_count > 0:
        print(f"⚠️  Runtime Mismatches: {mismatch_count}")
    print("=" * 60)

    if python_passed == total and vm_passed == total:
        print("✅ All tests passed on BOTH runtimes!")
        return 0
    else:
        if python_passed < total:
            print(f"❌ Python runtime has {total - python_passed} failure(s)")
        if vm_passed < total:
            print(f"❌ C VM runtime has {total - vm_passed} failure(s)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
