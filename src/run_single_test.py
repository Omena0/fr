#!/usr/bin/env python3
"""
Helper script to run a single test in isolation.
This is called by tests_isolated.py for each test.
Test content is read from stdin.
"""
import sys
import os
import shutil
import tempfile
import subprocess
from io import StringIO
from pathlib import Path

# Save original argv before modifying it
original_argv = sys.argv.copy()

# Setup paths
sys.path.insert(0, 'src')
sys.argv = [sys.argv[0], '-d']  # Enable debug mode

# Import after path setup
from parser import parse
from compiler import compile_ast_to_bytecode
from runtime import run, format_runtime_exception # type: ignore
from native import compile as compile_to_native

RUNTIME_DIR = Path(__file__).parent.parent / 'runtime'
RUNTIME_SRC = RUNTIME_DIR / 'runtime_lib.c'
RUNTIME_INCLUDE_DIR = str(RUNTIME_DIR)
RUNTIME_OBJ = Path(tempfile.gettempdir()) / 'frscript_runtime_lib.o'

def ensure_runtime_object():
    """Compile runtime_lib.c to an object file and reuse it across tests."""
    src_mtime = RUNTIME_SRC.stat().st_mtime
    if RUNTIME_OBJ.exists():
        try:
            if RUNTIME_OBJ.stat().st_mtime >= src_mtime:
                return str(RUNTIME_OBJ)
        except OSError:
            pass

    tmp_obj = RUNTIME_OBJ.with_suffix('.o.tmp')
    compile_cmd = [
        'gcc', '-c', '-O3', '-march=native', '-mtune=native',
        '-ffunction-sections', '-fdata-sections',
        '-I', RUNTIME_INCLUDE_DIR,
        '-o', str(tmp_obj), str(RUNTIME_SRC)
    ]
    result = subprocess.run(compile_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        try:
            tmp_obj.unlink()
        except OSError:
            pass
        raise RuntimeError(result.stderr.strip() or 'Failed to compile runtime_lib.c')

    tmp_obj.replace(RUNTIME_OBJ)
    return str(RUNTIME_OBJ)

def extract_error_message(error_text):
    """Extract and normalize error message to match expected format"""
    if not error_text:
        return ''

    lines = error_text.strip().split('\n')
    
    # For WAT validation errors, look for "error:" lines
    for line in lines:
        if 'error:' in line.lower() and ('out.wat' in line or '.wat:' in line):
            # Extract the actual error message after "error:"
            error_part = line.split('error:', 1)
            if len(error_part) > 1:
                return error_part[1].strip()
    
    # Check if already in ?line,col:message format (from runtime errors)
    for line in reversed(lines):
        if line.startswith('?'):
            # Already in correct format, just return it
            return line

    # Runtime errors can have two formats:
    # 1. "...file.fr:line:char: Message"
    # 2. "...Line line:char: Message" (when filename is not .fr)
    # Look for the last line with either pattern
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

    # For Python exceptions, look for the actual exception message
    for line in reversed(lines):
        if line.strip() and not line.startswith(' ') and not line.startswith('File ') and not line.startswith('Traceback'):
            # This is likely the exception message
            if ':' in line and 'Error' in line:
                # Format like "WasmCompilerError: message"
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()

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
    skip_wasm = '--skip-wasm' in original_argv

    # Test content is read from stdin
    content = sys.stdin.read()

    # Parse test - collect expectation comment lines at the beginning
    # First line: MUST be a comment (can be any comment)
    # Subsequent lines: ONLY if they start with '!', '?', or '@' (expectation markers)
    lines = content.split('\n')
    expect_lines = []
    code_start_idx = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip pragma directives when looking for expectations
        if stripped.startswith('#pragma'):
            code_start_idx = i + 1
            continue

        if stripped.startswith('//'):
            comment_content = stripped[2:].strip()  # Remove '//' and whitespace

            if not expect_lines:
                # First expectation line: Always treat as expectation
                expect_lines.append(comment_content)
                code_start_idx = i + 1
            elif comment_content.startswith('!') or comment_content.startswith('?') or comment_content.startswith('@'):
                # Subsequent lines: Only if they're expectation markers
                # For lines after the first, remove the '!' prefix if present
                # (only first line's '!' indicates output test)
                if comment_content.startswith('!'):
                    comment_content = comment_content[1:]
                expect_lines.append(comment_content)
                code_start_idx = i + 1
            else:
                # Regular comment (not an expectation) - stop looking for expectations
                break
        elif stripped == '':
            # Blank line after expectations - stop
            if expect_lines:
                break
            # Blank line before expectations - continue
            code_start_idx = i + 1
        else:
            # Found non-comment, non-blank line - stop
            break

    if not expect_lines:
        print("ERROR:Invalid test format - no expectation comment found")
        return 1

    # Join all expectation lines with newlines
    expect_line = '\n'.join(expect_lines)

    # Build code with blank lines to preserve line numbers
    code = '\n' * code_start_idx + '\n'.join(lines[code_start_idx:])

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
            ast = parse(code, file=test_filename)
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
        ast = parse(code, file=test_filename)
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

    # Determine whether we need bytecode for VM/native runtimes
    needs_bytecode = (runtime_filter != 'python' and not skip_c) or not skip_native
    bytecode = None
    line_map = []
    compile_error = None
    if needs_bytecode:
        try:
            bytecode, line_map = compile_ast_to_bytecode(ast)
        except Exception as e:
            compile_error = str(e)

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
        if compile_error:
            vm_error = compile_error
        else:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
                    bc_file = f.name
                    f.write(bytecode)

                # Extract and compile C imports
                c_import_so_files = []
                for line in bytecode.split('\n'):
                    if line.startswith('# C import:'):
                        c_file = line.split(':', 1)[1].strip()
                        # Make C file path absolute relative to test file
                        test_dir = os.path.dirname(os.path.abspath(test_filename))
                        c_file_abs = os.path.join(test_dir, c_file)

                        # Compile to .so
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.so', delete=False) as so_f:
                            so_file = so_f.name
                            c_import_so_files.append(so_file)

                        # Compile C file to shared library
                        compile_result = subprocess.run(
                            ['gcc', '-fPIC', '-shared', '-o', so_file, c_file_abs],
                            capture_output=True,
                            text=True
                        )
                        if compile_result.returncode != 0:
                            vm_error = f"Failed to compile {c_file}: {compile_result.stderr}"
                            break

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

                # Build VM command with .so files
                vm_command = [vm_path, '--debug-info', bc_file] + c_import_so_files

                # Set FR_TEST_MODE=1 for test error format
                env = os.environ.copy()
                env['FR_TEST_MODE'] = '1'

                result = subprocess.run(
                    vm_command,
                    input=debug_info,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env=env
                )

                os.unlink(bc_file)
                # Clean up .so files
                for so_file in c_import_so_files:
                    try:
                        os.unlink(so_file)
                    except:
                        pass

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
        # Skip C VM runtime for python-only tests or if --skip-py was specified
        vm_output = None
        vm_error = "SKIPPED"

    # Run on native compiler (unless skipped)
    native_error = None
    native_output = None
    if skip_native:
        # Skip native compiler if requested
        native_output = None
        native_error = "SKIPPED"
        native_error = "SKIPPED"

    elif compile_error:
        native_error = compile_error
    else:
        runtime_obj = None
        try:
            runtime_obj = ensure_runtime_object()
        except Exception as exc:
            native_error = str(exc)
        if runtime_obj:
            try:
                # Extract C imports from bytecode
                c_import_files = []
                for line in bytecode.split('\n'):
                    if line.startswith('# C import:'):
                        c_file = line.split(':', 1)[1].strip()
                        # Make C file path absolute relative to test file
                        test_dir = os.path.dirname(os.path.abspath(test_filename))
                        c_file_abs = os.path.join(test_dir, c_file)
                        c_import_files.append(c_file_abs)

                # Compile bytecode to x86_64 assembly
                assembly, runtime_deps = compile_to_native(bytecode, optimize=True)

                # Assemble via stdin without writing the assembly file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.o', delete=False) as f:
                    obj_file = f.name

                asm_result = subprocess.run(
                    ['as', '-o', obj_file, '-'],
                    input=assembly,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if asm_result.returncode != 0:
                    native_error = extract_error_message(asm_result.stderr)
                    native_output = None
                else:
                    # Compile assembly and runtime to binary using gcc
                    with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False) as f:
                        native_bin = f.name

                    compile_cmd = [
                        'gcc',
                        obj_file,
                        runtime_obj,
                        f'-I{RUNTIME_INCLUDE_DIR}',
                        '-O3', '-march=native', '-mtune=native',
                        '-ffunction-sections', '-fdata-sections',
                        '-Wl,--gc-sections',
                        '-o',
                        native_bin,
                    ] + c_import_files + [  # Add C import files to the command
                        '-lm',
                        '-no-pie',
                    ]

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
                        env = os.environ.copy()
                        env['FR_TEST_MODE'] = '1'

                        result = subprocess.run(
                            [native_bin],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            env=env
                        )

                        native_output = result.stdout.strip() if result.stdout else ""

                        if result.returncode != 0:
                            if result.returncode < 0:
                                signal_num = -result.returncode
                                signal_names = {11: "SIGSEGV", 6: "SIGABRT", 9: "SIGKILL", 15: "SIGTERM"}
                                signal_name = signal_names.get(signal_num, f"SIGNAL{signal_num}")
                                stderr_text = f"Binary crashed: {signal_name} (exit code {result.returncode})"
                            else:
                                stderr_text = result.stderr.strip() if result.stderr else f"Binary exited with code {result.returncode}"
                            native_error = extract_error_message(stderr_text)

                            if stderr_text and not native_output:
                                native_output = None

                    try:
                        os.unlink(native_bin)
                    except:
                        pass

                try:
                    os.unlink(obj_file)
                except:
                    pass

            except subprocess.TimeoutExpired:
                native_error = "Timeout"
                native_output = None
            except Exception as e:
                native_error = str(e)
                native_output = None

    # Run Wasm emission command (unless skipped)
    wasm_error = None
    wasm_output = None
    if skip_wasm:
        wasm_error = "SKIPPED"
    else:
        wasm_dir = tempfile.mkdtemp(prefix='fr-wasm-')
        os.makedirs(wasm_dir, exist_ok=True)
        wasm_dest = Path(wasm_dir) / 'output.wasm'
        wasm_command = [sys.executable, '-m', 'src.cli', 'wasm', test_filename, '-o', str(wasm_dest)]
        repo_root = Path(__file__).parent.parent
        try:
            # Compile to WASM
            result = subprocess.run(
                wasm_command,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(repo_root)
            )
            if result.returncode != 0:
                stderr_text = result.stderr.strip() if result.stderr else result.stdout.strip()
                wasm_error = extract_error_message(stderr_text)
            else:
                # Compilation succeeded, now try to execute
                # Check if the .wasm file was generated
                if wasm_dest.exists():
                    # Try to run with fr-wasm runner
                    runner_path = repo_root / 'runtime' / 'target' / 'release' / 'fr-wasm'
                    if runner_path.exists():
                        run_result = subprocess.run(
                            [str(runner_path), str(wasm_dest)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            cwd=str(repo_root)
                        )
                        if run_result.returncode != 0:
                            stderr_text = run_result.stderr.strip() if run_result.stderr else run_result.stdout.strip()
                            wasm_error = extract_error_message(stderr_text)
                        else:
                            wasm_output = run_result.stdout.strip()
                    else:
                        # No runner available, just mark as compile-only success
                        wasm_output = "Compiled (no runner)"
                else:
                    # WASM file not generated - capture the actual error from output
                    stderr_text = result.stderr.strip() if result.stderr else ""
                    stdout_text = result.stdout.strip() if result.stdout else ""
                    # Look for error messages in the output
                    combined_output = (stderr_text + "\n" + stdout_text).strip()
                    if "Error:" in combined_output or "error:" in combined_output:
                        wasm_error = extract_error_message(combined_output)
                    else:
                        wasm_error = "WASM file not generated"

        except subprocess.TimeoutExpired:
            wasm_error = "Timeout"
        except Exception as exc:
            wasm_error = str(exc)
        finally:
            shutil.rmtree(wasm_dir, ignore_errors=True)

    # Output results
    if py_error and py_error != "SKIPPED":
        print(f"PY_ERROR:{py_error}")
    elif py_error != "SKIPPED":
        escaped_py = py_output.replace('\\', '\\\\').replace('\n', '\\n') if py_output is not None else ''
        print(f"PY_OUTPUT:{escaped_py}")
    # Don't output PY results if skipped

    # For VM: prioritize output over error if we have valid output
    # EXCEPT for error tests (expect starts with ?), where we prefer stderr
    # This handles cases where program outputs correctly but crashes during cleanup
    is_error_test = expect.startswith('?')
    if vm_error == "SKIPPED":
        # Don't output VM results if skipped
        pass
    elif is_error_test and vm_error and vm_error != "SKIPPED":
        # For error tests, prefer the error over stdout
        print(f"VM_ERROR:{vm_error}")
    elif vm_output is not None:
        # Has output (could be empty string)
        # Escape newlines so multiline output is on one line
        escaped_output = vm_output.replace('\\', '\\\\').replace('\n', '\\n')
        print(f"VM_OUTPUT:{escaped_output}")
    elif vm_error:
        # Has error and no output
        print(f"VM_ERROR:{vm_error}")
    else:
        # No output and no error
        print("VM_OUTPUT:")

    # For native: prioritize output over error if we have valid output
    # EXCEPT for error tests (expect starts with ?), where we prefer stderr
    is_error_test = expect.startswith('?')
    if native_error == "SKIPPED":
        # Don't output native results if skipped
        pass
    elif is_error_test and native_error and native_error != "SKIPPED":
        # For error tests, prefer the error over stdout
        print(f"NATIVE_ERROR:{native_error}")
    elif native_output is not None:
        # Has output (could be empty string)
        # Escape newlines so multiline output is on one line
        escaped_output = native_output.replace('\\', '\\\\').replace('\n', '\\n')
        print(f"NATIVE_OUTPUT:{escaped_output}")
    elif native_error:
        # Has error and no output
        print(f"NATIVE_ERROR:{native_error}")
    else:
        # No output and no error
        print("NATIVE_OUTPUT:")

    # Wasm command output (compile-only, no expectation match)
    if wasm_error == "SKIPPED":
        pass
    elif wasm_error:
        print(f"WASM_ERROR:{wasm_error}")
    else:
        escaped_wasm = wasm_output.replace('\\', '\\\\').replace('\n', '\\n') if wasm_output is not None else ''
        print(f"WASM_OUTPUT:{escaped_wasm}")

    escaped_expect = expect.replace('\\', '\\\\').replace('\n', '\\n')
    print(f"EXPECT:{escaped_expect}")
    escaped_alts = []
    for alt in expect_alternatives:
        escaped = alt.replace('\\', '\\\\').replace('\n', '\\n')
        escaped_alts.append(escaped)
    print(f"EXPECT_ALTERNATIVES:{'||'.join(escaped_alts)}")
    print(f"IS_OUTPUT:{is_output_test}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
