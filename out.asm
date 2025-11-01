.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .func fibonacci i64 1

.align 16  # Function alignment
fibonacci:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local a i64
    # .local b i64
    # .local c i64
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CMP_LE_CONST 1
    pop rax
    cmp rax, 1
    jg .Lis_prime_if_end0  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lfibonacci_if_end0:
    # STORE_CONST_I64 1 0 2 1 3 1 4 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 1  # Immediate store
    mov qword ptr [rbp - 32], 1  # Immediate store
    mov qword ptr [rbp - 40], 0  # Immediate store
    # LABEL for_start2
.align 16  # Loop alignment
.Lfibonacci_for_start2:
    # LOAD2_CMP_LT 4 0
    mov rax, [rbp - 40]
    cmp rax, [rbp - 8]
    jge .Lpower_for_end4  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD2_ADD_I64 1 2
    mov rax, [rbp - 16]
    add rax, [rbp - 24]
    # FUSED_STORE_LOAD 3 2 1 3 2
    mov qword ptr [rbp - 32], rax  # Eliminated push/pop
    mov rax, [rbp - 24]
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    mov rax, [rbp - 32]
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # JUMP for_start2
    jmp .Lfibonacci_for_start2
    # LABEL for_end4
.Lfibonacci_for_end4:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lfibonacci_skip_labels:
    # .func factorial i64 1

.align 16  # Function alignment
factorial:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local result i64
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CMP_LE_CONST 1
    pop rax
    cmp rax, 1
    jg .Lfibonacci_if_end0  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_I64 1
    mov rax, 1
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lfactorial_if_end0:
    # STORE_CONST_I64 1 1 2 0
    mov qword ptr [rbp - 16], 1  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start2
.align 16  # Loop alignment
.Lfactorial_for_start2:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lfibonacci_for_end4  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1 2
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 24]
    push rax
    # ADD_CONST_I64 1
    pop rax
    add rax, 1
    push rax
    # MUL_I64 
    pop rbx
    pop rax
    imul rax, rbx
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start2
    jmp .Lfactorial_for_start2
    # LABEL for_end4
.Lfactorial_for_end4:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lfactorial_skip_labels:
    # .func power f64 2

.align 16  # Function alignment
power:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg base f64
    mov [rbp - 8], rdi
    # .arg exp i64
    mov [rbp - 16], rsi
    # .local result f64
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    jne .Lfactorial_if_end0  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_F64 1.0
    movsd xmm0, [.FLOAT0]
    sub rsp, 8
    movsd [rsp], xmm0
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lpower_if_end0:
    # STORE_CONST_F64 2 1.0
    movsd xmm0, [.FLOAT1]
    movsd [rbp - 24], xmm0
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start2
.align 16  # Loop alignment
.Lpower_for_start2:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Lfactorial_for_end4  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD2_MUL_F64 2 0
    movsd xmm0, [rbp - 24]
    mulsd xmm0, [rbp - 8]
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 2
    pop qword ptr [rbp - 24]  # Direct pop to memory
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start2
    jmp .Lpower_for_start2
    # LABEL for_end4
.Lpower_for_end4:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lpower_skip_labels:
    # .func gcd i64 2

.align 16  # Function alignment
gcd:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg a i64
    mov [rbp - 8], rdi
    # .arg b i64
    mov [rbp - 16], rsi
    # LABEL while_start0
.align 16  # Loop alignment
.Lgcd_while_start0:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CMP_NE_CONST 0
    pop rax
    cmp rax, 0
    je .Lgcd_while_end1  # Optimized: removed setcc+movzx+push+pop+test
    # FUSED_LOAD_STORE 1 2 0
    mov rax, [rbp - 16]
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # MOD_I64 
    pop rbx
    pop rax
    cqo
    idiv rbx
    push rdx
    # FUSED_STORE_LOAD 1 2 0
    pop qword ptr [rbp - 16]  # Direct pop to memory
    mov rax, [rbp - 24]
    mov qword ptr [rbp - 8], rax  # Eliminated push/pop
    # JUMP while_start0
    jmp .Lgcd_while_start0
    # LABEL while_end1
.Lgcd_while_end1:
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lgcd_skip_labels:
    # .func is_prime i64 1

.align 16  # Function alignment
is_prime:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CMP_LE_CONST 1
    pop rax
    cmp rax, 1
    jg .Lpower_if_end0  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_I64 0
    mov rax, 0
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lis_prime_if_end0:
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CMP_LE_CONST 3
    pop rax
    cmp rax, 3
    jg .Lis_prime_if_end2  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_I64 1
    mov rax, 1
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end2
.Lis_prime_if_end2:
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # MOD_CONST_I64 2
    pop rax
    and rax, 1  # Fast mod by power-of-2
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    jne .Lis_prime_if_end4  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_I64 0
    mov rax, 0
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end4
.Lis_prime_if_end4:
    # STORE_CONST_I64 1 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    # LABEL for_start6
.align 16  # Loop alignment
.Lis_prime_for_start6:
    # LOAD 1 0
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 8]
    push rax
    # DIV_CONST_I64 2
    pop rax
    cqo
    mov rbx, 2
    idiv rbx
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    jge .Lmain_for_end8  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # ADD_CONST_I64 2
    pop rax
    add rax, 2
    push rax
    # DUP 
    mov rax, [rsp]
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # MUL_I64 
    pop rbx
    pop rax
    imul rax, rbx
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    jle .Lis_prime_if_end9  # Optimized: removed setcc+movzx+push+pop+test
    # JUMP for_end8
    jmp .Lmain_for_end8
    # LABEL if_end9
.Lis_prime_if_end9:
    # LOAD2_MOD_I64 0 2
    mov rax, [rbp - 8]
    xor rdx, rdx
    mov rbx, [rbp - 24]
    idiv rbx
    push rdx
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    jne .Lis_prime_if_end11  # Optimized: removed setcc+movzx+push+pop+test
    # CONST_I64 0
    mov rax, 0
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end11
.Lis_prime_if_end11:
    # INC_LOCAL 1
    inc qword ptr [rbp - 16]
    # JUMP for_start6
    jmp .Lis_prime_for_start6
    # LABEL for_end8
.Lis_prime_for_end8:
    # CONST_I64 1
    mov rax, 1
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lis_prime_skip_labels:
    # .func build_list i64 1

.align 16  # Function alignment
build_list:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg size i64
    mov [rbp - 8], rdi
    # .local result i64
    # LIST_NEW 
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_new_aligned_0
    sub rsp, 8
    call runtime_list_new
    add rsp, 8
    jmp .Lruntime_list_new_done_0
.Lruntime_list_new_aligned_0: 
    call runtime_list_new
.Lruntime_list_new_done_0: 
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # STORE_CONST_I64 2 0
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lbuild_list_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lmain_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1 2
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 24]
    push rax
    # MUL_CONST_I64 2
    pop rax
    add rax, rax  # Multiply by 2
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1
.Lruntime_list_append_int_aligned_1: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1: 
    push rdi
    # STORE 1
    pop qword ptr [rbp - 16]  # Direct pop to memory
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lbuild_list_for_start0
    # LABEL for_end2
.Lbuild_list_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lbuild_list_skip_labels:
    # .func sum_list i64 1

.align 16  # Function alignment
sum_list:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg lst i64
    mov [rbp - 8], rdi
    # .local len_lst i64
    # .local total i64
    # CONST_I64 0
    mov rax, 0
    # FUSED_STORE_LOAD 2 0
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_2
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_2
.Lruntime_list_len_aligned_2: 
    call runtime_list_len
.Lruntime_list_len_done_2: 
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lsum_list_for_start0:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Lbuild_list_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2 0 3
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 32]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_3
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_3
.Lruntime_list_get_int_aligned_3: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_3: 
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start0
    jmp .Lsum_list_for_start0
    # LABEL for_end2
.Lsum_list_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lsum_list_skip_labels:
    # .func filter_even i64 1

.align 16  # Function alignment
filter_even:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg lst i64
    mov [rbp - 8], rdi
    # .local len_lst i64
    # .local result i64
    # LIST_NEW 
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_new_aligned_4
    sub rsp, 8
    call runtime_list_new
    add rsp, 8
    jmp .Lruntime_list_new_done_4
.Lruntime_list_new_aligned_4: 
    call runtime_list_new
.Lruntime_list_new_done_4: 
    # FUSED_STORE_LOAD 2 0
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_5
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_5
.Lruntime_list_len_aligned_5: 
    call runtime_list_len
.Lruntime_list_len_done_5: 
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lfilter_even_for_start0:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Lsum_list_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 0 3
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 32]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_6
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_6
.Lruntime_list_get_int_aligned_6: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_6: 
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 4
    mov qword ptr [rbp - 40], rax  # Eliminated push/pop
    # MOD_CONST_I64 2
    pop rax
    and rax, 1  # Fast mod by power-of-2
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    jne .Lbreak_continue_test_if_end3  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2 4
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 40]
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_7
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_7
.Lruntime_list_append_int_aligned_7: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_7: 
    push rdi
    # STORE 2
    pop qword ptr [rbp - 24]  # Direct pop to memory
    # LABEL if_end3
.Lfilter_even_if_end3:
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start0
    jmp .Lfilter_even_for_start0
    # LABEL for_end2
.Lfilter_even_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lfilter_even_skip_labels:
    # .func reverse_list i64 1

.align 16  # Function alignment
reverse_list:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg lst i64
    mov [rbp - 8], rdi
    # .local len_lst i64
    # .local result i64
    # LIST_NEW 
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_new_aligned_8
    sub rsp, 8
    call runtime_list_new
    add rsp, 8
    jmp .Lruntime_list_new_done_8
.Lruntime_list_new_aligned_8: 
    call runtime_list_new
.Lruntime_list_new_done_8: 
    # FUSED_STORE_LOAD 2 0
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_9
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_9
.Lruntime_list_len_aligned_9: 
    call runtime_list_len
.Lruntime_list_len_done_9: 
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lreverse_list_for_start0:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Lfilter_even_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2 0 1 3
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 32]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # SUB_CONST_I64 1
    pop rax
    sub rax, 1
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_10
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_10
.Lruntime_list_get_int_aligned_10: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_10: 
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_11
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_11
.Lruntime_list_append_int_aligned_11: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_11: 
    push rdi
    # STORE 2
    pop qword ptr [rbp - 24]  # Direct pop to memory
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start0
    jmp .Lreverse_list_for_start0
    # LABEL for_end2
.Lreverse_list_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lreverse_list_skip_labels:
    # .func merge_lists i64 2

.align 16  # Function alignment
merge_lists:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg a i64
    mov [rbp - 8], rdi
    # .arg b i64
    mov [rbp - 16], rsi
    # .local len_b i64
    # .local result i64
    # FUSED_LOAD_STORE 0 3 1
    mov rax, [rbp - 8]
    mov qword ptr [rbp - 32], rax  # Eliminated push/pop
    mov rax, [rbp - 16]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_12
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_12
.Lruntime_list_len_aligned_12: 
    call runtime_list_len
.Lruntime_list_len_done_12: 
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # STORE_CONST_I64 4 0
    mov qword ptr [rbp - 40], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lmerge_lists_for_start0:
    # LOAD2_CMP_LT 4 2
    mov rax, [rbp - 40]
    cmp rax, [rbp - 24]
    jge .Lreverse_list_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 3 1 4
    mov rax, [rbp - 32]
    push rax
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 40]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_13
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_13
.Lruntime_list_get_int_aligned_13: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_13: 
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_14
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_14
.Lruntime_list_append_int_aligned_14: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_14: 
    push rdi
    # STORE 3
    pop qword ptr [rbp - 32]  # Direct pop to memory
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # JUMP for_start0
    jmp .Lmerge_lists_for_start0
    # LABEL for_end2
.Lmerge_lists_for_end2:
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lmerge_lists_skip_labels:
    # .func list_max i64 1

.align 16  # Function alignment
list_max:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg lst i64
    mov [rbp - 8], rdi
    # .local len_lst i64
    # .local max_val i64
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_15
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_15
.Lruntime_list_get_int_aligned_15: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_15: 
    # FUSED_STORE_LOAD 2 0
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_16
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_16
.Lruntime_list_len_aligned_16: 
    call runtime_list_len
.Lruntime_list_len_done_16: 
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Llist_max_for_start0:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Lmerge_lists_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 0 3
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 32]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_17
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_17
.Lruntime_list_get_int_aligned_17: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_17: 
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 4
    mov qword ptr [rbp - 40], rax  # Eliminated push/pop
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    jle .Lfilter_even_if_end3  # Optimized: removed setcc+movzx+push+pop+test
    # FUSED_LOAD_STORE 4 2
    mov rax, [rbp - 40]
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # LABEL if_end3
.Llist_max_if_end3:
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start0
    jmp .Llist_max_for_start0
    # LABEL for_end2
.Llist_max_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Llist_max_skip_labels:
    # .func string_repeat str 2

.align 16  # Function alignment
string_repeat:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg s str
    mov [rbp - 8], rdi
    # .arg n i64
    mov [rbp - 16], rsi
    # .local result str
    # CONST_STR ""
    lea rax, [.STR2]
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lstring_repeat_for_start0:
    # LOAD2_CMP_LT 3 1
    mov rax, [rbp - 32]
    cmp rax, [rbp - 16]
    jge .Llist_max_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2 0
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 8]
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rsi
    pop rsi
    push rdi
    mov rdi, rsi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_18
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_18
.Lruntime_int_to_str_aligned_18: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_18: 
    mov rsi, rax
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_19
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_19
.Lruntime_str_concat_checked_aligned_19: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_19: 
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start0
    jmp .Lstring_repeat_for_start0
    # LABEL for_end2
.Lstring_repeat_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lstring_repeat_skip_labels:
    # .func count_char i64 2

.align 16  # Function alignment
count_char:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg s str
    mov [rbp - 8], rdi
    # .arg ch str
    mov [rbp - 16], rsi
    # .local count i64
    # .local len_s i64
    # CONST_I64 0
    mov rax, 0
    # FUSED_STORE_LOAD 2 0
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_20
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_20
.Lruntime_list_len_aligned_20: 
    call runtime_list_len
.Lruntime_list_len_done_20: 
    # STORE 3
    mov qword ptr [rbp - 32], rax  # Eliminated push/pop
    # STORE_CONST_I64 4 0
    mov qword ptr [rbp - 40], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lcount_char_for_start0:
    # LOAD2_CMP_LT 4 3
    mov rax, [rbp - 40]
    cmp rax, [rbp - 32]
    jge .Lstring_repeat_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 0 4
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 40]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_get_int_aligned_21
    sub rsp, 8
    call runtime_list_get_int
    add rsp, 8
    jmp .Lruntime_list_get_int_done_21
.Lruntime_list_get_int_aligned_21: 
    call runtime_list_get_int
.Lruntime_list_get_int_done_21: 
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CMP_EQ 
    pop rbx
    pop rax
    cmp rax, rbx
    jne .Llist_max_if_end3  # Optimized: removed setcc+movzx+push+pop+test
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # LABEL if_end3
.Lcount_char_if_end3:
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # JUMP for_start0
    jmp .Lcount_char_for_start0
    # LABEL for_end2
.Lcount_char_for_end2:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lcount_char_skip_labels:
    # .func switch_test i64 1

.align 16  # Function alignment
switch_test:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg iterations i64
    mov [rbp - 8], rdi
    # .local sum i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lswitch_test_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lcount_char_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 10
    pop rax
    mov rcx, 10  # Load modulo constant
    mov rdx, rax  # Save original
    sub rax, rcx  # Try subtract
    test rax, rax  # Check if negative
    cmovl rax, rdx  # Restore if negative (branchless)
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 3
    mov qword ptr [rbp - 32], rax  # Eliminated push/pop
    # DUP 
    mov rax, [rsp]
    # STORE 4
    mov qword ptr [rbp - 40], rax  # Eliminated push/pop
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    je .Lswitch_test_case_04  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # SWITCH_JUMP_TABLE 1 9 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 switch_opt_0 default14
    pop rax
    cmp rax, 1
    jl .Lswitch_test_default14
    cmp rax, 9
    jg .Lswitch_test_default14
    sub rax, 1
    cmp rax, 0
    je .Lswitch_test_switch_opt_0
    cmp rax, 1
    je .Lswitch_test_switch_opt_0
    cmp rax, 2
    je .Lswitch_test_switch_opt_0
    cmp rax, 3
    je .Lswitch_test_switch_opt_0
    cmp rax, 4
    je .Lswitch_test_switch_opt_0
    cmp rax, 5
    je .Lswitch_test_switch_opt_0
    cmp rax, 6
    je .Lswitch_test_switch_opt_0
    cmp rax, 7
    je .Lswitch_test_switch_opt_0
    cmp rax, 8
    je .Lswitch_test_switch_opt_0
    jmp .Lswitch_test_default14
    # LABEL case_04
.Lswitch_test_case_04:
    # INC_LOCAL 1
    inc qword ptr [rbp - 16]
    # JUMP switch_end3
    jmp .Lswitch_test_switch_end3
    # LABEL switch_opt_0
.Lswitch_test_switch_opt_0:
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # ADD_CONST_I64 1
    pop rax
    add rax, 1
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # JUMP switch_end3
    jmp .Lswitch_test_switch_end3
    # LABEL default14
    # Removed 1 dead instruction(s)
.Lswitch_test_default14:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # ADD_CONST_I64 0
    pop rax
    # Removed add rax, 0
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # LABEL switch_end3
.Lswitch_test_switch_end3:
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lswitch_test_for_start0
    # LABEL for_end2
.Lswitch_test_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    ret
    # .end 
.Lswitch_test_skip_labels:
    # .func while_loop_test i64 1

.align 16  # Function alignment
while_loop_test:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local count i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lwhile_loop_test_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lswitch_test_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # INC_LOCAL 1
    inc qword ptr [rbp - 16]
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lwhile_loop_test_for_start0
    # LABEL for_end2
.Lwhile_loop_test_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lwhile_loop_test_skip_labels:
    # .func nested_loops i64 1

.align 16  # Function alignment
nested_loops:
    push rbp
    mov rbp, rsp
    sub rsp, 48  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local result i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lnested_loops_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lwhile_loop_test_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start3
.align 16  # Loop alignment
.Lnested_loops_for_start3:
    # LOAD2_CMP_LT 3 0
    mov rax, [rbp - 32]
    cmp rax, [rbp - 8]
    jge .Lmain_for_end5  # Optimized: removed setcc+movzx+push+pop+test
    # STORE_CONST_I64 4 0
    mov qword ptr [rbp - 40], 0  # Immediate store
    # LABEL for_start6
.align 16  # Loop alignment
.Lnested_loops_for_start6:
    # LOAD2_CMP_LT 4 0
    mov rax, [rbp - 40]
    cmp rax, [rbp - 8]
    jge .Lis_prime_for_end8  # Optimized: removed setcc+movzx+push+pop+test
    # INC_LOCAL 1
    inc qword ptr [rbp - 16]
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # JUMP for_start6
    jmp .Lnested_loops_for_start6
    # LABEL for_end8
.Lnested_loops_for_end8:
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start3
    jmp .Lnested_loops_for_start3
    # LABEL for_end5
.Lnested_loops_for_end5:
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lnested_loops_for_start0
    # LABEL for_end2
.Lnested_loops_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lnested_loops_skip_labels:
    # .func matrix_multiply_sum i64 1

.align 16  # Function alignment
matrix_multiply_sum:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg size i64
    mov [rbp - 8], rdi
    # .local sum i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lmatrix_multiply_sum_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lnested_loops_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL for_start3
.align 16  # Loop alignment
.Lmatrix_multiply_sum_for_start3:
    # LOAD2_CMP_LT 3 0
    mov rax, [rbp - 32]
    cmp rax, [rbp - 8]
    jge .Lnested_loops_for_end5  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1 2 3
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 32]
    push rax
    # MUL_I64 
    pop rbx
    pop rax
    imul rax, rbx
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP for_start3
    jmp .Lmatrix_multiply_sum_for_start3
    # LABEL for_end5
.Lmatrix_multiply_sum_for_end5:
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lmatrix_multiply_sum_for_start0
    # LABEL for_end2
.Lmatrix_multiply_sum_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lmatrix_multiply_sum_skip_labels:
    # .func complex_conditions i64 1

.align 16  # Function alignment
complex_conditions:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local count i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lcomplex_conditions_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lmatrix_multiply_sum_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 2
    pop rax
    and rax, 1  # Fast mod by power-of-2
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    sete al
    movzx rax, al
    push rax
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 3
    pop rax
    mov rcx, 3  # Load modulo constant
    mov rdx, rax  # Save original
    sub rax, rcx  # Try subtract
    test rax, rax  # Check if negative
    cmovl rax, rdx  # Restore if negative (branchless)
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    sete al
    movzx rax, al
    push rax
    # AND 
    pop rbx
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end3
    pop rax
    test rax, rax
    jz .Lcount_char_if_end3
    # INC_LOCAL 1
    inc qword ptr [rbp - 16]
    # LABEL if_end3
.Lcomplex_conditions_if_end3:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 5
    pop rax
    mov rcx, 5  # Load modulo constant
    mov rdx, rax  # Save original
    sub rax, rcx  # Try subtract
    test rax, rax  # Check if negative
    cmovl rax, rdx  # Restore if negative (branchless)
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    sete al
    movzx rax, al
    push rax
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 7
    pop rax
    mov rcx, 7  # Load modulo constant
    mov rdx, rax  # Save original
    sub rax, rcx  # Try subtract
    test rax, rax  # Check if negative
    cmovl rax, rdx  # Restore if negative (branchless)
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    sete al
    movzx rax, al
    push rax
    # OR 
    pop rbx
    pop rax
    or rax, rbx
    test rax, rax
    jz .Lbreak_continue_test_if_end5  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # ADD_CONST_I64 2
    pop rax
    add rax, 2
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # LABEL if_end5
.Lcomplex_conditions_if_end5:
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lcomplex_conditions_for_start0
    # LABEL for_end2
.Lcomplex_conditions_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lcomplex_conditions_skip_labels:
    # .func break_continue_test i64 1

.align 16  # Function alignment
break_continue_test:
    push rbp
    mov rbp, rsp
    sub rsp, 32  # Optimized frame size (was 256)
    # .arg n i64
    mov [rbp - 8], rdi
    # .local sum i64
    # STORE_CONST_I64 1 0 2 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lbreak_continue_test_for_start0:
    # LOAD2_CMP_LT 2 0
    mov rax, [rbp - 24]
    cmp rax, [rbp - 8]
    jge .Lcomplex_conditions_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 10
    pop rax
    mov rcx, 10  # Load modulo constant
    mov rdx, rax  # Save original
    sub rax, rcx  # Try subtract
    test rax, rax  # Check if negative
    cmovl rax, rdx  # Restore if negative (branchless)
    push rax
    # CMP_EQ_CONST 0
    pop rax
    cmp rax, 0
    jne .Lcomplex_conditions_if_end3  # Optimized: removed setcc+movzx+push+pop+test
    # JUMP for_continue1
    jmp .Lbreak_continue_test_for_continue1
    # LABEL if_end3
.Lbreak_continue_test_if_end3:
    # LOAD 2 0
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 8]
    push rax
    # DIV_CONST_I64 2
    pop rax
    cqo
    mov rbx, 2
    idiv rbx
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    jle .Lcomplex_conditions_if_end5  # Optimized: removed setcc+movzx+push+pop+test
    # JUMP for_end2
    jmp .Lcomplex_conditions_for_end2
    # LABEL if_end5
.Lbreak_continue_test_if_end5:
    # LOAD2_ADD_I64 1 2
    mov rax, [rbp - 16]
    add rax, [rbp - 24]
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # LABEL for_continue1
.Lbreak_continue_test_for_continue1:
    # INC_LOCAL 2
    inc qword ptr [rbp - 24]
    # JUMP for_start0
    jmp .Lbreak_continue_test_for_start0
    # LABEL for_end2
