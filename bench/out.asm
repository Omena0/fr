.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .func pi_spigot str 1

.align 16  # Function alignment
pi_spigot:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg n_digits i64
    mov rax, [rbp + 16]
    mov [rbp - 8], rax




    mov [rbp - 8], rax
    # .local a i64
    # .local n i64
    # .local nines i64
    # .local predigit i64
    # .local result str
    # .line 4 "list a = []"
    # LIST_NEW 
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
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
    # .line 5 "int n = int((10 * n_digits) / 3 + 1)"
    # CONST_I64 10
    # LOAD 0
    mov rax, [rbp - 8]
    imul rax, 10  # Optimized multiply
    push rax
    # DIV_CONST_I64 3
    pop rax
    cqo
    mov rbx, 3
    idiv rbx
    push rax
    # ADD_CONST_I64 1
    pop rax
    add rax, 1
    # TO_INT 
    # STORE 2
    mov qword ptr [rbp - 24], rax  # Eliminated push/pop
    # .line 6 "for (i, n) {"
    # STORE_CONST_I64 6 0
    mov qword ptr [rbp - 56], 0  # Immediate store
    # LABEL for_start0
.align 16  # Loop alignment
.Lpi_spigot_for_start0:
    # LOAD2_CMP_LT 6 2
    mov rax, [rbp - 56]
    cmp rax, [rbp - 24]
    jge .Lpi_spigot_for_end2  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CONST_I64 2
    mov rax, 2
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    mov [rip + list_append_scratch], rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_list_append_int_aligned_1
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_1
.Lruntime_list_append_int_aligned_1: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_1: 
    mov rax, [rip + list_append_scratch]
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # INC_LOCAL 6
    inc qword ptr [rbp - 56]
    # JUMP for_start0
    jmp .Lpi_spigot_for_start0
    # LABEL for_end2
.Lpi_spigot_for_end2:
    # .line 10 "str result = \"\""
    # CONST_STR ""
    lea rax, [.STR0]
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # .line 11 "int nines = 0"
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # .line 12 "int predigit = 1"
    # STORE_CONST_I64 4 1
    mov qword ptr [rbp - 40], 1  # Immediate store
    # .line 14 "for (i, n_digits) {"
    # STORE_CONST_I64 6 0
    mov qword ptr [rbp - 56], 0  # Immediate store
    # LABEL for_start3
.align 16  # Loop alignment
.Lpi_spigot_for_start3:
    # LOAD2_CMP_LT 6 0
    mov rax, [rbp - 56]
    cmp rax, [rbp - 8]
    jge .Lpi_spigot_for_end5  # Optimized: removed setcc+movzx+push+pop+test
    # .line 15 "int carry = 0"
    # STORE_CONST_I64 7 0
    mov qword ptr [rbp - 64], 0  # Immediate store
    # .line 16 "int k = n - 1"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # SUB_CONST_I64 1
    pop rax
    sub rax, 1
    # STORE 8
    mov qword ptr [rbp - 72], rax  # Eliminated push/pop
    # .line 19 "while (k >= 1) {"
    # LABEL while_start6
