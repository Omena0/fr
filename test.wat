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
  (import "env" "str_upper" (func $str_upper (param i32 i32) (result i32 i32)))
  (import "env" "str_lower" (func $str_lower (param i32 i32) (result i32 i32)))
  (import "env" "str_strip" (func $str_strip (param i32 i32) (result i32 i32)))
  (import "env" "str_replace" (func $str_replace (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "env" "str_get" (func $str_get (param i32 i32 i64) (result i32 i32)))
  (import "env" "str_contains" (func $str_contains (param i32 i32 i32 i32) (result i32)))
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
  (import "env" "round_f64" (func $round_f64 (param f64) (result f64)))
  (import "env" "floor_f64" (func $floor_f64 (param f64) (result f64)))
  (import "env" "ceil_f64" (func $ceil_f64 (param f64) (result f64)))
  (import "env" "file_open" (func $file_open (param i32 i32 i32 i32) (result i32)))
  (import "env" "file_read" (func $file_read (param i32) (result i32 i32)))
  (import "env" "file_write" (func $file_write (param i32 i32 i32)))
  (import "env" "file_close" (func $file_close (param i32)))
  (import "env" "exit_process" (func $exit_process (param i32)))
  (memory (export "memory") 1 100)
  ;; Heap pointer for struct allocation
  (global $heap_ptr (mut i32) (i32.const 1024))
  (func $main (export "main")
    (local $l0 i64)
    (local $l1 i64)
    (local $l2 i64)
    (local $temp i32)
    (local $temp_i64 i64)
    (local $temp_f64 f64)
    ;; CONST_STR "/tmp/test_lang2.txt" "w"
    i32.const 0  ;; string: /tmp/test_lang2.txt...
    i32.const 19
    i32.const 19  ;; string: w...
    i32.const 1
    ;; FILE_OPEN
    call $file_open
    ;; STORE 1
    local.set $l1
    ;; LOAD 1
    local.get $l1
    ;; DUP
    local.tee $temp
    local.get $temp
    ;; CONST_STR "Hello, World! This is a test file."
    i32.const 20  ;; string: Hello, World! This i...
    i32.const 34
    ;; FILE_WRITE
    call $file_write
    ;; POP
    drop
    ;; FILE_CLOSE
    call $file_close
    ;; CONST_STR "/tmp/test_lang2.txt" "r"
    i32.const 0  ;; string: /tmp/test_lang2.txt...
    i32.const 19
    i32.const 54  ;; string: r...
    i32.const 1
    ;; FILE_OPEN
    call $file_open
    ;; STORE 2
    local.set $l2
    ;; LOAD 2
    local.get $l2
    ;; CONST_I64 1
    i64.const 1
    ;; NEG
    i64.const -1
    i64.mul
    ;; FILE_READ
    call $file_read
    ;; STORE 0
    local.set $l0_len
    local.set $l0
    ;; LOAD 2
    local.get $l2
    ;; FILE_CLOSE
    call $file_close
    ;; CONST_STR "File content:"
    i32.const 55  ;; string: File content:...
    i32.const 13
    ;; BUILTIN_PRINTLN
    call $println
    ;; LOAD 0
    local.get $l0
    local.get $l0_len
    ;; BUILTIN_PRINTLN
    call $println
    ;; RETURN_VOID
    return
  )
  (data (i32.const 0) "\2f\74\6d\70\2f\74\65\73\74\5f\6c\61\6e\67\32\2e\74\78\74")
  (data (i32.const 19) "\77")
  (data (i32.const 20) "\48\65\6c\6c\6f\2c\20\57\6f\72\6c\64\21\20\54\68\69\73\20\69\73\20\61\20\74\65\73\74\20\66\69\6c\65\2e")
  (data (i32.const 54) "\72")
  (data (i32.const 55) "\46\69\6c\65\20\63\6f\6e\74\65\6e\74\3a")
)