.Lbreak_continue_test_for_end2:
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lbreak_continue_test_skip_labels:
    # .func main void 0

.align 16  # Function alignment
main:
    push rbp
    mov rbp, rsp
    sub rsp, 176  # Optimized frame size (was 256)
    # .local bc_result i64
    # .local char_count i64
    # .local cond_result i64
    # .local fact_result i64
    # .local fib_result i64
    # .local filtered i64
    # .local filtered_sum i64
    # .local gcd_sum i64
    # .local list_sum i64
    # .local matrix_sum i64
    # .local merged i64
    # .local nested_result i64
    # .local pow_result f64
    # .local prime_count i64
    # .local repeated str
    # .local reversed i64
    # .local search_str str
    # .local small_list i64
    # .local switch_result i64
    # .local test_list i64
    # .local while_result i64
    # CONST_STR "=== Starting Comprehensive Benchmark ==="
    lea rax, [.STR3]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_27
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_27
.Lruntime_println_str_aligned_27: 
    call runtime_println_str
.Lruntime_println_str_done_27: 
    # CONST_STR ""
    lea rax, [.STR2]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_28
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_28
.Lruntime_println_str_aligned_28: 
    call runtime_println_str
.Lruntime_println_str_done_28: 
    # CONST_STR "Running math benchmarks..."
    lea rax, [.STR4]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_29
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_29
.Lruntime_println_str_aligned_29: 
    call runtime_println_str
.Lruntime_println_str_done_29: 
    # STORE_CONST_I64 4 0 21 0
    mov qword ptr [rbp - 40], 0  # Immediate store
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lmain_for_start0:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 1000
    pop rax
    cmp rax, 1000
    jge .Lbreak_continue_test_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # CONST_I64 1000
    mov rax, 1000
    push rax
    # CALL fibonacci 1
    pop rdi
    call fibonacci
    mov rbx, rax  # Optimized result transfer
    pop rax
    add rax, rbx
    # STORE 4
    mov qword ptr [rbp - 40], rax  # Eliminated push/pop
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start0
    jmp .Lmain_for_start0
    # LABEL for_end2
.Lmain_for_end2:
    # CONST_STR "Fibonacci sum: "
    lea rax, [.STR5]
    push rax
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_30
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_30
.Lruntime_int_to_str_aligned_30: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_30: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_31
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_31
.Lruntime_str_concat_checked_aligned_31: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_31: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_32
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_32
.Lruntime_println_str_aligned_32: 
    call runtime_println_str
.Lruntime_println_str_done_32: 
    # STORE_CONST_I64 3 0 21 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start3
.align 16  # Loop alignment
.Lmain_for_start3:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 10000
    pop rax
    cmp rax, 10000
    jge .Lmatrix_multiply_sum_for_end5  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CONST_I64 100
    mov rax, 100
    push rax
    # CALL factorial 1
    pop rdi
    call factorial
    mov rbx, rax  # Optimized result transfer
    pop rax
    add rax, rbx
    # STORE 3
    mov qword ptr [rbp - 32], rax  # Eliminated push/pop
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start3
    jmp .Lmain_for_start3
    # LABEL for_end5
.Lmain_for_end5:
    # CONST_STR "Factorial sum: "
    lea rax, [.STR6]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_33
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_33
.Lruntime_int_to_str_aligned_33: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_33: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_34
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_34
.Lruntime_str_concat_checked_aligned_34: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_34: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_35
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_35
.Lruntime_println_str_aligned_35: 
    call runtime_println_str
.Lruntime_println_str_done_35: 
    # STORE_CONST_F64 12 0.0
    movsd xmm0, [.FLOAT7]
    movsd [rbp - 104], xmm0
    # STORE_CONST_I64 21 0
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start6
.align 16  # Loop alignment
.Lmain_for_start6:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 10000
    pop rax
    cmp rax, 10000
    jge .Lnested_loops_for_end8  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 12
    mov rax, [rbp - 104]
    push rax
    # CONST_F64 5.7
    movsd xmm0, [.FLOAT8]
    sub rsp, 8
    movsd [rsp], xmm0
    # CONST_I64 100
    mov rax, 100
    push rax
    # CALL power 2
    pop rsi
    pop rdi
    call power
    push rax
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 12
    pop qword ptr [rbp - 104]  # Direct pop to memory
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start6
    jmp .Lmain_for_start6
    # LABEL for_end8
.Lmain_for_end8:
    # CONST_STR "Power sum: "
    lea rax, [.STR9]
    push rax
    # LOAD 12
    mov rax, [rbp - 104]
    push rax
    # BUILTIN_STR 
    movsd xmm0, [rsp]
    add rsp, 8
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_float_to_str_aligned_36
    sub rsp, 8
    call runtime_float_to_str
    add rsp, 8
    jmp .Lruntime_float_to_str_done_36
.Lruntime_float_to_str_aligned_36: 
    call runtime_float_to_str
.Lruntime_float_to_str_done_36: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_37
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_37
.Lruntime_str_concat_checked_aligned_37: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_37: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_38
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_38
.Lruntime_println_str_aligned_38: 
    call runtime_println_str
.Lruntime_println_str_done_38: 
    # STORE_CONST_I64 7 0 21 0
    mov qword ptr [rbp - 64], 0  # Immediate store
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start9
.align 16  # Loop alignment
.Lmain_for_start9:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 1000
    pop rax
    cmp rax, 1000
    jge .Lmain_for_end11  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 7
    mov rax, [rbp - 64]
    push rax
    # CONST_I64 48 18
    mov rax, 48
    push rax
    mov rax, 18
    push rax
    # CALL gcd 2
    pop rsi
    pop rdi
    call gcd
    mov rbx, rax  # Optimized result transfer
    pop rax
    add rax, rbx
    # STORE 7
    mov qword ptr [rbp - 64], rax  # Eliminated push/pop
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start9
    jmp .Lmain_for_start9
    # LABEL for_end11
.Lmain_for_end11:
    # CONST_STR "GCD sum: "
    lea rax, [.STR10]
    push rax
    # LOAD 7
    mov rax, [rbp - 64]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_39
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_39
.Lruntime_int_to_str_aligned_39: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_39: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_40
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_40
.Lruntime_str_concat_checked_aligned_40: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_40: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_41
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_41
.Lruntime_println_str_aligned_41: 
    call runtime_println_str
.Lruntime_println_str_done_41: 
    # STORE_CONST_I64 13 0 21 0
    mov qword ptr [rbp - 112], 0  # Immediate store
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start12
.align 16  # Loop alignment
.Lmain_for_start12:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 10000
    pop rax
    cmp rax, 10000
    jge .Lmain_for_end14  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CALL is_prime 1
    pop rdi
    call is_prime
    # Removed redundant push rax; pop rax
    test rax, rax
    jz .Lmain_if_end15
    # INC_LOCAL 13
    inc qword ptr [rbp - 112]
    # LABEL if_end15
.Lmain_if_end15:
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start12
    jmp .Lmain_for_start12
    # LABEL for_end14
.Lmain_for_end14:
    # CONST_STR "Prime checks: "
    lea rax, [.STR11]
    push rax
    # LOAD 13
    mov rax, [rbp - 112]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_42
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_42
.Lruntime_int_to_str_aligned_42: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_42: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_43
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_43
.Lruntime_str_concat_checked_aligned_43: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_43: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_44
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_44
.Lruntime_println_str_aligned_44: 
    call runtime_println_str
.Lruntime_println_str_done_44: 
    # CONST_STR ""
    lea rax, [.STR2]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_45
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_45
.Lruntime_println_str_aligned_45: 
    call runtime_println_str
.Lruntime_println_str_done_45: 
    # CONST_STR "Running list benchmarks..."
    lea rax, [.STR12]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_46
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_46
.Lruntime_println_str_aligned_46: 
    call runtime_println_str
.Lruntime_println_str_done_46: 
    # LIST_NEW_I64 1000 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 44 46 48 50 52 54 56 58 60 62 64 66 68 70 72 74 76 78 80 82 84 86 88 90 92 94 96 98 100 102 104 106 108 110 112 114 116 118 120 122 124 126 128 130 132 134 136 138 140 142 144 146 148 150 152 154 156 158 160 162 164 166 168 170 172 174 176 178 180 182 184 186 188 190 192 194 196 198 200 202 204 206 208 210 212 214 216 218 220 222 224 226 228 230 232 234 236 238 240 242 244 246 248 250 252 254 256 258 260 262 264 266 268 270 272 274 276 278 280 282 284 286 288 290 292 294 296 298 300 302 304 306 308 310 312 314 316 318 320 322 324 326 328 330 332 334 336 338 340 342 344 346 348 350 352 354 356 358 360 362 364 366 368 370 372 374 376 378 380 382 384 386 388 390 392 394 396 398 400 402 404 406 408 410 412 414 416 418 420 422 424 426 428 430 432 434 436 438 440 442 444 446 448 450 452 454 456 458 460 462 464 466 468 470 472 474 476 478 480 482 484 486 488 490 492 494 496 498 500 502 504 506 508 510 512 514 516 518 520 522 524 526 528 530 532 534 536 538 540 542 544 546 548 550 552 554 556 558 560 562 564 566 568 570 572 574 576 578 580 582 584 586 588 590 592 594 596 598 600 602 604 606 608 610 612 614 616 618 620 622 624 626 628 630 632 634 636 638 640 642 644 646 648 650 652 654 656 658 660 662 664 666 668 670 672 674 676 678 680 682 684 686 688 690 692 694 696 698 700 702 704 706 708 710 712 714 716 718 720 722 724 726 728 730 732 734 736 738 740 742 744 746 748 750 752 754 756 758 760 762 764 766 768 770 772 774 776 778 780 782 784 786 788 790 792 794 796 798 800 802 804 806 808 810 812 814 816 818 820 822 824 826 828 830 832 834 836 838 840 842 844 846 848 850 852 854 856 858 860 862 864 866 868 870 872 874 876 878 880 882 884 886 888 890 892 894 896 898 900 902 904 906 908 910 912 914 916 918 920 922 924 926 928 930 932 934 936 938 940 942 944 946 948 950 952 954 956 958 960 962 964 966 968 970 972 974 976 978 980 982 984 986 988 990 992 994 996 998 1000 1002 1004 1006 1008 1010 1012 1014 1016 1018 1020 1022 1024 1026 1028 1030 1032 1034 1036 1038 1040 1042 1044 1046 1048 1050 1052 1054 1056 1058 1060 1062 1064 1066 1068 1070 1072 1074 1076 1078 1080 1082 1084 1086 1088 1090 1092 1094 1096 1098 1100 1102 1104 1106 1108 1110 1112 1114 1116 1118 1120 1122 1124 1126 1128 1130 1132 1134 1136 1138 1140 1142 1144 1146 1148 1150 1152 1154 1156 1158 1160 1162 1164 1166 1168 1170 1172 1174 1176 1178 1180 1182 1184 1186 1188 1190 1192 1194 1196 1198 1200 1202 1204 1206 1208 1210 1212 1214 1216 1218 1220 1222 1224 1226 1228 1230 1232 1234 1236 1238 1240 1242 1244 1246 1248 1250 1252 1254 1256 1258 1260 1262 1264 1266 1268 1270 1272 1274 1276 1278 1280 1282 1284 1286 1288 1290 1292 1294 1296 1298 1300 1302 1304 1306 1308 1310 1312 1314 1316 1318 1320 1322 1324 1326 1328 1330 1332 1334 1336 1338 1340 1342 1344 1346 1348 1350 1352 1354 1356 1358 1360 1362 1364 1366 1368 1370 1372 1374 1376 1378 1380 1382 1384 1386 1388 1390 1392 1394 1396 1398 1400 1402 1404 1406 1408 1410 1412 1414 1416 1418 1420 1422 1424 1426 1428 1430 1432 1434 1436 1438 1440 1442 1444 1446 1448 1450 1452 1454 1456 1458 1460 1462 1464 1466 1468 1470 1472 1474 1476 1478 1480 1482 1484 1486 1488 1490 1492 1494 1496 1498 1500 1502 1504 1506 1508 1510 1512 1514 1516 1518 1520 1522 1524 1526 1528 1530 1532 1534 1536 1538 1540 1542 1544 1546 1548 1550 1552 1554 1556 1558 1560 1562 1564 1566 1568 1570 1572 1574 1576 1578 1580 1582 1584 1586 1588 1590 1592 1594 1596 1598 1600 1602 1604 1606 1608 1610 1612 1614 1616 1618 1620 1622 1624 1626 1628 1630 1632 1634 1636 1638 1640 1642 1644 1646 1648 1650 1652 1654 1656 1658 1660 1662 1664 1666 1668 1670 1672 1674 1676 1678 1680 1682 1684 1686 1688 1690 1692 1694 1696 1698 1700 1702 1704 1706 1708 1710 1712 1714 1716 1718 1720 1722 1724 1726 1728 1730 1732 1734 1736 1738 1740 1742 1744 1746 1748 1750 1752 1754 1756 1758 1760 1762 1764 1766 1768 1770 1772 1774 1776 1778 1780 1782 1784 1786 1788 1790 1792 1794 1796 1798 1800 1802 1804 1806 1808 1810 1812 1814 1816 1818 1820 1822 1824 1826 1828 1830 1832 1834 1836 1838 1840 1842 1844 1846 1848 1850 1852 1854 1856 1858 1860 1862 1864 1866 1868 1870 1872 1874 1876 1878 1880 1882 1884 1886 1888 1890 1892 1894 1896 1898 1900 1902 1904 1906 1908 1910 1912 1914 1916 1918 1920 1922 1924 1926 1928 1930 1932 1934 1936 1938 1940 1942 1944 1946 1948 1950 1952 1954 1956 1958 1960 1962 1964 1966 1968 1970 1972 1974 1976 1978 1980 1982 1984 1986 1988 1990 1992 1994 1996 1998
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_new_aligned_47
    sub rsp, 8
    call runtime_list_new
    add rsp, 8
    jmp .Lruntime_list_new_done_47
.Lruntime_list_new_aligned_47: 
    call runtime_list_new
