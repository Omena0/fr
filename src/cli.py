"""
Command-line interface for Fr script
"""
import sys
import os
import subprocess
import json
from pathlib import Path

# Add src to path if running from package
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from binary import encode_binary, decode_binary
from compiler import compile_ast_to_bytecode
from parser import parse
from runtime import run, format_runtime_exception
from debug_runtime import run_with_debug, init_debug_runtime

def get_vm_path():
    """Get path to the C VM executable"""
    # Try package installation location (installed via pip)
    try:
        import importlib.util
        spec = importlib.util.find_spec('runtime')
        if spec and spec.origin:
            runtime_pkg_path = Path(spec.origin).parent
            vm_path = runtime_pkg_path / 'vm'
            if vm_path.exists() and vm_path.is_file():
                return str(vm_path)
    except (ImportError, AttributeError):
        pass
    
    # Try relative to src (development location - sibling to src)
    vm_path = Path(__file__).parent.parent / 'runtime' / 'vm'
    if vm_path.exists():
        return str(vm_path)
    
    # Try legacy runtime directory name (backward compatibility)
    vm_path = Path(__file__).parent.parent / 'runtime' / 'vm'
    if vm_path.exists():
        return str(vm_path)
    
    # Try one level up (alternate development structure)
    vm_path = Path(__file__).parent.parent.parent / 'runtime' / 'vm'
    return str(vm_path) if vm_path.exists() else None

def has_untyped_functions(ast):
    """Check if AST contains functions with untyped parameters"""
    for node in ast:
        if isinstance(node, dict) and node.get('type') == 'function':
            args = node.get('args', [])
            for arg in args:
                if isinstance(arg, (tuple, list)) and len(arg) == 2:
                    if arg[1] is None:
                        return True
                elif isinstance(arg, str):
                    return True
    return False

def detect_file_type(filepath):
    """Detect if file is binary AST, bytecode, or JSON"""
    with open(filepath, 'rb') as f:
        header = f.read(8)

    if header[:4] == b'L2AS':
        return 'binary_ast'

    try:
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('.version') or first_line.startswith('FUNCTION') or first_line.startswith('CONST_'):
                return 'bytecode'
    except:
        pass

    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return 'json'
    except:
        pass

    return 'unknown'

def parse_cmd(args):
    """Parse source code to AST"""
    if len(args) < 1:
        print("Usage: fr parse <source.fr> [--json]")
        sys.exit(1)

    source_file = args[0]
    output_json = '--json' in args or '-j' in args

    with open(source_file) as f:
        source = f.read()

    try:
        ast = parse(source, file=source_file)
    except SyntaxError as e:
        print(f'Exception: {e}')
        sys.exit(1)

    if output_json:
        output_file = 'out.json'
        with open(output_file, 'w') as f:
            json.dump(ast, f, indent=2)
        print(f"Parsed to JSON: {output_file}")
    else:
        output_file = 'out.bin'
        with open(output_file, 'wb') as f:
            f.write(encode_binary(ast))
        print(f"Parsed to binary AST: {output_file}")

def compile_cmd(args=None):
    """Compile AST to bytecode"""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: fr compile <file.fr|ast.bin|ast.json> [-o output.bc]")
        sys.exit(1)

    input_file = args[0]

    # Determine output file
    output_file = 'out.bc'
    if '-o' in args:
        idx = args.index('-o')
        if idx + 1 < len(args):
            output_file = args[idx + 1]

    # Load AST
    file_type = detect_file_type(input_file)

    if file_type == 'json':
        with open(input_file, 'r') as f:
            ast = json.load(f)
    elif file_type == 'binary_ast':
        with open(input_file, 'rb') as f:
            ast = decode_binary(f.read())
    elif input_file.endswith('.fr'):
        # Parse source file to AST first
        try:
            with open(input_file) as f:
                source = f.read()
            ast = parse(source, file=input_file)
        except SyntaxError as e:
            print(f'Parse error: {e}')
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: File not found: {input_file}")
            sys.exit(1)
    else:
        print(f"Error: Cannot compile {input_file} - unknown format")
        print("Expected: .fr, .json, or binary AST file")
        sys.exit(1)

    try:
        bytecode, _line_map = compile_ast_to_bytecode(ast)

        with open(output_file, 'w') as f:
            f.write(bytecode)

        print(f"Compiled to bytecode: {output_file}")
    except Exception as e:
        print(f"Compilation error: {e}")
        sys.exit(1)

