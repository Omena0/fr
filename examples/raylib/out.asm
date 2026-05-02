.intel_syntax noprefix
.section .text
.global main
.align 16
createPaddle:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 16], r13
    mov r12, [rbp + 24]
    mov r13, [rbp + 16]
    push r12
    push r13
    push 20
    push 120
    movsd xmm0, [.FLOAT0]
    sub rsp, 8
    movsd [rsp], xmm0
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_0
    mov rcx, 1024
    .Lstruct_no_wrap_0:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 32], rbx
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 34
    push rax
    pop rax
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    leave
    ret
.align 16
createBall:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 32], r15
    mov r14, [rbp + 24]
    mov r15, [rbp + 16]
    mov r12, r14
    mov r13, r15
    push r12
    push r13
    movsd xmm0, [.FLOAT1]
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [.FLOAT2]
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    mov rax, 0x8000000000000000
    movq xmm1, rax
    xorpd xmm0, xmm1
    movsd [rsp], xmm0
    movsd xmm0, [.FLOAT3]
    sub rsp, 8
    movsd [rsp], xmm0
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_1
    mov rcx, 1024
    .Lstruct_no_wrap_1:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 32], rbx
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 35
    push rax
    pop rax
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.align 16
updatePaddle:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 32], r15
    mov r12, [rbp + 32]
    mov rax, [rbp + 24]
    mov [rbp - 48], rax
    mov rax, [rbp + 16]
    mov [rbp - 56], rax
    mov [rbp - 56], rax
    test spl, 0xF
    jz .LGetFrameTime_aligned_2
    sub rsp, 8
    call GetFrameTime
    add rsp, 8
    jmp .LGetFrameTime_done_2
    .LGetFrameTime_aligned_2:
    call GetFrameTime
    .LGetFrameTime_done_2:
    mov qword ptr [rbp - 88], rax
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_3
    and rbx, 0x3FFFF
    .Linstance_ok_3:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    mov rax, [rsp]
    mov r14, rax
    pop r13
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_4
    and rbx, 0x3FFFF
    .Linstance_ok_4:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_5
    and rbx, 0x3FFFF
    .Linstance_ok_5:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r14, rax
    mov rax, [rbp - 48]
    mov rdi, rax
    test spl, 0xF
    jz .LIsKeyDown_aligned_6
    sub rsp, 8
    call IsKeyDown
    add rsp, 8
    jmp .LIsKeyDown_done_6
    .LIsKeyDown_aligned_6:
    call IsKeyDown
    .LIsKeyDown_done_6:
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end0
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_7
    and rbx, 0x3FFFF
    .Linstance_ok_7:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_8
    and rbx, 0x3FFFF
    .Linstance_ok_8:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    mov rax, [rsp]
    mov r14, rax
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    mov rbx, [rbp - 88]
    mov rax, [rbp - 72]
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r13, rax
.LupdatePaddle_if_end0:
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_9
    and rbx, 0x3FFFF
    .Linstance_ok_9:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_10
    and rbx, 0x3FFFF
    .Linstance_ok_10:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r14, rax
    mov rax, [rbp - 56]
    mov rdi, rax
    test spl, 0xF
    jz .LIsKeyDown_aligned_11
    sub rsp, 8
    call IsKeyDown
    add rsp, 8
    jmp .LIsKeyDown_done_11
    .LIsKeyDown_aligned_11:
    call IsKeyDown
    .LIsKeyDown_done_11:
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end2
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_12
    and rbx, 0x3FFFF
    .Linstance_ok_12:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_13
    and rbx, 0x3FFFF
    .Linstance_ok_13:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    mov rax, [rsp]
    mov r14, rax
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    mov rbx, [rbp - 88]
    mov rax, [rbp - 72]
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r13, rax
.LupdatePaddle_if_end2:
    mov rax, r13
    cmp rax, 0
    jge .LupdatePaddle_if_end4
    mov rax, 0
    mov r13, 0
.LupdatePaddle_if_end4:
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_14
    and rbx, 0x3FFFF
    .Linstance_ok_14:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop r15
    push r13
    mov rbx, r15
    pop rax
    add rax, rbx
    push rax
    pop rax
    cmp rax, 600
    jle .LupdatePaddle_if_end6
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_15
    and rbx, 0x3FFFF
    .Linstance_ok_15:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop r15
    push 600
    mov rbx, r15
    pop rax
    sub rax, rbx
    mov r13, rax