.Lruntime_list_new_done_47: 
    mov dword ptr [rax + 24], 0  # elem_type = 0 (int)
    push rax
    mov rdi, [rsp]
    mov rsi, 0
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_48
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_48
.Lruntime_list_append_int_aligned_48: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_48: 
    mov rdi, [rsp]
    mov rsi, 2
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_49
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_49
.Lruntime_list_append_int_aligned_49: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_49: 
    mov rdi, [rsp]
    mov rsi, 4
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_50
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_50
.Lruntime_list_append_int_aligned_50: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_50: 
    mov rdi, [rsp]
    mov rsi, 6
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_51
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_51
.Lruntime_list_append_int_aligned_51: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_51: 
    mov rdi, [rsp]
    mov rsi, 8
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_52
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_52
.Lruntime_list_append_int_aligned_52: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_52: 
    mov rdi, [rsp]
    mov rsi, 10
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_53
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_53
.Lruntime_list_append_int_aligned_53: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_53: 
    mov rdi, [rsp]
    mov rsi, 12
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_54
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_54
.Lruntime_list_append_int_aligned_54: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_54: 
    mov rdi, [rsp]
    mov rsi, 14
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_55
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_55
.Lruntime_list_append_int_aligned_55: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_55: 
    mov rdi, [rsp]
    mov rsi, 16
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_56
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_56
.Lruntime_list_append_int_aligned_56: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_56: 
    mov rdi, [rsp]
    mov rsi, 18
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_57
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_57
.Lruntime_list_append_int_aligned_57: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_57: 
    mov rdi, [rsp]
    mov rsi, 20
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_58
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_58
.Lruntime_list_append_int_aligned_58: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_58: 
    mov rdi, [rsp]
    mov rsi, 22
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_59
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_59
.Lruntime_list_append_int_aligned_59: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_59: 
    mov rdi, [rsp]
    mov rsi, 24
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_60
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_60
.Lruntime_list_append_int_aligned_60: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_60: 
    mov rdi, [rsp]
    mov rsi, 26
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_61
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_61
.Lruntime_list_append_int_aligned_61: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_61: 
    mov rdi, [rsp]
    mov rsi, 28
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_62
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_62
.Lruntime_list_append_int_aligned_62: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_62: 
    mov rdi, [rsp]
    mov rsi, 30
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_63
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_63
.Lruntime_list_append_int_aligned_63: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_63: 
    mov rdi, [rsp]
    mov rsi, 32
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_64
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_64
.Lruntime_list_append_int_aligned_64: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_64: 
    mov rdi, [rsp]
    mov rsi, 34
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_65
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_65
.Lruntime_list_append_int_aligned_65: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_65: 
    mov rdi, [rsp]
    mov rsi, 36
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_66
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_66
.Lruntime_list_append_int_aligned_66: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_66: 
    mov rdi, [rsp]
    mov rsi, 38
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_67
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_67
.Lruntime_list_append_int_aligned_67: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_67: 
    mov rdi, [rsp]
    mov rsi, 40
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_68
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_68
.Lruntime_list_append_int_aligned_68: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_68: 
    mov rdi, [rsp]
    mov rsi, 42
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_69
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_69
.Lruntime_list_append_int_aligned_69: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_69: 
    mov rdi, [rsp]
    mov rsi, 44
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_70
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_70
.Lruntime_list_append_int_aligned_70: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_70: 
    mov rdi, [rsp]
    mov rsi, 46
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_71
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_71
.Lruntime_list_append_int_aligned_71: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_71: 
    mov rdi, [rsp]
    mov rsi, 48
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_72
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_72
.Lruntime_list_append_int_aligned_72: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_72: 
    mov rdi, [rsp]
    mov rsi, 50
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_73
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_73
.Lruntime_list_append_int_aligned_73: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_73: 
    mov rdi, [rsp]
    mov rsi, 52
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_74
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_74
.Lruntime_list_append_int_aligned_74: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_74: 
    mov rdi, [rsp]
    mov rsi, 54
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_75
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_75
.Lruntime_list_append_int_aligned_75: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_75: 
    mov rdi, [rsp]
    mov rsi, 56
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_76
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_76
.Lruntime_list_append_int_aligned_76: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_76: 
    mov rdi, [rsp]
    mov rsi, 58
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_77
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_77
.Lruntime_list_append_int_aligned_77: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_77: 
    mov rdi, [rsp]
    mov rsi, 60
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_78
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_78
.Lruntime_list_append_int_aligned_78: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_78: 
    mov rdi, [rsp]
    mov rsi, 62
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_79
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_79
.Lruntime_list_append_int_aligned_79: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_79: 
    mov rdi, [rsp]
    mov rsi, 64
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_80
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_80
.Lruntime_list_append_int_aligned_80: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_80: 
    mov rdi, [rsp]
    mov rsi, 66
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_81
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_81
.Lruntime_list_append_int_aligned_81: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_81: 
    mov rdi, [rsp]
    mov rsi, 68
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_82
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_82
.Lruntime_list_append_int_aligned_82: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_82: 
    mov rdi, [rsp]
    mov rsi, 70
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_83
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_83
.Lruntime_list_append_int_aligned_83: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_83: 
    mov rdi, [rsp]
    mov rsi, 72
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_84
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_84
.Lruntime_list_append_int_aligned_84: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_84: 
    mov rdi, [rsp]
    mov rsi, 74
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_85
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_85
.Lruntime_list_append_int_aligned_85: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_85: 
    mov rdi, [rsp]
    mov rsi, 76
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_86
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_86
.Lruntime_list_append_int_aligned_86: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_86: 
    mov rdi, [rsp]
    mov rsi, 78
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_87
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_87
.Lruntime_list_append_int_aligned_87: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_87: 
    mov rdi, [rsp]
    mov rsi, 80
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_88
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_88
.Lruntime_list_append_int_aligned_88: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_88: 
    mov rdi, [rsp]
    mov rsi, 82
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_89
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_89
.Lruntime_list_append_int_aligned_89: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_89: 
    mov rdi, [rsp]
    mov rsi, 84
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_90
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_90
.Lruntime_list_append_int_aligned_90: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_90: 
    mov rdi, [rsp]
    mov rsi, 86
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_91
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_91
.Lruntime_list_append_int_aligned_91: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_91: 
    mov rdi, [rsp]
    mov rsi, 88
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_92
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_92
.Lruntime_list_append_int_aligned_92: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_92: 
    mov rdi, [rsp]
    mov rsi, 90
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_93
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_93
.Lruntime_list_append_int_aligned_93: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_93: 
    mov rdi, [rsp]
    mov rsi, 92
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_94
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_94
.Lruntime_list_append_int_aligned_94: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_94: 
    mov rdi, [rsp]
    mov rsi, 94
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_95
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_95
.Lruntime_list_append_int_aligned_95: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_95: 
    mov rdi, [rsp]
    mov rsi, 96
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_96
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_96
.Lruntime_list_append_int_aligned_96: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_96: 
    mov rdi, [rsp]
    mov rsi, 98
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_97
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_97
.Lruntime_list_append_int_aligned_97: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_97: 
    mov rdi, [rsp]
    mov rsi, 100
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_98
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_98
.Lruntime_list_append_int_aligned_98: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_98: 
    mov rdi, [rsp]
    mov rsi, 102
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_99
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_99
.Lruntime_list_append_int_aligned_99: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_99: 
    mov rdi, [rsp]
    mov rsi, 104
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_100
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_100
.Lruntime_list_append_int_aligned_100: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_100: 
    mov rdi, [rsp]
    mov rsi, 106
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_101
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_101
.Lruntime_list_append_int_aligned_101: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_101: 
    mov rdi, [rsp]
    mov rsi, 108
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_102
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_102
.Lruntime_list_append_int_aligned_102: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_102: 
    mov rdi, [rsp]
    mov rsi, 110
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_103
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_103
.Lruntime_list_append_int_aligned_103: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_103: 
    mov rdi, [rsp]
    mov rsi, 112
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_104
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_104
.Lruntime_list_append_int_aligned_104: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_104: 
    mov rdi, [rsp]
    mov rsi, 114
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_105
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_105
.Lruntime_list_append_int_aligned_105: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_105: 
    mov rdi, [rsp]
    mov rsi, 116
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_106
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_106
.Lruntime_list_append_int_aligned_106: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_106: 
    mov rdi, [rsp]
    mov rsi, 118
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_107
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_107
.Lruntime_list_append_int_aligned_107: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_107: 
    mov rdi, [rsp]
    mov rsi, 120
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_108
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_108
.Lruntime_list_append_int_aligned_108: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_108: 
    mov rdi, [rsp]
    mov rsi, 122
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_109
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_109
.Lruntime_list_append_int_aligned_109: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_109: 
    mov rdi, [rsp]
    mov rsi, 124
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_110
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_110
.Lruntime_list_append_int_aligned_110: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_110: 
    mov rdi, [rsp]
    mov rsi, 126
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_111
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_111
.Lruntime_list_append_int_aligned_111: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_111: 
    mov rdi, [rsp]
    mov rsi, 128
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_112
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_112
.Lruntime_list_append_int_aligned_112: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_112: 
    mov rdi, [rsp]
    mov rsi, 130
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_113
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_113
.Lruntime_list_append_int_aligned_113: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_113: 
    mov rdi, [rsp]
    mov rsi, 132
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_114
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_114
.Lruntime_list_append_int_aligned_114: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_114: 
    mov rdi, [rsp]
    mov rsi, 134
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_115
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_115
.Lruntime_list_append_int_aligned_115: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_115: 
    mov rdi, [rsp]
    mov rsi, 136
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_116
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_116
.Lruntime_list_append_int_aligned_116: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_116: 
    mov rdi, [rsp]
    mov rsi, 138
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_117
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_117
.Lruntime_list_append_int_aligned_117: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_117: 
    mov rdi, [rsp]
    mov rsi, 140
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_118
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_118
.Lruntime_list_append_int_aligned_118: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_118: 
    mov rdi, [rsp]
    mov rsi, 142
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_119
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_119
.Lruntime_list_append_int_aligned_119: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_119: 
    mov rdi, [rsp]
    mov rsi, 144
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_120
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_120
.Lruntime_list_append_int_aligned_120: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_120: 
    mov rdi, [rsp]
    mov rsi, 146
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_121
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_121
.Lruntime_list_append_int_aligned_121: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_121: 
    mov rdi, [rsp]
    mov rsi, 148
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_122
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_122
.Lruntime_list_append_int_aligned_122: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_122: 
    mov rdi, [rsp]
    mov rsi, 150
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_123
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_123
.Lruntime_list_append_int_aligned_123: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_123: 
    mov rdi, [rsp]
    mov rsi, 152
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_124
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_124
.Lruntime_list_append_int_aligned_124: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_124: 
    mov rdi, [rsp]
    mov rsi, 154
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_125
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_125
.Lruntime_list_append_int_aligned_125: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_125: 
    mov rdi, [rsp]
    mov rsi, 156
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_126
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_126
.Lruntime_list_append_int_aligned_126: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_126: 
    mov rdi, [rsp]
    mov rsi, 158
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_127
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_127
.Lruntime_list_append_int_aligned_127: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_127: 
    mov rdi, [rsp]
    mov rsi, 160
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_128
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_128
.Lruntime_list_append_int_aligned_128: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_128: 
    mov rdi, [rsp]
    mov rsi, 162
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_129
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_129
.Lruntime_list_append_int_aligned_129: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_129: 
    mov rdi, [rsp]
    mov rsi, 164
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_130
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_130
.Lruntime_list_append_int_aligned_130: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_130: 
    mov rdi, [rsp]
    mov rsi, 166
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_131
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_131
.Lruntime_list_append_int_aligned_131: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_131: 
    mov rdi, [rsp]
    mov rsi, 168
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_132
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_132
.Lruntime_list_append_int_aligned_132: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_132: 
    mov rdi, [rsp]
    mov rsi, 170
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_133
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_133
.Lruntime_list_append_int_aligned_133: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_133: 
    mov rdi, [rsp]
    mov rsi, 172
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_134
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_134
.Lruntime_list_append_int_aligned_134: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_134: 
    mov rdi, [rsp]
    mov rsi, 174
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_135
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_135
.Lruntime_list_append_int_aligned_135: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_135: 
    mov rdi, [rsp]
    mov rsi, 176
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_136
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_136
.Lruntime_list_append_int_aligned_136: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_136: 
    mov rdi, [rsp]
    mov rsi, 178
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_137
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_137
.Lruntime_list_append_int_aligned_137: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_137: 
    mov rdi, [rsp]
    mov rsi, 180
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_138
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_138
.Lruntime_list_append_int_aligned_138: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_138: 
    mov rdi, [rsp]
    mov rsi, 182
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_139
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_139
.Lruntime_list_append_int_aligned_139: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_139: 
    mov rdi, [rsp]
    mov rsi, 184
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_140
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_140
.Lruntime_list_append_int_aligned_140: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_140: 
    mov rdi, [rsp]
    mov rsi, 186
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_141
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_141
.Lruntime_list_append_int_aligned_141: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_141: 
    mov rdi, [rsp]
    mov rsi, 188
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_142
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_142
.Lruntime_list_append_int_aligned_142: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_142: 
    mov rdi, [rsp]
    mov rsi, 190
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_143
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_143
.Lruntime_list_append_int_aligned_143: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_143: 
    mov rdi, [rsp]
    mov rsi, 192
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_144
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_144
.Lruntime_list_append_int_aligned_144: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_144: 
    mov rdi, [rsp]
    mov rsi, 194
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_145
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_145
.Lruntime_list_append_int_aligned_145: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_145: 
    mov rdi, [rsp]
    mov rsi, 196
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_146
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_146
.Lruntime_list_append_int_aligned_146: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_146: 
    mov rdi, [rsp]
    mov rsi, 198
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_147
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_147
.Lruntime_list_append_int_aligned_147: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_147: 
    mov rdi, [rsp]
    mov rsi, 200
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_148
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_148
.Lruntime_list_append_int_aligned_148: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_148: 
    mov rdi, [rsp]
    mov rsi, 202
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_149
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_149
.Lruntime_list_append_int_aligned_149: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_149: 
    mov rdi, [rsp]
    mov rsi, 204
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_150
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_150
.Lruntime_list_append_int_aligned_150: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_150: 
    mov rdi, [rsp]
    mov rsi, 206
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_151
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_151
.Lruntime_list_append_int_aligned_151: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_151: 
    mov rdi, [rsp]
    mov rsi, 208
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_152
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_152
.Lruntime_list_append_int_aligned_152: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_152: 
    mov rdi, [rsp]
    mov rsi, 210
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_153
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_153
.Lruntime_list_append_int_aligned_153: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_153: 
    mov rdi, [rsp]
    mov rsi, 212
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_154
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_154
.Lruntime_list_append_int_aligned_154: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_154: 
    mov rdi, [rsp]
    mov rsi, 214
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_155
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_155
.Lruntime_list_append_int_aligned_155: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_155: 
    mov rdi, [rsp]
    mov rsi, 216
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_156
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_156
.Lruntime_list_append_int_aligned_156: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_156: 
    mov rdi, [rsp]
    mov rsi, 218
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_157
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_157
.Lruntime_list_append_int_aligned_157: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_157: 
    mov rdi, [rsp]
    mov rsi, 220
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_158
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_158
.Lruntime_list_append_int_aligned_158: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_158: 
    mov rdi, [rsp]
    mov rsi, 222
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_159
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_159
.Lruntime_list_append_int_aligned_159: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_159: 
    mov rdi, [rsp]
    mov rsi, 224
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_160
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_160
.Lruntime_list_append_int_aligned_160: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_160: 
    mov rdi, [rsp]
    mov rsi, 226
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_161
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_161
.Lruntime_list_append_int_aligned_161: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_161: 
    mov rdi, [rsp]
    mov rsi, 228
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_162
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_162
.Lruntime_list_append_int_aligned_162: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_162: 
    mov rdi, [rsp]
    mov rsi, 230
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_163
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_163
.Lruntime_list_append_int_aligned_163: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_163: 
    mov rdi, [rsp]
    mov rsi, 232
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_164
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_164
.Lruntime_list_append_int_aligned_164: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_164: 
    mov rdi, [rsp]
    mov rsi, 234
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_165
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_165
.Lruntime_list_append_int_aligned_165: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_165: 
    mov rdi, [rsp]
    mov rsi, 236
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_166
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_166
.Lruntime_list_append_int_aligned_166: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_166: 
    mov rdi, [rsp]
    mov rsi, 238
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_167
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_167
.Lruntime_list_append_int_aligned_167: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_167: 
    mov rdi, [rsp]
    mov rsi, 240
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_168
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_168
.Lruntime_list_append_int_aligned_168: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_168: 
    mov rdi, [rsp]
    mov rsi, 242
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_169
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_169
.Lruntime_list_append_int_aligned_169: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_169: 
    mov rdi, [rsp]
    mov rsi, 244
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_170
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_170
.Lruntime_list_append_int_aligned_170: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_170: 
    mov rdi, [rsp]
    mov rsi, 246
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_171
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_171
.Lruntime_list_append_int_aligned_171: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_171: 
    mov rdi, [rsp]
    mov rsi, 248
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_172
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_172
.Lruntime_list_append_int_aligned_172: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_172: 
    mov rdi, [rsp]
    mov rsi, 250
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_173
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_173
.Lruntime_list_append_int_aligned_173: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_173: 
    mov rdi, [rsp]
    mov rsi, 252
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_174
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_174
.Lruntime_list_append_int_aligned_174: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_174: 
    mov rdi, [rsp]
    mov rsi, 254
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_175
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_175
.Lruntime_list_append_int_aligned_175: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_175: 
    mov rdi, [rsp]
    mov rsi, 256
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_176
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_176
.Lruntime_list_append_int_aligned_176: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_176: 
    mov rdi, [rsp]
    mov rsi, 258
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_177
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_177
.Lruntime_list_append_int_aligned_177: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_177: 
    mov rdi, [rsp]
    mov rsi, 260
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_178
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_178
.Lruntime_list_append_int_aligned_178: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_178: 
    mov rdi, [rsp]
    mov rsi, 262
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_179
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_179
.Lruntime_list_append_int_aligned_179: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_179: 
    mov rdi, [rsp]
    mov rsi, 264
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_180
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_180
.Lruntime_list_append_int_aligned_180: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_180: 
    mov rdi, [rsp]
    mov rsi, 266
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_181
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_181
.Lruntime_list_append_int_aligned_181: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_181: 
    mov rdi, [rsp]
    mov rsi, 268
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_182
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_182
.Lruntime_list_append_int_aligned_182: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_182: 
    mov rdi, [rsp]
    mov rsi, 270
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_183
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_183
.Lruntime_list_append_int_aligned_183: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_183: 
    mov rdi, [rsp]
    mov rsi, 272
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_184
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_184
.Lruntime_list_append_int_aligned_184: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_184: 
    mov rdi, [rsp]
    mov rsi, 274
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_185
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_185
.Lruntime_list_append_int_aligned_185: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_185: 
    mov rdi, [rsp]
    mov rsi, 276
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_186
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_186
.Lruntime_list_append_int_aligned_186: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_186: 
    mov rdi, [rsp]
    mov rsi, 278
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_187
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_187
.Lruntime_list_append_int_aligned_187: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_187: 
    mov rdi, [rsp]
    mov rsi, 280
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_188
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_188
.Lruntime_list_append_int_aligned_188: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_188: 
    mov rdi, [rsp]
    mov rsi, 282
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_189
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_189
.Lruntime_list_append_int_aligned_189: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_189: 
    mov rdi, [rsp]
    mov rsi, 284
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_190
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_190
.Lruntime_list_append_int_aligned_190: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_190: 
    mov rdi, [rsp]
    mov rsi, 286
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_191
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_191
.Lruntime_list_append_int_aligned_191: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_191: 
    mov rdi, [rsp]
    mov rsi, 288
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_192
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_192
.Lruntime_list_append_int_aligned_192: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_192: 
    mov rdi, [rsp]
    mov rsi, 290
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_193
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_193
.Lruntime_list_append_int_aligned_193: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_193: 
    mov rdi, [rsp]
    mov rsi, 292
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_194
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_194
.Lruntime_list_append_int_aligned_194: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_194: 
    mov rdi, [rsp]
    mov rsi, 294
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_195
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_195
.Lruntime_list_append_int_aligned_195: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_195: 
    mov rdi, [rsp]
    mov rsi, 296
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_196
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_196
.Lruntime_list_append_int_aligned_196: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_196: 
    mov rdi, [rsp]
    mov rsi, 298
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_197
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_197
.Lruntime_list_append_int_aligned_197: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_197: 
    mov rdi, [rsp]
    mov rsi, 300
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_198
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_198
.Lruntime_list_append_int_aligned_198: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_198: 
    mov rdi, [rsp]
    mov rsi, 302
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_199
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_199
.Lruntime_list_append_int_aligned_199: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_199: 
    mov rdi, [rsp]
    mov rsi, 304
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_200
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_200
.Lruntime_list_append_int_aligned_200: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_200: 
    mov rdi, [rsp]
    mov rsi, 306
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_201
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_201
.Lruntime_list_append_int_aligned_201: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_201: 
    mov rdi, [rsp]
    mov rsi, 308
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_202
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_202
.Lruntime_list_append_int_aligned_202: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_202: 
    mov rdi, [rsp]
    mov rsi, 310
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_203
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_203
.Lruntime_list_append_int_aligned_203: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_203: 
    mov rdi, [rsp]
    mov rsi, 312
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_204
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_204
.Lruntime_list_append_int_aligned_204: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_204: 
    mov rdi, [rsp]
    mov rsi, 314
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_205
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_205
.Lruntime_list_append_int_aligned_205: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_205: 
    mov rdi, [rsp]
    mov rsi, 316
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_206
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_206
.Lruntime_list_append_int_aligned_206: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_206: 
    mov rdi, [rsp]
    mov rsi, 318
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_207
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_207
.Lruntime_list_append_int_aligned_207: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_207: 
    mov rdi, [rsp]
    mov rsi, 320
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_208
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_208
.Lruntime_list_append_int_aligned_208: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_208: 
    mov rdi, [rsp]
    mov rsi, 322
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_209
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_209
.Lruntime_list_append_int_aligned_209: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_209: 
    mov rdi, [rsp]
    mov rsi, 324
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_210
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_210
.Lruntime_list_append_int_aligned_210: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_210: 
    mov rdi, [rsp]
    mov rsi, 326
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_211
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_211
.Lruntime_list_append_int_aligned_211: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_211: 
    mov rdi, [rsp]
    mov rsi, 328
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_212
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_212
.Lruntime_list_append_int_aligned_212: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_212: 
    mov rdi, [rsp]
    mov rsi, 330
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_213
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_213
.Lruntime_list_append_int_aligned_213: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_213: 
    mov rdi, [rsp]
    mov rsi, 332
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_214
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_214
.Lruntime_list_append_int_aligned_214: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_214: 
    mov rdi, [rsp]
    mov rsi, 334
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_215
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_215
.Lruntime_list_append_int_aligned_215: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_215: 
    mov rdi, [rsp]
    mov rsi, 336
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_216
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_216
.Lruntime_list_append_int_aligned_216: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_216: 
    mov rdi, [rsp]
    mov rsi, 338
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_217
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_217
.Lruntime_list_append_int_aligned_217: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_217: 
    mov rdi, [rsp]
    mov rsi, 340
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_218
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_218
.Lruntime_list_append_int_aligned_218: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_218: 
    mov rdi, [rsp]
    mov rsi, 342
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_219
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_219
.Lruntime_list_append_int_aligned_219: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_219: 
    mov rdi, [rsp]
    mov rsi, 344
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_220
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_220
.Lruntime_list_append_int_aligned_220: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_220: 
    mov rdi, [rsp]
    mov rsi, 346
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_221
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_221
.Lruntime_list_append_int_aligned_221: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_221: 
    mov rdi, [rsp]
    mov rsi, 348
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_222
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_222
.Lruntime_list_append_int_aligned_222: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_222: 
    mov rdi, [rsp]
    mov rsi, 350
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_223
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_223
.Lruntime_list_append_int_aligned_223: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_223: 
    mov rdi, [rsp]
    mov rsi, 352
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_224
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_224
.Lruntime_list_append_int_aligned_224: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_224: 
    mov rdi, [rsp]
    mov rsi, 354
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_225
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_225
.Lruntime_list_append_int_aligned_225: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_225: 
    mov rdi, [rsp]
    mov rsi, 356
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_226
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_226
.Lruntime_list_append_int_aligned_226: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_226: 
    mov rdi, [rsp]
    mov rsi, 358
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_227
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_227
.Lruntime_list_append_int_aligned_227: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_227: 
    mov rdi, [rsp]
    mov rsi, 360
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_228
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_228
.Lruntime_list_append_int_aligned_228: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_228: 
    mov rdi, [rsp]
    mov rsi, 362
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_229
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_229
.Lruntime_list_append_int_aligned_229: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_229: 
    mov rdi, [rsp]
    mov rsi, 364
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_230
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_230
.Lruntime_list_append_int_aligned_230: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_230: 
    mov rdi, [rsp]
    mov rsi, 366
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_231
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_231
.Lruntime_list_append_int_aligned_231: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_231: 
    mov rdi, [rsp]
    mov rsi, 368
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_232
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_232
.Lruntime_list_append_int_aligned_232: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_232: 
    mov rdi, [rsp]
    mov rsi, 370
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_233
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_233
.Lruntime_list_append_int_aligned_233: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_233: 
    mov rdi, [rsp]
    mov rsi, 372
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_234
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_234
.Lruntime_list_append_int_aligned_234: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_234: 
    mov rdi, [rsp]
    mov rsi, 374
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_235
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_235
.Lruntime_list_append_int_aligned_235: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_235: 
    mov rdi, [rsp]
    mov rsi, 376
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_236
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_236
.Lruntime_list_append_int_aligned_236: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_236: 
    mov rdi, [rsp]
    mov rsi, 378
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_237
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_237
.Lruntime_list_append_int_aligned_237: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_237: 
    mov rdi, [rsp]
    mov rsi, 380
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_238
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_238
.Lruntime_list_append_int_aligned_238: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_238: 
    mov rdi, [rsp]
    mov rsi, 382
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_239
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_239
.Lruntime_list_append_int_aligned_239: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_239: 
    mov rdi, [rsp]
    mov rsi, 384
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_240
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_240
.Lruntime_list_append_int_aligned_240: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_240: 
    mov rdi, [rsp]
    mov rsi, 386
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_241
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_241
.Lruntime_list_append_int_aligned_241: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_241: 
    mov rdi, [rsp]
    mov rsi, 388
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_242
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_242
.Lruntime_list_append_int_aligned_242: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_242: 
    mov rdi, [rsp]
    mov rsi, 390
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_243
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_243
.Lruntime_list_append_int_aligned_243: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_243: 
    mov rdi, [rsp]
    mov rsi, 392
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_244
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_244
.Lruntime_list_append_int_aligned_244: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_244: 
    mov rdi, [rsp]
    mov rsi, 394
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_245
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_245
.Lruntime_list_append_int_aligned_245: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_245: 
    mov rdi, [rsp]
    mov rsi, 396
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_246
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_246
.Lruntime_list_append_int_aligned_246: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_246: 
    mov rdi, [rsp]
    mov rsi, 398
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_247
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_247
.Lruntime_list_append_int_aligned_247: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_247: 
    mov rdi, [rsp]
    mov rsi, 400
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_248
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_248
.Lruntime_list_append_int_aligned_248: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_248: 
    mov rdi, [rsp]
    mov rsi, 402
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_249
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_249
.Lruntime_list_append_int_aligned_249: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_249: 
    mov rdi, [rsp]
    mov rsi, 404
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_250
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_250
.Lruntime_list_append_int_aligned_250: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_250: 
    mov rdi, [rsp]
    mov rsi, 406
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_251
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_251
.Lruntime_list_append_int_aligned_251: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_251: 
    mov rdi, [rsp]
    mov rsi, 408
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_252
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_252
.Lruntime_list_append_int_aligned_252: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_252: 
    mov rdi, [rsp]
    mov rsi, 410
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_253
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_253
.Lruntime_list_append_int_aligned_253: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_253: 
    mov rdi, [rsp]
    mov rsi, 412
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_254
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_254
.Lruntime_list_append_int_aligned_254: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_254: 
    mov rdi, [rsp]
    mov rsi, 414
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_255
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_255
.Lruntime_list_append_int_aligned_255: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_255: 
    mov rdi, [rsp]
    mov rsi, 416
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_256
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_256
.Lruntime_list_append_int_aligned_256: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_256: 
    mov rdi, [rsp]
    mov rsi, 418
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_257
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_257
.Lruntime_list_append_int_aligned_257: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_257: 
    mov rdi, [rsp]
    mov rsi, 420
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_258
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_258
.Lruntime_list_append_int_aligned_258: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_258: 
    mov rdi, [rsp]
    mov rsi, 422
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_259
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_259
.Lruntime_list_append_int_aligned_259: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_259: 
    mov rdi, [rsp]
    mov rsi, 424
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_260
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_260
.Lruntime_list_append_int_aligned_260: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_260: 
    mov rdi, [rsp]
    mov rsi, 426
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_261
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_261
.Lruntime_list_append_int_aligned_261: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_261: 
    mov rdi, [rsp]
    mov rsi, 428
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_262
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_262
.Lruntime_list_append_int_aligned_262: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_262: 
    mov rdi, [rsp]
    mov rsi, 430
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_263
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_263
.Lruntime_list_append_int_aligned_263: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_263: 
    mov rdi, [rsp]
    mov rsi, 432
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_264
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_264
.Lruntime_list_append_int_aligned_264: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_264: 
    mov rdi, [rsp]
    mov rsi, 434
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_265
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_265
.Lruntime_list_append_int_aligned_265: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_265: 
    mov rdi, [rsp]
    mov rsi, 436
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_266
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_266
.Lruntime_list_append_int_aligned_266: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_266: 
    mov rdi, [rsp]
    mov rsi, 438
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_267
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_267
.Lruntime_list_append_int_aligned_267: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_267: 
    mov rdi, [rsp]
    mov rsi, 440
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_268
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_268
.Lruntime_list_append_int_aligned_268: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_268: 
    mov rdi, [rsp]
    mov rsi, 442
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_269
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_269
.Lruntime_list_append_int_aligned_269: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_269: 
    mov rdi, [rsp]
    mov rsi, 444
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_270
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_270
.Lruntime_list_append_int_aligned_270: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_270: 
    mov rdi, [rsp]
    mov rsi, 446
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_271
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_271
.Lruntime_list_append_int_aligned_271: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_271: 
    mov rdi, [rsp]
    mov rsi, 448
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_272
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_272
.Lruntime_list_append_int_aligned_272: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_272: 
    mov rdi, [rsp]
    mov rsi, 450
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_273
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_273
.Lruntime_list_append_int_aligned_273: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_273: 
    mov rdi, [rsp]
    mov rsi, 452
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_274
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_274
.Lruntime_list_append_int_aligned_274: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_274: 
    mov rdi, [rsp]
    mov rsi, 454
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_275
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_275
.Lruntime_list_append_int_aligned_275: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_275: 
    mov rdi, [rsp]
    mov rsi, 456
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_276
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_276
.Lruntime_list_append_int_aligned_276: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_276: 
    mov rdi, [rsp]
    mov rsi, 458
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_277
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_277
.Lruntime_list_append_int_aligned_277: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_277: 
    mov rdi, [rsp]
    mov rsi, 460
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_278
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_278
.Lruntime_list_append_int_aligned_278: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_278: 
    mov rdi, [rsp]
    mov rsi, 462
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_279
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_279
.Lruntime_list_append_int_aligned_279: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_279: 
    mov rdi, [rsp]
    mov rsi, 464
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_280
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_280
.Lruntime_list_append_int_aligned_280: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_280: 
    mov rdi, [rsp]
    mov rsi, 466
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_281
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_281
.Lruntime_list_append_int_aligned_281: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_281: 
    mov rdi, [rsp]
    mov rsi, 468
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_282
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_282
.Lruntime_list_append_int_aligned_282: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_282: 
    mov rdi, [rsp]
    mov rsi, 470
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_283
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_283
.Lruntime_list_append_int_aligned_283: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_283: 
    mov rdi, [rsp]
    mov rsi, 472
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_284
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_284
.Lruntime_list_append_int_aligned_284: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_284: 
    mov rdi, [rsp]
    mov rsi, 474
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_285
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_285
.Lruntime_list_append_int_aligned_285: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_285: 
    mov rdi, [rsp]
    mov rsi, 476
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_286
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_286
.Lruntime_list_append_int_aligned_286: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_286: 
    mov rdi, [rsp]
    mov rsi, 478
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_287
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_287
.Lruntime_list_append_int_aligned_287: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_287: 
    mov rdi, [rsp]
    mov rsi, 480
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_288
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_288
.Lruntime_list_append_int_aligned_288: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_288: 
    mov rdi, [rsp]
    mov rsi, 482
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_289
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_289
.Lruntime_list_append_int_aligned_289: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_289: 
    mov rdi, [rsp]
    mov rsi, 484
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_290
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_290
.Lruntime_list_append_int_aligned_290: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_290: 
    mov rdi, [rsp]
    mov rsi, 486
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_291
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_291
.Lruntime_list_append_int_aligned_291: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_291: 
    mov rdi, [rsp]
    mov rsi, 488
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_292
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_292
.Lruntime_list_append_int_aligned_292: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_292: 
    mov rdi, [rsp]
    mov rsi, 490
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_293
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_293
.Lruntime_list_append_int_aligned_293: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_293: 
    mov rdi, [rsp]
    mov rsi, 492
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_294
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_294
.Lruntime_list_append_int_aligned_294: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_294: 
    mov rdi, [rsp]
    mov rsi, 494
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_295
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_295
.Lruntime_list_append_int_aligned_295: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_295: 
    mov rdi, [rsp]
    mov rsi, 496
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_296
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_296
.Lruntime_list_append_int_aligned_296: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_296: 
    mov rdi, [rsp]
    mov rsi, 498
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_297
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_297
.Lruntime_list_append_int_aligned_297: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_297: 
    mov rdi, [rsp]
    mov rsi, 500
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_298
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_298
.Lruntime_list_append_int_aligned_298: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_298: 
    mov rdi, [rsp]
    mov rsi, 502
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_299
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_299
.Lruntime_list_append_int_aligned_299: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_299: 
    mov rdi, [rsp]
    mov rsi, 504
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_300
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_300
.Lruntime_list_append_int_aligned_300: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_300: 
    mov rdi, [rsp]
    mov rsi, 506
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_301
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_301
.Lruntime_list_append_int_aligned_301: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_301: 
    mov rdi, [rsp]
    mov rsi, 508
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_302
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_302
.Lruntime_list_append_int_aligned_302: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_302: 
    mov rdi, [rsp]
    mov rsi, 510
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_303
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_303
.Lruntime_list_append_int_aligned_303: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_303: 
    mov rdi, [rsp]
    mov rsi, 512
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_304
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_304
.Lruntime_list_append_int_aligned_304: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_304: 
    mov rdi, [rsp]
    mov rsi, 514
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_305
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_305
.Lruntime_list_append_int_aligned_305: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_305: 
    mov rdi, [rsp]
    mov rsi, 516
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_306
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_306
.Lruntime_list_append_int_aligned_306: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_306: 
    mov rdi, [rsp]
    mov rsi, 518
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_307
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_307
.Lruntime_list_append_int_aligned_307: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_307: 
    mov rdi, [rsp]
    mov rsi, 520
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_308
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_308
.Lruntime_list_append_int_aligned_308: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_308: 
    mov rdi, [rsp]
    mov rsi, 522
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_309
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_309
.Lruntime_list_append_int_aligned_309: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_309: 
    mov rdi, [rsp]
    mov rsi, 524
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_310
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_310
.Lruntime_list_append_int_aligned_310: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_310: 
    mov rdi, [rsp]
    mov rsi, 526
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_311
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_311
.Lruntime_list_append_int_aligned_311: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_311: 
    mov rdi, [rsp]
    mov rsi, 528
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_312
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_312
.Lruntime_list_append_int_aligned_312: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_312: 
    mov rdi, [rsp]
    mov rsi, 530
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_313
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_313
.Lruntime_list_append_int_aligned_313: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_313: 
    mov rdi, [rsp]
    mov rsi, 532
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_314
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_314
.Lruntime_list_append_int_aligned_314: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_314: 
    mov rdi, [rsp]
    mov rsi, 534
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_315
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_315
.Lruntime_list_append_int_aligned_315: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_315: 
    mov rdi, [rsp]
    mov rsi, 536
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_316
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_316
.Lruntime_list_append_int_aligned_316: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_316: 
    mov rdi, [rsp]
    mov rsi, 538
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_317
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_317
.Lruntime_list_append_int_aligned_317: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_317: 
    mov rdi, [rsp]
    mov rsi, 540
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_318
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_318
.Lruntime_list_append_int_aligned_318: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_318: 
    mov rdi, [rsp]
    mov rsi, 542
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_319
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_319
.Lruntime_list_append_int_aligned_319: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_319: 
    mov rdi, [rsp]
    mov rsi, 544
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_320
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_320
.Lruntime_list_append_int_aligned_320: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_320: 
    mov rdi, [rsp]
    mov rsi, 546
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_321
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_321
.Lruntime_list_append_int_aligned_321: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_321: 
    mov rdi, [rsp]
    mov rsi, 548
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_322
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_322
.Lruntime_list_append_int_aligned_322: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_322: 
    mov rdi, [rsp]
    mov rsi, 550
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_323
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_323
.Lruntime_list_append_int_aligned_323: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_323: 
    mov rdi, [rsp]
    mov rsi, 552
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_324
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_324
.Lruntime_list_append_int_aligned_324: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_324: 
    mov rdi, [rsp]
    mov rsi, 554
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_325
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_325
.Lruntime_list_append_int_aligned_325: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_325: 
    mov rdi, [rsp]
    mov rsi, 556
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_326
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_326
.Lruntime_list_append_int_aligned_326: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_326: 
    mov rdi, [rsp]
    mov rsi, 558
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_327
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_327
.Lruntime_list_append_int_aligned_327: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_327: 
    mov rdi, [rsp]
    mov rsi, 560
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_328
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_328
.Lruntime_list_append_int_aligned_328: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_328: 
    mov rdi, [rsp]
    mov rsi, 562
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_329
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_329
.Lruntime_list_append_int_aligned_329: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_329: 
    mov rdi, [rsp]
    mov rsi, 564
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_330
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_330
.Lruntime_list_append_int_aligned_330: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_330: 
    mov rdi, [rsp]
    mov rsi, 566
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_331
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_331
.Lruntime_list_append_int_aligned_331: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_331: 
    mov rdi, [rsp]
    mov rsi, 568
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_332
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_332
.Lruntime_list_append_int_aligned_332: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_332: 
    mov rdi, [rsp]
    mov rsi, 570
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_333
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_333
.Lruntime_list_append_int_aligned_333: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_333: 
    mov rdi, [rsp]
    mov rsi, 572
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_334
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_334
.Lruntime_list_append_int_aligned_334: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_334: 
    mov rdi, [rsp]
    mov rsi, 574
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_335
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_335
.Lruntime_list_append_int_aligned_335: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_335: 
    mov rdi, [rsp]
    mov rsi, 576
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_336
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_336
.Lruntime_list_append_int_aligned_336: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_336: 
    mov rdi, [rsp]
    mov rsi, 578
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_337
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_337
.Lruntime_list_append_int_aligned_337: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_337: 
    mov rdi, [rsp]
    mov rsi, 580
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_338
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_338
.Lruntime_list_append_int_aligned_338: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_338: 
    mov rdi, [rsp]
    mov rsi, 582
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_339
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_339
.Lruntime_list_append_int_aligned_339: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_339: 
    mov rdi, [rsp]
    mov rsi, 584
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_340
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_340
.Lruntime_list_append_int_aligned_340: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_340: 
    mov rdi, [rsp]
    mov rsi, 586
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_341
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_341
.Lruntime_list_append_int_aligned_341: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_341: 
    mov rdi, [rsp]
    mov rsi, 588
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_342
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_342
.Lruntime_list_append_int_aligned_342: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_342: 
    mov rdi, [rsp]
    mov rsi, 590
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_343
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_343
.Lruntime_list_append_int_aligned_343: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_343: 
    mov rdi, [rsp]
    mov rsi, 592
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_344
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_344
.Lruntime_list_append_int_aligned_344: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_344: 
    mov rdi, [rsp]
    mov rsi, 594
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_345
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_345
.Lruntime_list_append_int_aligned_345: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_345: 
    mov rdi, [rsp]
    mov rsi, 596
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_346
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_346
.Lruntime_list_append_int_aligned_346: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_346: 
    mov rdi, [rsp]
    mov rsi, 598
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_347
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_347
.Lruntime_list_append_int_aligned_347: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_347: 
    mov rdi, [rsp]
    mov rsi, 600
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_348
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_348
.Lruntime_list_append_int_aligned_348: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_348: 
    mov rdi, [rsp]
    mov rsi, 602
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_349
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_349
.Lruntime_list_append_int_aligned_349: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_349: 
    mov rdi, [rsp]
    mov rsi, 604
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_350
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_350
.Lruntime_list_append_int_aligned_350: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_350: 
    mov rdi, [rsp]
    mov rsi, 606
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_351
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_351
.Lruntime_list_append_int_aligned_351: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_351: 
    mov rdi, [rsp]
    mov rsi, 608
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_352
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_352
.Lruntime_list_append_int_aligned_352: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_352: 
    mov rdi, [rsp]
    mov rsi, 610
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_353
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_353
.Lruntime_list_append_int_aligned_353: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_353: 
    mov rdi, [rsp]
    mov rsi, 612
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_354
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_354
.Lruntime_list_append_int_aligned_354: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_354: 
    mov rdi, [rsp]
    mov rsi, 614
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_355
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_355
.Lruntime_list_append_int_aligned_355: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_355: 
    mov rdi, [rsp]
    mov rsi, 616
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_356
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_356
.Lruntime_list_append_int_aligned_356: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_356: 
    mov rdi, [rsp]
    mov rsi, 618
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_357
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_357
.Lruntime_list_append_int_aligned_357: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_357: 
    mov rdi, [rsp]
    mov rsi, 620
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_358
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_358
.Lruntime_list_append_int_aligned_358: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_358: 
    mov rdi, [rsp]
    mov rsi, 622
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_359
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_359
.Lruntime_list_append_int_aligned_359: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_359: 
    mov rdi, [rsp]
    mov rsi, 624
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_360
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_360
.Lruntime_list_append_int_aligned_360: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_360: 
    mov rdi, [rsp]
    mov rsi, 626
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_361
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_361
.Lruntime_list_append_int_aligned_361: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_361: 
    mov rdi, [rsp]
    mov rsi, 628
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_362
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_362
.Lruntime_list_append_int_aligned_362: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_362: 
    mov rdi, [rsp]
    mov rsi, 630
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_363
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_363
.Lruntime_list_append_int_aligned_363: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_363: 
    mov rdi, [rsp]
    mov rsi, 632
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_364
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_364
.Lruntime_list_append_int_aligned_364: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_364: 
    mov rdi, [rsp]
    mov rsi, 634
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_365
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_365
.Lruntime_list_append_int_aligned_365: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_365: 
    mov rdi, [rsp]
    mov rsi, 636
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_366
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_366
.Lruntime_list_append_int_aligned_366: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_366: 
    mov rdi, [rsp]
    mov rsi, 638
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_367
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_367
.Lruntime_list_append_int_aligned_367: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_367: 
    mov rdi, [rsp]
    mov rsi, 640
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_368
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_368
.Lruntime_list_append_int_aligned_368: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_368: 
    mov rdi, [rsp]
    mov rsi, 642
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_369
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_369
.Lruntime_list_append_int_aligned_369: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_369: 
    mov rdi, [rsp]
    mov rsi, 644
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_370
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_370
.Lruntime_list_append_int_aligned_370: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_370: 
    mov rdi, [rsp]
    mov rsi, 646
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_371
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_371
.Lruntime_list_append_int_aligned_371: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_371: 
    mov rdi, [rsp]
    mov rsi, 648
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_372
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_372
.Lruntime_list_append_int_aligned_372: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_372: 
    mov rdi, [rsp]
    mov rsi, 650
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_373
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_373
.Lruntime_list_append_int_aligned_373: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_373: 
    mov rdi, [rsp]
    mov rsi, 652
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_374
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_374
.Lruntime_list_append_int_aligned_374: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_374: 
    mov rdi, [rsp]
    mov rsi, 654
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_375
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_375
.Lruntime_list_append_int_aligned_375: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_375: 
    mov rdi, [rsp]
    mov rsi, 656
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_376
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_376
.Lruntime_list_append_int_aligned_376: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_376: 
    mov rdi, [rsp]
    mov rsi, 658
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_377
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_377
.Lruntime_list_append_int_aligned_377: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_377: 
    mov rdi, [rsp]
    mov rsi, 660
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_378
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_378
.Lruntime_list_append_int_aligned_378: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_378: 
    mov rdi, [rsp]
    mov rsi, 662
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_379
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_379
.Lruntime_list_append_int_aligned_379: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_379: 
    mov rdi, [rsp]
    mov rsi, 664
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_380
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_380
.Lruntime_list_append_int_aligned_380: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_380: 
    mov rdi, [rsp]
    mov rsi, 666
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_381
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_381
.Lruntime_list_append_int_aligned_381: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_381: 
    mov rdi, [rsp]
    mov rsi, 668
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_382
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_382
.Lruntime_list_append_int_aligned_382: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_382: 
    mov rdi, [rsp]
    mov rsi, 670
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_383
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_383
.Lruntime_list_append_int_aligned_383: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_383: 
    mov rdi, [rsp]
    mov rsi, 672
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_384
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_384
.Lruntime_list_append_int_aligned_384: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_384: 
    mov rdi, [rsp]
    mov rsi, 674
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_385
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_385
.Lruntime_list_append_int_aligned_385: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_385: 
    mov rdi, [rsp]
    mov rsi, 676
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_386
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_386
.Lruntime_list_append_int_aligned_386: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_386: 
    mov rdi, [rsp]
    mov rsi, 678
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_387
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_387
.Lruntime_list_append_int_aligned_387: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_387: 
    mov rdi, [rsp]
    mov rsi, 680
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_388
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_388
.Lruntime_list_append_int_aligned_388: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_388: 
    mov rdi, [rsp]
    mov rsi, 682
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_389
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_389
.Lruntime_list_append_int_aligned_389: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_389: 
    mov rdi, [rsp]
    mov rsi, 684
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_390
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_390
.Lruntime_list_append_int_aligned_390: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_390: 
    mov rdi, [rsp]
    mov rsi, 686
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_391
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_391
.Lruntime_list_append_int_aligned_391: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_391: 
    mov rdi, [rsp]
    mov rsi, 688
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_392
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_392
.Lruntime_list_append_int_aligned_392: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_392: 
    mov rdi, [rsp]
    mov rsi, 690
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_393
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_393
.Lruntime_list_append_int_aligned_393: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_393: 
    mov rdi, [rsp]
    mov rsi, 692
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_394
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_394
.Lruntime_list_append_int_aligned_394: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_394: 
    mov rdi, [rsp]
    mov rsi, 694
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_395
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_395
.Lruntime_list_append_int_aligned_395: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_395: 
    mov rdi, [rsp]
    mov rsi, 696
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_396
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_396
.Lruntime_list_append_int_aligned_396: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_396: 
    mov rdi, [rsp]
    mov rsi, 698
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_397
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_397
.Lruntime_list_append_int_aligned_397: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_397: 
    mov rdi, [rsp]
    mov rsi, 700
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_398
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_398
.Lruntime_list_append_int_aligned_398: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_398: 
    mov rdi, [rsp]
    mov rsi, 702
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_399
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_399
.Lruntime_list_append_int_aligned_399: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_399: 
    mov rdi, [rsp]
    mov rsi, 704
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_400
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_400
.Lruntime_list_append_int_aligned_400: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_400: 
    mov rdi, [rsp]
    mov rsi, 706
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_401
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_401
.Lruntime_list_append_int_aligned_401: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_401: 
    mov rdi, [rsp]
    mov rsi, 708
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_402
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_402
.Lruntime_list_append_int_aligned_402: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_402: 
    mov rdi, [rsp]
    mov rsi, 710
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_403
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_403
.Lruntime_list_append_int_aligned_403: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_403: 
    mov rdi, [rsp]
    mov rsi, 712
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_404
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_404
.Lruntime_list_append_int_aligned_404: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_404: 
    mov rdi, [rsp]
    mov rsi, 714
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_405
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_405
.Lruntime_list_append_int_aligned_405: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_405: 
    mov rdi, [rsp]
    mov rsi, 716
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_406
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_406
.Lruntime_list_append_int_aligned_406: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_406: 
    mov rdi, [rsp]
    mov rsi, 718
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_407
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_407
.Lruntime_list_append_int_aligned_407: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_407: 
    mov rdi, [rsp]
    mov rsi, 720
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_408
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_408
.Lruntime_list_append_int_aligned_408: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_408: 
    mov rdi, [rsp]
    mov rsi, 722
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_409
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_409
.Lruntime_list_append_int_aligned_409: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_409: 
    mov rdi, [rsp]
    mov rsi, 724
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_410
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_410
.Lruntime_list_append_int_aligned_410: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_410: 
    mov rdi, [rsp]
    mov rsi, 726
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_411
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_411
.Lruntime_list_append_int_aligned_411: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_411: 
    mov rdi, [rsp]
    mov rsi, 728
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_412
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_412
.Lruntime_list_append_int_aligned_412: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_412: 
    mov rdi, [rsp]
    mov rsi, 730
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_413
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_413
.Lruntime_list_append_int_aligned_413: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_413: 
    mov rdi, [rsp]
    mov rsi, 732
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_414
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_414
.Lruntime_list_append_int_aligned_414: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_414: 
    mov rdi, [rsp]
    mov rsi, 734
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_415
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_415
.Lruntime_list_append_int_aligned_415: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_415: 
    mov rdi, [rsp]
    mov rsi, 736
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_416
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_416
.Lruntime_list_append_int_aligned_416: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_416: 
    mov rdi, [rsp]
    mov rsi, 738
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_417
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_417
.Lruntime_list_append_int_aligned_417: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_417: 
    mov rdi, [rsp]
    mov rsi, 740
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_418
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_418
.Lruntime_list_append_int_aligned_418: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_418: 
    mov rdi, [rsp]
    mov rsi, 742
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_419
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_419
.Lruntime_list_append_int_aligned_419: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_419: 
    mov rdi, [rsp]
    mov rsi, 744
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_420
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_420
.Lruntime_list_append_int_aligned_420: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_420: 
    mov rdi, [rsp]
    mov rsi, 746
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_421
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_421
.Lruntime_list_append_int_aligned_421: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_421: 
    mov rdi, [rsp]
    mov rsi, 748
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_422
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_422
.Lruntime_list_append_int_aligned_422: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_422: 
    mov rdi, [rsp]
    mov rsi, 750
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_423
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_423
.Lruntime_list_append_int_aligned_423: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_423: 
    mov rdi, [rsp]
    mov rsi, 752
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_424
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_424
.Lruntime_list_append_int_aligned_424: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_424: 
    mov rdi, [rsp]
    mov rsi, 754
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_425
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_425
.Lruntime_list_append_int_aligned_425: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_425: 
    mov rdi, [rsp]
    mov rsi, 756
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_426
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_426
.Lruntime_list_append_int_aligned_426: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_426: 
    mov rdi, [rsp]
    mov rsi, 758
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_427
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_427
.Lruntime_list_append_int_aligned_427: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_427: 
    mov rdi, [rsp]
    mov rsi, 760
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_428
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_428
.Lruntime_list_append_int_aligned_428: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_428: 
    mov rdi, [rsp]
    mov rsi, 762
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_429
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_429
.Lruntime_list_append_int_aligned_429: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_429: 
    mov rdi, [rsp]
    mov rsi, 764
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_430
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_430
.Lruntime_list_append_int_aligned_430: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_430: 
    mov rdi, [rsp]
    mov rsi, 766
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_431
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_431
.Lruntime_list_append_int_aligned_431: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_431: 
    mov rdi, [rsp]
    mov rsi, 768
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_432
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_432
.Lruntime_list_append_int_aligned_432: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_432: 
    mov rdi, [rsp]
    mov rsi, 770
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_433
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_433
.Lruntime_list_append_int_aligned_433: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_433: 
    mov rdi, [rsp]
    mov rsi, 772
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_434
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_434
.Lruntime_list_append_int_aligned_434: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_434: 
    mov rdi, [rsp]
    mov rsi, 774
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_435
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_435
.Lruntime_list_append_int_aligned_435: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_435: 
    mov rdi, [rsp]
    mov rsi, 776
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_436
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_436
.Lruntime_list_append_int_aligned_436: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_436: 
    mov rdi, [rsp]
    mov rsi, 778
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_437
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_437
.Lruntime_list_append_int_aligned_437: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_437: 
    mov rdi, [rsp]
    mov rsi, 780
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_438
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_438
.Lruntime_list_append_int_aligned_438: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_438: 
    mov rdi, [rsp]
    mov rsi, 782
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_439
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_439
.Lruntime_list_append_int_aligned_439: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_439: 
    mov rdi, [rsp]
    mov rsi, 784
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_440
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_440
.Lruntime_list_append_int_aligned_440: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_440: 
    mov rdi, [rsp]
    mov rsi, 786
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_441
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_441
.Lruntime_list_append_int_aligned_441: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_441: 
    mov rdi, [rsp]
    mov rsi, 788
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_442
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_442
.Lruntime_list_append_int_aligned_442: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_442: 
    mov rdi, [rsp]
    mov rsi, 790
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_443
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_443
.Lruntime_list_append_int_aligned_443: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_443: 
    mov rdi, [rsp]
    mov rsi, 792
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_444
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_444
.Lruntime_list_append_int_aligned_444: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_444: 
    mov rdi, [rsp]
    mov rsi, 794
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_445
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_445
.Lruntime_list_append_int_aligned_445: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_445: 
    mov rdi, [rsp]
    mov rsi, 796
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_446
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_446
.Lruntime_list_append_int_aligned_446: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_446: 
    mov rdi, [rsp]
    mov rsi, 798
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_447
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_447
.Lruntime_list_append_int_aligned_447: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_447: 
    mov rdi, [rsp]
    mov rsi, 800
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_448
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_448
.Lruntime_list_append_int_aligned_448: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_448: 
    mov rdi, [rsp]
    mov rsi, 802
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_449
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_449
.Lruntime_list_append_int_aligned_449: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_449: 
    mov rdi, [rsp]
    mov rsi, 804
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_450
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_450
.Lruntime_list_append_int_aligned_450: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_450: 
    mov rdi, [rsp]
    mov rsi, 806
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_451
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_451
.Lruntime_list_append_int_aligned_451: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_451: 
    mov rdi, [rsp]
    mov rsi, 808
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_452
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_452
.Lruntime_list_append_int_aligned_452: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_452: 
    mov rdi, [rsp]
    mov rsi, 810
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_453
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_453
.Lruntime_list_append_int_aligned_453: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_453: 
    mov rdi, [rsp]
    mov rsi, 812
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_454
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_454
.Lruntime_list_append_int_aligned_454: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_454: 
    mov rdi, [rsp]
    mov rsi, 814
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_455
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_455
.Lruntime_list_append_int_aligned_455: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_455: 
    mov rdi, [rsp]
    mov rsi, 816
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_456
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_456
.Lruntime_list_append_int_aligned_456: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_456: 
    mov rdi, [rsp]
    mov rsi, 818
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_457
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_457
.Lruntime_list_append_int_aligned_457: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_457: 
    mov rdi, [rsp]
    mov rsi, 820
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_458
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_458
.Lruntime_list_append_int_aligned_458: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_458: 
    mov rdi, [rsp]
    mov rsi, 822
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_459
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_459
.Lruntime_list_append_int_aligned_459: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_459: 
    mov rdi, [rsp]
    mov rsi, 824
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_460
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_460
.Lruntime_list_append_int_aligned_460: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_460: 
    mov rdi, [rsp]
    mov rsi, 826
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_461
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_461
.Lruntime_list_append_int_aligned_461: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_461: 
    mov rdi, [rsp]
    mov rsi, 828
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_462
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_462
.Lruntime_list_append_int_aligned_462: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_462: 
    mov rdi, [rsp]
    mov rsi, 830
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_463
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_463
.Lruntime_list_append_int_aligned_463: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_463: 
    mov rdi, [rsp]
    mov rsi, 832
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_464
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_464
.Lruntime_list_append_int_aligned_464: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_464: 
    mov rdi, [rsp]
    mov rsi, 834
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_465
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_465
.Lruntime_list_append_int_aligned_465: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_465: 
    mov rdi, [rsp]
    mov rsi, 836
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_466
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_466
.Lruntime_list_append_int_aligned_466: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_466: 
    mov rdi, [rsp]
    mov rsi, 838
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_467
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_467
.Lruntime_list_append_int_aligned_467: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_467: 
    mov rdi, [rsp]
    mov rsi, 840
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_468
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_468
.Lruntime_list_append_int_aligned_468: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_468: 
    mov rdi, [rsp]
    mov rsi, 842
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_469
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_469
.Lruntime_list_append_int_aligned_469: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_469: 
    mov rdi, [rsp]
    mov rsi, 844
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_470
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_470
.Lruntime_list_append_int_aligned_470: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_470: 
    mov rdi, [rsp]
    mov rsi, 846
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_471
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_471
.Lruntime_list_append_int_aligned_471: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_471: 
    mov rdi, [rsp]
    mov rsi, 848
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_472
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_472
.Lruntime_list_append_int_aligned_472: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_472: 
    mov rdi, [rsp]
    mov rsi, 850
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_473
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_473
.Lruntime_list_append_int_aligned_473: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_473: 
    mov rdi, [rsp]
    mov rsi, 852
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_474
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_474
.Lruntime_list_append_int_aligned_474: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_474: 
    mov rdi, [rsp]
    mov rsi, 854
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_475
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_475
.Lruntime_list_append_int_aligned_475: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_475: 
    mov rdi, [rsp]
    mov rsi, 856
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_476
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_476
.Lruntime_list_append_int_aligned_476: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_476: 
    mov rdi, [rsp]
    mov rsi, 858
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_477
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_477
.Lruntime_list_append_int_aligned_477: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_477: 
    mov rdi, [rsp]
    mov rsi, 860
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_478
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_478
.Lruntime_list_append_int_aligned_478: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_478: 
    mov rdi, [rsp]
    mov rsi, 862
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_479
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_479
.Lruntime_list_append_int_aligned_479: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_479: 
    mov rdi, [rsp]
    mov rsi, 864
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_480
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_480
.Lruntime_list_append_int_aligned_480: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_480: 
    mov rdi, [rsp]
    mov rsi, 866
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_481
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_481
.Lruntime_list_append_int_aligned_481: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_481: 
    mov rdi, [rsp]
    mov rsi, 868
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_482
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_482
.Lruntime_list_append_int_aligned_482: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_482: 
    mov rdi, [rsp]
    mov rsi, 870
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_483
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_483
.Lruntime_list_append_int_aligned_483: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_483: 
    mov rdi, [rsp]
    mov rsi, 872
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_484
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_484
.Lruntime_list_append_int_aligned_484: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_484: 
    mov rdi, [rsp]
    mov rsi, 874
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_485
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_485
.Lruntime_list_append_int_aligned_485: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_485: 
    mov rdi, [rsp]
    mov rsi, 876
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_486
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_486
.Lruntime_list_append_int_aligned_486: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_486: 
    mov rdi, [rsp]
    mov rsi, 878
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_487
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_487
.Lruntime_list_append_int_aligned_487: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_487: 
    mov rdi, [rsp]
    mov rsi, 880
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_488
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_488
.Lruntime_list_append_int_aligned_488: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_488: 
    mov rdi, [rsp]
    mov rsi, 882
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_489
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_489
.Lruntime_list_append_int_aligned_489: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_489: 
    mov rdi, [rsp]
    mov rsi, 884
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_490
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_490
.Lruntime_list_append_int_aligned_490: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_490: 
    mov rdi, [rsp]
    mov rsi, 886
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_491
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_491
.Lruntime_list_append_int_aligned_491: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_491: 
    mov rdi, [rsp]
    mov rsi, 888
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_492
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_492
.Lruntime_list_append_int_aligned_492: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_492: 
    mov rdi, [rsp]
    mov rsi, 890
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_493
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_493
.Lruntime_list_append_int_aligned_493: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_493: 
    mov rdi, [rsp]
    mov rsi, 892
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_494
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_494
.Lruntime_list_append_int_aligned_494: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_494: 
    mov rdi, [rsp]
    mov rsi, 894
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_495
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_495
.Lruntime_list_append_int_aligned_495: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_495: 
    mov rdi, [rsp]
    mov rsi, 896
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_496
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_496
.Lruntime_list_append_int_aligned_496: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_496: 
    mov rdi, [rsp]
    mov rsi, 898
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_497
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_497
.Lruntime_list_append_int_aligned_497: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_497: 
    mov rdi, [rsp]
    mov rsi, 900
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_498
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_498
.Lruntime_list_append_int_aligned_498: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_498: 
    mov rdi, [rsp]
    mov rsi, 902
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_499
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_499
.Lruntime_list_append_int_aligned_499: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_499: 
    mov rdi, [rsp]
    mov rsi, 904
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_500
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_500
.Lruntime_list_append_int_aligned_500: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_500: 
    mov rdi, [rsp]
    mov rsi, 906
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_501
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_501
.Lruntime_list_append_int_aligned_501: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_501: 
    mov rdi, [rsp]
    mov rsi, 908
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_502
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_502
.Lruntime_list_append_int_aligned_502: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_502: 
    mov rdi, [rsp]
    mov rsi, 910
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_503
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_503
.Lruntime_list_append_int_aligned_503: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_503: 
    mov rdi, [rsp]
    mov rsi, 912
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_504
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_504
.Lruntime_list_append_int_aligned_504: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_504: 
    mov rdi, [rsp]
    mov rsi, 914
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_505
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_505
.Lruntime_list_append_int_aligned_505: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_505: 
    mov rdi, [rsp]
    mov rsi, 916
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_506
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_506
.Lruntime_list_append_int_aligned_506: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_506: 
    mov rdi, [rsp]
    mov rsi, 918
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_507
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_507
.Lruntime_list_append_int_aligned_507: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_507: 
    mov rdi, [rsp]
    mov rsi, 920
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_508
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_508
.Lruntime_list_append_int_aligned_508: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_508: 
    mov rdi, [rsp]
    mov rsi, 922
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_509
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_509
.Lruntime_list_append_int_aligned_509: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_509: 
    mov rdi, [rsp]
    mov rsi, 924
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_510
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_510
.Lruntime_list_append_int_aligned_510: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_510: 
    mov rdi, [rsp]
    mov rsi, 926
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_511
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_511
.Lruntime_list_append_int_aligned_511: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_511: 
    mov rdi, [rsp]
    mov rsi, 928
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_512
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_512
.Lruntime_list_append_int_aligned_512: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_512: 
    mov rdi, [rsp]
    mov rsi, 930
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_513
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_513
.Lruntime_list_append_int_aligned_513: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_513: 
    mov rdi, [rsp]
    mov rsi, 932
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_514
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_514
.Lruntime_list_append_int_aligned_514: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_514: 
    mov rdi, [rsp]
    mov rsi, 934
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_515
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_515
.Lruntime_list_append_int_aligned_515: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_515: 
    mov rdi, [rsp]
    mov rsi, 936
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_516
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_516
.Lruntime_list_append_int_aligned_516: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_516: 
    mov rdi, [rsp]
    mov rsi, 938
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_517
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_517
.Lruntime_list_append_int_aligned_517: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_517: 
    mov rdi, [rsp]
    mov rsi, 940
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_518
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_518
.Lruntime_list_append_int_aligned_518: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_518: 
    mov rdi, [rsp]
    mov rsi, 942
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_519
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_519
.Lruntime_list_append_int_aligned_519: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_519: 
    mov rdi, [rsp]
    mov rsi, 944
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_520
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_520
.Lruntime_list_append_int_aligned_520: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_520: 
    mov rdi, [rsp]
    mov rsi, 946
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_521
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_521
.Lruntime_list_append_int_aligned_521: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_521: 
    mov rdi, [rsp]
    mov rsi, 948
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_522
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_522
.Lruntime_list_append_int_aligned_522: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_522: 
    mov rdi, [rsp]
    mov rsi, 950
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_523
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_523
.Lruntime_list_append_int_aligned_523: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_523: 
    mov rdi, [rsp]
    mov rsi, 952
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_524
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_524
.Lruntime_list_append_int_aligned_524: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_524: 
    mov rdi, [rsp]
    mov rsi, 954
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_525
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_525
.Lruntime_list_append_int_aligned_525: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_525: 
    mov rdi, [rsp]
    mov rsi, 956
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_526
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_526
.Lruntime_list_append_int_aligned_526: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_526: 
    mov rdi, [rsp]
    mov rsi, 958
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_527
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_527
.Lruntime_list_append_int_aligned_527: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_527: 
    mov rdi, [rsp]
    mov rsi, 960
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_528
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_528
.Lruntime_list_append_int_aligned_528: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_528: 
    mov rdi, [rsp]
    mov rsi, 962
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_529
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_529
.Lruntime_list_append_int_aligned_529: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_529: 
    mov rdi, [rsp]
    mov rsi, 964
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_530
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_530
.Lruntime_list_append_int_aligned_530: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_530: 
    mov rdi, [rsp]
    mov rsi, 966
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_531
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_531
.Lruntime_list_append_int_aligned_531: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_531: 
    mov rdi, [rsp]
    mov rsi, 968
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_532
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_532
.Lruntime_list_append_int_aligned_532: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_532: 
    mov rdi, [rsp]
    mov rsi, 970
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_533
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_533
.Lruntime_list_append_int_aligned_533: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_533: 
    mov rdi, [rsp]
    mov rsi, 972
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_534
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_534
.Lruntime_list_append_int_aligned_534: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_534: 
    mov rdi, [rsp]
    mov rsi, 974
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_535
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_535
.Lruntime_list_append_int_aligned_535: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_535: 
    mov rdi, [rsp]
    mov rsi, 976
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_536
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_536
.Lruntime_list_append_int_aligned_536: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_536: 
    mov rdi, [rsp]
    mov rsi, 978
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_537
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_537
.Lruntime_list_append_int_aligned_537: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_537: 
    mov rdi, [rsp]
    mov rsi, 980
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_538
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_538
.Lruntime_list_append_int_aligned_538: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_538: 
    mov rdi, [rsp]
    mov rsi, 982
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_539
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_539
.Lruntime_list_append_int_aligned_539: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_539: 
    mov rdi, [rsp]
    mov rsi, 984
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_540
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_540
.Lruntime_list_append_int_aligned_540: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_540: 
    mov rdi, [rsp]
    mov rsi, 986
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_541
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_541
.Lruntime_list_append_int_aligned_541: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_541: 
    mov rdi, [rsp]
    mov rsi, 988
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_542
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_542
.Lruntime_list_append_int_aligned_542: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_542: 
    mov rdi, [rsp]
    mov rsi, 990
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_543
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_543
.Lruntime_list_append_int_aligned_543: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_543: 
    mov rdi, [rsp]
    mov rsi, 992
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_544
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_544
.Lruntime_list_append_int_aligned_544: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_544: 
    mov rdi, [rsp]
    mov rsi, 994
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_545
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_545
.Lruntime_list_append_int_aligned_545: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_545: 
    mov rdi, [rsp]
    mov rsi, 996
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_546
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_546
.Lruntime_list_append_int_aligned_546: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_546: 
    mov rdi, [rsp]
    mov rsi, 998
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_547
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_547
.Lruntime_list_append_int_aligned_547: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_547: 
    mov rdi, [rsp]
    mov rsi, 1000
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_548
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_548
.Lruntime_list_append_int_aligned_548: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_548: 
    mov rdi, [rsp]
    mov rsi, 1002
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_549
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_549
.Lruntime_list_append_int_aligned_549: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_549: 
    mov rdi, [rsp]
    mov rsi, 1004
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_550
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_550
.Lruntime_list_append_int_aligned_550: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_550: 
    mov rdi, [rsp]
    mov rsi, 1006
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_551
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_551
.Lruntime_list_append_int_aligned_551: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_551: 
    mov rdi, [rsp]
    mov rsi, 1008
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_552
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_552
.Lruntime_list_append_int_aligned_552: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_552: 
    mov rdi, [rsp]
    mov rsi, 1010
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_553
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_553
.Lruntime_list_append_int_aligned_553: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_553: 
    mov rdi, [rsp]
    mov rsi, 1012
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_554
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_554
.Lruntime_list_append_int_aligned_554: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_554: 
    mov rdi, [rsp]
    mov rsi, 1014
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_555
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_555
.Lruntime_list_append_int_aligned_555: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_555: 
    mov rdi, [rsp]
    mov rsi, 1016
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_556
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_556
.Lruntime_list_append_int_aligned_556: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_556: 
    mov rdi, [rsp]
    mov rsi, 1018
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_557
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_557
.Lruntime_list_append_int_aligned_557: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_557: 
    mov rdi, [rsp]
    mov rsi, 1020
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_558
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_558
.Lruntime_list_append_int_aligned_558: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_558: 
    mov rdi, [rsp]
    mov rsi, 1022
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_559
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_559
.Lruntime_list_append_int_aligned_559: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_559: 
    mov rdi, [rsp]
    mov rsi, 1024
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_560
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_560
.Lruntime_list_append_int_aligned_560: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_560: 
    mov rdi, [rsp]
    mov rsi, 1026
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_561
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_561
.Lruntime_list_append_int_aligned_561: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_561: 
    mov rdi, [rsp]
    mov rsi, 1028
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_562
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_562
.Lruntime_list_append_int_aligned_562: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_562: 
    mov rdi, [rsp]
    mov rsi, 1030
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_563
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_563
.Lruntime_list_append_int_aligned_563: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_563: 
    mov rdi, [rsp]
    mov rsi, 1032
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_564
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_564
.Lruntime_list_append_int_aligned_564: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_564: 
    mov rdi, [rsp]
    mov rsi, 1034
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_565
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_565
.Lruntime_list_append_int_aligned_565: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_565: 
    mov rdi, [rsp]
    mov rsi, 1036
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_566
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_566
.Lruntime_list_append_int_aligned_566: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_566: 
    mov rdi, [rsp]
    mov rsi, 1038
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_567
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_567
.Lruntime_list_append_int_aligned_567: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_567: 
    mov rdi, [rsp]
    mov rsi, 1040
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_568
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_568
.Lruntime_list_append_int_aligned_568: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_568: 
    mov rdi, [rsp]
    mov rsi, 1042
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_569
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_569
.Lruntime_list_append_int_aligned_569: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_569: 
    mov rdi, [rsp]
    mov rsi, 1044
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_570
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_570
.Lruntime_list_append_int_aligned_570: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_570: 
    mov rdi, [rsp]
    mov rsi, 1046
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_571
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_571
.Lruntime_list_append_int_aligned_571: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_571: 
    mov rdi, [rsp]
    mov rsi, 1048
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_572
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_572
.Lruntime_list_append_int_aligned_572: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_572: 
    mov rdi, [rsp]
    mov rsi, 1050
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_573
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_573
.Lruntime_list_append_int_aligned_573: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_573: 
    mov rdi, [rsp]
    mov rsi, 1052
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_574
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_574
.Lruntime_list_append_int_aligned_574: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_574: 
    mov rdi, [rsp]
    mov rsi, 1054
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_575
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_575
.Lruntime_list_append_int_aligned_575: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_575: 
    mov rdi, [rsp]
    mov rsi, 1056
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_576
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_576
.Lruntime_list_append_int_aligned_576: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_576: 
    mov rdi, [rsp]
    mov rsi, 1058
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_577
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_577
.Lruntime_list_append_int_aligned_577: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_577: 
    mov rdi, [rsp]
    mov rsi, 1060
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_578
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_578
.Lruntime_list_append_int_aligned_578: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_578: 
    mov rdi, [rsp]
    mov rsi, 1062
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_579
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_579
.Lruntime_list_append_int_aligned_579: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_579: 
    mov rdi, [rsp]
    mov rsi, 1064
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_580
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_580
.Lruntime_list_append_int_aligned_580: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_580: 
    mov rdi, [rsp]
    mov rsi, 1066
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_581
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_581
.Lruntime_list_append_int_aligned_581: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_581: 
    mov rdi, [rsp]
    mov rsi, 1068
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_582
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_582
.Lruntime_list_append_int_aligned_582: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_582: 
    mov rdi, [rsp]
    mov rsi, 1070
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_583
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_583
.Lruntime_list_append_int_aligned_583: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_583: 
    mov rdi, [rsp]
    mov rsi, 1072
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_584
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_584
.Lruntime_list_append_int_aligned_584: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_584: 
    mov rdi, [rsp]
    mov rsi, 1074
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_585
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_585
.Lruntime_list_append_int_aligned_585: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_585: 
    mov rdi, [rsp]
    mov rsi, 1076
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_586
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_586
.Lruntime_list_append_int_aligned_586: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_586: 
    mov rdi, [rsp]
    mov rsi, 1078
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_587
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_587
.Lruntime_list_append_int_aligned_587: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_587: 
    mov rdi, [rsp]
    mov rsi, 1080
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_588
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_588
.Lruntime_list_append_int_aligned_588: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_588: 
    mov rdi, [rsp]
    mov rsi, 1082
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_589
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_589
.Lruntime_list_append_int_aligned_589: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_589: 
    mov rdi, [rsp]
    mov rsi, 1084
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_590
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_590
.Lruntime_list_append_int_aligned_590: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_590: 
    mov rdi, [rsp]
    mov rsi, 1086
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_591
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_591
.Lruntime_list_append_int_aligned_591: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_591: 
    mov rdi, [rsp]
    mov rsi, 1088
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_592
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_592
.Lruntime_list_append_int_aligned_592: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_592: 
    mov rdi, [rsp]
    mov rsi, 1090
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_593
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_593
.Lruntime_list_append_int_aligned_593: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_593: 
    mov rdi, [rsp]
    mov rsi, 1092
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_594
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_594
.Lruntime_list_append_int_aligned_594: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_594: 
    mov rdi, [rsp]
    mov rsi, 1094
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_595
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_595
.Lruntime_list_append_int_aligned_595: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_595: 
    mov rdi, [rsp]
    mov rsi, 1096
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_596
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_596
.Lruntime_list_append_int_aligned_596: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_596: 
    mov rdi, [rsp]
    mov rsi, 1098
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_597
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_597
.Lruntime_list_append_int_aligned_597: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_597: 
    mov rdi, [rsp]
    mov rsi, 1100
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_598
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_598
.Lruntime_list_append_int_aligned_598: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_598: 
    mov rdi, [rsp]
    mov rsi, 1102
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_599
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_599
.Lruntime_list_append_int_aligned_599: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_599: 
    mov rdi, [rsp]
    mov rsi, 1104
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_600
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_600
.Lruntime_list_append_int_aligned_600: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_600: 
    mov rdi, [rsp]
    mov rsi, 1106
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_601
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_601
.Lruntime_list_append_int_aligned_601: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_601: 
    mov rdi, [rsp]
    mov rsi, 1108
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_602
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_602
.Lruntime_list_append_int_aligned_602: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_602: 
    mov rdi, [rsp]
    mov rsi, 1110
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_603
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_603
.Lruntime_list_append_int_aligned_603: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_603: 
    mov rdi, [rsp]
    mov rsi, 1112
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_604
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_604
.Lruntime_list_append_int_aligned_604: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_604: 
    mov rdi, [rsp]
    mov rsi, 1114
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_605
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_605
.Lruntime_list_append_int_aligned_605: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_605: 
    mov rdi, [rsp]
    mov rsi, 1116
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_606
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_606
.Lruntime_list_append_int_aligned_606: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_606: 
    mov rdi, [rsp]
    mov rsi, 1118
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_607
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_607
.Lruntime_list_append_int_aligned_607: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_607: 
    mov rdi, [rsp]
    mov rsi, 1120
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_608
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_608
.Lruntime_list_append_int_aligned_608: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_608: 
    mov rdi, [rsp]
    mov rsi, 1122
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_609
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_609
.Lruntime_list_append_int_aligned_609: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_609: 
    mov rdi, [rsp]
    mov rsi, 1124
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_610
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_610
.Lruntime_list_append_int_aligned_610: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_610: 
    mov rdi, [rsp]
    mov rsi, 1126
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_611
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_611
.Lruntime_list_append_int_aligned_611: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_611: 
    mov rdi, [rsp]
    mov rsi, 1128
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_612
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_612
.Lruntime_list_append_int_aligned_612: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_612: 
    mov rdi, [rsp]
    mov rsi, 1130
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_613
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_613
.Lruntime_list_append_int_aligned_613: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_613: 
    mov rdi, [rsp]
    mov rsi, 1132
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_614
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_614
.Lruntime_list_append_int_aligned_614: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_614: 
    mov rdi, [rsp]
    mov rsi, 1134
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_615
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_615
.Lruntime_list_append_int_aligned_615: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_615: 
    mov rdi, [rsp]
    mov rsi, 1136
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_616
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_616
.Lruntime_list_append_int_aligned_616: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_616: 
    mov rdi, [rsp]
    mov rsi, 1138
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_617
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_617
.Lruntime_list_append_int_aligned_617: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_617: 
    mov rdi, [rsp]
    mov rsi, 1140
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_618
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_618
.Lruntime_list_append_int_aligned_618: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_618: 
    mov rdi, [rsp]
    mov rsi, 1142
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_619
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_619
.Lruntime_list_append_int_aligned_619: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_619: 
    mov rdi, [rsp]
    mov rsi, 1144
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_620
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_620
.Lruntime_list_append_int_aligned_620: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_620: 
    mov rdi, [rsp]
    mov rsi, 1146
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_621
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_621
.Lruntime_list_append_int_aligned_621: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_621: 
    mov rdi, [rsp]
    mov rsi, 1148
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_622
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_622
.Lruntime_list_append_int_aligned_622: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_622: 
    mov rdi, [rsp]
    mov rsi, 1150
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_623
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_623
.Lruntime_list_append_int_aligned_623: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_623: 
    mov rdi, [rsp]
    mov rsi, 1152
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_624
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_624
.Lruntime_list_append_int_aligned_624: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_624: 
    mov rdi, [rsp]
    mov rsi, 1154
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_625
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_625
.Lruntime_list_append_int_aligned_625: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_625: 
    mov rdi, [rsp]
    mov rsi, 1156
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_626
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_626
.Lruntime_list_append_int_aligned_626: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_626: 
    mov rdi, [rsp]
    mov rsi, 1158
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_627
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_627
.Lruntime_list_append_int_aligned_627: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_627: 
    mov rdi, [rsp]
    mov rsi, 1160
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_628
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_628
.Lruntime_list_append_int_aligned_628: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_628: 
    mov rdi, [rsp]
    mov rsi, 1162
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_629
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_629
.Lruntime_list_append_int_aligned_629: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_629: 
    mov rdi, [rsp]
    mov rsi, 1164
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_630
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_630
.Lruntime_list_append_int_aligned_630: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_630: 
    mov rdi, [rsp]
    mov rsi, 1166
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_631
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_631
.Lruntime_list_append_int_aligned_631: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_631: 
    mov rdi, [rsp]
    mov rsi, 1168
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_632
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_632
.Lruntime_list_append_int_aligned_632: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_632: 
    mov rdi, [rsp]
    mov rsi, 1170
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_633
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_633
.Lruntime_list_append_int_aligned_633: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_633: 
    mov rdi, [rsp]
    mov rsi, 1172
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_634
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_634
.Lruntime_list_append_int_aligned_634: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_634: 
    mov rdi, [rsp]
    mov rsi, 1174
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_635
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_635
.Lruntime_list_append_int_aligned_635: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_635: 
    mov rdi, [rsp]
    mov rsi, 1176
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_636
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_636
.Lruntime_list_append_int_aligned_636: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_636: 
    mov rdi, [rsp]
    mov rsi, 1178
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_637
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_637
.Lruntime_list_append_int_aligned_637: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_637: 
    mov rdi, [rsp]
    mov rsi, 1180
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_638
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_638
.Lruntime_list_append_int_aligned_638: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_638: 
    mov rdi, [rsp]
    mov rsi, 1182
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_639
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_639
.Lruntime_list_append_int_aligned_639: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_639: 
    mov rdi, [rsp]
    mov rsi, 1184
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_640
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_640
.Lruntime_list_append_int_aligned_640: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_640: 
    mov rdi, [rsp]
    mov rsi, 1186
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_641
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_641
.Lruntime_list_append_int_aligned_641: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_641: 
    mov rdi, [rsp]
    mov rsi, 1188
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_642
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_642
.Lruntime_list_append_int_aligned_642: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_642: 
    mov rdi, [rsp]
    mov rsi, 1190
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_643
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_643
.Lruntime_list_append_int_aligned_643: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_643: 
    mov rdi, [rsp]
    mov rsi, 1192
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_644
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_644
.Lruntime_list_append_int_aligned_644: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_644: 
    mov rdi, [rsp]
    mov rsi, 1194
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_645
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_645
.Lruntime_list_append_int_aligned_645: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_645: 
    mov rdi, [rsp]
    mov rsi, 1196
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_646
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_646
.Lruntime_list_append_int_aligned_646: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_646: 
    mov rdi, [rsp]
    mov rsi, 1198
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_647
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_647
.Lruntime_list_append_int_aligned_647: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_647: 
    mov rdi, [rsp]
    mov rsi, 1200
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_648
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_648
.Lruntime_list_append_int_aligned_648: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_648: 
    mov rdi, [rsp]
    mov rsi, 1202
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_649
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_649
.Lruntime_list_append_int_aligned_649: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_649: 
    mov rdi, [rsp]
    mov rsi, 1204
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_650
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_650
.Lruntime_list_append_int_aligned_650: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_650: 
    mov rdi, [rsp]
    mov rsi, 1206
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_651
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_651
.Lruntime_list_append_int_aligned_651: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_651: 
    mov rdi, [rsp]
    mov rsi, 1208
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_652
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_652
.Lruntime_list_append_int_aligned_652: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_652: 
    mov rdi, [rsp]
    mov rsi, 1210
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_653
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_653
.Lruntime_list_append_int_aligned_653: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_653: 
    mov rdi, [rsp]
    mov rsi, 1212
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_654
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_654
.Lruntime_list_append_int_aligned_654: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_654: 
    mov rdi, [rsp]
    mov rsi, 1214
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_655
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_655
.Lruntime_list_append_int_aligned_655: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_655: 
    mov rdi, [rsp]
    mov rsi, 1216
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_656
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_656
.Lruntime_list_append_int_aligned_656: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_656: 
    mov rdi, [rsp]
    mov rsi, 1218
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_657
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_657
.Lruntime_list_append_int_aligned_657: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_657: 
    mov rdi, [rsp]
    mov rsi, 1220
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_658
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_658
.Lruntime_list_append_int_aligned_658: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_658: 
    mov rdi, [rsp]
    mov rsi, 1222
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_659
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_659
.Lruntime_list_append_int_aligned_659: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_659: 
    mov rdi, [rsp]
    mov rsi, 1224
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_660
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_660
.Lruntime_list_append_int_aligned_660: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_660: 
    mov rdi, [rsp]
    mov rsi, 1226
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_661
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_661
.Lruntime_list_append_int_aligned_661: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_661: 
    mov rdi, [rsp]
    mov rsi, 1228
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_662
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_662
.Lruntime_list_append_int_aligned_662: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_662: 
    mov rdi, [rsp]
    mov rsi, 1230
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_663
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_663
.Lruntime_list_append_int_aligned_663: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_663: 
    mov rdi, [rsp]
    mov rsi, 1232
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_664
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_664
.Lruntime_list_append_int_aligned_664: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_664: 
    mov rdi, [rsp]
    mov rsi, 1234
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_665
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_665
.Lruntime_list_append_int_aligned_665: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_665: 
    mov rdi, [rsp]
    mov rsi, 1236
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_666
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_666
.Lruntime_list_append_int_aligned_666: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_666: 
    mov rdi, [rsp]
    mov rsi, 1238
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_667
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_667
.Lruntime_list_append_int_aligned_667: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_667: 
    mov rdi, [rsp]
    mov rsi, 1240
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_668
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_668
.Lruntime_list_append_int_aligned_668: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_668: 
    mov rdi, [rsp]
    mov rsi, 1242
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_669
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_669
.Lruntime_list_append_int_aligned_669: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_669: 
    mov rdi, [rsp]
    mov rsi, 1244
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_670
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_670
.Lruntime_list_append_int_aligned_670: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_670: 
    mov rdi, [rsp]
    mov rsi, 1246
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_671
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_671
.Lruntime_list_append_int_aligned_671: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_671: 
    mov rdi, [rsp]
    mov rsi, 1248
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_672
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_672
.Lruntime_list_append_int_aligned_672: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_672: 
    mov rdi, [rsp]
    mov rsi, 1250
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_673
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_673
.Lruntime_list_append_int_aligned_673: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_673: 
    mov rdi, [rsp]
    mov rsi, 1252
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_674
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_674
.Lruntime_list_append_int_aligned_674: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_674: 
    mov rdi, [rsp]
    mov rsi, 1254
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_675
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_675
.Lruntime_list_append_int_aligned_675: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_675: 
    mov rdi, [rsp]
    mov rsi, 1256
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_676
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_676
.Lruntime_list_append_int_aligned_676: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_676: 
    mov rdi, [rsp]
    mov rsi, 1258
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_677
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_677
.Lruntime_list_append_int_aligned_677: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_677: 
    mov rdi, [rsp]
    mov rsi, 1260
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_678
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_678
.Lruntime_list_append_int_aligned_678: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_678: 
    mov rdi, [rsp]
    mov rsi, 1262
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_679
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_679
.Lruntime_list_append_int_aligned_679: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_679: 
    mov rdi, [rsp]
    mov rsi, 1264
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_680
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_680
.Lruntime_list_append_int_aligned_680: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_680: 
    mov rdi, [rsp]
    mov rsi, 1266
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_681
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_681
.Lruntime_list_append_int_aligned_681: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_681: 
    mov rdi, [rsp]
    mov rsi, 1268
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_682
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_682
.Lruntime_list_append_int_aligned_682: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_682: 
    mov rdi, [rsp]
    mov rsi, 1270
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_683
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_683
.Lruntime_list_append_int_aligned_683: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_683: 
    mov rdi, [rsp]
    mov rsi, 1272
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_684
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_684
.Lruntime_list_append_int_aligned_684: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_684: 
    mov rdi, [rsp]
    mov rsi, 1274
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_685
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_685
.Lruntime_list_append_int_aligned_685: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_685: 
    mov rdi, [rsp]
    mov rsi, 1276
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_686
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_686
.Lruntime_list_append_int_aligned_686: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_686: 
    mov rdi, [rsp]
    mov rsi, 1278
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_687
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_687
.Lruntime_list_append_int_aligned_687: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_687: 
    mov rdi, [rsp]
    mov rsi, 1280
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_688
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_688
.Lruntime_list_append_int_aligned_688: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_688: 
    mov rdi, [rsp]
    mov rsi, 1282
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_689
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_689
.Lruntime_list_append_int_aligned_689: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_689: 
    mov rdi, [rsp]
    mov rsi, 1284
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_690
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_690
.Lruntime_list_append_int_aligned_690: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_690: 
    mov rdi, [rsp]
    mov rsi, 1286
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_691
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_691
.Lruntime_list_append_int_aligned_691: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_691: 
    mov rdi, [rsp]
    mov rsi, 1288
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_692
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_692
.Lruntime_list_append_int_aligned_692: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_692: 
    mov rdi, [rsp]
    mov rsi, 1290
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_693
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_693
.Lruntime_list_append_int_aligned_693: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_693: 
    mov rdi, [rsp]
    mov rsi, 1292
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_694
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_694
.Lruntime_list_append_int_aligned_694: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_694: 
    mov rdi, [rsp]
    mov rsi, 1294
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_695
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_695
.Lruntime_list_append_int_aligned_695: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_695: 
    mov rdi, [rsp]
    mov rsi, 1296
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_696
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_696
.Lruntime_list_append_int_aligned_696: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_696: 
    mov rdi, [rsp]
    mov rsi, 1298
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_697
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_697
.Lruntime_list_append_int_aligned_697: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_697: 
    mov rdi, [rsp]
    mov rsi, 1300
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_698
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_698
.Lruntime_list_append_int_aligned_698: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_698: 
    mov rdi, [rsp]
    mov rsi, 1302
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_699
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_699
.Lruntime_list_append_int_aligned_699: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_699: 
    mov rdi, [rsp]
    mov rsi, 1304
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_700
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_700
.Lruntime_list_append_int_aligned_700: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_700: 
    mov rdi, [rsp]
    mov rsi, 1306
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_701
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_701
.Lruntime_list_append_int_aligned_701: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_701: 
    mov rdi, [rsp]
    mov rsi, 1308
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_702
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_702
.Lruntime_list_append_int_aligned_702: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_702: 
    mov rdi, [rsp]
    mov rsi, 1310
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_703
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_703
.Lruntime_list_append_int_aligned_703: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_703: 
    mov rdi, [rsp]
    mov rsi, 1312
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_704
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_704
.Lruntime_list_append_int_aligned_704: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_704: 
    mov rdi, [rsp]
    mov rsi, 1314
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_705
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_705
.Lruntime_list_append_int_aligned_705: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_705: 
    mov rdi, [rsp]
    mov rsi, 1316
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_706
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_706
.Lruntime_list_append_int_aligned_706: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_706: 
    mov rdi, [rsp]
    mov rsi, 1318
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_707
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_707
.Lruntime_list_append_int_aligned_707: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_707: 
    mov rdi, [rsp]
    mov rsi, 1320
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_708
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_708
.Lruntime_list_append_int_aligned_708: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_708: 
    mov rdi, [rsp]
    mov rsi, 1322
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_709
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_709
.Lruntime_list_append_int_aligned_709: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_709: 
    mov rdi, [rsp]
    mov rsi, 1324
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_710
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_710
.Lruntime_list_append_int_aligned_710: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_710: 
    mov rdi, [rsp]
    mov rsi, 1326
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_711
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_711
.Lruntime_list_append_int_aligned_711: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_711: 
    mov rdi, [rsp]
    mov rsi, 1328
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_712
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_712
.Lruntime_list_append_int_aligned_712: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_712: 
    mov rdi, [rsp]
    mov rsi, 1330
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_713
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_713
.Lruntime_list_append_int_aligned_713: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_713: 
    mov rdi, [rsp]
    mov rsi, 1332
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_714
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_714
.Lruntime_list_append_int_aligned_714: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_714: 
    mov rdi, [rsp]
    mov rsi, 1334
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_715
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_715
.Lruntime_list_append_int_aligned_715: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_715: 
    mov rdi, [rsp]
    mov rsi, 1336
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_716
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_716
.Lruntime_list_append_int_aligned_716: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_716: 
    mov rdi, [rsp]
    mov rsi, 1338
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_717
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_717
.Lruntime_list_append_int_aligned_717: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_717: 
    mov rdi, [rsp]
    mov rsi, 1340
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_718
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_718
.Lruntime_list_append_int_aligned_718: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_718: 
    mov rdi, [rsp]
    mov rsi, 1342
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_719
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_719
.Lruntime_list_append_int_aligned_719: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_719: 
    mov rdi, [rsp]
    mov rsi, 1344
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_720
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_720
.Lruntime_list_append_int_aligned_720: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_720: 
    mov rdi, [rsp]
    mov rsi, 1346
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_721
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_721
.Lruntime_list_append_int_aligned_721: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_721: 
    mov rdi, [rsp]
    mov rsi, 1348
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_722
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_722
.Lruntime_list_append_int_aligned_722: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_722: 
    mov rdi, [rsp]
    mov rsi, 1350
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_723
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_723
.Lruntime_list_append_int_aligned_723: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_723: 
    mov rdi, [rsp]
    mov rsi, 1352
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_724
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_724
.Lruntime_list_append_int_aligned_724: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_724: 
    mov rdi, [rsp]
    mov rsi, 1354
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_725
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_725
.Lruntime_list_append_int_aligned_725: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_725: 
    mov rdi, [rsp]
    mov rsi, 1356
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_726
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_726
.Lruntime_list_append_int_aligned_726: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_726: 
    mov rdi, [rsp]
    mov rsi, 1358
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_727
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_727
.Lruntime_list_append_int_aligned_727: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_727: 
    mov rdi, [rsp]
    mov rsi, 1360
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_728
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_728
.Lruntime_list_append_int_aligned_728: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_728: 
    mov rdi, [rsp]
    mov rsi, 1362
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_729
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_729
.Lruntime_list_append_int_aligned_729: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_729: 
    mov rdi, [rsp]
    mov rsi, 1364
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_730
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_730
.Lruntime_list_append_int_aligned_730: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_730: 
    mov rdi, [rsp]
    mov rsi, 1366
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_731
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_731
.Lruntime_list_append_int_aligned_731: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_731: 
    mov rdi, [rsp]
    mov rsi, 1368
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_732
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_732
.Lruntime_list_append_int_aligned_732: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_732: 
    mov rdi, [rsp]
    mov rsi, 1370
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_733
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_733
.Lruntime_list_append_int_aligned_733: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_733: 
    mov rdi, [rsp]
    mov rsi, 1372
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_734
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_734
.Lruntime_list_append_int_aligned_734: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_734: 
    mov rdi, [rsp]
    mov rsi, 1374
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_735
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_735
.Lruntime_list_append_int_aligned_735: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_735: 
    mov rdi, [rsp]
    mov rsi, 1376
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_736
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_736
.Lruntime_list_append_int_aligned_736: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_736: 
    mov rdi, [rsp]
    mov rsi, 1378
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_737
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_737
.Lruntime_list_append_int_aligned_737: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_737: 
    mov rdi, [rsp]
    mov rsi, 1380
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_738
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_738
.Lruntime_list_append_int_aligned_738: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_738: 
    mov rdi, [rsp]
    mov rsi, 1382
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_739
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_739
.Lruntime_list_append_int_aligned_739: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_739: 
    mov rdi, [rsp]
    mov rsi, 1384
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_740
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_740
.Lruntime_list_append_int_aligned_740: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_740: 
    mov rdi, [rsp]
    mov rsi, 1386
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_741
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_741
.Lruntime_list_append_int_aligned_741: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_741: 
    mov rdi, [rsp]
    mov rsi, 1388
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_742
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_742
.Lruntime_list_append_int_aligned_742: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_742: 
    mov rdi, [rsp]
    mov rsi, 1390
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_743
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_743
.Lruntime_list_append_int_aligned_743: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_743: 
    mov rdi, [rsp]
    mov rsi, 1392
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_744
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_744
.Lruntime_list_append_int_aligned_744: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_744: 
    mov rdi, [rsp]
    mov rsi, 1394
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_745
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_745
.Lruntime_list_append_int_aligned_745: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_745: 
    mov rdi, [rsp]
    mov rsi, 1396
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_746
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_746
.Lruntime_list_append_int_aligned_746: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_746: 
    mov rdi, [rsp]
    mov rsi, 1398
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_747
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_747
.Lruntime_list_append_int_aligned_747: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_747: 
    mov rdi, [rsp]
    mov rsi, 1400
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_748
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_748
.Lruntime_list_append_int_aligned_748: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_748: 
    mov rdi, [rsp]
    mov rsi, 1402
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_749
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_749
.Lruntime_list_append_int_aligned_749: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_749: 
    mov rdi, [rsp]
    mov rsi, 1404
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_750
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_750
.Lruntime_list_append_int_aligned_750: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_750: 
    mov rdi, [rsp]
    mov rsi, 1406
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_751
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_751
.Lruntime_list_append_int_aligned_751: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_751: 
    mov rdi, [rsp]
    mov rsi, 1408
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_752
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_752
.Lruntime_list_append_int_aligned_752: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_752: 
    mov rdi, [rsp]
    mov rsi, 1410
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_753
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_753
.Lruntime_list_append_int_aligned_753: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_753: 
    mov rdi, [rsp]
    mov rsi, 1412
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_754
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_754
.Lruntime_list_append_int_aligned_754: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_754: 
    mov rdi, [rsp]
    mov rsi, 1414
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_755
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_755
.Lruntime_list_append_int_aligned_755: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_755: 
    mov rdi, [rsp]
    mov rsi, 1416
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_756
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_756
.Lruntime_list_append_int_aligned_756: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_756: 
    mov rdi, [rsp]
    mov rsi, 1418
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_757
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_757
.Lruntime_list_append_int_aligned_757: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_757: 
    mov rdi, [rsp]
    mov rsi, 1420
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_758
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_758
.Lruntime_list_append_int_aligned_758: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_758: 
    mov rdi, [rsp]
    mov rsi, 1422
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_759
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_759
.Lruntime_list_append_int_aligned_759: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_759: 
    mov rdi, [rsp]
    mov rsi, 1424
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_760
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_760
.Lruntime_list_append_int_aligned_760: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_760: 
    mov rdi, [rsp]
    mov rsi, 1426
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_761
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_761
.Lruntime_list_append_int_aligned_761: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_761: 
    mov rdi, [rsp]
    mov rsi, 1428
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_762
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_762
.Lruntime_list_append_int_aligned_762: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_762: 
    mov rdi, [rsp]
    mov rsi, 1430
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_763
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_763
.Lruntime_list_append_int_aligned_763: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_763: 
    mov rdi, [rsp]
    mov rsi, 1432
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_764
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_764
.Lruntime_list_append_int_aligned_764: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_764: 
    mov rdi, [rsp]
    mov rsi, 1434
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_765
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_765
.Lruntime_list_append_int_aligned_765: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_765: 
    mov rdi, [rsp]
    mov rsi, 1436
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_766
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_766
.Lruntime_list_append_int_aligned_766: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_766: 
    mov rdi, [rsp]
    mov rsi, 1438
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_767
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_767
.Lruntime_list_append_int_aligned_767: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_767: 
    mov rdi, [rsp]
    mov rsi, 1440
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_768
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_768
.Lruntime_list_append_int_aligned_768: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_768: 
    mov rdi, [rsp]
    mov rsi, 1442
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_769
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_769
.Lruntime_list_append_int_aligned_769: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_769: 
    mov rdi, [rsp]
    mov rsi, 1444
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_770
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_770
.Lruntime_list_append_int_aligned_770: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_770: 
    mov rdi, [rsp]
    mov rsi, 1446
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_771
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_771
.Lruntime_list_append_int_aligned_771: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_771: 
    mov rdi, [rsp]
    mov rsi, 1448
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_772
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_772
.Lruntime_list_append_int_aligned_772: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_772: 
    mov rdi, [rsp]
    mov rsi, 1450
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_773
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_773
.Lruntime_list_append_int_aligned_773: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_773: 
    mov rdi, [rsp]
    mov rsi, 1452
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_774
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_774
.Lruntime_list_append_int_aligned_774: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_774: 
    mov rdi, [rsp]
    mov rsi, 1454
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_775
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_775
.Lruntime_list_append_int_aligned_775: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_775: 
    mov rdi, [rsp]
    mov rsi, 1456
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_776
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_776
.Lruntime_list_append_int_aligned_776: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_776: 
    mov rdi, [rsp]
    mov rsi, 1458
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_777
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_777
.Lruntime_list_append_int_aligned_777: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_777: 
    mov rdi, [rsp]
    mov rsi, 1460
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_778
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_778
.Lruntime_list_append_int_aligned_778: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_778: 
    mov rdi, [rsp]
    mov rsi, 1462
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_779
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_779
.Lruntime_list_append_int_aligned_779: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_779: 
    mov rdi, [rsp]
    mov rsi, 1464
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_780
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_780
.Lruntime_list_append_int_aligned_780: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_780: 
    mov rdi, [rsp]
    mov rsi, 1466
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_781
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_781
.Lruntime_list_append_int_aligned_781: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_781: 
    mov rdi, [rsp]
    mov rsi, 1468
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_782
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_782
.Lruntime_list_append_int_aligned_782: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_782: 
    mov rdi, [rsp]
    mov rsi, 1470
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_783
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_783
.Lruntime_list_append_int_aligned_783: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_783: 
    mov rdi, [rsp]
    mov rsi, 1472
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_784
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_784
.Lruntime_list_append_int_aligned_784: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_784: 
    mov rdi, [rsp]
    mov rsi, 1474
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_785
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_785
.Lruntime_list_append_int_aligned_785: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_785: 
    mov rdi, [rsp]
    mov rsi, 1476
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_786
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_786
.Lruntime_list_append_int_aligned_786: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_786: 
    mov rdi, [rsp]
    mov rsi, 1478
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_787
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_787
.Lruntime_list_append_int_aligned_787: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_787: 
    mov rdi, [rsp]
    mov rsi, 1480
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_788
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_788
.Lruntime_list_append_int_aligned_788: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_788: 
    mov rdi, [rsp]
    mov rsi, 1482
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_789
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_789
.Lruntime_list_append_int_aligned_789: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_789: 
    mov rdi, [rsp]
    mov rsi, 1484
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_790
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_790
.Lruntime_list_append_int_aligned_790: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_790: 
    mov rdi, [rsp]
    mov rsi, 1486
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_791
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_791
.Lruntime_list_append_int_aligned_791: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_791: 
    mov rdi, [rsp]
    mov rsi, 1488
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_792
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_792
.Lruntime_list_append_int_aligned_792: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_792: 
    mov rdi, [rsp]
    mov rsi, 1490
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_793
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_793
.Lruntime_list_append_int_aligned_793: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_793: 
    mov rdi, [rsp]
    mov rsi, 1492
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_794
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_794
.Lruntime_list_append_int_aligned_794: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_794: 
    mov rdi, [rsp]
    mov rsi, 1494
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_795
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_795
.Lruntime_list_append_int_aligned_795: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_795: 
    mov rdi, [rsp]
    mov rsi, 1496
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_796
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_796
.Lruntime_list_append_int_aligned_796: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_796: 
    mov rdi, [rsp]
    mov rsi, 1498
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_797
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_797
.Lruntime_list_append_int_aligned_797: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_797: 
    mov rdi, [rsp]
    mov rsi, 1500
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_798
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_798
.Lruntime_list_append_int_aligned_798: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_798: 
    mov rdi, [rsp]
    mov rsi, 1502
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_799
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_799
.Lruntime_list_append_int_aligned_799: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_799: 
    mov rdi, [rsp]
    mov rsi, 1504
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_800
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_800
.Lruntime_list_append_int_aligned_800: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_800: 
    mov rdi, [rsp]
    mov rsi, 1506
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_801
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_801
.Lruntime_list_append_int_aligned_801: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_801: 
    mov rdi, [rsp]
    mov rsi, 1508
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_802
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_802
.Lruntime_list_append_int_aligned_802: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_802: 
    mov rdi, [rsp]
    mov rsi, 1510
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_803
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_803
.Lruntime_list_append_int_aligned_803: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_803: 
    mov rdi, [rsp]
    mov rsi, 1512
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_804
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_804
.Lruntime_list_append_int_aligned_804: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_804: 
    mov rdi, [rsp]
    mov rsi, 1514
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_805
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_805
.Lruntime_list_append_int_aligned_805: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_805: 
    mov rdi, [rsp]
    mov rsi, 1516
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_806
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_806
.Lruntime_list_append_int_aligned_806: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_806: 
    mov rdi, [rsp]
    mov rsi, 1518
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_807
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_807
.Lruntime_list_append_int_aligned_807: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_807: 
    mov rdi, [rsp]
    mov rsi, 1520
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_808
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_808
.Lruntime_list_append_int_aligned_808: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_808: 
    mov rdi, [rsp]
    mov rsi, 1522
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_809
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_809
.Lruntime_list_append_int_aligned_809: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_809: 
    mov rdi, [rsp]
    mov rsi, 1524
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_810
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_810
.Lruntime_list_append_int_aligned_810: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_810: 
    mov rdi, [rsp]
    mov rsi, 1526
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_811
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_811
.Lruntime_list_append_int_aligned_811: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_811: 
    mov rdi, [rsp]
    mov rsi, 1528
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_812
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_812
.Lruntime_list_append_int_aligned_812: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_812: 
    mov rdi, [rsp]
    mov rsi, 1530
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_813
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_813
.Lruntime_list_append_int_aligned_813: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_813: 
    mov rdi, [rsp]
    mov rsi, 1532
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_814
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_814
.Lruntime_list_append_int_aligned_814: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_814: 
    mov rdi, [rsp]
    mov rsi, 1534
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_815
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_815
.Lruntime_list_append_int_aligned_815: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_815: 
    mov rdi, [rsp]
    mov rsi, 1536
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_816
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_816
.Lruntime_list_append_int_aligned_816: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_816: 
    mov rdi, [rsp]
    mov rsi, 1538
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_817
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_817
.Lruntime_list_append_int_aligned_817: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_817: 
    mov rdi, [rsp]
    mov rsi, 1540
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_818
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_818
.Lruntime_list_append_int_aligned_818: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_818: 
    mov rdi, [rsp]
    mov rsi, 1542
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_819
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_819
.Lruntime_list_append_int_aligned_819: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_819: 
    mov rdi, [rsp]
    mov rsi, 1544
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_820
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_820
.Lruntime_list_append_int_aligned_820: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_820: 
    mov rdi, [rsp]
    mov rsi, 1546
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_821
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_821
.Lruntime_list_append_int_aligned_821: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_821: 
    mov rdi, [rsp]
    mov rsi, 1548
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_822
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_822
.Lruntime_list_append_int_aligned_822: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_822: 
    mov rdi, [rsp]
    mov rsi, 1550
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_823
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_823
.Lruntime_list_append_int_aligned_823: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_823: 
    mov rdi, [rsp]
    mov rsi, 1552
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_824
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_824
.Lruntime_list_append_int_aligned_824: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_824: 
    mov rdi, [rsp]
    mov rsi, 1554
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_825
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_825
.Lruntime_list_append_int_aligned_825: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_825: 
    mov rdi, [rsp]
    mov rsi, 1556
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_826
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_826
.Lruntime_list_append_int_aligned_826: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_826: 
    mov rdi, [rsp]
    mov rsi, 1558
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_827
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_827
.Lruntime_list_append_int_aligned_827: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_827: 
    mov rdi, [rsp]
    mov rsi, 1560
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_828
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_828
.Lruntime_list_append_int_aligned_828: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_828: 
    mov rdi, [rsp]
    mov rsi, 1562
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_829
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_829
.Lruntime_list_append_int_aligned_829: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_829: 
    mov rdi, [rsp]
    mov rsi, 1564
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_830
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_830
.Lruntime_list_append_int_aligned_830: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_830: 
    mov rdi, [rsp]
    mov rsi, 1566
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_831
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_831
.Lruntime_list_append_int_aligned_831: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_831: 
    mov rdi, [rsp]
    mov rsi, 1568
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_832
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_832
.Lruntime_list_append_int_aligned_832: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_832: 
    mov rdi, [rsp]
    mov rsi, 1570
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_833
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_833
.Lruntime_list_append_int_aligned_833: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_833: 
    mov rdi, [rsp]
    mov rsi, 1572
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_834
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_834
.Lruntime_list_append_int_aligned_834: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_834: 
    mov rdi, [rsp]
    mov rsi, 1574
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_835
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_835
.Lruntime_list_append_int_aligned_835: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_835: 
    mov rdi, [rsp]
    mov rsi, 1576
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_836
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_836
.Lruntime_list_append_int_aligned_836: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_836: 
    mov rdi, [rsp]
    mov rsi, 1578
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_837
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_837
.Lruntime_list_append_int_aligned_837: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_837: 
    mov rdi, [rsp]
    mov rsi, 1580
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_838
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_838
.Lruntime_list_append_int_aligned_838: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_838: 
    mov rdi, [rsp]
    mov rsi, 1582
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_839
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_839
.Lruntime_list_append_int_aligned_839: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_839: 
    mov rdi, [rsp]
    mov rsi, 1584
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_840
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_840
.Lruntime_list_append_int_aligned_840: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_840: 
    mov rdi, [rsp]
    mov rsi, 1586
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_841
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_841
.Lruntime_list_append_int_aligned_841: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_841: 
    mov rdi, [rsp]
    mov rsi, 1588
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_842
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_842
.Lruntime_list_append_int_aligned_842: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_842: 
    mov rdi, [rsp]
    mov rsi, 1590
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_843
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_843
.Lruntime_list_append_int_aligned_843: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_843: 
    mov rdi, [rsp]
    mov rsi, 1592
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_844
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_844
.Lruntime_list_append_int_aligned_844: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_844: 
    mov rdi, [rsp]
    mov rsi, 1594
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_845
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_845
.Lruntime_list_append_int_aligned_845: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_845: 
    mov rdi, [rsp]
    mov rsi, 1596
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_846
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_846
.Lruntime_list_append_int_aligned_846: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_846: 
    mov rdi, [rsp]
    mov rsi, 1598
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_847
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_847
.Lruntime_list_append_int_aligned_847: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_847: 
    mov rdi, [rsp]
    mov rsi, 1600
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_848
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_848
.Lruntime_list_append_int_aligned_848: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_848: 
    mov rdi, [rsp]
    mov rsi, 1602
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_849
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_849
.Lruntime_list_append_int_aligned_849: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_849: 
    mov rdi, [rsp]
    mov rsi, 1604
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_850
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_850
.Lruntime_list_append_int_aligned_850: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_850: 
    mov rdi, [rsp]
    mov rsi, 1606
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_851
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_851
.Lruntime_list_append_int_aligned_851: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_851: 
    mov rdi, [rsp]
    mov rsi, 1608
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_852
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_852
.Lruntime_list_append_int_aligned_852: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_852: 
    mov rdi, [rsp]
    mov rsi, 1610
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_853
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_853
.Lruntime_list_append_int_aligned_853: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_853: 
    mov rdi, [rsp]
    mov rsi, 1612
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_854
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_854
.Lruntime_list_append_int_aligned_854: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_854: 
    mov rdi, [rsp]
    mov rsi, 1614
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_855
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_855
.Lruntime_list_append_int_aligned_855: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_855: 
    mov rdi, [rsp]
    mov rsi, 1616
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_856
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_856
.Lruntime_list_append_int_aligned_856: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_856: 
    mov rdi, [rsp]
    mov rsi, 1618
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_857
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_857
.Lruntime_list_append_int_aligned_857: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_857: 
    mov rdi, [rsp]
    mov rsi, 1620
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_858
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_858
.Lruntime_list_append_int_aligned_858: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_858: 
    mov rdi, [rsp]
    mov rsi, 1622
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_859
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_859
.Lruntime_list_append_int_aligned_859: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_859: 
    mov rdi, [rsp]
    mov rsi, 1624
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_860
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_860
.Lruntime_list_append_int_aligned_860: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_860: 
    mov rdi, [rsp]
    mov rsi, 1626
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_861
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_861
.Lruntime_list_append_int_aligned_861: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_861: 
    mov rdi, [rsp]
    mov rsi, 1628
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_862
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_862
.Lruntime_list_append_int_aligned_862: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_862: 
    mov rdi, [rsp]
    mov rsi, 1630
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_863
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_863
.Lruntime_list_append_int_aligned_863: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_863: 
    mov rdi, [rsp]
    mov rsi, 1632
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_864
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_864
.Lruntime_list_append_int_aligned_864: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_864: 
    mov rdi, [rsp]
    mov rsi, 1634
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_865
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_865
.Lruntime_list_append_int_aligned_865: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_865: 
    mov rdi, [rsp]
    mov rsi, 1636
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_866
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_866
.Lruntime_list_append_int_aligned_866: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_866: 
    mov rdi, [rsp]
    mov rsi, 1638
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_867
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_867
.Lruntime_list_append_int_aligned_867: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_867: 
    mov rdi, [rsp]
    mov rsi, 1640
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_868
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_868
.Lruntime_list_append_int_aligned_868: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_868: 
    mov rdi, [rsp]
    mov rsi, 1642
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_869
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_869
.Lruntime_list_append_int_aligned_869: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_869: 
    mov rdi, [rsp]
    mov rsi, 1644
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_870
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_870
.Lruntime_list_append_int_aligned_870: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_870: 
    mov rdi, [rsp]
    mov rsi, 1646
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_871
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_871
.Lruntime_list_append_int_aligned_871: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_871: 
    mov rdi, [rsp]
    mov rsi, 1648
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_872
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_872
.Lruntime_list_append_int_aligned_872: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_872: 
    mov rdi, [rsp]
    mov rsi, 1650
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_873
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_873
.Lruntime_list_append_int_aligned_873: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_873: 
    mov rdi, [rsp]
    mov rsi, 1652
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_874
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_874
.Lruntime_list_append_int_aligned_874: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_874: 
    mov rdi, [rsp]
    mov rsi, 1654
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_875
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_875
.Lruntime_list_append_int_aligned_875: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_875: 
    mov rdi, [rsp]
    mov rsi, 1656
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_876
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_876
.Lruntime_list_append_int_aligned_876: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_876: 
    mov rdi, [rsp]
    mov rsi, 1658
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_877
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_877
.Lruntime_list_append_int_aligned_877: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_877: 
    mov rdi, [rsp]
    mov rsi, 1660
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_878
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_878
.Lruntime_list_append_int_aligned_878: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_878: 
    mov rdi, [rsp]
    mov rsi, 1662
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_879
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_879
.Lruntime_list_append_int_aligned_879: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_879: 
    mov rdi, [rsp]
    mov rsi, 1664
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_880
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_880
.Lruntime_list_append_int_aligned_880: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_880: 
    mov rdi, [rsp]
    mov rsi, 1666
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_881
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_881
.Lruntime_list_append_int_aligned_881: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_881: 
    mov rdi, [rsp]
    mov rsi, 1668
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_882
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_882
.Lruntime_list_append_int_aligned_882: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_882: 
    mov rdi, [rsp]
    mov rsi, 1670
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_883
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_883
.Lruntime_list_append_int_aligned_883: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_883: 
    mov rdi, [rsp]
    mov rsi, 1672
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_884
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_884
.Lruntime_list_append_int_aligned_884: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_884: 
    mov rdi, [rsp]
    mov rsi, 1674
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_885
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_885
.Lruntime_list_append_int_aligned_885: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_885: 
    mov rdi, [rsp]
    mov rsi, 1676
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_886
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_886
.Lruntime_list_append_int_aligned_886: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_886: 
    mov rdi, [rsp]
    mov rsi, 1678
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_887
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_887
.Lruntime_list_append_int_aligned_887: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_887: 
    mov rdi, [rsp]
    mov rsi, 1680
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_888
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_888
.Lruntime_list_append_int_aligned_888: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_888: 
    mov rdi, [rsp]
    mov rsi, 1682
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_889
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_889
.Lruntime_list_append_int_aligned_889: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_889: 
    mov rdi, [rsp]
    mov rsi, 1684
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_890
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_890
.Lruntime_list_append_int_aligned_890: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_890: 
    mov rdi, [rsp]
    mov rsi, 1686
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_891
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_891
.Lruntime_list_append_int_aligned_891: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_891: 
    mov rdi, [rsp]
    mov rsi, 1688
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_892
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_892
.Lruntime_list_append_int_aligned_892: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_892: 
    mov rdi, [rsp]
    mov rsi, 1690
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_893
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_893
.Lruntime_list_append_int_aligned_893: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_893: 
    mov rdi, [rsp]
    mov rsi, 1692
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_894
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_894
.Lruntime_list_append_int_aligned_894: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_894: 
    mov rdi, [rsp]
    mov rsi, 1694
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_895
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_895
.Lruntime_list_append_int_aligned_895: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_895: 
    mov rdi, [rsp]
    mov rsi, 1696
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_896
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_896
.Lruntime_list_append_int_aligned_896: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_896: 
    mov rdi, [rsp]
    mov rsi, 1698
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_897
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_897
.Lruntime_list_append_int_aligned_897: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_897: 
    mov rdi, [rsp]
    mov rsi, 1700
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_898
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_898
.Lruntime_list_append_int_aligned_898: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_898: 
    mov rdi, [rsp]
    mov rsi, 1702
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_899
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_899
.Lruntime_list_append_int_aligned_899: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_899: 
    mov rdi, [rsp]
    mov rsi, 1704
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_900
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_900
.Lruntime_list_append_int_aligned_900: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_900: 
    mov rdi, [rsp]
    mov rsi, 1706
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_901
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_901
.Lruntime_list_append_int_aligned_901: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_901: 
    mov rdi, [rsp]
    mov rsi, 1708
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_902
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_902
.Lruntime_list_append_int_aligned_902: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_902: 
    mov rdi, [rsp]
    mov rsi, 1710
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_903
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_903
.Lruntime_list_append_int_aligned_903: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_903: 
    mov rdi, [rsp]
    mov rsi, 1712
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_904
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_904
.Lruntime_list_append_int_aligned_904: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_904: 
    mov rdi, [rsp]
    mov rsi, 1714
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_905
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_905
.Lruntime_list_append_int_aligned_905: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_905: 
    mov rdi, [rsp]
    mov rsi, 1716
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_906
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_906
.Lruntime_list_append_int_aligned_906: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_906: 
    mov rdi, [rsp]
    mov rsi, 1718
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_907
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_907
.Lruntime_list_append_int_aligned_907: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_907: 
    mov rdi, [rsp]
    mov rsi, 1720
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_908
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_908
.Lruntime_list_append_int_aligned_908: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_908: 
    mov rdi, [rsp]
    mov rsi, 1722
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_909
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_909
.Lruntime_list_append_int_aligned_909: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_909: 
    mov rdi, [rsp]
    mov rsi, 1724
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_910
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_910
.Lruntime_list_append_int_aligned_910: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_910: 
    mov rdi, [rsp]
    mov rsi, 1726
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_911
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_911
.Lruntime_list_append_int_aligned_911: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_911: 
    mov rdi, [rsp]
    mov rsi, 1728
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_912
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_912
.Lruntime_list_append_int_aligned_912: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_912: 
    mov rdi, [rsp]
    mov rsi, 1730
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_913
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_913
.Lruntime_list_append_int_aligned_913: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_913: 
    mov rdi, [rsp]
    mov rsi, 1732
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_914
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_914
.Lruntime_list_append_int_aligned_914: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_914: 
    mov rdi, [rsp]
    mov rsi, 1734
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_915
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_915
.Lruntime_list_append_int_aligned_915: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_915: 
    mov rdi, [rsp]
    mov rsi, 1736
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_916
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_916
.Lruntime_list_append_int_aligned_916: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_916: 
    mov rdi, [rsp]
    mov rsi, 1738
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_917
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_917
.Lruntime_list_append_int_aligned_917: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_917: 
    mov rdi, [rsp]
    mov rsi, 1740
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_918
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_918
.Lruntime_list_append_int_aligned_918: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_918: 
    mov rdi, [rsp]
    mov rsi, 1742
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_919
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_919
.Lruntime_list_append_int_aligned_919: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_919: 
    mov rdi, [rsp]
    mov rsi, 1744
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_920
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_920
.Lruntime_list_append_int_aligned_920: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_920: 
    mov rdi, [rsp]
    mov rsi, 1746
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_921
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_921
.Lruntime_list_append_int_aligned_921: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_921: 
    mov rdi, [rsp]
    mov rsi, 1748
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_922
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_922
.Lruntime_list_append_int_aligned_922: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_922: 
    mov rdi, [rsp]
    mov rsi, 1750
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_923
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_923
.Lruntime_list_append_int_aligned_923: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_923: 
    mov rdi, [rsp]
    mov rsi, 1752
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_924
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_924
.Lruntime_list_append_int_aligned_924: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_924: 
    mov rdi, [rsp]
    mov rsi, 1754
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_925
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_925
.Lruntime_list_append_int_aligned_925: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_925: 
    mov rdi, [rsp]
    mov rsi, 1756
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_926
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_926
.Lruntime_list_append_int_aligned_926: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_926: 
    mov rdi, [rsp]
    mov rsi, 1758
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_927
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_927
.Lruntime_list_append_int_aligned_927: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_927: 
    mov rdi, [rsp]
    mov rsi, 1760
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_928
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_928
.Lruntime_list_append_int_aligned_928: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_928: 
    mov rdi, [rsp]
    mov rsi, 1762
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_929
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_929
.Lruntime_list_append_int_aligned_929: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_929: 
    mov rdi, [rsp]
    mov rsi, 1764
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_930
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_930
.Lruntime_list_append_int_aligned_930: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_930: 
    mov rdi, [rsp]
    mov rsi, 1766
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_931
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_931
.Lruntime_list_append_int_aligned_931: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_931: 
    mov rdi, [rsp]
    mov rsi, 1768
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_932
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_932
.Lruntime_list_append_int_aligned_932: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_932: 
    mov rdi, [rsp]
    mov rsi, 1770
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_933
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_933
.Lruntime_list_append_int_aligned_933: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_933: 
    mov rdi, [rsp]
    mov rsi, 1772
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_934
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_934
.Lruntime_list_append_int_aligned_934: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_934: 
    mov rdi, [rsp]
    mov rsi, 1774
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_935
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_935
.Lruntime_list_append_int_aligned_935: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_935: 
    mov rdi, [rsp]
    mov rsi, 1776
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_936
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_936
.Lruntime_list_append_int_aligned_936: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_936: 
    mov rdi, [rsp]
    mov rsi, 1778
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_937
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_937
.Lruntime_list_append_int_aligned_937: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_937: 
    mov rdi, [rsp]
    mov rsi, 1780
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_938
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_938
.Lruntime_list_append_int_aligned_938: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_938: 
    mov rdi, [rsp]
    mov rsi, 1782
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_939
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_939
.Lruntime_list_append_int_aligned_939: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_939: 
    mov rdi, [rsp]
    mov rsi, 1784
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_940
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_940
.Lruntime_list_append_int_aligned_940: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_940: 
    mov rdi, [rsp]
    mov rsi, 1786
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_941
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_941
.Lruntime_list_append_int_aligned_941: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_941: 
    mov rdi, [rsp]
    mov rsi, 1788
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_942
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_942
.Lruntime_list_append_int_aligned_942: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_942: 
    mov rdi, [rsp]
    mov rsi, 1790
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_943
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_943
.Lruntime_list_append_int_aligned_943: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_943: 
    mov rdi, [rsp]
    mov rsi, 1792
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_944
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_944
.Lruntime_list_append_int_aligned_944: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_944: 
    mov rdi, [rsp]
    mov rsi, 1794
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_945
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_945
.Lruntime_list_append_int_aligned_945: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_945: 
    mov rdi, [rsp]
    mov rsi, 1796
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_946
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_946
.Lruntime_list_append_int_aligned_946: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_946: 
    mov rdi, [rsp]
    mov rsi, 1798
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_947
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_947
.Lruntime_list_append_int_aligned_947: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_947: 
    mov rdi, [rsp]
    mov rsi, 1800
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_948
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_948
.Lruntime_list_append_int_aligned_948: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_948: 
    mov rdi, [rsp]
    mov rsi, 1802
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_949
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_949
.Lruntime_list_append_int_aligned_949: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_949: 
    mov rdi, [rsp]
    mov rsi, 1804
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_950
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_950
.Lruntime_list_append_int_aligned_950: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_950: 
    mov rdi, [rsp]
    mov rsi, 1806
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_951
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_951
.Lruntime_list_append_int_aligned_951: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_951: 
    mov rdi, [rsp]
    mov rsi, 1808
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_952
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_952
.Lruntime_list_append_int_aligned_952: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_952: 
    mov rdi, [rsp]
    mov rsi, 1810
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_953
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_953
.Lruntime_list_append_int_aligned_953: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_953: 
    mov rdi, [rsp]
    mov rsi, 1812
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_954
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_954
.Lruntime_list_append_int_aligned_954: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_954: 
    mov rdi, [rsp]
    mov rsi, 1814
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_955
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_955
.Lruntime_list_append_int_aligned_955: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_955: 
    mov rdi, [rsp]
    mov rsi, 1816
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_956
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_956
.Lruntime_list_append_int_aligned_956: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_956: 
    mov rdi, [rsp]
    mov rsi, 1818
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_957
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_957
.Lruntime_list_append_int_aligned_957: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_957: 
    mov rdi, [rsp]
    mov rsi, 1820
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_958
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_958
.Lruntime_list_append_int_aligned_958: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_958: 
    mov rdi, [rsp]
    mov rsi, 1822
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_959
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_959
.Lruntime_list_append_int_aligned_959: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_959: 
    mov rdi, [rsp]
    mov rsi, 1824
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_960
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_960
.Lruntime_list_append_int_aligned_960: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_960: 
    mov rdi, [rsp]
    mov rsi, 1826
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_961
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_961
.Lruntime_list_append_int_aligned_961: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_961: 
    mov rdi, [rsp]
    mov rsi, 1828
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_962
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_962
.Lruntime_list_append_int_aligned_962: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_962: 
    mov rdi, [rsp]
    mov rsi, 1830
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_963
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_963
.Lruntime_list_append_int_aligned_963: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_963: 
    mov rdi, [rsp]
    mov rsi, 1832
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_964
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_964
.Lruntime_list_append_int_aligned_964: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_964: 
    mov rdi, [rsp]
    mov rsi, 1834
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_965
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_965
.Lruntime_list_append_int_aligned_965: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_965: 
    mov rdi, [rsp]
    mov rsi, 1836
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_966
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_966
.Lruntime_list_append_int_aligned_966: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_966: 
    mov rdi, [rsp]
    mov rsi, 1838
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_967
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_967
.Lruntime_list_append_int_aligned_967: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_967: 
    mov rdi, [rsp]
    mov rsi, 1840
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_968
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_968
.Lruntime_list_append_int_aligned_968: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_968: 
    mov rdi, [rsp]
    mov rsi, 1842
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_969
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_969
.Lruntime_list_append_int_aligned_969: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_969: 
    mov rdi, [rsp]
    mov rsi, 1844
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_970
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_970
.Lruntime_list_append_int_aligned_970: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_970: 
    mov rdi, [rsp]
    mov rsi, 1846
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_971
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_971
.Lruntime_list_append_int_aligned_971: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_971: 
    mov rdi, [rsp]
    mov rsi, 1848
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_972
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_972
.Lruntime_list_append_int_aligned_972: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_972: 
    mov rdi, [rsp]
    mov rsi, 1850
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_973
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_973
.Lruntime_list_append_int_aligned_973: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_973: 
    mov rdi, [rsp]
    mov rsi, 1852
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_974
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_974
.Lruntime_list_append_int_aligned_974: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_974: 
    mov rdi, [rsp]
    mov rsi, 1854
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_975
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_975
.Lruntime_list_append_int_aligned_975: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_975: 
    mov rdi, [rsp]
    mov rsi, 1856
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_976
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_976
.Lruntime_list_append_int_aligned_976: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_976: 
    mov rdi, [rsp]
    mov rsi, 1858
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_977
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_977
.Lruntime_list_append_int_aligned_977: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_977: 
    mov rdi, [rsp]
    mov rsi, 1860
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_978
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_978
.Lruntime_list_append_int_aligned_978: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_978: 
    mov rdi, [rsp]
    mov rsi, 1862
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_979
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_979
.Lruntime_list_append_int_aligned_979: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_979: 
    mov rdi, [rsp]
    mov rsi, 1864
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_980
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_980
.Lruntime_list_append_int_aligned_980: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_980: 
    mov rdi, [rsp]
    mov rsi, 1866
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_981
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_981
.Lruntime_list_append_int_aligned_981: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_981: 
    mov rdi, [rsp]
    mov rsi, 1868
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_982
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_982
.Lruntime_list_append_int_aligned_982: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_982: 
    mov rdi, [rsp]
    mov rsi, 1870
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_983
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_983
.Lruntime_list_append_int_aligned_983: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_983: 
    mov rdi, [rsp]
    mov rsi, 1872
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_984
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_984
.Lruntime_list_append_int_aligned_984: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_984: 
    mov rdi, [rsp]
    mov rsi, 1874
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_985
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_985
.Lruntime_list_append_int_aligned_985: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_985: 
    mov rdi, [rsp]
    mov rsi, 1876
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_986
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_986
.Lruntime_list_append_int_aligned_986: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_986: 
    mov rdi, [rsp]
    mov rsi, 1878
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_987
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_987
.Lruntime_list_append_int_aligned_987: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_987: 
    mov rdi, [rsp]
    mov rsi, 1880
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_988
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_988
.Lruntime_list_append_int_aligned_988: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_988: 
    mov rdi, [rsp]
    mov rsi, 1882
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_989
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_989
.Lruntime_list_append_int_aligned_989: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_989: 
    mov rdi, [rsp]
    mov rsi, 1884
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_990
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_990
.Lruntime_list_append_int_aligned_990: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_990: 
    mov rdi, [rsp]
    mov rsi, 1886
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_991
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_991
.Lruntime_list_append_int_aligned_991: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_991: 
    mov rdi, [rsp]
    mov rsi, 1888
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_992
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_992
.Lruntime_list_append_int_aligned_992: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_992: 
    mov rdi, [rsp]
    mov rsi, 1890
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_993
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_993
.Lruntime_list_append_int_aligned_993: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_993: 
    mov rdi, [rsp]
    mov rsi, 1892
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_994
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_994
.Lruntime_list_append_int_aligned_994: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_994: 
    mov rdi, [rsp]
    mov rsi, 1894
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_995
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_995
.Lruntime_list_append_int_aligned_995: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_995: 
    mov rdi, [rsp]
    mov rsi, 1896
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_996
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_996
.Lruntime_list_append_int_aligned_996: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_996: 
    mov rdi, [rsp]
    mov rsi, 1898
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_997
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_997
.Lruntime_list_append_int_aligned_997: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_997: 
    mov rdi, [rsp]
    mov rsi, 1900
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_998
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_998
.Lruntime_list_append_int_aligned_998: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_998: 
    mov rdi, [rsp]
    mov rsi, 1902
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_999
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_999
.Lruntime_list_append_int_aligned_999: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_999: 
    mov rdi, [rsp]
    mov rsi, 1904
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1000
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1000
.Lruntime_list_append_int_aligned_1000: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1000: 
    mov rdi, [rsp]
    mov rsi, 1906
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1001
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1001
.Lruntime_list_append_int_aligned_1001: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1001: 
    mov rdi, [rsp]
    mov rsi, 1908
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1002
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1002
.Lruntime_list_append_int_aligned_1002: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1002: 
    mov rdi, [rsp]
    mov rsi, 1910
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1003
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1003
.Lruntime_list_append_int_aligned_1003: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1003: 
    mov rdi, [rsp]
    mov rsi, 1912
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1004
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1004
.Lruntime_list_append_int_aligned_1004: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1004: 
    mov rdi, [rsp]
    mov rsi, 1914
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1005
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1005
.Lruntime_list_append_int_aligned_1005: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1005: 
    mov rdi, [rsp]
    mov rsi, 1916
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1006
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1006
.Lruntime_list_append_int_aligned_1006: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1006: 
    mov rdi, [rsp]
    mov rsi, 1918
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1007
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1007
.Lruntime_list_append_int_aligned_1007: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1007: 
    mov rdi, [rsp]
    mov rsi, 1920
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1008
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1008
.Lruntime_list_append_int_aligned_1008: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1008: 
    mov rdi, [rsp]
    mov rsi, 1922
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1009
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1009
.Lruntime_list_append_int_aligned_1009: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1009: 
    mov rdi, [rsp]
    mov rsi, 1924
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1010
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1010
.Lruntime_list_append_int_aligned_1010: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1010: 
    mov rdi, [rsp]
    mov rsi, 1926
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1011
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1011
.Lruntime_list_append_int_aligned_1011: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1011: 
    mov rdi, [rsp]
    mov rsi, 1928
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1012
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1012
.Lruntime_list_append_int_aligned_1012: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1012: 
    mov rdi, [rsp]
    mov rsi, 1930
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1013
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1013
.Lruntime_list_append_int_aligned_1013: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1013: 
    mov rdi, [rsp]
    mov rsi, 1932
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1014
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1014
.Lruntime_list_append_int_aligned_1014: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1014: 
    mov rdi, [rsp]
    mov rsi, 1934
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1015
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1015
.Lruntime_list_append_int_aligned_1015: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1015: 
    mov rdi, [rsp]
    mov rsi, 1936
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1016
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1016
.Lruntime_list_append_int_aligned_1016: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1016: 
    mov rdi, [rsp]
    mov rsi, 1938
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1017
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1017
.Lruntime_list_append_int_aligned_1017: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1017: 
    mov rdi, [rsp]
    mov rsi, 1940
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1018
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1018
.Lruntime_list_append_int_aligned_1018: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1018: 
    mov rdi, [rsp]
    mov rsi, 1942
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1019
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1019
.Lruntime_list_append_int_aligned_1019: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1019: 
    mov rdi, [rsp]
    mov rsi, 1944
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1020
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1020
.Lruntime_list_append_int_aligned_1020: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1020: 
    mov rdi, [rsp]
    mov rsi, 1946
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1021
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1021
.Lruntime_list_append_int_aligned_1021: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1021: 
    mov rdi, [rsp]
    mov rsi, 1948
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1022
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1022
.Lruntime_list_append_int_aligned_1022: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1022: 
    mov rdi, [rsp]
    mov rsi, 1950
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1023
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1023
.Lruntime_list_append_int_aligned_1023: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1023: 
    mov rdi, [rsp]
    mov rsi, 1952
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1024
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1024
.Lruntime_list_append_int_aligned_1024: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1024: 
    mov rdi, [rsp]
    mov rsi, 1954
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1025
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1025
.Lruntime_list_append_int_aligned_1025: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1025: 
    mov rdi, [rsp]
    mov rsi, 1956
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1026
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1026
.Lruntime_list_append_int_aligned_1026: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1026: 
    mov rdi, [rsp]
    mov rsi, 1958
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1027
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1027
.Lruntime_list_append_int_aligned_1027: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1027: 
    mov rdi, [rsp]
    mov rsi, 1960
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1028
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1028
.Lruntime_list_append_int_aligned_1028: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1028: 
    mov rdi, [rsp]
    mov rsi, 1962
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1029
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1029
.Lruntime_list_append_int_aligned_1029: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1029: 
    mov rdi, [rsp]
    mov rsi, 1964
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1030
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1030
.Lruntime_list_append_int_aligned_1030: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1030: 
    mov rdi, [rsp]
    mov rsi, 1966
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1031
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1031
.Lruntime_list_append_int_aligned_1031: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1031: 
    mov rdi, [rsp]
    mov rsi, 1968
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1032
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1032
.Lruntime_list_append_int_aligned_1032: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1032: 
    mov rdi, [rsp]
    mov rsi, 1970
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1033
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1033
.Lruntime_list_append_int_aligned_1033: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1033: 
    mov rdi, [rsp]
    mov rsi, 1972
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1034
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1034
.Lruntime_list_append_int_aligned_1034: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1034: 
    mov rdi, [rsp]
    mov rsi, 1974
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1035
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1035
.Lruntime_list_append_int_aligned_1035: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1035: 
    mov rdi, [rsp]
    mov rsi, 1976
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1036
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1036
.Lruntime_list_append_int_aligned_1036: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1036: 
    mov rdi, [rsp]
    mov rsi, 1978
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1037
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1037
.Lruntime_list_append_int_aligned_1037: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1037: 
    mov rdi, [rsp]
    mov rsi, 1980
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1038
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1038
.Lruntime_list_append_int_aligned_1038: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1038: 
    mov rdi, [rsp]
    mov rsi, 1982
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1039
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1039
.Lruntime_list_append_int_aligned_1039: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1039: 
    mov rdi, [rsp]
    mov rsi, 1984
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1040
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1040
.Lruntime_list_append_int_aligned_1040: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1040: 
    mov rdi, [rsp]
    mov rsi, 1986
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1041
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1041
.Lruntime_list_append_int_aligned_1041: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1041: 
    mov rdi, [rsp]
    mov rsi, 1988
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1042
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1042
.Lruntime_list_append_int_aligned_1042: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1042: 
    mov rdi, [rsp]
    mov rsi, 1990
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1043
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1043
.Lruntime_list_append_int_aligned_1043: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1043: 
    mov rdi, [rsp]
    mov rsi, 1992
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1044
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1044
.Lruntime_list_append_int_aligned_1044: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1044: 
    mov rdi, [rsp]
    mov rsi, 1994
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1045
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1045
.Lruntime_list_append_int_aligned_1045: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1045: 
    mov rdi, [rsp]
    mov rsi, 1996
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1046
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1046
.Lruntime_list_append_int_aligned_1046: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1046: 
    mov rdi, [rsp]
    mov rsi, 1998
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1047
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1047
.Lruntime_list_append_int_aligned_1047: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1047: 
    # STORE 19
    pop qword ptr [rbp - 160]  # Direct pop to memory
    # STORE_CONST_I64 8 0 21 0
    mov qword ptr [rbp - 72], 0  # Immediate store
    mov qword ptr [rbp - 176], 0  # Immediate store
    # LABEL for_start17
