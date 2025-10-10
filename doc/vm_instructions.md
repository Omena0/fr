# VM Instructions Reference

This document describes all bytecode instructions supported by the fr VM.

## Table of Contents

- [Constants](#constants)
- [Memory Operations](#memory-operations)
- [Arithmetic Operations](#arithmetic-operations)
- [Comparison Operations](#comparison-operations)
- [Logical Operations](#logical-operations)
- [Control Flow](#control-flow)
- [Function Calls](#function-calls)
- [Stack Operations](#stack-operations)
- [List Operations](#list-operations)
- [Struct Operations](#struct-operations)
- [Type Conversions](#type-conversions)
- [String Operations](#string-operations)
- [Math Functions](#math-functions)
- [File I/O Operations](#file-io-operations)
- [Socket Operations](#socket-operations)
- [Python Interop](#python-interop)
- [Exception Handling](#exception-handling)
- [Built-in Functions](#built-in-functions)
- [Optimized Instructions](#optimized-instructions)

---

## Constants

### CONST_I64
Push a 64-bit integer constant onto the stack.

**Syntax:** `CONST_I64 <value>`

**Stack:** `-> int64`

### CONST_F64
Push a 64-bit float constant onto the stack.

**Syntax:** `CONST_F64 <value>`

**Stack:** `-> float64`

### CONST_STR
Push a string constant onto the stack.

**Syntax:** `CONST_STR <string>`

**Stack:** `-> string`

### CONST_BOOL
Push a boolean constant onto the stack.

**Syntax:** `CONST_BOOL <true|false>`

**Stack:** `-> bool`

### CONST_I64_MULTI
Push multiple int64 constants onto the stack.

**Syntax:** `CONST_I64_MULTI <count> <val1> <val2> ...`

**Stack:** `-> int64 int64 ...`

### CONST_F64_MULTI
Push multiple float64 constants onto the stack.

**Syntax:** `CONST_F64_MULTI <count> <val1> <val2> ...`

**Stack:** `-> float64 float64 ...`

### CONST_STR_MULTI
Push multiple string constants onto the stack.

**Syntax:** `CONST_STR_MULTI <count> <str1> <str2> ...`

**Stack:** `-> string string ...`

### CONST_BOOL_MULTI
Push multiple boolean constants onto the stack.

**Syntax:** `CONST_BOOL_MULTI <count> <val1> <val2> ...`

**Stack:** `-> bool bool ...`

---

## Memory Operations

### LOAD
Load a local variable onto the stack.

**Syntax:** `LOAD <var_index>`

**Stack:** `-> value`

### STORE
Pop a value from the stack and store it in a local variable.

**Syntax:** `STORE <var_index>`

**Stack:** `value ->`

### STORE_CONST_I64
Store integer constants directly to variable slots without using the stack.

**Syntax:** `STORE_CONST_I64 <count> <slot1> <val1> <slot2> <val2> ...`

**Stack:** `->`

### STORE_CONST_F64
Store float constants directly to variable slots without using the stack.

**Syntax:** `STORE_CONST_F64 <count> <slot1> <val1> <slot2> <val2> ...`

**Stack:** `->`

### STORE_CONST_BOOL
Store boolean constants directly to variable slots without using the stack.

**Syntax:** `STORE_CONST_BOOL <count> <slot1> <val1> <slot2> <val2> ...`

**Stack:** `->`

### STORE_CONST_STR
Store string constants directly to variable slots without using the stack.

**Syntax:** `STORE_CONST_STR <count> <slot1> <val1> <slot2> <val2> ...`

**Stack:** `->`

### STORE_REF
Store a reference/pointer instead of copying the value (for aliasing).

**Syntax:** `STORE_REF <var_index>`

**Stack:** `value ->`

### COPY_LOCAL
Copy one local variable to another without using the stack (deep copy).

**Syntax:** `COPY_LOCAL <src> <dst>`

**Stack:** `->`

### COPY_LOCAL_REF
Alias one local variable to another (pointer alias, not a copy).

**Syntax:** `COPY_LOCAL_REF <src> <dst>`

**Stack:** `->`

### LOAD_MULTI
Load multiple variables onto the stack at once.

**Syntax:** `LOAD_MULTI <count> <var1> <var2> ...`

**Stack:** `-> value1 value2 ...`

### FUSED_LOAD_STORE
Interleaved load/store operations.

**Syntax:** `FUSED_LOAD_STORE <count> <src1> <dst1> <src2> <dst2> ...`

**Stack:** `->`

### FUSED_STORE_LOAD
Interleaved store/load operations.

**Syntax:** `FUSED_STORE_LOAD <count> <dst1> <src1> <dst2> <src2> ...`

**Stack:** `->`

---

## Arithmetic Operations

### ADD_I64
Add two 64-bit integers.

**Syntax:** `ADD_I64`

**Stack:** `int64 int64 -> int64`

### SUB_I64
Subtract two 64-bit integers.

**Syntax:** `SUB_I64`

**Stack:** `int64 int64 -> int64`

### MUL_I64
Multiply two 64-bit integers.

**Syntax:** `MUL_I64`

**Stack:** `int64 int64 -> int64`

### DIV_I64
Divide two 64-bit integers.

**Syntax:** `DIV_I64`

**Stack:** `int64 int64 -> int64`

### MOD_I64
Compute modulo of two 64-bit integers.

**Syntax:** `MOD_I64`

**Stack:** `int64 int64 -> int64`

### ADD_F64
Add two 64-bit floats.

**Syntax:** `ADD_F64`

**Stack:** `float64 float64 -> float64`

### SUB_F64
Subtract two 64-bit floats.

**Syntax:** `SUB_F64`

**Stack:** `float64 float64 -> float64`

### MUL_F64
Multiply two 64-bit floats.

**Syntax:** `MUL_F64`

**Stack:** `float64 float64 -> float64`

### DIV_F64
Divide two 64-bit floats.

**Syntax:** `DIV_F64`

**Stack:** `float64 float64 -> float64`

### ADD_STR
Concatenate two strings.

**Syntax:** `ADD_STR`

**Stack:** `string string -> string`

### NEG
Negate the top of the stack (unary negation).

**Syntax:** `NEG`

**Stack:** `number -> number`

---

## Comparison Operations

### CMP_EQ
Compare two values for equality.

**Syntax:** `CMP_EQ`

**Stack:** `value value -> bool`

### CMP_NE
Compare two values for inequality.

**Syntax:** `CMP_NE`

**Stack:** `value value -> bool`

### CMP_LT
Compare if first value is less than second.

**Syntax:** `CMP_LT`

**Stack:** `value value -> bool`

### CMP_GT
Compare if first value is greater than second.

**Syntax:** `CMP_GT`

**Stack:** `value value -> bool`

### CMP_LE
Compare if first value is less than or equal to second.

**Syntax:** `CMP_LE`

**Stack:** `value value -> bool`

### CMP_GE
Compare if first value is greater than or equal to second.

**Syntax:** `CMP_GE`

**Stack:** `value value -> bool`

---

## Logical Operations

### AND
Logical AND of two boolean values.

**Syntax:** `AND`

**Stack:** `bool bool -> bool`

### OR
Logical OR of two boolean values.

**Syntax:** `OR`

**Stack:** `bool bool -> bool`

### NOT
Logical NOT of a boolean value.

**Syntax:** `NOT`

**Stack:** `bool -> bool`

### AND_I64
Bitwise AND of two 64-bit integers.

**Syntax:** `AND_I64`

**Stack:** `int64 int64 -> int64`

### OR_I64
Bitwise OR of two 64-bit integers.

**Syntax:** `OR_I64`

**Stack:** `int64 int64 -> int64`

### XOR_I64
Bitwise XOR of two 64-bit integers.

**Syntax:** `XOR_I64`

**Stack:** `int64 int64 -> int64`

### SHL_I64
Shift left (multiply by power of 2).

**Syntax:** `SHL_I64`

**Stack:** `int64 int64 -> int64`

### SHR_I64
Shift right (divide by power of 2).

**Syntax:** `SHR_I64`

**Stack:** `int64 int64 -> int64`

---

## Control Flow

### JUMP
Unconditional jump to a label.

**Syntax:** `JUMP <label>`

**Stack:** `->`

### JUMP_IF_FALSE
Jump to a label if the top of stack is false.

**Syntax:** `JUMP_IF_FALSE <label>`

**Stack:** `bool ->`

### JUMP_IF_TRUE
Jump to a label if the top of stack is true.

**Syntax:** `JUMP_IF_TRUE <label>`

**Stack:** `bool ->`

### LABEL
Define a jump target label.

**Syntax:** `LABEL <name>`

**Stack:** `->`

### BREAK
Break from a loop with a specified level.

**Syntax:** `BREAK <level>`

**Stack:** `->`

### CONTINUE
Continue to the next iteration of a loop with a specified level.

**Syntax:** `CONTINUE <level>`

**Stack:** `->`

### HALT
Stop execution of the VM.

**Syntax:** `HALT`

**Stack:** `->`

---

## Function Calls

### CALL
Call a function.

**Syntax:** `CALL <function_name>`

**Stack:** `arg1 arg2 ... -> return_value`

### RETURN
Return from a function with a value.

**Syntax:** `RETURN`

**Stack:** `value ->`

### RETURN_VOID
Return from a function without a value.

**Syntax:** `RETURN_VOID`

**Stack:** `->`

---

## Stack Operations

### POP
Remove the top value from the stack.

**Syntax:** `POP`

**Stack:** `value ->`

### DUP
Duplicate the top value on the stack.

**Syntax:** `DUP`

**Stack:** `value -> value value`

### DUP2
Duplicate the top two values on the stack.

**Syntax:** `DUP2`

**Stack:** `a b -> a b a b`

### SWAP
Swap the top two values on the stack.

**Syntax:** `SWAP`

**Stack:** `a b -> b a`

### ROT
Rotate the top three stack values.

**Syntax:** `ROT`

**Stack:** `a b c -> b c a`

### OVER
Copy the second item to the top.

**Syntax:** `OVER`

**Stack:** `a b -> a b a`

### SELECT
Select between two values based on a condition.

**Syntax:** `SELECT`

**Stack:** `cond a b -> result`

---

## List Operations

### LIST_NEW
Create a new empty list.

**Syntax:** `LIST_NEW`

**Stack:** `-> list`

### LIST_APPEND
Append a value to a list.

**Syntax:** `LIST_APPEND`

**Stack:** `list value -> list`

### LIST_GET
Get an element from a list at a specified index.

**Syntax:** `LIST_GET`

**Stack:** `list index -> value`

### LIST_SET
Set an element in a list at a specified index.

**Syntax:** `LIST_SET`

**Stack:** `list index value -> list`

### LIST_LEN
Get the length of a list.

**Syntax:** `LIST_LEN`

**Stack:** `list -> int64`

### LIST_POP
Pop the last element from a list.

**Syntax:** `LIST_POP`

**Stack:** `list -> value`

---

## Struct Operations

### STRUCT_NEW
Create a new struct instance.

**Syntax:** `STRUCT_NEW <struct_id>`

**Stack:** `-> struct`

### STRUCT_GET
Get a field value from a struct.

**Syntax:** `STRUCT_GET <field_index>`

**Stack:** `struct -> value`

### STRUCT_SET
Set a field value in a struct.

**Syntax:** `STRUCT_SET <field_index>`

**Stack:** `struct value -> struct`

---

## Type Conversions

### TO_INT
Convert the top of stack to an integer.

**Syntax:** `TO_INT`

**Stack:** `value -> int64`

### TO_FLOAT
Convert the top of stack to a float.

**Syntax:** `TO_FLOAT`

**Stack:** `value -> float64`

### TO_BOOL
Convert the top of stack to a boolean.

**Syntax:** `TO_BOOL`

**Stack:** `value -> bool`

### TO_STR
Convert the top of stack to a string (alias for BUILTIN_STR).

**Syntax:** `TO_STR`

**Stack:** `value -> string`

---

## String Operations

### STR_UPPER
Convert a string to uppercase.

**Syntax:** `STR_UPPER`

**Stack:** `string -> string`

### STR_LOWER
Convert a string to lowercase.

**Syntax:** `STR_LOWER`

**Stack:** `string -> string`

### STR_STRIP
Strip whitespace from both ends of a string.

**Syntax:** `STR_STRIP`

**Stack:** `string -> string`

### STR_SPLIT
Split a string by a separator.

**Syntax:** `STR_SPLIT`

**Stack:** `string separator -> list`

### STR_JOIN
Join a list of strings with a separator.

**Syntax:** `STR_JOIN`

**Stack:** `separator list -> string`

### STR_REPLACE
Replace a substring with another string.

**Syntax:** `STR_REPLACE`

**Stack:** `string old new -> string`

---

## Math Functions

### ABS
Compute the absolute value.

**Syntax:** `ABS`

**Stack:** `number -> number`

### POW
Raise a number to a power.

**Syntax:** `POW`

**Stack:** `base exponent -> result`

### MIN
Get the minimum of two values.

**Syntax:** `MIN`

**Stack:** `value value -> value`

### MAX
Get the maximum of two values.

**Syntax:** `MAX`

**Stack:** `value value -> value`

### FLOOR
Compute the floor of a number.

**Syntax:** `FLOOR`

**Stack:** `number -> number`

### CEIL
Compute the ceiling of a number.

**Syntax:** `CEIL`

**Stack:** `number -> number`

### SIN
Compute the sine of a number.

**Syntax:** `SIN`

**Stack:** `float64 -> float64`

### COS
Compute the cosine of a number.

**Syntax:** `COS`

**Stack:** `float64 -> float64`

### TAN
Compute the tangent of a number.

**Syntax:** `TAN`

**Stack:** `float64 -> float64`

---

## File I/O Operations

### FILE_OPEN
Open a file.

**Syntax:** `FILE_OPEN`

**Stack:** `path mode -> fd`

### FILE_READ
Read from a file.

**Syntax:** `FILE_READ`

**Stack:** `fd size -> string`

### FILE_WRITE
Write to a file.

**Syntax:** `FILE_WRITE`

**Stack:** `fd data -> bytes_written`

### FILE_CLOSE
Close a file.

**Syntax:** `FILE_CLOSE`

**Stack:** `fd ->`

### FILE_EXISTS
Check if a file or directory exists.

**Syntax:** `FILE_EXISTS`

**Stack:** `path -> bool`

### FILE_ISFILE
Check if a path is a file.

**Syntax:** `FILE_ISFILE`

**Stack:** `path -> bool`

### FILE_ISDIR
Check if a path is a directory.

**Syntax:** `FILE_ISDIR`

**Stack:** `path -> bool`

### FILE_LISTDIR
List the contents of a directory.

**Syntax:** `FILE_LISTDIR`

**Stack:** `path -> list`

### FILE_MKDIR
Create a directory.

**Syntax:** `FILE_MKDIR`

**Stack:** `path ->`

### FILE_MAKEDIRS
Create a directory and all parent directories.

**Syntax:** `FILE_MAKEDIRS`

**Stack:** `path ->`

### FILE_REMOVE
Remove a file.

**Syntax:** `FILE_REMOVE`

**Stack:** `path ->`

### FILE_RMDIR
Remove a directory.

**Syntax:** `FILE_RMDIR`

**Stack:** `path ->`

### FILE_RENAME
Rename or move a file.

**Syntax:** `FILE_RENAME`

**Stack:** `old_path new_path ->`

### FILE_GETSIZE
Get the size of a file.

**Syntax:** `FILE_GETSIZE`

**Stack:** `path -> int64`

### FILE_GETCWD
Get the current working directory.

**Syntax:** `FILE_GETCWD`

**Stack:** `-> string`

### FILE_CHDIR
Change the current working directory.

**Syntax:** `FILE_CHDIR`

**Stack:** `path ->`

### FILE_ABSPATH
Get the absolute path of a file.

**Syntax:** `FILE_ABSPATH`

**Stack:** `path -> string`

### FILE_BASENAME
Get the basename of a path.

**Syntax:** `FILE_BASENAME`

**Stack:** `path -> string`

### FILE_DIRNAME
Get the directory name of a path.

**Syntax:** `FILE_DIRNAME`

**Stack:** `path -> string`

### FILE_JOIN
Join multiple path components.

**Syntax:** `FILE_JOIN`

**Stack:** `list -> string`

---

## Socket Operations

### SOCKET_CREATE
Create a new socket.

**Syntax:** `SOCKET_CREATE`

**Stack:** `family type -> sock_id`

### SOCKET_CONNECT
Connect a socket to a remote address.

**Syntax:** `SOCKET_CONNECT`

**Stack:** `sock_id host port ->`

### SOCKET_BIND
Bind a socket to a local address.

**Syntax:** `SOCKET_BIND`

**Stack:** `sock_id host port ->`

### SOCKET_LISTEN
Listen for connections on a socket.

**Syntax:** `SOCKET_LISTEN`

**Stack:** `sock_id backlog ->`

### SOCKET_ACCEPT
Accept a connection on a listening socket.

**Syntax:** `SOCKET_ACCEPT`

**Stack:** `sock_id -> client_sock_id`

### SOCKET_SEND
Send data on a socket.

**Syntax:** `SOCKET_SEND`

**Stack:** `sock_id data -> bytes_sent`

### SOCKET_RECV
Receive data from a socket.

**Syntax:** `SOCKET_RECV`

**Stack:** `sock_id size -> string`

### SOCKET_CLOSE
Close a socket.

**Syntax:** `SOCKET_CLOSE`

**Stack:** `sock_id ->`

### SOCKET_SETSOCKOPT
Set a socket option.

**Syntax:** `SOCKET_SETSOCKOPT`

**Stack:** `sock_id level option value ->`

---

## Python Interop

### PY_IMPORT
Import a Python module.

**Syntax:** `PY_IMPORT`

**Stack:** `module_name -> module_object`

### PY_CALL
Call a Python function.

**Syntax:** `PY_CALL`

**Stack:** `module_name func_name arg1 ... argN num_args -> result`

### PY_GETATTR
Get an attribute from a Python object.

**Syntax:** `PY_GETATTR`

**Stack:** `obj attr_name -> value`

### PY_SETATTR
Set an attribute on a Python object.

**Syntax:** `PY_SETATTR`

**Stack:** `obj attr_name value ->`

### PY_CALL_METHOD
Call a method on a Python object.

**Syntax:** `PY_CALL_METHOD`

**Stack:** `obj method_name arg1 ... argN num_args -> result`

---

## Exception Handling

### TRY_BEGIN
Begin an exception handler block.

**Syntax:** `TRY_BEGIN <exception_type> <handler_label>`

**Stack:** `->`

### TRY_END
End an exception handler block.

**Syntax:** `TRY_END`

**Stack:** `->`

### RAISE
Raise an exception.

**Syntax:** `RAISE`

**Stack:** `exception_type message ->`

---

## Built-in Functions

### BUILTIN_PRINT
Print a value without a newline.

**Syntax:** `BUILTIN_PRINT`

**Stack:** `value ->`

### BUILTIN_PRINTLN
Print a value with a newline.

**Syntax:** `BUILTIN_PRINTLN`

**Stack:** `value ->`

### BUILTIN_STR
Convert a value to a string.

**Syntax:** `BUILTIN_STR`

**Stack:** `value -> string`

### BUILTIN_LEN
Get the length of a string or list.

**Syntax:** `BUILTIN_LEN`

**Stack:** `value -> int64`

### BUILTIN_SQRT
Compute the square root.

**Syntax:** `BUILTIN_SQRT`

**Stack:** `float64 -> float64`

### BUILTIN_ROUND
Round a number to the nearest integer.

**Syntax:** `BUILTIN_ROUND`

**Stack:** `float64 -> int64`

### BUILTIN_FLOOR
Compute the floor of a number (alias for FLOOR).

**Syntax:** `BUILTIN_FLOOR`

**Stack:** `float64 -> int64`

### BUILTIN_CEIL
Compute the ceiling of a number (alias for CEIL).

**Syntax:** `BUILTIN_CEIL`

**Stack:** `float64 -> int64`

### BUILTIN_PI
Push the value of π onto the stack.

**Syntax:** `BUILTIN_PI`

**Stack:** `-> float64`

### ASSERT
Assert that a condition is true.

**Syntax:** `ASSERT`

**Stack:** `condition [message] ->`

---

## Optimized Instructions

These instructions are optimized versions that combine multiple operations for better performance.

### INC_LOCAL
Increment a local variable in-place.

**Syntax:** `INC_LOCAL <var_index>`

**Stack:** `->`

### DEC_LOCAL
Decrement a local variable in-place.

**Syntax:** `DEC_LOCAL <var_index>`

**Stack:** `->`

### ADD_CONST_I64
Add a constant to the top of the stack.

**Syntax:** `ADD_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### SUB_CONST_I64
Subtract a constant from the top of the stack.

**Syntax:** `SUB_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### MUL_CONST_I64
Multiply the top of the stack by a constant.

**Syntax:** `MUL_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### DIV_CONST_I64
Divide the top of the stack by a constant.

**Syntax:** `DIV_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### MOD_CONST_I64
Compute modulo of the top of the stack by a constant.

**Syntax:** `MOD_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### AND_CONST
Logical AND with a constant boolean.

**Syntax:** `AND_CONST <constant>`

**Stack:** `bool -> bool`

### OR_CONST
Logical OR with a constant boolean.

**Syntax:** `OR_CONST <constant>`

**Stack:** `bool -> bool`

### AND_CONST_I64
Bitwise AND with a constant.

**Syntax:** `AND_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### OR_CONST_I64
Bitwise OR with a constant.

**Syntax:** `OR_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### XOR_CONST_I64
Bitwise XOR with a constant.

**Syntax:** `XOR_CONST_I64 <constant>`

**Stack:** `int64 -> int64`

### LOAD2_ADD_I64
Fused load two variables and add them (combines LOAD, LOAD, ADD_I64).

**Syntax:** `LOAD2_ADD_I64 <var1> <var2>`

**Stack:** `-> int64`

### LOAD2_SUB_I64
Fused load two variables and subtract them (combines LOAD, LOAD, SUB_I64).

**Syntax:** `LOAD2_SUB_I64 <var1> <var2>`

**Stack:** `-> int64`

### LOAD2_MUL_I64
Fused load two variables and multiply them (combines LOAD, LOAD, MUL_I64).

**Syntax:** `LOAD2_MUL_I64 <var1> <var2>`

**Stack:** `-> int64`

### LOAD2_MOD_I64
Fused load two variables and compute modulo (combines LOAD, LOAD, MOD_I64).

**Syntax:** `LOAD2_MOD_I64 <var1> <var2>`

**Stack:** `-> int64`

### LOAD2_MUL_F64
Fused load two variables and multiply them as floats (combines LOAD, LOAD, MUL_F64).

**Syntax:** `LOAD2_MUL_F64 <var1> <var2>`

**Stack:** `-> float64`

### LOAD2_CMP_LT
Fused load two variables and compare less than (combines LOAD, LOAD, CMP_LT).

**Syntax:** `LOAD2_CMP_LT <var1> <var2>`

**Stack:** `-> bool`

### LOAD2_CMP_GT
Fused load two variables and compare greater than (combines LOAD, LOAD, CMP_GT).

**Syntax:** `LOAD2_CMP_GT <var1> <var2>`

**Stack:** `-> bool`

### LOAD2_CMP_LE
Fused load two variables and compare less than or equal (combines LOAD, LOAD, CMP_LE).

**Syntax:** `LOAD2_CMP_LE <var1> <var2>`

**Stack:** `-> bool`

### LOAD2_CMP_GE
Fused load two variables and compare greater than or equal (combines LOAD, LOAD, CMP_GE).

**Syntax:** `LOAD2_CMP_GE <var1> <var2>`

**Stack:** `-> bool`

### LOAD2_CMP_EQ
Fused load two variables and compare equality (combines LOAD, LOAD, CMP_EQ).

**Syntax:** `LOAD2_CMP_EQ <var1> <var2>`

**Stack:** `-> bool`

### LOAD2_CMP_NE
Fused load two variables and compare inequality (combines LOAD, LOAD, CMP_NE).

**Syntax:** `LOAD2_CMP_NE <var1> <var2>`

**Stack:** `-> bool`

---

## Directives

These are not executable instructions but are used during bytecode parsing to define program structure.

### .version
Specify the bytecode version.

**Syntax:** `.version <version_number>`

### .struct
Define a struct type.

**Syntax:** `.struct <name> <field1> <field2> ...`

### .func
Begin a function definition.

**Syntax:** `.func <name>`

### .arg
Declare a function argument.

**Syntax:** `.arg <name>`

### .local
Declare a local variable.

**Syntax:** `.local <name>`

### .end
End a function definition.

**Syntax:** `.end`

### .entry
Specify the entry point function.

**Syntax:** `.entry <function_name>`
