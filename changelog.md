# Changelog

## 10A

### WebAssembly Compiler & Runtime

- Full WASM backend: translates frscript bytecode to WebAssembly Text (WAT) with wasmtime runner
- New opcodes supported in WASM:
  - Arithmetic: `ADD/SUB/MUL/DIV/MOD/POW/NEG` (i64 and f64 variants, const variants, fused LOAD2 variants)
  - Comparison: `CMP_EQ/NE/LT/GT/LE/GE` (regular, const, and f64 variants)
  - Logical/bitwise: `AND, OR, NOT, AND_I64, OR_I64, XOR_I64, SHL_I64, SHR_I64`
  - Control flow: `JUMP_IF_FALSE/TRUE, SWITCH_JUMP_TABLE, TRY_BEGIN/END, RAISE, GOTO_CALL`
  - Data: `STRUCT_NEW/GET/SET, LIST_NEW/GET/SET/POP/APPEND, SET_NEW/ADD/REMOVE/CONTAINS, DICT_*`
  - Strings: `STR_EQ, STR_SPLIT, STR_JOIN, CONTAINS, ENCODE, DECODE, ADD_STR`
  - Functions: `CALL, CALL_VAR, CALL_INDIRECT, CONST_FUNC, LOAD_OUTER`
  - Type: `TO_INT, TO_FLOAT, TO_BOOL, TO_STR, DUP, FUSED_LOAD_STORE, FUSED_GET_STORE_LOAD`
  - Builtins: `BUILTIN_LEN/STR/PRINT/PRINTLN/ROUND/FLOOR/CEIL/PI, SLEEP, EXIT`
  - I/O: `FILE_OPEN/READ/WRITE/CLOSE, FORK, WAIT`
- Semantic type stack tracking using `.type` annotations for correct type inference
- Two-pass control flow analysis for forward/backward jump detection
- Loop structure detection (for/while/for-in) with proper block/loop nesting
- WASM peephole optimizer: constant folding, strength reduction, dead code/block elimination, comparison inversion
- WAT optimizer: removes unused imports/locals/comments, reduces output ~35%
- String handling with (ptr, len) pairs, string constant pooling, and host functions (str_upper/lower/strip/replace/split/join/contains/eq)
- Full struct support with heap allocation and nested struct field access
- Exception handling via global state and block-based control flow (try/except/raise)
- Closure support: nested functions, decorators, first-class functions via CONST_FUNC/LOAD_OUTER/CALL_INDIRECT
- Host functions in Rust runner: print, math, string ops, file I/O, sets, fork/wait, error reporting

### WASM Web / Browser Support

- Self-contained HTML generation via `-w/--web` flag with embedded WASM
- `js_import` statement for importing JavaScript functions
- DOM manipulation: `dom_create, dom_set_text, dom_append, dom_query, dom_set_attr, dom_set_style`, etc.
- Browser APIs: `alert, confirm, prompt, console_log/warn/error`
- Timers: `set_timeout, set_interval, clear_timeout, clear_interval`
- Storage: `get/set/remove_local_storage`
- JS interop: `js_eval, js_get/set_global, js_call, performance_now`
- CSS helpers: `css_add_rule, css_class/classes`
- JS minification (terser), zopfli compression, tree-shaken runtime imports

### C VM Runtime

- `LIST_NEW_STACK` opcode and `runtime_list_from_array` for efficient bulk list creation
- `LIST_NEW_CAP` bytecode loader for preallocated lists
- Integer overflow detection in subtraction (bigint promotion)
- `INT64_MIN` handling in NEG/ABS (bigint promotion)
- Dynamic buffer growth for list/set `value_to_string`
- Heap-allocated arrays for LIST_NEW instead of fixed stack arrays
- `CALL_VAR` for indirect function calls, `LOAD_OUTER` for closure variable access
- Variadic argument packing into lists
- Correct raise/error line mapping for runtime errors

### Native Compiler