.align 16  # Loop alignment
.Lpi_spigot_while_start6:
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CMP_GE_CONST 1
    pop rax
    cmp rax, 1
    jl .Lpi_spigot_while_end7  # Optimized: removed setcc+movzx+push+pop+test
    # .line 20 "int x = a[k] * 10 + carry * k"
    # LOAD 1 8
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 72]
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_get_slow_2  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_get_slow_2  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov rax, [rax + rsi*8]  # rax = items[index]
    jmp .Llist_get_done_2
    .Llist_get_slow_2:
    mov rdx, 20  # line number
    call runtime_list_get_int_at
    .Llist_get_done_2:
    push rax
    # MUL_CONST_I64 10
    pop rax
    imul rax, 10
    push rax
    # LOAD2_MUL_I64 7 8
    mov rax, [rbp - 64]
    imul rax, [rbp - 72]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    # STORE 9
    mov qword ptr [rbp - 80], rax  # Eliminated push/pop
    # .line 21 "int denom = 2 * k - 1"
    # CONST_I64 2
    # LOAD 8
    mov rax, [rbp - 72]
    add rax, rax  # Optimized multiply by 2
    push rax
    # SUB_CONST_I64 1
    pop rax
    sub rax, 1
    # STORE 10
    mov qword ptr [rbp - 88], rax  # Eliminated push/pop
    # .line 22 "a[k] = x % denom"
    # LOAD 1 8 9 10
    mov rax, [rbp - 16]
    push rax
    mov rax, [rbp - 72]
    push rax
    mov rax, [rbp - 80]
    push rax
    mov rax, [rbp - 88]
    push rax
    # MOD_I64 
    pop rbx
    pop rax
    push rax  # save dividend
    mov rdi, rbx
    mov rsi, 22  # line number
    call runtime_check_div_zero_i64_at
    pop rax  # restore dividend
    cqo
    idiv rbx
    push rdx
    # LIST_SET 
    pop r8
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_set_slow_3  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_set_slow_3  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov [rax + rsi*8], r8  # items[index] = value
    mov rax, rdi  # return list pointer
    jmp .Llist_set_done_3
    .Llist_set_slow_3:
    mov [rip + list_append_scratch], rdi
    mov rdx, r8  # value
    mov rcx, 22  # line number
    call runtime_list_set_int_at
    mov rax, [rip + list_append_scratch]
    .Llist_set_done_3:
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # .line 23 "carry = x / denom"
    # LOAD2_DIV_I64 9 10
    mov rbx, [rbp - 88]  # divisor
    mov rax, [rbp - 80]  # dividend
    push rax  # save dividend
    push rbx  # save divisor
    mov rdi, rbx  # divisor for check
    mov rsi, 23  # line number
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_check_div_zero_i64_at_aligned_4
    sub rsp, 8
    call runtime_check_div_zero_i64_at
    add rsp, 8
    jmp .Lruntime_check_div_zero_i64_at_done_4
.Lruntime_check_div_zero_i64_at_aligned_4: 
    call runtime_check_div_zero_i64_at
.Lruntime_check_div_zero_i64_at_done_4: 
    pop rbx  # restore divisor
    pop rax  # restore dividend
    cqo  # sign-extend rax into rdx:rax
    idiv rbx
    # STORE 7
    mov qword ptr [rbp - 64], rax  # Eliminated push/pop
    # .line 24 "k -= 1"
    # DEC_LOCAL 8
    dec qword ptr [rbp - 72]
    # JUMP while_start6
    jmp .Lpi_spigot_while_start6
    # LABEL while_end7
.Lpi_spigot_while_end7:
    # .line 27 "int x = a[0] * 10 + carry"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_get_slow_5  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_get_slow_5  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov rax, [rax + rsi*8]  # rax = items[index]
    jmp .Llist_get_done_5
    .Llist_get_slow_5:
    mov rdx, 27  # line number
    call runtime_list_get_int_at
    .Llist_get_done_5:
    push rax
    # MUL_CONST_I64 10
    pop rax
    imul rax, 10
    push rax
    # LOAD 7
    mov rax, [rbp - 64]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    # STORE 9
    mov qword ptr [rbp - 80], rax  # Eliminated push/pop
    # .line 28 "int q = int(x / 10)"
    # LOAD 9
    mov rax, [rbp - 80]
    push rax
    # DIV_CONST_I64 10
    pop rax
    cqo
    mov rbx, 10
    idiv rbx
    # TO_INT 
    # STORE 11
    mov qword ptr [rbp - 96], rax  # Eliminated push/pop
    # .line 29 "a[0] = x % 10"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LOAD 9
    mov rax, [rbp - 80]
    push rax
    # MOD_CONST_I64 10
    pop rax
    mov rbx, 10  # Load divisor
    cqo  # Sign-extend rax into rdx:rax
    idiv rbx
    push rdx  # Remainder
    # LIST_SET 
    pop r8
    pop rsi
    pop rdi
    test rsi, rsi
    js .Llist_set_slow_6  # negative index, use slow path
    mov rcx, [rdi + 8]  # list->length
    cmp rsi, rcx
    jge .Llist_set_slow_6  # out of bounds, use slow path
    mov rax, [rdi]  # rax = list->items
    mov [rax + rsi*8], r8  # items[index] = value
    mov rax, rdi  # return list pointer
    jmp .Llist_set_done_6
    .Llist_set_slow_6:
    mov [rip + list_append_scratch], rdi
    mov rdx, r8  # value
    mov rcx, 29  # line number
    call runtime_list_set_int_at
    mov rax, [rip + list_append_scratch]
    .Llist_set_done_6:
    # STORE 1
    mov qword ptr [rbp - 16], rax  # Eliminated push/pop
    # .line 31 "if (i < 2) {"
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # CMP_LT_CONST 2
    pop rax
    cmp rax, 2
    jge .Lpi_spigot_if_end8  # Optimized: removed setcc+movzx+push+pop+test
    # .line 33 "}"
    # JUMP for_continue4
    jmp .Lpi_spigot_for_continue4
    # LABEL if_end8
