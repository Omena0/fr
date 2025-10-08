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
        print("   or: fr compile <ast.bin|ast.json> [-o output.bc]")
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
    else:
        print(f"Error: Cannot compile {input_file} - unknown format")
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
        print("  fr compile <ast.json|ast.bin> [-o out.bc] - Compile AST to bytecode")
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