- `LIST_NEW_STACK` with pointer preservation
- Closure support: `CONST_FUNC, LOAD_OUTER, CALL_INDIRECT` with `runtime_save/get_outer_var`
- `CALL_VAR` via strcmp-based function dispatch
- Decorator transformation via wrapper function extraction
- Register allocator for frequently used locals
- Struct codegen optimizations: shifts, hoisted base, fused LOAD+STRUCT_GET
- Assembly optimizer: jump chain collapse, mov-chain reduction, peephole no-op removal, push/pop folding
- Static data arrays for list literals to reduce asm size
- Consolidated print/println into single dispatch method; parameterized comparison/binop methods
- GCC optimization changed from `-Ofast` to `-O3` for IEEE 754 correctness
- Runtime fixes: dynamic buffer in list/set repr, fd_table slot recycling, no pointer heuristic in print

### SSA Compiler

- Exception handling via setjmp/longjmp
- Float division-by-zero runtime check
- Constraint-aware register allocation (forbidden_regs for DIV/MOD/SHL/SHR)
- Parallel move resolution with cycle detection for PHI copies
- Fixed MUL codegen rax clobbering, parameter live interval initialization, STORE_CONST_I64 multi-pair processing

### Parser

- Variadic parameter packing moved from compiler to parser (list literal transformation)
- `*args` / `**kwargs` syntax, return type annotations (`-> type`), decorator syntax (`@decorator`)
- Function references: function names as values, first-class functions
- Default function arguments
- Multiline support: function calls, list/set literals, struct creation, variable assignments
- Closure fixes: chained calls, nested function return types, decorator application
- Typed for-in loop variables preserved correctly

### Bytecode Compiler & Optimizer

- Dead store elimination with basic liveness analysis (full function context)
- Iterative constant folding for chained operations (e.g., `(5+3)*2-1` -> `15`)
- Fused instruction folding (`CONST_I64 + ADD_CONST_I64` -> `CONST_I64`)
- `FUSED_GET_STORE_LOAD` instruction fusing `STRUCT_GET+STORE+LOAD` triplets
- Table-driven LOAD2 fusion (20 blocks -> 1 set) and constant folding (17 blocks -> 2 dicts)
- Annotation-aware pattern matching (`.type` and `.line` directives preserved across all passes)
- `DICT_*` bytecode operations, `LIST_NEW_CAP` for static preallocated lists
- Struct field read caching per statement to reduce STRUCT_GET usage
- Parse-time evaluation with memoization, timeout guards, memo table compilation into bytecode
- Oversized integer constant folding to string literals for print contexts

### Python Runtime

- Variadic argument packing into lists
- Full decorator support with wrapper functions, nested functions, and closures
- Closure variable capture from enclosing scope

### VS Code Extension

- Web API completions with signatures and parameter hints
- Syntax highlighting: nested f-strings, varargs, WASM Web APIs, decorators, test lines
- Multiline support: function calls/declarations, list/set literals, struct creation
- Scope-aware rename provider, improved call hierarchy, C header parsing
- Fixed false positives for function references and decorated functions

### Testing & CLI

- `fr wasm` command with `-r/--run` flag; direct `.wasm` file execution; `-w/--web` for HTML output
- Bytecode caching for VM/native tests; runtime object file caching for native compilation
- Pre-flight gcc syntax check for runtime_lib.c
- Optimizer regression test suite
- WASM test runner with skip support

### Documentation

- Updated vm_instructions.md with function reference instructions and INPUT
- Added doc/wasm_support.md and doc/ir_ops.md

---

## Version 9B

Native executable support.

- Initial native compiler implementation with x86-64 assembly generation
- C interop: `c_import`, `c_link`, automatic C header parsing for function signatures and struct definitions
- `import <file.fr>` for importing other Fr source files
- `#pragma no_eval` directive to disable constant evaluation at parse time
- Color struct packing for raylib C interop
- Native optimizer passes: multiply strength reduction, stack alignment simplification, constant imul
- Inlined LIST_GET/LIST_SET with fast-path bounds checking
- Fused LOAD2_DIV_I64 and LOAD2_DIV_F64 instructions
- Automatic int-to-float conversion for C function float parameters
- GCC optimization level `-O3` for both CLI and test runner
- Numerous fixes for: function epilogues, argument type tracking, struct field types, set/list pointer preservation, float handling, control flow label detection, bool zero-extension

---

## Version 8A

Speed improvements (fibonacci benchmark now faster than Python), new language features.