.Lpi_spigot_if_end8:
    # .line 36 "if (q == 9) {"
    # LOAD 11
    mov rax, [rbp - 96]
    push rax
    # CMP_EQ_CONST 9
    pop rax
    cmp rax, 9
    jne .Lpi_spigot_else11  # Optimized: removed setcc+movzx+push+pop+test
    # .line 37 "nines += 1"
    # INC_LOCAL 3
    inc qword ptr [rbp - 32]
    # JUMP if_end10
    jmp .Lpi_spigot_if_end10
    # LABEL else11
.Lpi_spigot_else11:
    # LOAD 11
    mov rax, [rbp - 96]
    push rax
    # CMP_EQ_CONST 10
    pop rax
    cmp rax, 10
    jne .Lpi_spigot_else12  # Optimized: removed setcc+movzx+push+pop+test
    # .line 40 "result += str(predigit + 1)"
    # LOAD 5 4
    mov rax, [rbp - 48]
    push rax
    mov rax, [rbp - 40]
    push rax
    # CONST_I64 1
    mov rax, 1
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    add rdi, rsi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_int_to_str_aligned_7
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_7
.Lruntime_int_to_str_aligned_7: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_7: 
    push rax
    # BUILTIN_STR 
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_8
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_8
.Lruntime_str_concat_checked_aligned_8: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_8: 
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # .line 41 "for (j, nines) {"
    # STORE_CONST_I64 12 0
    mov qword ptr [rbp - 104], 0  # Immediate store
    # LABEL for_start13
.align 16  # Loop alignment
.Lpi_spigot_for_start13:
    # LOAD2_CMP_LT 12 3
    mov rax, [rbp - 104]
    cmp rax, [rbp - 32]
    jge .Lpi_spigot_for_end15  # Optimized: removed setcc+movzx+push+pop+test
    # .line 42 "result += \"0\""
    # LOAD 5
    mov rax, [rbp - 48]
    push rax
    # CONST_STR "0"
    lea rax, [.STR1]
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_9
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_9
.Lruntime_str_concat_checked_aligned_9: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_9: 
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # INC_LOCAL 12
    inc qword ptr [rbp - 104]
    # JUMP for_start13
    jmp .Lpi_spigot_for_start13
    # LABEL for_end15
.Lpi_spigot_for_end15:
    # .line 44 "predigit = 0"
    # STORE_CONST_I64 4 0
    mov qword ptr [rbp - 40], 0  # Immediate store
    # .line 45 "nines = 0"
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # JUMP if_end10
    jmp .Lpi_spigot_if_end10
    # LABEL else12
.Lpi_spigot_else12:
    # .line 48 "result += str(predigit)"
    # LOAD 5 4
    mov rax, [rbp - 48]
    push rax
    mov rax, [rbp - 40]
    push rax
    # BUILTIN_STR 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_int_to_str_aligned_10
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_10
.Lruntime_int_to_str_aligned_10: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_10: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_11
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_11
.Lruntime_str_concat_checked_aligned_11: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_11: 
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # .line 49 "predigit = q"
    # FUSED_LOAD_STORE 11 4
    mov rax, [rbp - 96]
    mov qword ptr [rbp - 40], rax  # Eliminated push/pop
    # .line 50 "if (nines > 0) {"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CMP_GT_CONST 0
    pop rax
    cmp rax, 0
    jle .Lpi_spigot_if_end16  # Optimized: removed setcc+movzx+push+pop+test
    # .line 51 "for (j, nines) {"
    # STORE_CONST_I64 12 0
    mov qword ptr [rbp - 104], 0  # Immediate store
    # LABEL for_start18
.align 16  # Loop alignment
.Lpi_spigot_for_start18:
    # LOAD2_CMP_LT 12 3
    mov rax, [rbp - 104]
    cmp rax, [rbp - 32]
    jge .Lpi_spigot_for_end20  # Optimized: removed setcc+movzx+push+pop+test
    # .line 52 "result += \"9\""
    # LOAD 5
    mov rax, [rbp - 48]
    push rax
    # CONST_STR "9"
    lea rax, [.STR2]
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_12
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_12
.Lruntime_str_concat_checked_aligned_12: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_12: 
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # INC_LOCAL 12
    inc qword ptr [rbp - 104]
    # JUMP for_start18
    jmp .Lpi_spigot_for_start18
    # LABEL for_end20
