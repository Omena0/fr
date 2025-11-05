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

    return 'source'

def run_cmd(cmd, args):
    """Run a file using appropriate runtime based on file type and flags"""
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
    program_args = [arg for arg in args if arg not in ['-c', '--compile', '-py', '--python', '-O', '-O0', '--optimize', '--debug']]

    import tempfile
    import json

    # Detect file type and load/parse as needed
    file_type = detect_file_type(cmd)

    # Variables that will be populated based on file type
    ast = None
    bytecode = None
    line_map = None
    source = None
    temp_bc = None
    should_cleanup_temp = False

    try:
        # ===== PHASE 1: Load/Parse input file =====
        if file_type == 'source':
            # Parse .fr source file
            with open(cmd) as f:
                source = f.read()

            try:
                ast = parse(source, file=cmd)
            except SyntaxError as e:
                print(f'Exception: {e}')
                sys.exit(1)

        elif file_type == 'json':
            # Load JSON AST file
            with open(cmd) as f:
                ast = json.load(f)
            source = None
            line_map = None

        elif file_type == 'binary_ast':
            # Load binary AST file
            with open(cmd, 'rb') as f:
                ast = decode_binary(f.read())
            source = None
            line_map = None

        elif file_type == 'bytecode':
            # Load bytecode file directly
            with open(cmd) as f:
                bytecode = f.read()
            source = None
            line_map = None
            ast = None

        # ===== PHASE 2: Determine runtime backend =====
        use_c_backend = False

        if bytecode is None:
            # We have AST - need to compile to bytecode
            if ast is None:
                print("Error: Failed to load file", file=sys.stderr)
                sys.exit(1)

            if force_py_backend or debug_mode:
                # Determine if we can use C backend
                has_c_imports = any(node.get('type') == 'c_import' for node in ast) if isinstance(ast, list) else False

                # User forced Python backend
                if has_c_imports:
                    print("Error: C imports require compilation, cannot use Python backend", file=sys.stderr)
                    sys.exit(1)
                use_c_backend = False
            else:
                # Auto-detect or use forced C backend
                use_c_backend = True if force_c_backend else not has_untyped_functions(ast)
        elif not force_py_backend and not debug_mode:
            use_c_backend = True

        # ===== PHASE 3: Compile AST to bytecode if needed =====
        if bytecode is None:
            # Compile AST to bytecode
            if ast is None:
                print("Error: Failed to prepare AST for compilation", file=sys.stderr)
                sys.exit(1)
            bytecode, line_map = compile_ast_to_bytecode(ast)

        # ===== PHASE 4: Prepare bytecode file =====
        c_link_flags = []
        
        # Extract c_link flags from bytecode if present
        if bytecode:
            for line in bytecode.split('\n'):
                if line.startswith('# c_link:'):
                    # Extract flag after "# c_link: "
                    flag = line[len('# c_link:'):].strip()
                    if flag and flag not in c_link_flags:
                        c_link_flags.append(flag)
        
        if use_c_backend:
            # Need to write bytecode to file for C VM
            if temp_bc is None:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
                    f.write(bytecode)
                    temp_bc = f.name
                    should_cleanup_temp = True

            if vm_path := get_vm_path():
                try:
                    # Prepare debug info for stdin
                    debug_info = json.dumps({
                        'file': cmd,
                        'source': source or '',
                        'line_map': line_map or []
                    })

                    # Pass program arguments to the VM with --debug-info flag
                    result = subprocess.run(
                        [vm_path, '--debug-info', temp_bc] + program_args,
                        input=debug_info,
                        text=True
                    )
                    sys.exit(result.returncode)

                except KeyboardInterrupt:
                    print(end='\r')
                    sys.exit(1)
                finally:
                    if should_cleanup_temp and temp_bc and os.path.exists(temp_bc):
                        os.unlink(temp_bc)

            elif force_c_backend:
                print("Error: C VM not found", file=sys.stderr)
                sys.exit(1)
            else:
                print("Warning: C VM not found, using Python runtime")
                use_c_backend = False

        if not use_c_backend:
            # Run with Python runtime
            if ast is None:
                # We must have bytecode if ast is None - cannot run bytecode with Python
                print("Error: Cannot run compiled bytecode with Python runtime, use C VM instead", file=sys.stderr)
                if should_cleanup_temp and temp_bc and os.path.exists(temp_bc):
                    os.unlink(temp_bc)
                sys.exit(1)

            try:
                if debug_mode:
                    # Run with debug runtime
                    init_debug_runtime()
                    run_with_debug(ast, cmd)
                else:
                    run(ast, file=cmd, source=source or '')
            except RuntimeError as e:
                print(f'Exception: {format_runtime_exception(e)}')
                sys.exit(1)
            finally:
                if should_cleanup_temp and temp_bc and os.path.exists(temp_bc):
                    os.unlink(temp_bc)

    except Exception as e:
        if force_c_backend:
            # User explicitly requested compilation, show error and exit
            print(f"Error: {e}", file=sys.stderr)
            if should_cleanup_temp and temp_bc and os.path.exists(temp_bc):
                os.unlink(temp_bc)
            sys.exit(1)
        else:
            # Try to fall back to Python runtime
            print(f"Warning: {e}", file=sys.stderr)
            if should_cleanup_temp and temp_bc and os.path.exists(temp_bc):
                os.unlink(temp_bc)
            sys.exit(1)

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
        print("Usage: fr native <file.bc> [-o output] [-a|--asm]")
        print("  -a, --asm:  Keep assembly file")
        sys.exit(1)

    input_file = args[0]
    keep_asm = '-a' in args or '--asm' in args

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

    # Extract C import files and linker flags from bytecode comments
    c_import_files = []
    link_libs = []
    for line in bytecode.split('\n'):
        if line.startswith('# C import:'):
            c_file = line.split('# C import:')[1].strip()
            c_import_files.append(c_file)
        elif line.startswith('# Link:'):
            lib = line.split('# Link:')[1].strip()
            # Split the library flags by spaces to handle multiple flags like "-L./lib -lraylib"
            lib_flags = lib.split()
            for flag in lib_flags:
                if flag not in link_libs:
                    link_libs.append(flag)

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

        # Build binary by default
        try:
            # Compile C import files to object files (skip header files)
            c_obj_files = []
            for c_file in c_import_files:
                # Skip header files - they're for parsing only
                if c_file.endswith('.h'):
                    continue

                c_obj = c_file.replace('.c', '.o')
                print(f"Compiling C file: {c_file}")
                result = subprocess.run([
                    'gcc', '-c', c_file, '-o', c_obj,
                    '-O0', '-march=native', '-mtune=native',
                    '-finline-functions', '-funroll-loops',
                    '-fno-strict-aliasing', '-fwrapv', '-fno-tree-pre', '-fno-ipa-cp',
                    '-ffunction-sections', '-fdata-sections'
                ], capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"Error compiling C file {c_file}:")
                    if result.stderr:
                        print(result.stderr)
                    if result.stdout:
                        print(result.stdout)
                    sys.exit(1)

                c_obj_files.append(c_obj)

            # Assemble to object file
            obj_file = asm_file.replace('.s', '.o').replace('.asm', '.o')
            subprocess.run(['as', asm_file, '-o', obj_file], check=True,
                         capture_output=True)

            if 'runtime' not in os.listdir():
                runtime_dir = '/'.join(__file__.split('/')[:-2])
                runtime_dir = os.path.join(runtime_dir, 'runtime')
                print(runtime_dir)
            else:
                runtime_dir = 'runtime'
            runtime_lib = f'{runtime_dir}/runtime_lib.c'

            # Use full runtime with static linking of C imports
            # Note: Using -O0 with selected optimizations (-finline-functions, -funroll-loops)
            # because -O2 and higher cause crashes with handwritten assembly code.
            # This appears to be a GCC issue with how it optimizes code that interacts
            # with inline assembly and calling conventions.
            # -fno-strict-aliasing: prevents type-punning issues
            # -fwrapv: ensures defined overflow behavior
            # -fno-tree-pre: prevents partial redundancy elimination that can break calling conventions
            # -fno-ipa-cp: prevents interprocedural constant propagation that assumes things about callers
            gcc_flags = [
                'gcc', obj_file, *c_obj_files, str(runtime_lib), '-o', exe_file,
                f'-I{runtime_dir}', '-O0', '-march=native', '-mtune=native',
                '-finline-functions', '-funroll-loops',
                '-fno-strict-aliasing', '-fwrapv', '-fno-tree-pre', '-fno-ipa-cp',
                '-ffunction-sections', '-fdata-sections',
                '-Wl,--gc-sections',
                '-lm', *link_libs, '-no-pie'
            ]

            # Build native binary executable
            subprocess.run(gcc_flags, check=True, capture_output=True)

            print(f"Built executable: {exe_file}")

            # Clean up intermediate files
            for c_obj in c_obj_files:
                os.remove(c_obj)
            os.remove(obj_file)
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
        print("  fr <file.fr> [-c] [-py|--python]")
        print("                                    -c: Force C runtime")
        print("                                   -py: Force Python runtime")
        print("  fr parse <file.fr> [--json]     - Parse to AST (binary or JSON)")
        print("  fr compile <file> [-o out.bc] - Compile to bytecode")
        print("  fr native <file.bc> [-o out] [-a|--asm] - Compile bytecode to native binary")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == 'parse':
        parse_cmd(args)
    elif cmd == 'compile':
        compile_cmd(args)
    elif cmd == 'native':
        native_cmd(args)
    elif cmd == 'encode':
        encode_cmd(args)
    elif cmd == 'decode':
        decode_cmd(args)
    elif os.path.exists(cmd):
        run_cmd(cmd, args)

    else:
        print(f"Unknown command: {cmd}")
        print("Run 'fr' without arguments for usage information.")
        sys.exit(1)

if __name__ == '__main__':
    main()