def run_cmd(args=None):
    """Run a file"""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: fr run <file>")
        sys.exit(1)

    input_file = args[0]
    file_type = detect_file_type(input_file)

    if file_type == 'bytecode':
        # Run bytecode with C VM
        vm_path = get_vm_path()
        if not vm_path:
            print("Error: C VM not found. Please build it with: cd runtime && make")
            sys.exit(1)

        result = subprocess.run([vm_path, input_file])
        sys.exit(result.returncode)

    elif file_type == 'json':
        with open(input_file, 'r') as f:
            ast = json.load(f)
    elif file_type == 'binary_ast':
        with open(input_file, 'rb') as f:
            ast = decode_binary(f.read())
    else:
        print(f"Error: Cannot run {input_file} - unknown format")
        sys.exit(1)

    # Run with Python runtime
    try:
        run(ast)
    except RuntimeError as e:
        print(e)
        sys.exit(1)

def encode_cmd(args):
    """Encode JSON AST to binary"""
    if len(args) < 1:
        print("Usage: fr encode <ast.json> [-o output.bin]")
        sys.exit(1)

    input_file = args[0]
    output_file = args[2] if '-o' in args and len(args) > 2 else 'out.bin'

    with open(input_file, 'r') as f:
        ast = json.load(f)

    with open(output_file, 'wb') as f:
        f.write(encode_binary(ast))

    print(f"Encoded to binary: {output_file}")

def decode_cmd(args):
    """Decode binary AST to JSON"""
    if len(args) < 1:
        print("Usage: fr decode <ast.bin> [-o output.json]")
        sys.exit(1)

    input_file = args[0]
    output_file = args[2] if '-o' in args and len(args) > 2 else 'out.json'

    with open(input_file, 'rb') as f:
        ast = decode_binary(f.read())

    with open(output_file, 'w') as f:
        json.dump(ast, f, indent=2)

    print(f"Decoded to JSON: {output_file}")

