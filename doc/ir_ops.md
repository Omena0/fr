# SSA IR Operations Reference

This document describes all operations in the SSA intermediate representation used by the optimizer pipeline.

The IR is in Static Single Assignment form: every value is defined exactly once. Control flow is expressed via basic blocks connected by explicit edges. Merge points use PHI nodes to select between values from different predecessor blocks.

## Table of Contents

- [Value Types](#value-types)
- [Constants](#constants)
- [Integer Arithmetic](#integer-arithmetic)
- [Float Arithmetic](#float-arithmetic)
- [Comparison](#comparison)
- [Logic](#logic)
- [Bitwise](#bitwise)
- [Struct Operations](#struct-operations)
- [List Operations](#list-operations)
- [String Operations](#string-operations)
- [Type Conversion](#type-conversion)
- [Function Calls](#function-calls)
- [Control Flow](#control-flow)
- [SSA](#ssa)
- [Special](#special)
- [Math Builtins](#math-builtins)
- [Global Variables](#global-variables)
- [I/O](#io)
- [Select](#select)
- [Exception Handling](#exception-handling)
- [Op Classification](#op-classification)

## Value Types

| Type | Description |
|------|-------------|
| `INT64` | 64-bit signed integer |
| `FLOAT64` | 64-bit IEEE 754 double |
| `BOOL` | Boolean (0 or 1) |
| `STRING` | Pointer to null-terminated string |
| `VOID` | No value (used for void returns) |
| `StructType` | Pointer to heap-allocated struct with named fields |
| `ListType` | Pointer to runtime-managed dynamic array |
| `SetType` | Pointer to runtime-managed hash set |

## Constants

### CONST_INT
```
%r = CONST_INT <value>
```
Materializes a 64-bit integer constant. Uses `xor reg, reg` for zero, `mov reg, imm` otherwise.

### CONST_FLOAT
```
%r = CONST_FLOAT <value>
```
Materializes a 64-bit float constant. The value is stored in `.rodata` and loaded via `movsd` from a RIP-relative address.

### CONST_STR
```
%r = CONST_STR "<value>"
```
Materializes a pointer to a null-terminated string constant stored in `.rodata`. Uses `lea reg, [rip + label]`.

### CONST_BOOL
```
%r = CONST_BOOL <0|1>
```
Materializes a boolean constant (0 or 1).

## Integer Arithmetic

All integer operations work on `INT64` values.

### ADD
```
%r = ADD %a %b
```
Integer addition. `%r = %a + %b`.

### SUB
```
%r = SUB %a %b
```
Integer subtraction. `%r = %a - %b`.

### MUL
```
%r = MUL %a %b
```
Integer multiplication using `imul`. `%r = %a * %b`.

### DIV
```
%r = DIV %a %b
```
Signed integer division using `cqo`/`idiv`. `%r = %a / %b`. Side-effecting: may raise `ZeroDivisionError`.

### MOD
```
%r = MOD %a %b
```
Signed integer modulo (remainder from `idiv`). `%r = %a % %b`. Side-effecting: may raise `ZeroDivisionError`.

### NEG
```
%r = NEG %a
```
Integer negation. `%r = -%a`.

## Float Arithmetic

All float operations work on `FLOAT64` values using SSE2 scalar double instructions.

### FADD
```
%r = FADD %a %b
```
Float addition (`addsd`). `%r = %a + %b`.

### FSUB
```
%r = FSUB %a %b
```
Float subtraction (`subsd`). `%r = %a - %b`.

### FMUL
```
%r = FMUL %a %b
```
Float multiplication (`mulsd`). `%r = %a * %b`.

### FDIV
```
%r = FDIV %a %b
```
Float division (`divsd`). `%r = %a / %b`. Side-effecting: checks for zero divisor via `ucomisd` and raises `ZeroDivisionError` if `%b == 0.0`.

### FNEG
```
%r = FNEG %a
```
Float negation via XOR with sign bit mask.

## Comparison

All comparison ops return `BOOL` (0 or 1). Emitted as `cmp` + `setCC` + `movzx`.

### LT / GT / LE / GE / EQ / NE
```
%r = LT %a %b    ; %r = %a < %b
%r = GT %a %b    ; %r = %a > %b
%r = LE %a %b    ; %r = %a <= %b
%r = GE %a %b    ; %r = %a >= %b
%r = EQ %a %b    ; %r = %a == %b
%r = NE %a %b    ; %r = %a != %b
```
For string operands, calls `runtime_str_eq` and adjusts the result. For float operands, uses `ucomisd` + `setCC`.

## Logic

### AND
```
%r = AND %a %b
```
Logical AND. `%r = %a & %b` (bitwise on booleans).

### OR
```
%r = OR %a %b
```
Logical OR. `%r = %a | %b`.

### NOT
```
%r = NOT %a
```
Logical NOT. `%r = %a ^ 1`.

## Bitwise

### SHL / SHR
```
%r = SHL %a %b    ; %r = %a << %b
%r = SHR %a %b    ; %r = %a >> %b (arithmetic)
```
Shift left / arithmetic shift right. The shift amount goes into `cl`.

### BIT_AND / BIT_OR / BIT_XOR
```
%r = BIT_AND %a %b
%r = BIT_OR %a %b
%r = BIT_XOR %a %b
```
Bitwise AND, OR, XOR operations.

## Struct Operations

Structs are heap-allocated with 8-byte-aligned fields. The struct pointer model uses a bump allocator in BSS (`struct_data`).

### ALLOC_STRUCT
```
%r = ALLOC_STRUCT %field0 %field1 ... "<struct_name>" <field_count>
```
Allocates a struct on the struct heap, stores initial field values, and returns the pointer. Uses `imm_str` for the struct name and `imm_int` for field count.

### LOAD_FIELD
```
%r = LOAD_FIELD %struct_ptr <field_index>
```
Loads a field from a struct pointer. `%r = *(struct_ptr + field_index * 8)`. Uses `imm_int` for the field index.

### STORE_FIELD
```
STORE_FIELD %struct_ptr %value <field_index>
```
Stores a value to a struct field. `*(struct_ptr + field_index * 8) = value`. Void (no result). Side-effecting.

## List Operations

Lists are runtime-managed dynamic arrays (`runtime_list_new`, `runtime_list_append_int`, etc.).

### ALLOC_LIST
```
%r = ALLOC_LIST <initial_size>
```
Allocates a new empty list via `runtime_list_new`. Returns a list pointer.

### LIST_GET
```
%r = LIST_GET %list %index
```
Gets element at index via `runtime_list_get_int`. Returns `INT64`.

### LIST_SET
```
LIST_SET %list %index %value
```
Sets element at index via `runtime_list_set_int`. Void. Side-effecting.

### LIST_APPEND
```
LIST_APPEND %list %value
```
Appends a value to the list via `runtime_list_append_int`. Void. Side-effecting.

### LIST_LEN
```
%r = LIST_LEN %list
```
Returns the length of a list via `runtime_list_len`.

## String Operations

### STR_CONCAT
```
%r = STR_CONCAT %a %b
```
Concatenates two strings via `runtime_str_concat`. Returns a new string pointer.

### STR_LEN
```
%r = STR_LEN %str
```
Returns the length of a string via `runtime_str_len`.

## Type Conversion

### INT_TO_FLOAT
```
%r = INT_TO_FLOAT %a
```
Converts `INT64` to `FLOAT64` via `cvtsi2sd`.

### FLOAT_TO_INT
```
%r = FLOAT_TO_INT %a
```
Converts `FLOAT64` to `INT64` via `cvttsd2si`.

### TO_STR
```
%r = TO_STR %a
```
Converts any value to its string representation. Dispatches to `runtime_int_to_str`, `runtime_float_to_str`, or `runtime_bool_to_str` based on operand type.

### TO_BOOL
```
%r = TO_BOOL %a
```
Converts a value to boolean via `runtime_to_bool`.

## Function Calls

### CALL
```
%r = CALL %arg0 %arg1 ... "<func_name>"
```
Direct call to a fr-defined function. Arguments are passed via System V AMD64 calling convention (rdi, rsi, rdx, rcx, r8, r9). The function name is in `imm_str`.

### CALL_EXTERN
```
%r = CALL_EXTERN %arg0 %arg1 ... "<func_name>"
```
Call to an external C function.

### CALL_BUILTIN
```
%r = CALL_BUILTIN %arg0 %arg1 ... "<builtin_name>"
```
Call to a builtin/runtime function. The builtin name maps to a runtime function (e.g., `"raise"` -> `runtime_exception_raise`, `"fork"` -> `runtime_fork`).

## Control Flow

These ops are block terminators -- they must be the last instruction in a basic block.

### BRANCH
```
BRANCH %cond "<false_label>" <true_block> <false_block>
```
Conditional branch. If `%cond` is zero, jumps to `false_label`. Otherwise falls through to the next block (true path). Emits `test` + `jz` with PHI copy trampolines for both paths.

### JUMP
```
JUMP "<target_label>" <target_block>
```
Unconditional jump to the target block. Emits PHI copies before jumping.

### RETURN
```
RETURN %value
```
Returns a value from the function. Moves result to `rax` (int) or `xmm0` (float), restores callee-saved registers, and executes `ret`.

### RETURN_VOID
```
RETURN_VOID
```
Returns from a void function. Sets `eax` to 0 and executes the epilogue.

## SSA

### PHI
```
%r = PHI %val_from_pred0 %val_from_pred1 ... <merge_index> <pred0> <pred1> ...
```
Selects a value based on which predecessor block was executed. PHI nodes are always at the beginning of a block. During codegen, PHI copies are emitted at the end of predecessor blocks (parallel move resolution).

## Special

### COPY
```
%r = COPY %src
```
Value copy. Used during SSA construction to propagate variable versions. Eliminated by optimization passes (copy propagation in SCCP).

### NOP
```
NOP
```
No operation. Placeholder that gets eliminated by DCE.

## Math Builtins

All math builtins call into the C standard library via the runtime.

```
%r = SQRT %a       ; sqrt(a)
%r = SIN %a        ; sin(a)
%r = COS %a        ; cos(a)
%r = TAN %a        ; tan(a)
%r = ABS %a        ; fabs(a) or abs(a)
%r = MIN %a %b     ; fmin(a, b)
%r = MAX %a %b     ; fmax(a, b)
%r = FLOOR %a      ; floor(a)
%r = CEIL %a       ; ceil(a)
%r = ROUND %a      ; round(a)
%r = POW %a %b     ; pow(a, b)
```

Return `FLOAT64` for most operations. `ABS` dispatches based on operand type (integer abs vs float fabs).

## Global Variables

### LOAD_GLOBAL
```
%r = LOAD_GLOBAL <slot_index>
```
Loads a global variable from the `global_vars` BSS array at the given slot index.

### STORE_GLOBAL
```
STORE_GLOBAL %value <slot_index>
```
Stores a value to a global variable slot. Void. Side-effecting.

## I/O

### PRINT
```
PRINT %value
```
Prints a value without newline. Dispatches to `runtime_print_int`, `runtime_print_str`, or `runtime_print_float` based on operand type. Side-effecting.

### PRINTLN
```
PRINTLN %value
```
Prints a value followed by a newline. Same dispatch as PRINT. Side-effecting.

### INPUT
```
%r = INPUT %prompt
```
Reads a line of input from stdin with the given prompt string. Returns a string pointer. Side-effecting.

## Select

### SELECT
```
%r = SELECT %cond %true_val %false_val
```
Branchless conditional: `%r = %cond ? %true_val : %false_val`. Emitted as `cmovz` for integer values.

## Exception Handling

### TRY_BEGIN
```
TRY_BEGIN %exc_type_str "<except_label>" <try_body_block> <except_block>
```
Sets up an exception handler. Calls `runtime_exception_push` with the exception type string, then `_setjmp` on the handler's jump buffer. If `setjmp` returns non-zero (exception was thrown), jumps to the except block. Otherwise falls through to the try body. Block terminator.

### TRY_END
```
TRY_END
```
Pops the current exception handler via `runtime_exception_pop`. Marks the end of a try or except block scope.

### RAISE
```
RAISE %exc_type_str %message_str
```
Raises an exception by calling `runtime_exception_raise`, which searches for a matching handler and performs `longjmp`. Does not return. Side-effecting.

## Op Classification

### Side-Effect Ops
These operations must never be eliminated by dead code elimination:
- Memory writes: `STORE_FIELD`, `LIST_SET`, `LIST_APPEND`, `STORE_GLOBAL`
- Calls: `CALL`, `CALL_EXTERN`, `CALL_BUILTIN`
- Control flow: `BRANCH`, `JUMP`, `RETURN`, `RETURN_VOID`
- I/O: `PRINT`, `PRINTLN`, `INPUT`
- Exception handling: `TRY_BEGIN`, `TRY_END`, `RAISE`
- Division (can raise): `DIV`, `MOD`, `FDIV`

### Terminator Ops
Must be the last instruction in a basic block:
- `BRANCH`, `JUMP`, `RETURN`, `RETURN_VOID`, `TRY_BEGIN`

### Commutative Ops
Operand order is irrelevant (used by CSE to normalize):
- `ADD`, `MUL`, `FADD`, `FMUL`
- `EQ`, `NE`, `AND`, `OR`
- `BIT_AND`, `BIT_OR`, `BIT_XOR`
- `MIN`, `MAX`