.LupdatePaddle_if_end6:
    push r12
    push r13
    pop rbx
    pop rax
    mov rcx, rax
    shr rcx, 16
    push rax
    mov rax, rcx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov [rdx + rax], rbx
    pop r12
    mov rax, r12
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.align 16
updateBall:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 32], r15
    mov r12, [rbp + 16]
    test spl, 0xF
    jz .LGetFrameTime_aligned_16
    sub rsp, 8
    call GetFrameTime
    add rsp, 8
    jmp .LGetFrameTime_done_16
    .LGetFrameTime_aligned_16:
    call GetFrameTime
    .LGetFrameTime_done_16:
    mov qword ptr [rbp - 88], rax
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_17
    and rbx, 0x3FFFF
    .Linstance_ok_17:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 56]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_18
    and rbx, 0x3FFFF
    .Linstance_ok_18:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    mov rax, [rsp]
    mov r15, rax
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    mov rbx, [rbp - 88]
    mov rax, [rbp - 56]
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r14, rax
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_19
    and rbx, 0x3FFFF
    .Linstance_ok_19:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 64]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_20
    and rbx, 0x3FFFF
    .Linstance_ok_20:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    push qword ptr [rsp]
    pop qword ptr [rbp - 80]
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    mov rbx, [rbp - 88]
    mov rax, [rbp - 64]
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r13, rax
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_21
    and rbx, 0x3FFFF
    .Linstance_ok_21:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rsp]
    pop qword ptr [rbp - 64]
    pop qword ptr [rbp - 96]
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_22
    and rbx, 0x3FFFF
    .Linstance_ok_22:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 48]
    push r13
    push qword ptr [rbp - 48]
    pop rbx
    pop rax
    cmp rax, rbx
    jge .LupdateBall_if_end0
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_23
    and rbx, 0x3FFFF
    .Linstance_ok_23:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rsp]
    pop qword ptr [rbp - 48]
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r13, rax
    movsd xmm0, [.FLOAT4]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 96]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 96]
.LupdateBall_if_end0:
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_24
    and rbx, 0x3FFFF
    .Linstance_ok_24:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 48]
    push r13
    push 600
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 48]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    pop rbx
    pop rax
    cmp rax, rbx
    jle .LupdateBall_if_end2
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_25
    and rbx, 0x3FFFF
    .Linstance_ok_25:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 48]
    push 600
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 48]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [rsp]
    add rsp, 8
    cvttsd2si rax, xmm0
    mov r13, rax
    movsd xmm0, [.FLOAT5]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 96]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 96]
