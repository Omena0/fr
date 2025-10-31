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
    jg .Lif_end0  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # LABEL if_end0
.Lif_end0:
    # STORE_CONST_I64 1 0 2 1 3 1 4 0
    mov qword ptr [rbp - 16], 0  # Immediate store
    mov qword ptr [rbp - 24], 1  # Immediate store
    mov qword ptr [rbp - 32], 1  # Immediate store
    mov qword ptr [rbp - 40], 0  # Immediate store
    # LABEL for_start2
.align 16  # Loop alignment
.Lfor_start2:
    # LOAD2_CMP_LT 4 0
    mov rax, [rbp - 40]
    cmp rax, [rbp - 8]
    jge .Lfor_end4  # Optimized: removed setcc+movzx+push+pop+test
    # LOAD2_ADD_I64 1 2
    mov rax, [rbp - 16]
    add rax, [rbp - 24]
    push rax
    # MOD_CONST_I64 1000000
    pop rax
    xor rdx, rdx
    mov rbx, 1000000
    idiv rbx
    mov [rbp - 32], rdx  # Direct store (no push/pop)
    # FUSED_STORE_LOAD 3 2 1 3 2
    mov rax, [rbp - 24]
    mov [rbp - 16], rax  # Direct store (no push/pop)
    mov rax, [rbp - 32]
    mov [rbp - 24], rax  # Direct store (no push/pop)
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # JUMP for_start2
    jmp .Lfor_start2
    # LABEL for_end4
.Lfor_end4:
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # RETURN 
    pop rax
    leave  # Optimized epilogue
    ret
    # .end 
.Lfibonacci_skip_labels:
    # .func main void 0

.align 16  # Function alignment
main:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # CONST_I64 1000000000
    mov rax, 1000000000
    push rax
    # CALL fibonacci 1
    pop rdi
    call fibonacci
    mov rdi, rax  # Optimized result transfer
    test rsp, 8
    jz .Lruntime_println_aligned_0
    sub rsp, 8  # Align stack
    call runtime_println
    add rsp, 8  # Restore stack
    jmp .Lruntime_println_done_0
.Lruntime_println_aligned_0:
    call runtime_println
.Lruntime_println_done_0:
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    leave  # Optimized epilogue
    ret
    # .end 
    # .entry main

.section .bss
global_vars:
    .space 16  # Optimized (was 2048, max offset 0)
.align 16  # Function alignment
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
.align 16  # Function alignment
struct_data:
    .space 65536  # Space for struct instances (256 instances * 256 bytes each)