.align 16  # Loop alignment
.Lmain_for_start17:
    # LOAD 21
    mov rax, [rbp - 176]
    push rax
    # CMP_LT_CONST 1000
    pop rax
    cmp rax, 1000
    jge .Lmain_for_end19  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 8 19
    mov rax, [rbp - 72]
    push rax
    mov rax, [rbp - 160]
    push rax
    # CALL sum_list 1
    pop rdi
    call sum_list
    mov rbx, rax  # Optimized result transfer
    pop rax
    add rax, rbx
    # STORE 8
    mov qword ptr [rbp - 72], rax  # Eliminated push/pop
    # INC_LOCAL 21
    inc qword ptr [rbp - 176]
    # JUMP for_start17
    jmp .Lmain_for_start17
    # LABEL for_end19
.Lmain_for_end19:
    # CONST_STR "List sum total: "
    lea rax, [.STR13]
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1048
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1048
.Lruntime_int_to_str_aligned_1048: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1048: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1049
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1049
.Lruntime_str_concat_checked_aligned_1049: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1049: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1050
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1050
.Lruntime_println_str_aligned_1050: 
    call runtime_println_str
.Lruntime_println_str_done_1050: 
    # LOAD 19
    mov rax, [rbp - 160]
    push rax
    # CALL filter_even 1
    pop rdi
    call filter_even
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # CALL sum_list 1
    pop rdi
    call sum_list
    # Removed redundant push rax; pop rax
    mov [rbp - 56], rax
    mov [rbp - 56], rax
    # CONST_STR "Filtered sum: "
    lea rax, [.STR14]
    push rax
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_to_str_aligned_1051
    sub rsp, 8
    call runtime_list_to_str
    add rsp, 8
    jmp .Lruntime_list_to_str_done_1051
