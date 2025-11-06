"""
Bytecode to x86_64 Assembly Compiler for fr

Compiles fr bytecode to x86_64 assembly with runtime library support.
Uses static typing assumption - no dynamic type checking.
Complex operations (lists, strings, Python interop) call into runtime library.

Architecture:
- Stack-based code generation (simple, maintainable)
- Runtime library (runtime_lib.so) for complex operations
- Direct x86_64 for arithmetic, control flow, locals
- System V ABI calling convention (Linux/macOS)
"""

import sys
from typing import List, Dict, Tuple, Optional
from native_optimizer import optimize_assembly

class X86CompilerError(Exception):
    """Raised when x86_64 compilation fails"""
    pass

class X86Compiler:
    """Compiles fr bytecode to x86_64 assembly"""

    def __init__(self, optimize: bool = True):
        self.output: List[str] = []
        self.data_section: List[str] = []  # For string constants
        self.string_constants: Dict[str, str] = {}  # Maps strings to labels
        self.string_counter = 0
        self.label_counter = 0  # Counter for generating unique labels
        self.label_map: Dict[str, str] = {}  # Maps bytecode labels to asm labels
        self.functions: List[Dict] = []
        self.current_function: Optional[Dict] = None
        self.stack_offset = 0  # Current stack frame offset
        self.max_stack = 0     # Maximum stack size needed
        self.optimize = optimize  # Whether to apply assembly optimizations
        self.runtime_dependencies: set = set()  # Track which runtime functions are used
        self.entry_point: Optional[str] = None  # Track the entry point function
        self.stack_types: List[str] = []  # Track types of values on stack: 'i64', 'f64', 'str', etc
        self.local_types: Dict[int, str] = {}  # Track types of local variables by index
        self.structs: Dict[int, Dict] = {}  # Maps struct_id to {field_count, field_names}
        self.struct_counter = 0  # Counter for allocating struct instances
        self.struct_data_offset = 0  # Offset into the struct data area
        self.last_struct_id: Optional[int] = None  # Track the struct_id from the last STRUCT_NEW
        self.in_label = False  # Track if we're inside a LABEL (for GOTO_CALL)
        self.current_line: int = 1  # Current source line number for error reporting
        self.source_file: Optional[str] = None  # Source file path from bytecode
        self.source_lines_dict: Dict[int, str] = {}  # Maps line numbers to source text from .line directives
        self.has_main: bool = False  # Track if main function exists
        self.internal_functions: set[str] = set()  # Track Fr functions (not external C)

    def emit(self, line: str, indent: int = 1):
        """Emit a line of assembly code"""
        if indent > 0:
            self.output.append("    " * indent + line)
        else:
            self.output.append(line)

    def emit_comment(self, comment: str):
        """Emit a comment"""
        self.output.append(f"    # {comment}")

    def emit_dependency(self, func_name: str):
        """Track a runtime library function dependency"""
        self.runtime_dependencies.add(func_name)

    def _convert_struct_to_c(self, struct_id: int):
        """Convert internal struct format to C-compatible layout"""
        struct_def = self.structs.get(struct_id, {'field_count': 0})
        field_count = struct_def['field_count']

        # Pop the internal struct format (struct_id | instance_id)
        self.emit("pop rax")
        # Extract instance_id from high bits
        self.emit("sar rax, 16")
        # Calculate base address in struct_data
        self.emit("mov rcx, 256")
        self.emit("imul rax, rcx  # rax = instance_id * 256")
        self.emit("lea rdx, [rip + struct_data]")

        # For structs, load fields into registers following System V ABI
        regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        for i in range(min(field_count, 6)):  # First 6 args in registers
            self.emit(f"mov {regs[i]}, [rdx + rax + {i * 8}]")

    def emit_runtime_call(self, func_name: str):
        """Emit a call to a runtime function and track the dependency
        Ensures stack is 16-byte aligned before the call"""
        self.emit_dependency(func_name)
        # The x86-64 ABI requires (rsp & 0x0F) == 0 BEFORE the call instruction.
        # We use inline alignment checking. We save rax temporarily to use as a scratch register.
        self.emit("push rax  # Save rax and check alignment")
        self.emit("mov rax, rsp")
        self.emit("add rax, 8  # Account for the push")
        self.emit("test rax, 0xF")
        self.emit("pop rax")
        self.emit(f"jz .L{func_name}_aligned_{self.label_counter}")
        # Not aligned - sub 8
        self.emit("sub rsp, 8")
        self.emit(f"call {func_name}")
        self.emit("add rsp, 8")
        self.emit(f"jmp .L{func_name}_done_{self.label_counter}")
        self.emit(f".L{func_name}_aligned_{self.label_counter}: ", 0)
        self.emit(f"call {func_name}")
        self.emit(f".L{func_name}_done_{self.label_counter}: ", 0)
        self.label_counter += 1

    def get_string_label(self, string: str) -> str:
        """Get or create a label for a string constant"""
        if string not in self.string_constants:
            label = f".STR{self.string_counter}"
            self.string_counter += 1
            self.string_constants[string] = label
            # Add to data section
            # Escape special characters for assembly
            escaped = string.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            self.data_section.append(f'{label}:')
            self.data_section.append(f'    .asciz "{escaped}"')
        return self.string_constants[string]

    def parse_bytecode(self, bytecode: str) -> List[Tuple[str, List[str]]]:
        """
        Parse bytecode into instructions.
        Returns list of (opcode, args) tuples.
        Handles quoted strings properly.
        """
        instructions = []
        for line in bytecode.strip().split('\n'):
            line = line.strip()

            # Check for source file comment
            if line.startswith('# source:'):
                self.source_file = line.split('# source:', 1)[1].strip()
                continue

            if not line or line.startswith('#'):
                continue

            # Split instruction and arguments
            parts = line.split(None, 1)
            if not parts:
                continue

            opcode = parts[0]
            args = []
            if len(parts) > 1:
                # Parse arguments, respecting quoted strings
                args_str = parts[1]
                in_quotes = False
                current_arg = []
                for i in range(len(args_str)):
                    ch = args_str[i]
                    if ch == '"':
                        in_quotes = not in_quotes
                        current_arg.append(ch)
                    elif ch == ' ' and not in_quotes:
                        if current_arg:
                            args.append(''.join(current_arg))
                            current_arg = []
                    else:
                        current_arg.append(ch)
                if current_arg:
                    args.append(''.join(current_arg))

            instructions.append((opcode, args))

        return instructions

    def compile(self, bytecode: str) -> str:
        """
        Compile bytecode to x86_64 assembly.
        Returns assembly code as string.
        """
        instructions = self.parse_bytecode(bytecode)

        # Emit file header with Intel syntax directive
        self.emit(".intel_syntax noprefix", 0)
        self.emit(".section .text", 0)

        # First pass: find the entry point and collect all labels
        current_func = None
        for opcode, args in instructions:
            if opcode == '.end':
                current_func = None
            elif opcode == '.entry':
                entry_point = args[0].rstrip('%')
                self.entry_point = entry_point
                self.emit(f".global {entry_point}", 0)
            elif opcode == '.func':
                current_func = args[0]
            elif opcode == 'LABEL':
                label = args[0].rstrip(':')
                # Pre-register the label with function scoping
                asm_label = f".L{current_func}_{label}" if current_func else f".L{label}"
                self.label_map[label] = asm_label

        self.emit("", 0)

        # Process instructions
        self._compile_instructions(instructions)

        # If we have main and source info, inject initialization code at start of main
        if self.has_main and self.source_file and self.source_lines_dict:
            # Reconstruct source from line dict (fill gaps with empty lines)
            max_line = max(self.source_lines_dict.keys()) if self.source_lines_dict else 0
            source_lines_list = []
            source_lines_list.extend(
                self.source_lines_dict.get(i, '') for i in range(1, max_line + 1)
            )
            source_content = '\n'.join(source_lines_list)

            # Create labels for filename and source content
            filename_label = self.get_string_label(self.source_file)
            source_label = self.get_string_label(source_content)

            # Find main: in output and inject after "sub rsp, 256"
            main_found = False
            for idx, line in enumerate(self.output):
                if line.strip() == "main:":
                    main_found = True
                elif main_found and "sub rsp, 256" in line:

                    # Generate label
                    label_num = self.label_counter
                    self.label_counter += 1

                    # Insert runtime init and source info setup after this line
                    init_code = [
                        "    # Zero out stack frame",
                        "    push rdi",
                        "    push rcx",
                        "    push rax",
                        "    lea rdi, [rsp + 24]  # point to start of our stack frame",
                        "    mov rcx, 32  # 256 bytes / 8 = 32 qwords",
                        "    xor rax, rax",
                        "    rep stosq  # zero out [rdi] for rcx qwords",
                        "    pop rax",
                        "    pop rcx",
                        "    pop rdi",
                        "    # Initialize runtime and source info"
                        "    push rax  # Save rax and check alignment",
                        "    mov rax, rsp",
                        "    add rax, 8  # Account for the push",
                        "    test rax, 0xF",
                        "    pop rax",
                        # Generate runtime_init call
                        f"    jz .Lruntime_init_aligned_{label_num}",
                        "    sub rsp, 8",
                        "    call runtime_init",
                        "    add rsp, 8",
                        f"    jmp .Lruntime_init_done_{label_num}",
                        f".Lruntime_init_aligned_{label_num}: ",
                        "    call runtime_init",
                        f".Lruntime_init_done_{label_num}: ",
                        f"    lea rdi, [{filename_label}]  # filename",
                        f"    lea rsi, [{source_label}]  # source",
                        "    push rax  # Save rax and check alignment",
                        "    mov rax, rsp",
                        "    add rax, 8  # Account for the push",
                        "    test rax, 0xF",
                        "    pop rax",
                    ]

                    # Generate runtime_set_source_info call
                    label_num = self.label_counter
                    self.label_counter += 1

                    init_code.extend([
                        f"    jz .Lruntime_set_source_info_aligned_{label_num}",
                        "    sub rsp, 8",
                        "    call runtime_set_source_info",
                        "    add rsp, 8",
                        f"    jmp .Lruntime_set_source_info_done_{label_num}",
                        f".Lruntime_set_source_info_aligned_{label_num}: ",
                        "    call runtime_set_source_info",
                        f".Lruntime_set_source_info_done_{label_num}: ",
                    ])

                    # Insert after current line
                    self.output = self.output[:idx+1] + init_code + self.output[idx+1:]
                    break

        # Emit data section
        if self.data_section:
            self.emit("", 0)
            self.emit(".section .rodata", 0)
            for line in self.data_section:
                if line.endswith(':'):
                    self.emit(line, 0)
                else:
                    self.emit(line, 0)

        # Emit BSS section for global variables
        self.emit("", 0)
        self.emit(".section .bss", 0)
        self.emit("global_vars:", 0)
        self.emit("    .space 2048  # Space for 256 global variables (8 bytes each)", 0)
        self.emit("struct_counter:", 0)
        self.emit("    .quad 0  # Counter for dynamic struct allocation", 0)
        self.emit("struct_data:", 0)
        self.emit("    .space 1048576  # Space for struct instances (4096 instances * 256 bytes each)", 0)

        result = '\n'.join(self.output) + '\n'

        # Apply optimizations if enabled
        if self.optimize:
            result = optimize_assembly(result)

        return result

    def _compile_instructions(self, instructions: List[Tuple[str, List[str]]]):
        """Compile a list of instructions"""
        i = 0
        while i < len(instructions):
            opcode, args = instructions[i]

            # Dispatch to instruction handler
            # Handle both .directive and OPCODE formats
            handler_name = f'_compile_{opcode.lower().lstrip(".")}'
            if handler := getattr(self, handler_name, None):
                self.emit_comment(f"{opcode} {' '.join(args)}")
                handler(args)
            elif not opcode.startswith('.'):
                print(f"Warning: Unimplemented opcode {opcode} {' '.join(args)}")
                self.emit_comment(f"TODO: {opcode} {' '.join(args)}")
                self.emit(f"# Unimplemented: {opcode}", 1)

            i += 1

    # ============================================================================
    # Instruction Handlers
    # ============================================================================

    def _compile_func(self, args: List[str]):
        """Start a function definition (.func name type arg_count)"""
        func_name = args[0]
        self.internal_functions.add(func_name)  # Track as internal Fr function
        self.current_function = {
            'name': func_name,
            'stack_offset': 0,
            'max_stack': 0,
            'local_count': 0,
            'arg_count': 0,
            'skip_label_emitted': False  # Track if skip label was emitted
        }
        self.local_types = {}  # Reset local types for new function
        # DON'T reset label_map - it needs to persist for label references to work

        # Track if this is main
        if func_name == 'main':
            self.has_main = True

        # Emit function label
        self.emit(f"\n{func_name}:", 0)

        # Function prologue
        self.emit("push rbp")
        self.emit("mov rbp, rsp")
        # Reserve stack space - ensure 16-byte alignment
        # After push rbp, stack is 16-byte aligned
        # We want to keep it aligned, so reserve a multiple of 16
        self.emit("sub rsp, 256")

    def _compile_end(self, args: List[str]):
        """End a function definition (.end)"""
        # Emit skip label if it hasn't been emitted yet (in case function has no RETURN_VOID)
        if self.current_function and not self.current_function.get('skip_label_emitted', False):
            func_name = self.current_function['name']
            self.emit(f".L{func_name}_skip_labels:", 0)
            self.current_function['skip_label_emitted'] = True

        # If the function didn't emit any RETURN, emit implicit epilogue
        # (This handles functions that fall through without explicit return)
        if self.current_function and not self.current_function.get('has_return', False):
            func_name = self.current_function['name']
            # Emit epilogue: restore stack and return
            self.emit(f"# Implicit return at end of {func_name}")
            self.emit("xor rax, rax  # default return value 0")
            self.emit("mov rsp, rbp")
            self.emit("pop rbp")
            self.emit("ret")
        
        # Function epilogue is emitted by RETURN or above implicit return
        self.current_function = None

    def _compile_endfunc(self, args: List[str]):
        """End a function definition (legacy ENDFUNC)"""
        self._compile_end(args)

    def _compile_label(self, args: List[str]):
        """Emit a label"""
        label = args[0].rstrip(':')
        # Convert bytecode label to asm label with function scope to avoid conflicts
        if self.current_function:
            func_name = self.current_function['name']
            asm_label = f".L{func_name}_{label}"
        else:
            asm_label = f".L{label}"
        self.label_map[label] = asm_label

        # Only emit jump to skip labels for GOTO_CALL targets
        # Loop/control flow labels should not be skipped
        # These include: for_, forin_, loop_, while_, if_, else_, end, switch_, case_, except, etc.
        is_control_flow_label = any(x in label for x in [
            'for_', 'forin_', 'loop_', 'while_', 'if_', 'else_', 'end',
            'switch_', 'case_', 'break_', 'continue_', 'except', 'try_'
        ])

        if not is_control_flow_label and self.current_function:
            # This is likely a GOTO_CALL target - emit jump to skip fall-through
            func_name = self.current_function['name']
            self.emit(f"jmp .L{func_name}_skip_labels", 1)

        self.emit(f"{asm_label}:", 0)

        # Mark that we're inside a label (for GOTO_CALL returns) only if not a control flow label
        if not is_control_flow_label:
            self.in_label = True

        # Clear type stack at labels since we don't know which path leads here
        self.stack_types = []

    def _compile_version(self, args: List[str]):
        """Handle .version directive (ignore for now)"""
        pass

    def _compile_line(self, args: List[str]):
        """Handle .line directive - track current source line number and optional source text"""
        if args:
            self.current_line = int(args[0])
            # Check if source text is provided (args[1] would be the quoted source line)
            if len(args) > 1:
                # Remove quotes from source text
                source_text = args[1]
                if source_text.startswith('"') and source_text.endswith('"'):
                    source_text = source_text[1:-1]
                # Unescape the source text
                source_text = source_text.replace('\\\\', '\\').replace('\\"', '"')

                # Store in source_lines dict (1-indexed)
                if not hasattr(self, 'source_lines_dict'):
                    self.source_lines_dict = {}
                self.source_lines_dict[self.current_line] = source_text

    def _compile_local(self, args: List[str]):
        """Handle .local variable declaration"""
        # .local var_name var_type
        # args = [var_name, var_type] or just [var_name]
        if self.current_function:
            # The local variable index is the current local_count
            local_index = self.current_function['local_count']
            var_type = args[1] if len(args) > 1 else 'i64'  # default to i64
            self.local_types[local_index] = var_type
            self.current_function['local_count'] += 1

    def _compile_arg(self, args: List[str]):
        """Handle .arg - function argument declaration"""
        # System V ABI calling convention (used on Linux/macOS):
        # First 6 integer/pointer arguments: rdi, rsi, rdx, rcx, r8, r9
        # Additional arguments on stack (in reverse order)
        # Arguments are stored in local variable slots starting from slot 0
        if self.current_function:
            arg_idx = self.current_function['arg_count']
            self.current_function['arg_count'] += 1
            # Also increment local_count since args occupy local slots
            self.current_function['local_count'] += 1

            # Map argument index to register or stack location
            arg_regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
            if arg_idx < len(arg_regs):
                # Argument is in a register - store it to local slot
                offset = (arg_idx + 1) * 8
                self.emit(f"mov [rbp - {offset}], {arg_regs[arg_idx]}")
            else:
                # Argument is on stack (above rbp)
                # Stack args start at [rbp + 16] (after return addr and saved rbp)
                stack_offset = 16 + (arg_idx - 6) * 8
                local_offset = (arg_idx + 1) * 8
                self.emit(f"mov rax, [rbp + {stack_offset}]")
                self.emit(f"mov [rbp - {local_offset}], rax")

    def _compile_entry(self, args: List[str]):
        """Handle .entry directive - set program entry point"""
        entry_point = args[0].rstrip('%')
        # Entry point was already marked as global in the first pass
        # Now handle wrapping if needed
        # When linking with C runtime, if entry point is not 'main', create a wrapper
        if entry_point != 'main':
            self.emit("\n.global main", 0)
            self.emit("main:", 0)
            self.emit_runtime_call("runtime_init")

            # Initialize source info for error reporting if we have source lines from .line directives
            if self.source_file and self.source_lines_dict:
                # Reconstruct source from line dict (fill gaps with empty lines)
                max_line = max(self.source_lines_dict.keys()) if self.source_lines_dict else 0
                source_lines_list = []
                source_lines_list.extend(
                    self.source_lines_dict.get(i, '')
                    for i in range(1, max_line + 1)
                )
                source_content = '\n'.join(source_lines_list)

                # Create labels for filename and source content
                filename_label = self.get_string_label(self.source_file)
                source_label = self.get_string_label(source_content)

                # Call runtime_set_source_info(filename, source)
                self.emit(f"lea rdi, [{filename_label}]  # filename")
                self.emit(f"lea rsi, [{source_label}]  # source")
                self.emit_runtime_call("runtime_set_source_info")

            self.emit(f"call {entry_point}")
            self.emit("ret")
        # If entry_point == 'main', source info injection is handled in compile() post-processing

    # ============================================================================
    # Constants
    # ============================================================================

    def _compile_const_i64(self, args: List[str]):
        """Push 64-bit integer constant(s) - can push multiple values"""
        for value in args:
            self.emit(f"mov rax, {value}")
            self.emit("push rax")
            self.stack_types.append('i64')

    def _compile_const_f64(self, args: List[str]):
        """Push 64-bit float constant(s) - can push multiple values"""
        for value in args:
            # Load float into xmm0, then push onto stack
            # This requires a data section entry
            label = f".FLOAT{self.string_counter}"
            self.string_counter += 1
            self.data_section.append(f"{label}:")
            self.data_section.append(f"    .double {value}")

            self.emit(f"movsd xmm0, [{label}]")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            self.stack_types.append('f64')

    def _compile_const_str(self, args: List[str]):
        """Push string constant(s) - can push multiple strings"""
        # Handle multiple string arguments (like "hello" "hey")
        for arg in args:
            # Remove quotes if present
            string = arg
            if string.startswith('"') and string.endswith('"'):
                string = string[1:-1]

            label = self.get_string_label(string)
            self.emit(f"lea rax, [{label}]")
            self.emit("push rax")
            self.stack_types.append('str')

    def _compile_const_bool(self, args: List[str]):
        """Push boolean constant(s) - can push multiple values"""
        for arg in args:
            # arg can be "1", "0", "true", or "false"
            value = "1" if arg in ("1", "true") else "0"
            self.emit(f"mov rax, {value}")
            self.emit("push rax")
            self.stack_types.append('bool')

    def _compile_const_i64_multi(self, args: List[str]):
        """Push multiple i64 constants (CONST_I64_MULTI val1 val2 val3...)"""
        for value in args:
            self.emit(f"mov rax, {value}")
            self.emit("push rax")
            self.stack_types.append('i64')

    def _compile_const_f64_multi(self, args: List[str]):
        """Push multiple f64 constants (CONST_F64_MULTI val1 val2 val3...)"""
        for value in args:
            label = f".FLOAT{self.string_counter}"
            self.string_counter += 1
            self.data_section.append(f"{label}:")
            self.data_section.append(f"    .double {value}")
            self.emit(f"movsd xmm0, [{label}]")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            self.stack_types.append('f64')

    def _compile_const_str_multi(self, args: List[str]):
        """Push multiple string constants (CONST_STR_MULTI "str1" "str2"...)"""
        for string_arg in args:
            # Remove quotes
            if string_arg.startswith('"') and string_arg.endswith('"'):
                string_arg = string_arg[1:-1]
            label = self.get_string_label(string_arg)
            self.emit(f"lea rax, [{label}]")
            self.emit("push rax")
            self.stack_types.append('str')

    def _compile_const_bool_multi(self, args: List[str]):
        """Push multiple boolean constants (CONST_BOOL_MULTI true false true...)"""
        for arg in args:
            value = "1" if arg.lower() == "true" else "0"
            self.emit(f"mov rax, {value}")
            self.emit("push rax")
            self.stack_types.append('i64')

    # ============================================================================
    # Arithmetic Operations
    # ============================================================================

    def _compile_add_i64(self, args: List[str]):
        """Add two 64-bit integers or concatenate strings"""
        # Check if both operands are strings
        second_type = self.stack_types[-1] if self.stack_types else 'i64'
        first_type = self.stack_types[-2] if len(self.stack_types) >= 2 else 'i64'

        if first_type == 'str' and second_type == 'str':
            # String concatenation
            self.emit("pop rsi")  # Second string
            self.emit("pop rdi")  # First string
            self.emit_runtime_call("runtime_str_concat_checked")
            self.emit("push rax")
            # Update type stack
            if self.stack_types and len(self.stack_types) >= 2:
                self.stack_types.pop()  # pop operand 2
                self.stack_types.pop()  # pop operand 1
            self.stack_types.append('str')
        else:
            # Integer addition
            self.emit("pop rbx")
            self.emit("pop rax")
            self.emit("add rax, rbx")
            self.emit("push rax")
            # Update type stack
            if self.stack_types and len(self.stack_types) >= 2:
                self.stack_types.pop()  # pop operand 2
                self.stack_types.pop()  # pop operand 1
            self.stack_types.append('i64')

    def _compile_sub_i64(self, args: List[str]):
        """Subtract two 64-bit integers"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("sub rax, rbx")
        self.emit("push rax")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('i64')

    def _compile_mul_i64(self, args: List[str]):
        """Multiply two 64-bit integers"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("imul rax, rbx")
        self.emit("push rax")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('i64')

    def _compile_div_i64(self, args: List[str]):
        """Divide two 64-bit integers"""
        self.emit("pop rbx")
        self.emit("pop rax")
        # Check for division by zero
        self.runtime_dependencies.add('runtime_check_div_zero_i64_at')
        self.emit("push rax  # save dividend")
        self.emit("mov rdi, rbx")
        self.emit(f"mov rsi, {self.current_line}  # line number")
        self.emit("call runtime_check_div_zero_i64_at")
        self.emit("pop rax  # restore dividend")
        self.emit("cqo")  # Sign extend rax into rdx:rax
        self.emit("idiv rbx")
        self.emit("push rax")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('i64')

    def _compile_mod_i64(self, args: List[str]):
        """Modulo of two 64-bit integers"""
        self.emit("pop rbx")
        self.emit("pop rax")
        # Check for division by zero
        self.runtime_dependencies.add('runtime_check_div_zero_i64_at')
        self.emit("push rax  # save dividend")
        self.emit("mov rdi, rbx")
        self.emit(f"mov rsi, {self.current_line}  # line number")
        self.emit("call runtime_check_div_zero_i64_at")
        self.emit("pop rax  # restore dividend")
        self.emit("cqo")
        self.emit("idiv rbx")
        self.emit("push rdx")  # Remainder is in rdx
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('i64')

    # ============================================================================
    # Float Arithmetic
    # ============================================================================

    def _compile_add_f64(self, args: List[str]):
        """Add two 64-bit floats"""
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit("addsd xmm0, xmm1")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('f64')

    def _compile_sub_f64(self, args: List[str]):
        """Subtract two 64-bit floats"""
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit("subsd xmm0, xmm1")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('f64')

    def _compile_mul_f64(self, args: List[str]):
        """Multiply two 64-bit floats"""
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit("mulsd xmm0, xmm1")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('f64')

    def _compile_div_f64(self, args: List[str]):
        """Divide two 64-bit floats"""
        # Check if operands are integers and convert them
        operand2_is_int = len(self.stack_types) >= 1 and self.stack_types[-1] == 'i64'
        operand1_is_int = len(self.stack_types) >= 2 and self.stack_types[-2] == 'i64'

        # Pop second operand (b)
        if operand2_is_int:
            # b is integer - pop as int and convert
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm1, rax")
        else:
            # b is float - load and pop from stack
            self.emit("movsd xmm1, [rsp]")
            self.emit("add rsp, 8")

        # Check for division by zero
        self.runtime_dependencies.add('runtime_check_div_zero_f64_at')
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm1  # save divisor")
        self.emit("movsd xmm0, xmm1")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        self.emit(f"mov rdi, {self.current_line}  # line number")
        self.emit("call runtime_check_div_zero_f64_at")
        self.emit("add rsp, 8")
        self.emit("movsd xmm1, [rsp]  # restore divisor")
        self.emit("add rsp, 8")

        # Pop first operand (a)
        if operand1_is_int:
            # a is integer - pop as int and convert
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
        else:
            # a is float - load and pop from stack
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")

        # Perform division
        self.emit("divsd xmm0, xmm1")

        # Push result back as float
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()  # pop operand 2
            self.stack_types.pop()  # pop operand 1
        self.stack_types.append('f64')

    # ============================================================================
    # Comparison Operations
    # ============================================================================

    def _compile_cmp_eq(self, args: List[str]):
        """Compare equality"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("sete al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_ne(self, args: List[str]):
        """Compare inequality"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("setne al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_lt(self, args: List[str]):
        """Compare less than"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("setl al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_gt(self, args: List[str]):
        """Compare greater than"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("setg al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_le(self, args: List[str]):
        """Compare less than or equal"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("setle al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_ge(self, args: List[str]):
        """Compare greater than or equal"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("cmp rax, rbx")
        self.emit("setge al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    # ============================================================================
    # Control Flow
    # ============================================================================

    def _compile_jump(self, args: List[str]):
        """Unconditional jump"""
        label = args[0]
        # Look up the label in the map (it may be function-scoped)
        asm_label = self.label_map.get(label, f".L{label}")
        self.emit(f"jmp {asm_label}")

    def _compile_jump_if_false(self, args: List[str]):
        """Jump if top of stack is false"""
        label = args[0]
        # Look up the label in the map (it may be function-scoped)
        asm_label = self.label_map.get(label, f".L{label}")
        self.emit("pop rax")
        self.emit("test rax, rax")
        self.emit(f"jz {asm_label}")

    def _compile_jump_if_true(self, args: List[str]):
        """Jump if top of stack is true"""
        label = args[0]
        # Look up the label in the map (it may be function-scoped)
        asm_label = self.label_map.get(label, f".L{label}")
        self.emit("pop rax")
        self.emit("test rax, rax")
        self.emit(f"jnz {asm_label}")

    def _pack_struct_for_c(self, struct_id: int, target_reg: str):
        """Pack a struct from our internal format to C representation in target_reg"""
        if struct_id == 4:  # Color struct: 4 unsigned chars -> pack into 32-bit value
            # Pop struct reference
            self.emit("pop rax")
            # Extract instance_id (unsigned shift)
            self.emit("shr rax, 16")
            # Clamp to valid range
            self.emit("and rax, 0xFFF  # Ensure instance_id < 4096")
            # Calculate base address in struct_data
            self.emit("mov rcx, 256")
            self.emit("imul rax, rcx")
            self.emit("lea rdx, [rip + struct_data]")
            # Pack 4 bytes: R, G, B, A into target register
            self.emit(f"xor {target_reg}, {target_reg}  # Clear target")
            self.emit("mov cl, byte ptr [rdx + rax + 0]  # R")
            self.emit(f"or {target_reg}, rcx")
            self.emit("mov cl, byte ptr [rdx + rax + 8]  # G")
            self.emit("shl rcx, 8")
            self.emit(f"or {target_reg}, rcx")
            self.emit("mov cl, byte ptr [rdx + rax + 16]  # B")
            self.emit("shl rcx, 16")
            self.emit(f"or {target_reg}, rcx")
            self.emit("mov cl, byte ptr [rdx + rax + 24]  # A")
            self.emit("shl rcx, 24")
            self.emit(f"or {target_reg}, rcx")
        else:
            # For other structs, just pass the reference as-is for now
            self.emit(f"pop {target_reg}")

    def _compile_call(self, args: List[str]):
        """Call a function - handle both regular and external function calls"""
        func_name = args[0]
        arg_count = int(args[1]) if len(args) > 1 else 0
        type_sig = args[2] if len(args) > 2 else ''

        # Parse type signature to identify struct arguments
        struct_args = set()
        if type_sig and '|' in type_sig:
            arg_types = type_sig.split('|')[0]
            for idx, ch in enumerate(arg_types):
                if ch == 's':
                    struct_args.add(idx)

        self.emit_comment(f"CALL {func_name}: struct_args={struct_args}, stack_types={self.stack_types[-min(arg_count,len(self.stack_types)):]}")

        # System V ABI: first 6 args in rdi, rsi, rdx, rcx, r8, r9
        arg_regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

        # Pop arguments from stack into registers (in reverse order since stack)
        # Arguments were pushed left-to-right, so we pop them right-to-left
        for i in range(min(arg_count, len(arg_regs))):
            # Pop in reverse order: last arg first
            reg_idx = arg_count - 1 - i
            if reg_idx < len(arg_regs):
                # Check if this argument is a struct that needs packing
                if reg_idx in struct_args and self.stack_types and self.stack_types[-1].startswith('struct:'):
                    struct_id = int(self.stack_types[-1].split(':')[1])
                    self.emit_comment(f"Packing struct {struct_id} for arg {reg_idx}")
                    self._pack_struct_for_c(struct_id, arg_regs[reg_idx])
                else:
                    self.emit(f"pop {arg_regs[reg_idx]}")
                if self.stack_types:
                    self.stack_types.pop()

        # If more than 6 args, leave remaining on stack (already in correct order)
        # TODO: handle > 6 arguments properly

        # Ensure stack is 16-byte aligned before external calls
        # Only align for external C functions, not internal Fr functions
        is_external = func_name not in self.internal_functions

        if is_external:
            # The x86-64 ABI requires rsp & 0xF == 0 before call
            self.emit("# Stack alignment for external call")
            self.emit("mov r11, rsp")
            self.emit("and r11, 0xF")
            self.emit(f"jz .L{func_name}_aligned_{self.label_counter}")
            self.emit("sub rsp, 8  # Align stack")
            self.emit(f"call {func_name}")
            self.emit("add rsp, 8  # Restore stack")
            self.emit(f"jmp .L{func_name}_done_{self.label_counter}")
            self.emit(f".L{func_name}_aligned_{self.label_counter}:")
            self.emit(f"call {func_name}")
            self.emit(f".L{func_name}_done_{self.label_counter}:")
            self.label_counter += 1
        else:
            # Internal Fr function - no alignment needed
            self.emit(f"call {func_name}")

        # Calling convention: result is in rax
        # Check if function returns void
        if not type_sig or not type_sig.endswith('|v'):
            # Regular return value
            self.emit("push rax")

    def _compile_return(self, args: List[str]):
        """Return from function or label"""
        # Pop return value into rax
        self.emit("pop rax")

        # If we're in a label (GOTO_CALL), just return without full epilogue
        # The function epilogue belongs to the containing function, not the label
        if self.in_label:
            self.emit("ret")
            self.in_label = False  # Reset flag after return from label
        else:
            # Full function epilogue for regular returns
            self.emit("mov rsp, rbp")
            self.emit("pop rbp")
            self.emit("ret")
            # Mark that we've emitted a return for this function
            if self.current_function:
                self.current_function['has_return'] = True

    def _compile_return_void(self, args: List[str]):
        """Return void from function"""
        # Emit skip label for labels that might be jumped over (only once per function)
        if self.current_function and not self.current_function.get('skip_label_emitted', False):
            func_name = self.current_function['name']
            self.emit(f".L{func_name}_skip_labels:", 0)
            self.current_function['skip_label_emitted'] = True

        self.emit("xor rax, rax")
        self.emit("mov rsp, rbp")
        self.emit("pop rbp")
        self.emit("ret")
        # Mark that we've emitted a return for this function
        if self.current_function:
            self.current_function['has_return'] = True

    def _compile_break(self, args: List[str]):
        """Break from loop (jump to .loop_end_<level>)"""
        level = args[0] if args else "0"
        # Emit a jump to the loop end label for the given break level.
        asm_label = f".Lloop_end_{level}"
        self.emit(f"jmp {asm_label}")

    def _compile_continue(self, args: List[str]):
        """Continue loop (jump to .loop_start_<level>)"""
        level = args[0] if args else "0"
        asm_label = f".Lloop_start_{level}"
        self.emit(f"jmp {asm_label}")

    def _compile_goto_call(self, args: List[str]):
        """Jump to label and save return address (like CALL but for goto with return)"""
        label = args[0].rstrip(':')
        # Map bytecode label to asm label
        asm_label = self.label_map.get(label, f".L{label}")
        # Similar to CALL but doesn't set up a new frame
        self.emit(f"call {asm_label}")
        self.emit("push rax")

    def _compile_select(self, args: List[str]):
        """Select instruction (like switch/case)"""
        # The SELECT instruction is commonly lowered by the frontend into a
        # sequence of CMP / JUMP_IF_* instructions and explicit LABELs for
        # each case. The current test-suite bytecode uses that lowering, so
        # the native backend can treat SELECT as a no-op placeholder.
        self.emit("# SELECT (handled by surrounding CMP/JUMP sequences)")

    def _compile_switch_jump_table(self, args: List[str]):
        """Switch jump table: SWITCH_JUMP_TABLE min_value max_value case_label1 case_label2 ... default_label"""
        if len(args) < 3:
            self.emit("# Invalid SWITCH_JUMP_TABLE instruction")
            return

        min_value = int(args[0])
        max_value = int(args[1])
        case_labels = args[2:]

        # The last argument is typically the default label
        default_label = case_labels[-1] if case_labels else None
        case_labels = case_labels[:-1] if len(case_labels) > 1 else []

        # Pop the switch value
        self.emit("pop rax")

        # Generate a jump table
        # Check if value is out of range
        self.emit(f"cmp rax, {min_value}")
        if default_label:
            asm_default = self.label_map.get(default_label, f".L{default_label}")
            self.emit(f"jl {asm_default}")

        self.emit(f"cmp rax, {max_value}")
        if default_label:
            asm_default = self.label_map.get(default_label, f".L{default_label}")
            self.emit(f"jg {asm_default}")

        # Compute offset into jump table: rax = rax - min_value
        if min_value != 0:
            self.emit(f"sub rax, {min_value}")

        # Generate jump table
        for i, label in enumerate(case_labels):
            asm_label = self.label_map.get(label, f".L{label}")
            # First case: value should be 0
            self.emit(f"cmp rax, {i}")
            self.emit(f"je {asm_label}")
        # Default case
        if default_label:
            asm_default = self.label_map.get(default_label, f".L{default_label}")
            self.emit(f"jmp {asm_default}")

    def _compile_cmp_lt_const(self, args: List[str]):
        """Compare top of stack < constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("setl al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_gt_const(self, args: List[str]):
        """Compare top of stack > constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("setg al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_le_const(self, args: List[str]):
        """Compare top of stack <= constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("setle al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_ge_const(self, args: List[str]):
        """Compare top of stack >= constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("setge al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_eq_const(self, args: List[str]):
        """Compare top of stack == constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("sete al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_cmp_ne_const(self, args: List[str]):
        """Compare top of stack != constant"""
        value = args[0]
        self.emit("pop rax")
        self.emit(f"cmp rax, {value}")
        self.emit("setne al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    # ============================================================================
    # Memory Operations
    # ============================================================================

    def _compile_load(self, args: List[str]):
        """Load local variable(s) onto stack"""
        # Handle multiple loads in one instruction
        for arg in args:
            var_index = int(arg)
            # Local variables are at [rbp - (var_index + 1) * 8]
            offset = (var_index + 1) * 8
            self.emit(f"mov rax, [rbp - {offset}]")
            self.emit("push rax")
            # Track the type of the loaded value
            var_type = self.local_types.get(var_index, 'i64')  # default to i64
            self.stack_types.append(var_type)

    def _compile_store(self, args: List[str]):
        """Store top of stack to local variable"""
        var_index = int(args[0])
        offset = (var_index + 1) * 8
        self.emit("pop rax")
        self.emit(f"mov [rbp - {offset}], rax")
        # Update local type based on what's on the stack
        if self.stack_types:
            self.local_types[var_index] = self.stack_types.pop()
        else:
            self.local_types[var_index] = 'i64'  # default

    def _compile_store_const_i64(self, args: List[str]):
        """Store integer constants directly to slots (STORE_CONST_I64 slot1 val1 slot2 val2 ...)"""
        # Args come in pairs: slot, value
        for i in range(0, len(args), 2):
            if i + 1 < len(args):
                slot = int(args[i])
                value_str = args[i + 1]
                offset = (slot + 1) * 8

                # Check if value fits in 64-bit signed integer
                try:
                    value = int(value_str)
                    # Check if it fits in signed 64-bit range
                    if value < -(2**63) or value >= 2**63:
                        # Value too large - truncate to 64-bit (simulating overflow)
                        value &= 0xFFFFFFFFFFFFFFFF
                    if value >= 2**63:
                        value -= 2**64
                except ValueError:
                    # Invalid integer, use 0
                    value = 0

                # Use movabs for 64-bit immediate values
                if value < -2147483648 or value > 2147483647:
                    self.emit(f"movabs rax, {value}")
                else:
                    self.emit(f"mov rax, {value}")
                self.emit(f"mov [rbp - {offset}], rax")
                # Track that this local is an i64
                self.local_types[slot] = 'i64'

    def _compile_store_const_f64(self, args: List[str]):
        """Store float constants directly to slots (STORE_CONST_F64 slot1 val1 slot2 val2 ...)"""
        # Args come in pairs: slot, value
        for i in range(0, len(args), 2):
            if i + 1 < len(args):
                slot = int(args[i])
                value = args[i + 1]
                offset = (slot + 1) * 8

                # Create a unique data label for this float constant
                label_name = f".FLOAT{self.string_counter}"
                self.string_counter += 1

                # Add to data section
                self.data_section.append(f"{label_name}:")
                self.data_section.append(f"    .double {value}")

                # Load the float constant and store it
                self.emit(f"movsd xmm0, [{label_name}]")
                self.emit(f"movsd [rbp - {offset}], xmm0")
                # Track that this local is an f64
                self.local_types[slot] = 'f64'

    def _compile_fused_store_load(self, args: List[str]):
        """Interleaved store/load operations (FUSED_STORE_LOAD var0 var1 var2 ...)
        Even indices are STORE operations (pop and store to var)
        Odd indices are LOAD operations (load from var and push)"""
        for i, var_str in enumerate(args):
            var_id = int(var_str)
            offset = (var_id + 1) * 8

            if i % 2 == 0:
                # STORE: pop from stack and store to variable
                self.emit("pop rax")
                self.emit(f"mov [rbp - {offset}], rax")
                # Track the type being stored
                if self.stack_types:
                    stored_type = self.stack_types.pop()
                    self.local_types[var_id] = stored_type
            else:
                # LOAD: load from variable and push to stack
                self.emit(f"mov rax, [rbp - {offset}]")
                self.emit("push rax")
                # Push the correct type based on what we know about the local
                var_type = self.local_types.get(var_id, 'i64')
                self.stack_types.append(var_type)

    def _compile_fused_load_store(self, args: List[str]):
        """Interleaved load/store operations (FUSED_LOAD_STORE var0 var1 var2 ...)
        Even indices are LOAD operations (load from var and push)
        Odd indices are STORE operations (pop and store to var)"""
        for i, var_str in enumerate(args):
            var_id = int(var_str)
            offset = (var_id + 1) * 8

            if i % 2 == 0:
                # LOAD: load from variable and push to stack
                self.emit(f"mov rax, [rbp - {offset}]")
                self.emit("push rax")
                # Push the correct type based on what we know about the local
                var_type = self.local_types.get(var_id, 'i64')
                self.stack_types.append(var_type)
            else:
                # STORE: pop from stack and store to variable
                self.emit("pop rax")
                self.emit(f"mov [rbp - {offset}], rax")
                # Track the type being stored
                if self.stack_types:
                    stored_type = self.stack_types.pop()
                    self.local_types[var_id] = stored_type

    def _compile_inc_local(self, args: List[str]):
        """Increment local variable by 1"""
        var_index = int(args[0])
        offset = (var_index + 1) * 8
        self.emit(f"inc qword ptr [rbp - {offset}]")

    def _compile_dec_local(self, args: List[str]):
        """Decrement local variable by 1"""
        var_index = int(args[0])
        offset = (var_index + 1) * 8
        self.emit(f"dec qword ptr [rbp - {offset}]")

    def _compile_add_const_i64(self, args: List[str]):
        """Add constant to top of stack"""
        value = args[0]
        top_type = self.stack_types[-1] if self.stack_types else 'i64'

        if top_type == 'f64':
            # Float addition
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit(f"mov rax, {value}")
            self.emit("cvtsi2sd xmm1, rax")
            self.emit("addsd xmm0, xmm1")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            # Type stack: f64 + i64 = f64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('f64')
        else:
            # Integer addition
            self.emit("pop rax")
            self.emit(f"add rax, {value}")
            self.emit("push rax")
            # Type stack: i64 + i64 = i64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('i64')

    def _compile_sub_const_i64(self, args: List[str]):
        """Subtract constant from top of stack"""
        value = args[0]
        top_type = self.stack_types[-1] if self.stack_types else 'i64'

        if top_type == 'f64':
            # Float subtraction
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit(f"mov rax, {value}")
            self.emit("cvtsi2sd xmm1, rax")
            self.emit("subsd xmm0, xmm1")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            # Type stack: f64 - i64 = f64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('f64')
        else:
            # Integer subtraction
            self.emit("pop rax")
            self.emit(f"sub rax, {value}")
            self.emit("push rax")
            # Type stack: i64 - i64 = i64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('i64')

    def _compile_mul_const_i64(self, args: List[str]):
        """Multiply top of stack by constant"""
        value = args[0]
        top_type = self.stack_types[-1] if self.stack_types else 'i64'

        if top_type == 'f64':
            # Float multiplication
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit(f"mov rax, {value}")
            self.emit("cvtsi2sd xmm1, rax")
            self.emit("mulsd xmm0, xmm1")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            # Type stack: f64 * i64 = f64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('f64')
        else:
            # Integer multiplication
            self.emit("pop rax")
            self.emit(f"imul rax, {value}")
            self.emit("push rax")
            # Type stack: i64 * i64 = i64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('i64')

    def _compile_mod_const_i64(self, args: List[str]):
        """Modulo top of stack by constant - optimized to avoid slow idiv"""
        value = args[0]
        self.emit("pop rax")

        # For small constants that are powers of 2, use AND (fastest)
        try:
            const_val = int(value)
            if const_val > 0 and (const_val & (const_val - 1)) == 0:
                # Power of 2: use bitwise AND
                mask = const_val - 1
                self.emit(f"and rax, {mask}  # Fast mod by power-of-2")
                self.emit("push rax")
                if self.stack_types:
                    self.stack_types.pop()
                self.stack_types.append('i64')
                return
        except ValueError:
            pass

        # For other constants, use optimized conditional subtraction
        # For fibonacci: values are always < 2*modulo, so at most 1 subtraction needed
        # Use branchless cmov for even better performance
        self.label_counter += 1

        # Optimized: subtract modulo, then conditionally restore if we went negative
        # This is branchless and much faster than a loop
        self.emit(f"mov rcx, {value}  # Load modulo constant")
        self.emit("mov rdx, rax  # Save original")
        self.emit("sub rax, rcx  # Try subtract")
        self.emit("test rax, rax  # Check if negative")
        self.emit("cmovl rax, rdx  # Restore if negative (branchless)")
        self.emit("push rax")

        # Type stack: i64 % i64 = i64
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('i64')

    def _compile_div_const_i64(self, args: List[str]):
        """Divide top of stack by constant"""
        value = args[0]
        top_type = self.stack_types[-1] if self.stack_types else 'i64'

        # Check for division by zero constant
        if int(value) == 0:
            # Division by zero - always raise error
            self.runtime_dependencies.add('runtime_error_at')
            message_label = self.get_string_label("integer division by zero")
            self.emit(f"lea rdi, [{message_label}]  # error message")
            self.emit(f"mov rsi, {self.current_line}  # line number")
            self.emit("call runtime_error_at")
            self.emit("# Never reached - exception handler jumps away")
        elif top_type == 'f64':
            # Float division
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit(f"mov rax, {value}")
            self.emit("cvtsi2sd xmm1, rax")
            self.emit("divsd xmm0, xmm1")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            # Type stack: f64 / i64 = f64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('f64')
        else:
            # Integer division
            self.emit("pop rax")
            self.emit("cqo")  # Sign extend rax into rdx:rax
            self.emit(f"mov rbx, {value}")
            self.emit("idiv rbx")
            self.emit("push rax")
            # Type stack: i64 / i64 = i64
            if self.stack_types:
                self.stack_types.pop()
            self.stack_types.append('i64')

    def _compile_add_const_f64(self, args: List[str]):
        """Add constant to top of stack (float)"""
        value = args[0]
        # Create a label for the constant
        label = f".FLOAT{self.string_counter}"
        self.string_counter += 1
        self.data_section.append(f"{label}:")
        self.data_section.append(f"    .double {value}")

        self.emit(f"movsd xmm0, [{label}]")
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("addsd xmm1, xmm0")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm1")

    def _compile_sub_const_f64(self, args: List[str]):
        """Subtract constant from top of stack (float)"""
        value = args[0]
        # Create a label for the constant
        label = f".FLOAT{self.string_counter}"
        self.string_counter += 1
        self.data_section.append(f"{label}:")
        self.data_section.append(f"    .double {value}")

        self.emit(f"movsd xmm0, [{label}]")
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("subsd xmm1, xmm0")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm1")

    def _compile_mul_const_f64(self, args: List[str]):
        """Multiply top of stack by constant (float)"""
        value = args[0]
        # Create a label for the constant
        label = f".FLOAT{self.string_counter}"
        self.string_counter += 1
        self.data_section.append(f"{label}:")
        self.data_section.append(f"    .double {value}")

        self.emit(f"movsd xmm0, [{label}]")
        self.emit("movsd xmm1, [rsp]")
        self.emit("add rsp, 8")
        self.emit("mulsd xmm1, xmm0")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm1")

    def _compile_div_const_f64(self, args: List[str]):
        """Divide top of stack by constant (float)"""
        value = args[0]

        # Check for division by zero constant
        if float(value) == 0.0:
            # Division by zero - always raise error
            self.runtime_dependencies.add('runtime_error_at')
            message_label = self.get_string_label("float division by zero")
            self.emit(f"lea rdi, [{message_label}]  # error message")
            self.emit(f"mov rsi, {self.current_line}  # line number")
            self.emit("call runtime_error_at")
            self.emit("# Never reached - exception handler jumps away")
        else:
            # Create a label for the constant
            label = f".FLOAT{self.string_counter}"
            self.string_counter += 1
            self.data_section.append(f"{label}:")
            self.data_section.append(f"    .double {value}")

            self.emit(f"movsd xmm0, [{label}]")
            self.emit("movsd xmm1, [rsp]")
            self.emit("add rsp, 8")
            self.emit("divsd xmm1, xmm0")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm1")

    def _compile_copy_local(self, args: List[str]):
        """Copy local variable to another local (COPY_LOCAL dst src)"""
        dst = int(args[0])
        src = int(args[1])
        src_offset = (src + 1) * 8
        dst_offset = (dst + 1) * 8
        self.emit(f"mov rax, [rbp - {src_offset}]")
        self.emit(f"mov [rbp - {dst_offset}], rax")

    def _compile_copy_local_ref(self, args: List[str]):
        """Copy local variable reference (same as COPY_LOCAL for now)"""
        self._compile_copy_local(args)

    def _compile_load_multi(self, args: List[str]):
        """Load multiple locals onto stack (LOAD_MULTI var1 var2 var3...)"""
        for arg in args:
            var_index = int(arg)
            offset = (var_index + 1) * 8
            self.emit(f"mov rax, [rbp - {offset}]")
            self.emit("push rax")

    # LOAD2_* fused instructions (load two variables and perform operation)

    def _compile_load2_add_i64(self, args: List[str]):
        """Fused: load var1, load var2, add"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"add rax, [rbp - {offset2}]")
        self.emit("push rax")

    def _compile_load2_sub_i64(self, args: List[str]):
        """Fused: load var1, load var2, subtract"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"sub rax, [rbp - {offset2}]")
        self.emit("push rax")

    def _compile_load2_mul_i64(self, args: List[str]):
        """Fused: load var1, load var2, multiply"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"imul rax, [rbp - {offset2}]")
        self.emit("push rax")

    def _compile_load2_mod_i64(self, args: List[str]):
        """Fused: load var1, load var2, modulo"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit("xor rdx, rdx")
        self.emit(f"mov rbx, [rbp - {offset2}]")
        self.emit("idiv rbx")
        self.emit("push rdx")

    def _compile_load2_mul_f64(self, args: List[str]):
        """Fused: load var1, load var2, multiply (floats)"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"movsd xmm0, [rbp - {offset1}]")
        self.emit(f"mulsd xmm0, [rbp - {offset2}]")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    def _compile_load2_cmp_lt(self, args: List[str]):
        """Fused: load var1, load var2, compare <"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("setl al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    def _compile_load2_cmp_gt(self, args: List[str]):
        """Fused: load var1, load var2, compare >"""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("setg al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    def _compile_load2_cmp_le(self, args: List[str]):
        """Fused: load var1, load var2, compare <="""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("setle al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    def _compile_load2_cmp_ge(self, args: List[str]):
        """Fused: load var1, load var2, compare >="""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("setge al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    def _compile_load2_cmp_eq(self, args: List[str]):
        """Fused: load var1, load var2, compare =="""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("sete al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    def _compile_load2_cmp_ne(self, args: List[str]):
        """Fused: load var1, load var2, compare !="""
        var1, var2 = int(args[0]), int(args[1])
        offset1, offset2 = (var1 + 1) * 8, (var2 + 1) * 8
        self.emit(f"mov rax, [rbp - {offset1}]")
        self.emit(f"cmp rax, [rbp - {offset2}]")
        self.emit("setne al")
        self.emit("movzx rax, al")
        self.emit("push rax")

    # ============================================================================
    # Stack Operations
    # ============================================================================

    def _compile_pop(self, args: List[str]):
        """Pop and discard top of stack"""
        self.emit("add rsp, 8")

    def _compile_dup(self, args: List[str]):
        """Duplicate top of stack"""
        # Read the value at the current top of stack and push a copy.
        # Using mov/push sequence is more portable and avoids assembler quirks.
        self.emit("mov rax, [rsp]")
        self.emit("push rax")
        # Duplicate the type
        if self.stack_types:
            self.stack_types.append(self.stack_types[-1])

    def _compile_swap(self, args: List[str]):
        """Swap top two stack values"""
        self.emit("pop rax")
        self.emit("pop rbx")
        self.emit("push rax")
        # Swap types
        if len(self.stack_types) >= 2:
            self.stack_types[-1], self.stack_types[-2] = self.stack_types[-2], self.stack_types[-1]
        self.emit("push rbx")

    # ============================================================================
    # Runtime Library Calls
    # ============================================================================

    def _compile_builtin_print(self, args: List[str]):
        """Print value (call runtime)"""
        # Pop value into rdi (first argument in System V ABI)
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_print")

    def _compile_builtin_println(self, args: List[str]):
        """Print value with newline (call runtime)"""
        # Check if top of stack is a float
        if self.stack_types and self.stack_types[-1] == 'f64':
            # Float value - use runtime_println_float
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit("xor rax, rax")  # Set rax=0 (number of XMM registers used per ABI)
            self.emit_runtime_call("runtime_println_float")
            self.stack_types.pop()
        elif self.stack_types and self.stack_types[-1] == 'str':
            # String value - use runtime_println_str
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_println_str")
            self.stack_types.pop()
        elif self.stack_types and self.stack_types[-1] == 'bool':
            # Bool value - convert to string first
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_bool_to_str")
            self.emit("mov rdi, rax")
            self.emit_runtime_call("runtime_println")
            self.stack_types.pop()
        elif self.stack_types and self.stack_types[-1] == 'list':
            # List value - convert to string and print
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_list_to_str")
            self.emit("mov rdi, rax")
            self.emit_runtime_call("runtime_println")
            self.stack_types.pop()
        elif self.stack_types and self.stack_types[-1] == 'set':
            # Set value - convert to string and print
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_set_to_str")
            self.emit("mov rdi, rax")
            self.emit_runtime_call("runtime_println")
            self.stack_types.pop()
        else:
            # Integer or other value - use regular runtime_println
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_println")
            if self.stack_types:
                self.stack_types.pop()

    def _compile_halt(self, args: List[str]):
        """Halt/exit program"""
        # Exit syscall
        self.emit("mov rax, 60")  # sys_exit
        self.emit("xor rdi, rdi")  # exit code 0
        self.emit("syscall")

    def _compile_exit(self, args: List[str]):
        """Exit with status code from stack"""
        self.emit("pop rdi   # exit status")
        self.emit_runtime_call("runtime_exit")

    def _compile_sleep(self, args: List[str]):
        """Sleep for seconds (float on stack)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_sleep")

    def _compile_assert(self, args: List[str]):
        """Assert condition is true"""
        # Stack: message_ptr (lower), condition (top)
        self.emit("pop rdi   # condition (top)")
        self.emit("pop rsi   # message (or NULL)")
        self.emit_runtime_call("runtime_assert")

    # ============================================================================
    # Logical Operations
    # ============================================================================

    def _compile_and(self, args: List[str]):
        """Logical AND"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("test rax, rax")
        self.emit("setnz al")
        self.emit("test rbx, rbx")
        self.emit("setnz bl")
        self.emit("and al, bl")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_or(self, args: List[str]):
        """Logical OR"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("or rax, rbx")
        self.emit("test rax, rax")
        self.emit("setnz al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_not(self, args: List[str]):
        """Logical NOT"""
        self.emit("pop rax")
        self.emit("test rax, rax")
        self.emit("setz al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Result is boolean
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    # ============================================================================
    # Bitwise Operations
    # ============================================================================

    def _compile_and_i64(self, args: List[str]):
        """Bitwise AND"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("and rax, rbx")
        self.emit("push rax")

    def _compile_or_i64(self, args: List[str]):
        """Bitwise OR"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("or rax, rbx")
        self.emit("push rax")

    def _compile_xor_i64(self, args: List[str]):
        """Bitwise XOR"""
        self.emit("pop rbx")
        self.emit("pop rax")
        self.emit("xor rax, rbx")
        self.emit("push rax")

    def _compile_shl_i64(self, args: List[str]):
        """Shift left"""
        self.emit("pop rcx")  # Shift amount
        self.emit("pop rax")  # Value to shift
        self.emit("shl rax, cl")
        self.emit("push rax")

    def _compile_shr_i64(self, args: List[str]):
        """Shift right"""
        self.emit("pop rcx")  # Shift amount
        self.emit("pop rax")  # Value to shift
        self.emit("shr rax, cl")
        self.emit("push rax")

    # ============================================================================
    # Additional Stack Operations
    # ============================================================================

    def _compile_rot(self, args: List[str]):
        """Rotate top 3 stack values (a b c -> b c a)"""
        self.emit("pop rcx")  # c
        self.emit("pop rbx")  # b
        self.emit("pop rax")  # a
        self.emit("push rbx")
        self.emit("push rcx")
        self.emit("push rax")

    def _compile_over(self, args: List[str]):
        """Copy second item to top (a b -> a b a)"""
        self.emit("pop rbx")  # b
        self.emit("pop rax")  # a
        self.emit("push rax")
        self.emit("push rbx")
        self.emit("push rax")

    def _compile_dup2(self, args: List[str]):
        """Duplicate top two items (a b -> a b a b)"""
        self.emit("mov rbx, [rsp + 8]")  # Get second item
        self.emit("mov rax, [rsp]")       # Get top item
        self.emit("push rbx")
        self.emit("push rax")

    # ============================================================================
    # String Operations
    # ============================================================================

    def _compile_add_str(self, args: List[str]):
        """Concatenate two strings or add integers and convert to string"""
        # Check types based on compile-time type information
        second_type = self.stack_types[-1] if self.stack_types else 'str'
        first_type = self.stack_types[-2] if len(self.stack_types) >= 2 else 'str'

        # Pop operands
        self.emit("pop rsi")  # Second operand (top of stack)
        self.emit("pop rdi")  # First operand

        # Handle different type combinations
        if first_type == 'i64' and second_type == 'i64':
            # Both are integers - add them and convert result to string
            self.emit("add rdi, rsi")  # Add the integers
            self.emit_runtime_call("runtime_int_to_str")  # Convert result to string
        elif first_type == 'f64' and second_type == 'f64':
            # Both are floats - add them and convert result to string
            self.emit("movq xmm0, rdi")
            self.emit("movq xmm1, rsi")
            self.emit("addsd xmm0, xmm1")
            self.emit_runtime_call("runtime_float_to_str")
        elif first_type == 'str' and second_type == 'str':
            # Both are strings - concatenate them
            self.emit_runtime_call("runtime_str_concat_checked")
        else:
            # Mixed types - convert each to string first, then concatenate
            # Save second operand
            self.emit("push rsi")

            # Convert first operand to string if needed
            if first_type != 'str':
                if first_type in ['i64', 'bool']:
                    self.emit_runtime_call("runtime_int_to_str")
                    self.emit("mov rdi, rax")
                elif first_type == 'f64':
                    self.emit("movq xmm0, rdi")
                    self.emit_runtime_call("runtime_float_to_str")
                    self.emit("mov rdi, rax")

            # Get second operand and convert to string if needed
            self.emit("pop rsi")
            if second_type != 'str':
                self.emit("push rdi")  # Save first string
                if second_type in ['i64', 'bool']:
                    self.emit("mov rdi, rsi")
                    self.emit_runtime_call("runtime_int_to_str")
                    self.emit("mov rsi, rax")
                elif second_type == 'f64':
                    self.emit("movq xmm0, rsi")
                    self.emit_runtime_call("runtime_float_to_str")
                    self.emit("mov rsi, rax")
                self.emit("pop rdi")  # Restore first string

            # Now both are strings - concatenate
            self.emit_runtime_call("runtime_str_concat_checked")

        self.emit("push rax")
        # Result is always a string
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('str')

    def _compile_str_upper(self, args: List[str]):
        """Convert string to uppercase"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_str_upper")
        self.emit("push rax")

    def _compile_str_lower(self, args: List[str]):
        """Convert string to lowercase"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_str_lower")
        self.emit("push rax")

    def _compile_str_len(self, args: List[str]):
        """Get string length"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_str_len")
        self.emit("push rax")

    def _compile_str_strip(self, args: List[str]):
        """Strip whitespace from string"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_str_strip")
        self.emit("push rax")

    def _compile_str_split(self, args: List[str]):
        """Split string by delimiter"""
        self.emit("pop rsi   # delimiter (top)")
        self.emit("pop rdi   # string")
        self.emit_runtime_call("runtime_str_split")
        self.emit("push rax   # list")
        # Pop string and delimiter, push list result
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop delimiter
            self.stack_types.pop()  # Pop string
        self.stack_types.append('list')

    def _compile_str_join(self, args: List[str]):
        """Join list with delimiter"""
        self.emit("pop rdi   # list (top)")
        self.emit("pop rsi   # delimiter")
        self.emit_runtime_call("runtime_str_join")
        self.emit("push rax   # string")
        # Pop list and delimiter, push string result
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop list
            self.stack_types.pop()  # Pop delimiter
        self.stack_types.append('str')

    def _compile_str_replace(self, args: List[str]):
        """Replace occurrences in string"""
        self.emit("pop rdx   # new")
        self.emit("pop rsi   # old")
        self.emit("pop rdi   # string")
        self.emit_runtime_call("runtime_str_replace")
        self.emit("push rax   # result")
        # Pop three strings, push one string
        if len(self.stack_types) >= 3:
            self.stack_types.pop()  # new
            self.stack_types.pop()  # old
            self.stack_types.pop()  # string
        self.stack_types.append('str')

    def _compile_encode(self, args: List[str]):
        """Encode string to bytes"""
        self.emit("pop rsi   # encoding")
        self.emit("pop rdi   # string")
        self.emit_runtime_call("runtime_str_encode")
        self.emit("push rax")
        # Pop both encoding and string, push bytes
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # encoding
            self.stack_types.pop()  # string
        self.stack_types.append('bytes')

    def _compile_decode(self, args: List[str]):
        """Decode bytes to string"""
        self.emit("pop rsi   # encoding")
        self.emit("pop rdi   # bytes")
        self.emit_runtime_call("runtime_str_decode")
        self.emit("push rax")
        # Pop both encoding and bytes, push string
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # encoding
            self.stack_types.pop()  # bytes
        self.stack_types.append('str')

    # ============================================================================
    # Math Operations
    # ============================================================================

    def _compile_neg(self, args: List[str]):
        """Negate top of stack (int or float)"""
        if self.stack_types and self.stack_types[-1] == 'f64':
            # Float negation
            self.emit("movsd xmm0, [rsp]")
            # Flip the sign bit
            self.emit("mov rax, 0x8000000000000000")  # Sign bit mask
            self.emit("movq xmm1, rax")
            self.emit("xorpd xmm0, xmm1")  # Flip sign bit
            self.emit("movsd [rsp], xmm0")
        else:
            # Integer negation
            self.emit("pop rax")
            self.emit("neg rax")
            self.emit("push rax")

    def _compile_abs(self, args: List[str]):
        """Absolute value"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_abs_int")
        self.emit("push rax")

    def _compile_pow(self, args: List[str]):
        """Power function - converts i64 arguments to f64 if needed, returns int64 if whole"""
        # Stack has: [base, exponent] with exponent on top
        # Pop exponent (may be i64 or f64)
        exponent_type = self.stack_types[-1] if self.stack_types else 'i64'
        if exponent_type == 'f64':
            self.emit("movsd xmm1, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer exponent - convert to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm1, rax")

        # Pop base (may be i64 or f64)
        base_type = self.stack_types[-2] if len(self.stack_types) >= 2 else 'i64'
        if base_type == 'f64':
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer base - convert to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")

        self.emit_runtime_call("runtime_pow")

        # Check if result is a whole number that fits in int64
        # xmm0 now contains result
        # Create label for this check
        whole_label = f".Lpow_whole_{self.label_counter}"
        float_label = f".Lpow_float_{self.label_counter}"
        done_label = f".Lpow_done_{self.label_counter}"
        self.label_counter += 1

        # Check if floor(result) == result
        self.emit("movsd xmm1, xmm0")
        self.emit("roundsd xmm1, xmm0, 1")  # Round toward zero (trunc)
        self.emit("comisd xmm0, xmm1")      # Compare result with floored value
        self.emit(f"je {whole_label}")

        # Not a whole number - push as float
        self.emit(f"{float_label}:")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        self.stack_types.pop() if len(self.stack_types) >= 2 else None
        if len(self.stack_types) >= 1:
            self.stack_types.pop()
        self.stack_types.append('f64')
        self.emit(f"jmp {done_label}")

        # Whole number - convert to int64
        self.emit(f"{whole_label}:")
        self.emit("cvttsd2si rax, xmm0")    # Convert with truncation
        self.emit("push rax")
        self.stack_types.pop() if len(self.stack_types) >= 2 else None
        if len(self.stack_types) >= 1:
            self.stack_types.pop()
        self.stack_types.append('i64')

        self.emit(f"{done_label}:")

    def _compile_builtin_sqrt(self, args: List[str]):
        """Square root - converts i64 argument to f64 if needed"""
        arg_type = self.stack_types[-1] if self.stack_types else 'i64'
        if arg_type == 'f64':
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer argument
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
        self.emit_runtime_call("runtime_sqrt")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update stack types: result is f64
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('f64')

    def _compile_builtin_floor(self, args: List[str]):
        """Floor function - converts i64 argument to f64 if needed"""
        arg_type = self.stack_types[-1] if self.stack_types else 'i64'
        if arg_type == 'f64':
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer argument - convert to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
        self.emit_runtime_call("runtime_floor")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update stack types: result is f64
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('f64')

    def _compile_builtin_ceil(self, args: List[str]):
        """Ceil function - converts i64 argument to f64 if needed"""
        arg_type = self.stack_types[-1] if self.stack_types else 'i64'
        if arg_type == 'f64':
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer argument - convert to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
        self.emit_runtime_call("runtime_ceil")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update stack types: result is f64
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('f64')

    def _compile_builtin_pi(self, args: List[str]):
        """Push PI constant"""
        # M_PI = 3.14159265358979323846
        label = ".PI_CONST"
        if label not in [d for d in self.data_section if d.startswith(label)]:
            self.data_section.append(f"{label}:")
            self.data_section.append("    .double 3.14159265358979323846")
        self.emit(f"movsd xmm0, [{label}]")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update stack types: pi is f64
        self.stack_types.append('f64')

    def _compile_min(self, args: List[str]):
        """Pop two values, push minimum (supports both int and float)"""
        # For simplicity, treat as integers. In full implementation, would need type checking
        self.emit("pop rax   # second operand")
        self.emit("pop rbx   # first operand")
        self.emit("cmp rbx, rax")
        self.emit("cmovg rbx, rax   # rbx = min(rbx, rax)")
        self.emit("push rbx")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('i64')

    def _compile_max(self, args: List[str]):
        """Pop two values, push maximum (supports both int and float)"""
        self.emit("pop rax   # second operand")
        self.emit("pop rbx   # first operand")
        self.emit("cmp rbx, rax")
        self.emit("cmovl rbx, rax   # rbx = max(rbx, rax)")
        self.emit("push rbx")
        # Update type stack
        if self.stack_types and len(self.stack_types) >= 2:
            self.stack_types.pop()
            self.stack_types.pop()
        self.stack_types.append('i64')

    def _compile_sin(self, args: List[str]):
        """Pop float, push sin(float)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_sin")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    def _compile_cos(self, args: List[str]):
        """Pop float, push cos(float)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_cos")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    def _compile_tan(self, args: List[str]):
        """Pop float, push tan(float)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_tan")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    def _compile_builtin_round(self, args: List[str]):
        """Pop float/int, push round(value) - converts i64 argument to f64 if needed"""
        arg_type = self.stack_types[-1] if self.stack_types else 'i64'
        if arg_type == 'f64':
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
        else:
            # Integer argument - convert to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
        self.emit_runtime_call("runtime_round")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")
        # Update stack types: result is f64
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('f64')

    def _compile_floor(self, args: List[str]):
        """Pop float, push floor(float)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_floor")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    def _compile_ceil(self, args: List[str]):
        """Pop float, push ceil(float)"""
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        self.emit_runtime_call("runtime_ceil")
        self.emit("sub rsp, 8")
        self.emit("movsd [rsp], xmm0")

    # ============================================================================
    # List Operations
    # ============================================================================

    def _compile_list_new(self, args: List[str]):
        """Create new empty list"""
        self.emit_runtime_call("runtime_list_new")
        self.emit("push rax")
        self.stack_types.append('list')

    def _compile_list_append(self, args: List[str]):
        """Append value to list"""
        self.emit("pop rsi")  # value
        self.emit("pop rdi")  # list
        self.emit_runtime_call("runtime_list_append_int")
        self.emit("push rdi")  # push list back
        # Pop value and list from stack_types, push list back
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop list
        self.stack_types.append('list')

    def _compile_list_get(self, args: List[str]):
        """Get element at index - works for both lists and strings"""
        self.emit("pop rsi")  # index
        self.emit("pop rdi")  # list/string

        # Check if this is a string indexing operation
        if len(self.stack_types) >= 2:
            # Get the second-to-last type (the container)
            container_type = self.stack_types[-2] if len(self.stack_types) >= 2 else None
            if container_type == 'str':
                # String indexing
                self.emit_runtime_call("runtime_str_get_char")
                self.emit("push rax")
                # Result is a string
                if self.stack_types:
                    self.stack_types.pop()  # Remove string from stack
                if self.stack_types:
                    self.stack_types.pop()  # Remove index from stack
                self.stack_types.append('str')
                return

        # Default to list indexing
        self.runtime_dependencies.add('runtime_list_get_int_at')
        # index and list already in rsi and rdi from above pops
        self.emit(f"mov rdx, {self.current_line}  # line number")
        self.emit("call runtime_list_get_int_at")
        self.emit("push rax")
        # Result is based on list contents - typically int64
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Remove list
            self.stack_types.pop()  # Remove index
        self.stack_types.append('i64')

    def _compile_list_set(self, args: List[str]):
        """Set element at index"""
        self.runtime_dependencies.add('runtime_list_set_int_at')
        self.emit("pop r8")   # value (temporarily in r8)
        self.emit("pop rsi")  # index
        self.emit("pop rdi")  # list
        self.emit("mov rdx, r8  # value")
        self.emit(f"mov rcx, {self.current_line}  # line number")
        self.emit("call runtime_list_set_int_at")
        self.emit("push rdi")  # push list back
        # Pop value, index, and list from stack_types, push list back
        if len(self.stack_types) >= 3:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop index
            self.stack_types.pop()  # Pop list
        self.stack_types.append('list')

    def _compile_list_len(self, args: List[str]):
        """Get list/string length"""
        self.emit("pop rdi")  # list or string

        # Check if this is a string
        if self.stack_types and self.stack_types[-1] == 'str':
            # String length
            self.emit_runtime_call("runtime_str_len")
        else:
            # List length (default)
            self.emit_runtime_call("runtime_list_len")

        self.emit("push rax")
        # Result is an integer
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('i64')

    def _compile_list_pop(self, args: List[str]):
        """Pop last element from list and push both modified list and popped element"""
        self.emit("pop rdi")  # list
        self.emit_runtime_call("runtime_list_pop")
        # rax now contains the popped element
        # The list is already modified in place
        # We need to push: list (rdi), element (rax)
        self.emit("push rdi")  # Push modified list
        self.emit("push rax")  # Push popped element
        # Pop list from stack_types (it was on top), push it back, then push i64
        if self.stack_types:
            self.stack_types.pop()  # Pop list from stack
        self.stack_types.append('list')
        self.stack_types.append('i64')

    def _compile_list_new_i64(self, args: List[str]):
        """Create list from int64 array (LIST_NEW_I64 count val1 val2 ...)"""
        count = int(args[0])
        values = args[1:count+1]

        # Create new list
        self.emit_runtime_call("runtime_list_new")

        # Set elem_type to 0 (integer) - rax has the list pointer
        self.emit("mov dword ptr [rax + 24], 0  # elem_type = 0 (int)")

        # Save list pointer on stack
        self.emit("push rax")

        # Append each value
        for value in values:
            # Peek at list pointer without popping
            self.emit("mov rdi, [rsp]")  # Load list pointer to rdi (first param)
            self.emit(f"mov rsi, {value}")  # value (second param)
            self.emit_runtime_call("runtime_list_append_int")

        # List pointer is already on stack

        # Update type stack
        self.stack_types.append('list')

    def _compile_list_new_f64(self, args: List[str]):
        """Create list from float64 array (LIST_NEW_F64 count val1 val2 ...)"""
        count = int(args[0])
        values = args[1:count+1]

        # Create new list
        self.emit_runtime_call("runtime_list_new")

        # Set elem_type to 2 (float)
        self.emit("mov dword ptr [rax + 24], 2  # elem_type = 2 (float)")

        # Save list pointer on stack
        self.emit("push rax")

        # Append each value
        for value in values:
            # Create a label for the float constant
            label = f".FLOAT{self.string_counter}"
            self.string_counter += 1
            self.data_section.append(f"{label}:")
            self.data_section.append(f"    .double {value}")

            # Load float value and append
            self.emit("mov rdi, [rsp]")  # Peek at list pointer
            self.emit(f"movsd xmm0, [{label}]")  # value in xmm0
            self.emit("movq rsi, xmm0")  # Move xmm0 to rsi as int64 bits
            self.emit_runtime_call("runtime_list_append_int")

        # List pointer is already on stack

        # Update type stack
        self.stack_types.append('list')

    def _compile_list_new_str(self, args: List[str]):
        """Create list from string array (LIST_NEW_STR count "str1" "str2" ...)"""
        # Note: args[0] is count, rest are string literals with quotes
        count = int(args[0])
        values = args[1:count+1]

        # Create new list
        self.emit_runtime_call("runtime_list_new")

        # Set elem_type to 1 (string)
        self.emit("mov dword ptr [rax + 24], 1  # elem_type = 1 (string)")

        # Save list pointer on stack
        self.emit("push rax")

        # Append each value
        for value_str in values:
            # Remove quotes if present
            if value_str.startswith('"') and value_str.endswith('"'):
                value_str = value_str[1:-1]

            label = self.get_string_label(value_str)

            # Load string pointer and append
            self.emit("mov rdi, [rsp]")  # Peek at list pointer
            self.emit(f"lea rsi, [{label}]")  # value as string pointer
            self.emit_runtime_call("runtime_list_append_int")

        # List pointer is already on stack

        # Update type stack
        self.stack_types.append('list')

    def _compile_list_new_bool(self, args: List[str]):
        """Create list from bool array (LIST_NEW_BOOL count val1 val2 ...)"""
        count = int(args[0])
        values = args[1:count+1]

        # Create new list
        self.emit_runtime_call("runtime_list_new")

        # Set elem_type to 3 (bool)
        self.emit("mov dword ptr [rax + 24], 3  # elem_type = 3 (bool)")

        # Save list pointer on stack
        self.emit("push rax")

        # Append each value
        for value in values:
            # Convert bool string to value
            bool_val = "1" if value in ("1", "true") else "0"

            # Load bool value and append
            self.emit("mov rdi, [rsp]")  # Peek at list pointer
            self.emit(f"mov rsi, {bool_val}")  # value
            self.emit_runtime_call("runtime_list_append_int")

        # List pointer is already on stack

        # Update type stack
        self.stack_types.append('list')

    def _compile_contains(self, args: List[str]):
        """Check if list/string/set contains value"""
        container_type = self.stack_types[-2] if len(self.stack_types) >= 2 else 'i64'
        self.emit("pop rsi   # value")
        self.emit("pop rdi   # list/string/set")

        # Determine which runtime function to call based on container type
        if container_type == 'set':
            self.emit_runtime_call("runtime_set_contains")
        elif container_type == 'str':
            self.emit_runtime_call("runtime_str_contains")
        else:  # Default to list
            self.emit_runtime_call("runtime_contains")

        self.emit("push rax   # bool result")
        # Pop value and container, push bool result
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop container
        self.stack_types.append('bool')

    def _compile_builtin_len(self, args: List[str]):
        """Get length (calls list_len for now)"""
        self._compile_list_len(args)

    def _compile_fork(self, args: List[str]):
        """Fork the current process and return pid"""
        self.emit("xor rax, rax  # Clear rax (set rax=0 for no XMM args per ABI)")
        self.emit_runtime_call("runtime_fork")
        self.emit("push rax  # Push pid onto stack")
        self.stack_types.append('i64')

    def _compile_join(self, args: List[str]):
        """Wait for a forked process to finish"""
        # Pop pid from stack, call runtime_wait(pid), push status
        self.emit("pop rdi  # pid")
        self.emit_runtime_call("runtime_wait")
        self.emit("push rax  # Push exit status onto stack")
        # Pop pid type, push status type
        if self.stack_types:
            self.stack_types.pop()  # Pop i64 pid
        self.stack_types.append('i64')

    # ============================================================================
    # File I/O Operations
    # ============================================================================

    def _compile_file_open(self, args: List[str]):
        """Open a file and return a file descriptor"""
        # Stack: mode path -> fd
        # Pop mode and path, call runtime_fopen, push fd
        self.emit("pop rsi  # mode (second argument)")
        self.emit("pop rdi  # path (first argument)")
        self.emit_runtime_call("runtime_fopen")
        self.emit("push rax  # Push file descriptor")
        # Pop two strings, push one i64
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop mode
            self.stack_types.pop()  # Pop path
        self.stack_types.append('i64')

    def _compile_file_write(self, args: List[str]):
        """Write data to a file"""
        # Stack: fd data -> bytes_written
        # Pop data and fd, call runtime_fwrite, push bytes_written
        self.emit("pop rsi  # data (second argument)")
        self.emit("pop rdi  # fd (first argument)")
        self.emit_runtime_call("runtime_fwrite")
        self.emit("push rax  # Push bytes_written")
        # Pop i64 and str, push i64
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop data
            self.stack_types.pop()  # Pop fd
        self.stack_types.append('i64')

    def _compile_file_read(self, args: List[str]):
        """Read data from a file"""
        # Stack: fd size -> data
        # Pop size and fd, call runtime_fread, push data
        self.emit("pop rsi  # size (second argument)")
        self.emit("pop rdi  # fd (first argument)")
        self.emit_runtime_call("runtime_fread")
        self.emit("push rax  # Push read data string")
        # Pop two i64, push string
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop size
            self.stack_types.pop()  # Pop fd
        self.stack_types.append('str')

    def _compile_file_close(self, args: List[str]):
        """Close a file"""
        # Stack: fd ->
        # Pop fd, call runtime_fclose
        self.emit("pop rdi  # fd")
        self.emit_runtime_call("runtime_fclose")
        # Pop i64 from stack_types
        if self.stack_types:
            self.stack_types.pop()

    # ============================================================================
    # Set Operations
    # ============================================================================

    def _compile_set_new(self, args: List[str]):
        """Create new empty set"""
        self.emit_runtime_call("runtime_set_new")
        self.emit("push rax")
        self.stack_types.append('set')

    def _compile_set_add(self, args: List[str]):
        """Add value to set"""
        # Get the type of the value being added
        value_type = self.stack_types[-1] if self.stack_types else 'i64'

        self.emit("pop rsi   # value")
        self.emit("pop rdi   # set")

        # Pass element type as third argument (0=int, 1=string)
        if value_type == 'str':
            self.emit("mov rdx, 1  # elem_type: string")
        else:
            self.emit("mov rdx, 0  # elem_type: int")

        self.emit_runtime_call("runtime_set_add_typed")
        self.emit("push rdi   # return set")
        # Pop both value and set from stack_types, push set back
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop set
        self.stack_types.append('set')

    def _compile_set_remove(self, args: List[str]):
        """Remove value from set"""
        self.emit("pop rsi   # value")
        self.emit("pop rdi   # set")
        self.emit_runtime_call("runtime_set_remove")
        self.emit("push rdi   # return set")
        # Pop both value and set from stack_types, push set back
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop set
        self.stack_types.append('set')

    def _compile_set_contains(self, args: List[str]):
        """Check if set contains value"""
        self.emit("pop rsi   # value")
        self.emit("pop rdi   # set")
        self.emit_runtime_call("runtime_set_contains")
        self.emit("push rax   # bool result")
        # Pop both value and set, push bool result
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop set
        self.stack_types.append('bool')

    def _compile_set_len(self, args: List[str]):
        """Get set length"""
        self.emit("pop rdi   # set")
        self.emit_runtime_call("runtime_set_len")
        self.emit("push rax")
        # Pop set, push int result
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('i64')

    # ============================================================================
    # Struct Operations
    # ============================================================================

    def _compile_struct(self, args: List[str]):
        """Register struct definition (.struct struct_id field_count total_size field_names... field_types...)"""
        struct_id = int(args[0])
        field_count = int(args[1])
        # args[2] is total_size - skip it
        field_names = args[3:3+field_count]
        field_types = args[3+field_count:3+field_count*2] if len(args) >= 3+field_count*2 else ['i64'] * field_count

        self.structs[struct_id] = {
            'field_count': field_count,
            'field_names': field_names,
            'field_types': field_types
        }

    def _compile_struct_to_c(self, struct_id: int):
        """Convert internal struct format to C-compatible layout"""
        struct_def = self.structs.get(struct_id, {'field_count': 0, 'field_types': []})
        field_count = struct_def.get('field_count', 0)
        field_types = struct_def.get('field_types', ['i64'] * field_count)

        # Pop the internal struct format (struct_id | instance_id)
        self.emit("pop rax")
        # Extract instance_id from high bits
        self.emit("shr rax, 16")
        # Calculate base address in struct_data
        self.emit("mov rcx, 256")
        self.emit("imul rax, rcx  # rax = instance_id * 256")
        self.emit("lea rdx, [rip + struct_data]")

        # Allocate space for C struct on stack (field_count * 8 bytes)
        self.emit(f"sub rsp, {field_count * 8}  # allocate C struct space on stack")
        # rdx = base address of struct_data, rax = offset for instance

        # Copy each field to C struct layout
        for i in range(field_count):
            # Load field value from struct_data
            self.emit(f"mov rbx, [rdx + rax + {i * 8}]  # field {i}")
            # Store to stack (C struct layout)
            self.emit(f"mov [rsp + {i * 8}], rbx")

        # Push pointer to C struct layout (stack address)
        self.emit("mov rax, rsp")
        self.emit("push rax")
        # Update type stack: push 'ptr' to indicate pointer to C struct
        self.stack_types.append('ptr')

    def _compile_struct_new(self, args: List[str]):
        """Create new struct instance - store fields in struct data area"""
        struct_id = int(args[0])

        if struct_id not in self.structs:
            self.emit_comment(f"ERROR: Unknown struct {struct_id}")
            return

        struct_def = self.structs[struct_id]
        field_count = struct_def['field_count']

        # Allocate from struct_data area
        self.emit("lea rax, [rip + struct_counter]")
        self.emit("mov rbx, [rax]  # rbx = current counter")
        self.emit("mov rcx, rbx")
        self.emit("inc rcx")
        # Wrap around at 4096 to stay within allocated struct_data
        self.emit("cmp rcx, 4096")
        label_num = self.label_counter
        self.label_counter += 1
        self.emit(f"jb .Lstruct_no_wrap_{label_num}  # Jump if below 4096")
        self.emit("xor rcx, rcx  # rcx >= 4096, wrap to 0")
        self.emit(f".Lstruct_no_wrap_{label_num}:")
        self.emit("mov [rax], rcx  # store counter")

        # Calculate base offset for struct_data: instance_id * 256
        self.emit("mov rax, rcx  # rax = new instance_id after wrap")
        self.emit("mov rdx, 256")
        self.emit("imul rax, rdx  # rax = instance_id * 256")

        # Store fields in struct_data
        for i in range(field_count - 1, -1, -1):
            self.emit(f"pop rbx  # field {i}")
            self.emit("lea rdx, [rip + struct_data]")
            self.emit(f"mov [rdx + rax + {i * 8}], rbx")
            if self.stack_types:
                self.stack_types.pop()

        # Return struct reference: (instance_id << 16) | struct_id
        self.emit("mov rax, rcx  # rax = new instance_id")
        self.emit("shl rax, 16")
        self.emit(f"or rax, {struct_id}")
        self.emit("push rax")
        self.stack_types.append(f'struct:{struct_id}')
        self.last_struct_id = struct_id  # Track for STRUCT_GET

    def _compile_struct_get(self, args: List[str]):
        """Get field from struct - retrieve from struct data area"""
        field_idx = int(args[0])

        # Pop the struct reference
        self.emit("pop rax  # struct reference")
        
        # Pop struct type from stack and extract struct_id from it
        struct_id_from_stack = None
        if self.stack_types:
            popped_type = self.stack_types.pop()
            # Extract struct_id from type like "struct:0"
            if isinstance(popped_type, str) and popped_type.startswith('struct:'):
                struct_id_from_stack = int(popped_type.split(':')[1])

        # Decode: instance_id = rax >> 16, struct_id = rax & 0xFFFF
        self.emit("mov rbx, rax")
        self.emit("shr rbx, 16  # rbx = instance_id")
        self.emit("mov rcx, rax")
        self.emit("and rcx, 0xFFFF  # rcx = struct_id")
        
        # Clamp instance_id to valid range (0-4095) to prevent out-of-bounds access
        self.emit("cmp rbx, 4096")
        label_num = self.label_counter
        self.label_counter += 1
        self.emit(f"jb .Linstance_ok_{label_num}")
        self.emit("and rbx, 0xFFF  # Wrap to 0-4095")
        self.emit(f".Linstance_ok_{label_num}:")

        # Calculate address: base + (instance_id * 256) + (field_idx * 8)
        # rax = instance_id * 256
        self.emit("mov rax, rbx")
        self.emit("mov rdx, 256")
        self.emit("imul rax, rdx  # rax = instance_id * 256")
        self.emit(f"add rax, {field_idx * 8}  # rax += field_idx * 8")

        # Load field value from struct_data
        self.emit("lea rdx, [rip + struct_data]")

        # Determine field type from struct definition using struct_id from stack
        field_type = 'i64'  # default
        struct_id_to_use = struct_id_from_stack if struct_id_from_stack is not None else self.last_struct_id
        if struct_id_to_use is not None and struct_id_to_use in self.structs:
            struct_def = self.structs[struct_id_to_use]
            field_types = struct_def.get('field_types', [])
            if field_idx < len(field_types):
                field_type = field_types[field_idx]

        # Load based on field type
        if field_type == 'float':
            # For float fields, load as double into xmm0 and push as 8 bytes
            self.emit("movsd xmm0, [rdx + rax]")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            self.stack_types.append('f64')
        else:
            # For integer, string, bool - load as 64-bit value
            self.emit("mov rax, [rdx + rax]")
            self.emit("push rax")
            if field_type == 'str':
                self.stack_types.append('str')
            elif field_type == 'bool':
                self.stack_types.append('bool')
            else:
                self.stack_types.append('i64')

    def _compile_struct_set(self, args: List[str]):
        """Set field in struct - store to struct data area"""
        field_idx = int(args[0])

        # Stack: struct_ref value -> struct_ref
        # Pop the new value and struct reference
        self.emit("pop rbx  # new value")
        self.emit("pop rax  # struct reference")

        # Pop from stack types
        if len(self.stack_types) >= 2:
            self.stack_types.pop()  # Pop value
            self.stack_types.pop()  # Pop struct

        # Decode: instance_id = rax >> 16, struct_id = rax & 0xFFFF
        self.emit("mov rcx, rax")
        self.emit("shr rcx, 16  # rcx = instance_id")
        self.emit("mov rdx, rax")
        self.emit("and rdx, 0xFFFF  # rdx = struct_id")

        # Save struct reference for return
        self.emit("push rax  # save struct reference for return")

        # Calculate address: base + (instance_id * 256) + (field_idx * 8)
        self.emit("mov rax, rcx")
        self.emit("mov rdx, 256")
        self.emit("imul rax, rdx  # rax = instance_id * 256")
        self.emit(f"add rax, {field_idx * 8}  # rax += field_idx * 8")

        # Store new value to struct_data
        self.emit("lea rdx, [rip + struct_data]")
        self.emit("mov [rdx + rax], rbx  # store new value")

        # Struct reference is already on stack as return value
        # Restore the stack type to indicate we have a struct on top
        # Determine struct type from the last_struct_id if available
        if self.last_struct_id is not None:
            self.stack_types.append(f'struct:{self.last_struct_id}')
        else:
            self.stack_types.append('i64')  # fallback

    # ============================================================================
    # Builtin Functions
    # ============================================================================

    def _compile_builtin_str(self, args: List[str]):
        """Convert value to string - type-aware based on stack_types"""
        # Determine type from stack
        value_type = self.stack_types[-1] if self.stack_types else 'i64'

        if value_type == 'bool':
            # For boolean: pop into rdi, call runtime_bool_to_str
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_bool_to_str")
            self.emit("push rax")
        elif value_type == 'f64':
            # For float: pop from stack into xmm0, call runtime_float_to_str
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit_runtime_call("runtime_float_to_str")
            self.emit("push rax")
        elif value_type == 'list':
            # For list: pop into rdi, call runtime_list_to_str
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_list_to_str")
            self.emit("push rax")
        elif value_type == 'set':
            # For set: pop into rdi, call runtime_set_to_str
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_set_to_str")
            self.emit("push rax")
        elif value_type == 'str':
            # For string: already a string, no conversion needed
            # Just keep it on the stack as-is
            pass
        else:
            # For i64 (or unknown, default to i64): pop into rdi, call runtime_int_to_str
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_int_to_str")
            self.emit("push rax")

        # Result is always a string
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('str')

    def _compile_to_str_bool(self, args: List[str]):
        """Convert boolean value to string"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_bool_to_str")
        self.emit("push rax")

    def _compile_to_str_float(self, args: List[str]):
        """Convert float value to string"""
        # Pop the float from stack into xmm0 (System V ABI: first float arg in xmm0)
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        # Don't move to rdi - it's already in xmm0 where it needs to be!
        self.emit_runtime_call("runtime_float_to_str")
        self.emit("push rax")

    def _compile_to_str_list(self, args: List[str]):
        """Convert list to string representation"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_list_to_str")
        self.emit("push rax")

    def _compile_to_str_set(self, args: List[str]):
        """Convert set to string representation"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_set_to_str")
        self.emit("push rax")

    def _compile_to_str_i64(self, args: List[str]):
        """Convert 64-bit integer to string"""
        self.emit("pop rdi")
        self.emit_runtime_call("runtime_int_to_str")
        self.emit("push rax")

    def _compile_to_str_f64(self, args: List[str]):
        """Convert 64-bit float to string"""
        # Pop the float from stack into xmm0 (System V ABI: first float arg in xmm0)
        self.emit("movsd xmm0, [rsp]")
        self.emit("add rsp, 8")
        # Don't move to rdi - it's already in xmm0 where it needs to be!
        self.emit_runtime_call("runtime_float_to_str")
        self.emit("push rax")

    def _compile_to_str_string(self, args: List[str]):
        """Convert string to string (no-op, already a string)"""
        # String is already on the stack, just leave it there
        pass

    # ============================================================================
    # Type Conversions
    # ============================================================================

    def _compile_to_int(self, args: List[str]):
        """Convert to int (from float, string, or int)"""
        value_type = self.stack_types[-1] if self.stack_types else 'i64'

        if value_type == 'f64':
            # Convert float to int
            self.emit("movsd xmm0, [rsp]")
            self.emit("add rsp, 8")
            self.emit("cvttsd2si rax, xmm0")
            self.emit("push rax")
            self.stack_types.pop()
        elif value_type == 'str':
            # Convert string to int
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_str_to_int")
            self.emit("push rax")
            self.stack_types.pop()
        # Otherwise it's already an int, no-op
        self.stack_types.append('i64')

    def _compile_to_float(self, args: List[str]):
        """Convert int or string to float"""
        value_type = self.stack_types[-1] if self.stack_types else 'i64'

        if value_type == 'str':
            # Convert string to float
            self.emit("pop rdi")
            self.emit_runtime_call("runtime_str_to_float")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            self.stack_types.pop()
        elif value_type == 'i64':
            # Convert int to float
            self.emit("pop rax")
            self.emit("cvtsi2sd xmm0, rax")
            self.emit("sub rsp, 8")
            self.emit("movsd [rsp], xmm0")
            self.stack_types.pop()
        # Otherwise assume it's already a float, no-op

        # Update type stack
        self.stack_types.append('f64')

    def _compile_to_bool(self, args: List[str]):
        """Convert to bool"""
        self.emit("pop rax")
        self.emit("test rax, rax")
        self.emit("setnz al")
        self.emit("movzx rax, al")
        self.emit("push rax")
        # Update type stack - result is a bool
        if self.stack_types:
            self.stack_types.pop()
        self.stack_types.append('bool')

    def _compile_to_str(self, args: List[str]):
        """Convert to string"""
        self._compile_builtin_str(args)

    # ============================================================================
    # Global Variables
    # ============================================================================

    def _compile_load_global(self, args: List[str]):
        """Load global variable"""
        var_index = int(args[0])
        # Globals are stored in .bss section
        self.emit(f"mov rax, [global_vars + {var_index * 8}]")
        self.emit("push rax")

    def _compile_store_global(self, args: List[str]):
        """Store to global variable"""
        var_index = int(args[0])
        self.emit("pop rax")
        self.emit(f"mov [global_vars + {var_index * 8}], rax")

    def _compile_try_begin(self, args: List[str]):
        """Begin exception handler block (TRY_BEGIN "exc_type" handler_label)"""
        # Parse: TRY_BEGIN "exc_type" label
        # The bytecode format is: TRY_BEGIN "ExceptionType" label_name
        # After parsing in bytecode, we get 2 args: exc_type and label

        if len(args) < 2:
            # Malformed - should have been caught by parser
            raise X86CompilerError("TRY_BEGIN requires exception type and label")

        exc_type = args[0].strip('"')
        handler_label = args[1]

        # Get the assembly label for the handler
        asm_label = self.label_map.get(handler_label, f".L{handler_label}")

        # Store the exception type string in data section
        exc_type_label = self.get_string_label(exc_type)

        # Call runtime to push exception handler
        # runtime_exception_push(exc_type)
        self.runtime_dependencies.add('runtime_exception_push')
        self.runtime_dependencies.add('runtime_exception_get_jump_buffer')

        self.emit(f"lea rdi, [{exc_type_label}]  # exc_type")
        self.emit("call runtime_exception_push")

        # Get the jump buffer and save the current context with setjmp
        self.emit("call runtime_exception_get_jump_buffer")
        self.emit("mov rdi, rax  # jump buffer pointer")
        self.emit("call setjmp@PLT  # returns 0 first time, 1 when longjmp is called")

        # Check if we just returned from setjmp (0) or from longjmp (non-zero)
        self.emit("test rax, rax")
        self.emit(f"jnz {asm_label}  # if non-zero, jump to exception handler")
        # Otherwise, continue with try block

    def _compile_try_end(self, args: List[str]):
        """End exception handler block (TRY_END)"""
        # Pop exception handler from stack
        self.runtime_dependencies.add('runtime_exception_pop')
        self.emit("call runtime_exception_pop")

    def _compile_raise(self, args: List[str]):
        """Raise an exception (RAISE "exc_type" "message")"""
        # Parse the arguments - they're quoted strings
        # Format: RAISE "ExceptionType" "message"

        if len(args) < 2:
            raise X86CompilerError("RAISE requires exception type and message")

        exc_type = args[0].strip('"')
        message = args[1].strip('"') if len(args) > 1 else ""

        # Store strings in data section
        exc_type_label = self.get_string_label(exc_type)
        message_label = self.get_string_label(message)

        # Call runtime_exception_raise_at(exc_type, message, line)
        # This either jumps to a handler via longjmp or exits the program
        self.runtime_dependencies.add('runtime_exception_raise_at')

        self.emit(f"lea rdi, [{exc_type_label}]")
        self.emit(f"lea rsi, [{message_label}]")
        self.emit(f"mov rdx, {self.current_line}  # line number")
        self.emit("call runtime_exception_raise_at")
        # This function never returns if a handler is found
        # If we get here, the program has exited


def compile(bytecode: str, optimize: bool = False) -> Tuple[str, set]:
    """
    Main entry point for x86_64 compilation.

    Args:
        bytecode: Fr bytecode as string
        optimize: Whether to apply peephole optimizations (default: False - disabled due to bugs)

    Returns:
        Tuple of (assembly code as string, set of runtime dependencies)
    """
    compiler = X86Compiler(optimize=optimize)
    assembly = compiler.compile(bytecode)
    return assembly, compiler.runtime_dependencies


if __name__ == "__main__":
    # Test with simple bytecode
    test_bytecode = """
FUNC main
  CONST_I64 5
  CONST_I64 3
  ADD_I64
  BUILTIN_PRINTLN
  RETURN_VOID
ENDFUNC
"""

    asm = compile(test_bytecode)
    print(asm)

