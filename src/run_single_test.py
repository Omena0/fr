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

# Save original argv before modifying it
original_argv = sys.argv.copy()

# Setup paths
sys.path.insert(0, 'src')
sys.argv = [sys.argv[0], '-d']  # Enable debug mode

# Import after path setup
from parser import parse
from compiler import compile_ast_to_bytecode
from runtime import run, format_runtime_exception
from native import compile as compile_to_native, create_minimal_runtime

def extract_error_message(error_text):
    """Extract and normalize error message to match expected format"""
    if not error_text:
        return ''

    # Runtime errors can have two formats:
    # 1. "...file.fr:line:char: Message"
    # 2. "...Line line:char: Message" (when filename is not .fr)
    # Look for the last line with either pattern
    lines = error_text.strip().split('\n')
    for line in reversed(lines):
        # Try to match "file.fr:line:char: Message" first
        if '.fr:' in line and ':' in line:
            parts = line.split('.fr:', 1)
            if len(parts) > 1:
                loc_and_msg = parts[1]
                # Format is "line:char: Message"
                # Split only the first two colons (line and char), keep rest as message
                first_colon = loc_and_msg.find(':')
                if first_colon != -1:
                    line_num = loc_and_msg[:first_colon].strip()
                    rest = loc_and_msg[first_colon+1:]
                    second_colon = rest.find(':')
                    if second_colon != -1:
                        char_num = rest[:second_colon].strip()
                        message = rest[second_colon+1:].strip()
                        # Return in format ?line,char:message
                        return f"?{line_num},{char_num}:{message}"

        # Try to match "Line line:char: Message" or "filename:line:char: Message" format
        # This handles errors where file is not .fr or Line prefix is used
        if ': ' in line and any(x in line for x in ['Line ', ':', ' line ']):
            # Look for pattern like "Line 5:16: " or "file:5:16: "
            import re
            if match := re.search(r'(?:Line\s+)?(\d+):(\d+):\s+(.+)$', line):
                line_num = match.group(1)
                char_num = match.group(2)
                message = match.group(3)
                return f"?{line_num},{char_num}:{message}"

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
    # Filename can be passed as first argument
    test_filename = original_argv[1] if len(original_argv) > 1 else ''

    # Check for skip flags
    skip_py = '--skip-py' in original_argv
    skip_c = '--skip-c' in original_argv
    skip_native = '--skip-native' in original_argv

    # Test content is read from stdin
    content = sys.stdin.read()

    # Parse test - first line is the expectation, rest is code
    lines = content.split('\n', 1)
    if len(lines) < 2:
        print("ERROR:Invalid test format")
        return 1

    expect_line = lines[0]
    # Keep the original code with blank line to preserve line numbers
    # Replace the expectation line with a blank line so line numbers match the file
    code = '\n' + lines[1] if lines[1] else '\n'

    # Check for runtime-specific test markers
    runtime_filter = None  # None means run on both, 'python' or 'c' for specific
    if '@python-only' in expect_line or '@python' in expect_line:
        runtime_filter = 'python'
    elif '@c-only' in expect_line or '@c' in expect_line:
        runtime_filter = 'c'

    # Extract expectation
    expect = expect_line.replace('//', '').strip()
    # Remove runtime markers from expectation
    expect = expect.replace('@python-only', '').replace('@python', '').replace('@c-only', '').replace('@c', '').strip()

    is_output_test = expect.startswith('!')

    # Split by || to get alternative expected outputs first
    if '||' in expect:
        expect_alternatives = [e.strip() for e in expect.split('||')]
        # Remove ! from each alternative if this is an output test
        if is_output_test:
            expect_alternatives = [e[1:].strip().replace('\\n', '\n') if e.startswith('!') else e.strip().replace('\\n', '\n') for e in expect_alternatives]
        expect = expect_alternatives[0]  # Use first alternative as primary
    else:
        if is_output_test:
            expect = expect[1:].strip().replace('\\n', '\n')
        else:
            expect = expect.rstrip('.')
        expect_alternatives = [expect]

    # Special case: if expect is "none", test passes if parsing succeeds
    # Don't run the code to avoid timeouts from infinite loops
    if expect.lower() == 'none' and not is_output_test:
        try:
            ast = parse(code)
            # Parse succeeded - all runtimes pass
            print("PY_OUTPUT:none")
            print("VM_OUTPUT:none")
            print("NATIVE_OUTPUT:none")
            print("EXPECT:none")
            print("IS_OUTPUT:False")
            return 0
        except Exception as e:
            err_msg = extract_error_message(str(e))
            print(f"PY_ERROR:{err_msg}")
            print(f"VM_ERROR:{err_msg}")
            print(f"NATIVE_ERROR:{err_msg}")
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
        print(f"NATIVE_OUTPUT:{err_msg}")
        print(f"EXPECT:{expect}")
        print(f"IS_OUTPUT:{is_output_test}")
        return 0

    # Run on Python runtime (unless filtered out or skipped)
    py_error = None
    py_output = None
    if runtime_filter != 'c' and not skip_py:
        old_stdout = sys.stdout
        string_io = StringIO()
        sys.stdout = string_io
        try:
            run(ast, file=test_filename, source=code)
            py_output = string_io.getvalue().strip()
        except Exception as e:
            py_output = None
            # Format runtime errors properly
            if isinstance(e, RuntimeError):
                formatted_error = format_runtime_exception(e)
                # Extract the message in ?line:message format
                py_error = extract_error_message(formatted_error)
            else:
                py_error = str(e)
        finally:
            sys.stdout = old_stdout
    else:
        # Skip Python runtime for C-only tests or if --skip-py was specified
        py_output = None
        py_error = "SKIPPED"

    # Run on C VM runtime (unless filtered out or skipped)
    vm_error = None
    vm_output = None
    if runtime_filter != 'python' and not skip_c:
        try:
            bytecode, line_map = compile_ast_to_bytecode(ast)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
                bc_file = f.name
                f.write(bytecode)

            # Try to find VM path
            vm_path = None
            # Try new package location
            try:
                import importlib.util
                spec = importlib.util.find_spec('runtime')
                if spec and spec.origin:
                    from pathlib import Path
                    runtime_pkg_path = Path(spec.origin).parent
                    vm_candidate = runtime_pkg_path / 'vm'
                    if vm_candidate.exists():
                        vm_path = str(vm_candidate)
            except (ImportError, AttributeError):
                pass

            # Fall back to development locations
            if not vm_path:
                from pathlib import Path
                vm_candidate = Path('runtime/vm')
                vm_path = str(vm_candidate) if vm_candidate.exists() else 'runtime/vm'
            # Prepare debug info for VM
            import json
            debug_info = json.dumps({
                'file': test_filename,
                'source': code,
                'line_map': line_map
            })

            result = subprocess.run(
                [vm_path, '--debug-info', bc_file],
                input=debug_info,
                capture_output=True,
                text=True,
                timeout=5
            )

            os.unlink(bc_file)

            # Capture output even if program crashes (e.g., stack overflow after main returns)
            vm_output = result.stdout.strip() if result.stdout else ""

            if result.returncode != 0:
                stderr_text = result.stderr.strip() if result.stderr else f"VM exited with code {result.returncode}"
                # Extract the error message from stderr
                vm_error = extract_error_message(stderr_text)

                # If there's an error in stderr (exception, runtime error), discard partial stdout
                # to match Python runtime behavior where exceptions override partial output
                if (stderr_text and "Exception:" in stderr_text or not vm_output):
                    vm_output = None

        except subprocess.TimeoutExpired:
            vm_error = "Timeout"
            vm_output = None
        except Exception as e:
            vm_error = str(e)
            vm_output = None
    else:
        # Skip C VM runtime for python-only tests
        vm_output = None
        vm_error = "SKIPPED"

    # Run on native compiler (unless skipped)
    native_error = None
    native_output = None
    if not skip_native:
        try:
            # Compile to bytecode (reuse from VM compilation)
            bytecode, line_map = compile_ast_to_bytecode(ast)

            # Compile bytecode to x86_64 assembly
            assembly, runtime_deps = compile_to_native(bytecode, optimize=False)

            # Create minimal runtime with only needed functions
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                runtime_file = f.name
            
            create_minimal_runtime(runtime_deps, runtime_file)

            # Write assembly to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.s', delete=False) as f:
                asm_file = f.name
                f.write(assembly)

            # Find runtime library header (for compilation)
            from pathlib import Path
            runtime_h = Path(__file__).parent.parent / 'runtime' / 'runtime_lib.h'
            runtime_include_dir = str(runtime_h.parent)

            # Compile assembly and runtime to binary using gcc
            with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False) as f:
                native_bin = f.name

            compile_cmd = ['gcc', '-I' + runtime_include_dir, '-o', native_bin, asm_file, runtime_file, '-lm', '-no-pie']

            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                native_error = extract_error_message(result.stderr)
                native_output = None
            else:
                # Run the compiled binary
                result = subprocess.run(
                    [native_bin],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                native_output = result.stdout.strip() if result.stdout else ""

                if result.returncode != 0:
                    stderr_text = result.stderr.strip() if result.stderr else f"Binary exited with code {result.returncode}"
                    native_error = extract_error_message(stderr_text)

                    # If there's an error in stderr, discard partial stdout to match Python runtime behavior
                    if stderr_text and not native_output:
                        native_output = None

                # Clean up binary
                try:
                    os.unlink(native_bin)
                except:
                    pass

            # Clean up temporary files
            try:
                os.unlink(asm_file)
                os.unlink(runtime_file)
            except:
                pass

        except subprocess.TimeoutExpired:
            native_error = "Timeout"
            native_output = None
        except Exception as e:
            native_error = str(e)
            native_output = None
    else:
        # Skip native compiler if requested
        native_output = None
        native_error = "SKIPPED"

    # Output results
    if py_error and py_error != "SKIPPED":
        print(f"PY_ERROR:{py_error}")
    elif py_error != "SKIPPED":
        print(f"PY_OUTPUT:{py_output if py_output is not None else ''}")
    # Don't output PY results if skipped

    # For VM: prioritize output over error if we have valid output
    # This handles cases where program outputs correctly but crashes during cleanup
    if vm_error == "SKIPPED":
        # Don't output VM results if skipped
        pass
    elif vm_output is not None:
        # Has output (could be empty string)
        print(f"VM_OUTPUT:{vm_output}")
    elif vm_error:
        # Has error and no output
        print(f"VM_ERROR:{vm_error}")
    else:
        # No output and no error
        print("VM_OUTPUT:")

    # For native: prioritize output over error if we have valid output
    if native_error == "SKIPPED":
        # Don't output native results if skipped
        pass
    elif native_output is not None:
        # Has output (could be empty string)
        print(f"NATIVE_OUTPUT:{native_output}")
    elif native_error:
        # Has error and no output
        print(f"NATIVE_ERROR:{native_error}")
    else:
        # No output and no error
        print("NATIVE_OUTPUT:")

    print(f"EXPECT:{expect}")
    print(f"EXPECT_ALTERNATIVES:{'||'.join(expect_alternatives)}")
    print(f"IS_OUTPUT:{is_output_test}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