.Lruntime_list_to_str_aligned_1051: 
    call runtime_list_to_str
.Lruntime_list_to_str_done_1051: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1052
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1052
.Lruntime_str_concat_checked_aligned_1052: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1052: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1053
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1053
.Lruntime_println_str_aligned_1053: 
    call runtime_println_str
.Lruntime_println_str_done_1053: 
    # LIST_NEW_I64 10 0 2 4 6 8 10 12 14 16 18
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_new_aligned_1054
    sub rsp, 8
    call runtime_list_new
    add rsp, 8
    jmp .Lruntime_list_new_done_1054
.Lruntime_list_new_aligned_1054: 
    call runtime_list_new
.Lruntime_list_new_done_1054: 
    mov dword ptr [rax + 24], 0  # elem_type = 0 (int)
    push rax
    mov rdi, [rsp]
    mov rsi, 0
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1055
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1055
.Lruntime_list_append_int_aligned_1055: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1055: 
    mov rdi, [rsp]
    mov rsi, 2
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1056
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1056
.Lruntime_list_append_int_aligned_1056: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1056: 
    mov rdi, [rsp]
    mov rsi, 4
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1057
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1057
.Lruntime_list_append_int_aligned_1057: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1057: 
    mov rdi, [rsp]
    mov rsi, 6
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1058
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1058
.Lruntime_list_append_int_aligned_1058: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1058: 
    mov rdi, [rsp]
    mov rsi, 8
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1059
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1059
.Lruntime_list_append_int_aligned_1059: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1059: 
    mov rdi, [rsp]
    mov rsi, 10
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1060
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1060
.Lruntime_list_append_int_aligned_1060: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1060: 
    mov rdi, [rsp]
    mov rsi, 12
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1061
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1061
.Lruntime_list_append_int_aligned_1061: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1061: 
    mov rdi, [rsp]
    mov rsi, 14
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1062
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1062
.Lruntime_list_append_int_aligned_1062: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1062: 
    mov rdi, [rsp]
    mov rsi, 16
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1063
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1063
.Lruntime_list_append_int_aligned_1063: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1063: 
    mov rdi, [rsp]
    mov rsi, 18
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_1064
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1064
.Lruntime_list_append_int_aligned_1064: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1064: 
    # DUP 
    mov rax, [rsp]
    # STORE 17
    mov qword ptr [rbp - 144], rax  # Eliminated push/pop
    # CALL reverse_list 1
    pop rdi
    call reverse_list
    # Removed redundant push rax; pop rax
    mov [rbp - 128], rax
    mov [rbp - 128], rax
    # CONST_STR "Reversed list max: "
    lea rax, [.STR15]
    push rax
    # LOAD 15
    mov rax, [rbp - 128]
    push rax
    # CALL list_max 1
    pop rdi
    call list_max
    mov rdi, rax  # Optimized result transfer
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_to_str_aligned_1065
    sub rsp, 8
    call runtime_list_to_str
    add rsp, 8
    jmp .Lruntime_list_to_str_done_1065