.LupdateBall_if_end2:
    push r12
    push r14
    pop rbx
    pop rax
    mov rcx, rax
    shr rcx, 16
    push rax
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    mov [rdx + rax], rbx
    pop r12
    push r12
    push r13
    pop rbx
    pop rax
    mov rcx, rax
    shr rcx, 16
    push rax
    mov rax, rcx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov [rdx + rax], rbx
    pop r12
    push r12
    push qword ptr [rbp - 96]
    pop rbx
    pop rax
    mov rcx, rax
    shr rcx, 16
    push rax
    mov rax, rcx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    mov [rdx + rax], rbx
    pop r12
    mov rax, r12
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.align 16
checkLeftPaddleCollision:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 32], r15
    mov r12, [rbp + 24]
    mov rax, [rbp + 16]
    mov [rbp - 48], rax
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_26
    and rbx, 0x3FFFF
    .Linstance_ok_26:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 56]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_27
    and rbx, 0x3FFFF
    .Linstance_ok_27:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 64]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_28
    and rbx, 0x3FFFF
    .Linstance_ok_28:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_29
    and rbx, 0x3FFFF
    .Linstance_ok_29:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_30
    and rbx, 0x3FFFF
    .Linstance_ok_30:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r13, rax
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_31
    and rbx, 0x3FFFF
    .Linstance_ok_31:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 96]
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_32
    and rbx, 0x3FFFF
    .Linstance_ok_32:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 104]
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_33
    and rbx, 0x3FFFF
    .Linstance_ok_33:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r14, rax
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_34
    and rbx, 0x3FFFF
    .Linstance_ok_34:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r15, rax
    push qword ptr [rbp - 80]
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 56]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    mov rax, r14
    add rax, [rbp - 104]
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setle al
    movzx rax, al
    push rax
    mov rax, [rbp - 80]
    cmp rax, r14
    setge al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    mov rax, r13
    cmp rax, r15
    setge al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    push r13
    push r15
    push qword ptr [rbp - 96]
    pop rbx
    pop rax
    add rax, rbx
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setle al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz .LcheckLeftPaddleCollision_if_end0
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_35
    and rbx, 0x3FFFF
    .Linstance_ok_35:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 56]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_36
    and rbx, 0x3FFFF
    .Linstance_ok_36:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 64]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_37
    and rbx, 0x3FFFF
    .Linstance_ok_37:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_38
    and rbx, 0x3FFFF
    .Linstance_ok_38:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_39
    and rbx, 0x3FFFF
    .Linstance_ok_39:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r13, rax
    push qword ptr [rbp - 80]
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [.FLOAT6]
    movsd xmm1, [rsp]
    add rsp, 8
    addsd xmm1, xmm0
    sub rsp, 8
    movsd [rsp], xmm1
    push r13
    push qword ptr [rbp - 56]
    movsd xmm0, [.FLOAT7]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 64]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 72]
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_40
    mov rcx, 1024
    .Lstruct_no_wrap_40:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 32], rbx
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 35
    push rax
    pop rax
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.LcheckLeftPaddleCollision_if_end0:
    mov rax, r12
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.align 16
checkRightPaddleCollision:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    mov [rbp - 32], r15
    mov r12, [rbp + 24]
    mov rax, [rbp + 16]
    mov [rbp - 48], rax
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_41
    and rbx, 0x3FFFF
    .Linstance_ok_41:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 56]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_42
    and rbx, 0x3FFFF
    .Linstance_ok_42:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 64]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_43
    and rbx, 0x3FFFF
    .Linstance_ok_43:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_44
    and rbx, 0x3FFFF
    .Linstance_ok_44:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_45
    and rbx, 0x3FFFF
    .Linstance_ok_45:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r13, rax
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_46
    and rbx, 0x3FFFF
    .Linstance_ok_46:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 96]
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_47
    and rbx, 0x3FFFF
    .Linstance_ok_47:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 104]
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_48
    and rbx, 0x3FFFF
    .Linstance_ok_48:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r14, rax
    push qword ptr [rbp - 48]
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_49
    and rbx, 0x3FFFF
    .Linstance_ok_49:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r15, rax
    push qword ptr [rbp - 80]
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 56]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    mov rbx, r14
    pop rax
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
    push qword ptr [rbp - 80]
    push r14
    push qword ptr [rbp - 104]
    pop rbx
    pop rax
    add rax, rbx
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setle al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    mov rax, r13
    cmp rax, r15
    setge al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    push r13
    push r15
    push qword ptr [rbp - 96]
    pop rbx
    pop rax
    add rax, rbx
    mov rbx, rax
    pop rax
    cmp rax, rbx
    setle al
    movzx rax, al
    mov rbx, rax
    pop rax
    test rax, rax
    setnz al
    test rbx, rbx
    setnz bl
    and al, bl
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jz .LcheckRightPaddleCollision_if_end0
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_50
    and rbx, 0x3FFFF
    .Linstance_ok_50:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 56]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_51
    and rbx, 0x3FFFF
    .Linstance_ok_51:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 64]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_52
    and rbx, 0x3FFFF
    .Linstance_ok_52:
    mov rax, rbx
    shl rax, 8
    add rax, 32
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    pop qword ptr [rbp - 72]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_53
    and rbx, 0x3FFFF
    .Linstance_ok_53:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_54
    and rbx, 0x3FFFF
    .Linstance_ok_54:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    mov r13, rax
    push qword ptr [rbp - 80]
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [.FLOAT8]
    movsd xmm1, [rsp]
    add rsp, 8
    subsd xmm1, xmm0
    sub rsp, 8
    movsd [rsp], xmm1
    push r13
    push qword ptr [rbp - 56]
    movsd xmm0, [.FLOAT9]
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 64]
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 72]
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_55
    mov rcx, 1024
    .Lstruct_no_wrap_55:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 32], rbx
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 35
    push rax
    pop rax
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.LcheckRightPaddleCollision_if_end0:
    mov rax, r12
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.align 16
main:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    push rdi
    push rcx
    push rax
    lea rdi, [rsp + 24]
    mov rcx, 32
    xor rax, rax
    rep stosq
    pop rax
    pop rcx
    pop rdi
    mov rax, rsp
    add rax, 8
    test rax, 0xF
    pop rax
    jz .Lruntime_init_aligned_104
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_104
.Lruntime_init_aligned_104: 
    call runtime_init
