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
        self.struct_type_stack: List[Optional[int]] = []  # Track struct IDs on the value stack (parallel to type_stack)
        self.imports: Set[str] = set()  # Track imported functions
        self.pending_if_label: Optional[str] = None  # Track if blocks
        self.if_indent: int = 0  # Track indent for if blocks
        self.struct_defs: Dict[int, Dict] = {}  # Maps struct ID to struct definition
        self.local_value_types: Dict[int, str] = {}  # Track what type of value each local holds (set, list, bool)

        # Bytecode version
        self.version = 1

        # Allocate memory for struct storage (start after string constants)
        self.heap_offset = 1024  # Start heap at 1KB

    def push_type(self, wasm_type: str, struct_id: Optional[int] = None):
        """Push a type onto the type stack and track struct ID if applicable"""
        self.type_stack.append(wasm_type)
        self.struct_type_stack.append(struct_id)

    def pop_type(self) -> Tuple[Optional[str], Optional[int]]:
        """Pop a type from the type stack and return (type, struct_id)"""
        wasm_type = self.type_stack.pop() if self.type_stack else None
        # Auto-fill struct_type_stack if it's out of sync
        while len(self.struct_type_stack) < len(self.type_stack):
            self.struct_type_stack.append(None)
        struct_id = self.struct_type_stack.pop() if self.struct_type_stack else None
        return wasm_type, struct_id

    def get_struct_id(self) -> Optional[int]:
        """Peek at the struct ID on top of struct_type_stack without popping"""
        # Auto-fill if needed
        while len(self.struct_type_stack) < len(self.type_stack):
            self.struct_type_stack.append(None)
        return self.struct_type_stack[-1] if self.struct_type_stack else None

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
        self.emit('(import "env" "str_to_f64" (func $str_to_f64 (param i32 i32) (result f64)))', 1)
        self.emit('(import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))', 1)
        self.emit('(import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))', 1)
        self.emit('(import "env" "bool_to_str" (func $bool_to_str (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "list_to_str" (func $list_to_str (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "set_to_str" (func $set_to_str (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_upper" (func $str_upper (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_lower" (func $str_lower (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_strip" (func $str_strip (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_replace" (func $str_replace (param i32 i32 i32 i32 i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_get" (func $str_get (param i32 i32 i64) (result i32 i32)))', 1)
        self.emit('(import "env" "str_contains" (func $str_contains (param i32 i32 i32 i32) (result i32)))', 1)
        self.emit('(import "env" "str_join" (func $str_join (param i32 i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_split" (func $str_split (param i32 i32 i32 i32) (result i32)))', 1)

        # Import math functions
        self.emit('(import "env" "sqrt" (func $sqrt (param f64) (result f64)))', 1)

        # Import list operations
        self.emit('(import "env" "list_new" (func $list_new (result i32)))', 1)
        self.emit('(import "env" "list_append" (func $list_append (param i32 i64) (result i32)))', 1)
        self.emit('(import "env" "list_get" (func $list_get (param i32 i64) (result i64)))', 1)
        self.emit('(import "env" "list_set" (func $list_set (param i32 i64 i64) (result i32)))', 1)
        self.emit('(import "env" "list_len" (func $list_len (param i32) (result i64)))', 1)
        self.emit('(import "env" "list_pop" (func $list_pop (param i32) (result i32 i64)))', 1)

        # Set operations
        self.emit('(import "env" "set_new" (func $set_new (result i32)))', 1)
        self.emit('(import "env" "set_add" (func $set_add (param i32 i64) (result i32)))', 1)
        self.emit('(import "env" "set_remove" (func $set_remove (param i32 i64) (result i32)))', 1)
        self.emit('(import "env" "set_contains" (func $set_contains (param i32 i64) (result i32)))', 1)
        self.emit('(import "env" "set_len" (func $set_len (param i32) (result i64)))', 1)

        # Math functions
        self.emit('(import "env" "round_f64" (func $round_f64 (param f64) (result f64)))', 1)
        self.emit('(import "env" "floor_f64" (func $floor_f64 (param f64) (result f64)))', 1)
        self.emit('(import "env" "ceil_f64" (func $ceil_f64 (param f64) (result f64)))', 1)

        # File I/O
        self.emit('(import "env" "file_open" (func $file_open (param i32 i32 i32 i32) (result i32)))', 1)
        self.emit('(import "env" "file_read" (func $file_read (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "file_write" (func $file_write (param i32 i32 i32)))', 1)
        self.emit('(import "env" "file_close" (func $file_close (param i32)))', 1)

        # Process control
        self.emit('(import "env" "exit_process" (func $exit_process (param i32)))', 1)

    def _emit_globals(self):
        """Emit global variable declarations"""
        # Always emit heap pointer for struct allocation
        self.emit_comment("Heap pointer for struct allocation", 1)
        self.emit(f"(global $heap_ptr (mut i32) (i32.const {self.heap_offset}))", 1)

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

            # Struct definition: .struct <id> <field_count> <size> <field_names...> <field_types...>
            if line.startswith('.struct '):
                parts = line.split()
                struct_id = int(parts[1])
                field_count = int(parts[2])
                size = int(parts[3])
                field_names = parts[4:4+field_count]
                field_types = parts[4+field_count:4+field_count*2]

                self.struct_defs[struct_id] = {
                    'id': struct_id,
                    'field_count': field_count,
                    'size': size,
                    'field_names': field_names,
                    'field_types': field_types,
                }
                continue

            # Struct type mapping: .struct_type <name> <id>
            if line.startswith('.struct_type '):
                parts = line.split()
                struct_name = parts[1]
                struct_id = int(parts[2])
                if struct_id in self.struct_defs:
                    self.struct_defs[struct_id]['name'] = struct_name
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
        # Handle struct types (e.g., "struct:Point")
        if fr_type.startswith('struct:'):
            return 'i32'  # Structs are represented as pointers
        return type_map.get(fr_type, 'i64')

    def _compile_function(self, func_name: str, func_meta: Dict, bytecode_lines: List[str]):
        """Compile a single function"""
        self.current_function = func_name
        self.local_vars = func_meta['locals'].copy()
        self.type_stack = []
        self.struct_type_stack = []
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

        # Count total locals needed - we already have them from parsing!
        num_locals = len(func_meta['locals'])
        max_local_idx = param_count + num_locals - 1
        in_func = False

        # Pre-scan to detect list operations and update types
        local_inferred_types = {}  # Maps absolute index to inferred type

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
            for inst in ['STORE ', 'LOAD ', 'STORE_CONST_I64 ', 'INC_LOCAL ', 'DEC_LOCAL ', 'LOAD2_', 'FUSED_LOAD_STORE ']:
                if line.startswith(inst):
                    parts = line.split()
                    for part in parts[1:]:
                        if part.isdigit():
                            idx = int(part)
                            if idx > max_local_idx:
                                max_local_idx = idx

            # Detect list operations: LIST_NEW* followed by STORE means the var is a list (i32)
            if line.startswith('LIST_NEW'):
                # Next non-comment line should be STORE
                # This is a simplification - we'd need better tracking
                pass

        # Second pass: track stack operations to infer types
        type_stack_sim = []
        value_type_tracker = {}  # Track what type of value each stack position/local holds
        for line in bytecode_lines:
            line = line.strip()
            if line.startswith('.func'):
                parts = line.split()
                in_func = (parts[1] == func_name)
                type_stack_sim = []
                continue
            if line.startswith('.func') or line.startswith('.end'):
                if in_func:
                    break
            if not in_func:
                continue

            parts = line.split()
            if not parts:
                continue
            opcode = parts[0]

            # Simulate type stack for key operations
            if opcode == 'LIST_NEW' or opcode == 'LIST_NEW_I64' or opcode == 'LIST_NEW_STR':
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'list'
            elif opcode == 'SET_NEW':
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'set'
            elif opcode == 'STRUCT_NEW':
                # STRUCT_NEW pops field values and pushes struct pointer
                struct_id = None
                if len(parts) > 1:
                    struct_id = int(parts[1])
                    if struct_id in self.struct_defs:
                        field_count = self.struct_defs[struct_id]['field_count']
                        # Pop field values
                        for _ in range(field_count):
                            if type_stack_sim:
                                type_stack_sim.pop()
                type_stack_sim.append('i32')
                # Track which struct type this is
                value_type_tracker[len(type_stack_sim) - 1] = f'struct:{struct_id}'
            elif opcode == 'STRUCT_GET':
                # STRUCT_GET pops struct pointer, pushes field value
                # The type depends on the struct field type
                if len(parts) > 1:
                    field_idx = int(parts[1])
                    # Try to determine struct type from stack
                    struct_type = None
                    if type_stack_sim and len(type_stack_sim) - 1 in value_type_tracker:
                        vt = value_type_tracker[len(type_stack_sim) - 1]
                        if vt and vt.startswith('struct:'):
                            struct_id = int(vt.split(':')[1])
                            if struct_id in self.struct_defs:
                                struct_type = struct_id

                    if type_stack_sim:
                        type_stack_sim.pop()  # pop struct ptr

                    # Push field value based on type
                    if struct_type is not None:
                        field_types = self.struct_defs[struct_type]['field_types']
                        if field_idx < len(field_types):
                            field_type = field_types[field_idx]
                            if field_type == 'float':
                                type_stack_sim.append('f64')
                            elif field_type == 'str':
                                type_stack_sim.append('i32')  # ptr
                                type_stack_sim.append('i32')  # len
                                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                                value_type_tracker[len(type_stack_sim) - 1] = 'str'
                            elif field_type == 'bool':
                                type_stack_sim.append('i32')
                            else:  # int or default
                                type_stack_sim.append('i64')
                        else:
                            type_stack_sim.append('i64')  # default
                    else:
                        type_stack_sim.append('i64')  # default when we don't know struct type
                else:
                    if type_stack_sim:
                        type_stack_sim.pop()
                    type_stack_sim.append('i64')
            elif opcode == 'STRUCT_SET':
                # STRUCT_SET pops value and struct pointer, pushes struct pointer
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # struct
                type_stack_sim.append('i32')  # return modified struct
            elif opcode == 'CONST_I64':
                # CONST_I64 can push multiple values (e.g., CONST_I64 0 1 pushes 0 then 1)
                num_values = len(parts) - 1
                for _ in range(num_values):
                    type_stack_sim.append('i64')
            elif opcode == 'CONST_STR':
                # CONST_STR pushes ptr and len (two i32 values) representing a string
                type_stack_sim.append('i32')  # ptr
                type_stack_sim.append('i32')  # len
                # Mark this as a string type
                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                value_type_tracker[len(type_stack_sim) - 1] = 'str'
            elif opcode == 'LOAD2_ADD_I64' or opcode == 'LIST_LEN':
                type_stack_sim.append('i64')
            elif opcode == 'BUILTIN_LEN':
                # BUILTIN_LEN consumes a list/set/string and returns i64
                if len(type_stack_sim) >= 2 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32':
                    # String: pop ptr and len
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                else:
                    # List or Set: pop the pointer
                    if type_stack_sim:
                        type_stack_sim.pop()
                type_stack_sim.append('i64')
            elif opcode == 'LIST_GET':
                # LIST_GET can return i64 (for list) or (i32, i32) for string
                # We need to check what's on the stack
                # If stack has string type markers, result will be string
                # For now, we'll handle this specially in STORE
                if len(type_stack_sim) >= 3 and (len(type_stack_sim) - 3 in value_type_tracker and value_type_tracker[len(type_stack_sim) - 3] == 'str'):
                    type_stack_sim.pop()  # index
                    type_stack_sim.pop()  # len
                    type_stack_sim.pop()  # ptr

                    type_stack_sim.append('i32')  # char ptr
                    type_stack_sim.append('i32')  # char len
                    value_type_tracker[len(type_stack_sim) - 2] = 'str'
                    value_type_tracker[len(type_stack_sim) - 1] = 'str'

                else:
                    # List indexing: assume i64 result
                    type_stack_sim.append('i64')

            elif opcode == 'CONST_F64':
                type_stack_sim.append('f64')

            elif opcode == 'LOAD' and len(parts) > 1:
                # LOAD can load multiple locals: LOAD 0 2 means load 0 then 2
                for part in parts[1:]:
                    if part.isdigit():
                        idx = int(part)
                        if idx in local_inferred_types:
                            local_type = local_inferred_types[idx]

                            if local_type == 'str':
                                # String: push ptr and len
                                type_stack_sim.append('i32')  # ptr
                                type_stack_sim.append('i32')  # len
                                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                                value_type_tracker[len(type_stack_sim) - 1] = 'str'

                            else:
                                type_stack_sim.append(local_type)

                        else:
                            type_stack_sim.append('i64')  # default

            elif opcode == 'STORE' and len(parts) > 1 and parts[1].isdigit():
                idx = int(parts[1])

                if type_stack_sim:
                    # Check if we're storing a string (two i32 values)
                    if (len(type_stack_sim) >= 2 and
                        type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32' and
                        len(type_stack_sim) - 1 in value_type_tracker and value_type_tracker[len(type_stack_sim) - 1] == 'str'):
                        # String: mark local as str type
                        local_inferred_types[idx] = 'str'
                        type_stack_sim.pop()  # len

                    else:
                        local_inferred_types[idx] = type_stack_sim[-1]
                        # Track the value type (set, list, bool, etc.)
                        stack_pos = len(type_stack_sim) - 1
                        if stack_pos in value_type_tracker:
                            self.local_value_types[idx] = value_type_tracker[stack_pos]

                    type_stack_sim.pop()  # ptr

            elif opcode == 'LIST_APPEND':
                # LIST_APPEND pops value and list, pushes list
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # list
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'list'

            elif opcode == 'SET_ADD' or opcode == 'SET_REMOVE':
                # SET_ADD/SET_REMOVE pops value and set, pushes set
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # set
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'set'

            elif opcode == 'SET_CONTAINS':
                # SET_CONTAINS pops value and set, pushes bool (i32)
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # set
                type_stack_sim.append('i32')  # result

            elif opcode == 'LIST_SET':
                # LIST_SET pops value, index, list, pushes list
                if len(type_stack_sim) >= 3:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # index
                    type_stack_sim.pop()  # list
                type_stack_sim.append('i32')  # result

            elif opcode == 'LIST_POP':
                # LIST_POP pops list, pushes list and value
                if type_stack_sim:
                    type_stack_sim.pop()  # list
                type_stack_sim.append('i32')  # list
                type_stack_sim.append('i64')  # value

            elif opcode == 'POP':
                if type_stack_sim:
                    type_stack_sim.pop()

        # Update local_vars with inferred types (but don't overwrite explicit types like 'str')
        for idx, inferred_type in local_inferred_types.items():
            if idx >= param_count:
                rel_idx = idx - param_count
                # Only update if we don't already have an explicit type
                if rel_idx not in self.local_vars or self.local_vars[rel_idx] == 'i64':
                    self.local_vars[rel_idx] = inferred_type

        # Declare locals (indices from param_count to max_local_idx)
        for idx in range(param_count, max_local_idx + 1):
            # Default to i64 type
            local_type = self.local_vars.get(idx - param_count, 'i64')
            # Check if this is already a WASM type (from type inference)
            if local_type in ['i32', 'i64', 'f64']:
                wasm_type = local_type

            else:
                wasm_type = self._map_type_to_wasm(local_type)

            # Local variables in WASM start from 0, so use idx - param_count
            self.emit(f"(local $l{idx - param_count} {wasm_type})", 2)

            # If this is a string, we need an extra local for the length
            if local_type == 'str':
                self.emit(f"(local $l{idx - param_count}_len i32)", 2)

        # Add temp locals for operations
        self.emit("(local $temp i32)", 2)
        self.emit("(local $temp_i64 i64)", 2)
        self.emit("(local $temp_f64 f64)", 2)

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
        """Compile the body of a function with proper WASM block nesting"""
        indent = 2

        # Initialize tracking for i32 value types (list/set)
        self._last_i32_source = None

        # ===== PASS 1: Scan and analyze control flow =====
        scan_in_func = False
        func_lines = []
        label_positions = {}
        labels_in_func = []

        # Collect all lines and label positions
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

        # Detect all jumps and classify them as forward or backward
        forward_jumps = {}  # Maps jump position -> target label (for forward jumps)
        backward_jumps = {}  # Maps jump position -> target label (for backward jumps)

        for i, line in enumerate(func_lines):
            target = None
            if line.startswith('JUMP_IF_FALSE ') or line.startswith('JUMP_IF_TRUE ') or line.startswith('JUMP '):
                parts = line.split()
                if len(parts) > 1:
                    target = parts[1]

                    # Classify as forward or backward jump
                    if target in label_positions:
                        target_pos = label_positions[target]
                        if target_pos > i:
                            forward_jumps[i] = target
                        elif target_pos <= i:
                            backward_jumps[i] = target

        # Identify loop structures by analyzing backward jumps and loop naming
        loop_structures = {}  # Maps loop_start -> (loop_end, loop_continue)
        for label in labels_in_func:
            if label.startswith('for_start') or label.startswith('forin_start') or label.startswith('while_start'):
                start_pos = label_positions[label]
                end_label = None
                continue_label = None

                # Look for JUMP_IF_FALSE after the start label (this is the loop exit condition)
                for i in range(start_pos, min(start_pos + 10, len(func_lines))):
                    line = func_lines[i]
                    if line.startswith('JUMP_IF_FALSE '):
                        parts = line.split()
                        if len(parts) > 1:
                            end_label = parts[1]
                            break

                # Look for continue label between start and end
                if end_label:
                    end_pos = label_positions.get(end_label, len(func_lines))
                    for lbl in labels_in_func:
                        lbl_pos = label_positions.get(lbl, 0)
                        if (lbl.startswith('for_continue') or lbl.startswith('forin_continue') or lbl.startswith('while_continue')) and start_pos < lbl_pos < end_pos:
                            continue_label = lbl
                            break
                    loop_structures[label] = (end_label, continue_label)

        # Determine which labels are inside loops vs outside
        loop_ranges = {}  # Maps loop_start -> (start_pos, end_pos)
        for loop_start, (loop_end, _) in loop_structures.items():
            start_pos = label_positions[loop_start]
            end_pos = label_positions.get(loop_end, len(func_lines))
            loop_ranges[loop_start] = (start_pos, end_pos)

        def is_inside_loop(pos):
            """Check if a position is inside any loop"""
            for start_pos, end_pos in loop_ranges.values():
                if start_pos < pos < end_pos:
                    return True
            return False

        # Identify which labels need blocks (forward jump targets not related to loops)
        loop_end_labels = [end for end, _ in loop_structures.values()]
        labels_needing_blocks_outside_loops = set()  # Labels that need blocks opened at function start
        labels_needing_blocks_inside_loops = set()   # Labels that need blocks opened inside loops

        for target in forward_jumps.values():
            # Don't create blocks for loop structures - they're handled specially
            if target not in loop_structures and target not in loop_end_labels:
                target_pos = label_positions[target]
                if is_inside_loop(target_pos):
                    labels_needing_blocks_inside_loops.add(target)
                else:
                    labels_needing_blocks_outside_loops.add(target)

        # ===== PASS 2: Generate WASM code with proper block structure =====

        # Split function body around the first label
        first_label_idx = None
        for idx, body_line in enumerate(func_lines):
            if body_line.startswith('LABEL '):
                first_label_idx = idx
                break

        pre_label_lines = func_lines[:first_label_idx] if first_label_idx is not None else func_lines
        post_label_lines = func_lines[first_label_idx:] if first_label_idx is not None else []

        # Open blocks for labels that are outside loops (at function level)
        blocks_to_open_upfront = sorted(labels_needing_blocks_outside_loops,
                                       key=lambda x: label_positions.get(x, 0),
                                       reverse=True)

        active_blocks = []  # Stack of (label, is_loop, indent_level)
        for label in blocks_to_open_upfront:
            self.emit(f"(block ${label}", indent)
            indent += 1
            active_blocks.append((label, False, indent))

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

        current_loop = None
        loop_internal_blocks = []  # Track blocks opened inside current loop

        for i, raw_line in enumerate(post_label_lines):
            stripped = raw_line.strip()

            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith('.'):
                continue

            # Handle LABEL
            if stripped.startswith('LABEL '):
                label_name = stripped.split()[1]

                # Close any blocks that end at this label
                blocks_to_close = []
                for j, (lbl, is_loop, _) in enumerate(active_blocks):
                    if lbl == label_name:
                        blocks_to_close.append(j)

                # Close in reverse order (from innermost to outermost)
                for j in reversed(blocks_to_close):
                    lbl, is_loop, _ = active_blocks.pop(j)
                    indent -= 1
                    self.emit(")", indent)
                    if is_loop:
                        current_loop = None
                        loop_internal_blocks = []

                # Check if this is a loop start label
                if label_name in loop_structures:
                    end_label, continue_label = loop_structures[label_name]

                    # Open blocks for labels inside this loop first
                    loop_start_pos = label_positions[label_name]
                    loop_end_pos = label_positions.get(end_label, len(func_lines))

                    # Find labels inside this loop that need blocks
                    labels_in_this_loop = []
                    for lbl in labels_needing_blocks_inside_loops:
                        lbl_pos = label_positions[lbl]
                        if loop_start_pos < lbl_pos < loop_end_pos:
                            labels_in_this_loop.append(lbl)

                    # Open blocks for these labels (in reverse position order for proper nesting)
                    labels_in_this_loop.sort(key=lambda x: label_positions[x], reverse=True)
                    for lbl in labels_in_this_loop:
                        self.emit(f"(block ${lbl}", indent)
                        indent += 1
                        active_blocks.append((lbl, False, indent))
                        loop_internal_blocks.append(lbl)

                    # Open outer block for loop exit
                    self.emit(f"(block ${end_label}", indent)
                    indent += 1
                    active_blocks.append((end_label, False, indent))
                    # Open the loop block
                    self.emit(f"(loop ${label_name}", indent)
                    indent += 1
                    active_blocks.append((label_name, True, indent))
                    current_loop = (label_name, end_label, continue_label)
                    continue

                # Check if this is a loop end label
                if current_loop and label_name == current_loop[1]:
                    # Close the loop block first
                    for j in range(len(active_blocks) - 1, -1, -1):
                        if active_blocks[j][0] == current_loop[0]:
                            active_blocks.pop(j)
                            indent -= 1
                            self.emit(")", indent)
                            break
                    # Close the end block
                    for j in range(len(active_blocks) - 1, -1, -1):
                        if active_blocks[j][0] == label_name:
                            active_blocks.pop(j)
                            indent -= 1
                            self.emit(")", indent)
                            break
                    # Close any loop internal blocks that are still open
                    for lbl in loop_internal_blocks:
                        for j in range(len(active_blocks) - 1, -1, -1):
                            if active_blocks[j][0] == lbl:
                                active_blocks.pop(j)
                                indent -= 1
                                self.emit(")", indent)
                                break
                    current_loop = None
                    loop_internal_blocks = []
                    continue

                # Check if this is a continue label - just a marker
                if current_loop and label_name == current_loop[2]:
                    continue

                continue

            try:
                self._compile_instruction(stripped, indent)
            except Exception as e:
                raise WasmCompilerError(f"Error compiling instruction '{stripped}': {e}")

        # Close all remaining blocks
        while active_blocks:
            _, _, _ = active_blocks.pop()
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
            # Check if we have a string (two i32 values) or a list/set (one i32 value)
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String: (ptr, len) - convert len to i64 and discard ptr
                self.emit_comment("String length: swap and convert i32 len to i64", indent)
                # Stack: ... ptr len
                # We need to convert len to i64 and drop ptr
                # Use local.set to save len, drop ptr, then convert
                self.emit("local.set $temp", indent)  # save len
                self.emit("drop", indent)  # drop ptr
                self.emit("local.get $temp", indent)  # get len back
                self.emit("i64.extend_i32_u", indent)  # convert to i64
                self.type_stack.pop()  # remove i32 len
                self.type_stack.pop()  # remove i32 ptr
                self.type_stack.append('i64')  # push i64 len
            else:
                # List or Set: check _last_i32_source to determine which
                if hasattr(self, '_last_i32_source') and self._last_i32_source == 'set':
                    self.emit("call $set_len", indent)
                    self.imports.add('set_len')
                else:
                    # Default to list
                    self.emit("call $list_len", indent)
                    self.imports.add('list_len')
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('i64')

        elif opcode == 'BUILTIN_PRINT':
            # print expects (i32 ptr, i32 len)
            self.emit("call $print", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('print')

        elif opcode == 'BUILTIN_PRINTLN':
            # println expects (i32 ptr, i32 len)
            # If stack already has (i32, i32), it's already a string - don't convert
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # Already a string (ptr, len)
                pass
            # If top of stack is i64, convert to string first
            elif self.type_stack and self.type_stack[-1] == 'i64':
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
            elif self.type_stack and self.type_stack[-1] == 'i32':
                # i32 could be a list, set, or boolean - check value type tracking
                if hasattr(self, '_last_i32_source') and self._last_i32_source:
                    if self._last_i32_source == 'list':
                        self.emit("call $list_to_str", indent)
                        self.imports.add('list_to_str')
                        self.type_stack.pop()
                        self.type_stack.append('i32')  # ptr
                        self.type_stack.append('i32')  # len
                    elif self._last_i32_source == 'set':
                        self.emit("call $set_to_str", indent)
                        self.imports.add('set_to_str')
                        self.type_stack.pop()
                        self.type_stack.append('i32')  # ptr
                        self.type_stack.append('i32')  # len
                    else:
                        # Boolean or other i32 - convert to string
                        self.emit("call $bool_to_str", indent)
                        self.imports.add('bool_to_str')
                        self.type_stack.pop()
                        self.type_stack.append('i32')  # ptr
                        self.type_stack.append('i32')  # len
                    # Clear the tracking after conversion
                    self._last_i32_source = None
                else:
                    # Default: treat as boolean
                    self.emit("call $bool_to_str", indent)
                    self.imports.add('bool_to_str')
                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len

            # Now call println
            self.emit("call $println", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('println')

        elif opcode == 'BUILTIN_SQRT':
            self.emit("call $sqrt", indent)
            self.imports.add('sqrt')

        elif opcode == 'BUILTIN_ROUND':
            self.emit("call $round_f64", indent)
            self.imports.add('round_f64')
            # Type stays as f64

        elif opcode == 'BUILTIN_FLOOR':
            self.emit("call $floor_f64", indent)
            self.imports.add('floor_f64')
            # Type stays as f64

        elif opcode == 'BUILTIN_CEIL':
            self.emit("call $ceil_f64", indent)
            self.imports.add('ceil_f64')
            # Type stays as f64

        elif opcode == 'BUILTIN_STR':
            # Convert value to string - returns (i32 ptr, i32 len) as two stack values
            # Check type of value on stack
            if self.type_stack:
                value_type = self.type_stack[-1]

                if value_type == 'i64':
                    self.emit("call $i64_to_str", indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    self.imports.add('i64_to_str')
                elif value_type == 'f64':
                    self.emit("call $f64_to_str", indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    self.imports.add('f64_to_str')
                elif value_type == 'i32':
                    # Could be a boolean, list, set, or other i32 value
                    # Check if we have tracked value type metadata
                    # Look back at previous instruction to see what type it is
                    converted_type = None

                    # Try to determine if this is a list or set from local_value_types
                    # This requires checking what local was loaded
                    # For now, we'll need a more sophisticated approach - track value metadata

                    # Use a heuristic: check the last few instructions in bytecode
                    # This is a limitation - proper solution needs runtime type info
                    # For WASM, we'll default to bool_to_str but add proper tracking

                    # Better approach: track what pushed this i32 onto the stack
                    # We'll enhance this by tracking value semantics
                    if hasattr(self, '_last_i32_source'):
                        if self._last_i32_source == 'list':
                            self.emit("call $list_to_str", indent)
                            self.imports.add('list_to_str')
                            converted_type = 'list'
                        elif self._last_i32_source == 'set':
                            self.emit("call $set_to_str", indent)
                            self.imports.add('set_to_str')
                            converted_type = 'set'

                    if not converted_type:
                        # Default to boolean
                        self.emit("call $bool_to_str", indent)
                        self.imports.add('bool_to_str')

                    self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    # Clear the i32 source tracking since we've now converted to string
                    self._last_i32_source = None

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
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

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
            self.emit("i64.lt_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_LT_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.lt_s", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

        elif opcode == 'CMP_LE_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.le_s", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

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
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')

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
            # Need to ensure value is i32 first
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i32.wrap_i64", indent)
                self.type_stack[-1] = 'i32'
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
            if self.type_stack and self.type_stack[-1] == 'i64':
                # For i64: 0 - value
                self.emit("i64.const -1", indent)
                self.emit("i64.mul", indent)
                # Stack type remains i64
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
            # Extract strings (handles multiple quoted strings)
            rest = inst[len('CONST_STR'):].strip()

            # Parse all quoted strings from the line
            strings = []
            i = 0
            while i < len(rest):
                if rest[i] == '"':
                    # Find the closing quote
                    j = i + 1
                    while j < len(rest) and rest[j] != '"':
                        if rest[j] == '\\':
                            j += 2  # Skip escaped character
                        else:
                            j += 1
                    if j < len(rest):
                        strings.append(rest[i+1:j])
                        i = j + 1
                    else:
                        break
                else:
                    i += 1

            # If no strings found, treat entire content as one string
            if not strings:
                string_content = rest
                if string_content.startswith('"') and string_content.endswith('"'):
                    string_content = string_content[1:-1]
                strings = [string_content]

            # Emit each string as (ptr, len)
            for string_content in strings:
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
            # Convert operands to f64 if needed
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'i64':
                    self.emit("f64.convert_i64_s", indent)
                    self.type_stack[-1] = 'f64'
                if self.type_stack[-2] == 'i64':
                    # Need to swap, convert, swap back
                    self.emit("local.set $temp_f64", indent)
                    self.type_stack.pop()
                    self.emit("f64.convert_i64_s", indent)
                    self.type_stack[-1] = 'f64'
                    self.emit("local.get $temp_f64", indent)
                    self.type_stack.append('f64')
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
            # Duplicate the top stack value
            # In WASM, we use local.tee with an appropriate temp local
            if self.type_stack:
                top_type = self.type_stack[-1]
                # Use correct temp local based on type
                if top_type == 'i64':
                    self.emit("local.tee $temp_i64", indent)
                    self.emit("local.get $temp_i64", indent)
                    self.type_stack.append('i64')
                elif top_type == 'i32':
                    self.emit("local.tee $temp", indent)
                    self.emit("local.get $temp", indent)
                    self.type_stack.append('i32')
                elif top_type == 'f64':
                    # For f64, we'd need a separate temp local
                    # For now, just approximate
                    self.emit_comment("DUP f64 - approximated", indent)
                    self.type_stack.append('f64')
                else:
                    self.emit_comment(f"DUP {top_type} - not implemented", indent)
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
            # Load from variables and store to others, alternating
            # Pattern: LOAD src1, STORE dst1, LOAD src2, STORE dst2, ...
            # If odd number of args, ends with LOAD (leaves value on stack)
            for i in range(0, len(args) - 1, 2):
                src_idx = int(args[i])
                dst_idx = int(args[i + 1])
                src_ref = self._get_var_ref(src_idx)
                dst_ref = self._get_var_ref(dst_idx)
                self.emit(f"local.get {src_ref}", indent)
                self.emit(f"local.set {dst_ref}", indent)
                # Update type tracking
                src_type = self.local_vars.get(src_idx, 'i64')
                self.local_vars[dst_idx] = src_type

            # If odd number of args, there's a final LOAD
            if len(args) % 2 == 1:
                final_idx = int(args[-1])
                final_ref = self._get_var_ref(final_idx)
                self.emit(f"local.get {final_ref}", indent)
                local_type = self.local_vars.get(final_idx, 'i64')
                self.type_stack.append(self._map_type_to_wasm(local_type))

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
            # Ensure value is i32 before testing
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i32.wrap_i64", indent)
                self.type_stack[-1] = 'i32'

            # Use br_if to jump to the label if condition is false
            self.emit("i32.eqz", indent)
            self.emit(f"br_if ${label_name}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'JUMP_IF_TRUE':
            label_name = args[0]
            # Ensure value is i32 before testing
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i32.wrap_i64", indent)
                self.type_stack[-1] = 'i32'
            # Branch if top of stack is non-zero/true
            self.emit(f"br_if ${label_name}", indent)
            if self.type_stack:
                self.type_stack.pop()

        elif opcode == 'LABEL':
            pass

        elif opcode == 'LIST_APPEND':
            self.emit("call $list_append", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()  # pop value
                self.type_stack.pop()  # pop list pointer
            self.type_stack.append('i32')  # list_append returns the list pointer
            self._last_i32_source = 'list'  # Track that this i32 is a list
            self.imports.add('list_append')

        elif opcode == 'LIST_GET':
            # Check if we have a string (i32, i32, i64) or list (i32, i64)
            # Stack layout for string: ... ptr(i32) len(i32) index(i64)
            if len(self.type_stack) >= 3 and self.type_stack[-3] == 'i32' and self.type_stack[-2] == 'i32' and self.type_stack[-1] == 'i64':
                # String indexing: (ptr, len, index) -> (ptr, len) of char
                self.emit("call $str_get", indent)
                for _ in range(3):
                    self.type_stack.pop()
                self.type_stack.append('i32')  # char ptr
                self.type_stack.append('i32')  # char len (always 1)
                self.imports.add('str_get')
            else:
                # List indexing
                self.emit("call $list_get", indent)
                if len(self.type_stack) >= 2:
                    self.type_stack.pop()
                    self.type_stack.pop()
                self.type_stack.append('i64')
                self.imports.add('list_get')

        elif opcode == 'LIST_NEW':
            self.emit("call $list_new", indent)
            self.type_stack.append('i32')
            self._last_i32_source = 'list'  # Track that this i32 is a list
            self.imports.add('list_new')

        elif opcode == 'LIST_SET':
            self.emit("call $list_set", indent)
            if len(self.type_stack) >= 3:
                self.type_stack.pop()  # value
                self.type_stack.pop()  # index
                self.type_stack.pop()  # list pointer
            self.type_stack.append('i32')  # list_set returns the list pointer
            self._last_i32_source = 'list'  # Track that this i32 is a list
            self.imports.add('list_set')

        elif opcode == 'LOAD':
            # LOAD can have multiple indices: LOAD 1 2 means load var1 then var2
            if len(args) == 0:
                return

            for arg in args:
                local_idx = int(arg)
                var_ref = self._get_var_ref(local_idx)

                # Check if this is a string local
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if local_idx < param_count:
                        # It's a parameter
                        param_type = func_meta['params'][local_idx][1]
                        local_type_fr = param_type
                    else:
                        # It's a local variable
                        rel_idx = local_idx - param_count
                        local_type_fr = self.local_vars.get(rel_idx, 'i64')

                    # If it's a string, load both ptr and len
                    if local_type_fr == 'str':
                        self.emit(f"local.get {var_ref}", indent)
                        self.type_stack.append('i32')
                        self.struct_type_stack.append(None)
                        len_ref = f"{var_ref}_len"
                        self.emit(f"local.get {len_ref}", indent)
                        self.type_stack.append('i32')
                        self.struct_type_stack.append(None)
                        continue

                # Regular single-value load
                self.emit(f"local.get {var_ref}", indent)
                # Get the correct local type
                struct_id = None
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if local_idx < param_count:
                        param_type = func_meta['params'][local_idx][1]
                        local_type = self._map_type_to_wasm(param_type)
                        # Track struct type
                        if param_type.startswith('struct:'):
                            struct_name = param_type.split(':')[1]
                            # Find struct ID by name (need to add name->id mapping)
                            for sid, sdef in self.struct_defs.items():
                                if 'name' in sdef and sdef['name'] == struct_name:
                                    struct_id = sid
                                    break
                    else:
                        rel_idx = local_idx - param_count
                        local_type_fr = self.local_vars.get(rel_idx, 'i64')
                        # Track struct type
                        if local_type_fr.startswith('struct:'):
                            struct_name = local_type_fr.split(':')[1]
                            # Find struct ID by name
                            for sid, sdef in self.struct_defs.items():
                                if 'name' in sdef and sdef['name'] == struct_name:
                                    struct_id = sid
                                    break
                        local_type = local_type_fr
                        if local_type not in ['i32', 'i64', 'f64']:
                            local_type = self._map_type_to_wasm(local_type)
                else:
                    local_type = 'i64'
                self.type_stack.append(local_type)
                self.struct_type_stack.append(struct_id)

                # Track value type if this is a list or set
                if local_idx in self.local_value_types:
                    self._last_i32_source = self.local_value_types[local_idx]

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

            # Check if we're storing a string (two i32 values)
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String: store len first, then ptr
                # Stack: ... ptr len (top)
                # We need to use two locals: var_ref for ptr, var_ref+"_len" for len
                len_ref = f"{var_ref}_len"
                self.emit(f"local.set {len_ref}", indent)
                self.type_stack.pop()
                self.emit(f"local.set {var_ref}", indent)
                self.type_stack.pop()
                # Track that this is a string type
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if var_idx >= param_count:
                        self.local_vars[var_idx - param_count] = 'str'
            else:
                # Regular value: single local.set
                if self.type_stack and self.current_function:
                    stored_type = self.type_stack[-1]
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if var_idx >= param_count:
                        self.local_vars[var_idx - param_count] = stored_type
                        # Track value type (list/set) if available
                        if hasattr(self, '_last_i32_source') and stored_type == 'i32':
                            self.local_value_types[var_idx] = self._last_i32_source
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
            if self.type_stack:
                if self.type_stack[-1] == 'i64':
                    self.emit("f64.convert_i64_s", indent)
                    self.type_stack[-1] = 'f64'
                elif len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                    # String (ptr, len) to float
                    self.emit("call $str_to_f64", indent)
                    self.type_stack.pop()
                    self.type_stack.pop()
                    self.type_stack.append('f64')
                    self.imports.add('str_to_f64')

        elif opcode == 'TO_INT':
            # Convert top of stack to i64
            if self.type_stack:
                if self.type_stack[-1] == 'f64':
                    self.emit("i64.trunc_f64_s", indent)
                    self.type_stack[-1] = 'i64'
                elif len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                    # String (ptr, len) to int - str_to_i64 already handles float strings
                    self.emit("call $str_to_i64", indent)
                    self.type_stack.pop()
                    self.type_stack.pop()
                    self.type_stack.append('i64')
                    self.imports.add('str_to_i64')

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
            # Store it temporarily so we can use it multiple times
            if count > 0:
                self.emit("local.set $temp", indent)  # Save list pointer
                # For each value, we need: list_ptr value -> call append -> list_ptr
                for i in range(count):
                    val = args[i + 1]
                    self.emit("local.get $temp", indent)  # Get list pointer
                    self.emit("i64.const " + val, indent)  # Push value
                    self.emit("call $list_append", indent)  # Append (returns updated list)
                    self.emit("local.set $temp", indent)  # Save updated list pointer
                # Put the list pointer back on stack
                self.emit("local.get $temp", indent)
            self.type_stack.append('i32')
            self._last_i32_source = 'list'  # Track that this i32 is a list
            self.imports.add('list_new')
            self.imports.add('list_append')

        elif opcode == 'LIST_NEW_STR':
            # LIST_NEW_STR count "str1" "str2" ...
            self.emit_comment(f"LIST_NEW_STR - requires runtime support", indent)
            count = int(args[0])
            self.emit("call $list_new", indent)
            # For now, just create empty list
            self.type_stack.append('i32')

        elif opcode == 'STRUCT_NEW':
            # STRUCT_NEW struct_id
            # Stack before: field_0 field_1 ... field_n (top of stack is last field)
            # Stack after: struct_ptr (i32)
            struct_id = int(args[0]) if args else 0

            if struct_id not in self.struct_defs:
                raise WasmCompilerError(f"Unknown struct ID: {struct_id}")

            struct_def = self.struct_defs[struct_id]
            field_count = struct_def['field_count']
            field_types = struct_def['field_types']

            self.emit_comment(f"STRUCT_NEW {struct_id} ({field_count} fields)", indent)

            # Get heap pointer for the new struct
            self.emit("global.get $heap_ptr", indent)

            # Increment heap pointer (8 bytes per field for all types)
            self.emit("global.get $heap_ptr", indent)
            self.emit(f"i32.const {field_count * 8}", indent)
            self.emit("i32.add", indent)
            self.emit("global.set $heap_ptr", indent)

            # Save the struct pointer
            self.emit("local.set $temp", indent)

            # Now pop each field (they come off in reverse order) and store
            # We need different store instructions for different types
            for i in range(field_count - 1, -1, -1):
                field_type = field_types[i]

                # Determine storage strategy based on field type
                if field_type == 'float':
                    # Float is f64, need to store as f64
                    # Stack: ... f64_value
                    # Convert f64 to i64 bits for storage in temp_i64
                    self.emit("i64.reinterpret_f64", indent)
                    self.emit("local.set $temp_i64", indent)
                    self.emit("local.get $temp", indent)
                    self.emit("local.get $temp_i64", indent)
                    # Convert back to f64 for f64.store
                    self.emit("f64.reinterpret_i64", indent)
                    self.emit(f"f64.store offset={i * 8}", indent)
                elif field_type == 'str':
                    # String is (ptr, len) = two i32 values on stack
                    # Top of stack is len, below is ptr
                    # Combine into one i64: (len << 32) | ptr
                    # Stack: ... ptr(i32) len(i32)
                    self.emit("i64.extend_i32_u", indent)  # len(i32) -> len(i64)
                    # Stack: ... ptr(i32) len(i64)
                    self.emit("i64.const 32", indent)
                    self.emit("i64.shl", indent)  # len << 32
                    # Stack: ... ptr(i32) (len<<32)(i64)
                    self.emit("local.set $temp_i64", indent)  # Save (len<<32)
                    # Stack: ... ptr(i32)
                    self.emit("i64.extend_i32_u", indent)  # ptr -> i64
                    # Stack: ... ptr(i64)
                    self.emit("local.get $temp_i64", indent)  # Get (len<<32)
                    # Stack: ... ptr(i64) (len<<32)(i64)
                    self.emit("i64.or", indent)  # ptr | (len << 32)
                    # Stack: ... combined(i64)
                    self.emit("local.set $temp_i64", indent)
                    self.emit("local.get $temp", indent)
                    self.emit("local.get $temp_i64", indent)
                    self.emit(f"i64.store offset={i * 8}", indent)
                elif field_type == 'bool':
                    # Bool is i32, extend to i64
                    self.emit("i64.extend_i32_u", indent)
                    self.emit("local.set $temp_i64", indent)
                    self.emit("local.get $temp", indent)
                    self.emit("local.get $temp_i64", indent)
                    self.emit(f"i64.store offset={i * 8}", indent)
                else:  # int or any other type
                    # Already i64, just store
                    self.emit("local.set $temp_i64", indent)
                    self.emit("local.get $temp", indent)
                    self.emit("local.get $temp_i64", indent)
                    self.emit(f"i64.store offset={i * 8}", indent)

            # Push struct pointer back to stack
            self.emit("local.get $temp", indent)

            # Update type stack
            for _ in range(field_count):
                self.pop_type()
            self.push_type('i32', struct_id)

        elif opcode == 'STRUCT_GET':
            # STRUCT_GET field_index
            # Stack before: struct_ptr (i32)
            # Stack after: field_value (type depends on field)
            field_idx = int(args[0]) if args else 0

            self.emit_comment(f"STRUCT_GET {field_idx}", indent)

            # Get struct type from struct_type_stack
            struct_id = self.get_struct_id()

            # Pop struct pointer type
            self.pop_type()

            # Determine field type
            field_type = None
            if struct_id is not None and struct_id in self.struct_defs:
                struct_def = self.struct_defs[struct_id]
                field_types = struct_def['field_types']
                if field_idx < len(field_types):
                    field_type = field_types[field_idx]

            # Load field with appropriate instruction
            if field_type == 'float':
                # Float field: load as f64
                self.emit(f"f64.load offset={field_idx * 8}", indent)
                self.push_type('f64')
            elif field_type == 'str':
                # String field: load combined i64, extract ptr and len
                # Combined format: (len << 32) | ptr
                self.emit(f"i64.load offset={field_idx * 8}", indent)
                # Split into ptr (lower 32) and len (upper 32)
                # First, duplicate for extracting both parts
                self.emit("local.set $temp_i64", indent)
                # Extract ptr (lower 32 bits)
                self.emit("local.get $temp_i64", indent)
                self.emit("i32.wrap_i64", indent)  # ptr
                # Extract len (upper 32 bits)
                self.emit("local.get $temp_i64", indent)
                self.emit("i64.const 32", indent)
                self.emit("i64.shr_u", indent)
                self.emit("i32.wrap_i64", indent)  # len
                self.push_type('i32')  # ptr
                self.push_type('i32')  # len
            elif field_type == 'bool':
                # Bool field: load as i64, truncate to i32
                self.emit(f"i64.load offset={field_idx * 8}", indent)
                self.emit("i32.wrap_i64", indent)
                self.push_type('i32')
            elif field_type and field_type.startswith('struct:'):
                # Nested struct field: load pointer as i32
                # The struct pointer is stored as i64, extract as i32
                self.emit(f"i64.load offset={field_idx * 8}", indent)
                self.emit("i32.wrap_i64", indent)
                # Try to find the nested struct ID
                nested_struct_name = field_type.split(':')[1]
                nested_struct_id = None
                for sid, sdef in self.struct_defs.items():
                    if 'name' in sdef and sdef['name'] == nested_struct_name:
                        nested_struct_id = sid
                        break
                self.push_type('i32', nested_struct_id)
            else:
                # Default: int or unknown type, load as i64
                self.emit(f"i64.load offset={field_idx * 8}", indent)
                self.push_type('i64')

        elif opcode == 'STRUCT_SET':
            # STRUCT_SET field_index
            # Stack before: struct_ptr (i32) field_value (i64)
            # Stack after: struct_ptr (i32)
            field_idx = int(args[0]) if args else 0

            self.emit_comment(f"STRUCT_SET {field_idx}", indent)

            # Pop value and struct pointer
            if len(self.type_stack) >= 2:
                self.type_stack.pop()  # value
                self.type_stack.pop()  # struct

            # Save value and struct pointer
            self.emit("local.set $temp_i64", indent)  # value
            self.emit("local.set $temp", indent)  # struct_ptr

            # Store value at struct_ptr + field_idx * 8
            self.emit("local.get $temp", indent)  # struct_ptr
            self.emit("local.get $temp_i64", indent)  # value
            self.emit(f"i64.store offset={field_idx * 8}", indent)

            # Push struct pointer back to stack
            self.emit("local.get $temp", indent)
            self.type_stack.append('i32')

        elif opcode == 'STR_EQ':
            # String equality comparison
            self.emit_comment("STR_EQ - requires runtime support", indent)
            # Pop two string refs (ptr+len each = 4 values)
            for _ in range(4):
                if self.type_stack:
                    self.type_stack.pop()
            self.emit("i32.const 0", indent)
            self.type_stack.append('i32')

        elif opcode == 'STR_UPPER':
            # Consumes (ptr, len), produces (ptr, len)
            self.emit("call $str_upper", indent)
            # Stack already has correct types
            self.imports.add('str_upper')

        elif opcode == 'STR_LOWER':
            # Consumes (ptr, len), produces (ptr, len)
            self.emit("call $str_lower", indent)
            self.imports.add('str_lower')

        elif opcode == 'STR_STRIP':
            # Consumes (ptr, len), produces (ptr, len)
            self.emit("call $str_strip", indent)
            self.imports.add('str_strip')

        elif opcode == 'STR_REPLACE':
            # Consumes (str_ptr, str_len, old_ptr, old_len, new_ptr, new_len), produces (ptr, len)
            self.emit("call $str_replace", indent)
            # Pop 6 i32 values (3 strings), push 2 i32 values (1 string)
            for _ in range(6):
                if self.type_stack:
                    self.type_stack.pop()
            self.type_stack.append('i32')
            self.type_stack.append('i32')
            self.imports.add('str_replace')

        elif opcode == 'STR_JOIN':
            # Consumes (sep_ptr, sep_len, list_ptr), produces (ptr, len)
            self.emit("call $str_join", indent)
            # Pop 3 values, push 2 values
            for _ in range(3):
                if self.type_stack:
                    self.type_stack.pop()
            self.type_stack.append('i32')
            self.type_stack.append('i32')
            self.imports.add('str_join')

        elif opcode == 'STR_SPLIT':
            # Consumes (str_ptr, str_len, sep_ptr, sep_len), produces list_ptr
            self.emit("call $str_split", indent)
            # Pop 4 i32 values, push 1 i32 value
            for _ in range(4):
                if self.type_stack:
                    self.type_stack.pop()
            self.type_stack.append('i32')
            self.imports.add('str_split')

        elif opcode == 'CONTAINS':
            # Check if we have strings (4 i32s) or list (2 values)
            if len(self.type_stack) >= 4 and all(t == 'i32' for t in self.type_stack[-4:]):
                # String contains: (haystack_ptr, haystack_len, needle_ptr, needle_len)
                self.emit("call $str_contains", indent)
                for _ in range(4):
                    if self.type_stack:
                        self.type_stack.pop()
                self.type_stack.append('i32')
                self.imports.add('str_contains')
            else:
                # List contains - requires runtime support
                self.emit_comment("CONTAINS (list) - requires runtime support", indent)
                if self.type_stack:
                    self.type_stack.pop()  # container
                if self.type_stack:
                    self.type_stack.pop()  # value
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')

        elif opcode == 'LIST_POP':
            # Pop from list - returns (list_ptr, value)
            self.emit("call $list_pop", indent)
            if self.type_stack:
                self.type_stack.pop()  # consume list pointer
            self.type_stack.append('i32')  # list pointer
            self.type_stack.append('i64')  # popped value
            self.imports.add('list_pop')

        elif opcode == 'BUILTIN_PI':
            # Push π constant
            self.emit("f64.const 3.141592653589793", indent)
            self.type_stack.append('f64')

        elif opcode == 'SWITCH_JUMP_TABLE':
            # SWITCH_JUMP_TABLE min_value max_value label1 label2 ... labelN
            # Value is on stack, check if in range [min, max], then use br_table
            if len(args) < 3:
                self.emit_comment("SWITCH_JUMP_TABLE - invalid args", indent)
                # Pop the value
                if self.type_stack:
                    self.type_stack.pop()
                return

            min_val = int(args[0])
            max_val = int(args[1])
            labels = args[2:]

            # Pop the switch value from type stack
            if self.type_stack:
                self.type_stack.pop()

            # Value is on stack as i64
            # Convert to i32 for br_table and subtract min_val to get index
            self.emit(f"i32.wrap_i64", indent)
            if min_val != 0:
                self.emit(f"i32.const {min_val}", indent)
                self.emit("i32.sub", indent)

            # Now we have the index. Use br_table with all labels
            # br_table takes: index on stack, list of labels, default label
            # If index out of range, use last label as default
            label_str = " ".join(f"${lbl}" for lbl in labels)
            self.emit(f"br_table {label_str}", indent)

        elif opcode == 'SET_NEW':
            self.emit("call $set_new", indent)
            self.type_stack.append('i32')
            self._last_i32_source = 'set'  # Track that this i32 is a set
            self.imports.add('set_new')

        elif opcode == 'SET_ADD':
            # Stack: set(i32) value(any) -> set(i32)
            # Need to check if value is a string (i32, i32) and convert to i64 hash
            if len(self.type_stack) >= 3 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String value: (set, ptr, len) -> need to hash string to i64
                # For now, use str_to_i64 to convert string to number
                # TODO: implement proper string hashing
                self.emit("call $str_to_i64", indent)
                self.emit("call $set_add", indent)
                self.type_stack.pop()  # i32 len
                self.type_stack.pop()  # i32 ptr
                self.type_stack.pop()  # i32 set
                self.type_stack.append('i32')
                self._last_i32_source = 'set'
                self.imports.add('str_to_i64')
                self.imports.add('set_add')
            else:
                # Regular i64 value
                self.emit("call $set_add", indent)
                if len(self.type_stack) >= 2:
                    self.type_stack.pop()  # value
                    self.type_stack.pop()  # set
                self.type_stack.append('i32')
                self._last_i32_source = 'set'  # Track that this i32 is a set
                self.imports.add('set_add')

        elif opcode == 'SET_REMOVE':
            # Stack: set(i32) value(any) -> set(i32)
            # Need to check if value is a string (i32, i32) and convert to i64 hash
            if len(self.type_stack) >= 3 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String value: (set, ptr, len) -> need to hash string to i64
                self.emit("call $str_to_i64", indent)
                self.emit("call $set_remove", indent)
                self.type_stack.pop()  # i32 len
                self.type_stack.pop()  # i32 ptr
                self.type_stack.pop()  # i32 set
                self.type_stack.append('i32')
                self._last_i32_source = 'set'
                self.imports.add('str_to_i64')
                self.imports.add('set_remove')
            else:
                # Regular i64 value
                self.emit("call $set_remove", indent)
                if len(self.type_stack) >= 2:
                    self.type_stack.pop()  # value
                    self.type_stack.pop()  # set
                self.type_stack.append('i32')
                self._last_i32_source = 'set'  # Track that this i32 is a set
                self.imports.add('set_remove')

        elif opcode == 'SET_CONTAINS':
            # Stack: set(i32) value(i64) -> result(i32)
            self.emit("call $set_contains", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()  # value
                self.type_stack.pop()  # set
            self.type_stack.append('i32')
            self.imports.add('set_contains')

        elif opcode == 'TRY_BEGIN':
            # Start of try block - for now, just a marker
            # WASM doesn't have try-catch, we'd need to emulate with result types
            self.emit_comment("TRY_BEGIN - exception handling not supported in WASM", indent)

        elif opcode == 'TRY_END':
            # End of try block
            self.emit_comment("TRY_END - exception handling not supported in WASM", indent)

        elif opcode == 'FILE_OPEN':
            # Stack: path_ptr(i32) path_len(i32) mode_ptr(i32) mode_len(i32) -> fd(i32)
            self.emit("call $file_open", indent)
            for _ in range(4):
                if self.type_stack:
                    self.type_stack.pop()
            self.type_stack.append('i32')
            self.imports.add('file_open')

        elif opcode == 'FILE_READ':
            # Stack: fd(i32) -> ptr(i32) len(i32)
            self.emit("call $file_read", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')
            self.type_stack.append('i32')
            self.imports.add('file_read')

        elif opcode == 'FILE_WRITE':
            # Stack: fd(i32) ptr(i32) len(i32) -> (nothing)
            self.emit("call $file_write", indent)
            for _ in range(3):
                if self.type_stack:
                    self.type_stack.pop()
            self.imports.add('file_write')

        elif opcode == 'FILE_CLOSE':
            # Stack: fd(i32) -> (nothing)
            self.emit("call $file_close", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.imports.add('file_close')

        elif opcode == 'EXIT':
            # Stack: code(i64) -> (never returns)
            # Convert i64 to i32 for exit code
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("i32.wrap_i64", indent)
                self.type_stack[-1] = 'i32'
            self.emit("call $exit_process", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.imports.add('exit_process')

        elif opcode in ['RAISE', 'SOCKET_CREATE', 'SOCKET_CONNECT', 'SOCKET_BIND', 'SOCKET_LISTEN', 'SOCKET_ACCEPT', 'SOCKET_SEND', 'SOCKET_RECV', 'SOCKET_CLOSE', 'FORK', 'JOIN', 'SLEEP', 'GOTO_CALL', 'ENCODE', 'DECODE', 'LOAD2_CMP_GT']:
            # Operations that require special runtime or OS support
            self.emit_comment(f"{opcode} - not supported in WASM", indent)
            # Push dummy values to keep stack balanced
            if opcode in ['SOCKET_CREATE', 'SOCKET_ACCEPT', 'FORK']:
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
            elif opcode in ['SOCKET_RECV', 'ENCODE', 'DECODE']:
                # Returns bytes/string (ptr, len)
                self.emit("i32.const 0", indent)
                self.emit("i32.const 0", indent)
                self.type_stack.append('i32')
                self.type_stack.append('i32')
            elif opcode in ['SOCKET_CONNECT', 'SOCKET_BIND', 'SOCKET_LISTEN', 'SOCKET_SEND', 'SOCKET_CLOSE', 'JOIN', 'SLEEP', 'RAISE']:
                # Operations that consume values but return nothing (or consume from stack)
                pass

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