.Lruntime_list_to_str_aligned_1065: 
    call runtime_list_to_str
.Lruntime_list_to_str_done_1065: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1066
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1066
.Lruntime_str_concat_checked_aligned_1066: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1066: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1067
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1067
.Lruntime_println_str_aligned_1067: 
    call runtime_println_str
.Lruntime_println_str_done_1067: 
    # LOAD 17 15
    mov rax, [rbp - 144]
    push rax
    mov rax, [rbp - 128]
    push rax
    # CALL merge_lists 2
    pop rsi
    pop rdi
    call merge_lists
    # Removed redundant push rax; pop rax
    mov [rbp - 88], rax
    mov [rbp - 88], rax
    # CONST_STR "Merged list length: "
    lea rax, [.STR16]
    push rax
    # LOAD 10
    mov rax, [rbp - 88]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_1068
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_1068
.Lruntime_list_len_aligned_1068: 
    call runtime_list_len
.Lruntime_list_len_done_1068: 
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1069
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1069
.Lruntime_int_to_str_aligned_1069: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1069: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1070
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1070
.Lruntime_str_concat_checked_aligned_1070: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1070: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1071
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1071
.Lruntime_println_str_aligned_1071: 
    call runtime_println_str
.Lruntime_println_str_done_1071: 
    # CONST_STR ""
    lea rax, [.STR2]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1072
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1072
.Lruntime_println_str_aligned_1072: 
    call runtime_println_str
