(module
  ;; Runtime imports for complex operations
  (import "env" "dom_create" (func $dom_create (param i32 i32) (result i32)))
  (import "env" "dom_get_body" (func $dom_get_body (result i32)))
  (import "env" "dom_set_text" (func $dom_set_text (param i32 i32 i32)))
  (import "env" "dom_append" (func $dom_append (param i32 i32)))
  (import "env" "dom_add_class" (func $dom_add_class (param i32 i32 i32)))
  (import "env" "dom_set_style" (func $dom_set_style (param i32 i32 i32 i32 i32)))
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
  (import "env" "list_from_array" (func $list_from_array (param i32 i64) (result i32)))
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
  ;; Exception handling globals
  (global $exception_active (mut i32) (i32.const 0))
  ;; Global variables
  (global $g0 (mut i32) (i32.const 0))
  (global $g1 (mut i64) (i64.const 0))
  (global $g2 (mut i64) (i64.const 0))
  (global $g3 (mut i64) (i64.const 0))
  (global $g4 (mut i64) (i64.const 0))
  (global $g5 (mut i64) (i64.const 0))
  (global $g6 (mut i64) (i64.const 0))
  (global $g7 (mut i64) (i64.const 0))
  (global $g8 (mut i64) (i64.const 0))
  (func $element (param $p0 i32) (param $p0_len i32) (param $p1 i32) (param $p1_len i32) (param $p2 i32) (result i32)
    (local $l0 i32)
    (local $l1 i32)
    (local $l2 i32)
    (local $l3 i64)
    (local $l4 i64)
    (local $temp i32)
    (local $temp_i64 i64)
    (local $temp_i32_0 i32)
    (local $temp_i64_0 i64)
    (local $temp_i32_1 i32)
    ;; LOAD 0
    local.get $p0
    local.get $p0_len
    ;; CALL dom_create 1
    ;; OPTIMIZED CALL SKIP SHUFFLE
    call $dom_create
    ;; STORE 5
    local.set $l2
    ;; LOAD 5
    local.get $l2
    ;; LOAD 1
    local.get $p1
    local.get $p1_len
    ;; CALL dom_set_text 2
    ;; OPTIMIZED CALL SKIP SHUFFLE
    call $dom_set_text
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; STORE 4
    local.set $l1
    ;; CONST_I64 0
    i64.const 0
    ;; STORE 7
    local.set $l4
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 7
        local.get $l4
        ;; LOAD 2
        local.get $p2
        ;; BUILTIN_LEN
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 2
        local.get $p2
        ;; LOAD 7
        local.get $l4
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list', None]
        call $list_get
        ;; STORE 6
        local.set $l3
        ;; LOAD 5
        local.get $l2
        ;; LOAD 6
        local.get $l3
        ;; STRUCT_GET 0
        i32.wrap_i64
        i32.const 0
        i32.add
        i64.load
        ;; CALL dom_append 2
        local.set $temp_i64_0
        local.set $temp_i32_0
        local.get $temp_i32_0
        local.get $temp_i64_0
        i32.wrap_i64
        call $dom_append
        ;; LOAD 4
        local.get $l1
        ;; LOAD 6
        local.get $l3
        ;; LIST_APPEND
        call $list_append
        ;; STORE 4
        local.set $l1
        ;; LOAD 7
        local.get $l4
        ;; CONST_I64 1
        i64.const 1
        ;; ADD_I64
        i64.add
        ;; STORE 7
        local.set $l4
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; LOAD 5
    local.get $l2
    ;; LOAD 0
    local.get $p0
    local.get $p0_len
    ;; LOAD 4
    local.get $l1
    ;; STRUCT_NEW 0
    global.get $heap_ptr
    local.tee $temp_i32_0
    i32.const 24
    i32.add
    global.set $heap_ptr
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store offset=16
    local.set $temp_i32_1
    i64.extend_i32_u
    local.get $temp_i32_1
    i64.extend_i32_u
    i64.const 32
    i64.shl
    i64.or
    local.set $temp_i64_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    i64.store offset=8
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store offset=0
    local.get $temp_i32_0
    ;; STORE 3
    local.set $l0
    ;; LOAD_GLOBAL 8
    global.get $g8
    ;; LOAD 3
    local.get $l0
    ;; LIST_APPEND
    local.set $temp
    i32.wrap_i64
    local.get $temp
    i64.extend_i32_u
    call $list_append
    ;; STORE_GLOBAL 8
    i64.extend_i32_u
    global.set $g8
    ;; CALL dom_get_body 0
    ;; OPTIMIZED CALL SKIP SHUFFLE
    call $dom_get_body
    ;; LOAD 5
    local.get $l2
    ;; CALL dom_append 2
    ;; OPTIMIZED CALL SKIP SHUFFLE
    call $dom_append
    ;; LOAD 3
    local.get $l0
    ;; RETURN
    return
    unreachable
  )
  (func $styles (param $p0 i32) (param $p1 i32) (result i32)
    (local $l0 i64)
    (local $l1 i64)
    (local $l2 i64)
    (local $l3 i64)
    (local $temp i32)
    (local $temp_i32_0 i32)
    (local $temp_i64_0 i64)
    (local $temp_i64_1 i64)
    (local $temp_i64_2 i64)
    (local $call_temp_i32_0 i32)
    (local $call_temp_i64_0 i64)
    (local $call_temp_i32_1 i32)
    ;; LOAD 1
    local.get $p1
    ;; BUILTIN_PRINTLN
    call $list_to_str
    call $println
    ;; CONST_I64 0
    i64.const 0
    ;; STORE 3
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 3
        local.get $l1
        ;; LOAD 1
        local.get $p1
        ;; BUILTIN_LEN
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 1
        local.get $p1
        ;; LOAD 3
        local.get $l1
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list', None]
        call $list_get
        ;; STORE 2
        local.set $l0
        ;; LOAD 2
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
        i32.const 1
        ;; STR_SPLIT
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        ;; CONST_I64 0
        i64.const 0
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list_str', None]
        call $list_get
        ;; STR_STRIP
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        ;; STORE 4
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l2
        ;; LOAD 2
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
        i32.const 1
        ;; STR_SPLIT
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        ;; CONST_I64 1
        i64.const 1
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list_str', None]
        call $list_get
        ;; STR_STRIP
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        ;; STORE 5
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l3
        ;; LOAD 0
        local.get $p0
        ;; STRUCT_GET 0
        local.set $temp_i32_0
        local.get $temp_i32_0
        i32.const 0
        i32.add
        i64.load
        ;; LOAD 4
        local.get $l2
        ;; LOAD 5
        local.get $l3
        ;; CALL dom_set_style 3
        local.set $temp_i64_0
        local.set $temp_i64_1
        local.set $temp_i64_2
        local.get $temp_i64_2
        i32.wrap_i64
        local.get $temp_i64_1
        i32.wrap_i64
        local.get $temp_i64_1
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $temp_i64_0
        i32.wrap_i64
        local.get $temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $dom_set_style
        ;; LOAD 3
        local.get $l1
        ;; CONST_I64 1
        i64.const 1
        ;; ADD_I64
        i64.add
        ;; STORE 3
        local.set $l1
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; LOAD 0
    local.get $p0
    ;; RETURN
    return
    unreachable
  )
  (func $class (param $p0 i32) (param $p0_len i32) (param $p1 i32)
    (local $l0 i64)
    (local $l1 i64)
    (local $l2 i64)
    (local $l3 i64)
    (local $temp i32)
    (local $temp2 i32)
    (local $call_temp_i32_0 i32)
    (local $call_temp_i64_0 i64)
    (local $call_temp_i32_1 i32)
    ;; CONST_I64 0
    i64.const 0
    ;; STORE 3
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 3
        local.get $l1
        ;; LOAD 1
        local.get $p1
        ;; BUILTIN_LEN
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 1
        local.get $p1
        ;; LOAD 3
        local.get $l1
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list', None]
        call $list_get
        ;; STORE 2
        local.set $l0
        ;; LOAD 2
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
        i32.const 1
        ;; STR_SPLIT
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        ;; CONST_I64 0
        i64.const 0
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list_str', None]
        call $list_get
        ;; STR_STRIP
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        ;; STORE 4
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l2
        ;; LOAD 2
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
        i32.const 1
        ;; STR_SPLIT
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        ;; CONST_I64 1
        i64.const 1
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list_str', None]
        call $list_get
        ;; STR_STRIP
        local.set $call_temp_i64_0
        local.get $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        ;; STORE 5
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l3
        ;; CONST_STR "."
        i32.const 1  ;; string: ....
        i32.const 1
        ;; LOAD 0
        local.get $p0
        local.get $p0_len
        ;; ADD_STR
        local.set $temp2
        local.set $temp
        local.get $temp
        local.get $temp2
        call $str_concat
        ;; LOAD 4
        local.get $l2
        ;; LOAD 5
        local.get $l3
        ;; CALL css_add_rule 3
        ;; LOAD 3
        local.get $l1
        ;; CONST_I64 1
        i64.const 1
        ;; ADD_I64
        i64.add
        ;; STORE 3
        local.set $l1
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; RETURN_VOID
    return
  )
  (func $classes (param $p0 i32) (param $p1 i32) (result i32)
    (local $l0 i64)
    (local $l1 i64)
    (local $temp_i32_0 i32)
    (local $temp_i64_0 i64)
    (local $temp_i64_1 i64)
    ;; CONST_I64 0
    i64.const 0
    ;; STORE 3
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 3
        local.get $l1
        ;; LOAD 1
        local.get $p1
        ;; BUILTIN_LEN
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 1
        local.get $p1
        ;; LOAD 3
        local.get $l1
        ;; LIST_GET
        ;; LIST_GET extended_stack=['list', None]
        call $list_get
        ;; STORE 2
        local.set $l0
        ;; LOAD 0
        local.get $p0
        ;; STRUCT_GET 0
        local.set $temp_i32_0
        local.get $temp_i32_0
        i32.const 0
        i32.add
        i64.load
        ;; LOAD 2
        local.get $l0
        ;; CALL dom_add_class 2
        local.set $temp_i64_0
        local.set $temp_i64_1
        local.get $temp_i64_1
        i32.wrap_i64
        local.get $temp_i64_0
        i32.wrap_i64
        local.get $temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $dom_add_class
        ;; LOAD 3
        local.get $l1
        ;; CONST_I64 1
        i64.const 1
        ;; ADD_I64
        i64.add
        ;; STORE 3
        local.set $l1
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; LOAD 0
    local.get $p0
    ;; RETURN
    return
    unreachable
  )
  (func $main (export "main")
    (local $l0 i32)
    (local $l1 i32)
    (local $l2 i32)
    (local $l3 i32)
    (local $temp_i64 i64)
    (local $temp_i32_0 i32)
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; STORE_GLOBAL 4
    i64.extend_i32_u
    global.set $g4
    ;; CONST_STR "badge"
    i32.const 2  ;; string: badge...
    i32.const 5
    ;; LIST_NEW_STR 5 "color: white" "padding: 8px 20px" "border-radius: 20px" "margin: 5px" "display: inline-block"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 51539607559
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 73014444051
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 81604378660
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 47244640311
    i64.store
    local.get $temp_i32_0
    i32.const 32
    i32.add
    i64.const 90194313282
    i64.store
    local.get $temp_i32_0
    i64.const 5
    call $list_from_array
    ;; CALL class 2
    call $class
    ;; CONST_STR "feature-card"
    i32.const 87  ;; string: feature-card...
    i32.const 12
    ;; LIST_NEW_STR 7 "background: white" "padding: 30px" "border-radius: 15px" "flex: 1" "margin: 10px" "min-width: 250px" "box-shadow: 0 10px 30px rgba(240, 147, 251, 0.1)"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 73014444131
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 55834574964
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 81604378753
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 30064771220
    i64.store
    local.get $temp_i32_0
    i32.const 32
    i32.add
    i64.const 51539607707
    i64.store
    local.get $temp_i32_0
    i32.const 40
    i32.add
    i64.const 68719476903
    i64.store
    local.get $temp_i32_0
    i32.const 48
    i32.add
    i64.const 206158430391
    i64.store
    local.get $temp_i32_0
    i64.const 7
    call $list_from_array
    ;; CALL class 2
    call $class
    ;; CONST_STR "section-title"
    i32.const 231  ;; string: section-title...
    i32.const 13
    ;; LIST_NEW_STR 3 "text-align: center" "color: #333" "margin-bottom: 30px"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 77309411572
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 47244640518
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 81604378897
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL class 2
    call $class
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h1"
    i32.const 295  ;; string: h1...
    i32.const 2
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "🚀 "
    i32.const 301  ;; string: 🚀 ...
    i32.const 5
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "font-size: 4rem"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 64424509746
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "FrScript"
    i32.const 321  ;; string: FrScript...
    i32.const 8
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 4 "font-size: 4rem" "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)" "-webkit-background-clip: text" "-webkit-text-fill-color: transparent"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 64424509746
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 261993005385
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 124554051974
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 154618823075
    i64.store
    local.get $temp_i32_0
    i64.const 4
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "margin: 0" "animation: pulse 2s infinite"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 38654706119
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 120259084752
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "p"
    i32.const 492  ;; string: p...
    i32.const 1
    ;; CONST_STR "A fast, modern bytecode-compiled language"
    i32.const 493  ;; string: A fast, modern bytec...
    i32.const 41
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 3 "font-size: 1.5rem" "color: #666" "margin-top: 10px"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 73014444566
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 68719477298
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "⚡ Fast"
    i32.const 578  ;; string: ⚡ Fast...
    i32.const 8
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "badge"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STR 4 "background: #667eea" "color: white" "padding: 8px 20px" "border-radius: 20px"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 81604379210
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 51539607559
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 73014444051
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 81604378660
    i64.store
    local.get $temp_i32_0
    i64.const 4
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "🎯 Simple"
    i32.const 605  ;; string: 🎯 Simple...
    i32.const 11
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "badge"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STR 4 "background: #764ba2" "color: white" "padding: 8px 20px" "border-radius: 20px"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 81604379240
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 51539607559
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 73014444051
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 81604378660
    i64.store
    local.get $temp_i32_0
    i64.const 4
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "🌐 Web-Ready"
    i32.const 635  ;; string: 🌐 Web-Ready...
    i32.const 14
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "badge"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STR 4 "background: #f093fb" "color: white" "padding: 8px 20px" "border-radius: 20px"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 81604379273
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 51539607559
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 73014444051
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 81604378660
    i64.store
    local.get $temp_i32_0
    i64.const 4
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 3
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 16
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 5 "margin-top: 30px" "display: flex" "gap: 15px" "justify-content: center" "flex-wrap: wrap"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 68719477404
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 55834575532
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 38654706361
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 98784248514
    i64.store
    local.get $temp_i32_0
    i32.const 32
    i32.add
    i64.const 64424510169
    i64.store
    local.get $temp_i32_0
    i64.const 5
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 3
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 16
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 3 "text-align: center" "padding: 80px 20px" "background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%)"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 77309411572
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 77309412072
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 261993005818
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; STORE 3
    local.set $l3
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h2"
    i32.const 823  ;; string: h2...
    i32.const 2
    ;; CONST_STR "✨ Features"
    i32.const 825  ;; string: ✨ Features...
    i32.const 12
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "section-title"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 55834575079
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STR 2 "font-size: 2.5rem" "text-align: center"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 73014444869
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 77309411572
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h3"
    i32.const 854  ;; string: h3...
    i32.const 2
    ;; CONST_STR "🔥 Blazing Fast"
    i32.const 856  ;; string: 🔥 Blazing Fast...
    i32.const 17
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "color: #667eea" "margin: 0"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543017
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 38654706119
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "p"
    i32.const 492  ;; string: p...
    i32.const 1
    ;; CONST_STR "Compiles to optimized bytecode for maximum performance"
    i32.const 887  ;; string: Compiles to optimize...
    i32.const 54
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #666"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "feature-card"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h3"
    i32.const 854  ;; string: h3...
    i32.const 2
    ;; CONST_STR "🎨 Clean Syntax"
    i32.const 941  ;; string: 🎨 Clean Syntax...
    i32.const 17
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "color: #764ba2" "margin: 0"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543102
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 38654706119
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "p"
    i32.const 492  ;; string: p...
    i32.const 1
    ;; CONST_STR "Write beautiful, readable code with modern syntax"
    i32.const 972  ;; string: Write beautiful, rea...
    i32.const 49
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #666"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "feature-card"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h3"
    i32.const 854  ;; string: h3...
    i32.const 2
    ;; CONST_STR "🌍 Cross-Platform"
    i32.const 1021  ;; string: 🌍 Cross-Platform...
    i32.const 19
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "color: #f093fb" "margin: 0"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543184
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 38654706119
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "p"
    i32.const 492  ;; string: p...
    i32.const 1
    ;; CONST_STR "Run on native, Python runtime, or compile to WebAssembly"
    i32.const 1054  ;; string: Run on native, Pytho...
    i32.const 56
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #666"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "feature-card"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STACK 3
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 16
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 3
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 5 "display: flex" "flex-wrap: wrap" "justify-content: center" "max-width: 1000px" "margin: 0 auto"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 55834575532
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 64424510169
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 98784248514
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 73014445142
    i64.store
    local.get $temp_i32_0
    i32.const 32
    i32.add
    i64.const 60129543271
    i64.store
    local.get $temp_i32_0
    i64.const 5
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "padding: 60px 20px" "background: #f8f9ff"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 77309412469
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 81604379783
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; STORE 1
    local.set $l1
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "h2"
    i32.const 823  ;; string: h2...
    i32.const 2
    ;; CONST_STR "💻 Simple  and  Elegant"
    i32.const 1178  ;; string: 💻 Simple  and  Elega...
    i32.const 25
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "section-title"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 55834575079
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL classes 2
    call $classes
    ;; LIST_NEW_STR 2 "font-size: 2rem" "text-align: center"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 64424510643
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 77309411572
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "pre"
    i32.const 1218  ;; string: pre...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "void"
    i32.const 1221  ;; string: void...
    i32.const 4
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #569CD6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543369
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR " "
    i32.const 1239  ;; string:  ...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "main"
    i32.const 1240  ;; string: main...
    i32.const 4
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #DCDCAA"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "("
    i32.const 1258  ;; string: (...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ")"
    i32.const 1273  ;; string: )...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR " "
    i32.const 1239  ;; string:  ...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "{"
    i32.const 1274  ;; string: {...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\n"
    i32.const 1275  ;; string: \n...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "    "
    i32.const 1276  ;; string:     ...
    i32.const 4
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "println"
    i32.const 1280  ;; string: println...
    i32.const 7
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #DCDCAA"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "("
    i32.const 1258  ;; string: (...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\"Hello, World!\""
    i32.const 1301  ;; string: "Hello, World!"...
    i32.const 15
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #CE9178"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543460
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ")"
    i32.const 1273  ;; string: )...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\n\n"
    i32.const 1330  ;; string: \n\n...
    i32.const 2
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "    "
    i32.const 1276  ;; string:     ...
    i32.const 4
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "for"
    i32.const 1332  ;; string: for...
    i32.const 3
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #C586C0"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543479
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR " "
    i32.const 1239  ;; string:  ...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "("
    i32.const 1258  ;; string: (...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "i"
    i32.const 1349  ;; string: i...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #9CDCFE"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543494
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ".."
    i32.const 1364  ;; string: .....
    i32.const 2
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "5"
    i32.const 1366  ;; string: 5...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #B5CEA8"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543511
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ")"
    i32.const 1273  ;; string: )...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR " "
    i32.const 1239  ;; string:  ...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "{"
    i32.const 1274  ;; string: {...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\n"
    i32.const 1275  ;; string: \n...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "        "
    i32.const 1381  ;; string:         ...
    i32.const 8
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "println"
    i32.const 1280  ;; string: println...
    i32.const 7
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #DCDCAA"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "("
    i32.const 1258  ;; string: (...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #179fff"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543533
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\"Count: \""
    i32.const 1403  ;; string: "Count: "...
    i32.const 9
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #CE9178"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543460
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR " + "
    i32.const 1412  ;; string:  + ...
    i32.const 3
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "str"
    i32.const 1415  ;; string: str...
    i32.const 3
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #DCDCAA"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "("
    i32.const 1258  ;; string: (...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "i"
    i32.const 1349  ;; string: i...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #9CDCFE"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543494
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ")"
    i32.const 1273  ;; string: )...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR ")"
    i32.const 1273  ;; string: )...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #179fff"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543533
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\n"
    i32.const 1275  ;; string: \n...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "    "
    i32.const 1276  ;; string:     ...
    i32.const 4
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "}"
    i32.const 1418  ;; string: }...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #da70d6"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "\n"
    i32.const 1275  ;; string: \n...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; CONST_STR "span"
    i32.const 297  ;; string: span...
    i32.const 4
    ;; CONST_STR "}"
    i32.const 1418  ;; string: }...
    i32.const 1
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 1 "color: #ffd700"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 40
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 312
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 304
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 296
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 288
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 280
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 272
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 264
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 256
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 248
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 240
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 232
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 224
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 216
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 208
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 200
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 192
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 184
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 176
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 168
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 160
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 152
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 144
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 136
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 128
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 120
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 112
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 104
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 96
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 88
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 80
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 72
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 64
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 56
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 48
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 40
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 32
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 24
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 16
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 40
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 12 "background: #1E1E1E" "color: #D4D4D4" "padding: 30px" "border-radius: 15px" "font-family: monospace" "font-size: 1.1rem" "overflow-x: auto" "max-width: 600px" "margin: 0 auto" "box-shadow: 0 20px 40px rgba(0,0,0,0.2)" "white-space: pre" "text-align: left"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 81604380043
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 60129543582
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 55834574964
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 81604378753
    i64.store
    local.get $temp_i32_0
    i32.const 32
    i32.add
    i64.const 94489281964
    i64.store
    local.get $temp_i32_0
    i32.const 40
    i32.add
    i64.const 73014445506
    i64.store
    local.get $temp_i32_0
    i32.const 48
    i32.add
    i64.const 68719478227
    i64.store
    local.get $temp_i32_0
    i32.const 56
    i32.add
    i64.const 68719478243
    i64.store
    local.get $temp_i32_0
    i32.const 64
    i32.add
    i64.const 60129543271
    i64.store
    local.get $temp_i32_0
    i32.const 72
    i32.add
    i64.const 167503726067
    i64.store
    local.get $temp_i32_0
    i32.const 80
    i32.add
    i64.const 68719478298
    i64.store
    local.get $temp_i32_0
    i32.const 88
    i32.add
    i64.const 68719478314
    i64.store
    local.get $temp_i32_0
    i64.const 12
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 2
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "padding: 60px 20px" "background: white"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 77309412469
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 73014444131
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; STORE 0
    local.set $l0
    ;; CONST_STR "div"
    i32.const 292  ;; string: div...
    i32.const 3
    ;; CONST_STR ""
    i32.const 295  ;; string: ...
    i32.const 0
    ;; CONST_STR "p"
    i32.const 492  ;; string: p...
    i32.const 1
    ;; CONST_STR "🌟 Built with FrScript WASM backend"
    i32.const 1594  ;; string: 🌟 Built with FrScrip...
    i32.const 37
    ;; LIST_NEW_STACK 0
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 0
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 2 "margin: 0" "font-size: 1.1rem"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 38654706119
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 73014445506
    i64.store
    local.get $temp_i32_0
    i64.const 2
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; LIST_NEW_STACK 1
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    local.get $temp_i64
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    ;; CALL element 3
    call $element
    ;; LIST_NEW_STR 4 "text-align: center" "padding: 40px 20px" "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)" "color: white"
    global.get $scratchpad_ptr
    local.set $temp_i32_0
    local.get $temp_i32_0
    i64.const 77309411572
    i64.store
    local.get $temp_i32_0
    i32.const 8
    i32.add
    i64.const 77309412959
    i64.store
    local.get $temp_i32_0
    i32.const 16
    i32.add
    i64.const 261993005385
    i64.store
    local.get $temp_i32_0
    i32.const 24
    i32.add
    i64.const 51539607559
    i64.store
    local.get $temp_i32_0
    i64.const 4
    call $list_from_array
    ;; CALL styles 2
    call $styles
    ;; STORE 2
    local.set $l2
    ;; RETURN_VOID
    return
  )
  ;; Heap pointer for struct allocation
  (global $heap_ptr (mut i32) (i32.const 5760))
  ;; Scratchpad pointer for list creation
  (global $scratchpad_ptr i32 (i32.const 1664))
  (data (i32.const 0) ":.badgecolor: whitepadding: 8px 20pxborder-radius: 20pxmargin: 5pxdisplay: inline-blockfeature-cardbackground: whitepadding: 30pxborder-radius: 15pxflex: 1margin: 10pxmin-width: 250pxbox-shadow: 0 10px 30px rgba(240, 147, 251, 0.1)section-titletext-align: centercolor: #333margin-bottom: 30pxdivh1span\f0\9f\9a\80 font-size: 4remFrScriptbackground: linear-gradient(135deg, #667eea 0%, #764ba2 100%)-webkit-background-clip: text-webkit-text-fill-color: transparentmargin: 0animation: pulse 2s infinitepA fast, modern bytecode-compiled languagefont-size: 1.5remcolor: #666margin-top: 10px\e2\9a\a1 Fastbackground: #667eea\f0\9f\8e\af Simplebackground: #764ba2\f0\9f\8c\90 Web-Readybackground: #f093fbmargin-top: 30pxdisplay: flexgap: 15pxjustify-content: centerflex-wrap: wrappadding: 80px 20pxbackground: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%)h2\e2\9c\a8 Featuresfont-size: 2.5remh3\f0\9f\94\a5 Blazing Fastcolor: #667eeaCompiles to optimized bytecode for maximum performance\f0\9f\8e\a8 Clean Syntaxcolor: #764ba2Write beautiful, readable code with modern syntax\f0\9f\8c\8d Cross-Platformcolor: #f093fbRun on native, Python runtime, or compile to WebAssemblymax-width: 1000pxmargin: 0 autopadding: 60px 20pxbackground: #f8f9ff\f0\9f\92\bb Simple  and  Elegantfont-size: 2remprevoidcolor: #569CD6 maincolor: #DCDCAA(color: #ffd700){\n    printlncolor: #da70d6\"Hello, World!\"color: #CE9178\n\nforcolor: #C586C0icolor: #9CDCFE..5color: #B5CEA8        color: #179fff\"Count: \" + str}background: #1E1E1Ecolor: #D4D4D4font-family: monospacefont-size: 1.1removerflow-x: automax-width: 600pxbox-shadow: 0 20px 40px rgba(0,0,0,0.2)white-space: pretext-align: left\f0\9f\8c\9f Built with FrScript WASM backendpadding: 40px 20px")
)