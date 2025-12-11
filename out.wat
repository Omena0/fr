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
  (func $pi_spigot (param $p0 i64) (result i32 i32)
    (local $l0 i32)
    (local $l0_len i32)
    (local $l1 i64)
    (local $l1_len i32)
    (local $l2 i64)
    (local $l2_len i32)
    (local $l3 i64)
    (local $l3_len i32)
    (local $l4 i32)
    (local $l4_len i32)
    (local $l5 i64)
    (local $l5_len i32)
    (local $l6 i64)
    (local $l6_len i32)
    (local $l7 i64)
    (local $l7_len i32)
    (local $l8 i64)
    (local $l8_len i32)
    (local $l9 i64)
    (local $l9_len i32)
    (local $l10 i64)
    (local $l10_len i32)
    (local $l11 i64)
    (local $l11_len i32)
    (local $temp i32)
    (local $temp2 i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    ;; LIST_NEW
    call $list_new
    ;; STORE 1
    local.set $l0
    ;; CONST_I64 10
    i64.const 10
    ;; LOAD 0
    local.get $p0
    ;; MUL_I64
    i64.mul
    ;; DIV_CONST_I64 3
    f64.convert_i64_s
    f64.const 3
    f64.div
    ;; ADD_CONST_I64 1
    f64.const 1
    f64.add
    ;; TO_INT
    i64.trunc_f64_s
    ;; STORE 2
    local.set $l1
    ;; STORE_CONST_I64 6 0
    i64.const 0
    local.set $l5
    (block $for_end2
      (loop $for_start0
        ;; LOAD2_CMP_LT 6 2
        local.get $l5
        local.get $l1
        i64.lt_s
        ;; JUMP_IF_FALSE for_end2
        i32.eqz
        br_if $for_end2
        ;; LOAD 1
        local.get $l0
        ;; CONST_I64 2
        i64.const 2
        ;; LIST_APPEND
        call $list_append
        ;; STORE 1
        local.set $l0
        ;; INC_LOCAL 6
        local.get $l5
        i64.const 1
        i64.add
        local.set $l5
        ;; JUMP for_start0
        br $for_start0
      )
    )
    ;; CONST_STR ""
    i32.const 0  ;; string: ...
    i32.const 0
    ;; STORE 5
    local.set $l4_len
    local.set $l4
    ;; STORE_CONST_I64 3 0
    i64.const 0
    local.set $l2
    ;; STORE_CONST_I64 4 1
    i64.const 1
    local.set $l3
    ;; STORE_CONST_I64 6 0
    i64.const 0
    local.set $l5
    (block $for_end5
      (loop $for_start3
        (block $for_continue4
          (block $if_end10
            (block $if_end16
              (block $else12
                (block $else11
                  (block $if_end8
                    ;; LOAD2_CMP_LT 6 0
                    local.get $l5
                    local.get $p0
                    i64.lt_s
                    ;; JUMP_IF_FALSE for_end5
                    i32.eqz
                    br_if $for_end5
                    ;; STORE_CONST_I64 7 0
                    i64.const 0
                    local.set $l6
                    ;; LOAD 2
                    local.get $l1
                    ;; SUB_CONST_I64 1
                    i64.const 1
                    i64.sub
                    ;; STORE 8
                    local.set $l7
                    (block $while_end7
                      (loop $while_start6
                        ;; LOAD 8
                        local.get $l7
                        ;; CMP_GE_CONST 1
                        i64.const 1
                        i64.ge_s
                        ;; JUMP_IF_FALSE while_end7
                        i32.eqz
                        br_if $while_end7
                        ;; LOAD 1 8
                        local.get $l0
                        local.get $l7
                        ;; LIST_GET
                        call $list_get
                        ;; MUL_CONST_I64 10
                        i64.const 10
                        i64.mul
                        ;; LOAD2_MUL_I64 7 8
                        local.get $l6
                        local.get $l7
                        i64.mul
                        ;; ADD_I64
                        i64.add
                        ;; STORE 9
                        local.set $l8
                        ;; CONST_I64 2
                        i64.const 2
                        ;; LOAD 8
                        local.get $l7
                        ;; MUL_I64
                        i64.mul
                        ;; SUB_CONST_I64 1
                        i64.const 1
                        i64.sub
                        ;; STORE 10
                        local.set $l9
                        ;; LOAD 1 8 9 10
                        local.get $l0
                        local.get $l7
                        local.get $l8
                        local.get $l9
                        ;; MOD_I64
                        i64.rem_s
                        ;; LIST_SET
                        call $list_set
                        ;; STORE 1
                        local.set $l0
                        ;; LOAD2_DIV_I64 9 10
                        local.get $l8
                        local.get $l9
                        f64.convert_i64_s
                        local.set $temp_f64
                        f64.convert_i64_s
                        local.get $temp_f64
                        f64.div
                        ;; STORE 7
                        i64.trunc_f64_s
                        local.set $l6
                        ;; DEC_LOCAL 8
                        local.get $l7
                        i64.const 1
                        i64.sub
                        local.set $l7
                        ;; JUMP while_start6
                        br $while_start6
                      )
                    )
                    ;; LOAD 1
                    local.get $l0
                    ;; CONST_I64 0
                    i64.const 0
                    ;; LIST_GET
                    call $list_get
                    ;; MUL_CONST_I64 10
                    i64.const 10
                    i64.mul
                    ;; LOAD 7
                    local.get $l6
                    ;; ADD_I64
                    i64.add
                    ;; STORE 9
                    local.set $l8
                    ;; LOAD 9
                    local.get $l8
                    ;; DIV_CONST_I64 10
                    f64.convert_i64_s
                    f64.const 10
                    f64.div
                    ;; TO_INT
                    i64.trunc_f64_s
                    ;; STORE 11
                    local.set $l10
                    ;; LOAD 1
                    local.get $l0
                    ;; CONST_I64 0
                    i64.const 0
                    ;; LOAD 9
                    local.get $l8
                    ;; MOD_CONST_I64 10
                    i64.const 10
                    i64.rem_s
                    ;; LIST_SET
                    call $list_set
                    ;; STORE 1
                    local.set $l0
                    ;; LOAD 6
                    local.get $l5
                    ;; CMP_LT_CONST 2
                    i64.const 2
                    i64.lt_s
                    ;; JUMP_IF_FALSE if_end8
                    i32.eqz
                    br_if $if_end8
                    ;; JUMP for_continue4
                    br $for_continue4
                  )
                  ;; LOAD 11
                  local.get $l10
                  ;; CMP_EQ_CONST 9
                  i64.const 9
                  i64.eq
                  ;; JUMP_IF_FALSE else11
                  i32.eqz
                  br_if $else11
                  ;; INC_LOCAL 3
                  local.get $l2
                  i64.const 1
                  i64.add
                  local.set $l2
                  ;; JUMP if_end10
                  br $if_end10
                )
                ;; LOAD 11
                local.get $l10
                ;; CMP_EQ_CONST 10
                i64.const 10
                i64.eq
                ;; JUMP_IF_FALSE else12
                i32.eqz
                br_if $else12
                ;; LOAD 5 4
                local.get $l4
                local.get $l4_len
                local.get $l3
                ;; ADD_CONST_I64 1
                i64.const 1
                i64.add
                ;; BUILTIN_STR
                call $i64_to_str
                ;; ADD_STR
                local.set $temp2
                local.set $temp
                local.get $temp
                local.get $temp2
                call $str_concat
                ;; STORE 5
                local.set $l4_len
                local.set $l4
                ;; STORE_CONST_I64 12 0
                i64.const 0
                local.set $l11
                (block $for_end15
                  (loop $for_start13
                    ;; LOAD2_CMP_LT 12 3
                    local.get $l11
                    local.get $l2
                    i64.lt_s
                    ;; JUMP_IF_FALSE for_end15
                    i32.eqz
                    br_if $for_end15
                    ;; LOAD 5
                    local.get $l4
                    local.get $l4_len
                    ;; CONST_STR "0"
                    i32.const 0  ;; string: 0...
                    i32.const 1
                    ;; ADD_STR
                    local.set $temp2
                    local.set $temp
                    local.get $temp
                    local.get $temp2
                    call $str_concat
                    ;; STORE 5
                    local.set $l4_len
                    local.set $l4
                    ;; INC_LOCAL 12
                    local.get $l11
                    i64.const 1
                    i64.add
                    local.set $l11
                    ;; JUMP for_start13
                    br $for_start13
                  )
                )
                ;; STORE_CONST_I64 4 0
                i64.const 0
                local.set $l3
                ;; STORE_CONST_I64 3 0
                i64.const 0
                local.set $l2
                ;; JUMP if_end10
                br $if_end10
              )
              ;; LOAD 5 4
              local.get $l4
              local.get $l4_len
              local.get $l3
              ;; BUILTIN_STR
              call $i64_to_str
              ;; ADD_STR
              local.set $temp2
              local.set $temp
              local.get $temp
              local.get $temp2
              call $str_concat
              ;; STORE 5
              local.set $l4_len
              local.set $l4
              ;; FUSED_LOAD_STORE 11 4
              local.get $l10
              local.set $l3
              ;; LOAD 3
              local.get $l2
              ;; CMP_GT_CONST 0
              i64.const 0
              i64.gt_s
              ;; JUMP_IF_FALSE if_end16
              i32.eqz
              br_if $if_end16
              ;; STORE_CONST_I64 12 0
              i64.const 0
              local.set $l11
              (block $for_end20
                (loop $for_start18
                  ;; LOAD2_CMP_LT 12 3
                  local.get $l11
                  local.get $l2
                  i64.lt_s
                  ;; JUMP_IF_FALSE for_end20
                  i32.eqz
                  br_if $for_end20
                  ;; LOAD 5
                  local.get $l4
                  local.get $l4_len
                  ;; CONST_STR "9"
                  i32.const 1  ;; string: 9...
                  i32.const 1
                  ;; ADD_STR
                  local.set $temp2
                  local.set $temp
                  local.get $temp
                  local.get $temp2
                  call $str_concat
                  ;; STORE 5
                  local.set $l4_len
                  local.set $l4
                  ;; INC_LOCAL 12
                  local.get $l11
                  i64.const 1
                  i64.add
                  local.set $l11
                  ;; JUMP for_start18
                  br $for_start18
                )
              )
              ;; STORE_CONST_I64 3 0
              i64.const 0
              local.set $l2
            )
          )
        )
        ;; INC_LOCAL 6
        local.get $l5
        i64.const 1
        i64.add
        local.set $l5
        ;; JUMP for_start3
        br $for_start3
      )
    )
    ;; LOAD 5 4
    local.get $l4
    local.get $l4_len
    local.get $l3
    ;; BUILTIN_STR
    call $i64_to_str
    ;; ADD_STR
    local.set $temp2
    local.set $temp
    local.get $temp
    local.get $temp2
    call $str_concat
    ;; STORE 5
    local.set $l4_len
    local.set $l4
    ;; CONST_STR "3."
    i32.const 2  ;; string: 3....
    i32.const 2
    ;; LOAD 5
    local.get $l4
    local.get $l4_len
    ;; BUILTIN_STR
    ;; ADD_STR
    local.set $temp2
    local.set $temp
    local.get $temp
    local.get $temp2
    call $str_concat
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
    ;; CONST_I64 1000
    i64.const 1000
    ;; CALL pi_spigot 1
    call $pi_spigot
    ;; STORE 0
    local.set $l0_len
    local.set $l0
    ;; LOAD 0
    local.get $l0
    local.get $l0_len
    ;; BUILTIN_PRINTLN
    call $println
    ;; RETURN_VOID
    return
    unreachable
  )
  (data (i32.const 0) "")
  (data (i32.const 0) "\30")
  (data (i32.const 1) "\39")
  (data (i32.const 2) "\33\2e")
)