.Lruntime_println_str_done_1072: 
    # CONST_STR "Running string benchmarks..."
    lea rax, [.STR17]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1073
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1073
.Lruntime_println_str_aligned_1073: 
    call runtime_println_str
.Lruntime_println_str_done_1073: 
    # CONST_STR "test"
    lea rax, [.STR18]
    push rax
    # CONST_I64 100
    mov rax, 100
    push rax
    # CALL string_repeat 2
    pop rsi
    pop rdi
    call string_repeat
    # Removed redundant push rax; pop rax
    mov [rbp - 120], rax
    mov [rbp - 120], rax
    # CONST_STR "Repeated string length: "
    lea rax, [.STR19]
    push rax
    # LOAD 14
    mov rax, [rbp - 120]
    push rax
    # BUILTIN_LEN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_len_aligned_1074
    sub rsp, 8
    call runtime_list_len
    add rsp, 8
    jmp .Lruntime_list_len_done_1074
.Lruntime_list_len_aligned_1074: 
    call runtime_list_len
.Lruntime_list_len_done_1074: 
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1075
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1075
.Lruntime_int_to_str_aligned_1075: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1075: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1076
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1076
.Lruntime_str_concat_checked_aligned_1076: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1076: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1077
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1077
.Lruntime_println_str_aligned_1077: 
    call runtime_println_str
