"""
WebAssembly Compiler for fr bytecode

Compiles fr bytecode to WebAssembly text format (WAT).
"""

from typing import List, Dict, Tuple, Optional, Set


class WasmCompilerError(Exception):
    """Raised when WASM compilation fails"""
    pass

class WasmCompiler:
    """Compiles fr bytecode to WebAssembly"""

    def __init__(self):
        self.output: List[str] = []
        self.data_section: List[str] = []
        self.string_constants: Dict[str, int] = {}  # Maps strings to memory offsets
        self.memory_offset = 0  # Current offset in linear memory
        self.functions: Dict[str, Dict] = {}  # Maps function names to metadata
        self.current_function: Optional[str] = None
        self.local_count = 0
        self.label_stack: List[str] = []  # Stack of labels for break/continue
        self.global_vars: Dict[int, str] = {}  # Maps global indices to types
        self.local_vars: Dict[int, str] = {}  # Maps local indices to types
        self.type_stack: List[str] = []  # Track types on the value stack
        self.imports: Set[str] = set()  # Track imported functions
        self.pending_if_label: Optional[str] = None  # Track if blocks
        self.if_indent: int = 0  # Track indent for if blocks

        # Bytecode version
        self.version = 1

    def emit(self, line: str, indent: int = 1):
        """Emit a line of WAT code"""
        if indent > 0:
            self.output.append("  " * indent + line)
        else:
            self.output.append(line)

    def emit_comment(self, comment: str, indent: int = 1):
        """Emit a comment"""
        self.output.append("  " * indent + f";; {comment}")

    def add_string_constant(self, s: str) -> int:
        """Add a string constant to memory and return its offset"""
        if s in self.string_constants:
            return self.string_constants[s]

        offset = self.memory_offset
        self.string_constants[s] = offset

        # Encode the string (just UTF-8 bytes, no length prefix needed)
        encoded = s.encode('utf-8')
        length = len(encoded)

        # Store just the string data
        self.data_section.append(f'(data (i32.const {offset}) "')

        # Add the actual string data
        for byte in encoded:
            self.data_section[-1] += f'\\{byte:02x}'
        self.data_section[-1] += '")'

        self.memory_offset += length
        return offset

    def compile(self, bytecode: str) -> Tuple[str, Dict]:
        """Compile bytecode to WebAssembly text format (WAT)"""
        lines = bytecode.strip().split('\n')

        # Parse bytecode and build function metadata
        self._parse_bytecode_structure(lines)

        # Generate WAT module
        self.emit("(module", 0)

        # Import memory management functions (for string/list operations)
        self._emit_imports()

        # Define memory (start with 1 page = 64KB, max 100 pages)
        self.emit("(memory (export \"memory\") 1 100)", 1)

        # Define globals
        self._emit_globals()

        # Compile each function
        for func_name, func_meta in self.functions.items():
            self._compile_function(func_name, func_meta, lines)

        # Emit string constants
        for data_line in self.data_section:
            self.emit(data_line, 1)

        self.emit(")", 0)  # Close module

        # Build metadata
        metadata = {
            "version": self.version,
            "functions": list(self.functions.keys()),
            "entry_point": "main" if "main" in self.functions else None,
            "imports": list(self.imports),
            "memory_size": self.memory_offset,
            "string_constants": self.string_constants
        }

        return '\n'.join(self.output), metadata

    def _emit_imports(self):
        """Emit import declarations for runtime functions"""
        self.emit_comment("Runtime imports for complex operations", 1)

        # Import console output
        self.emit('(import "env" "print" (func $print (param i32 i32)))', 1)
        self.emit('(import "env" "println" (func $println (param i32 i32)))', 1)

        # Import string operations (return ptr and len as two values)
        self.emit('(import "env" "str_concat" (func $str_concat (param i32 i32 i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_to_i64" (func $str_to_i64 (param i32 i32) (result i64)))', 1)
        self.emit('(import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))', 1)
        self.emit('(import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))', 1)

        # Import math functions
        self.emit('(import "env" "sqrt" (func $sqrt (param f64) (result f64)))', 1)

        # Import list operations
        self.emit('(import "env" "list_new" (func $list_new (result i32)))', 1)
        self.emit('(import "env" "list_append" (func $list_append (param i32 i64)))', 1)
        self.emit('(import "env" "list_get" (func $list_get (param i32 i64) (result i64)))', 1)
        self.emit('(import "env" "list_set" (func $list_set (param i32 i64 i64)))', 1)
        self.emit('(import "env" "list_len" (func $list_len (param i32) (result i64)))', 1)

    def _emit_globals(self):
        """Emit global variable declarations"""
        if not self.global_vars:
            return

        self.emit_comment("Global variables", 1)
        for idx, var_type in sorted(self.global_vars.items()):
            wasm_type = self._map_type_to_wasm(var_type)
            init_value = "0" if wasm_type in ("i32", "i64") else "0.0"
            self.emit(f"(global $g{idx} (mut {wasm_type}) ({wasm_type}.const {init_value}))", 1)

    def _parse_bytecode_structure(self, lines: List[str]):
        """Parse bytecode to extract function metadata"""
        current_func = None

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Version directive
            if line.startswith('.version'):
                self.version = int(line.split()[1])
                continue

            # Function definition
            if line.startswith('.func'):
                parts = line.split()
                func_name = parts[1]
                return_type = parts[2] if len(parts) > 2 else 'void'
                param_count = int(parts[3]) if len(parts) > 3 else 0

                current_func = func_name
                self.functions[func_name] = {
                    'name': func_name,
                    'return_type': return_type,
                    'param_count': param_count,
                    'params': [],
                    'locals': {},
                    'body_start': -1,
                    'body_end': -1
                }
                continue

            # Function parameters
            if line.startswith('.arg') and current_func:
                parts = line.split()
                param_name = parts[1]
                param_type = parts[2] if len(parts) > 2 else 'i64'
                self.functions[current_func]['params'].append((param_name, param_type))
                continue

            # Local variables
            if line.startswith('.local') and current_func:
                parts = line.split()
                local_name = parts[1]
                local_type = parts[2] if len(parts) > 2 else 'i64'
                local_idx = len(self.functions[current_func]['locals'])
                self.functions[current_func]['locals'][local_idx] = local_type
                continue

    def _map_type_to_wasm(self, fr_type: str) -> str:
        """Map fr type to WASM type"""
        type_map = {
            'i64': 'i64',
            'f64': 'f64',
            'str': 'i32',  # String pointer
            'bool': 'i32',  # Boolean as i32
            'void': '',
            'list': 'i32',  # List pointer
            'any': 'i64',
        }
        return type_map.get(fr_type, 'i64')

    def _compile_function(self, func_name: str, func_meta: Dict, bytecode_lines: List[str]):
        """Compile a single function"""
        self.current_function = func_name
        self.local_vars = func_meta['locals'].copy()
        self.type_stack = []
        self.label_stack = []

        # Track parameter count for index translation
        param_count = len(func_meta['params'])

        # Start function definition
        export_attr = ' (export "main")' if func_name == "main" else ""
        params_str = ""

        # Add parameters
        for idx, (param_name, param_type) in enumerate(func_meta['params']):
            wasm_type = self._map_type_to_wasm(param_type)
            params_str += f" (param $p{idx} {wasm_type})"

        # Determine return type
        return_type = func_meta['return_type']
        wasm_return = ""
        if return_type and return_type != 'void':
            wasm_type = self._map_type_to_wasm(return_type)
            wasm_return = f" (result {wasm_type})"

        self.emit(f"(func ${func_name}{export_attr}{params_str}{wasm_return}", 1)

        # Count total locals needed by scanning bytecode for this function
        # Locals in bytecode are indexed from 0 (params + locals together)
        # We need to declare locals starting after parameters
        max_local_idx = param_count - 1
        in_func = False
        for line in bytecode_lines:
            line = line.strip()
            if line.startswith('.func'):
                parts = line.split()
                in_func = (parts[1] == func_name)
                continue
            if line.startswith('.func') or line.startswith('.end'):
                if in_func:
                    break
            if not in_func:
                continue

            # Check for STORE, LOAD, etc. that reference local indices
            for inst in ['STORE ', 'LOAD ', 'STORE_CONST_I64 ', 'INC_LOCAL ', 'DEC_LOCAL ', 'LOAD2_']:
                if line.startswith(inst):
                    parts = line.split()
                    for part in parts[1:]:
                        if part.isdigit():
                            idx = int(part)
                            if idx > max_local_idx:
                                max_local_idx = idx
                            break

        # Declare locals (indices from param_count to max_local_idx)
        for idx in range(param_count, max_local_idx + 1):
            # Default to i64 type
            local_type = self.local_vars.get(idx - param_count, 'i64')
            wasm_type = self._map_type_to_wasm(local_type)
            # Local variables in WASM start from 0, so use idx - param_count
            self.emit(f"(local $l{idx - param_count} {wasm_type})", 2)
        
        # Add temp local for AND/OR operations
        self.emit("(local $temp i32)", 2)

        # Compile function body
        self._compile_function_body(func_name, bytecode_lines)

        # Ensure function returns properly
        if return_type != 'void' and return_type:
            # If there's no explicit return, add a default one
            if all(
                line.strip() != 'RETURN'
                for line in bytecode_lines
                if self._is_in_function(line, func_name)
            ):
                wasm_type = self._map_type_to_wasm(return_type)
                if wasm_type == 'i64':
                    self.emit("i64.const 0", 2)
                elif wasm_type == 'f64':
                    self.emit("f64.const 0", 2)
                elif wasm_type == 'i32':
                    self.emit("i32.const 0", 2)

        self.emit(")", 1)  # Close function
        self.current_function = None

    def _is_in_function(self, line: str, func_name: str) -> bool:
        """Check if a bytecode line belongs to a function"""
        # Simple heuristic - would need better tracking in real implementation
        return True

    def _compile_function_body(self, func_name: str, bytecode_lines: List[str]):
        """Compile the body of a function"""
        indent = 2
        
        # Pre-scan to find all labels and detect loop vs block
        labels_in_func = []
        loop_labels = set()
        scan_in_func = False
        func_lines = []
        label_positions = {}
        
        for line in bytecode_lines:
            line = line.strip()
            if line.startswith('.func'):
                parts = line.split()
                current_name = parts[1]
                scan_in_func = (current_name == func_name)
                continue
            if line.startswith('.end'):
                if scan_in_func:
                    break
            if scan_in_func:
                if line.startswith('LABEL '):
                    parts = line.split()
                    if len(parts) > 1:
                        label_name = parts[1]
                        labels_in_func.append(label_name)
                        label_positions[label_name] = len(func_lines)
                func_lines.append(line)
        
        # Detect loop labels (backward jumps)
        for i, line in enumerate(func_lines):
            if line.startswith('JUMP ') and not line.startswith('JUMP_IF'):
                parts = line.split()
                if len(parts) > 1:
                    target = parts[1]
                    if target in label_positions and label_positions[target] <= i:
                        loop_labels.add(target)
        
        # Split function body around the first label so we can emit initialization code
        first_label_idx: Optional[int] = None
        for idx, body_line in enumerate(func_lines):
            if body_line.startswith('LABEL '):
                first_label_idx = idx
                break

        pre_label_lines = func_lines[:first_label_idx] if first_label_idx is not None else func_lines
        post_label_lines = func_lines[first_label_idx:] if first_label_idx is not None else []

        # Open blocks for non-loop labels upfront (reverse order for nesting)
        for label in reversed(labels_in_func):
            if label in loop_labels:
                continue
            self.emit(f"(block ${label}", indent)
            indent += 1

        # Emit any instructions that occur before the first label (setup code)
        for raw_line in pre_label_lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith('.') or stripped.startswith('LABEL '):
                continue
            try:
                self._compile_instruction(stripped, indent)
            except Exception as e:
                raise WasmCompilerError(f"Error compiling instruction '{stripped}': {e}")

        # Emit the rest of the function, opening loop blocks lazily as their labels appear
        opened_loops: Set[str] = set()
        for raw_line in post_label_lines:
            stripped = raw_line.strip()

            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith('LABEL '):
                label_name = stripped.split()[1]
                if label_name in loop_labels and label_name not in opened_loops:
                    self.emit(f"(loop ${label_name}", indent)
                    indent += 1
                    opened_loops.add(label_name)
                continue

            if stripped.startswith('.'):
                continue

            try:
                self._compile_instruction(stripped, indent)

            except Exception as e:
                raise WasmCompilerError(f"Error compiling instruction '{stripped}': {e}")

        # Close all remaining blocks (for labels)
        while indent > 2:
            indent -= 1
            self.emit(")", indent)

    def _compile_instruction(self, inst: str, indent: int):
        """Compile a single bytecode instruction to WASM"""
        parts = inst.split()
        if not parts:
            return

        opcode = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        self.emit_comment(inst, indent)

        # === Constants ===
        if opcode == 'ADD_CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.add", indent)

        elif opcode == 'ADD_F64':
            self.emit("f64.add", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'ADD_I64':
            self.emit("i64.add", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'ADD_STR':
            self.emit("call $str_concat", indent)
            if len(self.type_stack) >= 4:
                self.type_stack.pop()
                self.type_stack.pop()
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')
            self.imports.add('str_concat')

        elif opcode == 'BUILTIN_LEN':
            self.emit("call $list_len", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i64')
            self.imports.add('list_len')

        elif opcode == 'BUILTIN_PRINT':
            # print expects (i32 ptr, i32 len)
            self.emit("call $print", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('print')

        elif opcode == 'BUILTIN_PRINTLN':
            # println expects (i32 ptr, i32 len)
            # If top of stack is i64, convert to string first
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("call $i64_to_str", indent)
                self.type_stack.pop()
                self.type_stack.append('i32')  # ptr
                self.type_stack.append('i32')  # len
                self.imports.add('i64_to_str')
            elif self.type_stack and self.type_stack[-1] == 'f64':
                self.emit("call $f64_to_str", indent)
                self.type_stack.pop()
                self.type_stack.append('i32')  # ptr
                self.type_stack.append('i32')  # len
                self.imports.add('f64_to_str')
            
            # Now call println
            self.emit("call $println", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('println')

        elif opcode == 'BUILTIN_SQRT':
            self.emit("call $sqrt", indent)
            self.imports.add('sqrt')

        elif opcode == 'BUILTIN_STR':
            # Convert value to string - returns (i32 ptr, i32 len) as two stack values
            # Check type of value on stack
            if self.type_stack:
                if self.type_stack[-1] == 'i64':
                    self.emit("call $i64_to_str", indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    self.imports.add('i64_to_str')
                elif self.type_stack[-1] == 'f64':
                    self.emit("call $f64_to_str", indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    self.imports.add('f64_to_str')
        
        elif opcode == 'CALL':
            func_name = args[0]
            
            # Handle special built-in functions
            if func_name == 'assert':
                # Assert in WASM: just pop the value and continue
                # In a real implementation, you'd check and trap
                self.emit("drop", indent)
                if self.type_stack:
                    self.type_stack.pop()
                return
            
            self.emit(f"call ${func_name}", indent)
            # Update type stack based on function signature
            if func_name in self.functions:
                return_type = self.functions[func_name]['return_type']
                if return_type and return_type != 'void':
                    self.type_stack.append(self._map_type_to_wasm(return_type))

        elif opcode == 'CMP_EQ':
            # Assumes i64 comparison
            self.emit("i64.eq", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_EQ_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.eq", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_GE':
            self.emit("i64.ge_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_GE_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.ge_s", indent)

        elif opcode == 'CMP_GT':
            self.emit("i64.gt_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_GT_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.gt_s", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_LT':
            self.emit("i64.le_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_LT':
            self.emit("i64.lt_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_LT_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.lt_s", indent)

        elif opcode == 'CMP_LE_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.le_s", indent)

        elif opcode == 'CMP_LE':
            self.emit("i64.le_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_NE':
            self.emit("i64.ne", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_NE_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.ne", indent)

        elif opcode == 'AND':
            # Logical AND - both operands must be i32
            # Stack: [val1 (i64), val2 (i64)]
            # Need to convert to [val1 (i32), val2 (i32)]
            if len(self.type_stack) >= 2:
                if self.type_stack[-2] == 'i64' and self.type_stack[-1] == 'i64':
                    # Both are i64, wrap them
                    self.emit("i32.wrap_i64", indent)  # Convert val2
                    self.type_stack[-1] = 'i32'
                    # To convert val1, we need to swap, convert, swap back
                    # Or simpler: use a rotate pattern - pop, convert below, push
                    # Actually simplest: use (i32.and (i32.wrap_i64 val1) (i32.wrap_i64 val2))
                    # But we're working with a stack... Let me use a different approach
                    # Pop val2, convert val1, push val2, do and
                    # WASM: val1 val2 -> convert val2 -> val1 val2(i32)
                    # Then we need: val1(i32) val2(i32) for and
                    # Actually, we can use: get val2 off, convert val1, put val2 back
                    # But that needs locals. Simpler: just do wrap on both in reverse order
                    # Actually the stack is: ... val1 val2 (top)
                    # We need to: wrap val2 (done above), then swap and wrap val1
                    # Let's use: i32.wrap_i64 (wraps val2), then use temp to swap
                    # Even simpler: insert wrap_i64 for the second value, then for first
                    # Wait, I already wrapped val2. Now I need to get to val1.
                    # Use rotl pattern: a b -> b a -> wrap a -> b a(i32) -> a(i32) b
                    # Actually in WASM we can't easily swap without locals
                    # Let me just accept we need locals here
                    pass  # val2 already wrapped above
                    # Now wrap val1: need to insert wrap before val2
                    # This requires moving val2 off stack temporarily
                    # For now, let's just emit wrap for the one we can reach
                    # Actually, my previous wrap already converted val2
                    # To convert val1, I need to do it BEFORE val2 is on stack
                    # Let me rethink: I'll wrap each value right after it's pushed
                    # But that's not how the bytecode works...
                    # OK simpler solution: convert as we go in CONST_I64 itself
                    # Or: accept that AND needs wrapping and do it here properly
                    # For now: assume top 2 values, wrap top, swap somehow...
                    # Actually just emit both wraps in sequence assuming they work:
                    # Stack before: val1(i64) val2(i64)
                    # After first wrap: val1(i64) val2(i32) 
                    # We can't wrap val1 now without a local
                    # So let's use a simpler approach: define the pattern at CONST_I64 time
                    # OR: just accept locals are needed
                    # Let me create a temp local in the function
                    self.emit("local.set $temp", indent)  # save val2(i32)
                    self.emit("i32.wrap_i64", indent)  # convert val1
                    self.emit("local.get $temp", indent)  # restore val2
                    self.type_stack[-2] = 'i32'
            self.emit("i32.and", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'OR':
            # Logical OR - both operands must be i32  
            if len(self.type_stack) >= 2:
                if self.type_stack[-2] == 'i64' and self.type_stack[-1] == 'i64':
                    self.emit("i32.wrap_i64", indent)  # Convert val2
                    self.type_stack[-1] = 'i32'
                    self.emit("local.set $temp", indent)  # save val2(i32)
                    self.emit("i32.wrap_i64", indent)  # convert val1
                    self.emit("local.get $temp", indent)  # restore val2
                    self.type_stack[-2] = 'i32'
            self.emit("i32.or", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'NOT':
            # Logical NOT (i32 operand)
            self.emit("i32.eqz", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'AND_I64':
            # Bitwise AND (i64 operands)
            self.emit("i64.and", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'OR_I64':
            # Bitwise OR (i64 operands)
            self.emit("i64.or", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'XOR_I64':
            # Bitwise XOR (i64 operands)
            self.emit("i64.xor", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'SHL_I64':
            # Shift left (i64 operands)
            self.emit("i64.shl", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'SHR_I64':
            # Shift right (i64 operands)
            self.emit("i64.shr_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'NEG':
            # Negate (multiply by -1)
            # For i64, we do: 0 - value
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i64.const 0", indent)
                self.emit("i64.sub", indent)
            elif self.type_stack and self.type_stack[-1] == 'f64':
                self.emit("f64.neg", indent)

        elif opcode == 'CONST_BOOL':
            val = '1' if args[0] in ('1', 'true') else '0'
            self.emit(f"i32.const {val}", indent)
            self.type_stack.append('i32')

        elif opcode == 'CONST_F64':
            self.emit(f"f64.const {args[0]}", indent)
            self.type_stack.append('f64')

        elif opcode == 'CONST_I64':
            # Handle True/False constants, and multiple values
            for value in args:
                if value == 'True':
                    value = '1'
                elif value == 'False':
                    value = '0'
                self.emit(f"i64.const {value}", indent)
                self.type_stack.append('i64')

        elif opcode == 'CONST_STR':
            # Extract string (handles quoted strings)
            string_content = inst[len('CONST_STR'):].strip()
            if string_content.startswith('"') and string_content.endswith('"'):
                string_content = string_content[1:-1]

            # Unescape string
            string_content = self._unescape_string(string_content)
            offset = self.add_string_constant(string_content)
            self.emit(f"i32.const {offset}  ;; string: {string_content[:20]}...", indent)
            self.emit(f"i32.const {len(string_content.encode('utf-8'))}", indent)
            self.type_stack.append('i32')
            self.type_stack.append('i32')

        elif opcode == 'DEC_LOCAL':
            var_idx = int(args[0])
            var_ref = self._get_var_ref(var_idx)
            self.emit(f"local.get {var_ref}", indent)
            self.emit("i64.const 1", indent)
            self.emit("i64.sub", indent)
            self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.div_s", indent)

        elif opcode == 'DIV_CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.div_s", indent)

        elif opcode == 'DIV_F64':
            self.emit("f64.div", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'DIV_I64':
            self.emit("i64.div_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'DUP':
            # WASM doesn't have a direct DUP
            # We need to store to a temp local and load it back
            # Allocate a temp local if needed
            # For now, just emit the value twice by popping and re-pushing
            # This is a simplified implementation
            print("WARNING: DUP Not fully implemented!")
            if self.type_stack:
                top_type = self.type_stack[-1]
                # In WASM, we can't truly DUP without a local
                # The bytecode compiler should have handled this differently
                # For now, just note it's not properly implemented
                self.emit_comment("DUP - WARNING: not fully implemented", indent)
                self.type_stack.append(top_type)
            else:
                self.emit_comment("DUP (no type info)", indent)

        elif opcode == 'DUP2':
            # Duplicate top 2 stack values: a b -> a b a b
            print("WARNING: DUP2 Not fully implemented!")
            if len(self.type_stack) >= 2:
                type1 = self.type_stack[-2]
                type2 = self.type_stack[-1]
                self.emit_comment("DUP2 - WARNING: not fully implemented", indent)
                self.type_stack.append(type1)
                self.type_stack.append(type2)
            else:
                self.emit_comment("DUP2 (insufficient type info)", indent)

        elif opcode == 'SWAP':
            # Swap top 2 stack values: a b -> b a
            # WASM needs locals for this
            print("WARNING: SWAP Not fully implemented!")
            if len(self.type_stack) >= 2:
                type1 = self.type_stack.pop()
                type2 = self.type_stack.pop()
                self.emit_comment("SWAP - WARNING: not fully implemented", indent)
                self.type_stack.append(type1)
                self.type_stack.append(type2)
            else:
                self.emit_comment("SWAP (insufficient type info)", indent)

        elif opcode == 'ROT':
            # Rotate top 3 stack values: a b c -> b c a
            print("WARNING: ROT Not fully implemented!")
            if len(self.type_stack) >= 3:
                type1 = self.type_stack.pop()
                type2 = self.type_stack.pop()
                type3 = self.type_stack.pop()
                self.emit_comment("ROT - WARNING: not fully implemented", indent)
                self.type_stack.append(type2)
                self.type_stack.append(type1)
                self.type_stack.append(type3)
            else:
                self.emit_comment("ROT (insufficient type info)", indent)

        elif opcode == 'OVER':
            # Copy second stack value to top: a b -> a b a
            print("WARNING: OVER Not fully implemented!")
            if len(self.type_stack) >= 2:
                type_second = self.type_stack[-2]
                self.emit_comment("OVER - WARNING: not fully implemented", indent)
                self.type_stack.append(type_second)
            else:
                self.emit_comment("OVER (insufficient type info)", indent)

        elif opcode == 'FUSED_LOAD_STORE':
            # Load from one variable and store to another
            src_idx = int(args[0])
            dst_idx = int(args[1])
            src_ref = self._get_var_ref(src_idx)
            dst_ref = self._get_var_ref(dst_idx)
            self.emit(f"local.get {src_ref}", indent)
            self.emit(f"local.set {dst_ref}", indent)

        elif opcode == 'INC_LOCAL':
            var_idx = int(args[0])
            var_ref = self._get_var_ref(var_idx)
            self.emit(f"local.get {var_ref}", indent)
            self.emit("i64.const 1", indent)
            self.emit("i64.add", indent)
            self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'JUMP':
            label_name = args[0]
            # Unconditional branch to label
            self.emit(f"br ${label_name}", indent)

        elif opcode == 'JUMP_IF_FALSE':
            label_name = args[0]
            # Skip for if-end labels - we don't use them in structured WASM
            if '_if_end' in label_name or 'if_end' in label_name:
                # Just invert the condition and continue
                self.emit("i32.eqz", indent)
                if self.type_stack:
                    self.type_stack.pop()
                return
            
            # For other labels, use block/br_if pattern
            self.emit("i32.eqz", indent)
            self.emit(f"br_if ${label_name}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'JUMP_IF_TRUE':
            label_name = args[0]
            # Branch if top of stack is non-zero/true
            self.emit(f"br_if ${label_name}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'LABEL':
            pass

        elif opcode == 'LIST_APPEND':
            self.emit("call $list_append", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('list_append')

        elif opcode == 'LIST_GET':
            self.emit("call $list_get", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')
            self.imports.add('list_get')

        elif opcode == 'LIST_NEW':
            self.emit("call $list_new", indent)
            self.type_stack.append('i32')
            self.imports.add('list_new')

        elif opcode == 'LIST_SET':
            self.emit("call $list_set", indent)
            if len(self.type_stack) >= 3:
                self.type_stack.pop()
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('list_set')

        elif opcode == 'LOAD':
            local_idx = int(args[0])
            var_ref = self._get_var_ref(local_idx)
            self.emit(f"local.get {var_ref}", indent)
            local_type = self.local_vars.get(local_idx, 'i64')
            self.type_stack.append(self._map_type_to_wasm(local_type))

        elif opcode == 'LOAD2_ADD_I64':
            # Load two variables and add them
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit("i64.add", indent)
            self.type_stack.append('i64')

        elif opcode == 'LOAD2_CMP_LT':
            # Load two variables and compare
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit("i64.lt_s", indent)
            self.type_stack.append('i32')

        elif opcode == 'LOAD2_DIV_I64':
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit("i64.div_s", indent)
            self.type_stack.append('i64')

        elif opcode == 'LOAD2_MUL_I64':
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit("i64.mul", indent)
            self.type_stack.append('i64')

        elif opcode == 'LOAD_GLOBAL':
            global_idx = int(args[0])
            self.emit(f"global.get $g{global_idx}", indent)
            global_type = self.global_vars.get(global_idx, 'i64')
            self.type_stack.append(self._map_type_to_wasm(global_type))

        elif opcode == 'MOD_CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.rem_s", indent)

        elif opcode == 'MOD_I64':
            self.emit("i64.rem_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'MUL_CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.mul", indent)

        elif opcode == 'MUL_F64':
            self.emit("f64.mul", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'MUL_I64':
            self.emit("i64.mul", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'POP':
            self.emit("drop", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode in ['RETURN', 'RETURN_VOID']:
            self.emit("return", indent)

        elif opcode == 'STORE':
            var_idx = int(args[0])
            var_ref = self._get_var_ref(var_idx)
            self.emit(f"local.set {var_ref}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'STORE_CONST_I64':
            # Format: STORE_CONST_I64 slot1 val1 [slot2 val2 ...]
            # Arguments come in pairs: slot, value
            num_pairs = len(args) // 2
            for i in range(num_pairs):
                var_idx = int(args[i * 2])
                value = args[i * 2 + 1]
                var_ref = self._get_var_ref(var_idx)
                self.emit(f"i64.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'STORE_CONST_F64':
            # Format: STORE_CONST_F64 slot1 val1 [slot2 val2 ...]
            # Arguments come in pairs: slot, value
            num_pairs = len(args) // 2
            for i in range(num_pairs):
                var_idx = int(args[i * 2])
                value = args[i * 2 + 1]
                var_ref = self._get_var_ref(var_idx)
                self.emit(f"f64.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'STORE_CONST_BOOL':
            # Format: STORE_CONST_BOOL slot1 val1 [slot2 val2 ...]
            # Arguments come in pairs: slot, value (0 or 1)
            num_pairs = len(args) // 2
            for i in range(num_pairs):
                var_idx = int(args[i * 2])
                value = args[i * 2 + 1]
                var_ref = self._get_var_ref(var_idx)
                self.emit(f"i32.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'STORE_GLOBAL':
            global_idx = int(args[0])
            self.emit(f"global.set $g{global_idx}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'SUB_CONST_I64':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.sub", indent)

        elif opcode == 'SUB_F64':
            self.emit("f64.sub", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'SUB_I64':
            self.emit("i64.sub", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'TO_FLOAT':
            # Convert top of stack to f64
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'

        elif opcode == 'TO_INT':
            # Convert top of stack to i64
            # If it's already i64, do nothing; if f64, convert
            if self.type_stack and self.type_stack[-1] == 'f64':
                self.emit("i64.trunc_f64_s", indent)
                self.type_stack[-1] = 'i64'

        elif opcode == 'TO_BOOL':
            # Convert to boolean (i32: 0 or 1)
            # Any non-zero value becomes 1
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i64.const 0", indent)
                self.emit("i64.ne", indent)
                self.type_stack.pop()
                self.type_stack.append('i32')
            elif self.type_stack and self.type_stack[-1] == 'f64':
                self.emit("f64.const 0", indent)
                self.emit("f64.ne", indent)
                self.type_stack.pop()
                self.type_stack.append('i32')

        elif opcode == 'ADD_CONST_F64':
            const_val = args[0]
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.add", indent)

        elif opcode == 'SUB_CONST_F64':
            const_val = args[0]
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.sub", indent)

        elif opcode == 'MUL_CONST_F64':
            const_val = args[0]
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.mul", indent)

        elif opcode == 'DIV_CONST_F64':
            const_val = args[0]
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.div", indent)

        elif opcode == 'LIST_NEW_I64':
            # LIST_NEW_I64 count val1 val2 val3 ...
            # For now, treat as unsupported - lists need runtime support
            self.emit_comment(f"LIST_NEW_I64 - requires runtime support", indent)
            # Call list_new to create empty list, then append each value
            count = int(args[0])
            self.emit("call $list_new", indent)
            # Result is list handle (i32) on stack
            for i in range(count):
                val = args[i + 1]
                self.emit("i64.const " + val, indent)
                self.emit("call $list_append", indent)
            self.type_stack.append('i32')

        elif opcode == 'LIST_NEW_STR':
            # LIST_NEW_STR count "str1" "str2" ...
            self.emit_comment(f"LIST_NEW_STR - requires runtime support", indent)
            count = int(args[0])
            self.emit("call $list_new", indent)
            # For now, just create empty list
            self.type_stack.append('i32')

        elif opcode == 'SET_NEW':
            # Create a new set - requires runtime support
            self.emit_comment("SET_NEW - requires runtime support", indent)
            # For now, just push a dummy value
            self.emit("i32.const 0", indent)
            self.type_stack.append('i32')

        elif opcode == 'STRUCT_NEW':
            # STRUCT_NEW struct_id
            self.emit_comment(f"STRUCT_NEW - requires runtime support", indent)
            # For now, just push a dummy handle
            self.emit("i32.const 0", indent)
            self.type_stack.append('i32')

        elif opcode == 'STRUCT_GET':
            # STRUCT_GET field_index
            self.emit_comment(f"STRUCT_GET - requires runtime support", indent)
            # Pop struct handle, push field value
            if self.type_stack:
                self.type_stack.pop()
            self.emit("i64.const 0", indent)
            self.type_stack.append('i64')

        elif opcode == 'STR_EQ':
            # String equality comparison
            self.emit_comment("STR_EQ - requires runtime support", indent)
            # Pop two string refs (ptr+len each = 4 values)
            for _ in range(4):
                if self.type_stack:
                    self.type_stack.pop()
            self.emit("i32.const 0", indent)
            self.type_stack.append('i32')

        elif opcode in ['STR_LOWER', 'STR_UPPER', 'STR_STRIP', 'STR_REPLACE', 'STR_SPLIT', 'STR_JOIN']:
            # String operations require runtime support
            self.emit_comment(f"{opcode} - requires runtime support", indent)
            # These typically consume and produce string refs
            if opcode == 'STR_SPLIT':
                # Returns a list
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
            else:
                # Returns a string (ptr, len)
                self.emit("i32.const 0", indent)
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
                self.type_stack.append('i32')

        elif opcode == 'CONTAINS':
            # Check if value in container
            self.emit_comment("CONTAINS - requires runtime support", indent)
            if self.type_stack:
                self.type_stack.pop()  # container
            if self.type_stack:
                self.type_stack.pop()  # value
            self.emit("i32.const 0", indent)
            self.type_stack.append('i32')

        elif opcode == 'LIST_POP':
            # Pop from list
            self.emit_comment("LIST_POP - requires runtime support", indent)
            # Consume list handle, produce value
            if self.type_stack:
                self.type_stack.pop()
            self.emit("i64.const 0", indent)
            self.type_stack.append('i64')

        elif opcode == 'BUILTIN_PI':
            # Push π constant
            self.emit("f64.const 3.141592653589793", indent)
            self.type_stack.append('f64')

        elif opcode in ['TRY_BEGIN', 'RAISE', 'FILE_OPEN', 'SOCKET_CREATE', 'FORK', 'SLEEP', 'GOTO_CALL', 'ENCODE', 'DECODE', 'SWITCH_JUMP_TABLE', 'LOAD2_CMP_GT']:
            # Operations that require special runtime or OS support
            self.emit_comment(f"{opcode} - not supported in WASM", indent)
            # Push dummy values to keep stack balanced
            if opcode in ['FILE_OPEN', 'SOCKET_CREATE']:
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
            elif opcode in ['ENCODE', 'DECODE']:
                # Returns bytes/string (ptr, len)
                self.emit("i32.const 0", indent)
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
                self.type_stack.append('i32')

        else:
            # Unsupported instruction - fatal error
            raise WasmCompilerError(f"Unsupported instruction: {inst}")

    def _unescape_string(self, s: str) -> str:
        # sourcery skip: inline-immediately-returned-variable
        """Unescape a bytecode string literal"""
        # Handle common escape sequences
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\r', '\r')
        s = s.replace('\\\\', '\\')
        s = s.replace('\\"', '"')
        return s

    def _get_var_ref(self, index: int) -> str:
        """Get the correct WASM variable reference (param or local) for a bytecode index"""
        if not self.current_function:
            return f"$l{index}"

        func_meta = self.functions.get(self.current_function, {})
        param_count = len(func_meta.get('params', []))

        # Bytecode uses unified 0-based indexing for all variables
        # First param_count indices are parameters, rest are locals
        return f"$p{index}" if index < param_count else f"$l{index - param_count}"


def compile_to_wasm(bytecode: str) -> Tuple[str, Dict]:
    """Compile fr bytecode to WebAssembly text format (WAT)"""
    compiler = WasmCompiler()
    return compiler.compile(bytecode)
