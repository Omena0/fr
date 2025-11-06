.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .struct 0 2 16 name age str int
    # .func main void 0

main:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .local p struct:Person
    # .line 9
    # CONST_STR "John Doe"
    lea rax, [.STR0]
    push rax
    # CONST_I64 30
    mov rax, 30
    push rax
    # STRUCT_NEW 0
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 4096
    jb .Lstruct_no_wrap_0  # Jump if below 4096
    xor rcx, rcx  # rcx >= 4096, wrap to 0
    .Lstruct_no_wrap_0:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
    shl rax, 16
    or rax, 0
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 10
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 4096
    jb .Linstance_ok_1
    and rbx, 0xFFF  # Wrap to 0-4095
    .Linstance_ok_1:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    # Field 0 type: age (struct_id: 0)
    mov rax, [rdx + rax]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_aligned_2
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_2
.Lruntime_println_aligned_2: 
    call runtime_println
.Lruntime_println_done_2: 
    # .line 11
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 4096
    jb .Linstance_ok_3
    and rbx, 0xFFF  # Wrap to 0-4095
    .Linstance_ok_3:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    # Field 1 type: str (struct_id: 0)
    mov rax, [rdx + rax]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_4
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_4
.Lruntime_println_str_aligned_4: 
    call runtime_println_str
.Lruntime_println_str_done_4: 
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
    .asciz "John Doe"

.section .bss
global_vars:
    .space 2048  # Space for 256 global variables (8 bytes each)
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
struct_data:
    .space 1048576  # Space for struct instances (4096 instances * 256 bytes each)
