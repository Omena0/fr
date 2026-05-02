(module
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
  (global $exception_active (mut i32) (i32.const 0))
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
    local.get $p0
    local.get $p0_len
    call $dom_create
    local.tee $l2
    local.get $p1
    local.get $p1_len
    call $dom_set_text
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    local.set $l1
    i64.const 0
    local.set $l4
    (block $forin_end2
      (loop $forin_start0
        local.get $l4
        local.get $p2
        call $list_len
        i64.lt_s
        i32.eqz
        br_if $forin_end2
        local.get $p2
        local.get $l4
        call $list_get
        local.set $l3
        local.get $l2
        local.get $l3
        i32.wrap_i64
        i32.const 0
        i32.add
        i64.load
        local.set $temp_i64_0
        local.tee $temp_i32_0
        local.get $temp_i64_0
        i32.wrap_i64
        call $dom_append
        local.get $l1
        local.get $l3
        call $list_append
        local.set $l1
        local.get $l4
        i64.const 1
        i64.add
        local.set $l4
        br $forin_start0
      )
    )
    local.get $l2
    local.get $p0
    local.get $p0_len
    local.get $l1
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
    local.set $l0
    global.get $g8
    local.get $l0
    local.set $temp
    i32.wrap_i64
    local.get $temp
    i64.extend_i32_u
    call $list_append
    i64.extend_i32_u
    global.set $g8
    call $dom_get_body
    local.get $l2
    call $dom_append
    local.get $l0
    return
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
    local.get $p1
    call $list_to_str
    call $println
    i64.const 0
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        local.get $l1
        local.get $p1
        call $list_len
        i64.lt_s
        i32.eqz
        br_if $forin_end2
        local.get $p1
        local.get $l1
        call $list_get
        local.tee $l0
        i32.const 0
        i32.const 1
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        i64.const 0
        call $list_get
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l2
        local.get $l0
        i32.const 0
        i32.const 1
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        i64.const 1
        call $list_get
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l3
        local.get $p0
        local.tee $temp_i32_0
        i32.const 0
        i32.add
        i64.load
        local.get $l2
        local.get $l3
        local.set $temp_i64_0
        local.set $temp_i64_1
        local.tee $temp_i64_2
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
        local.get $l1
        i64.const 1
        i64.add
        local.set $l1
        br $forin_start0
      )
    )
    local.get $p0
    return
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
    i64.const 0
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        local.get $l1
        local.get $p1
        call $list_len
        i64.lt_s
        i32.eqz
        br_if $forin_end2
        local.get $p1
        local.get $l1
        call $list_get
        local.tee $l0
        i32.const 0
        i32.const 1
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        i64.const 0
        call $list_get
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l2
        local.get $l0
        i32.const 0
        i32.const 1
        local.set $call_temp_i32_0
        local.set $call_temp_i32_1
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        local.get $call_temp_i32_1
        local.get $call_temp_i32_0
        call $str_split
        i64.const 1
        call $list_get
        local.tee $call_temp_i64_0
        i32.wrap_i64
        local.get $call_temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $str_strip
        local.set $temp
        i64.extend_i32_u
        local.get $temp
        i64.extend_i32_u
        i64.const 32
        i64.shl
        i64.or
        local.set $l3
        i32.const 1
        i32.const 1
        local.get $p0
        local.get $p0_len
        local.set $temp2
        local.tee $temp
        local.get $temp2
        call $str_concat
        local.get $l2
        local.get $l3
        local.get $l1
        i64.const 1
        i64.add
        local.set $l1
        br $forin_start0
      )
    )
    return
  )
  (func $classes (param $p0 i32) (param $p1 i32) (result i32)
    (local $l0 i64)
    (local $l1 i64)
    (local $temp_i32_0 i32)
    (local $temp_i64_0 i64)
    (local $temp_i64_1 i64)
    i64.const 0
    local.set $l1
    (block $forin_end2
      (loop $forin_start0
        local.get $l1
        local.get $p1
        call $list_len
        i64.lt_s
        i32.eqz
        br_if $forin_end2
        local.get $p1
        local.get $l1
        call $list_get
        local.set $l0
        local.get $p0
        local.tee $temp_i32_0
        i32.const 0
        i32.add
        i64.load
        local.get $l0
        local.set $temp_i64_0
        local.tee $temp_i64_1
        i32.wrap_i64
        local.get $temp_i64_0
        i32.wrap_i64
        local.get $temp_i64_0
        i64.const 32
        i64.shr_u
        i32.wrap_i64
        call $dom_add_class
        local.get $l1
        i64.const 1
        i64.add
        local.set $l1
        br $forin_start0
      )
    )
    local.get $p0
    return
  )
  (func $main (export "main")
    (local $l0 i32)
    (local $l1 i32)
    (local $l2 i32)
    (local $l3 i32)
    (local $temp_i64 i64)
    (local $temp_i32_0 i32)
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    i64.extend_i32_u
    global.set $g4
    i32.const 2
    i32.const 5
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $class
    i32.const 87
    i32.const 12
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $class
    i32.const 231
    i32.const 13
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $class
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 295
    i32.const 2
    i32.const 295
    i32.const 0
    i32.const 297
    i32.const 4
    i32.const 301
    i32.const 5
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 64424509746
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 321
    i32.const 8
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 492
    i32.const 1
    i32.const 493
    i32.const 41
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 297
    i32.const 4
    i32.const 578
    i32.const 8
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 297
    i32.const 4
    i32.const 605
    i32.const 11
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 297
    i32.const 4
    i32.const 635
    i32.const 14
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 21474836482
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    local.set $l3
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 823
    i32.const 2
    i32.const 825
    i32.const 12
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 55834575079
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 854
    i32.const 2
    i32.const 856
    i32.const 17
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 492
    i32.const 1
    i32.const 887
    i32.const 54
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 854
    i32.const 2
    i32.const 941
    i32.const 17
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 492
    i32.const 1
    i32.const 972
    i32.const 49
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 854
    i32.const 2
    i32.const 1021
    i32.const 19
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 492
    i32.const 1
    i32.const 1054
    i32.const 56
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 47244640807
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 51539607639
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    local.set $l1
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 823
    i32.const 2
    i32.const 1178
    i32.const 25
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 55834575079
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $classes
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    i32.const 1218
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 297
    i32.const 4
    i32.const 1221
    i32.const 4
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543369
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1239
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1240
    i32.const 4
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1258
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1273
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1239
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1274
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1275
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1276
    i32.const 4
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1280
    i32.const 7
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1258
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1301
    i32.const 15
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543460
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1273
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1330
    i32.const 2
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1276
    i32.const 4
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1332
    i32.const 3
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543479
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1239
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1258
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1349
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543494
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1364
    i32.const 2
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1366
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543511
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1273
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1239
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1274
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1275
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1381
    i32.const 8
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1280
    i32.const 7
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1258
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543533
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1403
    i32.const 9
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543460
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1412
    i32.const 3
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1415
    i32.const 3
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543388
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1258
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1349
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543494
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1273
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1273
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543533
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1275
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1276
    i32.const 4
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1418
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543431
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
    i32.const 297
    i32.const 4
    i32.const 1275
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    i32.const 297
    i32.const 4
    i32.const 1418
    i32.const 1
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 60129543403
    i64.store
    local.get $temp_i32_0
    i64.const 1
    call $list_from_array
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    local.set $l0
    i32.const 292
    i32.const 3
    i32.const 295
    i32.const 0
    i32.const 492
    i32.const 1
    i32.const 1594
    i32.const 37
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
    i64.const 0
    call $list_from_array
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
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
    call $element
    global.get $scratchpad_ptr
    local.tee $temp_i32_0
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
    call $styles
    local.set $l2
    return
  )
  (global $heap_ptr (mut i32) (i32.const 5760))
  (global $scratchpad_ptr i32 (i32.const 1664))
  (data (i32.const 0) ":.badgecolor: whitepadding: 8px 20pxborder-radius: 20pxmargin: 5pxdisplay: inline-blockfeature-cardbackground: whitepadding: 30pxborder-radius: 15pxflex: 1margin: 10pxmin-width: 250pxbox-shadow: 0 10px 30px rgba(240, 147, 251, 0.1)section-titletext-align: centercolor: #333margin-bottom: 30pxdivh1span\f0\9f\9a\80 font-size: 4remFrScriptbackground: linear-gradient(135deg, #667eea 0%, #764ba2 100%)-webkit-background-clip: text-webkit-text-fill-color: transparentmargin: 0animation: pulse 2s infinitepA fast, modern bytecode-compiled languagefont-size: 1.5remcolor: #666margin-top: 10px\e2\9a\a1 Fastbackground: #667eea\f0\9f\8e\af Simplebackground: #764ba2\f0\9f\8c\90 Web-Readybackground: #f093fbmargin-top: 30pxdisplay: flexgap: 15pxjustify-content: centerflex-wrap: wrappadding: 80px 20pxbackground: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%)h2\e2\9c\a8 Featuresfont-size: 2.5remh3\f0\9f\94\a5 Blazing Fastcolor: #667eeaCompiles to optimized bytecode for maximum performance\f0\9f\8e\a8 Clean Syntaxcolor: #764ba2Write beautiful, readable code with modern syntax\f0\9f\8c\8d Cross-Platformcolor: #f093fbRun on native, Python runtime, or compile to WebAssemblymax-width: 1000pxmargin: 0 autopadding: 60px 20pxbackground: #f8f9ff\f0\9f\92\bb Simple  and  Elegantfont-size: 2remprevoidcolor: #569CD6 maincolor: #DCDCAA(color: #ffd700){\n    printlncolor: #da70d6\"Hello, World!\"color: #CE9178\n\nforcolor: #C586C0icolor: #9CDCFE..5color: #B5CEA8        color: #179fff\"Count: \" + str}background: #1E1E1Ecolor: #D4D4D4font-family: monospacefont-size: 1.1removerflow-x: automax-width: 600pxbox-shadow: 0 20px 40px rgba(0,0,0,0.2)white-space: pretext-align: left\f0\9f\8c\9f Built with FrScript WASM backendpadding: 40px 20px")
)