(module
  ;; Runtime imports for complex operations
  (import "env" "print" (func $print (param i32 i32)))
  (import "env" "println" (func $println (param i32 i32)))
  (import "env" "str_concat" (func $str_concat (param i32 i32 i32 i32) (result i32 i32)))
  (import "env" "str_to_i64" (func $str_to_i64 (param i32 i32) (result i64)))
  (import "env" "i64_to_str" (func $i64_to_str (param i64) (result i32 i32)))
  (import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32 i32)))
  (import "env" "sqrt" (func $sqrt (param f64) (result f64)))
  (import "env" "list_new" (func $list_new (result i32)))
  (import "env" "list_append" (func $list_append (param i32 i64)))
  (import "env" "list_get" (func $list_get (param i32 i64) (result i64)))
  (import "env" "list_set" (func $list_set (param i32 i64 i64)))
  (import "env" "list_len" (func $list_len (param i32) (result i64)))
  (memory (export "memory") 1 100)
  (func $main (export "main")
    (block $if_end0
      (block $else1
        ;; CONST_I64 1 1
        i64.const 1
        ;; AND
        i32.wrap_i64
        i32.and
        ;; JUMP_IF_FALSE else1
        i32.eqz
        br_if $else1
        ;; CONST_STR "true"
        i32.const 0  ;; string: true...
        i32.const 4
        ;; BUILTIN_PRINTLN
        call $println
        ;; JUMP if_end0
        br $if_end0
      )
      ;; CONST_STR "false"
      i32.const 4  ;; string: false...
      i32.const 5
      ;; BUILTIN_PRINTLN
      call $println
    )
    ;; RETURN_VOID
    return
  )
  (data (i32.const 0) "\74\72\75\65")
  (data (i32.const 4) "\66\61\6c\73\65")
)
