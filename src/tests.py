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
import json

def load_config():
    """Load test configuration from cases/config.json"""
    config_path = Path('cases/config.json')
    if not config_path.exists():
        # Return default config if file doesn't exist
        return {
            'native': {'enabled': True, 'timeout': 10, 'ignore': [], 'skip_mismatch': [], 'allow_timeout_failures': False},
            'c': {'enabled': True, 'timeout': 10, 'ignore': [], 'skip_mismatch': [], 'allow_timeout_failures': False},
            'py': {'enabled': True, 'timeout': 10, 'ignore': [], 'skip_mismatch': [], 'allow_timeout_failures': False},
        }

    with open(config_path) as f:
        config = json.load(f)

    # Ensure all required fields exist with defaults
    for runtime in ['native', 'c', 'py']:
        if runtime not in config:
            config[runtime] = {}
        if 'enabled' not in config[runtime]:
            config[runtime]['enabled'] = True
        if 'timeout' not in config[runtime]:
            config[runtime]['timeout'] = 10
        if 'ignore' not in config[runtime]:
            config[runtime]['ignore'] = []
        if 'skip_mismatch' not in config[runtime]:
            config[runtime]['skip_mismatch'] = []
        if 'allow_timeout_failures' not in config[runtime]:
            config[runtime]['allow_timeout_failures'] = False

    return config

def get_test_category(test_path):
    """Extract test category from test path (first folder name under cases/)

    Examples:
    - cases/control_flow/if_else.fr -> control_flow
    - cases/data_structures/struct_basic.fr -> data_structures
    - cases/assertions/assert_pass.fr -> assertions
    """
    parts = test_path.replace('cases/', '').split('/')
    return parts[0] if len(parts) > 1 else 'root'

def should_skip_test(test_path, runtime, config):
    """Check if a test should be skipped for a given runtime based on config

    Returns: True if test should be skipped, False otherwise
    """
    runtime_config = config.get(runtime, {})

    # Check if runtime is disabled
    if not runtime_config.get('enabled', True):
        return True

    # Check if test category or specific test file is in ignore list
    category = get_test_category(test_path)
    ignore_list = runtime_config.get('ignore', [])
    
    # Check both category and full test path
    return bool(category in ignore_list or test_path in ignore_list)