.Lruntime_println_str_done_1077: 
    # CONST_STR "the quick brown fox jumps over the lazy dog"
    lea rax, [.STR20]
    push rax
    # DUP 
    mov rax, [rsp]
    # STORE 16
    mov qword ptr [rbp - 136], rax  # Eliminated push/pop
    # CONST_STR "o"
    lea rax, [.STR21]
    push rax
    # CALL count_char 2
    pop rsi
    pop rdi
    call count_char
    # Removed redundant push rax; pop rax
    mov [rbp - 16], rax
    mov [rbp - 16], rax
    # CONST_STR "Character count: "
    lea rax, [.STR22]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # BUILTIN_STR 
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1078
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1078
.Lruntime_str_concat_checked_aligned_1078: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1078: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1079
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1079
.Lruntime_println_str_aligned_1079: 
    call runtime_println_str
.Lruntime_println_str_done_1079: 
    # CONST_STR ""
    lea rax, [.STR2]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1080
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1080
.Lruntime_println_str_aligned_1080: 
    call runtime_println_str
.Lruntime_println_str_done_1080: 
    # CONST_STR "Running control flow benchmarks..."
    lea rax, [.STR23]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1081
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1081
.Lruntime_println_str_aligned_1081: 
    call runtime_println_str
.Lruntime_println_str_done_1081: 
    # STORE_CONST_I64 11 512
    mov qword ptr [rbp - 96], 512  # Immediate store
    # CONST_STR "Nested loops: "
    lea rax, [.STR24]
    push rax
    # LOAD 11
    mov rax, [rbp - 96]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1082
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1082
.Lruntime_int_to_str_aligned_1082: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1082: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1083
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1083
.Lruntime_str_concat_checked_aligned_1083: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1083: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1084
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1084
.Lruntime_println_str_aligned_1084: 
    call runtime_println_str
.Lruntime_println_str_done_1084: 
    # STORE_CONST_I64 18 5500000
    mov qword ptr [rbp - 152], 5500000  # Immediate store
    # CONST_STR "Switch sum: "
    lea rax, [.STR25]
    push rax
    # LOAD 18
    mov rax, [rbp - 152]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1085
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1085
.Lruntime_int_to_str_aligned_1085: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1085: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1086
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1086
.Lruntime_str_concat_checked_aligned_1086: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1086: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1087
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1087
.Lruntime_println_str_aligned_1087: 
    call runtime_println_str
.Lruntime_println_str_done_1087: 
    # STORE_CONST_I64 20 50000
    mov qword ptr [rbp - 168], 50000  # Immediate store
    # CONST_STR "While count: "
    lea rax, [.STR26]
    push rax
    # LOAD 20
    mov rax, [rbp - 168]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1088
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1088
.Lruntime_int_to_str_aligned_1088: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1088: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1089
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1089
.Lruntime_str_concat_checked_aligned_1089: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1089: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1090
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1090
.Lruntime_println_str_aligned_1090: 
    call runtime_println_str
.Lruntime_println_str_done_1090: 
    # STORE_CONST_I64 9 1500625
    mov qword ptr [rbp - 80], 1500625  # Immediate store
    # CONST_STR "Matrix sum: "
    lea rax, [.STR27]
    push rax
    # LOAD 9
    mov rax, [rbp - 80]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1091
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1091
.Lruntime_int_to_str_aligned_1091: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1091: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1092
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1092
.Lruntime_str_concat_checked_aligned_1092: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1092: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1093
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1093
.Lruntime_println_str_aligned_1093: 
    call runtime_println_str
.Lruntime_println_str_done_1093: 
    # STORE_CONST_I64 2 7953
    mov qword ptr [rbp - 24], 7953  # Immediate store
    # CONST_STR "Complex conditions: "
    lea rax, [.STR28]
    push rax
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1094
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1094
.Lruntime_int_to_str_aligned_1094: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1094: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1095
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1095
.Lruntime_str_concat_checked_aligned_1095: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1095: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1096
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1096
.Lruntime_println_str_aligned_1096: 
    call runtime_println_str
.Lruntime_println_str_done_1096: 
    # STORE_CONST_I64 0 11250000
    mov qword ptr [rbp - 8], 11250000  # Immediate store
    # CONST_STR "Break/Continue sum: "
    lea rax, [.STR29]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # BUILTIN_STR 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_int_to_str_aligned_1097
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_1097
.Lruntime_int_to_str_aligned_1097: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_1097: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1098
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1098
.Lruntime_str_concat_checked_aligned_1098: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1098: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1099
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1099
.Lruntime_println_str_aligned_1099: 
    call runtime_println_str
.Lruntime_println_str_done_1099: 
    # CONST_STR ""
    lea rax, [.STR2]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1100
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1100
.Lruntime_println_str_aligned_1100: 
    call runtime_println_str
.Lruntime_println_str_done_1100: 
    # CONST_STR "=== Benchmark Complete ==="
    lea rax, [.STR30]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_1101
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_1101
.Lruntime_println_str_aligned_1101: 
    call runtime_println_str
.Lruntime_println_str_done_1101: 
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .entry main

.section .rodata
.FLOAT0:
    .double 1.0
.FLOAT1:
    .double 1.0
.STR2:
    .asciz ""
.STR3:
    .asciz "=== Starting Comprehensive Benchmark ==="
.STR4:
    .asciz "Running math benchmarks..."
.STR5:
    .asciz "Fibonacci sum: "
.STR6:
    .asciz "Factorial sum: "
.FLOAT7:
    .double 0.0
.FLOAT8:
    .double 5.7
.STR9:
    .asciz "Power sum: "
.STR10:
    .asciz "GCD sum: "
.STR11:
    .asciz "Prime checks: "
.STR12:
    .asciz "Running list benchmarks..."
.STR13:
    .asciz "List sum total: "
.STR14:
    .asciz "Filtered sum: "
.STR15:
    .asciz "Reversed list max: "
.STR16:
    .asciz "Merged list length: "
.STR17:
    .asciz "Running string benchmarks..."
.STR18:
    .asciz "test"
.STR19:
    .asciz "Repeated string length: "
.STR20:
    .asciz "the quick brown fox jumps over the lazy dog"
.STR21:
    .asciz "o"
.STR22:
    .asciz "Character count: "
.STR23:
    .asciz "Running control flow benchmarks..."
.STR24:
    .asciz "Nested loops: "
.STR25:
    .asciz "Switch sum: "
.STR26:
    .asciz "While count: "
.STR27:
    .asciz "Matrix sum: "
.STR28:
    .asciz "Complex conditions: "
.STR29:
    .asciz "Break/Continue sum: "
.STR30:
    .asciz "=== Benchmark Complete ==="

.section .bss
global_vars:
    .space 16  # Optimized (was 2048, max offset 0)
.align 16  # Function alignment
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
.align 16  # Function alignment
struct_data:
    .space 65536  # Space for struct instances (256 instances * 256 bytes each)