- `goto` statement with `<type> <var> = goto <label>` return value syntax
- Compiler directives: `#label` for jump targets, `#bytecode` for inline bytecode
- `print()` function (no newline)
- `fork()` and `wait()` for process management
- `bytes` and `set` types with full VM support
- Global variables: `LOAD_GLOBAL`, `STORE_GLOBAL`, `.global` directive
- `ENCODE`/`DECODE` bytecode for string encoding operations
- `CONTAINS` instruction for generic membership checking (`in`/`not in` on lists, strings, sets)
- Set operations: `SET_NEW, SET_ADD, SET_REMOVE, SET_CONTAINS, SET_LEN` with hash table (O(1))
- Reference counting for strings and lists (eliminates deep copying)
- Arena allocator for batch allocation (64KB blocks)
- String interning for constant strings
- Inlined arithmetic fast paths; optimized comparison and LOAD operations
- `||` syntax in test expectations for alternative expected values
- Socket functions updated to use bytes type
- Fixed: stack underflow on builtin method calls, bytes conversion, dict initialization, f-string method chaining, optimizer CONST_STR merging before PY_CALL

---

## Version 7B

- Fixed FUSED_LOAD_STORE and FUSED_STORE_LOAD executing in pairs
- Fixed SELECT instruction mapping
- Added SELECT optimization for simple if-else assignment patterns with side-effect preservation

---

## Version 7A

~10% performance improvement over 6A.

- `SWITCH_JUMP_TABLE` opcode for O(1) dense integer switch dispatch (83% instruction reduction)
- Fused float instructions: `LOAD2_MUL/ADD/SUB/DIV_F64, MOD_CONST_I64`
- Const-comparison instructions: `CMP_LT/GT/LE/GE/EQ/NE_CONST` (int and float variants)
- Float const arithmetic: `ADD/SUB/MUL/DIV_CONST_F64`
- `LIST_NEW_I64/F64/STR/BOOL` instructions (constant list creation in 1 instruction)
- `cache_loaded_values` optimization (duplicate LOAD -> DUP)
- Function-scoped label resolution; case body fusion pass
- VS Code extension: signature help, inlay hints fixes, syntax highlighting improvements
- Bytecode buffer increased to 65536 chars
- Warning for non-evaluable builtins in const functions

---

## Version 6D

Runtime error handling.

- `try`/`except`/`raise` statements
- Exception handler stack (max 64), `TRY_BEGIN/TRY_END/RAISE` opcodes
- Exception type detection from "[Type] message" format
- Float division by zero detection in DIV_F64
- Fixed: error line/char reporting, stack overflow from missing RETURN_VOID, eval_expr exception propagation

---

## Version 6A

- Fixed Python SyntaxError handling for unclosed strings in parser
- Improved error handling in expression parser

---

## Version 5A

Debugging support.

- Debug runtime with step-by-step execution, breakpoints, variable tracking, and execution tracing
- Chat application examples (client and server)
- Reorganized 240+ test files into categorized folders

---

## Version 4E

- Fixed C runtime Python object handling
- Improved optimizer for Python objects

---

## Version 4D

- Added `pyobj` as type alias for `pyobject`

---

## Version 4C

- Added 9 test cases for Python object setattr functionality

---

## Version 4B

- Fixed Python attribute access in both runtimes
- Added Python module function call support
- Enhanced optimizer (190+ lines), C VM Python object handling (1000+ lines)
- Method call statement support

---

## Version 4A

Full Python integration.

- `pyimport` statements (basic, from, as) and `pyobject` type
- Call Python functions, access attributes, instantiate classes from FrScript
- 53 Python interop test cases
- Integration with Python standard library (datetime, pathlib, regex, StringIO, collections)

---

## Version 3B

- Bugfixes for HTTP server, enhanced builtins, improved CLI

---

## Version 3A

- HTTP server example with static file serving and routing
- Renamed test files from .c to .fr

---

## Version 2B

- Enhanced file I/O with sequential reads and write returns
- Improved socket handling with multiple connections

---

## Version 2A

- File I/O: read, write, append, partial reads
- Socket I/O for network programming (client and server)
- Userdata support for custom data handling

---

## Version A1

Initial release.

- Python runtime (709 lines) and C VM (3758 lines)
- Parser (1430 lines), compiler (1207 lines), optimizer (488 lines)
- Variables, functions, control flow (if/else, for, while, switch), assertions
- String ops (concat, join, split, replace, upper, lower, strip), list ops, math ops
- F-strings, structs with nesting, type conversions, break/continue with levels
- 101 test cases, CLI with multiple execution modes
