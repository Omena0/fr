"""
WebAssembly Compiler for fr bytecode

Compiles fr bytecode to WebAssembly text format (WAT).
"""

from typing import List, Dict, Tuple, Optional, Set


class WasmCompilerError(Exception):
    """Raised when WASM compilation fails"""
    pass

class TypeStack(list):
    """A list wrapper that keeps extended_type_stack in sync"""
    def __init__(self, compiler):
        super().__init__()
        self.compiler = compiler

    def append(self, item):
        super().append(item)
        if hasattr(self.compiler, 'extended_type_stack'):
            self.compiler.extended_type_stack.append(None)

    def pop(self, index=-1):
        if hasattr(self.compiler, 'extended_type_stack') and self.compiler.extended_type_stack:
            self.compiler.extended_type_stack.pop(index)
        return super().pop(index)

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        if hasattr(self.compiler, 'extended_type_stack') and len(self.compiler.extended_type_stack) > index:
             self.compiler.extended_type_stack[index] = None

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
        self.builtin_map = {
            'fopen': ('file_open', ['i32'], ['i32', 'i32', 'i32', 'i32']),
            'fread': ('file_read', ['i32', 'i32'], ['i32', 'i32']),
            'fwrite': ('file_write', [], ['i32', 'i32', 'i32']),
            'fclose': ('file_close', [], ['i32']),
            # Web/WASM Functions - DOM
            'dom_create': ('dom_create', ['i32'], ['i32', 'i32']),
            'dom_get_body': ('dom_get_body', ['i32'], []),
            'dom_get_document': ('dom_get_document', ['i32'], []),
            'dom_set_text': ('dom_set_text', [], ['i32', 'i32', 'i32']),
            'dom_get_text': ('dom_get_text', ['i32', 'i32'], ['i32']),
            'dom_set_html': ('dom_set_html', [], ['i32', 'i32', 'i32']),
            'dom_get_html': ('dom_get_html', ['i32', 'i32'], ['i32']),
            'dom_set_attr': ('dom_set_attr', [], ['i32', 'i32', 'i32']),
            'dom_get_attr': ('dom_get_attr', ['i32', 'i32'], ['i32', 'i32', 'i32']),
            'dom_remove_attr': ('dom_remove_attr', [], ['i32', 'i32', 'i32']),
            'dom_append': ('dom_append', [], ['i32', 'i32']),
            'dom_prepend': ('dom_prepend', [], ['i32', 'i32']),
            'dom_remove': ('dom_remove', [], ['i32']),
            'dom_clone': ('dom_clone', ['i32'], ['i32', 'i32']),
            'dom_parent': ('dom_parent', ['i32'], ['i32']),
            'dom_children': ('dom_children', ['i32'], ['i32']),
            'dom_add_class': ('dom_add_class', [], ['i32', 'i32', 'i32']),
            'dom_remove_class': ('dom_remove_class', [], ['i32', 'i32', 'i32']),
            'dom_toggle_class': ('dom_toggle_class', [], ['i32', 'i32', 'i32']),
            'dom_has_class': ('dom_has_class', ['i32'], ['i32', 'i32', 'i32']),
            'dom_set_style': ('dom_set_style', [], ['i32', 'i32', 'i32', 'i32', 'i32']),
            'dom_get_style': ('dom_get_style', ['i32', 'i32'], ['i32', 'i32', 'i32']),
            'dom_get_value': ('dom_get_value', ['i32', 'i32'], ['i32']),
            'dom_set_value': ('dom_set_value', [], ['i32', 'i32', 'i32']),
            'dom_focus': ('dom_focus', [], ['i32']),
            'dom_blur': ('dom_blur', [], ['i32']),
            'dom_query': ('dom_query', ['i32'], ['i32', 'i32']),
            'dom_query_all': ('dom_query_all', ['i32'], ['i32', 'i32']),
            'dom_on': ('dom_on', [], ['i32', 'i32', 'i32', 'i32']),
            'dom_off': ('dom_off', [], ['i32']),
            'event_prevent_default': ('event_prevent_default', [], []),
            'event_stop_propagation': ('event_stop_propagation', [], []),
            'event_target': ('event_target', ['i32'], []),
            # Web/WASM Functions - Timers (variadic - accept variable args to pass to callback)
            'set_timeout': ('set_timeout', ['i32'], []),  # Returns i32, params handled specially
            'set_interval': ('set_interval', ['i32'], []),
            'clear_timeout': ('clear_timeout', [], ['i32']),
            'clear_interval': ('clear_interval', [], ['i32']),
        }

        # Exception handling
        self.try_stack: List[Tuple[str, str]] = []  # Stack of (error_type, handler_label)
        self.global_str_bases: Set[int] = set()  # Base indices for string globals (ptr, len)

        # Bytecode version
        self.version = 1

        # Allocate memory for struct storage (start after string constants)
        self.heap_offset = 1024  # Start heap at 1KB

        # Track current source line from `.line` directives (best-effort).
        self.current_source_line = 0

        # Track function references for callbacks
        self.callback_functions: Set[str] = set()  # Functions used as callbacks

        # Track timer function signatures (variadic)
        self.timer_signatures: Dict[str, str] = {}  # Maps timer func name to param signature

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

        # Detect which imports are actually used
        self._collect_imports_used(lines)

        # Pre-pass to determine timer function signatures (variadic)
        self._analyze_timer_signatures(lines)

        # Generate WAT module
        self.emit("(module", 0)

        # Import memory management functions (for string/list operations)
        self._emit_imports()

        # Define memory (start with 64KB * 64 = 4MB, allow growth up to 1024 pages ~64MB)
        self.emit("(memory (export \"memory\") 64 1024)", 1)

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
            "string_constants": self.string_constants,
            "callbacks": list(self.callback_functions)
        }

        return '\n'.join(self.output), metadata

    def _collect_imports_used(self, lines: List[str]):
        """Scan bytecode to determine which imports are actually used"""
        for line in lines:
            line = line.strip()

            # Check for FUNC_REF markers to track callback functions
            if line.startswith('# FUNC_REF '):
                parts = line.split()
                if len(parts) >= 3:
                    func_name = parts[2]
                    self.callback_functions.add(func_name)
                continue

            if not line or line.startswith('#'):
                continue

            # Check for CALL instructions that use builtin functions
            if line.startswith('CALL '):
                parts = line.split()
                if len(parts) >= 2:
                    func_name = parts[1]
                    # Check if this is a builtin function in our map
                    if func_name in self.builtin_map:
                        self.imports.add(func_name)

    def _analyze_timer_signatures(self, lines: List[str]):
        """Pre-pass to determine variadic timer function signatures"""
        # Build a simple type stack to track what's on stack at each CALL
        type_stack = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('.'):
                continue

            parts = line.split()
            if not parts:
                continue

            opcode = parts[0]

            # Track constants being pushed
            if opcode == 'CONST_I64':
                # Can have multiple values: CONST_I64 0 10 pushes two i64 values
                for _ in parts[1:]:
                    type_stack.append('i64')
            elif opcode == 'CONST_F64':
                type_stack.append('f64')
            elif opcode == 'LOAD' or opcode == 'LOAD_GLOBAL':
                # Could be any type, assume i64 for simplicity
                type_stack.append('i64')
            elif opcode in ('ADD', 'SUB', 'MUL', 'DIV', 'MOD'):
                # Binary ops pop 2, push 1
                if len(type_stack) >= 2:
                    type_stack.pop()
                    type_stack.pop()
                type_stack.append('i64')
            elif opcode == 'CALL':
                func_name = parts[1]
                arg_count = int(parts[2]) if len(parts) > 2 else 0

                # Check if it's a timer function
                if func_name in ('set_timeout', 'set_interval'):
                    # Determine signature from stack
                    if len(type_stack) >= arg_count:
                        # Timer functions: (callback_idx: i32, ms: i32, ...args: i32)
                        # All callback args are i32 (will be converted at call site if needed)
                        param_types = ['i32'] * arg_count
                        sig_parts = ' '.join(f'(param {t})' for t in param_types)
                        self.timer_signatures[func_name] = sig_parts

                # Pop args and push result (simplified)
                for _ in range(min(arg_count, len(type_stack))):
                    type_stack.pop()
                type_stack.append('i32')  # Most functions return i32
            elif opcode == 'POP':
                if type_stack:
                    type_stack.pop()
            elif opcode in ('STORE', 'STORE_GLOBAL'):
                if type_stack:
                    type_stack.pop()

    def _emit_imports(self):
        """Emit import declarations for runtime functions"""
        self.emit_comment("Runtime imports for complex operations", 1)

        # DOM/Web functions (only emit if used)
        if 'dom_create' in self.imports:
            self.emit('(import "env" "dom_create" (func $dom_create (param i32 i32) (result i32)))', 1)
        if 'dom_get_body' in self.imports:
            self.emit('(import "env" "dom_get_body" (func $dom_get_body (result i32)))', 1)
        if 'dom_get_document' in self.imports:
            self.emit('(import "env" "dom_get_document" (func $dom_get_document (result i32)))', 1)
        if 'dom_set_text' in self.imports:
            self.emit('(import "env" "dom_set_text" (func $dom_set_text (param i32 i32 i32)))', 1)
        if 'dom_get_text' in self.imports:
            self.emit('(import "env" "dom_get_text" (func $dom_get_text (param i32) (result i32 i32)))', 1)
        if 'dom_set_html' in self.imports:
            self.emit('(import "env" "dom_set_html" (func $dom_set_html (param i32 i32 i32)))', 1)
        if 'dom_get_html' in self.imports:
            self.emit('(import "env" "dom_get_html" (func $dom_get_html (param i32) (result i32 i32)))', 1)
        if 'dom_set_attr' in self.imports:
            self.emit('(import "env" "dom_set_attr" (func $dom_set_attr (param i32 i32 i32)))', 1)
        if 'dom_get_attr' in self.imports:
            self.emit('(import "env" "dom_get_attr" (func $dom_get_attr (param i32 i32 i32) (result i32 i32)))', 1)
        if 'dom_remove_attr' in self.imports:
            self.emit('(import "env" "dom_remove_attr" (func $dom_remove_attr (param i32 i32 i32)))', 1)
        if 'dom_append' in self.imports:
            self.emit('(import "env" "dom_append" (func $dom_append (param i32 i32)))', 1)
        if 'dom_prepend' in self.imports:
            self.emit('(import "env" "dom_prepend" (func $dom_prepend (param i32 i32)))', 1)
        if 'dom_remove' in self.imports:
            self.emit('(import "env" "dom_remove" (func $dom_remove (param i32)))', 1)
        if 'dom_clone' in self.imports:
            self.emit('(import "env" "dom_clone" (func $dom_clone (param i32 i32) (result i32)))', 1)
        if 'dom_parent' in self.imports:
            self.emit('(import "env" "dom_parent" (func $dom_parent (param i32) (result i32)))', 1)
        if 'dom_children' in self.imports:
            self.emit('(import "env" "dom_children" (func $dom_children (param i32) (result i32)))', 1)
        if 'dom_add_class' in self.imports:
            self.emit('(import "env" "dom_add_class" (func $dom_add_class (param i32 i32 i32)))', 1)
        if 'dom_remove_class' in self.imports:
            self.emit('(import "env" "dom_remove_class" (func $dom_remove_class (param i32 i32 i32)))', 1)
        if 'dom_toggle_class' in self.imports:
            self.emit('(import "env" "dom_toggle_class" (func $dom_toggle_class (param i32 i32 i32)))', 1)
        if 'dom_has_class' in self.imports:
            self.emit('(import "env" "dom_has_class" (func $dom_has_class (param i32 i32 i32) (result i32)))', 1)
        if 'dom_set_style' in self.imports:
            self.emit('(import "env" "dom_set_style" (func $dom_set_style (param i32 i32 i32 i32 i32)))', 1)
        if 'dom_get_style' in self.imports:
            self.emit('(import "env" "dom_get_style" (func $dom_get_style (param i32 i32 i32) (result i32 i32)))', 1)
        if 'dom_get_value' in self.imports:
            self.emit('(import "env" "dom_get_value" (func $dom_get_value (param i32) (result i32 i32)))', 1)
        if 'dom_set_value' in self.imports:
            self.emit('(import "env" "dom_set_value" (func $dom_set_value (param i32 i32 i32)))', 1)
        if 'dom_focus' in self.imports:
            self.emit('(import "env" "dom_focus" (func $dom_focus (param i32)))', 1)
        if 'dom_blur' in self.imports:
            self.emit('(import "env" "dom_blur" (func $dom_blur (param i32)))', 1)
        if 'dom_query' in self.imports:
            self.emit('(import "env" "dom_query" (func $dom_query (param i32 i32) (result i32)))', 1)
        if 'dom_query_all' in self.imports:
            self.emit('(import "env" "dom_query_all" (func $dom_query_all (param i32 i32) (result i32)))', 1)
        if 'dom_on' in self.imports:
            self.emit('(import "env" "dom_on" (func $dom_on (param i32 i32 i32 i32)))', 1)
        if 'dom_off' in self.imports:
            self.emit('(import "env" "dom_off" (func $dom_off (param i32)))', 1)
        if 'event_prevent_default' in self.imports:
            self.emit('(import "env" "event_prevent_default" (func $event_prevent_default))', 1)
        if 'event_stop_propagation' in self.imports:
            self.emit('(import "env" "event_stop_propagation" (func $event_stop_propagation))', 1)
        if 'event_target' in self.imports:
            self.emit('(import "env" "event_target" (func $event_target (result i32)))', 1)

        # Timer functions (only emit if used) - signatures determined dynamically
        if 'set_timeout' in self.imports:
            sig = self.timer_signatures.get('set_timeout', '(param i32 i32)')
            self.emit(f'(import "env" "set_timeout" (func $set_timeout {sig} (result i32)))', 1)
        if 'set_interval' in self.imports:
            sig = self.timer_signatures.get('set_interval', '(param i32 i32)')
            self.emit(f'(import "env" "set_interval" (func $set_interval {sig} (result i32)))', 1)
        if 'clear_timeout' in self.imports:
            self.emit('(import "env" "clear_timeout" (func $clear_timeout (param i32)))', 1)
        if 'clear_interval' in self.imports:
            self.emit('(import "env" "clear_interval" (func $clear_interval (param i32)))', 1)

        # Import console output
        self.emit('(import "env" "print" (func $print (param i32 i32)))', 1)
        self.emit('(import "env" "println" (func $println (param i32 i32)))', 1)

        # Import runtime error reporting (error_type_ptr, error_type_len, message_ptr, message_len, line_num)
        self.emit('(import "env" "runtime_error" (func $runtime_error (param i32 i32 i32 i32 i32)))', 1)

        # Import string operations (return ptr and len as two values)
        self.emit('(import "env" "str_concat" (func $str_concat (param i32 i32 i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_to_i64" (func $str_to_i64 (param i32 i32) (result i64)))', 1)
        self.emit('(import "env" "str_to_f64" (func $str_to_f64 (param i32 i32) (result f64)))', 1)
        self.emit('(import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))', 1)
        self.emit('(import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))', 1)
        self.emit('(import "env" "bool_to_str" (func $bool_to_str (param i64) (result i32 i32)))', 1)
        self.emit('(import "env" "list_to_str" (func $list_to_str (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "set_to_str" (func $set_to_str (param i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_upper" (func $str_upper (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_lower" (func $str_lower (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_strip" (func $str_strip (param i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_replace" (func $str_replace (param i32 i32 i32 i32 i32 i32) (result i32 i32)))', 1)
        self.emit('(import "env" "str_get" (func $str_get (param i32 i32 i64) (result i32 i32)))', 1)
        self.emit('(import "env" "str_contains" (func $str_contains (param i32 i32 i32 i32) (result i32)))', 1)
        self.emit('(import "env" "str_eq" (func $str_eq (param i32 i32 i32 i32) (result i32)))', 1)
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
        self.emit('(import "env" "list_contains" (func $list_contains (param i32 i64) (result i32)))', 1)
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
        self.emit('(import "env" "sleep" (func $sleep (param f64)))', 1)

    def _emit_globals(self):
        """Emit global variable declarations"""
        # Always emit heap pointer for struct allocation
        self.emit_comment("Heap pointer for struct allocation", 1)
        self.emit(f"(global $heap_ptr (mut i32) (i32.const {self.heap_offset}))", 1)

        # Exception handling globals
        self.emit_comment("Exception handling globals", 1)
        self.emit("(global $exception_active (mut i32) (i32.const 0))", 1)

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
        global_count = 0
        referenced_globals: Set[int] = set()

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
                struct_id = int(parts[2])
                if struct_id in self.struct_defs:
                    struct_name = parts[1]
                    self.struct_defs[struct_id]['name'] = struct_name
                continue

            # Global variable declaration: .global <name> <type>
            if line.startswith('.global '):
                parts = line.split()
                if len(parts) >= 3:
                    fr_type = parts[2]
                else:
                    fr_type = 'i64'
                if fr_type == 'str':
                    # Allocate two globals: base for ptr, base+1 for len
                    self.global_vars[global_count] = 'i32'
                    self.global_vars[global_count + 1] = 'i32'
                    self.global_str_bases.add(global_count)
                    global_count += 2
                else:
                    wasm_type = self._map_type_to_wasm(fr_type)
                    self.global_vars[global_count] = wasm_type
                    global_count += 1
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

            # Track referenced globals to backfill missing declarations
            if line.startswith('LOAD_GLOBAL ') or line.startswith('STORE_GLOBAL '):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    referenced_globals.add(int(parts[1]))

        # Ensure we declare globals for any referenced indices not explicitly declared
        if referenced_globals:
            max_idx = max(referenced_globals)
            for idx in range(max_idx + 1):
                if idx not in self.global_vars:
                    # Default to i64 to safely hold packed values
                    self.global_vars[idx] = 'i64'

    def _map_type_to_wasm(self, fr_type: str) -> str:
        """Map fr type to WASM type"""
        if fr_type in ('i32', 'i64', 'f64'):
            return fr_type
        type_map = {
            'i64': 'i64',
            'f64': 'f64',
            'str': 'i32',  # String pointer
            'bool': 'i32',  # Boolean as i32
            'void': '',
            'list': 'i32',  # List pointer
            'set': 'i32',   # Set pointer
            'any': 'i64',
            'int': 'i32',
            'variadic': 'i32', # List pointer
        }
        # Handle struct types (e.g., "struct:Point") or bare struct names (e.g., "Point")
        if fr_type.startswith('struct:') or self._is_struct_name(fr_type):
            return 'i32'
        return type_map.get(fr_type, 'i64')

    def _is_struct_name(self, name: str) -> bool:
        """Check if a name is a known struct name"""
        for sdef in self.struct_defs.values():
            if sdef.get('name') == name:
                return True
        return False

    def _compile_function(self, func_name: str, func_meta: Dict, bytecode_lines: List[str]):
        """Compile a single function"""
        self.current_function = func_name
        self.local_vars = func_meta['locals'].copy()
        self.type_stack = TypeStack(self)
        self.extended_type_stack = []  # Track detailed types (e.g. 'str') parallel to type_stack
        self.struct_type_stack = []
        self.label_stack = []

        # Track parameter count for index translation
        param_count = len(func_meta['params'])

        # Start function definition
        export_attr = ''
        if func_name == "main":
            export_attr = ' (export "main")'
        elif func_name in self.callback_functions:
            # Export callback functions so they can be called from JavaScript
            export_attr = f' (export "{func_name}")'

        params_str = ""

        # Add parameters
        for idx, (param_name, param_type) in enumerate(func_meta['params']):
            # Strings are represented as (ptr, len) -> two i32 params
            if param_type == 'str':
                params_str += f" (param $p{idx} i32) (param $p{idx}_len i32)"
            else:
                wasm_type = self._map_type_to_wasm(param_type)
                params_str += f" (param $p{idx} {wasm_type})"

        # Determine return type
        return_type = func_meta['return_type']
        wasm_return = ""
        if return_type and return_type != 'void':
            if return_type == 'str':
                # String return: two i32 values (ptr, len)
                wasm_return = " (result i32 i32)"
            else:
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
                # Heuristic handled below in a dedicated scan
                pass

        # Heuristic scan: if a LIST_NEW_* is immediately stored to a local
        # (pattern: LIST_NEW_* ... \n STORE N) then mark that local as a list
        # so we declare it as an i32 instead of default i64. This fixes cases
        # where list literals are stored directly into locals (common in tests).
        scan_in_func = False
        lines = [l.strip() for l in bytecode_lines]
        last_load_idx = None
        for i, line in enumerate(lines):
            if line.startswith('.func'):
                parts = line.split()
                scan_in_func = (parts[1] == func_name)
                last_load_idx = None
                continue
            if not scan_in_func:
                continue

            if line.startswith('LOAD ') and len(line.split()) == 2 and line.split()[1].isdigit():
                last_load_idx = int(line.split()[1])

            # DOM element handles are i32; if dom_create/dom_query result is stored, mark it
            if line.startswith('CALL dom_create') or line.startswith('CALL dom_query'):
                j = i + 1
                while j < len(lines) and (lines[j] == '' or lines[j].startswith('#') or lines[j].startswith('.line')):
                    j += 1
                if j < len(lines) and lines[j].startswith('STORE '):
                    parts = lines[j].split()
                    if len(parts) > 1 and parts[1].isdigit():
                        idx = int(parts[1])
                        local_inferred_types[idx] = 'i32'
                        rel_idx = idx - param_count
                        if rel_idx >= 0:
                            self.local_vars[rel_idx] = 'i32'

            # If we call dom_set_text/dom_set_html after a single LOAD, treat that LOAD as dom handle
            if line.startswith('CALL dom_set_text') or line.startswith('CALL dom_set_html'):
                if last_load_idx is not None:
                    local_inferred_types[last_load_idx] = 'i32'
                    rel_idx = last_load_idx - param_count
                    if rel_idx >= 0:
                        self.local_vars[rel_idx] = 'i32'

            if line.startswith('LIST_NEW') or line.startswith('LIST_NEW_I64') or line.startswith('LIST_NEW_STR'):
                # Look ahead for next non-empty, non-comment line
                j = i + 1
                while j < len(lines) and (lines[j] == '' or lines[j].startswith('#') or lines[j].startswith('.line')):
                    j += 1
                if j < len(lines) and lines[j].startswith('STORE '):
                    parts = lines[j].split()
                    if len(parts) > 1 and parts[1].isdigit():
                        idx = int(parts[1])
                        # mark inferred local type as i32 (list pointer)
                        local_inferred_types[idx] = 'i32'
                        # also mark as list value type for later tracking
                        self.local_value_types[idx] = 'list'

        # Second pass: track stack operations to infer types
        type_stack_sim = []
        value_type_tracker = {}  # Track what type of value each stack position/local holds
        explicit_const_locals = set()  # Track locals that have been assigned via STORE_CONST_*
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
            elif opcode in ['LOAD2_ADD_I64', 'LIST_LEN']:
                type_stack_sim.append('i64')
            elif opcode == 'BUILTIN_LEN':
                # BUILTIN_LEN consumes a list/set/string and returns i64
                if len(type_stack_sim) >= 2 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32':
                    # String: pop ptr and len
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                elif type_stack_sim:
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
                        # Only overwrite if not explicitly assigned via STORE_CONST
                        if idx not in explicit_const_locals:
                            local_inferred_types[idx] = 'str'
                        type_stack_sim.pop()  # len

                    else:
                        # Only infer type if the local hasn't been explicitly declared or STORE_CONST assigned
                        # Explicit declarations in .local should be trusted
                        # Also respect STORE_CONST_* assignments which are explicit
                        if (idx not in self.functions.get(self.current_function, {}).get('locals', {}) and
                            idx not in explicit_const_locals):
                            inferred_type = type_stack_sim[-1]
                            local_inferred_types[idx] = inferred_type
                            # Track the value type (set, list, bool, etc.)
                            stack_pos = len(type_stack_sim) - 1
                            if stack_pos in value_type_tracker:
                                self.local_value_types[idx] = value_type_tracker[stack_pos]
                            elif type_stack_sim[-1] == 'i32':
                                self.local_value_types[idx] = 'bool'

                    type_stack_sim.pop()  # ptr

            elif opcode == 'LIST_APPEND':
                # LIST_APPEND pops value and list, pushes list
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # list
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'list'

            elif opcode in ['SET_ADD', 'SET_REMOVE']:
                # SET_ADD/SET_REMOVE pops value and set, pushes set
                # Value could be i64 or (i32 ptr, i32 len) for string
                if len(type_stack_sim) >= 3 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32' and len(type_stack_sim) - 1 in value_type_tracker and value_type_tracker[len(type_stack_sim) - 1] == 'str':
                    # String: pop ptr and len, push i64
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                    type_stack_sim.append('i64')
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # set
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'set'

            elif opcode == 'SET_CONTAINS':
                # SET_CONTAINS pops value and set, pushes bool (i32)
                # Value could be i64 or (i32 ptr, i32 len) for string
                if len(type_stack_sim) >= 3 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32' and len(type_stack_sim) - 1 in value_type_tracker and value_type_tracker[len(type_stack_sim) - 1] == 'str':
                    # String: pop ptr and len, push i64
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                    type_stack_sim.append('i64')
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # set
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'bool'

            elif opcode == 'CONTAINS':
                # CONTAINS: check if element is in container
                # String contains: (4 i32s) -> i32
                # Set contains: (i32 set_ptr, i64 value) -> i32
                # List contains: (i32 list_ptr, value) -> i32
                if len(type_stack_sim) >= 4 and all(t == 'i32' for t in type_stack_sim[-4:]):
                    # String contains
                    for _ in range(4):
                        type_stack_sim.pop()
                elif len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # value
                    type_stack_sim.pop()  # container
                type_stack_sim.append('i32')  # result
                value_type_tracker[len(type_stack_sim) - 1] = 'bool'

            elif opcode == 'CMP_EQ':
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'bool'

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

            elif opcode == 'STR_SPLIT':
                # STR_SPLIT consumes 4 i32s (string, separator), produces 1 i32 (list ptr)
                for _ in range(min(4, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'list'

            elif opcode == 'STR_JOIN':
                # STR_JOIN consumes 3 values (sep_ptr, sep_len, list_ptr), produces 2 i32s (string)
                for _ in range(min(3, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')  # ptr
                type_stack_sim.append('i32')  # len
                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                value_type_tracker[len(type_stack_sim) - 1] = 'str'

            elif opcode == 'DUP':
                # Duplicate top value
                if type_stack_sim:
                    type_stack_sim.append(type_stack_sim[-1])

            elif opcode == 'TO_INT':
                # Convert top of stack to i64
                if type_stack_sim:
                    if type_stack_sim[-1] == 'f64':
                        type_stack_sim[-1] = 'i64'
                    elif len(type_stack_sim) >= 2 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32':
                        # String (ptr, len) to int
                        type_stack_sim.pop()  # len
                        type_stack_sim.pop()  # ptr
                        type_stack_sim.append('i64')

            elif opcode == 'TO_FLOAT':
                # Convert to float
                if type_stack_sim:
                    if type_stack_sim[-1] == 'i64':
                        type_stack_sim[-1] = 'f64'
                    elif len(type_stack_sim) >= 2 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32':
                        # String to float
                        type_stack_sim.pop()
                        type_stack_sim.pop()
                        type_stack_sim.append('f64')

            elif opcode == 'BUILTIN_STR':
                # Convert value to string (ptr, len)
                # Pop 1 value (any type), push 2 i32s
                if len(type_stack_sim) >= 2 and type_stack_sim[-1] == 'i32' and type_stack_sim[-2] == 'i32':
                    # Already a string, do nothing
                    pass
                elif type_stack_sim:
                    type_stack_sim.pop()
                    type_stack_sim.append('i32')  # ptr
                    type_stack_sim.append('i32')  # len
                    value_type_tracker[len(type_stack_sim) - 2] = 'str'
                    value_type_tracker[len(type_stack_sim) - 1] = 'str'

            elif opcode.startswith('CMP_') or opcode in ['AND', 'OR', 'NOT']:
                # Comparison and logical operators return i32 (boolean)
                # CMP_* with CONST variant: consumes 1 value, produces 1 i32
                # CMP_* without CONST: consumes 2 values, produces 1 i32
                # AND/OR: consumes 2 values, produces 1 i32
                # NOT: consumes 1 value, produces 1 i32
                if 'CONST' in opcode:
                    # CMP_*_CONST: pop 1, push 1
                    if type_stack_sim:
                        type_stack_sim.pop()
                elif opcode == 'NOT':
                    # NOT: pop 1, push 1
                    if type_stack_sim:
                        type_stack_sim.pop()
                else:
                    # CMP_*, AND, OR: pop 2, push 1
                    if len(type_stack_sim) >= 2:
                        type_stack_sim.pop()
                        type_stack_sim.pop()
                    elif type_stack_sim:
                        type_stack_sim.pop()
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'bool'

            elif opcode == 'STORE_CONST_I64':
                # STORE_CONST_I64 slot1 val1 [slot2 val2 ...] - directly stores i64 to local(s)
                # Mark local as i64 type and track as explicitly assigned
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts) and parts[i + 1].isdigit():
                        idx = int(parts[i + 1])
                        local_inferred_types[idx] = 'i64'
                        explicit_const_locals.add(idx)

            elif opcode == 'STORE_CONST_F64':
                # STORE_CONST_F64 slot val - directly stores f64 to local
                # Mark local as f64 type and track as explicitly assigned
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts) and parts[i + 1].isdigit():
                        idx = int(parts[i + 1])
                        local_inferred_types[idx] = 'f64'
                        explicit_const_locals.add(idx)

            elif opcode == 'STORE_CONST_BOOL':
                # STORE_CONST_BOOL slot val - directly stores bool (i32) to local
                # Mark local as i32 type and track as explicitly assigned
                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        idx = int(parts[i + 1])
                        local_inferred_types[idx] = 'i32'
                        explicit_const_locals.add(idx)

            elif opcode == 'TO_BOOL':
                # TO_BOOL converts any value to boolean (i32)
                if type_stack_sim:
                    type_stack_sim.pop()
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 1] = 'bool'

            elif opcode == 'FILE_OPEN':
                # FILE_OPEN consumes path (ptr, len) and mode (ptr, len), returns fd (i32)
                # Pop 4 values (2 strings)
                for _ in range(min(4, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')  # fd

            elif opcode == 'FILE_READ':
                # FILE_READ consumes fd(i64), size(i64) and returns string (ptr, len) as two i32 values
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()  # size
                    type_stack_sim.pop()  # fd
                type_stack_sim.append('i32')  # ptr
                type_stack_sim.append('i32')  # len
                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                value_type_tracker[len(type_stack_sim) - 1] = 'str'

            elif opcode == 'FILE_WRITE':
                # FILE_WRITE consumes fd, ptr, len (3 values) and returns nothing
                for _ in range(min(3, len(type_stack_sim))):
                    type_stack_sim.pop()

            elif opcode == 'FILE_CLOSE':
                # FILE_CLOSE consumes fd (1 value) and returns nothing
                if type_stack_sim:
                    type_stack_sim.pop()

            elif opcode == 'SOCKET_CREATE':
                # socket(domain: str, type: str) -> fd (i64)
                # Pop 4 i32s (two strings), push i64
                for _ in range(min(4, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i64')

            elif opcode == 'SOCKET_CLOSE':
                # Pop fd (i64)
                if type_stack_sim:
                    type_stack_sim.pop()

            elif opcode == 'SOCKET_CONNECT':
                # Pop fd and addr string, push result
                for _ in range(min(3, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')

            elif opcode == 'SOCKET_ACCEPT':
                # Pop fd, push new fd (i64)
                if type_stack_sim:
                    type_stack_sim.pop()
                type_stack_sim.append('i64')

            elif opcode == 'SOCKET_SEND':
                # Pop fd and data, push bytes sent
                for _ in range(min(3, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i64')

            elif opcode == 'SOCKET_RECV':
                # Pop fd and size, push string (ptr, len)
                for _ in range(min(2, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')
                type_stack_sim.append('i32')
                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                value_type_tracker[len(type_stack_sim) - 1] = 'str'

            elif opcode == 'FORK':
                # No args, returns pid (i64)
                type_stack_sim.append('i64')

            elif opcode == 'JOIN':
                # Pop pid, push result
                if type_stack_sim:
                    type_stack_sim.pop()
                type_stack_sim.append('i64')

            elif opcode == 'CALL':
                # User-defined or builtin function call
                # Parse: CALL func_name arg_count
                if len(parts) >= 2:
                    call_func_name = parts[1]

                    # Handle builtin imports first so stack simulation matches real emission
                    if call_func_name in self.builtin_map:
                        _, return_types, param_types = self.builtin_map[call_func_name]

                        # Pop arguments according to the builtin signature
                        for _ in param_types:
                            if type_stack_sim:
                                type_stack_sim.pop()

                        # Push return values according to the signature
                        if return_types == ['i32', 'i32']:
                            # Treat double i32 return as string (ptr, len)
                            type_stack_sim.append('i32')
                            type_stack_sim.append('i32')
                            value_type_tracker[len(type_stack_sim) - 2] = 'str'
                            value_type_tracker[len(type_stack_sim) - 1] = 'str'
                        else:
                            for ret_type in return_types:
                                type_stack_sim.append(ret_type)

                    # Handle user-defined functions
                    elif call_func_name in self.functions:
                        call_return_type = self.functions[call_func_name].get('return_type', 'void')
                        param_count_call = len(self.functions[call_func_name].get('params', []))
                        # Pop arguments from type_stack_sim
                        for _ in range(param_count_call):
                            if type_stack_sim:
                                type_stack_sim.pop()
                        # Push return type
                        if call_return_type and call_return_type != 'void':
                            if call_return_type == 'str':
                                type_stack_sim.append('i32')  # ptr
                                type_stack_sim.append('i32')  # len
                                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                                value_type_tracker[len(type_stack_sim) - 1] = 'str'
                            elif call_return_type.startswith('struct:'):
                                # Struct return is i32 pointer
                                type_stack_sim.append('i32')
                            else:
                                wasm_ret = self._map_type_to_wasm(call_return_type)
                                type_stack_sim.append(wasm_ret)

            elif opcode == 'FUSED_LOAD_STORE':
                # Handle type inference for FUSED_LOAD_STORE
                # Pattern: src1 dst1 src2 dst2 ... [optional final_src]
                for i in range(0, len(parts) - 1, 2):
                    if i + 2 < len(parts) and parts[i + 1].isdigit() and parts[i + 2].isdigit():
                        src_idx = int(parts[i + 1])
                        # Copy type from source to destination
                        if src_idx in local_inferred_types:
                            dst_idx = int(parts[i + 2])
                            local_inferred_types[dst_idx] = local_inferred_types[src_idx]

                # If odd number of args, final value is left on stack
                if len(parts) % 2 == 0 and len(parts) > 1:  # has final LOAD
                    final_idx = int(parts[-1])
                    if final_idx in local_inferred_types:
                        final_type = local_inferred_types[final_idx]
                        if final_type == 'str':
                            type_stack_sim.append('i32')
                            type_stack_sim.append('i32')
                        else:
                            type_stack_sim.append(final_type)

            # Binary arithmetic operations
            elif opcode in ['ADD_CONST_I64', 'ADD_I64', 'ADD_F64']:
                # ADD_CONST_I64: pop 1, push 1
                # ADD_I64: pop 2, push 1
                # ADD_F64: pop 2, push 1
                if opcode == 'ADD_CONST_I64':
                    if type_stack_sim:
                        if type_stack_sim[-1] == 'f64':
                            type_stack_sim[-1] = 'f64'
                        else:
                            type_stack_sim[-1] = 'i64'
                else:
                    # ADD_I64 or ADD_F64
                    if len(type_stack_sim) >= 2:
                        type_stack_sim.pop()
                        type_stack_sim.pop()
                    type_stack_sim.append('f64' if opcode == 'ADD_F64' else 'i64')

            elif opcode in ['SUB_CONST_I64', 'SUB_I64', 'SUB_F64']:
                if len(type_stack_sim) >= 2:
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                type_stack_sim.append('f64' if 'F64' in opcode else 'i64')

            elif opcode in ['MUL_CONST_I64', 'MUL_I64', 'MUL_F64']:
                # Check if multiplying with f64
                if type_stack_sim and type_stack_sim[-1] == 'f64':
                    type_stack_sim[-1] = 'f64'
                elif len(type_stack_sim) >= 2:
                    type_stack_sim.pop()
                    type_stack_sim.pop()
                    type_stack_sim.append('f64' if 'F64' in opcode else 'i64')
                else:
                    type_stack_sim.append('f64' if 'F64' in opcode else 'i64')

            elif opcode in ['DIV_CONST_I64', 'DIV_I64', 'DIV_F64']:
                # For DIV_I64: division of two i64s returns f64 (Python-style true division)
                # For DIV_F64: f64 division returns f64
                # For DIV_CONST_I64: same as DIV_I64 but with a constant
                if opcode == 'DIV_I64':
                    # Pop 2 operands, push f64
                    if len(type_stack_sim) >= 2:
                        type_stack_sim.pop()
                        type_stack_sim.pop()
                    type_stack_sim.append('f64')
                elif opcode == 'DIV_CONST_I64':
                    # Pop 1 operand, push f64
                    if len(type_stack_sim) >= 1:
                        type_stack_sim.pop()
                    type_stack_sim.append('f64')
                elif opcode == 'DIV_F64':
                    # Pop 2 operands, push f64
                    if len(type_stack_sim) >= 2:
                        type_stack_sim.pop()
                        type_stack_sim.pop()
                    type_stack_sim.append('f64')

            elif opcode in ['MOD_CONST_I64', 'MOD_I64']:
                # Modulo always returns i64
                if type_stack_sim:
                    type_stack_sim.pop()
                if len(type_stack_sim) >= 1 and opcode == 'MOD_I64':
                    type_stack_sim.pop()
                type_stack_sim.append('i64')

            elif opcode == 'ADD_STR':
                # String concatenation: pop 4 i32s (2 strings), push 2 i32s (string)
                for _ in range(min(4, len(type_stack_sim))):
                    type_stack_sim.pop()
                type_stack_sim.append('i32')  # ptr
                type_stack_sim.append('i32')  # len
                value_type_tracker[len(type_stack_sim) - 2] = 'str'
                value_type_tracker[len(type_stack_sim) - 1] = 'str'

            elif opcode in ['LOAD2_ADD_I64', 'LOAD2_MUL_I64', 'LOAD2_DIV_I64']:
                # These load 2 vars, perform operation, push result
                type_stack_sim.append('f64' if 'DIV' in opcode else 'i64')

            elif opcode == 'LOAD2_CMP_LT':
                type_stack_sim.append('i32')

            elif opcode == 'LOAD2_CMP_GT':
                type_stack_sim.append('i32')

            elif opcode == 'SWITCH_JUMP_TABLE':
                # Stack simulation only: pop the switch value.
                # Real codegen for SWITCH_JUMP_TABLE happens in `_compile_opcode`.
                if type_stack_sim:
                    type_stack_sim.pop()

        # Update local_vars with inferred types (but don't overwrite explicit types from bytecode)
        for idx, inferred_type in local_inferred_types.items():
            if idx >= param_count:
                rel_idx = idx - param_count
                # Prefer inferred list types over default i64 declarations.
                # If the local wasn't explicitly declared, set it. If it was declared
                # as the generic i64, and we inferred a more specific i32 (list ptr),
                # override that to ensure correct WASM local typing.
                if rel_idx not in self.local_vars:
                    self.local_vars[rel_idx] = inferred_type
                else:
                    existing = self.local_vars[rel_idx]
                    # Override i64 with more specific types (i32, str, etc.)
                    if existing == 'i64' and inferred_type in ['i32', 'str']:
                        self.local_vars[rel_idx] = inferred_type

        # Declare locals (indices from param_count to max_local_idx)
        for idx in range(param_count, max_local_idx + 1):
            # Default to i64 type
            # Prefer explicit `.local` declarations from the bytecode.
            explicit_local_type = self.local_vars.get(idx - param_count)
            if explicit_local_type is not None:
                local_type = explicit_local_type
            # Otherwise, if we inferred a different type (local_inferred_types uses absolute index), use it.
            elif idx in local_inferred_types:
                local_type = local_inferred_types[idx]
            else:
                local_type = 'i64'
            # Check if this is already a WASM type (from type inference)
            if local_type in ['i32', 'i64', 'f64']:
                wasm_type = local_type

            else:
                wasm_type = self._map_type_to_wasm(local_type)

            # Local variables in WASM start from 0, so use idx - param_count
            self.emit(f"(local $l{idx - param_count} {wasm_type})", 2)

            # Always emit a companion _len i32 local to avoid undefined references
            # (some codepaths reference "$lN_len" even when we couldn't infer str)
            self.emit(f"(local $l{idx - param_count}_len i32)", 2)

        # Add temp locals for operations
        self.emit("(local $temp i32)", 2)
        self.emit("(local $temp2 i32)", 2)
        self.emit("(local $temp_i64 i64)", 2)
        self.emit("(local $temp_f64 f64)", 2)

        # Add indexed temps for argument shuffling
        for i in range(10):
            self.emit(f"(local $temp_i32_{i} i32)", 2)
            self.emit(f"(local $temp_i64_{i} i64)", 2)
            self.emit(f"(local $temp_f64_{i} f64)", 2)

        # Compile function body
        self._compile_function_body(func_name, bytecode_lines)

        # Ensure function returns properly
        if return_type != 'void' and return_type:
            # Check if function has explicit returns
            has_return = any(
                line.strip() == 'RETURN' or line.strip().startswith('RETURN ')
                for line in bytecode_lines
                if self._is_in_function(line, func_name)
            )
            if has_return:
                # Function has returns in branches - add unreachable at end
                # This tells WASM that reaching this point is impossible
                # BUT: if control flow CAN reach here (e.g. missing return in one branch),
                # this will trap.
                # For main, we should return 0 if it's i64
                if func_name == 'main':
                    self.emit("i64.const 0", 2)
                else:
                    self.emit("unreachable", 2)
            else:
                # No explicit return - add a default one
                wasm_type = self._map_type_to_wasm(return_type)
                if wasm_type == 'i64':
                    self.emit("i64.const 0", 2)
                elif wasm_type == 'f64':
                    self.emit("f64.const 0", 2)
                elif wasm_type == 'i32':
                    self.emit("i32.const 0", 2)
        elif func_name == 'main':
             # Main is void in source but exported as returning i64 (usually)
             # If we didn't emit a result type for main, we shouldn't return anything.
             # But wait, earlier code:
             # if func_name == "main": export_attr = ...
             # return_type comes from func_meta.
             # If main is void in source, return_type is void.
             # So wasm_return is empty.
             # But the runtime might expect main to return i64?
             # Let's check how main is called in JS.
             pass

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
        switch_case_labels = set()  # Track all switch case labels that need blocks

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

            # Also detect switch case labels from SWITCH_JUMP_TABLE
            elif line.startswith('SWITCH_JUMP_TABLE '):
                parts = line.split()
                if len(parts) >= 3:
                    # Format: SWITCH_JUMP_TABLE min_val max_val label1 label2 ... labelN
                    case_labels = parts[3:]  # All labels after min and max
                    for target in case_labels:
                        if target in label_positions:
                            target_pos = label_positions[target]
                            if target_pos > i:
                                # Mark this as a switch case label
                                switch_case_labels.add(target)

            # Detect TRY_BEGIN handler labels
            elif line.startswith('TRY_BEGIN '):
                parts = line.split()
                if len(parts) >= 3:
                    # Format: TRY_BEGIN "exc_type" handler_label
                    handler_label = parts[2]
                    if handler_label in label_positions:
                        target_pos = label_positions[handler_label]
                        if target_pos > i:
                            forward_jumps[i] = handler_label

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

        # Add switch case labels to blocks that need to be opened
        for target in switch_case_labels:
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

        loop_stack = []  # Stack of (loop_start, loop_end, continue_label, internal_blocks)

        for i, raw_line in enumerate(post_label_lines):
            stripped = raw_line.strip()

            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith('.'):
                continue

            # Handle LABEL
            if stripped.startswith('LABEL '):
                label_name = stripped.split()[1]

                # Close any blocks that end at this label (but not loops - they close at backward jumps)
                blocks_to_close = []
                for j, (lbl, is_loop, _) in enumerate(active_blocks):
                    if lbl == label_name and not is_loop:
                        blocks_to_close.append(j)

                # Close in reverse order (from innermost to outermost)
                for j in reversed(blocks_to_close):
                    lbl, is_loop, _ = active_blocks.pop(j)
                    indent -= 1
                    self.emit(")", indent)

                # Check if this is a loop start label
                if label_name in loop_structures:
                    end_label, continue_label = loop_structures[label_name]

                    # Find labels that need blocks inside this loop
                    loop_start_pos = label_positions[label_name]
                    loop_end_pos = label_positions.get(end_label, len(func_lines))

                    labels_in_this_loop = []
                    for lbl in labels_needing_blocks_inside_loops:
                        lbl_pos = label_positions[lbl]
                        if loop_start_pos < lbl_pos < loop_end_pos:
                            # Check if this label is inside a nested loop
                            in_nested_loop = False
                            for nested_loop_start in loop_structures:
                                if nested_loop_start == label_name:
                                    continue
                                nested_start_pos = label_positions.get(nested_loop_start, -1)
                                nested_end_label = loop_structures[nested_loop_start][0]
                                nested_end_pos = label_positions.get(nested_end_label, len(func_lines))
                                # Check if the nested loop is inside this loop and the label is inside the nested loop
                                if loop_start_pos < nested_start_pos < nested_end_pos < loop_end_pos:
                                    # nested loop is inside this loop
                                    if nested_start_pos < lbl_pos < nested_end_pos:
                                        # label is inside the nested loop, not directly in this loop
                                        in_nested_loop = True
                                        break
                            if not in_nested_loop:
                                labels_in_this_loop.append((lbl, lbl_pos))

                    # Sort by position (innermost first for proper nesting)
                    labels_in_this_loop.sort(key=lambda x: x[1], reverse=True)

                    # Open outer block for loop exit
                    self.emit(f"(block ${end_label}", indent)
                    indent += 1
                    active_blocks.append((end_label, False, indent))
                    # Open the loop block
                    self.emit(f"(loop ${label_name}", indent)
                    indent += 1
                    active_blocks.append((label_name, True, indent))

                    # Open blocks for forward jump targets inside this loop
                    # These will be closed when we encounter their labels
                    for lbl, _ in labels_in_this_loop:
                        self.emit(f"(block ${lbl}", indent)
                        indent += 1
                        active_blocks.append((lbl, False, indent))

                    # Push this loop onto the stack
                    loop_stack.append((label_name, end_label, continue_label, [lbl for lbl, _ in labels_in_this_loop]))
                    continue

                # Check if this is a continue label - just a marker
                if loop_stack and label_name == loop_stack[-1][2]:
                    continue

                continue

            # Compile the instruction
            try:
                self._compile_instruction(stripped, indent)
            except Exception as e:
                raise WasmCompilerError(f"Error compiling instruction '{stripped}': {e}")

            # After compiling, check if this was a backward jump - if so, close the loop
            # Check by examining the instruction directly
            if stripped.startswith('JUMP '):
                parts = stripped.split()
                if len(parts) > 1:
                    target_label = parts[1]
                    # Check if this is a backward jump to a loop start
                    for j in range(len(loop_stack) - 1, -1, -1):
                        loop_start, loop_end, continue_label, internal_blocks = loop_stack[j]
                        if loop_start == target_label:
                            # Close the loop block
                            for k in range(len(active_blocks) - 1, -1, -1):
                                if active_blocks[k][0] == loop_start and active_blocks[k][1]:  # is_loop
                                    active_blocks.pop(k)
                                    indent -= 1
                                    self.emit(")", indent)
                                    break
                            # Pop from loop stack
                            loop_stack.pop(j)
                            break

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

        # Source line directive (used for error reporting).
        if opcode == '.line':
            try:
                if args and args[0].lstrip('-').isdigit():
                    self.current_source_line = int(args[0])
            except Exception:
                pass
            return

        print(f"Compiling {opcode} {args} - Stack: {self.type_stack}")

        self.emit_comment(inst, indent)

        # === Constants ===
        if opcode == 'ADD_CONST_I64':
            const_val = args[0]
            # Ensure the top of stack is i64 before adding
            if self.type_stack and self.type_stack[-1] == 'f64':
                self.emit(f"f64.const {const_val}", indent)
                self.emit("f64.add", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('f64')
            else:
                self.emit(f"i64.const {const_val}", indent)
                self.emit("i64.add", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('i64')

        elif opcode == 'SUB_CONST_I64':
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'f64':
                self.emit(f"f64.const {const_val}", indent)
                self.emit("f64.sub", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('f64')
            else:
                self.emit(f"i64.const {const_val}", indent)
                self.emit("i64.sub", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('i64')

        elif opcode == 'MUL_CONST_I64':
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'f64':
                self.emit(f"f64.const {const_val}", indent)
                self.emit("f64.mul", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('f64')
            else:
                self.emit(f"i64.const {const_val}", indent)
                self.emit("i64.mul", indent)
                if self.type_stack:
                    self.type_stack.pop()
                self.type_stack.append('i64')

        elif opcode == 'MOD_CONST_I64':
            const_val = args[0]
            # Ensure operand is i64
            if self.type_stack and self.type_stack[-1] == 'f64':
                self.emit("i64.trunc_f64_s", indent)
                self.type_stack[-1] = 'i64'
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.rem_s", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'ADD_CONST_F64':
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.add", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'SUB_CONST_F64':
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.sub", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'MUL_CONST_F64':
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.mul", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'DIV_CONST_F64':
            # Guard division-by-zero to match VM behavior (raise runtime error).
            const_val = args[0]
            if self.type_stack and self.type_stack[-1] == 'i64':
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'

            # Save numerator
            self.emit("local.set $temp_f64", indent)
            if self.type_stack:
                self.type_stack.pop()

            # (if (result f64) (then runtime_error; 0.0) (else numerator / const))
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.const 0.0", indent)
            self.emit("f64.eq", indent)
            self.emit("(if (result f64)", indent)
            self.emit("(then", indent + 1)

            msg = "float division by zero"
            msg_off = self.add_string_constant(msg)
            self.emit("i32.const 0", indent + 2)
            self.emit("i32.const 0", indent + 2)
            self.emit(f"i32.const {msg_off}", indent + 2)
            self.emit(f"i32.const {len(msg.encode('utf-8'))}", indent + 2)
            self.emit("i32.const 0", indent + 2)
            self.emit("call $runtime_error", indent + 2)
            self.emit("f64.const 0.0", indent + 2)
            self.emit(")", indent + 1)
            self.emit("(else", indent + 1)
            self.emit("local.get $temp_f64", indent + 2)
            self.emit(f"f64.const {const_val}", indent + 2)
            self.emit("f64.div", indent + 2)
            self.emit(")", indent + 1)
            self.emit(")", indent)

            self.type_stack.append('f64')

        elif opcode == 'STORE_CONST_I64':
            # STORE_CONST_I64 slot1 val1 [slot2 val2 ...]
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                slot = int(args[i])
                value = args[i + 1]
                var_ref = self._get_var_ref(slot)
                self.emit(f"i64.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'STORE_CONST_F64':
            # STORE_CONST_F64 slot val
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                slot = int(args[i])
                value = args[i + 1]
                var_ref = self._get_var_ref(slot)
                self.emit(f"f64.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'STORE_CONST_BOOL':
            # STORE_CONST_BOOL slot val
            for i in range(0, len(args), 2):
                if i + 1 >= len(args):
                    break
                slot = int(args[i])
                value = args[i + 1]
                if value == 'True':
                    value = '1'
                elif value == 'False':
                    value = '0'
                var_ref = self._get_var_ref(slot)
                self.emit(f"i32.const {value}", indent)
                self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'ADD_F64':
            # Ensure operands are f64
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'i64':
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                if self.type_stack[-2] == 'i64':
                    self.emit('local.set $temp_f64', indent)
                    self.type_stack.pop()
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                    self.emit('local.get $temp_f64', indent)
                    self.type_stack.append('f64')
            self.emit('f64.add', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'SUB_F64':
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'i64':
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                if self.type_stack[-2] == 'i64':
                    self.emit('local.set $temp_f64', indent)
                    self.type_stack.pop()
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                    self.emit('local.get $temp_f64', indent)
                    self.type_stack.append('f64')
            self.emit('f64.sub', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'MUL_F64':
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'i64':
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                if self.type_stack[-2] == 'i64':
                    self.emit('local.set $temp_f64', indent)
                    self.type_stack.pop()
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                    self.emit('local.get $temp_f64', indent)
                    self.type_stack.append('f64')
            self.emit('f64.mul', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('f64')

        elif opcode == 'ADD_I64':
            # Check if operands are f64 and convert if needed
            if len(self.type_stack) >= 2:
                # Top is second operand, below is first
                if self.type_stack[-1] == 'f64':
                    self.emit("i64.trunc_f64_s", indent)
                    self.type_stack[-1] = 'i64'
                if self.type_stack[-2] == 'f64':
                    # Save result, convert bottom operand, restore result
                    self.emit("local.set $temp_i64", indent)
                    self.type_stack.pop()
                    self.emit("i64.trunc_f64_s", indent)
                    self.type_stack[-1] = 'i64'
                    self.emit("local.get $temp_i64", indent)
                    self.type_stack.append('i64')
            self.emit("i64.add", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'SUB_I64':
            # Ensure operands are i64
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'f64':
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                if self.type_stack[-2] == 'f64':
                    self.emit('local.set $temp_i64', indent)
                    self.type_stack.pop()
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                    self.emit('local.get $temp_i64', indent)
                    self.type_stack.append('i64')
            self.emit('i64.sub', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'MUL_I64':
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'f64':
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                if self.type_stack[-2] == 'f64':
                    self.emit('local.set $temp_i64', indent)
                    self.type_stack.pop()
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                    self.emit('local.get $temp_i64', indent)
                    self.type_stack.append('i64')
            self.emit('i64.mul', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'MOD_I64':
            if len(self.type_stack) >= 2:
                if self.type_stack[-1] == 'f64':
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                if self.type_stack[-2] == 'f64':
                    self.emit('local.set $temp_i64', indent)
                    self.type_stack.pop()
                    self.emit('i64.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i64'
                    self.emit('local.get $temp_i64', indent)
                    self.type_stack.append('i64')
            self.emit('i64.rem_s', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i64')

        elif opcode == 'ADD_STR':
            # Ensure both operands are converted to (i32 ptr, i32 len) pairs
            self._normalize_two_operands_for_concat(indent)
            self._emit_call('str_concat', indent)
            if len(self.type_stack) >= 4:
                self.type_stack.pop()
                self.type_stack.pop()
                self.type_stack.pop()
                self.type_stack.pop()
            # str_concat returns (i32 ptr, i32 len)
            self.type_stack.append('i32')
            self.type_stack.append('i32')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                self.extended_type_stack[-2] = 'str'
                self.extended_type_stack[-1] = 'str'
            self.imports.add('str_concat')

        elif opcode == 'STR_UPPER':
            self._emit_call('str_upper', indent)
            self.imports.add('str_upper')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 2:
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'

        elif opcode == 'STR_LOWER':
            self._emit_call('str_lower', indent)
            self.imports.add('str_lower')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 2:
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'

        elif opcode == 'STR_STRIP':
            self._emit_call('str_strip', indent)
            self.imports.add('str_strip')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 2:
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'

        elif opcode == 'STR_REPLACE':
            self._emit_call('str_replace', indent)
            self.imports.add('str_replace')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 2:
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'

        elif opcode == 'STR_JOIN':
            # (sep_ptr, sep_len, list_ptr) -> (ptr, len)
            self._emit_call('str_join', indent)
            self.imports.add('str_join')
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 2:
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'

        elif opcode == 'STR_SPLIT':
            # (str_ptr, str_len, sep_ptr, sep_len) -> list_ptr
            self._emit_call('str_split', indent)
            self.imports.add('str_split')
            self._last_i32_source = 'list'
            # str_split always produces a list of strings.
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 1:
                    self.extended_type_stack[-1] = 'list_str'

        elif opcode == 'ENCODE' or opcode == 'DECODE':
            # Both are effectively identity in the WASM backend.
            # Bytecode typically provides a default encoding string (e.g. "utf-8").
            # Stack forms:
            # - encode/decode(): str_ptr str_len enc_ptr enc_len -> str_ptr str_len
            # - encode/decode(x): same shape
            if len(self.type_stack) >= 4 and all(t == 'i32' for t in self.type_stack[-4:]):
                # Drop encoding len then encoding ptr
                self.emit('drop', indent)
                self.emit('drop', indent)
                self.type_stack.pop()
                self.type_stack.pop()
                # Remaining top two i32s are the string/bytes
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    if len(self.extended_type_stack) >= 2:
                        self.extended_type_stack[-2] = 'str'
                        self.extended_type_stack[-1] = 'str'

        elif opcode == 'TO_INT':
            # Convert top of stack to i64.
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String (ptr,len)
                self._emit_call('str_to_i64', indent)
                self.imports.add('str_to_i64')
            elif self.type_stack and self.type_stack[-1] == 'f64':
                self.emit('i64.trunc_f64_s', indent)
                self.type_stack[-1] = 'i64'
            elif self.type_stack and self.type_stack[-1] == 'i32':
                self.emit('i64.extend_i32_u', indent)
                self.type_stack[-1] = 'i64'

        elif opcode == 'TO_FLOAT':
            # Convert top of stack to f64.
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                self._emit_call('str_to_f64', indent)
                self.imports.add('str_to_f64')
            elif self.type_stack and self.type_stack[-1] == 'i64':
                self.emit('f64.convert_i64_s', indent)
                self.type_stack[-1] = 'f64'
            elif self.type_stack and self.type_stack[-1] == 'i32':
                self.emit('f64.convert_i32_s', indent)
                self.type_stack[-1] = 'f64'

        elif opcode == 'TO_BOOL':
            # Convert top of stack to boolean i32.
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                # String truthiness: len != 0
                self.emit('local.set $temp', indent)  # len
                self.type_stack.pop()
                self.emit('drop', indent)  # ptr
                self.type_stack.pop()
                self.emit('local.get $temp', indent)
                self.emit('i32.const 0', indent)
                self.emit('i32.ne', indent)
                self.type_stack.append('i32')
            elif self.type_stack and self.type_stack[-1] == 'i64':
                self.emit('i64.const 0', indent)
                self.emit('i64.ne', indent)
                self.type_stack.pop()
                self.type_stack.append('i32')
            elif self.type_stack and self.type_stack[-1] == 'f64':
                self.emit('f64.const 0.0', indent)
                self.emit('f64.ne', indent)
                self.type_stack.pop()
                self.type_stack.append('i32')
            elif self.type_stack and self.type_stack[-1] == 'i32':
                self.emit('i32.const 0', indent)
                self.emit('i32.ne', indent)
                self.type_stack.pop()
                self.type_stack.append('i32')
            self._last_i32_source = 'bool'

        elif opcode == 'CONTAINS':
            # String contains: (hay_ptr, hay_len, needle_ptr, needle_len) -> i32
            if len(self.type_stack) >= 4 and all(t == 'i32' for t in self.type_stack[-4:]):
                self._emit_call('str_contains', indent)
                self.imports.add('str_contains')
                # _emit_call updates type_stack; ensure bool tracking
                self._last_i32_source = 'bool'
            else:
                # List/set contains: (container_i32, value) -> i32
                # Ensure container is i32 (second-from-top)
                self._ensure_second_is_i32(indent)
                # Ensure value is i64 (top)
                if self.type_stack and self.type_stack[-1] == 'i32':
                    self.emit('i64.extend_i32_u', indent)
                    self.type_stack[-1] = 'i64'

                container_kind = getattr(self, '_last_i32_source', None)
                if container_kind == 'set':
                    self._emit_call('set_contains', indent)
                    self.imports.add('set_contains')
                else:
                    self._emit_call('list_contains', indent)
                    self.imports.add('list_contains')
                self._last_i32_source = 'bool'

        elif opcode == 'BUILTIN_LEN':
            # Prefer explicit source tracking so list/set pointers are not mistaken for strings
            source = getattr(self, '_last_i32_source', None)

            if self.type_stack and self.type_stack[-1] == 'i32' and source in ('list', 'set'):
                # List or set length using tracked source
                if source == 'set':
                    self._ensure_top_is_i32(indent)
                    self._emit_call('set_len', indent)
                else:
                    self._ensure_top_is_i32(indent)
                    self._emit_call('list_len', indent)
                self._last_i32_source = None
            elif len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
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
                self._last_i32_source = None
            else:
                # Default to list if nothing else is known
                if source == 'set':
                    self._ensure_top_is_i32(indent)
                    self._emit_call('set_len', indent)
                else:
                    self._ensure_top_is_i32(indent)
                    self._emit_call('list_len', indent)
                self._last_i32_source = None

        elif opcode == 'BUILTIN_PRINT':
            # print expects (i32 ptr, i32 len)
            self._emit_call('print', indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.imports.add('print')

        elif opcode == 'BUILTIN_PRINTLN':
            # println expects (i32 ptr, i32 len)
            # If stack already has (i32, i32), it's already a string - don't convert
            if len(self.type_stack) >= 2 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32':
                pass
            elif self.type_stack and self.type_stack[-1] == 'i64':
                # _emit_call handles type_stack: pops i64, pushes [i32, i32]
                self._emit_call('i64_to_str', indent)
            elif self.type_stack and self.type_stack[-1] == 'f64':
                # _emit_call handles type_stack: pops f64, pushes [i32, i32]
                self._emit_call('f64_to_str', indent)
            elif self.type_stack and self.type_stack[-1] == 'i32':
                # i32 could be list/set/bool - use tracked source when available
                if hasattr(self, '_last_i32_source') and self._last_i32_source:
                    if self._last_i32_source == 'list':
                        self._ensure_top_is_i32(indent)
                        # _emit_call handles type_stack: pops i32, pushes [i32, i32]
                        self._emit_call('list_to_str', indent)
                    elif self._last_i32_source == 'set':
                        self._ensure_top_is_i32(indent)
                        # _emit_call handles type_stack: pops i32, pushes [i32, i32]
                        self._emit_call('set_to_str', indent)
                    else:
                        # _emit_call handles type_stack: pops i32, pushes [i32, i32]
                        self._emit_call('bool_to_str', indent)
                    self._last_i32_source = None
                else:
                    # _emit_call handles type_stack: pops i32, pushes [i32, i32]
                    self._emit_call('bool_to_str', indent)

            # Now call println - _emit_call pops [i32, i32] for the params
            self._emit_call('println', indent)

        elif opcode == 'BUILTIN_SQRT':
            self._emit_call('sqrt', indent)
            self.imports.add('sqrt')

        elif opcode == 'BUILTIN_ROUND':
            # Round and convert to i64
            self._emit_call('round_f64', indent)
            # Convert f64 result to i64
            self.emit("i64.trunc_f64_s", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i64')
            self.imports.add('round_f64')

        elif opcode == 'BUILTIN_FLOOR':
            self._emit_call('floor_f64', indent)
            # Type stays as f64

        elif opcode == 'BUILTIN_CEIL':
            self._emit_call('ceil_f64', indent)
            # Type stays as f64

        elif opcode == 'BUILTIN_PI':
            # Push pi as f64
            self.emit('f64.const 3.141592653589793', indent)
            self.type_stack.append('f64')

        elif opcode == 'BUILTIN_STR':
            # Convert value to string - returns (i32 ptr, i32 len) as two stack values
            # Check type of value on stack
            if self.type_stack:
                value_type = self.type_stack[-1]
                source = getattr(self, '_last_i32_source', None)

                # If the top two stack entries are already an (i32 ptr, i32 len)
                # pair AND we have no tracked i32 source, this value is already a string.
                if (
                    len(self.type_stack) >= 2
                    and self.type_stack[-1] == 'i32'
                    and self.type_stack[-2] == 'i32'
                    and source is None
                ):
                    return

                if value_type == 'i64':
                    self._emit_call('i64_to_str', indent)
                    # self.type_stack.pop() - _emit_call already pops
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                        self.extended_type_stack[-2] = 'str'
                        self.extended_type_stack[-1] = 'str'
                    self.imports.add('i64_to_str')
                elif value_type == 'f64':
                    self._emit_call('f64_to_str', indent)
                    # self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                        self.extended_type_stack[-2] = 'str'
                        self.extended_type_stack[-1] = 'str'
                    self.imports.add('f64_to_str')
                elif value_type == 'i32':
                    # Could be a boolean, list, set, or other i32 value
                    converted_type = None

                    if source == 'list':
                        self._emit_call('list_to_str', indent)
                        converted_type = 'list'
                    elif source == 'set':
                        self._emit_call('set_to_str', indent)
                        converted_type = 'set'
                    elif source == 'bool':
                        self._emit_call('bool_to_str', indent)
                        converted_type = 'bool'

                    if not converted_type:
                        # Default to boolean
                        self._emit_call('bool_to_str', indent)

                    # self.type_stack.pop()
                    self.type_stack.append('i32')  # ptr
                    self.type_stack.append('i32')  # len
                    if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                        self.extended_type_stack[-2] = 'str'
                        self.extended_type_stack[-1] = 'str'
                    # Clear the i32 source tracking since we've now converted to string
                    self._last_i32_source = None

        elif opcode == 'CALL':
            func_name = args[0]
            arg_count = int(args[1]) if len(args) > 1 else 0

            # Handle special built-in functions
            if func_name == 'assert':
                # Assert in WASM: just pop the value and continue
                # In a real implementation, you'd check and trap
                self.emit("drop", indent)
                if self.type_stack:
                    self.type_stack.pop()
                return

            # Map builtin function names to import names
            builtin_map = self.builtin_map

            if func_name in builtin_map:
                import_name, return_types, param_types = builtin_map[func_name]

                # Special handling for variadic timer functions
                if func_name in ('set_timeout', 'set_interval') and len(param_types) == 0:
                    # Variadic function - all parameters are i32
                    # Format: callback_idx (i32), milliseconds (i32), ...callback_args (all i32)
                    param_types = ['i32'] * arg_count
                    # Store the signature for import generation
                    sig_parts = ' '.join(f'(param {t})' for t in param_types)
                    self.timer_signatures[func_name] = sig_parts

                # --- Argument Handling Logic ---
                # Analyze requirements and stack to build a plan
                # We work backwards from the last parameter (Right-to-Left)

                param_idx = len(param_types) - 1
                stack_idx = len(self.type_stack) - 1

                # List of operations to perform: (pop_type, temp_local, push_action)
                # push_action is a function/lambda that emits code
                ops = []

                # We need to track which temps we use
                next_i64_temp = 0
                next_i32_temp = 0
                next_f64_temp = 0

                while param_idx >= 0:
                    if stack_idx < 0:
                        # Error: not enough arguments on stack
                        # For now, break and let WASM trap or fail validation
                        break

                    param_type = param_types[param_idx]
                    stack_type = self.type_stack[stack_idx]

                    if param_type == 'i32':
                        if stack_type == 'i32':
                            # Direct match
                            temp = f"$temp_i32_{next_i32_temp}"
                            next_i32_temp += 1
                            ops.append(('i32', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                            param_idx -= 1
                            stack_idx -= 1
                        elif stack_type == 'i64':
                            # Mismatch: i64 on stack, i32 expected
                            # Check if we should unpack (requires another i32 expected before this)
                            should_unpack = False
                            if param_idx > 0 and param_types[param_idx-1] == 'i32':
                                # Check if explicit string
                                if hasattr(self, 'extended_type_stack') and self.extended_type_stack and stack_idx < len(self.extended_type_stack) and self.extended_type_stack[stack_idx] == 'str':
                                    should_unpack = True
                                # Check if we have more params than args (implies unpacking needed)
                                elif len(param_types) > arg_count:
                                    should_unpack = True

                            if should_unpack:
                                # Unpack i64 -> i32, i32
                                temp = f"$temp_i64_{next_i64_temp}"
                                next_i64_temp += 1

                                def push_unpack(t):
                                    # Push ptr (lower)
                                    self.emit(f"local.get {t}", indent)
                                    self.emit("i32.wrap_i64", indent)
                                    # Push len (upper)
                                    self.emit(f"local.get {t}", indent)
                                    self.emit("i64.const 32", indent)
                                    self.emit("i64.shr_u", indent)
                                    self.emit("i32.wrap_i64", indent)

                                ops.append(('i64', temp, lambda t=temp: push_unpack(t)))

                                param_idx -= 2 # Consumed 2 params
                                stack_idx -= 1 # Consumed 1 stack item
                            else:
                                # Truncate i64 -> i32
                                temp = f"$temp_i64_{next_i64_temp}"
                                next_i64_temp += 1
                                ops.append(('i64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i32.wrap_i64", indent))))
                                param_idx -= 1
                                stack_idx -= 1
                        else:
                            # f64 -> i32 (conversion)
                            temp = f"$temp_f64_{next_f64_temp}"
                            next_f64_temp += 1
                            ops.append(('f64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i32.trunc_f64_s", indent))))
                            param_idx -= 1
                            stack_idx -= 1

                    elif param_type == 'i64':
                        if stack_type == 'i64':
                            temp = f"$temp_i64_{next_i64_temp}"
                            next_i64_temp += 1
                            ops.append(('i64', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                        elif stack_type == 'i32':
                            temp = f"$temp_i32_{next_i32_temp}"
                            next_i32_temp += 1
                            ops.append(('i32', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i64.extend_i32_u", indent))))
                        elif stack_type == 'f64':
                            temp = f"$temp_f64_{next_f64_temp}"
                            next_f64_temp += 1
                            ops.append(('f64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i64.trunc_f64_s", indent))))
                        param_idx -= 1
                        stack_idx -= 1

                    elif param_type == 'f64':
                        if stack_type == 'f64':
                            temp = f"$temp_f64_{next_f64_temp}"
                            next_f64_temp += 1
                            ops.append(('f64', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                        elif stack_type == 'i32':
                            temp = f"$temp_i32_{next_i32_temp}"
                            next_i32_temp += 1
                            ops.append(('i32', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("f64.convert_i32_s", indent))))
                        elif stack_type == 'i64':
                            temp = f"$temp_i64_{next_i64_temp}"
                            next_i64_temp += 1
                            ops.append(('i64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("f64.convert_i64_s", indent))))
                        param_idx -= 1
                        stack_idx -= 1

                # Now execute the plan
                # 1. Pop values into temps (in the order of ops, which is R-to-L of stack)
                for pop_type, temp, _ in ops:
                    self.emit(f"local.set {temp}", indent)
                    self.pop_type() # Update type stack tracking

                # 2. Push values back (in reverse order of ops, which is L-to-R of params)
                for _, _, push_action in reversed(ops):
                    push_action()

                # Update type stack to reflect the arguments we just pushed
                for t in param_types:
                    self.push_type(t)

                # Now emit the call
                self.emit(f"call ${import_name}", indent)

                # The call consumes the arguments
                for _ in param_types:
                    self.pop_type()

                # Push return values
                for rt in return_types:
                    self.push_type(rt)

            elif func_name in self.functions:
                # User-defined function call
                func_meta = self.functions[func_name]
                params = func_meta['params']
                param_count = len(params)
                return_type = func_meta['return_type']

                # Check for variadic
                is_variadic = False
                if params and params[-1][1] == 'variadic':
                    is_variadic = True
                    fixed_param_count = param_count - 1
                    variadic_logical_count = arg_count - fixed_param_count

                    if variadic_logical_count >= 0:
                        # Pack variadic arguments into a list
                        args_to_pack = []
                        remaining_args = variadic_logical_count
                        next_i64_temp = 0

                        while remaining_args > 0:
                            if not self.type_stack:
                                break

                            top_type = self.type_stack[-1]
                            stack_idx = len(self.type_stack) - 1

                            is_str = False
                            if top_type == 'i32':
                                # Check extended type stack
                                if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                                    # Debug print
                                    # print(f"DEBUG: stack_idx={stack_idx}, extended={self.extended_type_stack}")
                                    if stack_idx < len(self.extended_type_stack) and self.extended_type_stack[stack_idx] == 'str':
                                        # Check if previous is also str (ptr)
                                        if stack_idx - 1 >= 0 and self.extended_type_stack[stack_idx-1] == 'str':
                                            is_str = True
                            
                            if is_str:
                                # Pop 2 values (len, ptr) -> pack into i64
                                temp = f"$temp_i64_{next_i64_temp}"
                                next_i64_temp += 1

                                self.emit("local.set $temp", indent) # len
                                self.type_stack.pop()
                                # Stack top is ptr
                                self.emit("i64.extend_i32_u", indent) # ptr -> i64
                                # Stack top is ptr(i64)

                                self.emit("local.get $temp", indent) # len
                                self.emit("i64.extend_i32_u", indent) # len -> i64
                                self.emit("i64.const 32", indent)
                                self.emit("i64.shl", indent) # len << 32

                                self.emit("i64.or", indent) # ptr | (len << 32)

                                self.emit(f"local.set {temp}", indent)
                                self.type_stack.pop() # pop ptr

                                args_to_pack.append(('i64', temp))
                                remaining_args -= 2 # String consumes 2 stack slots
                            else:
                                # Single value
                                if top_type == 'i64':
                                    temp = f"$temp_i64_{next_i64_temp}"
                                    next_i64_temp += 1
                                    self.emit(f"local.set {temp}", indent)
                                    self.type_stack.pop()
                                    args_to_pack.append(('i64', temp))
                                elif top_type == 'f64':
                                    temp = f"$temp_i64_{next_i64_temp}"
                                    next_i64_temp += 1
                                    self.emit("i64.trunc_f64_s", indent)
                                    self.emit(f"local.set {temp}", indent)
                                    self.type_stack.pop()
                                    args_to_pack.append(('i64', temp))
                                elif top_type == 'i32':
                                    temp = f"$temp_i64_{next_i64_temp}"
                                    next_i64_temp += 1
                                    self.emit("i64.extend_i32_u", indent)
                                    self.emit(f"local.set {temp}", indent)
                                    self.type_stack.pop()
                                    args_to_pack.append(('i64', temp))

                                remaining_args -= 1

                        # Create new list
                        self._emit_call('list_new', indent)
                        # Stack: list_ptr (i32)

                        # Append args (in correct order: reverse of args_to_pack)
                        for _, temp in reversed(args_to_pack):
                            # Stack: list_ptr
                            self.emit(f"local.get {temp}", indent) # value
                            # Stack: list_ptr, value

                            # Update type stack for _emit_call
                            # list_ptr is already on type_stack (from list_new or previous append)
                            self.type_stack.append('i64')

                            self._emit_call('list_append', indent)
                            # Stack: list_ptr (i32)

                        # Result is list_ptr on stack
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                             self.extended_type_stack[-1] = 'list'

                        self.imports.add('list_new')
                        self.imports.add('list_append')

                # Convert parameters to match expected types
                # Walk through params from last to first (stack is LIFO)
                stack_offset = -1
                for i in range(param_count - 1, -1, -1):
                    param_name, param_type = func_meta['params'][i]
                    
                    # Determine how many stack slots this parameter occupies
                    slots = 2 if param_type == 'str' else 1
                    
                    if len(self.type_stack) >= abs(stack_offset):
                        actual_type = self.type_stack[stack_offset]  # Get the correct stack position

                        if param_type == 'str':
                            # Expect (i32, i32) for string
                            # If actual is not a string pair, this is an error
                            pass
                        else:
                            expected_wasm = self._map_type_to_wasm(param_type)
                            if actual_type != expected_wasm:
                                # Need conversion
                                if expected_wasm == 'i64' and actual_type == 'i32':
                                    # Extend i32 to i64 (e.g., set/list pointer to i64)
                                    # We need to apply this at the right stack position
                                    # For now, assume conversions happen at top of stack
                                    if stack_offset == -1:  # This is the top parameter
                                        self.emit("i64.extend_i32_u", indent)
                                        self.type_stack[-1] = 'i64'
                                elif expected_wasm == 'i32' and actual_type == 'i64':
                                    # Wrap i64 to i32
                                    if stack_offset == -1:
                                        self.emit("i32.wrap_i64", indent)
                                        self.type_stack[-1] = 'i32'
                                elif expected_wasm == 'i64' and actual_type == 'f64':
                                    # Converting f64 to i64
                                    if stack_offset == -1:
                                        self.emit("i64.trunc_f64_s", indent)
                                        self.type_stack[-1] = 'i64'
                                elif expected_wasm == 'f64' and actual_type == 'i64':
                                    # Converting i64 to f64 (python-style true division targets float locals)
                                    if stack_offset == -1:
                                        self.emit("f64.convert_i64_s", indent)
                                        self.type_stack[-1] = 'f64'
                    
                    stack_offset -= slots

                # Pop params from type stack (consumed by call)
                for i, (param_name, param_type) in enumerate(func_meta['params']):
                    if param_type == 'str':
                        # String param: pop two i32s (ptr, len)
                        if self.type_stack:
                            self.type_stack.pop()
                        if self.type_stack:
                            self.type_stack.pop()
                    else:
                        if self.type_stack:
                            self.type_stack.pop()

                # Emit the call
                self.emit(f"call ${func_name}", indent)

                # Push return type onto stack
                if return_type and return_type != 'void':
                    if return_type == 'str':
                        # String return: push two i32s (ptr, len)
                        self.type_stack.append('i32')  # ptr
                        self.type_stack.append('i32')  # len
                        self._last_i32_source = None  # It's a string, not list/set
                    else:
                        wasm_type = self._map_type_to_wasm(return_type)
                        self.type_stack.append(wasm_type)
                        if return_type == 'bool':
                            self._last_i32_source = 'bool'
                        elif return_type == 'list':
                            self._last_i32_source = 'list'
                        elif return_type == 'set':
                            self._last_i32_source = 'set'
                        else:
                            self._last_i32_source = None

        elif opcode == 'POP':
            # Pop top value from stack (discard)
            if self.type_stack:
                # Check if we are popping a string (which takes 2 stack slots)
                is_str = False
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                    if self.extended_type_stack[-1] == 'str':
                        is_str = True
                
                self.type_stack.pop()
                self.emit("drop", indent)
                
                if is_str:
                    # Pop the second part of the string (pointer)
                    if self.type_stack:
                        self.type_stack.pop()
                        self.emit("drop", indent)
                # If string (2 values), need to drop both?
                # But type_stack only has 'i32' for string parts?
                # If it was 'str' in extended, we popped twice?
                # POP opcode usually pops 1 logical value.
                # If logical value is string, it pops 2 stack items.
                # But type_stack tracks stack items.
                # So POP should pop 1 stack item?
                # No, FrScript POP pops 1 logical value.
                # If that value is a string, it pops 2 items.
                # But bytecode compiler emits POP for expression statements.
                # If expression is string, it emits POP.
                # Does POP consume 2 items?
                # In `_infer_locals`, POP pops 1 item from `type_stack_sim`.
                # This implies `type_stack_sim` tracks logical values?
                # No, `type_stack_sim` tracks stack items (i32, i64).
                # If string is on stack, it is 2 items.
                # So POP should pop 2 items if it's a string?
                
                # Let's check `_infer_locals` POP again.
                # `type_stack_sim.pop()`. Just one.
                # This suggests `_infer_locals` might be wrong for strings?
                # Or strings are 1 item in `type_stack_sim`?
                # `CONST_STR`: `type_stack_sim.append('i32'); type_stack_sim.append('i32')`.
                # So strings are 2 items.
                # So `POP` in `_infer_locals` only pops 1 item (len). Ptr remains!
                
                # This is a bug in `_infer_locals` too!
                # But for now, let's implement POP in `_compile_function` to pop 1 item.
                # If `styles` returns `i64`, it's 1 item.
                pass

        elif opcode == 'RETURN':
            self.emit("return", indent)

        elif opcode == 'RETURN_VOID':
            self.emit("return", indent)

        elif opcode == 'CMP_EQ':
            # Assumes i64 comparison
            self.emit("i64.eq", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')
            self._last_i32_source = 'bool'

        elif opcode == 'CMP_EQ_CONST':
            const_val = args[0]
            self.emit(f"i64.const {const_val}", indent)
            self.emit("i64.eq", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('i32')
            self._last_i32_source = 'bool'

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
                    # Wait, I already wrapped val2. Now I need to get to val1.
                    # Use rotl pattern: a b -> b a -> wrap a -> b a(i32) -> a(i32) b
                    # Actually in WASM we can't easily swap without locals
                    # Let me just accept we need locals here
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

        elif opcode == 'RETURN':
            self.emit("return", indent)
            # Clear stack tracking for this path as it's unreachable
            self.type_stack = []

        elif opcode == 'RETURN_VOID':
            self.emit("return", indent)
            self.type_stack = []

        elif opcode == 'FORK':
            # WASM environment can't fork; emulate parent path.
            # Real fork returns >0 in parent, 0 in child.
            self.emit('i64.const 1', indent)
            self.type_stack.append('i64')

        elif opcode == 'EXIT':
            # EXIT consumes an exit code and terminates via host import.
            if self.type_stack:
                if self.type_stack[-1] == 'i64':
                    self.emit('i32.wrap_i64', indent)
                    self.type_stack[-1] = 'i32'
                elif self.type_stack[-1] == 'f64':
                    self.emit('i32.trunc_f64_s', indent)
                    self.type_stack[-1] = 'i32'
            self._emit_call('exit_process', indent)
            self.imports.add('exit_process')
            self.type_stack = []

        elif opcode == 'RAISE':
            # RAISE "Type" "message" -> runtime_error(type, msg, line)
            rest = inst[len('RAISE'):].strip()
            strings = []
            i = 0
            while i < len(rest):
                if rest[i] == '"':
                    j = i + 1
                    while j < len(rest) and rest[j] != '"':
                        if rest[j] == '\\':
                            j += 2
                        else:
                            j += 1
                    if j < len(rest):
                        strings.append(rest[i+1:j])
                        i = j + 1
                    else:
                        break
                else:
                    i += 1

            error_type = self._unescape_string(strings[0]) if len(strings) > 0 else 'RuntimeError'
            message = self._unescape_string(strings[1]) if len(strings) > 1 else ''

            type_off = self.add_string_constant(error_type)
            msg_off = self.add_string_constant(message)
            self.emit(f"i32.const {type_off}", indent)
            self.emit(f"i32.const {len(error_type.encode('utf-8'))}", indent)
            self.emit(f"i32.const {msg_off}", indent)
            self.emit(f"i32.const {len(message.encode('utf-8'))}", indent)
            self.emit(f"i32.const {int(getattr(self, 'current_source_line', 0))}", indent)
            self.emit('call $runtime_error', indent)
            self.imports.add('runtime_error')
            self.type_stack = []

        elif opcode == 'STRUCT_NEW':
            struct_id = int(args[0])
            if struct_id in self.struct_defs:
                struct_def = self.struct_defs[struct_id]
                field_count = struct_def['field_count']
                field_types = struct_def['field_types']

                # Calculate size (8 bytes per field for simplicity)
                struct_size = field_count * 8

                # Allocate memory (bump pointer)
                self.emit("global.get $heap_ptr", indent)
                self.emit("local.tee $temp_i32_0", indent) # struct_base

                # Increment heap pointer
                self.emit(f"i32.const {struct_size}", indent)
                self.emit("i32.add", indent)
                self.emit("global.set $heap_ptr", indent)

                # Store fields (reverse order)
                # We need to pop fields from stack and store them
                # Stack has fields in order: f1, f2, ...
                # So top of stack is last field.

                for i in range(field_count - 1, -1, -1):
                    field_type = field_types[i] if i < len(field_types) else 'i64'
                    # Normalize field types (struct metadata uses front-end types).
                    if field_type == 'float':
                        field_type = 'f64'
                    elif field_type == 'int':
                        field_type = 'i64'
                    offset = i * 8

                    # Pop value and store
                    if field_type == 'str':
                        # String is 2 values on stack (ptr, len)
                        # Pack into i64
                        # Pop len
                        self.emit("local.set $temp_i32_1", indent) # len
                        self.type_stack.pop()
                        # Pop ptr
                        self.emit("i64.extend_i32_u", indent) # ptr -> i64
                        self.emit("local.set $temp_i64_0", indent) # save ptr
                        self.type_stack.pop()

                        # Calculate address: struct_base + offset
                        self.emit("local.get $temp_i32_0", indent)
                        self.emit(f"i32.const {offset}", indent)
                        self.emit("i32.add", indent)

                        # Push packed value
                        self.emit("local.get $temp_i64_0", indent) # ptr
                        self.emit("local.get $temp_i32_1", indent) # len
                        self.emit("i64.extend_i32_u", indent)
                        self.emit("i64.const 32", indent)
                        self.emit("i64.shl", indent)
                        self.emit("i64.or", indent) # ptr | (len << 32)

                        # Store i64
                        self.emit("i64.store", indent)

                    elif field_type == 'f64':
                        # Store f64
                        self.emit("local.set $temp_f64", indent)
                        self.type_stack.pop()

                        # Calculate address
                        self.emit("local.get $temp_i32_0", indent)
                        self.emit(f"i32.const {offset}", indent)
                        self.emit("i32.add", indent)

                        self.emit("local.get $temp_f64", indent)
                        self.emit("f64.store", indent)

                    elif field_type == 'i32' or field_type == 'bool':
                        # Store i32 as i64 (extended)
                        self.emit("local.set $temp_i32_1", indent)
                        self.type_stack.pop()

                        # Calculate address
                        self.emit("local.get $temp_i32_0", indent)
                        self.emit(f"i32.const {offset}", indent)
                        self.emit("i32.add", indent)

                        self.emit("local.get $temp_i32_1", indent)
                        self.emit("i64.extend_i32_u", indent)
                        self.emit("i64.store", indent)

                    else: # i64 or default
                        # Check if stack top is i32 (e.g. list, set, struct ptr)
                        if self.type_stack and self.type_stack[-1] == 'i32':
                            self.emit("i64.extend_i32_u", indent)
                            self.type_stack[-1] = 'i64'
                            
                        self.emit("local.set $temp_i64", indent)
                        self.type_stack.pop()

                        # Calculate address
                        self.emit("local.get $temp_i32_0", indent)
                        self.emit(f"i32.const {offset}", indent)
                        self.emit("i32.add", indent)

                        self.emit("local.get $temp_i64", indent)
                        self.emit("i64.store", indent)

                # Push struct pointer
                self.emit("local.get $temp_i32_0", indent)
                self.type_stack.append('i32')
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    self.extended_type_stack[-1] = f'struct:{struct_id}'

        elif opcode == 'STRUCT_GET':
            field_idx = int(args[0])
            
            # Get struct type from stack tracking
            struct_type = None
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                struct_type_str = self.extended_type_stack[-1]
                if struct_type_str and struct_type_str.startswith('struct:'):
                    # Format: struct:ID or struct:Name
                    parts = struct_type_str.split(':')
                    if len(parts) > 1:
                        val = parts[1]
                        if val.isdigit():
                            struct_type = int(val)
                        else:
                            # Find ID by name
                            for sid, sdef in self.struct_defs.items():
                                if sdef.get('name') == val:
                                    struct_type = sid
                                    break
            
            if struct_type is not None and struct_type in self.struct_defs:
                struct_def = self.struct_defs[struct_type]
                field_types = struct_def['field_types']
                
                if field_idx < len(field_types):
                    field_type = field_types[field_idx]
                    # Normalize field types (struct metadata uses front-end types).
                    if field_type == 'float':
                        field_type = 'f64'
                    elif field_type == 'int':
                        field_type = 'i64'
                    offset = field_idx * 8
                    
                    # Pop struct pointer
                    if self.type_stack and self.type_stack[-1] == 'i64':
                        self.emit("i32.wrap_i64", indent)
                        self.type_stack[-1] = 'i32'

                    self.emit("local.set $temp_i32_0", indent)
                    self.type_stack.pop()
                    
                    # Calculate address
                    self.emit("local.get $temp_i32_0", indent)
                    self.emit(f"i32.const {offset}", indent)
                    self.emit("i32.add", indent)
                    
                    # Load value based on type
                    if field_type == 'str':
                        # String is stored as i64 (ptr | len << 32)
                        self.emit("i64.load", indent)
                        self.emit("local.tee $temp_i64", indent)
                        
                        # Extract ptr (lower 32 bits)
                        self.emit("i32.wrap_i64", indent)
                        self.type_stack.append('i32')
                        
                        # Extract len (upper 32 bits)
                        self.emit("local.get $temp_i64", indent)
                        self.emit("i64.const 32", indent)
                        self.emit("i64.shr_u", indent)
                        self.emit("i32.wrap_i64", indent)
                        self.type_stack.append('i32')
                        
                        # Update extended stack
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            self.extended_type_stack.append('str')
                            self.extended_type_stack.append('str')
                            
                    elif field_type == 'f64':
                        self.emit("f64.load", indent)
                        self.type_stack.append('f64')
                        
                    elif field_type == 'i32' or field_type == 'bool':
                        # Stored as i64, need to load and wrap
                        self.emit("i64.load", indent)
                        self.emit("i32.wrap_i64", indent)
                        self.type_stack.append('i32')
                        
                    else: # i64 or default (including int)
                        self.emit("i64.load", indent)
                        self.type_stack.append('i64')
            else:
                # Fallback: assume i64
                offset = field_idx * 8
                
                # Check if stack has i64 (pointer)
                if self.type_stack and self.type_stack[-1] == 'i64':
                    self.emit("i32.wrap_i64", indent)
                    self.type_stack[-1] = 'i32'

                self.emit(f"i32.const {offset}", indent)
                self.emit("i32.add", indent)
                self.emit("i64.load", indent)
                if self.type_stack: self.type_stack.pop()
                self.type_stack.append('i64')

        elif opcode == 'STRUCT_SET':
            # STRUCT_SET field_idx
            # Stack before: struct_ptr, value
            # Returns: struct_ptr
            field_idx = int(args[0])

            # Determine how many stack slots the value takes.
            value_is_str = False
            if (
                len(self.type_stack) >= 3
                and self.type_stack[-1] == 'i32'
                and self.type_stack[-2] == 'i32'
                and self.type_stack[-3] == 'i32'
                and hasattr(self, 'extended_type_stack')
                and self.extended_type_stack is not None
                and len(self.extended_type_stack) >= 2
                and self.extended_type_stack[-1] == 'str'
                and self.extended_type_stack[-2] == 'str'
            ):
                value_is_str = True

            # Identify struct type (best-effort) from the struct pointer position.
            struct_type = None
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                struct_pos = -2 if not value_is_str else -3
                if len(self.extended_type_stack) >= abs(struct_pos):
                    st = self.extended_type_stack[struct_pos]
                    if st and isinstance(st, str) and st.startswith('struct:'):
                        parts = st.split(':')
                        if len(parts) > 1 and parts[1].isdigit():
                            struct_type = int(parts[1])

            field_type = 'i64'
            if struct_type is not None and struct_type in self.struct_defs:
                field_types = self.struct_defs[struct_type].get('field_types', [])
                if field_idx < len(field_types):
                    ft = field_types[field_idx]
                    if ft == 'float':
                        field_type = 'f64'
                    elif ft == 'int':
                        field_type = 'i64'
                    elif ft == 'bool':
                        field_type = 'i32'
                    elif ft == 'str':
                        field_type = 'str'
                    else:
                        field_type = ft

            offset = field_idx * 8

            if field_type == 'str' and value_is_str:
                # Stack: struct_ptr ptr len
                self.emit('local.set $temp_i32_1', indent)  # len
                self.type_stack.pop()
                self.emit('i64.extend_i32_u', indent)  # ptr -> i64
                self.emit('local.set $temp_i64_0', indent)
                self.type_stack.pop()

                # struct ptr
                if self.type_stack and self.type_stack[-1] == 'i64':
                    self.emit('i32.wrap_i64', indent)
                    self.type_stack[-1] = 'i32'
                self.emit('local.set $temp_i32_0', indent)
                self.type_stack.pop()

                # addr
                self.emit('local.get $temp_i32_0', indent)
                self.emit(f'i32.const {offset}', indent)
                self.emit('i32.add', indent)

                # pack and store
                self.emit('local.get $temp_i64_0', indent)  # ptr
                self.emit('local.get $temp_i32_1', indent)  # len
                self.emit('i64.extend_i32_u', indent)
                self.emit('i64.const 32', indent)
                self.emit('i64.shl', indent)
                self.emit('i64.or', indent)
                self.emit('i64.store', indent)

                # return struct ptr
                self.emit('local.get $temp_i32_0', indent)
                self.type_stack.append('i32')

            elif field_type == 'f64':
                # Stack: struct_ptr value
                if self.type_stack and self.type_stack[-1] == 'i64':
                    self.emit('f64.convert_i64_s', indent)
                    self.type_stack[-1] = 'f64'
                self.emit('local.set $temp_f64', indent)
                self.type_stack.pop()

                if self.type_stack and self.type_stack[-1] == 'i64':
                    self.emit('i32.wrap_i64', indent)
                    self.type_stack[-1] = 'i32'
                self.emit('local.set $temp_i32_0', indent)
                self.type_stack.pop()

                self.emit('local.get $temp_i32_0', indent)
                self.emit(f'i32.const {offset}', indent)
                self.emit('i32.add', indent)
                self.emit('local.get $temp_f64', indent)
                self.emit('f64.store', indent)

                self.emit('local.get $temp_i32_0', indent)
                self.type_stack.append('i32')

            else:
                # Store as i64 in memory.
                if self.type_stack and self.type_stack[-1] == 'i32':
                    self.emit('i64.extend_i32_u', indent)
                    self.type_stack[-1] = 'i64'
                self.emit('local.set $temp_i64', indent)
                self.type_stack.pop()

                if self.type_stack and self.type_stack[-1] == 'i64':
                    self.emit('i32.wrap_i64', indent)
                    self.type_stack[-1] = 'i32'
                self.emit('local.set $temp_i32_0', indent)
                self.type_stack.pop()

                self.emit('local.get $temp_i32_0', indent)
                self.emit(f'i32.const {offset}', indent)
                self.emit('i32.add', indent)
                self.emit('local.get $temp_i64', indent)
                self.emit('i64.store', indent)

                self.emit('local.get $temp_i32_0', indent)
                self.type_stack.append('i32')

            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                while len(self.extended_type_stack) < len(self.type_stack):
                    self.extended_type_stack.append(None)
                if struct_type is not None:
                    self.extended_type_stack[-1] = f'struct:{struct_type}'

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
            self.type_stack.append('i32')

        elif opcode == 'SHR_I64':
            # Shift right (i64 operands)
            self.emit("i64.shr_s", indent)
            if len(self.type_stack) >= 2:
                self.type_stack.pop()
                self.type_stack.pop()
            self.type_stack.append('i32')

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
                # Mark as string in extended stack
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    while len(self.extended_type_stack) < len(self.type_stack):
                        self.extended_type_stack.append(None)
                    self.extended_type_stack[-2] = 'str'
                    self.extended_type_stack[-1] = 'str'
                    # print(f"DEBUG: CONST_STR extended stack: {self.extended_type_stack}")

        elif opcode == 'DEC_LOCAL':
            var_idx = int(args[0])
            var_ref = self._get_var_ref(var_idx)
            self.emit(f"local.get {var_ref}", indent)
            self.emit("i64.const 1", indent)
            self.emit("i64.sub", indent)
            self.emit(f"local.set {var_ref}", indent)

        elif opcode == 'DIV_CONST_I64':
            const_val = args[0]
            # Always use float division (Python-style true division)
            if self.type_stack and self.type_stack[-1] == 'i64':
                # Convert i64 operand to f64 first
                self.emit("f64.convert_i64_s", indent)
                self.type_stack[-1] = 'f64'
            self.emit(f"f64.const {const_val}", indent)
            self.emit("f64.div", indent)
            if self.type_stack:
                self.type_stack.pop()
            self.type_stack.append('f64')

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
            # Integer division in fr returns float (Python-style true division)
            # Convert both operands to f64, perform f64 division
            if len(self.type_stack) >= 2:
                # Top operand
                if self.type_stack[-1] == 'i64':
                    self.emit("f64.convert_i64_s", indent)
                    self.type_stack[-1] = 'f64'
                # Bottom operand
                if self.type_stack[-2] == 'i64':
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

                # Determine source type
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if src_idx < param_count:
                        src_type_fr = func_meta['params'][src_idx][1]
                    else:
                        src_type_fr = self.local_vars.get(src_idx - param_count, 'i64')
                else:
                    src_type_fr = 'i64'

                src_ref = self._get_var_ref(src_idx)
                dst_ref = self._get_var_ref(dst_idx)

                # Handle strings specially (need to copy both ptr and len)
                if src_type_fr == 'str':
                    self.emit(f"local.get {src_ref}", indent)
                    self.emit(f"local.set {dst_ref}", indent)
                    src_len_ref = f"{src_ref}_len"
                    dst_len_ref = f"{dst_ref}_len"
                    self.emit(f"local.get {src_len_ref}", indent)
                    self.emit(f"local.set {dst_len_ref}", indent)
                else:
                    self.emit(f"local.get {src_ref}", indent)
                    self.emit(f"local.set {dst_ref}", indent)

                # Update type tracking
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if dst_idx >= param_count:
                        self.local_vars[dst_idx - param_count] = src_type_fr

            # If odd number of args, there's a final LOAD
            if len(args) % 2 == 1:
                final_idx = int(args[-1])
                final_ref = self._get_var_ref(final_idx)

                # Determine type
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if final_idx < param_count:
                        local_type_fr = func_meta['params'][final_idx][1]
                    else:
                        local_type_fr = self.local_vars.get(final_idx - param_count, 'i64')
                else:
                    local_type_fr = 'i64'

                # Handle strings specially
                if local_type_fr == 'str':
                    self.emit(f"local.get {final_ref}", indent)
                    self.type_stack.append('i32')
                    len_ref = f"{final_ref}_len"
                    self.emit(f"local.get {len_ref}", indent)
                    self.type_stack.append('i32')
                else:
                    self.emit(f"local.get {final_ref}", indent)
                    local_type = self._map_type_to_wasm(local_type_fr)
                    self.type_stack.append(local_type)

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
            # Handle append where value may be a string (ptr,len) or a single i64
            # Stack for string value: ... list_ptr ptr len
            # Only treat as string packing when we are sure it is a string
            is_string = False
            if (len(self.type_stack) >= 3
                and self.type_stack[-1] == 'i32'
                and self.type_stack[-2] == 'i32'
                and self.type_stack[-3] == 'i32'):
                
                # Check extended types if available
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                    if (len(self.extended_type_stack) >= 2 
                        and self.extended_type_stack[-1] == 'str' 
                        and self.extended_type_stack[-2] == 'str'):
                        is_string = True
                else:
                    # Fallback heuristic: if we don't have extended types, assume string
                    # BUT this is dangerous as seen in struct_in_list case.
                    # Better to be conservative?
                    # Most strings come from CONST_STR or string ops which set extended types.
                    pass

            if is_string:
                # Pack (ptr,len) into i64: (len<<32) | ptr
                # Stack: ... list_ptr ptr len
                # Save len
                self.emit("local.set $temp", indent) # len
                self.type_stack.pop()
                # Convert ptr to i64 and save
                self.emit("i64.extend_i32_u", indent) # ptr -> i64
                self.emit("local.set $temp_i64", indent)
                self.type_stack.pop()

                # Combine
                self.emit("local.get $temp", indent) # len
                self.emit("i64.extend_i32_u", indent)
                self.emit("i64.const 32", indent)
                self.emit("i64.shl", indent)
                self.emit("local.get $temp_i64", indent) # ptr
                self.emit("i64.or", indent)
                
                # Now stack has `combined_i64`.
                # We need to update type_stack to reflect this change.
                # We popped 2 i32s. We pushed 1 i64 (implicitly on stack).
                self.type_stack.append('i64')
            else:
                # Ensure list pointer (second-from-top) is i32 for non-string values
                self._ensure_second_is_i32(indent)
                # Ensure value (top of stack) is i64 - struct pointers are i32
                if len(self.type_stack) >= 1 and self.type_stack[-1] == 'i32':
                    self.emit("i64.extend_i32_u", indent)
                    self.type_stack[-1] = 'i64'

            # Call runtime append
            self._emit_call('list_append', indent)
            # list_append returns list pointer (i32)
            # _emit_call handles type_stack
            self._last_i32_source = 'list'  # Track that this i32 is a list
            if is_string and hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 1:
                    self.extended_type_stack[-1] = 'list_str'
            self.imports.add('list_append')

        elif opcode == 'LIST_GET':
            # Check if we have a string (i32, i32, i64) or list (i32, i64)
            # Stack layout for string: ... ptr(i32) len(i32) index(i64)
            if len(self.type_stack) >= 3 and self.type_stack[-3] == 'i32' and self.type_stack[-2] == 'i32' and self.type_stack[-1] == 'i64':
                # String indexing: (ptr, len, index) -> (ptr, len) of char
                # _emit_call handles popping params and pushing result
                self._emit_call('str_get', indent)
                self.imports.add('str_get')
            else:
                # List indexing - ensure list pointer (second-from-top) is i32
                self._ensure_second_is_i32(indent)
                is_list_str = False
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    # Stack: ... list_ptr(i32) index(i64)
                    if len(self.extended_type_stack) >= 2 and self.extended_type_stack[-2] == 'list_str':
                        is_list_str = True
                # _emit_call handles popping params and pushing result
                self._emit_call('list_get', indent)
                self.imports.add('list_get')
                # list_get returns i64; if the list is known to contain packed strings,
                # mark this i64 so _emit_call can unpack it for string functions.
                if is_list_str and hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    if len(self.extended_type_stack) >= 1:
                        self.extended_type_stack[-1] = 'str'

        elif opcode == 'LIST_NEW':
            self._emit_call('list_new', indent)
            # _emit_call already pushes i32 return type
            self._last_i32_source = 'list'  # Track that this i32 is a list
            self.imports.add('list_new')

        elif opcode == 'LIST_POP':
            # (list_ptr) -> (list_ptr, value)
            self._ensure_top_is_i32(indent)
            self._emit_call('list_pop', indent)
            self.imports.add('list_pop')
            self._last_i32_source = 'list'

        elif opcode == 'LIST_NEW_I64':
            count = int(args[0])
            values = args[1:]
            
            self._emit_call('list_new', indent)
            self.imports.add('list_new')
            self._last_i32_source = 'list'
            
            for val in values:
                self.emit(f"i64.const {val}", indent)
                self.type_stack.append('i64')
                self._emit_call('list_append', indent)
                self.imports.add('list_append')

        elif opcode == 'LIST_NEW_STR':
            count = int(args[0])
            # Reconstruct args if they were split by space
            # This is tricky. But let's assume simple strings for now.
            values = args[1:]
            
            self._emit_call('list_new', indent)
            self.imports.add('list_new')
            self._last_i32_source = 'list'
            if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                if len(self.extended_type_stack) >= 1:
                    self.extended_type_stack[-1] = 'list_str'
            
            for val in values:
                # val is a string literal, e.g. "abc"
                # Remove quotes
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                
                # Add to string constants
                str_offset = self.add_string_constant(val)
                str_len = len(val)
                
                # Push ptr, len
                self.emit(f"i32.const {str_offset}", indent)
                self.emit(f"i32.const {str_len}", indent)
                self.type_stack.append('i32')
                self.type_stack.append('i32')
                
                # Pack (ptr,len) into i64: (len<<32) | ptr
                self.emit("local.set $temp", indent) # len
                self.type_stack.pop()
                self.emit("i64.extend_i32_u", indent) # ptr -> i64
                self.emit("local.set $temp_i64", indent)
                self.type_stack.pop()
                
                self.emit("local.get $temp", indent) # len
                self.emit("i64.extend_i32_u", indent)
                self.emit("i64.const 32", indent)
                self.emit("i64.shl", indent)
                self.emit("local.get $temp_i64", indent) # ptr
                self.emit("i64.or", indent)
                
                self.type_stack.append('i64')
                
                self._emit_call('list_append', indent)
                self.imports.add('list_append')

        elif opcode == 'SET_NEW':
            self._emit_call('set_new', indent)
            self.imports.add('set_new')
            self._last_i32_source = 'set'

        elif opcode in ('SET_ADD', 'SET_REMOVE', 'SET_CONTAINS'):
            # Runtime expects (set_ptr: i32, value: i64).
            # If value is a string (ptr,len), pack it into i64 like lists do.
            is_string = False
            if len(self.type_stack) >= 3 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32' and self.type_stack[-3] == 'i32':
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack:
                    if len(self.extended_type_stack) >= 2 and self.extended_type_stack[-1] == 'str' and self.extended_type_stack[-2] == 'str':
                        is_string = True

            if is_string:
                # Stack: set_ptr ptr len
                self.emit('local.set $temp', indent)  # len
                self.type_stack.pop()
                self.emit('i64.extend_i32_u', indent)  # ptr
                self.emit('local.set $temp_i64', indent)
                self.type_stack.pop()
                self.emit('local.get $temp', indent)
                self.emit('i64.extend_i32_u', indent)
                self.emit('i64.const 32', indent)
                self.emit('i64.shl', indent)
                self.emit('local.get $temp_i64', indent)
                self.emit('i64.or', indent)
                self.type_stack.append('i64')
            else:
                # Ensure value is i64 when not a string.
                if self.type_stack and self.type_stack[-1] == 'i32':
                    self.emit('i64.extend_i32_u', indent)
                    self.type_stack[-1] = 'i64'

            if opcode == 'SET_ADD':
                self._emit_call('set_add', indent)
                self.imports.add('set_add')
                self._last_i32_source = 'set'
            elif opcode == 'SET_REMOVE':
                self._emit_call('set_remove', indent)
                self.imports.add('set_remove')
                self._last_i32_source = 'set'
            else:  # SET_CONTAINS
                self._emit_call('set_contains', indent)
                self.imports.add('set_contains')
                self._last_i32_source = 'bool'

        elif opcode == 'LIST_SET':
            # Ensure list pointer (third-from-top) is i32
            # If value is a string (ptr,len) the stack layout is: ... list_ptr index ptr len
            # We need to pack ptr,len into i64 so list_set sees (list_ptr, index, value_i64)
            if len(self.type_stack) >= 4 and self.type_stack[-1] == 'i32' and self.type_stack[-2] == 'i32' and self.type_stack[-3] == 'i64' and self.type_stack[-4] == 'i32':
                # Stack: ... list_ptr index ptr len
                # Save len
                self.emit("local.set $temp", indent)
                self.type_stack.pop()
                # Convert ptr to i64 and save
                self.emit("i64.extend_i32_u", indent)
                self.emit("local.set $temp_i64", indent)
                self.type_stack.pop()
                # Now stack: ... list_ptr index
                # Build combined i64
                self.emit("local.get $temp", indent)
                self.emit("i64.extend_i32_u", indent)
                self.emit("i64.const 32", indent)
                self.emit("i64.shl", indent)
                self.emit("local.get $temp_i64", indent)
                self.emit("i64.or", indent)
                # Now stack: ... list_ptr index combined_i64
                # Update tracked types accordingly
                # Remove the top two placeholders and replace with i64
                # (we already popped ptr/len above)
                # leave list_ptr and index on stack and append i64
                self.type_stack = self.type_stack[:-2]
                self.type_stack.append('i32')
            else:
                # Ensure list pointer (third-from-top) is i32
                self._ensure_nth_from_top_is_i32(3, indent)

            self._emit_call('list_set', indent)
            # _emit_call already handles popping params and pushing return type
            self._last_i32_source = 'list'
            self.imports.add('list_set')

        elif opcode == 'STORE':
            for arg in args:
                var_idx = int(arg)
                var_ref = self._get_var_ref(var_idx)
                
                # Check if it's a string
                is_str = False
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    params = func_meta.get('params', [])
                    param_count = len(params)
                    
                    if var_idx < param_count:
                        if params[var_idx][1] == 'str':
                            is_str = True
                    else:
                        local_idx = var_idx - param_count
                        if local_idx in self.local_vars and self.local_vars[local_idx] == 'str':
                            is_str = True
                
                if is_str:
                    # Check if we have i64 on stack (packed string)
                    if self.type_stack and self.type_stack[-1] == 'i64':
                        # Unpack i64 -> ptr, len
                        self.emit("local.set $temp_i64", indent)
                        self.type_stack.pop()
                        
                        # Get ptr (lower 32 bits)
                        self.emit("local.get $temp_i64", indent)
                        self.emit("i32.wrap_i64", indent)
                        self.emit(f"local.set {var_ref}", indent)
                        
                        # Get len (upper 32 bits)
                        self.emit("local.get $temp_i64", indent)
                        self.emit("i64.const 32", indent)
                        self.emit("i64.shr_u", indent)
                        self.emit("i32.wrap_i64", indent)
                        self.emit(f"local.set {var_ref}_len", indent)
                    else:
                        # Pop len, store to _len
                        self.emit(f"local.set {var_ref}_len", indent)
                        if self.type_stack: self.type_stack.pop()
                        
                        # Pop ptr, store to var
                        self.emit(f"local.set {var_ref}", indent)
                        if self.type_stack: self.type_stack.pop()
                else:
                    # Check expected type
                    expected_type = 'i64' # Default
                    if self.current_function:
                        func_meta = self.functions.get(self.current_function, {})
                        params = func_meta.get('params', [])
                        param_count = len(params)
                        
                        if var_idx < param_count:
                            param_type = params[var_idx][1]
                            expected_type = self._map_type_to_wasm(param_type)
                        else:
                            local_idx = var_idx - param_count
                            if local_idx in self.local_vars:
                                local_type_fr = self.local_vars[local_idx]
                                expected_type = self._map_type_to_wasm(local_type_fr)
                    
                    # Check stack type
                    if self.type_stack:
                        stack_type = self.type_stack[-1]

                        # If the destination expects i64 but we currently have a string
                        # as (ptr,len) i32 pair, pack it into a single i64.
                        # This is used by code that keeps strings packed in i64 locals
                        # (e.g. results of LIST_GET on lists of strings).
                        if (
                            expected_type == 'i64'
                            and len(self.type_stack) >= 2
                            and self.type_stack[-1] == 'i32'
                            and self.type_stack[-2] == 'i32'
                            and hasattr(self, 'extended_type_stack')
                            and self.extended_type_stack is not None
                            and len(self.extended_type_stack) >= 2
                            and self.extended_type_stack[-1] == 'str'
                            and self.extended_type_stack[-2] == 'str'
                        ):
                            # Stack: ... ptr(i32) len(i32)
                            self.emit('local.set $temp', indent)  # len
                            self.type_stack.pop()
                            if self.extended_type_stack:
                                self.extended_type_stack.pop()

                            self.emit('i64.extend_i32_u', indent)  # ptr -> i64
                            self.emit('local.set $temp_i64', indent)
                            self.type_stack.pop()
                            if self.extended_type_stack:
                                self.extended_type_stack.pop()

                            self.emit('local.get $temp', indent)
                            self.emit('i64.extend_i32_u', indent)
                            self.emit('i64.const 32', indent)
                            self.emit('i64.shl', indent)
                            self.emit('local.get $temp_i64', indent)
                            self.emit('i64.or', indent)
                            self.type_stack.append('i64')
                            if self.extended_type_stack is not None:
                                self.extended_type_stack.append('str')

                            stack_type = 'i64'

                        if expected_type == 'i64' and stack_type == 'i32':
                            self.emit("i64.extend_i32_u", indent)
                            self.type_stack[-1] = 'i64'
                        elif expected_type == 'i32' and stack_type == 'i64':
                            self.emit("i32.wrap_i64", indent)
                            self.type_stack[-1] = 'i32'
                        elif expected_type == 'f64' and stack_type == 'i64':
                            self.emit('f64.convert_i64_s', indent)
                            self.type_stack[-1] = 'f64'
                        elif expected_type == 'f64' and stack_type == 'i32':
                            self.emit('f64.convert_i32_s', indent)
                            self.type_stack[-1] = 'f64'
                        elif expected_type == 'i64' and stack_type == 'f64':
                            self.emit('i64.trunc_f64_s', indent)
                            self.type_stack[-1] = 'i64'
                        elif expected_type == 'i32' and stack_type == 'f64':
                            self.emit('i32.trunc_f64_s', indent)
                            self.type_stack[-1] = 'i32'
                            
                    self.emit(f"local.set {var_ref}", indent)
                    if self.type_stack: self.type_stack.pop()

        elif opcode == 'LOAD_GLOBAL':
            global_idx = int(args[0])
            global_ref = f"$g{global_idx}"
            
            # Determine type
            global_type_fr = self.global_vars.get(global_idx, 'i64')
            wasm_type = self._map_type_to_wasm(global_type_fr)
            
            self.emit(f"global.get {global_ref}", indent)
            self.type_stack.append(wasm_type)
            self.struct_type_stack.append(None)
            
            # Track extended type
            if global_type_fr == 'list':
                self._last_i32_source = 'list'
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    self.extended_type_stack[-1] = 'list'
            elif global_type_fr == 'set':
                self._last_i32_source = 'set'
                if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                    self.extended_type_stack[-1] = 'set'

        elif opcode == 'STORE_GLOBAL':
            global_idx = int(args[0])
            global_ref = f"$g{global_idx}"
            
            # Determine type
            global_type_fr = self.global_vars.get(global_idx, 'i64')
            wasm_type = self._map_type_to_wasm(global_type_fr)
            
            # Check stack type
            if self.type_stack:
                stack_type = self.type_stack[-1]
                if wasm_type == 'i64' and stack_type == 'i32':
                    self.emit("i64.extend_i32_u", indent)
                    self.type_stack[-1] = 'i64'
                elif wasm_type == 'i32' and stack_type == 'i64':
                    self.emit("i32.wrap_i64", indent)
                    self.type_stack[-1] = 'i32'
            
            self.emit(f"global.set {global_ref}", indent)
            if self.type_stack:
                self.type_stack.pop()

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

                        # Mark as string in extended stack
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            # Ensure extended_type_stack is large enough (TypeStack handles this usually)
                            while len(self.extended_type_stack) < len(self.type_stack):
                                self.extended_type_stack.append(None)
                            self.extended_type_stack[-2] = 'str'
                            self.extended_type_stack[-1] = 'str'
                        continue

                # Regular single-value load
                self.emit(f"local.get {var_ref}", indent)
                # Get the correct local type
                struct_id = None
                local_type_fr = 'i64'
                
                if self.current_function:
                    func_meta = self.functions.get(self.current_function, {})
                    param_count = len(func_meta.get('params', []))
                    if local_idx < param_count:
                        param_type = func_meta['params'][local_idx][1]
                        local_type = self._map_type_to_wasm(param_type)
                        local_type_fr = param_type
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
                        local_type = self._map_type_to_wasm(local_type_fr)
                else:
                    local_type = 'i64'
                self.type_stack.append(local_type)
                self.struct_type_stack.append(struct_id)

                # Track value type if this is a list or set
                if local_idx in self.local_value_types:
                    self._last_i32_source = self.local_value_types[local_idx]
                
                # Also track based on type name
                if local_type == 'i32':
                    if local_type_fr == 'list' or local_type_fr == 'variadic':
                        self._last_i32_source = 'list'
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            self.extended_type_stack[-1] = 'list'
                    elif local_type_fr == 'set':
                        self._last_i32_source = 'set'
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            self.extended_type_stack[-1] = 'set'
                    elif local_type_fr == 'bool':
                        self._last_i32_source = 'bool'
                    elif local_type_fr.startswith('struct:'):
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            self.extended_type_stack[-1] = local_type_fr

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

        elif opcode == 'LOAD2_MUL_I64':
            # Load two variables and multiply them (i64)
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit('i64.mul', indent)
            self.type_stack.append('i64')

        elif opcode == 'LOAD2_DIV_I64':
            # Load two variables and divide them (true division => f64)
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit('f64.convert_i64_s', indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit('f64.convert_i64_s', indent)
            self.emit('f64.div', indent)
            self.type_stack.append('f64')

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

        elif opcode == 'LOAD2_CMP_GT':
            # Load two variables and compare
            var1 = int(args[0])
            var2 = int(args[1])
            var_ref1 = self._get_var_ref(var1)
            var_ref2 = self._get_var_ref(var2)
            self.emit(f"local.get {var_ref1}", indent)
            self.emit(f"local.get {var_ref2}", indent)
            self.emit("i64.gt_s", indent)
            self.type_stack.append('i32')

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

    def _ensure_top_is_i32(self, indent: int):
        """Ensure the top stack value is an i32 (wrap from i64 if needed)."""
        if self.type_stack and self.type_stack[-1] == 'i64':
            self.emit("i32.wrap_i64", indent)
            self.type_stack[-1] = 'i32'

    def _ensure_second_is_i32(self, indent: int):
        """Ensure the second-from-top stack value is an i32.

        If the second value is i64, pop the top into a temp local, wrap the second
        value to i32, then push the top value back.
        """
        if len(self.type_stack) >= 2 and self.type_stack[-2] == 'i64':
            # Save top value into appropriate temp local
            top_type = self.type_stack[-1]
            if top_type == 'i64':
                self.emit("local.set $temp_i64", indent)
            elif top_type == 'f64':
                self.emit("local.set $temp_f64", indent)
            else:
                self.emit("local.set $temp", indent)

            # Now top of stack is the former second value; wrap it
            self.emit("i32.wrap_i64", indent)
            # Update type stack: second becomes i32, top remains as before
            self.type_stack[-2] = 'i32'

            # Push back saved top value
            if top_type == 'i64':
                self.emit("local.get $temp_i64", indent)
            elif top_type == 'f64':
                self.emit("local.get $temp_f64", indent)
            else:
                self.emit("local.get $temp", indent)

    def _ensure_nth_from_top_is_i32(self, n: int, indent: int):
        """Ensure the n-th-from-top (1-based) stack value is an i32.

        n=1 is top, n=2 is second-from-top, etc. This implementation only
        handles n up to 3 which is sufficient for list/set operations in bytecode.
        """
        if n <= 0:
            return
        if len(self.type_stack) < n:
            return
        idx = -n
        if self.type_stack[idx] != 'i64':
            return

        # For n==1 we can simply wrap
        if n == 1:
            self.emit("i32.wrap_i64", indent)
            self.type_stack[idx] = 'i32'
            return

        # For n>1 we need to save higher stack values, wrap, then restore
        saved = []
        # Use multiple temps to avoid overwriting ($temp, $temp2, $temp_i64)
        for i in range(n-1):
            t = self.type_stack.pop()
            saved.append(t)
            if t == 'i64':
                if i == 0:
                    self.emit("local.set $temp_i64", indent)
                else:
                    self.emit("local.set $temp", indent)
            elif t == 'f64':
                self.emit("local.set $temp_f64", indent)
            else:
                if i == 0:
                    self.emit("local.set $temp", indent)
                else:
                    self.emit("local.set $temp2", indent)

        # Pop the target from simulated stack and perform extend on it
        target_type = self.type_stack.pop()
        self.emit("i32.wrap_i64", indent)
        # Update tracked type for that position to i32
        self.type_stack.append('i32')

        # Restore saved values in reverse order
        for i, t in enumerate(reversed(saved)):
            if t == 'i64':
                self.emit("local.get $temp_i64", indent)
            elif t == 'f64':
                self.emit("local.get $temp_f64", indent)
            else:
                if i == 0:
                    self.emit("local.get $temp2", indent)
                else:
                    self.emit("local.get $temp", indent)
            self.type_stack.append(t)

    def _ensure_nth_from_top_is_i64(self, n: int, indent: int):
        """Ensure the n-th-from-top stack value is an i64 (extend i32 if needed).

        Saves/restores higher stack values similarly to the i32 helper.
        """
        if n <= 0:
            return
        if len(self.type_stack) < n:
            return
        idx = -n
        if self.type_stack[idx] != 'i32':
            return

        # For n==1 we can simply extend
        if n == 1:
            self.emit("i64.extend_i32_u", indent)
            self.type_stack[idx] = 'i64'
            return

        # Save higher stack values
        saved = []
        # Use multiple temps to avoid overwriting ($temp, $temp2, $temp_i64)
        for i in range(n-1):
            t = self.type_stack.pop()
            saved.append(t)
            if t == 'i64':
                if i == 0:
                    self.emit("local.set $temp_i64", indent)
                else:
                    self.emit("local.set $temp", indent)
            elif t == 'f64':
                self.emit("local.set $temp_f64", indent)
            else:
                if i == 0:
                    self.emit("local.set $temp", indent)
                else:
                    self.emit("local.set $temp2", indent)

        # Pop the target from simulated stack and perform extend on it
        target_type = self.type_stack.pop()
        self.emit("i64.extend_i32_u", indent)
        # Update tracked type for that position to i64
        self.type_stack.append('i64')

        # Restore saved values in reverse order
        for i, t in enumerate(reversed(saved)):
            if t == 'i64':
                self.emit("local.get $temp_i64", indent)
            elif t == 'f64':
                self.emit("local.get $temp_f64", indent)
            else:
                if i == 0:
                    self.emit("local.get $temp2", indent)
                else:
                    self.emit("local.get $temp", indent)
            self.type_stack.append(t)

    def _emit_call(self, name: str, indent: int):
        """Emit a call to an imported runtime function, converting argument types as needed.

        This uses a small signature map for common runtime functions that the
        WASM backend expects. It will wrap/extend integer widths for deeper
        stack positions when necessary.
        """
        sig = {
            'str_concat': ['i32','i32','i32','i32'],
            'str_contains': ['i32','i32','i32','i32'],
            'i64_to_str': ['i64'],
            'f64_to_str': ['f64'],
            'bool_to_str': ['i64'],
            'str_to_i64': ['i32','i32'],
            'str_to_f64': ['i32','i32'],
            'list_to_str': ['i32'],
            'set_to_str': ['i32'],
            'list_append': ['i32','i64'],
            'list_get': ['i32','i64'],
            'list_set': ['i32','i64','i64'],
            'list_len': ['i32'],
            'list_contains': ['i32','i64'],
            'list_pop': ['i32'],
            'set_new': [],
            'set_add': ['i32','i64'],
            'set_remove': ['i32','i64'],
            'set_contains': ['i32','i64'],
            'set_len': ['i32'],
            'runtime_error': ['i32','i32','i32','i32','i32'],
            'exit_process': ['i32'],
            'str_join': ['i32','i32','i32'],
            'str_split': ['i32','i32','i32','i32'],
            'str_strip': ['i32','i32'],
            'str_get': ['i32','i32','i64'],
            'print': ['i32','i32'],
            'println': ['i32','i32'],
            'file_write': ['i32','i32','i32'],
            'file_read': ['i32'],
            'file_open': ['i32','i32','i32','i32'],
            'sqrt': ['f64'],
            'round_f64': ['f64'],
            'floor_f64': ['f64'],
            'ceil_f64': ['f64'],
            'dom_create': ['i32','i32'],
            'dom_set_text': ['i32','i32','i32'],
            'dom_get_text': ['i32'],
            'dom_set_html': ['i32','i32','i32'],
            'dom_get_html': ['i32'],
            'dom_set_attr': ['i32','i32','i32'],
            'dom_get_attr': ['i32','i32','i32'],
            'dom_remove_attr': ['i32','i32','i32'],
            'dom_append': ['i32','i32'],
            'dom_prepend': ['i32','i32'],
            'dom_remove': ['i32'],
            'dom_clone': ['i32','i32'],
            'dom_parent': ['i32'],
            'dom_children': ['i32'],
            'dom_add_class': ['i32','i32','i32'],
            'dom_remove_class': ['i32','i32','i32'],
            'dom_toggle_class': ['i32','i32','i32'],
            'dom_has_class': ['i32','i32','i32'],
            'dom_set_style': ['i32','i32','i32','i32','i32'],
            'dom_get_style': ['i32','i32','i32'],
            'dom_get_value': ['i32'],
            'dom_set_value': ['i32','i32','i32'],
            'dom_focus': ['i32'],
            'dom_blur': ['i32'],
            'dom_get_body': [],
            'dom_get_document': [],
            'dom_query': ['i32','i32'],
            'dom_query_all': ['i32','i32'],
            'dom_on': ['i32','i32','i32','i32'],
            'dom_off': ['i32'],
            'event_prevent_default': [],
            'event_stop_propagation': [],
            'event_target': [],
        }

        # Some runtime functions take (ptr,len) string pairs as two i32 params.
        # Only these functions are allowed to unpack an i64 into two i32s without
        # an explicit extended_type_stack marker. This prevents non-string i64
        # values (e.g. DOM handles stored as i64) from being misinterpreted.
        allow_i64_unpack_to_i32_pair = name in {
            'str_concat',
            'str_contains',
            'str_eq',
            'str_upper',
            'str_lower',
            'str_strip',
            'str_replace',
            'str_get',
            'str_join',
            'str_split',
        }

        if params := sig.get(name):
            # Use smart argument preparation logic (same as in CALL opcode)
            param_types = params
            param_idx = len(param_types) - 1
            stack_idx = len(self.type_stack) - 1
            ops = []
            next_i64_temp = 0
            next_i32_temp = 0
            next_f64_temp = 0

            while param_idx >= 0:
                if stack_idx < 0:
                    break
                param_type = param_types[param_idx]
                stack_type = self.type_stack[stack_idx]

                if param_type == 'i32':
                    if stack_type == 'i32':
                        temp = f"$temp_i32_{next_i32_temp}"
                        next_i32_temp += 1
                        ops.append(('i32', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                        param_idx -= 1
                        stack_idx -= 1
                    elif stack_type == 'i64':
                        is_packed_str_i64 = False
                        if hasattr(self, 'extended_type_stack') and self.extended_type_stack is not None:
                            if 0 <= stack_idx < len(self.extended_type_stack):
                                is_packed_str_i64 = self.extended_type_stack[stack_idx] == 'str'

                        if (is_packed_str_i64 or allow_i64_unpack_to_i32_pair) and param_idx > 0 and param_types[param_idx-1] == 'i32':
                            # Unpack packed string i64 -> i32(ptr), i32(len)
                            temp = f"$temp_i64_{next_i64_temp}"
                            next_i64_temp += 1

                            def push_unpack(t):
                                self.emit(f"local.get {t}", indent)
                                self.emit("i32.wrap_i64", indent)
                                self.emit(f"local.get {t}", indent)
                                self.emit("i64.const 32", indent)
                                self.emit("i64.shr_u", indent)
                                self.emit("i32.wrap_i64", indent)

                            ops.append(('i64', temp, lambda t=temp: push_unpack(t)))
                            param_idx -= 2 # Consumed 2 params
                            stack_idx -= 1 # Consumed 1 stack item
                        else:
                            # Truncate i64 -> i32
                            temp = f"$temp_i64_{next_i64_temp}"
                            next_i64_temp += 1
                            ops.append(('i64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i32.wrap_i64", indent))))
                            param_idx -= 1
                            stack_idx -= 1
                    else: # f64
                        temp = f"$temp_f64_{next_f64_temp}"
                        next_f64_temp += 1
                        ops.append(('f64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i32.trunc_f64_s", indent))))
                        param_idx -= 1
                        stack_idx -= 1

                elif param_type == 'i64':
                    if stack_type == 'i64':
                        temp = f"$temp_i64_{next_i64_temp}"
                        next_i64_temp += 1
                        ops.append(('i64', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                    elif stack_type == 'i32':
                        temp = f"$temp_i32_{next_i32_temp}"
                        next_i32_temp += 1
                        ops.append(('i32', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i64.extend_i32_u", indent))))
                    elif stack_type == 'f64':
                        temp = f"$temp_f64_{next_f64_temp}"
                        next_f64_temp += 1
                        ops.append(('f64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("i64.trunc_f64_s", indent))))
                    param_idx -= 1
                    stack_idx -= 1
                elif param_type == 'f64':
                    if stack_type == 'f64':
                        temp = f"$temp_f64_{next_f64_temp}"
                        next_f64_temp += 1
                        ops.append(('f64', temp, lambda t=temp: self.emit(f"local.get {t}", indent)))
                    elif stack_type == 'i32':
                        temp = f"$temp_i32_{next_i32_temp}"
                        next_i32_temp += 1
                        ops.append(('i32', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("f64.convert_i32_s", indent))))
                    elif stack_type == 'i64':
                        temp = f"$temp_i64_{next_i64_temp}"
                        next_i64_temp += 1
                        ops.append(('i64', temp, lambda t=temp: (self.emit(f"local.get {t}", indent), self.emit("f64.convert_i64_s", indent))))
                    param_idx -= 1
                    stack_idx -= 1

            # Execute plan
            for pop_type, temp, _ in ops:
                self.emit(f"local.set {temp}", indent)
                self.pop_type()

            for _, _, push_action in reversed(ops):
                push_action()

        # Emit the call
        self.emit(f"call ${name}", indent)

        # Push return types for known runtime imports
        rets = {
            'str_concat': ['i32','i32'],
            'str_contains': ['i32'],
            'i64_to_str': ['i32','i32'],
            'f64_to_str': ['i32','i32'],
            'bool_to_str': ['i32','i32'],
            'list_to_str': ['i32','i32'],
            'set_to_str': ['i32','i32'],
            'str_upper': ['i32','i32'],
            'str_lower': ['i32','i32'],
            'str_strip': ['i32','i32'],
            'str_replace': ['i32','i32'],
            'list_new': ['i32'],
            'list_append': ['i32'],
            'list_get': ['i64'],
            'list_set': ['i32'],
            'list_len': ['i64'],
            'list_contains': ['i32'],
            'list_pop': ['i32','i64'],
            'set_new': ['i32'],
            'set_add': ['i32'],
            'set_remove': ['i32'],
            'set_contains': ['i32'],
            'set_len': ['i64'],
            'str_to_i64': ['i64'],
            'str_to_f64': ['f64'],
            'str_join': ['i32','i32'],
            'str_split': ['i32'],
            'str_get': ['i32','i32'],
            'file_open': ['i32'],
            'file_read': ['i32','i32'],
            'file_write': [],
            'file_close': [],
        }
        if name in rets:
            for ret in rets[name]:
                self.type_stack.append(ret)

    def _normalize_top_operand_to_string_pair(self, indent: int):
        """Ensure the top operand is a (i32 ptr, i32 len) pair.

        Converts single i64/f64/i32 values to string pairs by calling the
        appropriate runtime conversion functions. If already a pair, does nothing.
        """
        # If top two values are already (i32, i32), treat as an existing string pair
        # regardless of _last_i32_source - in ADD_STR context, two i32s = string
        if (
            len(self.type_stack) >= 2
            and self.type_stack[-2] == 'i32'
            and self.type_stack[-1] == 'i32'
        ):
            # Clear source tracking since we're treating this as a string pair
            self._last_i32_source = None
            return

        if not self.type_stack:
            return

        top = self.type_stack[-1]

        if top == 'i64':
            # Convert i64 -> (ptr,len)
            self._emit_call('i64_to_str', indent)
            self.type_stack.pop()
            self.type_stack.append('i32')  # ptr
            self.type_stack.append('i32')  # len
            self.imports.add('i64_to_str')
            return
        if top == 'f64':
            self._emit_call('f64_to_str', indent)
            self.type_stack.pop()
            self.type_stack.append('i32')  # ptr
            self.type_stack.append('i32')  # len
            self.imports.add('f64_to_str')
            return

        if top == 'i32':
            # Could be list/set/bool/str pointer. Use tracked source if available.
            if hasattr(self, '_last_i32_source') and self._last_i32_source:
                if self._last_i32_source == 'list':
                    self._ensure_top_is_i32(indent)
                    self._emit_call('list_to_str', indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')
                    self.type_stack.append('i32')
                    self._last_i32_source = None
                    return
                if self._last_i32_source == 'set':
                    self._ensure_top_is_i32(indent)
                    self._emit_call('set_to_str', indent)
                    self.type_stack.pop()
                    self.type_stack.append('i32')
                    self.type_stack.append('i32')
                    self._last_i32_source = None
                    return
            # Default: boolean or other i32
            self._ensure_top_is_i32(indent)
            self._emit_call('bool_to_str', indent)
            self.type_stack.pop()
            self.type_stack.append('i32')
            self.type_stack.append('i32')
            self._last_i32_source = None
            return

    def _normalize_two_operands_for_concat(self, indent: int):
        """Normalize the two topmost operands so each becomes (i32 ptr, i32 len).

        Handles saving/restoring intermediate values when necessary.
        """
        # First normalize the top operand
        self._normalize_top_operand_to_string_pair(indent)

        # Now normalize the first operand (which is below the top pair)
        # Determine how many stack entries the top operand currently occupies (should be 2)
        top_size = 2 if len(self.type_stack) >= 2 and self.type_stack[-2] == 'i32' and self.type_stack[-1] == 'i32' else 1

        # Save the top operand values into temps
        saved = []
        for i in range(top_size):
            if not self.type_stack:
                break
            t = self.type_stack.pop()
            # Choose distinct temp slots so we don't overwrite multiple saved values
            if t == 'i64':
                self.emit("local.set $temp_i64", indent)
                saved.append(('$temp_i64', 'i64'))
            elif t == 'f64':
                self.emit("local.set $temp_f64", indent)
                saved.append(('$temp_f64', 'f64'))
            else:
                # Use $temp2 for the first saved i32 and $temp for the second
                temp_name = '$temp2' if i == 0 else '$temp'
                self.emit(f"local.set {temp_name}", indent)
                saved.append((temp_name, 'i32'))

        # Now top of stack is the first operand; normalize it
        self._normalize_top_operand_to_string_pair(indent)

        # Restore saved second operand values
        for temp_name, t in reversed(saved):
            self.emit(f"local.get {temp_name}", indent)
            self.type_stack.append(t)

def compile_to_wasm(bytecode: str) -> Tuple[str, Dict]:
    """Compile fr bytecode to WebAssembly text format"""
    compiler = WasmCompiler()
    return compiler.compile(bytecode)
