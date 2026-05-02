.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .func fib i64 1

.align 16  # Function alignment
fib:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg num i64
    mov rax, [rbp + 16]
    mov [rbp - 8], rax


    mov [rbp - 8], rax  # Store
    # Removed: mov rax, [rbp - 8]  # Load (rax already contains value)
    push rax
    # CMP_LT_CONST 2
    pop rax
    cmp rax, 2
    jge .Lfib_if_end0  # Optimized: removed setcc+movzx+push+pop+test
    # .line 4 "return num"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lfib_if_end0:
    # .line 7 "return fib(num-1) + fib(num-2)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # SUB_CONST_I64 1
    pop rax
    sub rax, 1
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # LOAD_GLOBAL 2
    mov rax, [global_vars + 16]
    push rax
    # BUILTIN_LEN 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_list_len_aligned_0
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_0
.Lruntime_list_len_aligned_0: 
    call runtime_list_len
.Lruntime_list_len_done_0: 
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    jge .Lfib_memo_fallback2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD_GLOBAL 2
    mov rax, [global_vars + 16]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_get_slow_1  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_get_slow_1  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov rax, [rax + rsi*8]  # rax = items[index]
    jmp .Llist_get_done_1
    .Llist_get_slow_1:
    mov rdx, 7  # line number
    call runtime_list_get_int_at
    .Llist_get_done_1:
    push rax
    # JUMP memo_done3
    jmp .Lfib_memo_done3
    # LABEL memo_fallback2
    # Removed 1 dead instruction(s)
.Lfib_memo_fallback2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CALL fib 1
    # CALL fib: struct_args=set(), float_args=set(), stack_types=['i64']
    call fib
    push rax
    # LABEL memo_done3
    jmp .Lfib_skip_labels
.Lfib_memo_done3:
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # SUB_CONST_I64 2
    pop rax
    sub rax, 2
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # LOAD_GLOBAL 2
    mov rax, [global_vars + 16]
    push rax
    # BUILTIN_LEN 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_list_len_aligned_2
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_2
.Lruntime_list_len_aligned_2: 
    call runtime_list_len
.Lruntime_list_len_done_2: 
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    jge .Lfib_memo_fallback4  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD_GLOBAL 2
    mov rax, [global_vars + 16]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_get_slow_3  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_get_slow_3  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov rax, [rax + rsi*8]  # rax = items[index]
    jmp .Llist_get_done_3
    .Llist_get_slow_3:
    mov rdx, 7  # line number
    call runtime_list_get_int_at
    .Llist_get_done_3:
    push rax
    # JUMP memo_done5
    jmp .Lfib_memo_done5
    # LABEL memo_fallback4
    # Removed 1 dead instruction(s)
.Lfib_memo_fallback4:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CALL fib 1
    # CALL fib: struct_args=set(), float_args=set(), stack_types=['i64']
    call fib
    push rax
    # LABEL memo_done5
    jmp .Lfib_skip_labels
.Lfib_memo_done5:
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # RETURN 
    pop rax
    ret
    # .end 
.Lfib_skip_labels:
    # .func main void 0

.align 16  # Function alignment
main:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # Zero out stack frame
    push rdi
    push rcx
    push rax
    lea rdi, [rsp + 24]  # point to start of our stack frame
    mov rcx, 32  # 256 bytes / 8 = 32 qwords
    xor rax, rax
    rep stosq  # zero out [rdi] for rcx qwords
    pop rax
    pop rcx
    pop rdi
    # Initialize runtime and source info    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_init_aligned_8
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_8
.Lruntime_init_aligned_8: 
    call runtime_init
.Lruntime_init_done_8: 
    lea rdi, [.STR0]  # filename
    lea rsi, [.STR1]  # source
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_set_source_info_aligned_9
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_9
.Lruntime_set_source_info_aligned_9: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_9: 
    # .local __memo_tmp i64
    # LIST_NEW_I64 93 0 1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987 1597 2584 4181 6765 10946 17711 28657 46368 75025 121393 196418 317811 514229 832040 1346269 2178309 3524578 5702887 9227465 14930352 24157817 39088169 63245986 102334155 165580141 267914296 433494437 701408733 1134903170 1836311903 2971215073 4807526976 7778742049 12586269025 20365011074 32951280099 53316291173 86267571272 139583862445 225851433717 365435296162 591286729879 956722026041 1548008755920 2504730781961 4052739537881 6557470319842 10610209857723 17167680177565 27777890035288 44945570212853 72723460248141 117669030460994 190392490709135 308061521170129 498454011879264 806515533049393 1304969544928657 2111485077978050 3416454622906707 5527939700884757 8944394323791464 14472334024676221 23416728348467685 37889062373143906 61305790721611591 99194853094755497 160500643816367088 259695496911122585 420196140727489673 679891637638612258 1100087778366101931 1779979416004714189 2880067194370816120 4660046610375530309 7540113804746346429
    lea rdi, [.ARR0]
    mov rsi, 93
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_list_from_array_aligned_4
    sub rsp, 8
    call runtime_list_from_array
    add rsp, 8
    jmp .Lruntime_list_from_array_done_4
