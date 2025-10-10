

# Fr

[![Build](https://github.com/Omena0/fr/actions/workflows/publish.yaml/badge.svg)](https://github.com/Omena0/fr/actions/workflows/publish.yaml)
![Tests](https://github.com/Omena0/fr/actions/workflows/test.yaml/badge.svg)
![License](https://img.shields.io/badge/license-PolyForm%20Noncommercial-blue)
![AI Code](https://img.shields.io/badge/AI_code-59%25-red?logo=Github%20copilot)

Simple bytecode compiled C-style scripting language.

## Installation

```zsh
pip install frscript
```

## Features:
- Command line launcher (`fr`)
- **File and Socket I/O**. Low-level file operations and sockets.
- Python integration - You can use any Python libraries with Frscript.
- **Aggressive optimization**. Bytecode and AST optimizations, fused operations, fast C runtime. Stack-based VM.


## What's New

### In version 7B:
Bugfixes and performance.

- Fixed FUSED_LOAD_STORE and FUSED_STORE_LOAD instructions executing in pairs.
- Fixed SELECT instruction being incorrectly mapped.
- Added SELECT optimization for if-else statements that assign to the same variable
- SELECT instruction now automatically replaces simple if-else assignment patterns
- Optimizer detects and preserves side effects in conditional branches

### In version 7A:
General performance upgrade.

This version is ~10% faster than 6A.

- Added signature help for user-defined functions in VSCode extension
- Added float literal support to binary AST encoder/decoder
- Added function-scoped label resolution to prevent cross-function jump collisions
- Added SWITCH_JUMP_TABLE opcode with jump table optimization for switches with 5+ consecutive cases
- Added function-scoped label resolution to prevent cross-function jump collisions
- Added case body fusion pass for detecting similar labeled blocks
- Added parser support for all CMP_*_CONST and arithmetic float const instructions in C VM
- Added SWITCH_JUMP_TABLE opcode to VM instruction set
- Added parser for SWITCH_JUMP_TABLE with min/max bounds and label array
- Added label resolution for SWITCH_JUMP_TABLE jump tables
- Added warning when const functions contain non-evaluable builtins, automatically treating them as regular functions
- Implemented OP_LOAD2_MUL_F64 instruction for optimized float multiplication
- Implemented OP_SWITCH_JUMP_TABLE instruction for O(1) dense integer switch dispatch
- Implemented OP_MOD_CONST_I64 instruction for modulo with constant operand
- Implemented CMP_LT_CONST, CMP_GT_CONST, CMP_LE_CONST, CMP_GE_CONST, CMP_EQ_CONST, CMP_NE_CONST instructions & f64 variants
- Implemented ADD_CONST_F64, SUB_CONST_F64, MUL_CONST_F64, DIV_CONST_F64 VM instructions for optimized float arithmetic
- Implemented LOAD2_ADD_F64, LOAD2_SUB_F64, LOAD2_MUL_F64, LOAD2_DIV_F64 fused instructions for float operations
- Implemented SWITCH_JUMP_TABLE instruction for O(1) dense integer switch dispatch
- Implemented LIST_NEW_I64, LIST_NEW_F64, LIST_NEW_STR, and LIST_NEW_BOOL instructions
- Implemented cache_loaded_values optimization to detect duplicate LOAD instructions and use DUP
- Improved hover information to display properly formatted function signatures
- Increased VM bytecode buffer size from 4096 to 65536 characters to support long optimized list instructions
- Optimized switch case bodies by fusing similar LOAD/ADD_CONST/STORE patterns into single arithmetic expression
- Reduced switch statement overhead from 70+ instructions to ~12 instructions (83% reduction)
- Increased VM bytecode buffer size from 4096 to 65536 characters to support long optimized list instructions
- Constant list creation is now optimized to use only 1 instruction
- Fixed critical label scoping bug in C VM causing jumps to resolve to wrong function
- Fixed syntax highlighting for function parameter types using single-match pattern
- Fixed function parameter type checking to correctly identify parameter types within function bodies
- Fixed inlay hints showing parameter names in function definitions instead of just function calls
- Fixed import path in compiler.py (from optimizer -> from src.optimizer)
- Fixed ADD_CONST_I64 instruction not checking for integer overflow
- Fixed len() function evaluating at parse time instead of runtime
- Fixed the frscript extension type errors and highlighting
- Fixed type errors

### In Version 6D
Feature and bugfix update

- Added runtime error handling
- Added try-except statements.
- Added raise statement
- Added ExceptionHandler structure to VM with exception type, handler PC, and state snapshots
- Added float division by zero detection in DIV_F64 operation
- Added bytecode parsing for TRY_BEGIN "exc_type" label and TRY_END instructions
- Added tests for exception handling
- Added exception type detection from "[Type] message" format in C VM error handler
- Implemented exception handling with OP_TRY_BEGIN, OP_TRY_END, and OP_RAISE opcodes
- Implemented exception handler stack (MAX_EXCEPTION_HANDLERS = 64)
- Modified vm_runtime_error() to check for active exception handlers and jump to matching ones
- Fixed some errors not showing the correct line or char
- Fixed eval_expr not properly re-raising exceptions
- Fixed stack overflow in C VM caused by missing RETURN_VOID in void functions
- Fixed float division by zero detection in C VM
- Fixed test runner to properly handle exceptions vs partial output in C VM

### In Version 6A
Bugfixes.

- Fixed Python SyntaxError handling for unclosed strings in parser

    The parser now properly catches and handles Python SyntaxErrors when parsing expressions with unclosed strings, providing better error messages.

- Improved error handling in expression parser
- Updated README with improved installation instructions

### In Version 5A
Debugging update

- Added comprehensive debugging support

    You can now debug FRScript code with step-by-step execution, breakpoints, and detailed variable tracking.
    The debug runtime provides execution tracing and improved error tracking for easier troubleshooting.

- Added debug runtime with step-by-step execution capabilities
- Enhanced parser with improved error tracking and debugging information
- Added breakpoint support in debug runtime
- Created chat application examples (client and server)
- Improved runtime with better variable tracking
- Added detailed execution tracing capabilities
- Reorganized test cases into categorized folders (assertions, control_flow, data_structures, data_types, expressions, functions, io, math, misc, operators, python_interop, runtime_errors, syntax_errors)
- Moved over 240 test files into organized directory structure

### In Version 4E
- Fixed C runtime Python object handling
- Improved optimizer for Python objects
- Enhanced test suite stability

### In Version 4D
- Added pyobj as type alias for pyobject

    You can now use the shorter `pyobj` keyword instead of `pyobject` for Python object types.

- Created test cases for pyobj usage
- Updated examples to use shorter pyobj syntax

### In Version 4C
- Added 9 test cases for Python object setattr functionality

    Comprehensive testing for setting Python object attributes from FRScript, covering all data types and edge cases.

- Tests cover: basic setattr, boolean, float, list, multiple attributes, multiple objects, nested attributes, overwrite, string values

### In Version 4B
- Fixed Python attribute access in both runtimes
- Added Python module function call support

    You can now call Python module functions directly and access Python object methods from FRScript.

- Enhanced optimizer with 190+ lines of improvements
- Improved C VM with 1000+ lines of Python object handling
- Added method call statement support
- Enhanced compiler with better Python integration

### In Version 4A
- Full Python integration and interoperability

    You can now use any Python libraries from FRScript! Import Python modules, create Python objects, call functions, and access attributes seamlessly.
    Support for pyimport statements (basic, from, as) and pyobject types for wrapping Python objects.
    Integration with Python standard library including datetime, pathlib, regex, StringIO, and collections.

- Added Python import support (pyimport, pyimport from, pyimport as)
- Implemented Python object (pyobject) type for wrapping Python objects
- Added Python function calling from FRScript
- Support for Python attribute access and method calls
- Created 53 Python interop test cases
- Enhanced compiler with 340+ lines of Python integration code
- Improved C VM with 430+ lines of Python support
- Added builtin functions for Python interop
- Support for Python class instantiation
- Python object comparison and collection support
- Integration with Python standard library (datetime, pathlib, regex, StringIO, collections)
- Created UI example using Python integration
- Enhanced parser with Python syntax support
- Improved runtime with Python object handling
- Updated README with Python integration examples

### In Version 3B
- Bugfixes for HTTP server
- Enhanced builtin functions
- Improved CLI functionality
- Fixed compiler edge cases

### In Version 3A
- Added HTTP server example with static file serving

    Full-featured HTTP server implementation with routing, static file serving, and socket handling.

- Renamed all test files from .c to .fr extension
- Enhanced parser for better syntax handling
- Improved runtime with additional capabilities
- Added comprehensive HTTP routing example

### In Version 2B
- Added more I/O utility functions

    Enhanced file I/O with sequential reads, write returns, and improved socket handling for multiple connections.

- Enhanced file operations with sequential reads and write returns
- Improved socket handling with multiple connections
- Updated C VM with 550+ lines of I/O improvements
- Enhanced builtin functions with 220+ lines of I/O code
- Improved compiler with better I/O bytecode generation
- Enhanced parser with 120+ lines of improvements
- Added var_in_function test case

### In Version 2A
- Added comprehensive file I/O support

    Low-level file operations including read, write, append, and partial reads.
    Socket I/O for network programming with client and server functionality.

- Implemented socket I/O for network programming
- Added file operations: read, write, append, partial reads
- Socket client and server functionality
- Added userdata support for custom data handling
- Enhanced C VM with 440+ lines of I/O code
- Added 290+ lines of builtin I/O functions
- Enhanced compiler with I/O bytecode generation
- Added 10 I/O test cases

### In Version A1
- Initial release of FRScript

    A simple bytecode compiled C-style scripting language with Python runtime and C VM.
    Full language support for variables, functions, control flow, data types, and operations.

- Complete Python runtime implementation (709 lines)
- C VM implementation with 3758 lines
- Parser with full language syntax support (1430 lines)
- Compiler with bytecode generation (1207 lines)
- Optimizer for code optimization (488 lines)
- Support for: variables, functions, control flow (if/else, for, while, switch), assertions
- String operations: concat, join, split, replace, upper, lower, strip
- List operations: indexing, assignment, length
- Math operations: abs, max, min, pow, expressions
- F-string support with expressions
- Struct/object support with nested structs
- Type conversions: int, float, bool, str
- Break and continue statements with level support
- Comprehensive error handling
- 101 initial test cases
- CLI with multiple execution modes (327 lines)
- Binary module for bytecode operations (160 lines)
- Builtin functions module (270 lines)
- Utility functions for runtime operations (265 lines)
- Test runner (250 lines)
- Complete README documentation

