.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .func helper void 0

.align 16  # Function alignment
helper:
    push rbp
    mov rbp, rsp
    sub rsp, 16  # Optimized frame size (was 256)
    # .local nums i64
    # .local x i64
    # .line 4 "    list nums = [42]"
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
    push rax
    # CONST_I64 42
    mov rax, 42
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
    # STORE 0
    pop qword ptr [rbp - 8]  # Direct pop to memory
    # .line 5 "    int x = nums[100]"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CONST_I64 100
    mov rax, 100
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    mov rdx, 5  # line number
    call runtime_list_get_int_at
    # Removed redundant push rax; pop rax
    mov [rbp - 16], rax
    mov [rbp - 16], rax
    # RETURN_VOID 
.Lhelper_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .func main void 0

.align 16  # Function alignment
main:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # Initialize runtime and source info
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_init_aligned_2
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_2
.Lruntime_init_aligned_2: 
    call runtime_init
.Lruntime_init_done_2: 
    lea rdi, [.STR0]  # filename
    lea rsi, [.STR1]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_3
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_3
.Lruntime_set_source_info_aligned_3: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_3: 
    # .line 9 "    helper()"
    # CALL helper 0
    call helper
    push rax
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .entry main

.section .rodata
.STR0:
    .asciz "cases/runtime_errors/index_error_in_function.fr"
.STR1:
    .asciz "


    list nums = [42]
    int x = nums[100]



    helper()"

.section .bss
global_vars:
    .space 16  # Optimized (was 2048, max offset 0)
.align 16  # Function alignment
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
.align 16  # Function alignment
struct_data:
    .space 65536  # Space for struct instances (256 instances * 256 bytes each)