def run_test_isolated(test_file, test_path, test_content, config=None):
    """Run a single test in complete isolation via subprocess
    
    Args:
        test_file: Relative path without 'cases/' prefix (for display and config matching)
        test_path: Full path with 'cases/' prefix (for import resolution)
        test_content: Test file content
        config: Test configuration
    """
    repo_root = Path(__file__).parent.parent
    helper_script = repo_root / 'src' / 'run_single_test.py'

    if config is None:
        config = load_config()

    # Calculate maximum timeout from all enabled runtimes
    max_timeout = 5
    for runtime in ['native', 'c', 'py']:
        if config.get(runtime, {}).get('enabled', True):
            runtime_timeout = config.get(runtime, {}).get('timeout', 10)
            max_timeout = max(max_timeout, runtime_timeout)

    # Determine which runtimes to skip for this test
    skip_py = should_skip_test(test_file, 'py', config)
    skip_c = should_skip_test(test_file, 'c', config)
    skip_native = should_skip_test(test_file, 'native', config)

    # Build arguments to pass to helper script - use full test_path for import resolution
    helper_args = [sys.executable, str(helper_script), test_path]
    if skip_py:
        helper_args.append('--skip-py')
    if skip_c:
        helper_args.append('--skip-c')
    if skip_native:
        helper_args.append('--skip-native')

    # Run the helper script with test content via stdin and filename as argument
    result = subprocess.run(
        helper_args,
        input=test_content,
        capture_output=True,
        text=True,
        timeout=max_timeout,
        cwd=str(repo_root)
    )

    # Parse results
    py_output = vm_output = native_output = expect = None
    py_error = vm_error = native_error = None
    is_output_test = False
    expect_alternatives = None
    py_skipped = vm_skipped = native_skipped = False

    for line in result.stdout.strip().split('\n'):
        if line.startswith('PY_OUTPUT:'):
            py_output = line[10:].replace('\\n', '\n').replace('\\\\', '\\')
        elif line.startswith('PY_ERROR:'):
            py_error = line[9:]
            if py_error == 'SKIPPED':
                py_skipped = True
        elif line.startswith('VM_OUTPUT:'):
            vm_output = line[10:].replace('\\n', '\n').replace('\\\\', '\\')
        elif line.startswith('VM_ERROR:'):
            vm_error = line[9:]
            if vm_error == 'SKIPPED':
                vm_skipped = True
        elif line.startswith('NATIVE_OUTPUT:'):
            native_output = line[14:].replace('\\n', '\n').replace('\\\\', '\\')
        elif line.startswith('NATIVE_ERROR:'):
            native_error = line[13:]
            if native_error == 'SKIPPED':
                native_skipped = True
        elif line.startswith('EXPECT:'):
            expect = line[7:].replace('\\n', '\n').replace('\\\\', '\\')
        elif line.startswith('EXPECT_ALTERNATIVES:'):
            expect_alternatives = [e.strip().replace('\\n', '\n').replace('\\\\', '\\') for e in line[20:].split('||')]
        elif line.startswith('IS_OUTPUT:'):
            is_output_test = line[10:] == 'True'
        elif line.startswith('ERROR:'):
            # Test script error
            return {
                'file': test_file,
                'py_passed': False,
                'vm_passed': False,
                'native_passed': False,
                'py_error': line[6:],
                'vm_error': line[6:],
                'native_error': line[6:],
                'mismatch': False
            }

    # If neither PY_OUTPUT nor PY_ERROR is present, Python runtime was skipped
    if py_output is None and py_error is None:
        py_skipped = True
    # If neither VM_OUTPUT nor VM_ERROR is present, C VM was skipped
    if vm_output is None and vm_error is None:
        vm_skipped = True
    # If neither NATIVE_OUTPUT nor NATIVE_ERROR is present, native was skipped
    if native_output is None and native_error is None:
        native_skipped = True

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

    # Helper to check if output matches any alternative
    def matches_any_alternative(output, alternatives):
        """Check if output matches any of the expected alternatives"""
        if not alternatives:
            return normalize_line_numbers(output or '', expect)
        return any(normalize_line_numbers(output or '', alt) for alt in alternatives)

    # Determine if tests passed
    if is_output_test:
        # For output tests, compare output directly
        # Use normalized comparison for error-like output (with line numbers)
        # Check against alternatives if provided
        if expect_alternatives:
            py_passed = not py_skipped and matches_any_alternative(py_output, expect_alternatives)
            vm_passed = not vm_skipped and matches_any_alternative(vm_output, expect_alternatives)
            native_passed = not native_skipped and matches_any_alternative(native_output, expect_alternatives)
        else:
            py_passed = not py_skipped and normalize_line_numbers(py_output or '', expect)
            vm_passed = not vm_skipped and normalize_line_numbers(vm_output or '', expect)
            native_passed = not native_skipped and normalize_line_numbers(native_output or '', expect)

        # Helper to escape newlines for error display
        def escape_for_display(text):
            return text.replace('\n', '\\n') if text else ""
        
        return {
            'file': test_file,
            'py_passed': py_passed,
            'vm_passed': vm_passed,
            'native_passed': native_passed,
            'py_output': py_output,
            'vm_output': vm_output,
            'native_output': native_output,
            'py_error': None if py_passed else f'Output "{escape_for_display(py_output)}" != expected "{escape_for_display(expect)}"',
            'vm_error': None if vm_passed else f'Output "{escape_for_display(vm_output)}" != expected "{escape_for_display(expect)}"',
            'native_error': None if native_passed else f'Output "{escape_for_display(native_output)}" != expected "{escape_for_display(expect)}"',
            'py_skipped': py_skipped,
            'vm_skipped': vm_skipped,
            'native_skipped': native_skipped,
            'mismatch': py_passed and not vm_passed and py_output != vm_output
        }
    else:
        # Error test or "none" test
        # Check if this is a "none" test (parsing succeeded)
        if py_output == 'none' and vm_output == 'none' and native_output == 'none' and expect.lower() == 'none': # type: ignore
            py_passed = True
            vm_passed = True
            native_passed = True
        else:
            py_msg = extract_msg(py_error) if py_error and py_error != 'SKIPPED' else extract_msg(py_output) if py_output else ''
            vm_msg = extract_msg(vm_error) if vm_error and vm_error != 'SKIPPED' else extract_msg(vm_output) if vm_output else ''
            native_msg = extract_msg(native_error) if native_error and native_error != 'SKIPPED' else extract_msg(native_output) if native_output else ''

            # Check against alternatives if provided
            if expect_alternatives:
                py_passed = not py_skipped and any(normalize_line_numbers(py_msg, extract_msg(alt)) for alt in expect_alternatives)
                vm_passed = not vm_skipped and any(normalize_line_numbers(vm_msg, extract_msg(alt)) for alt in expect_alternatives)
                native_passed = not native_skipped and any(normalize_line_numbers(native_msg, extract_msg(alt)) for alt in expect_alternatives)
            else:
                exp_msg = extract_msg(expect)
                # Use normalized comparison for line numbers
                py_passed = not py_skipped and normalize_line_numbers(py_msg, exp_msg)
                vm_passed = not vm_skipped and normalize_line_numbers(vm_msg, exp_msg)
                native_passed = not native_skipped and normalize_line_numbers(native_msg, exp_msg)
                native_passed = native_skipped or normalize_line_numbers(native_msg, exp_msg)

        return {
            'file': test_file,
            'py_passed': py_passed,
            'vm_passed': vm_passed,
            'native_passed': native_passed,
            'py_error': None if py_passed else f'Error "{py_msg if "py_msg" in locals() else py_output}" != expected "{expect}"', # type: ignore
            'vm_error': None if vm_passed else f'Error "{vm_msg if "vm_msg" in locals() else vm_output}" != expected "{expect}"', # type: ignore
            'native_error': None if native_passed else f'Error "{native_msg if "native_msg" in locals() else native_output}" != expected "{expect}"', # type: ignore
            'py_skipped': py_skipped,
            'vm_skipped': vm_skipped,
            'native_skipped': native_skipped,
            'mismatch': False
        }