.Lruntime_init_done_104: 
    lea rdi, [.STR15]
    lea rsi, [.STR16]
    test spl, 0xF
    jz .Lruntime_set_source_info_aligned_105
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_105
.Lruntime_set_source_info_aligned_105: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_105: 
    mov [rbp - 32], r15
    push 1200
    push 600
    lea rax, [.STR10]
    mov rdx, rax
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LInitWindow_aligned_56
    sub rsp, 8
    call InitWindow
    add rsp, 8
    jmp .LInitWindow_done_56
    .LInitWindow_aligned_56:
    call InitWindow
    .LInitWindow_done_56:
    push 60
    pop rdi
    test spl, 0xF
    jz .LSetTargetFPS_aligned_57
    sub rsp, 8
    call SetTargetFPS
    add rsp, 8
    jmp .LSetTargetFPS_done_57
    .LSetTargetFPS_aligned_57:
    call SetTargetFPS
    .LSetTargetFPS_done_57:
    push 0
    push 0
    push 50
    push 255
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_58
    mov rcx, 1024
    .Lstruct_no_wrap_58:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 4
    mov qword ptr [rbp - 144], rax
    push 0
    push 255
    push 0
    push 255
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_59
    mov rcx, 1024
    .Lstruct_no_wrap_59:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 4
    mov qword ptr [rbp - 168], rax
    push 255
    push 255
    push 100
    push 255
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_60
    mov rcx, 1024
    .Lstruct_no_wrap_60:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 4
    mov qword ptr [rbp - 136], rax
    push 255
    push 255
    push 255
    push 255
    lea rax, [rip + struct_counter]
    mov rcx, [rax]
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_61
    mov rcx, 1024
    .Lstruct_no_wrap_61:
    mov [rax], rcx
    mov rax, rcx
    shl rax, 8
    lea rdx, [rip + struct_data]
    pop rbx
    mov [rdx + rax + 24], rbx
    pop rbx
    mov [rdx + rax + 16], rbx
    pop rbx
    mov [rdx + rax + 8], rbx
    pop rbx
    mov [rdx + rax + 0], rbx
    mov rax, rcx
    shl rax, 16
    or rax, 4
    mov r15, rax
    push 30
    push 250
    call createPaddle
    mov r13, rax
    push 1160
    push 250
    call createPaddle
    mov r14, rax
    push 600
    push 300
    call createBall
    mov r12, rax
    mov qword ptr [rbp - 160], 0
    mov qword ptr [rbp - 184], 0
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_62
    and rbx, 0x3FFFF
    .Linstance_ok_62:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 40]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_63
    and rbx, 0x3FFFF
    .Linstance_ok_63:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 48]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_64
    and rbx, 0x3FFFF
    .Linstance_ok_64:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 56]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_65
    and rbx, 0x3FFFF
    .Linstance_ok_65:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 64]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_66
    and rbx, 0x3FFFF
    .Linstance_ok_66:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 72]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_67
    and rbx, 0x3FFFF
    .Linstance_ok_67:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_68
    and rbx, 0x3FFFF
    .Linstance_ok_68:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 88]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_69
    and rbx, 0x3FFFF
    .Linstance_ok_69:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 96]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_70
    and rbx, 0x3FFFF
    .Linstance_ok_70:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 104]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_71
    and rbx, 0x3FFFF
    .Linstance_ok_71:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 112]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_72
    and rbx, 0x3FFFF
    .Linstance_ok_72:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 120]
