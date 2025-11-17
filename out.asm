.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .func main void 0

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
    jz .Lruntime_init_aligned_3
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_3
.Lruntime_init_aligned_3: 
    call runtime_init
.Lruntime_init_done_3: 
    lea rdi, [.STR0]  # filename
    lea rsi, [.STR1]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_4
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_4
.Lruntime_set_source_info_aligned_4: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_4: 
    # .local lst i64
    # .line 4 "list lst = []"
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
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 5 "println(str(lst))"
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
    jz .Lruntime_list_to_str_aligned_1
    sub rsp, 8
    call runtime_list_to_str
    add rsp, 8
    jmp .Lruntime_list_to_str_done_1
.Lruntime_list_to_str_aligned_1: 
    call runtime_list_to_str
.Lruntime_list_to_str_done_1: 
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_2
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_2
.Lruntime_println_str_aligned_2: 
    call runtime_println_str
.Lruntime_println_str_done_2: 
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
    # .entry main

.section .rodata
.STR0:
    .asciz "cases/data_types/list_empty.fr"
.STR1:
    .asciz "\n\n\nlist lst = []\nprintln(str(lst))"

.section .bss
.globl global_vars
global_vars:
    .space 2048  # Space for 256 global variables (8 bytes each)
.globl struct_heap_ptr
struct_heap_ptr:
    .quad 0  # Current heap position (bump allocator)
.globl struct_heap_base
struct_heap_base:
    .quad 0  # Base pointer to heap (allocated at runtime)
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
list_append_scratch:
    .quad 0  # Temporary storage for list pointer during list_append
struct_data:
    .space 67108864  # Space for struct instances (262144 instances * 256 bytes each = 64MB)