def native_cmd(args):
    """Compile bytecode to x86_64 native binary"""
    if len(args) < 1:
        print("Usage: fr native <file.bc> [-o output] [-a|--asm] [--minimal]")
        print("  -a, --asm:  Keep assembly file")
        print("  --minimal:  Use static linking with syscalls (smaller, no libc)")
        sys.exit(1)

    input_file = args[0]
    keep_asm = '-a' in args or '--asm' in args
    use_minimal = '--minimal' in args or '-min' in args or '-m' in args

    # Determine output filename
    if '-o' in args:
        output_idx = args.index('-o') + 1
        output_base = args[output_idx] if output_idx < len(args) else 'out'
    else:
        output_base = 'out'

    asm_file = output_base if output_base.endswith('.asm') else f'{output_base}.asm'
    exe_file = output_base.replace('.asm', '').replace('.s', '')

    # Ensure input is bytecode
    file_type = detect_file_type(input_file)
    if file_type != 'bytecode':
        print(f"Error: Input must be bytecode file (.bc), got {file_type}")
        sys.exit(1)

    # Read bytecode
    with open(input_file, 'r') as f:
        bytecode = f.read()

    # Compile to x86_64
    try:
        import native
        optimize = '-O' in args
        if optimize:
            print('Optimizing assembly')
        asm, runtime_deps = native.compile(bytecode, optimize)

        # Always write assembly to temp file for building
        with open(asm_file, 'w') as f:
            f.write(asm)

        if keep_asm:
            print(f"Compiled to x86_64 assembly: {asm_file}")

        # When using minimal syscall runtime, remove the entry stub (_start)
        if use_minimal:
            with open(asm_file, 'r') as f:
                lines = f.readlines()

            result_lines = []
            skip_until_section = False
            for i, line in enumerate(lines):
                # Replace .global _start with .global main
                if line.strip() == '.global _start':
                    result_lines.append(line.replace('_start', 'main'))
                    continue
                # Find and remove the _start stub that was generated
                if line.strip() == '_start:' and i > 50:  # After main() function
                    skip_until_section = True
                    continue
                # Stop skipping when we hit the next section
                if skip_until_section and line.startswith('.section'):
                    skip_until_section = False
                if skip_until_section:
                    continue
                result_lines.append(line)

            with open(asm_file, 'w') as f:
                f.writelines(result_lines)

        # Build binary by default
        try:
            # Assemble to object file
            obj_file = asm_file.replace('.s', '.o').replace('.asm', '.o')
            subprocess.run(['as', asm_file, '-o', obj_file], check=True, 
                         capture_output=True)

            runtime_lib = r'runtime/runtime_lib.c'
            runtime_dir = os.path.dirname(os.path.abspath(runtime_lib))

            # Use full minimal runtime with dynamic linking
            gcc_flags = [
                'gcc', obj_file, str(runtime_lib), '-o', exe_file,
                f'-I{runtime_dir}', '-Ofast', '-march=native', '-mtune=native',
                '-flto', '-ffast-math', '-funroll-loops',
                '-ffunction-sections', '-fdata-sections',
                '-Wl,--gc-sections', '-s',
                '-lm', '-no-pie'
            ]

            # Build native binary executable
            subprocess.run(gcc_flags, check=True, capture_output=True)

            print(f"Built executable: {exe_file}")

            # Clean up intermediate files
            # DEBUG: Keep object file
            # os.remove(obj_file)
            if not keep_asm:
                os.remove(asm_file)

        except subprocess.CalledProcessError as e:
            print(f"Build error: {e}")
            if e.stderr:
                print(e.stderr.decode())
            sys.exit(1)

    except Exception as e:
        print(f"Compilation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Fr - Fast bytecode-compiled language")
        print()
        print("Usage:")
        print("  fr <file.fr> [-c|--compile] [-py|--python] [-O|--optimize] [--debug]")
        print("                                    -c: Force C backend compilation")
        print("                                   -py: Force Python backend runtime")
        print("                                --debug: Run in debug mode (for debugger)")
        print("  fr parse <file.fr> [--json]     - Parse to AST (binary or JSON)")
        print("  fr compile <file.fr|ast.json|ast.bin> [-o out.bc] - Compile to bytecode")
        print("  fr native <file.bc> [-o out] [-a|--asm] [--minimal] - Compile bytecode to native binary")
        print("  fr run <file>                   - Run file (auto-detect type)")
        print("  fr encode <ast.json> [-o out]   - Encode JSON to binary AST")
        print("  fr decode <ast.bin> [-o out]    - Decode binary to JSON AST")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == 'parse':
        parse_cmd(args)
    elif cmd == 'compile':
        compile_cmd(args)
    elif cmd == 'native':
        native_cmd(args)
    elif cmd == 'run':
        run_cmd(args)
    elif cmd == 'encode':
        encode_cmd(args)
    elif cmd == 'decode':
        decode_cmd(args)
    elif os.path.exists(cmd):
        # Check for backend flags
        force_c_backend = '-c' in args or '--compile' in args
        force_py_backend = '-py' in args or '--python' in args
        debug_mode = '--debug' in args

        # Validate flags
        if force_c_backend and force_py_backend:
            print("Error: Cannot use both -c and -py flags", file=sys.stderr)
            sys.exit(1)

        # Debug mode requires Python backend
        if debug_mode and force_c_backend:
            print("Error: Debug mode requires Python backend, cannot use -c flag", file=sys.stderr)
            sys.exit(1)

        # Filter out flags to get program arguments
        program_args = [arg for arg in args if arg not in ['-c', '--compile', '-py', '--python', '-O', '--optimize', '--debug']]

        # Direct file execution
        file_type = detect_file_type(cmd)

        if file_type == 'bytecode':
            run_cmd([cmd])
        else:
            # Parse and run source file
            with open(cmd) as f:
                source = f.read()

            # Parse with optimization flag (checks sys.argv internally)
            try:
                ast = parse(source, file=cmd)
            except SyntaxError as e:
                print(f'Exception: {e}')
                sys.exit(1)

            # Determine which backend to use
            if force_py_backend or debug_mode:
                use_c_backend = False
            else:
                use_c_backend = force_c_backend or not has_untyped_functions(ast)

            if use_c_backend:
                try:
                    bytecode, line_map = compile_ast_to_bytecode(ast)

                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
                        f.write(bytecode)
                        temp_bc = f.name

                    if vm_path := get_vm_path():
                        # Prepare debug info for stdin
                        import json
                        debug_info = json.dumps({
                            'file': cmd,
                            'source': source,
                            'line_map': line_map
                        })
                        
                        # Pass program arguments to the VM with --debug-info flag
                        result = subprocess.run(
                            [vm_path, '--debug-info', temp_bc] + program_args,
                            input=debug_info,
                            text=True
                        )
                        os.unlink(temp_bc)
                        sys.exit(result.returncode)
                    else:
                        print("Warning: C VM not found, using Python runtime")
                        os.unlink(temp_bc)
                        use_c_backend = False
                except Exception as e:
                    if force_c_backend:
                        # User explicitly requested compilation, show error and exit
                        print(f"Compilation error: {e}", file=sys.stderr)
                        sys.exit(1)
                    else:
                        # Fall back to Python runtime for auto-detection
                        print(f"Warning: C compilation failed ({e}), using Python runtime")
                        use_c_backend = False
                except KeyboardInterrupt:
                    print(end='\r')
                    exit(0)

            if not use_c_backend:
                try:
                    if debug_mode:
                        # Run with debug runtime
                        init_debug_runtime()
                        run_with_debug(ast, cmd)
                    else:
                        run(ast, file=cmd, source=source)
                except RuntimeError as e:
                    print(f'Exception: {format_runtime_exception(e)}')
                    sys.exit(1)
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'fr' without arguments for usage information.")
        sys.exit(1)

if __name__ == '__main__':
    main()