.align 16
.Lmain_while_start0:
    test spl, 0xF
    jz .LWindowShouldClose_aligned_73
    sub rsp, 8
    call WindowShouldClose
    add rsp, 8
    jmp .LWindowShouldClose_done_73
    .LWindowShouldClose_aligned_73:
    call WindowShouldClose
    .LWindowShouldClose_done_73:
    movzx rax, al
    push rax
    pop rax
    test rax, rax
    jnz .Lmain_while_end1
    push r13
    push 265
    push 264
    call updatePaddle
    mov r13, rax
    push r14
    push 87
    push 83
    call updatePaddle
    mov r14, rax
    push r12
    call updateBall
    mov r12, rax
    push r12
    push r13
    call checkLeftPaddleCollision
    mov r12, rax
    push r12
    push r14
    call checkRightPaddleCollision
    mov r12, rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_74
    and rbx, 0x3FFFF
    .Linstance_ok_74:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 40]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_75
    and rbx, 0x3FFFF
    .Linstance_ok_75:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    push qword ptr [rsp]
    pop qword ptr [rbp - 48]
    push qword ptr [rbp - 40]
    push 2
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    pop rax
    cvtsi2sd xmm0, rax
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    pop rbx
    pop rax
    cmp rax, rbx
    jge .Lmain_if_end2
    inc qword ptr [rbp - 160]
    push 600
    push 300
    call createBall
    mov r12, rax
.Lmain_if_end2:
    mov rbx, r12
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_76
    and rbx, 0x3FFFF
    .Linstance_ok_76:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 40]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_77
    and rbx, 0x3FFFF
    .Linstance_ok_77:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    push qword ptr [rsp]
    pop qword ptr [rbp - 48]
    push 1200
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    push qword ptr [rbp - 40]
    pop rax
    cvtsi2sd xmm1, rax
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    push 2
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    pop rbx
    pop rax
    cmp rax, rbx
    jle .Lmain_if_end4
    inc qword ptr [rbp - 184]
    push 600
    push 300
    call createBall
    mov r12, rax
