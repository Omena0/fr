(module
  ;; Runtime imports for complex operations
  (import "env" "print" (func $print (param i32 i32)))
  (import "env" "println" (func $println (param i32 i32)))
  (import "env" "str_concat" (func $str_concat (param i32 i32 i32 i32) (result i32 i32)))
  (import "env" "str_to_i64" (func $str_to_i64 (param i32 i32) (result i64)))
  (import "env" "str_to_f64" (func $str_to_f64 (param i32 i32) (result f64)))
  (import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))
  (import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))
  (import "env" "bool_to_str" (func $bool_to_str (param i32) (result i32 i32)))
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
  (memory (export "memory") 16 100)
  ;; Heap pointer for struct allocation
  (global $heap_ptr (mut i32) (i32.const 1024))
  (func $main (export "main")
    (local $l0 i32)
    (local $l0_len i32)
    (local $l1 i32)
    (local $l1_len i32)
    (local $l2 i32)
    (local $l2_len i32)
    (local $temp i32)
    (local $temp2 i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    ;; CONST_I64 1 2
    i64.const 1
    i64.const 2
    ;; STRUCT_NEW 0
    ;; STRUCT_NEW 0 (2 fields)
    global.get $heap_ptr
    global.get $heap_ptr
    i32.const 16
    i32.add
    global.set $heap_ptr
    local.set $temp
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=8
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=0
    local.get $temp
    ;; STORE 0
    local.set $l0
    ;; CONST_I64 3 4
    i64.const 3
    i64.const 4
    ;; STRUCT_NEW 0
    ;; STRUCT_NEW 0 (2 fields)
    global.get $heap_ptr
    global.get $heap_ptr
    i32.const 16
    i32.add
    global.set $heap_ptr
    local.set $temp
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=8
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=0
    local.get $temp
    ;; STORE 1
    local.set $l1
    ;; LIST_NEW
    call $list_new
    ;; LOAD 0
    local.get $l0
    ;; LIST_APPEND
    i64.extend_i32_u
    call $list_append
    ;; LOAD 1
    local.get $l1
    ;; LIST_APPEND
    i64.extend_i32_u
    call $list_append
    ;; STORE 2
    local.set $l2
    ;; LOAD 2
    local.get $l2
    ;; CONST_I64 0
    i64.const 0
    ;; LIST_GET
    call $list_get
    ;; STRUCT_GET 0
    ;; STRUCT_GET 0
    i32.wrap_i64
    i64.load offset=0
    ;; BUILTIN_PRINTLN
    call $i64_to_str
    call $println
    ;; LOAD 2
    local.get $l2
    ;; CONST_I64 0
    i64.const 0
    ;; LIST_GET
    call $list_get
    ;; STRUCT_GET 1
    ;; STRUCT_GET 1
    i32.wrap_i64
    i64.load offset=8
    ;; BUILTIN_PRINTLN
    call $i64_to_str
    call $println
    ;; LOAD 2
    local.get $l2
    ;; CONST_I64 1
    i64.const 1
    ;; LIST_GET
    call $list_get
    ;; STRUCT_GET 0
    ;; STRUCT_GET 0
    i32.wrap_i64
    i64.load offset=0
    ;; BUILTIN_PRINTLN
    call $i64_to_str
    call $println
    ;; LOAD 2
    local.get $l2
    ;; CONST_I64 1
    i64.const 1
    ;; LIST_GET
    call $list_get
    ;; STRUCT_GET 1
    ;; STRUCT_GET 1
    i32.wrap_i64
    i64.load offset=8
    ;; BUILTIN_PRINTLN
    call $i64_to_str
    call $println
    ;; RETURN_VOID
    return
  )
)