.Lpi_spigot_for_end20:
    # .line 54 "nines = 0"
    # STORE_CONST_I64 3 0
    mov qword ptr [rbp - 32], 0  # Immediate store
    # LABEL if_end16
.Lpi_spigot_if_end16:
    # LABEL if_end10
.Lpi_spigot_if_end10:
    # LABEL for_continue4
.Lpi_spigot_for_continue4:
    # INC_LOCAL 6
    inc qword ptr [rbp - 56]
    # JUMP for_start3
    jmp .Lpi_spigot_for_start3
    # LABEL for_end5
.Lpi_spigot_for_end5:
    # .line 60 "result += str(predigit)"
    # LOAD 5 4
    mov rax, [rbp - 48]
    push rax
    mov rax, [rbp - 40]
    push rax
    # BUILTIN_STR 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_int_to_str_aligned_13
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_13
.Lruntime_int_to_str_aligned_13: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_13: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_14
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_14
.Lruntime_str_concat_checked_aligned_14: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_14: 
    # STORE 5
    mov qword ptr [rbp - 48], rax  # Eliminated push/pop
    # .line 63 "return f\"3.{result}\""
    # CONST_STR "3."
    lea rax, [.STR3]
    push rax
    # LOAD 5
    mov rax, [rbp - 48]
    push rax
    # BUILTIN_STR 
    # ADD_STR 
    pop rsi
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_str_concat_checked_aligned_15
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_15
.Lruntime_str_concat_checked_aligned_15: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_15: 
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lpi_spigot_skip_labels:
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
    jz .Lruntime_init_aligned_17
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_17
.Lruntime_init_aligned_17: 
    call runtime_init
.Lruntime_init_done_17: 
    lea rdi, [.STR4]  # filename
    lea rsi, [.STR5]  # source
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_set_source_info_aligned_18
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_18
.Lruntime_set_source_info_aligned_18: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_18: 
    # .local pi str
    # .line 68 "str pi = pi_spigot(10000)"
    # CONST_I64 10000
    mov rax, 10000
    push rax
    # CALL pi_spigot 1
    # CALL pi_spigot: struct_args=set(), float_args=set(), stack_types=['i64']
    call pi_spigot
    # Removed redundant push rax; pop rax
    mov [rbp - 8], rax

    mov [rbp - 8], rax  # Store
    # Removed: mov rax, [rbp - 8]  # Load (rax already contains value)
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    # Simplified alignment check (was 5 instructions)
    test spl, 0xF  # Check stack alignment
    jz .Lruntime_println_str_aligned_16
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_16
.Lruntime_println_str_aligned_16: 
    call runtime_println_str
.Lruntime_println_str_done_16: 
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .entry main

.section .rodata
.STR0:
    .asciz ""
.STR1:
    .asciz "0"
.STR2:
    .asciz "9"
.STR3:
    .asciz "3."
.STR4:
    .asciz "pi_1k.fr"
.STR5:
    .asciz "\n\n\nlist a = []\nint n = int((10 * n_digits) / 3 + 1)\nfor (i, n) {\n\n\n\nstr result = \"\"\nint nines = 0\nint predigit = 1\n\nfor (i, n_digits) {\nint carry = 0\nint k = n - 1\n\n\nwhile (k >= 1) {\nint x = a[k] * 10 + carry * k\nint denom = 2 * k - 1\na[k] = x % denom\ncarry = x / denom\nk -= 1\n\n\nint x = a[0] * 10 + carry\nint q = int(x / 10)\na[0] = x % 10\n\nif (i < 2) {\n\n}\n\n\nif (q == 9) {\nnines += 1\n\n\nresult += str(predigit + 1)\nfor (j, nines) {\nresult += \"0\"\n\npredigit = 0\nnines = 0\n\n\nresult += str(predigit)\npredigit = q\nif (nines > 0) {\nfor (j, nines) {\nresult += \"9\"\n\nnines = 0\n\n\n\n\n\nresult += str(predigit)\n\n\nreturn f\"3.{result}\"\n\n\n\n\nstr pi = pi_spigot(10000)\nprintln(pi)"

.section .bss
.globl global_vars
global_vars:
    .space 16  # Optimized (was 2048, max offset 0)
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
