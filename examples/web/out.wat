(module
  ;; Runtime imports for complex operations
  (import "env" "dom_create" (func $dom_create (param i32 i32) (result i32)))
  (import "env" "dom_set_text" (func $dom_set_text (param i32 i32 i32)))
  (import "env" "dom_append" (func $dom_append (param i32 i32)))
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
  (func $element (param $p0 i32) (param $p0_len i32) (param $p1 i32) (param $p1_len i32) (param $p2 i32) (result i32)
    (local $l0 i32)
    (local $l0_len i32)
    (local $l1 i32)
    (local $l1_len i32)
    (local $l2 i64)
    (local $l2_len i32)
    (local $l3 i64)
    (local $l3_len i32)
    (local $temp i32)
    (local $temp2 i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    ;; LOAD 0
    local.get $p0
    local.get $p0_len
    ;; CALL dom_create 1
    call $dom_create
    ;; STORE 4
    local.set $l1
    ;; LOAD 4 1
    local.get $l1
    local.get $p1
    local.get $p1_len
    ;; CALL dom_set_text 2
    call $dom_set_text
    ;; LIST_NEW
    call $list_new
    ;; STORE 3
    local.set $l0
    ;; STORE_CONST_I64 6 0
    i64.const 0
    local.set $l3
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 6 2
        local.get $l3
        local.get $p2
        ;; BUILTIN_LEN
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 2 6
        local.get $p2
        local.get $l3
        ;; LIST_GET
        call $list_get
        ;; STORE 5
        local.set $l2
        ;; LOAD 4 5
        local.get $l1
        local.get $l2
        ;; STRUCT_GET 0
        ;; STRUCT_GET 0
        i32.wrap_i64
        i64.load offset=0
        ;; CALL dom_append 2
        i32.wrap_i64
        call $dom_append
        ;; LOAD 3 5
        local.get $l0
        local.get $l2
        ;; LIST_APPEND
        call $list_append
        ;; STORE 3
        local.set $l0
        ;; INC_LOCAL 6
        local.get $l3
        i64.const 1
        i64.add
        local.set $l3
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; LOAD 4 0 3
    local.get $l1
    local.get $p0
    local.get $p0_len
    local.get $l0
    ;; STRUCT_NEW 0
    ;; STRUCT_NEW 0 (3 fields)
    global.get $heap_ptr
    global.get $heap_ptr
    i32.const 24
    i32.add
    global.set $heap_ptr
    local.set $temp
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=16
    i64.extend_i32_u
    i64.const 32
    i64.shl
    local.set $temp_i64
    i64.extend_i32_u
    local.get $temp_i64
    i64.or
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=8
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp
    local.get $temp_i64
    i64.store offset=0
    local.get $temp
    ;; RETURN
    return
    unreachable
  )
  (func $main (export "main")
    (local $l0 i32)
    (local $l0_len i32)
    (local $temp i32)
    (local $temp2 i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    ;; CONST_STR "div" "Div 1"
    i32.const 0  ;; string: div...
    i32.const 3
    i32.const 3  ;; string: Div 1...
    i32.const 5
    ;; LIST_NEW
    call $list_new
    ;; CONST_STR "h1" "h1"
    i32.const 8  ;; string: h1...
    i32.const 2
    i32.const 8  ;; string: h1...
    i32.const 2
    ;; LIST_NEW
    call $list_new
    ;; CALL element 3
    call $element
    ;; LIST_APPEND
    i64.extend_i32_u
    call $list_append
    ;; CALL element 3
    call $element
    ;; STORE 0
    local.set $l0
    ;; RETURN_VOID
    return
    unreachable
  )
  (data (i32.const 0) "\64\69\76")
  (data (i32.const 3) "\44\69\76\20\31")
  (data (i32.const 8) "\68\31")
)