.Lmain_if_end4:
    test spl, 0xF
    jz .LBeginDrawing_aligned_78
    sub rsp, 8
    call BeginDrawing
    add rsp, 8
    jmp .LBeginDrawing_done_78
    .LBeginDrawing_aligned_78:
    call BeginDrawing
    .LBeginDrawing_done_78:
    push qword ptr [rbp - 144]
    pop rax
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor rdi, rdi
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or rdi, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or rdi, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or rdi, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or rdi, rbx
    test spl, 0xF
    jz .LClearBackground_aligned_79
    sub rsp, 8
    call ClearBackground
    add rsp, 8
    jmp .LClearBackground_done_79
    .LClearBackground_aligned_79:
    call ClearBackground
    .LClearBackground_done_79:
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_80
    and rbx, 0x3FFFF
    .Linstance_ok_80:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 64]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_81
    and rbx, 0x3FFFF
    .Linstance_ok_81:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 72]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_82
    and rbx, 0x3FFFF
    .Linstance_ok_82:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 80]
    push r13
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_83
    and rbx, 0x3FFFF
    .Linstance_ok_83:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 88]
    push qword ptr [rbp - 80]
    push qword ptr [rbp - 88]
    push qword ptr [rbp - 72]
    push qword ptr [rbp - 64]
    push qword ptr [rbp - 168]
    pop rax
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawRectangle_aligned_84
    sub rsp, 8
    call DrawRectangle
    add rsp, 8
    jmp .LDrawRectangle_done_84
    .LDrawRectangle_aligned_84:
    call DrawRectangle
    .LDrawRectangle_done_84:
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_85
    and rbx, 0x3FFFF
    .Linstance_ok_85:
    mov rax, rbx
    shl rax, 8
    add rax, 24
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 96]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_86
    and rbx, 0x3FFFF
    .Linstance_ok_86:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 104]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_87
    and rbx, 0x3FFFF
    .Linstance_ok_87:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 112]
    push r14
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_88
    and rbx, 0x3FFFF
    .Linstance_ok_88:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 120]
    push qword ptr [rbp - 112]
    push qword ptr [rbp - 120]
    push qword ptr [rbp - 104]
    push qword ptr [rbp - 96]
    push qword ptr [rbp - 168]
    pop rax
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawRectangle_aligned_89
    sub rsp, 8
    call DrawRectangle
    add rsp, 8
    jmp .LDrawRectangle_done_89
    .LDrawRectangle_aligned_89:
    call DrawRectangle
    .LDrawRectangle_done_89:
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_90
    and rbx, 0x3FFFF
    .Linstance_ok_90:
    mov rax, rbx
    shl rax, 8
    add rax, 16
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 40]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_91
    and rbx, 0x3FFFF
    .Linstance_ok_91:
    mov rax, rbx
    shl rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 48]
    push r12
    pop rax
    mov rbx, rax
    shr rbx, 16
    cmp rbx, 262144
    jb .Linstance_ok_92
    and rbx, 0x3FFFF
    .Linstance_ok_92:
    mov rax, rbx
    shl rax, 8
    add rax, 8
    lea rdx, [rip + struct_data]
    push qword ptr [rdx + rax]
    pop qword ptr [rbp - 56]
    push qword ptr [rbp - 48]
    push qword ptr [rbp - 56]
    push qword ptr [rbp - 40]
    push qword ptr [rbp - 136]
    pop rax
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor rdx, rdx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or rdx, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or rdx, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or rdx, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or rdx, rbx
    pop rax
    cvtsi2ss xmm0, rax
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawCircle_aligned_93
    sub rsp, 8
    call DrawCircle
    add rsp, 8
    jmp .LDrawCircle_done_93
    .LDrawCircle_aligned_93:
    call DrawCircle
    .LDrawCircle_done_93:
    lea rax, [.STR11]
    push rax
    push 450
    push 20
    push 40
    mov rax, r15
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawText_aligned_94
    sub rsp, 8
    call DrawText
    add rsp, 8
    jmp .LDrawText_done_94
    .LDrawText_aligned_94:
    call DrawText
    .LDrawText_done_94:
    lea rax, [.STR12]
    push rax
    push qword ptr [rbp - 160]
    pop rdi
    test spl, 0xF
    jz .Lruntime_int_to_str_aligned_95
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_95
.Lruntime_int_to_str_aligned_95: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_95: 
    mov rsi, rax
    pop rdi
    test spl, 0xF
    jz .Lruntime_str_concat_checked_aligned_96
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_96
.Lruntime_str_concat_checked_aligned_96: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_96: 
    push rax
    push 100
    push 50
    push 30
    mov rax, r15
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawText_aligned_97
    sub rsp, 8
    call DrawText
    add rsp, 8
    jmp .LDrawText_done_97
    .LDrawText_aligned_97:
    call DrawText
    .LDrawText_done_97:
    lea rax, [.STR13]
    push rax
    push qword ptr [rbp - 184]
    pop rdi
    test spl, 0xF
    jz .Lruntime_int_to_str_aligned_98
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_98
.Lruntime_int_to_str_aligned_98: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_98: 
    mov rsi, rax
    pop rdi
    test spl, 0xF
    jz .Lruntime_str_concat_checked_aligned_99
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_99
.Lruntime_str_concat_checked_aligned_99: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_99: 
    push rax
    push 1000
    push 50
    push 30
    mov rax, r15
    shr rax, 16
    and rax, 0x3FFF
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 0]
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 8]
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 16]
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx
    mov bl, byte ptr [r10 + rax + 24]
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    test spl, 0xF
    jz .LDrawText_aligned_100
    sub rsp, 8
    call DrawText
    add rsp, 8
    jmp .LDrawText_done_100
    .LDrawText_aligned_100:
    call DrawText
    .LDrawText_done_100:
    test spl, 0xF
    jz .LEndDrawing_aligned_101
    sub rsp, 8
    call EndDrawing
    add rsp, 8
    jmp .Lmain_while_start0
    .LEndDrawing_aligned_101:
    call EndDrawing
    jmp .Lmain_while_start0
.Lmain_while_end1:
    test spl, 0xF
    jz .LCloseWindow_aligned_102
    sub rsp, 8
    call CloseWindow
    add rsp, 8
    jmp .LCloseWindow_done_102
    .LCloseWindow_aligned_102:
    call CloseWindow
    .LCloseWindow_done_102:
    lea rax, [.STR14]
    mov rdi, rax
    test spl, 0xF
    jz .Lruntime_println_str_aligned_103
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_103
.Lruntime_println_str_aligned_103: 
    call runtime_println_str
.Lruntime_println_str_done_103: 
    xor rax, rax
    mov r12, [rbp - 8]
    mov r13, [rbp - 16]
    mov r14, [rbp - 24]
    mov r15, [rbp - 32]
    leave
    ret
.section .rodata
.FLOAT0:
    .double 720.0