def run_single_test_wrapper(args):
    """Wrapper for parallel execution"""
    test_path, _repo_root, config = args
    # Keep relative path for better readability
    test_file = test_path.replace('cases/', '')
    try:
        with open(test_path, 'r') as f:
            content = f.read()
        # Pass both test_file (for config) and test_path (for imports)
        result = run_test_isolated(test_file, test_path, content, config)
        result['file'] = test_file  # Use relative path for display
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

    # Load configuration
    config = load_config()

    # Load all test files recursively from cases/ and subdirectories
    test_files = sorted(glob.glob('cases/**/*.fr', recursive=True))

    if not test_files:
        print("Error: No test files found in cases/")
        return 1

    print(f"Running {len(test_files)} tests..")
    print()

    # Run tests in parallel
    max_workers = 18
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tests
        future_to_test = {
            executor.submit(run_single_test_wrapper, (test_path, str(repo_root), config)): test_path
            for test_path in test_files
        }

        for completed, future in enumerate(as_completed(future_to_test), start=1):
            result = future.result()
            results.append(result)
            print(f'[{completed}/{len(test_files)}]                 \r', end='', flush=True)

    print()  # New line after progress indicator

    # Print failures and count skipped tests
    python_passed = 0
    vm_passed = 0
    native_passed = 0
    python_skipped = 0
    vm_skipped = 0
    native_skipped = 0
    mismatch_count = 0

    for result in results:
        if result['py_passed']:
            python_passed += 1
        elif result.get('py_skipped'):
            python_skipped += 1
        elif result['py_error']:
            print(f"❌ {result['file']} [Python]: {result['py_error']}")

        if result['vm_passed']:
            vm_passed += 1
        elif result.get('vm_skipped'):
            vm_skipped += 1
        elif result['vm_error']:
            print(f"❌ {result['file']} [C VM]: {result['vm_error']}")

        if result.get('native_passed'):
            native_passed += 1
        elif result.get('native_skipped'):
            native_skipped += 1
        elif result.get('native_error'):
            print(f"❌ {result['file']} [Native]: {result.get('native_error')}")

    # Calculate totals for actually run tests (not skipped)
    total = len(results)
    python_total = total - python_skipped
    vm_total = total - vm_skipped
    native_total = total - native_skipped

    # Print summary
    print()
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)

    print(f"Python Runtime: {python_passed}/{python_total} passed")
    print(f"C VM Runtime:   {vm_passed}/{vm_total} passed")
    print(f"Native Compiler: {native_passed}/{native_total} passed")

    if mismatch_count > 0:
        print(f"⚠️  Runtime Mismatches: {mismatch_count}")
    print("=" * 60)

    if python_passed == python_total and vm_passed == vm_total and native_passed == native_total:
        print("✅ All tests passed on ALL runtimes!")
        return 0
    else:
        if python_passed < python_total:
            print(f"❌ Python runtime has {python_total - python_passed} failure(s)")
        if vm_passed < vm_total:
            print(f"❌ C VM runtime has {vm_total - vm_passed} failure(s)")
        if native_passed < native_total:
            print(f"❌ Native compiler has {native_total - native_passed} failure(s)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
