.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .struct 0 2 8 x y int int
    # .struct_type Point 0
    # .func createPoint struct:Point 2

createPoint:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg x i64
    mov [rbp - 8], rdi
    # .arg y i64
    mov [rbp - 16], rsi
    # .line 9 "return Point(x, y)"
    # LOAD 0 1
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 16]
    push rax
    # STRUCT_NEW 0
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov r10, rbx
    inc r10
    mov [rax], r10  # increment counter
    mov rax, rbx
    mov r10, 256
    imul rax, r10  # rax = instance_id * 256
    lea r10, [rip + struct_data]
    pop rcx  # field 1
    mov dword [r10 + rax + 4], ecx
    pop rcx  # field 0
    mov dword [r10 + rax + 0], ecx
    mov rax, rbx
    shl rax, 16
    or rax, 0
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LcreatePoint_skip_labels:
    # .func main void 0

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
    jz .Lruntime_init_aligned_4
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_4
.Lruntime_init_aligned_4: 
    call runtime_init
.Lruntime_init_done_4: 
    lea rdi, [.STR0]  # filename
    lea rsi, [.STR1]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_5
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_5
.Lruntime_set_source_info_aligned_5: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_5: 
    # .local p1 struct:Point
    # .local p2 struct:Point
    # .line 13 "Point p1 = createPoint(0, 0)"
    # CONST_I64 0 0
    mov rax, 0
    push rax
    mov rax, 0
    push rax
    # CALL createPoint 2
    pop rsi
    pop rdi
    call createPoint
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 14 "Point p2 = createPoint(5, 10)"
    # CONST_I64 5 10
    mov rax, 5
    push rax
    mov rax, 10
    push rax
    # CALL createPoint 2
    pop rsi
    pop rdi
    call createPoint
    push rax
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 16 "println(p1.x)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov r10, 256
    imul rax, r10  # rax = instance_id * 256
    add rax, 0  # rax += field offset
    lea r10, [rip + struct_data]
    mov rax, [r10 + rax]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_aligned_0
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_0
.Lruntime_println_aligned_0: 
    call runtime_println
.Lruntime_println_done_0: 
    # .line 17 "println(p1.y)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov r10, 256
    imul rax, r10  # rax = instance_id * 256
    add rax, 8  # rax += field offset
    lea r10, [rip + struct_data]
    mov rax, [r10 + rax]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_aligned_1
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_1
.Lruntime_println_aligned_1: 
    call runtime_println
.Lruntime_println_done_1: 
    # .line 18 "println(p2.x)"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov r10, 256
    imul rax, r10  # rax = instance_id * 256
    add rax, 0  # rax += field offset
    lea r10, [rip + struct_data]
    mov rax, [r10 + rax]
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
    # .line 19 "println(p2.y)"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov r10, 256
    imul rax, r10  # rax = instance_id * 256
    add rax, 8  # rax += field offset
    lea r10, [rip + struct_data]
    mov rax, [r10 + rax]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_aligned_3
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_3
.Lruntime_println_aligned_3: 
    call runtime_println
.Lruntime_println_done_3: 
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
    .asciz "struct_return.fr"
.STR1:
    .asciz "







return Point(x, y)



Point p1 = createPoint(0, 0)
Point p2 = createPoint(5, 10)

println(p1.x)
println(p1.y)
println(p2.x)
println(p2.y)"

.section .bss
global_vars:
    .space 2048  # Space for 256 global variables (8 bytes each)
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
struct_data:
    .space 6553600  # Space for struct instances (25600 instances * 256 bytes each)
