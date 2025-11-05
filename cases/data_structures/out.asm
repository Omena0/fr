.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .struct 0 2 8 x y int int
    # .struct_type Point 0
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
    jz .Lruntime_init_aligned_7
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_7
.Lruntime_init_aligned_7: 
    call runtime_init
.Lruntime_init_done_7: 
    lea rdi, [.STR0]  # filename
    lea rsi, [.STR1]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_8
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_8
.Lruntime_set_source_info_aligned_8: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_8: 
    # .local p1 struct:Point
    # .local p2 struct:Point
    # .local points i64
    # .line 9 "Point p1 = Point(1, 2)"
    # CONST_I64 1 2
    mov rax, 1
    push rax
    mov rax, 2
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
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 10 "Point p2 = Point(3, 4)"
    # CONST_I64 3 4
    mov rax, 3
    push rax
    mov rax, 4
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
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 12 "list points = [p1, p2]"
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
    # LOAD 0
    mov rax, [rbp - 8]
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
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # LIST_APPEND 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_list_append_int_aligned_2
    sub rsp, 8
    call runtime_list_append_int
    add rsp, 8
    jmp .Lruntime_list_append_int_done_2
.Lruntime_list_append_int_aligned_2: 
    call runtime_list_append_int
.Lruntime_list_append_int_done_2: 
    push rdi
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 14 "println(points[0].x)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    mov rdx, 14  # line number
    call runtime_list_get_int_at
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
    jz .Lruntime_println_aligned_3
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_3
.Lruntime_println_aligned_3: 
    call runtime_println
.Lruntime_println_done_3: 
    # .line 15 "println(points[0].y)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    mov rdx, 15  # line number
    call runtime_list_get_int_at
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
    jz .Lruntime_println_aligned_4
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_4
.Lruntime_println_aligned_4: 
    call runtime_println
.Lruntime_println_done_4: 
    # .line 16 "println(points[1].x)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CONST_I64 1
    mov rax, 1
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    mov rdx, 16  # line number
    call runtime_list_get_int_at
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
    jz .Lruntime_println_aligned_5
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_5
.Lruntime_println_aligned_5: 
    call runtime_println
.Lruntime_println_done_5: 
    # .line 17 "println(points[1].y)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CONST_I64 1
    mov rax, 1
    push rax
    # LIST_GET 
    pop rsi
    pop rdi
    mov rdx, 17  # line number
    call runtime_list_get_int_at
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
    jz .Lruntime_println_aligned_6
    sub rsp, 8
    call runtime_println
    add rsp, 8
    jmp .Lruntime_println_done_6
.Lruntime_println_aligned_6: 
    call runtime_println
.Lruntime_println_done_6: 
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
    .asciz "struct_in_list.fr"
.STR1:
    .asciz "







Point p1 = Point(1, 2)
Point p2 = Point(3, 4)

list points = [p1, p2]

println(points[0].x)
println(points[0].y)
println(points[1].x)
println(points[1].y)"

.section .bss
global_vars:
    .space 2048  # Space for 256 global variables (8 bytes each)
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
struct_data:
    .space 6553600  # Space for struct instances (25600 instances * 256 bytes each)
