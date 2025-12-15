(module
  ;; Runtime imports for complex operations
  (import "env" "dom_create" (func $dom_create (param i32 i32) (result i32)))
  (import "env" "dom_set_text" (func $dom_set_text (param i32 i32 i32)))
  (import "env" "dom_append" (func $dom_append (param i32 i32)))
  (import "env" "dom_set_style" (func $dom_set_style (param i32 i32 i32 i32 i32)))
  (import "env" "dom_query" (func $dom_query (param i32 i32) (result i32)))
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
    (local $l0_len i32)
    (local $l1 i32)
    (local $l1_len i32)
    (local $l2 i32)
    (local $l2_len i32)
    (local $l3 i64)
    (local $l3_len i32)
    (local $l4 i64)
    (local $l4_len i32)
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
    ;; LOAD 0
    local.get $p0
    local.get $p0_len
    ;; CALL dom_create 1
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $dom_create
    ;; STORE 5
    local.set $l2
    ;; LOAD 5 1
    local.get $l2
    local.get $p1
    local.get $p1_len
    ;; CALL dom_set_text 2
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.set $temp_i32_2
    local.get $temp_i32_2
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $dom_set_text
    ;; LIST_NEW
    call $list_new
    ;; STORE 4
    local.set $l1
    ;; STORE_CONST_I64 7 0
    i64.const 0
    local.set $l4
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 7 2
        local.get $l4
        local.get $p2
        ;; BUILTIN_LEN
        local.set $temp_i32_0
        local.get $temp_i32_0
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 2 7
        local.get $p2
        local.get $l4
        ;; LIST_GET
        local.set $temp_i64_0
        local.set $temp_i32_0
        local.get $temp_i32_0
        local.get $temp_i64_0
        call $list_get
        ;; STORE 6
        local.set $l3
        ;; LOAD 5 6
        local.get $l2
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
        ;; LOAD 4 6
        local.get $l1
        local.get $l3
        ;; LIST_APPEND
        local.set $temp_i64_0
        local.set $temp_i32_0
        local.get $temp_i32_0
        local.get $temp_i64_0
        call $list_append
        ;; STORE 4
        local.set $l1
        ;; INC_LOCAL 7
        local.get $l4
        i64.const 1
        i64.add
        local.set $l4
        ;; JUMP forin_start0
        br $forin_start0
      )
    )
    ;; LOAD 5 0 4
    local.get $l2
    local.get $p0
    local.get $p0_len
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
    i32.const 16
    i32.add
    local.get $temp_i64
    i64.store
    local.set $temp_i32_1
    i64.extend_i32_u
    local.set $temp_i64_0
    local.get $temp_i32_0
    i32.const 8
    i32.add
    local.get $temp_i64_0
    local.get $temp_i32_1
    i64.extend_i32_u
    i64.const 32
    i64.shl
    i64.or
    i64.store
    i64.extend_i32_u
    local.set $temp_i64
    local.get $temp_i32_0
    i32.const 0
    i32.add
    local.get $temp_i64
    i64.store
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
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    ;; STORE_GLOBAL 8
    i64.extend_i32_u
    global.set $g8
    ;; LOAD 3
    local.get $l0
    ;; RETURN
    return
    unreachable
  )
  (func $styles (param $p0 i32) (param $p1 i32) (result i32)
    (local $l0 i64)
    (local $l0_len i32)
    (local $l1 i64)
    (local $l1_len i32)
    (local $l2 i64)
    (local $l2_len i32)
    (local $l3 i64)
    (local $l3_len i32)
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
    ;; LOAD 1
    local.get $p1
    ;; BUILTIN_PRINTLN
    local.set $temp_i32_0
    local.get $temp_i32_0
    call $list_to_str
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $println
    ;; STORE_CONST_I64 3 0
    i64.const 0
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        ;; LOAD 3 1
        local.get $l1
        local.get $p1
        ;; BUILTIN_LEN
        local.set $temp_i32_0
        local.get $temp_i32_0
        call $list_len
        ;; CMP_LT
        i64.lt_s
        ;; JUMP_IF_FALSE forin_end2
        i32.eqz
        br_if $forin_end2
        ;; LOAD 1 3
        local.get $p1
        local.get $l1
        ;; LIST_GET
        local.set $temp_i64_0
        local.set $temp_i32_0
        local.get $temp_i32_0
        local.get $temp_i64_0
        call $list_get
        ;; STORE 2
        local.set $l0
        ;; LOAD 2
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
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
        ;; STORE 4
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
        local.get $l0
        ;; CONST_STR ":"
        i32.const 0  ;; string: :...
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
        ;; CONST_I64 1
        i64.const 1
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
        ;; STORE 5
        local.set $temp
        i64.extend_i32_u
        local.set $temp_i64
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        local.get $temp_i64
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
        ;; LOAD 4 5
        local.get $l2
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
        ;; INC_LOCAL 3
        local.get $l1
        i64.const 1
        i64.add
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
    (local $l0_len i32)
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
    ;; STORE_GLOBAL 1
    i64.extend_i32_u
    global.set $g1
    ;; CONST_STR "div"
    i32.const 1  ;; string: div...
    i32.const 3
    ;; CONST_STR "Div 1"
    i32.const 4  ;; string: Div 1...
    i32.const 5
    ;; CONST_STR "h1"
    i32.const 9  ;; string: h1...
    i32.const 2
    ;; CONST_STR "Bing chilling 1"
    i32.const 11  ;; string: Bing chilling 1...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CONST_STR "margin-top: 100px"
    i32.const 26  ;; string: margin-top: 100px...
    i32.const 17
    ;; CALL styles 2
    local.set $temp
    i64.extend_i32_u
    local.get $temp
    i64.extend_i32_u
    i64.const 32
    i64.shl
    i64.or
    local.set $temp_i64_0
    call $list_new
    local.get $temp_i64_0
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    call $styles
    ;; CONST_STR "h2"
    i32.const 43  ;; string: h2...
    i32.const 2
    ;; CONST_STR "Bing chilling 2"
    i32.const 45  ;; string: Bing chilling 2...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CONST_STR "h3"
    i32.const 60  ;; string: h3...
    i32.const 2
    ;; CONST_STR "Bing chilling 3"
    i32.const 62  ;; string: Bing chilling 3...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CONST_STR "h4"
    i32.const 77  ;; string: h4...
    i32.const 2
    ;; CONST_STR "Bing chilling 4"
    i32.const 79  ;; string: Bing chilling 4...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CONST_STR "h5"
    i32.const 94  ;; string: h5...
    i32.const 2
    ;; CONST_STR "Bing chilling 5"
    i32.const 96  ;; string: Bing chilling 5...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CONST_STR "h6"
    i32.const 111  ;; string: h6...
    i32.const 2
    ;; CONST_STR "Bing chilling 6"
    i32.const 113  ;; string: Bing chilling 6...
    i32.const 15
    ;; CALL element 2
    call $list_new
    call $element
    ;; CALL element 8
    i64.extend_i32_u
    local.set $temp_i64_0
    i64.extend_i32_u
    local.set $temp_i64_1
    i64.extend_i32_u
    local.set $temp_i64_2
    i64.extend_i32_u
    local.set $temp_i64_3
    i64.extend_i32_u
    local.set $temp_i64_4
    i64.extend_i32_u
    local.set $temp_i64_5
    call $list_new
    local.get $temp_i64_5
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    local.get $temp_i64_4
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    local.get $temp_i64_3
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    local.get $temp_i64_2
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    local.get $temp_i64_1
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    local.get $temp_i64_0
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    call $element
    ;; CONST_STR "margin-left: 30px"
    i32.const 128  ;; string: margin-left: 30px...
    i32.const 17
    ;; CALL styles 2
    local.set $temp
    i64.extend_i32_u
    local.get $temp
    i64.extend_i32_u
    i64.const 32
    i64.shl
    i64.or
    local.set $temp_i64_0
    call $list_new
    local.get $temp_i64_0
    local.set $temp_i64_0
    local.set $temp_i32_0
    local.get $temp_i32_0
    local.get $temp_i64_0
    call $list_append
    call $styles
    ;; STORE 0
    local.set $l0
    ;; CONST_STR "#output"
    i32.const 145  ;; string: #output...
    i32.const 7
    ;; CALL dom_query 1
    local.set $temp_i32_0
    local.set $temp_i32_1
    local.get $temp_i32_1
    local.get $temp_i32_0
    call $dom_query
    ;; LOAD 0
    local.get $l0
    ;; STRUCT_GET 0
    local.set $temp_i32_0
    local.get $temp_i32_0
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
    ;; RETURN_VOID
    return
  )
  (data (i32.const 0) "\3a")
  (data (i32.const 1) "\64\69\76")
  (data (i32.const 4) "\44\69\76\20\31")
  (data (i32.const 9) "\68\31")
  (data (i32.const 11) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\31")
  (data (i32.const 26) "\6d\61\72\67\69\6e\2d\74\6f\70\3a\20\31\30\30\70\78")
  (data (i32.const 43) "\68\32")
  (data (i32.const 45) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\32")
  (data (i32.const 60) "\68\33")
  (data (i32.const 62) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\33")
  (data (i32.const 77) "\68\34")
  (data (i32.const 79) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\34")
  (data (i32.const 94) "\68\35")
  (data (i32.const 96) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\35")
  (data (i32.const 111) "\68\36")
  (data (i32.const 113) "\42\69\6e\67\20\63\68\69\6c\6c\69\6e\67\20\36")
  (data (i32.const 128) "\6d\61\72\67\69\6e\2d\6c\65\66\74\3a\20\33\30\70\78")
  (data (i32.const 145) "\23\6f\75\74\70\75\74")
)