.Lruntime_list_from_array_aligned_4: 
    call runtime_list_from_array
.Lruntime_list_from_array_done_4: 
    mov dword ptr [rax + 24], 0  # elem_type = 0 (int)
    push rax
    # STORE_GLOBAL 1
    pop qword ptr [global_vars + 8]  # Direct pop to memory
    # .line 11 "println(fib(100000))"
    # CONST_I64 100000
    mov rax, 100000
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 0
    mov qword ptr [rbp - 8], rax  # Eliminated push/pop
    # LOAD_GLOBAL 1
    mov rax, [global_vars + 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_list_len_aligned_5
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_5
.Lruntime_list_len_aligned_5: 
    call runtime_list_len
.Lruntime_list_len_done_5: 
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    jge .Lmain_memo_fallback0  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD_GLOBAL 1
    mov rax, [global_vars + 8]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_get_slow_6  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_get_slow_6  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov rax, [rax + rsi*8]  # rax = items[index]
    jmp .Llist_get_done_6
    .Llist_get_slow_6:
    mov rdx, 11  # line number
    call runtime_list_get_int_at
    .Llist_get_done_6:
    push rax
    # JUMP memo_done1
    jmp .Lmain_memo_done1
    # LABEL memo_fallback0
    # Removed 1 dead instruction(s)
.Lmain_memo_fallback0:
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CALL fib 1
    # CALL fib: struct_args=set(), float_args=set(), stack_types=['i64']
    call fib
    push rax
    # LABEL memo_done1
    jmp .Lmain_skip_labels
.Lmain_memo_done1:
    # BUILTIN_PRINTLN 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_println_aligned_7
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_7
.Lruntime_println_aligned_7: 
    call runtime_println
.Lruntime_println_done_7: 
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .entry main

.section .rodata
.ARR0:
    .quad 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040, 1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986, 102334155, 165580141, 267914296, 433494437, 701408733, 1134903170, 1836311903, 2971215073, 4807526976, 7778742049, 12586269025, 20365011074, 32951280099, 53316291173, 86267571272, 139583862445, 225851433717, 365435296162, 591286729879, 956722026041, 1548008755920, 2504730781961, 4052739537881, 6557470319842, 10610209857723, 17167680177565, 27777890035288, 44945570212853, 72723460248141, 117669030460994, 190392490709135, 308061521170129, 498454011879264, 806515533049393, 1304969544928657, 2111485077978050, 3416454622906707, 5527939700884757, 8944394323791464, 14472334024676221, 23416728348467685, 37889062373143906, 61305790721611591, 99194853094755497, 160500643816367088, 259695496911122585, 420196140727489673, 679891637638612258, 1100087778366101931, 1779979416004714189, 2880067194370816120, 4660046610375530309, 7540113804746346429
.STR0:
    .asciz "fib_recursive.fr"
.STR1:
    .asciz "\n\nif (num < 2) {\nreturn num\n\n\nreturn fib(num-1) + fib(num-2)\n\n\n\nprintln(fib(100000))"

.section .bss
.globl global_vars
global_vars:
    .space 32  # Optimized (was 2048, max offset 16)
.globl struct_heap_ptr
.align 16  # Function alignment
struct_heap_ptr:
    .quad 0  # Current heap position (bump allocator)
.globl struct_heap_base
.align 16  # Function alignment
struct_heap_base:
    .quad 0  # Base pointer to heap (allocated at runtime)
.align 16  # Function alignment
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
.align 16  # Function alignment
list_append_scratch:
    .quad 0  # Temporary storage for list pointer during list_append
.align 16  # Function alignment
struct_data:
    .space 67108864  # Space for struct instances (262144 instances * 256 bytes each = 64MB)