.FLOAT1:
    .double 20.0
.FLOAT2:
    .double 300.0
.FLOAT3:
    .double 100.0
.FLOAT4:
    .double 0.0
.FLOAT5:
    .double 0.0
.FLOAT6:
    .double 12.0
.FLOAT7:
    .double 0.0
.FLOAT8:
    .double 12.0
.FLOAT9:
    .double 0.0
.STR10:
    .asciz "Pong"
.STR11:
    .asciz "Pong Game"
.STR12:
    .asciz "Left: "
.STR13:
    .asciz "Right: "
.STR14:
    .asciz "Thanks for playing Pong in Fr!"
.STR15:
    .asciz "pong.fr"
.STR16:
    .asciz "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nreturn Paddle(startX, startY, 20, 120, 720.0)\n\n\n\nint fx = startX\nint fy = startY\nreturn Ball(fx, fy, 20.0, -300.0, 100.0)\n\n\n\nfloat dt = GetFrameTime()\n\nint newY = p.y\nif (IsKeyDown(upKey)) {\nnewY = p.y - p.speed * dt\n\nif (IsKeyDown(downKey)) {\nnewY = p.y + p.speed * dt\n\nif (newY < 0) {\nnewY = 0\n\nif (newY + p.height > 600) {\nnewY = 600 - p.height\n\np.y = newY\nreturn p\n\n\n\nfloat dt = GetFrameTime()\n\nint newX = int(b.x + b.velX * dt)\nint newY = int(b.y + b.velY * dt)\nfloat newVelY = b.velY\n\nif (newY < b.radius) {\nnewY = b.radius\nnewVelY = 0.0 - newVelY\n\nif (newY > 600 - b.radius) {\nnewY = 600 - b.radius\nnewVelY = 0.0 - newVelY\n\n\nb.x = newX\nb.y = newY\nb.velY = newVelY\nreturn b\n\n\n\nif (b.x - b.radius <= p.x + p.width && b.x >= p.x && b.y >= p.y && b.y <= p.y + p.height) {\nreturn Ball(b.x + 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)\n\nreturn b\n\n\n\nif (b.x + b.radius >= p.x && b.x <= p.x + p.width && b.y >= p.y && b.y <= p.y + p.height) {\nreturn Ball(b.x - 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)\n\nreturn b\n\n\n\nInitWindow(1200, 600, \"Pong\")\nSetTargetFPS(60)\n\nColor bgColor = Color(0, 0, 50, 255)\nColor paddleColor = Color(0, 255, 0, 255)\nColor ballColor = Color(255, 255, 100, 255)\nColor textColor = Color(255, 255, 255, 255)\n\nPaddle leftPaddle = createPaddle(30, 250)\nPaddle rightPaddle = createPaddle(1160, 250)\nBall ball = createBall(600, 300)\n\nint leftScore = 0\n\n\nwhile (!WindowShouldClose()) {\nleftPaddle = updatePaddle(leftPaddle, 265, 264)\nrightPaddle = updatePaddle(rightPaddle, 87, 83)\nball = updateBall(ball)\n\nball = checkLeftPaddleCollision(ball, leftPaddle)\nball = checkRightPaddleCollision(ball, rightPaddle)\n\nif (ball.x < ball.radius+2) {\nleftScore = leftScore + 1\nball = createBall(600, 300)\n\nif (ball.x > 1200 - ball.radius-2) {\nrightScore = rightScore + 1\nball = createBall(600, 300)\n\n\nBeginDrawing()\nClearBackground(bgColor)\n\nDrawRectangle(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height, paddleColor)\nDrawRectangle(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height, paddleColor)\n\nDrawCircle(ball.x, ball.y, ball.radius, ballColor)\n\n\"DrawText(\"Pong\n\"DrawText(f\"Left:\n\"DrawText(f\"Right:\n\nEndDrawing()\n\n\nCloseWindow()\n\"println(\"Thanks"
.section .bss
.globl global_vars
global_vars:
    .space 16
.globl struct_heap_ptr
.align 16
struct_heap_ptr:
    .quad 0
.globl struct_heap_base
.align 16
struct_heap_base:
    .quad 0
.align 16
struct_counter:
    .quad 0
.align 16
list_append_scratch:
    .quad 0
.align 16
struct_data:
    .space 67108864