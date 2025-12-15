(module
  ;; Runtime imports for complex operations
  (import "env" "print" (func $print (param i32 i32)))
  (import "env" "println" (func $println (param i32 i32)))
  (import "env" "runtime_error" (func $runtime_error (param i32 i32 i32 i32 i32)))
  (import "env" "str_concat" (func $str_concat (param i32 i32 i32 i32) (result i32 i32)))
  (import "env" "str_to_i64" (func $str_to_i64 (param i32 i32) (result i64)))
  (import "env" "str_to_f64" (func $str_to_f64 (param i32 i32) (result f64)))
  (import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))
  (import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))
  (import "env" "bool_to_str" (func $bool_to_str (param i64) (result i32 i32)))
  (import "env" "list_to_str" (func $list_to_str (param i32) (result i32 i32)))
  (import "env" "set_to_str" (func $set_to_str (param i32) (result i32 i32)))
  (import "env" "str_upper" (func $str_upper (param i32 i32) (result i32 i32)))
  (import "env" "str_lower" (func $str_lower (param i32 i32) (result i32 i32)))
  (import "env" "str_strip" (func $str_strip (param i32 i32) (result i32 i32)))
  (import "env" "str_replace" (func $str_replace (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "env" "str_get" (func $str_get (param i32 i32 i64) (result i32 i32)))
  (import "env" "str_contains" (func $str_contains (param i32 i32 i32 i32) (result i32)))
  (import "env" "str_eq" (func $str_eq (param i32 i32 i32 i32) (result i32)))
  (import "env" "str_join" (func $str_join (param i32 i32 i32) (result i32 i32)))
  (import "env" "str_split" (func $str_split (param i32 i32 i32 i32) (result i32)))
  (import "env" "sqrt" (func $sqrt (param f64) (result f64)))
  (import "env" "list_new" (func $list_new (result i32)))
  (import "env" "list_append" (func $list_append (param i32 i64) (result i32)))
  (import "env" "list_get" (func $list_get (param i32 i64) (result i64)))
  (import "env" "list_set" (func $list_set (param i32 i64 i64) (result i32)))
  (import "env" "list_len" (func $list_len (param i32) (result i64)))
  (import "env" "list_contains" (func $list_contains (param i32 i64) (result i32)))
  (import "env" "list_pop" (func $list_pop (param i32) (result i32 i64)))
  (import "env" "set_new" (func $set_new (result i32)))
  (import "env" "set_add" (func $set_add (param i32 i64) (result i32)))
  (import "env" "set_remove" (func $set_remove (param i32 i64) (result i32)))
  (import "env" "set_contains" (func $set_contains (param i32 i64) (result i32)))
  (import "env" "set_len" (func $set_len (param i32) (result i64)))
  (import "env" "round_f64" (func $round_f64 (param f64) (result f64)))
  (import "env" "floor_f64" (func $floor_f64 (param f64) (result f64)))
  (import "env" "ceil_f64" (func $ceil_f64 (param f64) (result f64)))
  (import "env" "file_open" (func $file_open (param i32 i32 i32 i32) (result i32)))
  (import "env" "file_read" (func $file_read (param i32) (result i32 i32)))
  (import "env" "file_write" (func $file_write (param i32 i32 i32)))
  (import "env" "file_close" (func $file_close (param i32)))
  (import "env" "exit_process" (func $exit_process (param i32)))
  (import "env" "sleep" (func $sleep (param f64)))
  (memory (export "memory") 64 1024)
  ;; Heap pointer for struct allocation
  (global $heap_ptr (mut i32) (i32.const 1024))
  ;; Exception handling globals
  (global $exception_active (mut i32) (i32.const 0))
  (func $main (export "main")
    (local $l0 i32)
    (local $l0_len i32)
    (local $l1 i32)
    (local $l1_len i32)
    (local $l2 i64)
    (local $l2_len i32)
    (local $temp i32)
    (local $temp2 i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    (local $temp_i32_0 i32)
    (local $temp_i64_0 i64)
    (local $temp_f64_0 f64)
    (local $temp_i32_1 i32)
    (local $temp_i64_1 i64)
    (local $temp_f64_1 f64)
    (local $temp_i32_2 i32)
    (local $temp_i64_2 i64)
    (local $temp_f64_2 f64)
    (local $temp_i32_3 i32)
    (local $temp_i64_3 i64)
    (local $temp_f64_3 f64)
    (local $temp_i32_4 i32)
    (local $temp_i64_4 i64)
    (local $temp_f64_4 f64)
    (local $temp_i32_5 i32)
    (local $temp_i64_5 i64)
    (local $temp_f64_5 f64)
    (local $temp_i32_6 i32)
    (local $temp_i64_6 i64)
    (local $temp_f64_6 f64)
    (local $temp_i32_7 i32)
    (local $temp_i64_7 i64)
    (local $temp_f64_7 f64)
    (local $temp_i32_8 i32)
    (local $temp_i64_8 i64)
    (local $temp_f64_8 f64)
    (local $temp_i32_9 i32)
    (local $temp_i64_9 i64)
    (local $temp_f64_9 f64)
    ;; LIST_NEW
    call $list_new
    ;; CONST_STR "  a:b  "
    i32.const 0  ;; string:   a:b  ...
    i32.const 7
    ;; LIST_APPEND
    local.set $temp
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp
    i64.extend_i32_u
    i64.const 32
    i64.shl
    local.get $temp_i64
    i64.or
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    ;; STORE 0
    local.set $l0
    ;; LOAD 0
    local.get $l0
    ;; CONST_I64 0
    i64.const 0
    ;; LIST_GET
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_get
    ;; STR_STRIP
    local.set $temp_i64_0
    local.get $temp_i64_0
    i32.wrap_i64
    local.get $temp_i64_0
    i64.const 32
    i64.shr_u
    i32.wrap_i64
    call $str_strip
    ;; STORE 2
    local.set $temp
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp
    i64.extend_i32_u
    i64.const 32
    i64.shl
    local.get $temp_i64
    i64.or
    local.set $l2
    ;; LOAD 2
    local.get $l2
    ;; CONST_STR ":"
    i32.const 7  ;; string: :...
    i32.const 1
    ;; STR_SPLIT
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.set $temp_i64_0
    local.get $temp_i64_0
    i32.wrap_i64
    local.get $temp_i64_0
    i64.const 32
    i64.shr_u
    i32.wrap_i64
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $str_split
    ;; STORE 1
    local.set $l1
    ;; LOAD 1
    local.get $l1
    ;; BUILTIN_LEN
    local.set $temp_i32_0
    local.get $temp_i32_0
    call $list_len
    ;; BUILTIN_PRINTLN
    local.set $temp_i64_0
    local.get $temp_i64_0
    call $i64_to_str
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $println
    ;; RETURN_VOID
    return
  )
  (data (i32.const 0) "\20\20\61\3a\62\20\20")
  (data (i32.const 7) "\3a")
)