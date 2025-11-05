.intel_syntax noprefix
.section .text
.global main

    # .version 1
    # .struct 0 2 8 x y float float
    # .struct 1 3 12 x y z float float float
    # .struct 2 4 16 x y z w float float float float
    # .struct 3 16 64 m0 m4 m8 m12 m1 m5 m9 m13 m2 m6 m10 m14 m3 m7 m11 m15 float float float float float float float float float float float float float float float float
    # .struct 4 4 4 r g b a unsigned char unsigned char unsigned char unsigned char
    # .struct 5 4 16 x y width height float float float float
    # .struct 6 4 16 width height mipmaps format int int int int
    # .struct 7 5 20 id width height mipmaps format unsigned int int int int int
    # .struct 8 3 24 id texture depth unsigned int Texture Texture
    # .struct 9 6 32 source left top right bottom layout Rectangle int int int int int
    # .struct 10 5 24 value offsetX offsetY advanceX image int int int int Image
    # .struct 11 4 24 baseSize glyphCount glyphPadding texture int int int Texture2D
    # .struct 12 5 32 position target up fovy projection Vector3 Vector3 Vector3 float int
    # .struct 13 4 24 offset target rotation zoom Vector2 Vector2 float float
    # .struct 14 4 16 vertexCount triangleCount boneCount vaoId int int int unsigned int
    # .struct 15 1 4 id unsigned int
    # .struct 16 3 24 texture color value Texture2D Color float
    # .struct 17 2 16 shader params Shader float
    # .struct 18 3 24 translation rotation scale Vector3 Quaternion Vector3
    # .struct 19 2 8 name parent char int
    # .struct 20 4 24 transform meshCount materialCount boneCount Matrix int int int
    # .struct 21 3 12 boneCount frameCount name int int char
    # .struct 22 2 16 position direction Vector3 Vector3
    # .struct 23 4 32 hit distance point normal bool float Vector3 Vector3
    # .struct 24 2 16 min max Vector3 Vector3
    # .struct 25 4 16 frameCount sampleRate sampleSize channels unsigned int unsigned int unsigned int unsigned int
    # .struct 26 3 12 sampleRate sampleSize channels unsigned int unsigned int unsigned int
    # .struct 27 2 16 stream frameCount AudioStream unsigned int
    # .struct 28 4 32 stream frameCount looping ctxType AudioStream unsigned int bool int
    # .struct 29 9 36 hResolution vResolution hScreenSize vScreenSize eyeToScreenDistance lensSeparationDistance interpupillaryDistance lensDistortionValues chromaAbCorrection int int float float float float float float float
    # .struct 30 8 40 projection viewOffset leftLensCenter rightLensCenter leftScreenCenter rightScreenCenter scale scaleIn Matrix Matrix float float float float float float
    # .struct 31 2 8 capacity count unsigned int unsigned int
    # .struct 32 3 12 frame type params unsigned int unsigned int int
    # .struct 33 2 8 capacity count unsigned int unsigned int
    # .struct 34 5 20 x y width height speed int int int int int
    # .struct 35 5 20 x y radius velX velY int int int int int
    # .func createPaddle struct:Paddle 2

createPaddle:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg startX i64
    mov [rbp - 8], rdi
    # .arg startY i64
    mov [rbp - 16], rsi
    # .line 21 "return Paddle(startX, startY, 20, 120, 12)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CONST_I64 20
    mov rax, 20
    push rax
    # CONST_I64 120
    mov rax, 120
    push rax
    # CONST_I64 12
    mov rax, 12
    push rax
    # STRUCT_NEW 34
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 34
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LcreatePaddle_skip_labels:
    # .func createBall struct:Ball 2

createBall:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg startX i64
    mov [rbp - 8], rdi
    # .arg startY i64
    mov [rbp - 16], rsi
    # .line 25 "return Ball(startX, startY, 20, 8, 6)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CONST_I64 20
    mov rax, 20
    push rax
    # CONST_I64 8
    mov rax, 8
    push rax
    # CONST_I64 6
    mov rax, 6
    push rax
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 35
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LcreateBall_skip_labels:
    # .func updatePaddle struct:Paddle 3

updatePaddle:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg p struct:Paddle
    mov [rbp - 8], rdi
    # .arg upKey i64
    mov [rbp - 16], rsi
    # .arg downKey i64
    mov [rbp - 24], rdx
    # .local newY i64
    # .line 29 "int newY = p.y"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 30 "if (IsKeyDown(upKey)) {"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CALL IsKeyDown 1 i|i
    pop rdi
    call IsKeyDown
    push rax
    # JUMP_IF_FALSE if_end0
    pop rax
    test rax, rax
    jz .LcheckRightPaddleCollision_if_end0
    # .line 31 "newY = p.y - p.speed"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # LABEL if_end0
.LupdatePaddle_if_end0:
    # .line 33 "if (IsKeyDown(downKey)) {"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CALL IsKeyDown 1 i|i
    pop rdi
    call IsKeyDown
    push rax
    # JUMP_IF_FALSE if_end2
    pop rax
    test rax, rax
    jz .Lmain_if_end2
    # .line 34 "newY = p.y + p.speed"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # LABEL if_end2
.LupdatePaddle_if_end2:
    # .line 36 "if (newY < 0) {"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end4
    pop rax
    test rax, rax
    jz .Lmain_if_end4
    # .line 37 "newY = 0"
    # CONST_I64 0
    mov rax, 0
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # LABEL if_end4
.LupdatePaddle_if_end4:
    # .line 39 "if (newY + p.height > 600) {"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CONST_I64 600
    mov rax, 600
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    setg al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end6
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end6
    # .line 40 "newY = 600 - p.height"
    # CONST_I64 600
    mov rax, 600
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # LABEL if_end6
.LupdatePaddle_if_end6:
    # .line 42 "return Paddle(p.x, newY, p.width, p.height, p.speed)"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STRUCT_NEW 34
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 34
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LupdatePaddle_skip_labels:
    # .func updateBall struct:Ball 1

updateBall:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg b struct:Ball
    mov [rbp - 8], rdi
    # .local newX i64
    # .local newY i64
    # .line 46 "int newX = int(b.x + b.velX)"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # TO_INT 
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 47 "int newY = int(b.y + b.velY)"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # TO_INT 
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 49 "if (newY < b.radius) {"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end0
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end0
    # .line 50 "newY = b.radius"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # LABEL if_end0
.LupdateBall_if_end0:
    # .line 52 "if (newY > 600 - b.radius) {"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CONST_I64 600
    mov rax, 600
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    setg al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end2
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end2
    # .line 53 "newY = 600 - b.radius"
    # CONST_I64 600
    mov rax, 600
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # LABEL if_end2
.LupdateBall_if_end2:
    # .line 56 "return Ball(newX, newY, b.radius, b.velX, b.velY)"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 35
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LupdateBall_skip_labels:
    # .func checkLeftPaddleCollision struct:Ball 2

checkLeftPaddleCollision:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg b struct:Ball
    mov [rbp - 8], rdi
    # .arg p struct:Paddle
    mov [rbp - 16], rsi
    # .line 60 "if (b.x - b.radius <= p.x + p.width && b.x >= p.x && b.y >= p.y && b.y <= p.y + p.height) {"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CMP_LE 
    pop rbx
    pop rax
    cmp rax, rbx
    setle al
    movzx rax, al
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CMP_GE 
    pop rbx
    pop rax
    cmp rax, rbx
    setge al
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CMP_GE 
    pop rbx
    pop rax
    cmp rax, rbx
    setge al
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CMP_LE 
    pop rbx
    pop rax
    cmp rax, rbx
    setle al
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
    # JUMP_IF_FALSE if_end0
    pop rax
    test rax, rax
    jz .LupdateBall_if_end0
    # .line 61 "return Ball(b.x + 12, b.y, b.radius, 0 - b.velX, b.velY)"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 12
    mov rax, 12
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 35
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # LABEL if_end0
.LcheckLeftPaddleCollision_if_end0:
    # .line 63 "return b"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LcheckLeftPaddleCollision_skip_labels:
    # .func checkRightPaddleCollision struct:Ball 2

checkRightPaddleCollision:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg b struct:Ball
    mov [rbp - 8], rdi
    # .arg p struct:Paddle
    mov [rbp - 16], rsi
    # .line 67 "if (b.x + b.radius >= p.x && b.x <= p.x + p.width && b.y >= p.y && b.y <= p.y + p.height) {"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CMP_GE 
    pop rbx
    pop rax
    cmp rax, rbx
    setge al
    movzx rax, al
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CMP_LE 
    pop rbx
    pop rax
    cmp rax, rbx
    setle al
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CMP_GE 
    pop rbx
    pop rax
    cmp rax, rbx
    setge al
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CMP_LE 
    pop rbx
    pop rax
    cmp rax, rbx
    setle al
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
    # JUMP_IF_FALSE if_end0
    pop rax
    test rax, rax
    jz .LcheckLeftPaddleCollision_if_end0
    # .line 68 "return Ball(b.x - 12, b.y, b.radius, 0 - b.velX, b.velY)"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 12
    mov rax, 12
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 32], rax
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 35
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # LABEL if_end0
.LcheckRightPaddleCollision_if_end0:
    # .line 70 "return b"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # RETURN 
    pop rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
.LcheckRightPaddleCollision_skip_labels:
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
    jz .Lruntime_init_aligned_5
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_5
.Lruntime_init_aligned_5: 
    call runtime_init
.Lruntime_init_done_5: 
    lea rdi, [.STR5]  # filename
    lea rsi, [.STR6]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_6
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_6
.Lruntime_set_source_info_aligned_6: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_6: 
    # .local ball struct:Ball
    # .local ballColor struct:Color
    # .local bgColor struct:Color
    # .local leftPaddle struct:Paddle
    # .local leftScore i64
    # .local paddleColor struct:Color
    # .local rightPaddle struct:Paddle
    # .local rightScore i64
    # .local textColor struct:Color
    # .line 74 "InitWindow(1200, 600, \"Pong\")"
    # CONST_I64 1200
    mov rax, 1200
    push rax
    # CONST_I64 600
    mov rax, 600
    push rax
    # CONST_STR "Pong"
    lea rax, [.STR0]
    push rax
    # CALL InitWindow 3 iii|v
    pop rdx
    pop rsi
    pop rdi
    call InitWindow
    push rax
    # .line 75 "SetTargetFPS(60)"
    # CONST_I64 60
    mov rax, 60
    push rax
    # CALL SetTargetFPS 1 i|v
    pop rdi
    call SetTargetFPS
    push rax
    # .line 77 "Color bgColor = Color(0, 0, 50, 255)"
    # CONST_I64 0
    mov rax, 0
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # CONST_I64 50
    mov rax, 50
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 4
    push rax
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 78 "Color paddleColor = Color(0, 255, 0, 255)"
    # CONST_I64 0
    mov rax, 0
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 0
    mov rax, 0
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 4
    push rax
    # STORE 5
    pop rax
    mov [rbp - 48], rax
    # .line 79 "Color ballColor = Color(255, 255, 100, 255)"
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 100
    mov rax, 100
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 4
    push rax
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 80 "Color textColor = Color(255, 255, 255, 255)"
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 4
    push rax
    # STORE 8
    pop rax
    mov [rbp - 72], rax
    # .line 82 "Paddle leftPaddle = createPaddle(30, 250)"
    # CONST_I64 30
    mov rax, 30
    push rax
    # CONST_I64 250
    mov rax, 250
    push rax
    # CALL createPaddle 2
    pop rsi
    pop rdi
    call createPaddle
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 83 "Paddle rightPaddle = createPaddle(1160, 250)"
    # CONST_I64 1160
    mov rax, 1160
    push rax
    # CONST_I64 250
    mov rax, 250
    push rax
    # CALL createPaddle 2
    pop rsi
    pop rdi
    call createPaddle
    push rax
    # STORE 6
    pop rax
    mov [rbp - 56], rax
    # .line 84 "Ball ball = createBall(600, 300)"
    # CONST_I64 600
    mov rax, 600
    push rax
    # CONST_I64 300
    mov rax, 300
    push rax
    # CALL createBall 2
    pop rsi
    pop rdi
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 86 "int leftScore = 0"
    # CONST_I64 0
    mov rax, 0
    push rax
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 87 "int rightScore = 0"
    # CONST_I64 0
    mov rax, 0
    push rax
    # STORE 7
    pop rax
    mov [rbp - 64], rax
    # .line 89 "while (!WindowShouldClose()) {"
    # LABEL while_start0
.Lmain_while_start0:
    # CALL WindowShouldClose 0 |i
    call WindowShouldClose
    push rax
    # NOT 
    pop rax
    test rax, rax
    setz al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE while_end1
    pop rax
    test rax, rax
    jz .Lmain_while_end1
    # .line 90 "leftPaddle = updatePaddle(leftPaddle, 87, 83)"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CONST_I64 87
    mov rax, 87
    push rax
    # CONST_I64 83
    mov rax, 83
    push rax
    # CALL updatePaddle 3
    pop rdx
    pop rsi
    pop rdi
    call updatePaddle
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 91 "rightPaddle = updatePaddle(rightPaddle, 265, 264)"
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # CONST_I64 265
    mov rax, 265
    push rax
    # CONST_I64 264
    mov rax, 264
    push rax
    # CALL updatePaddle 3
    pop rdx
    pop rsi
    pop rdi
    call updatePaddle
    push rax
    # STORE 6
    pop rax
    mov [rbp - 56], rax
    # .line 92 "ball = updateBall(ball)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CALL updateBall 1
    pop rdi
    call updateBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 94 "ball = checkLeftPaddleCollision(ball, leftPaddle)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CALL checkLeftPaddleCollision 2
    pop rsi
    pop rdi
    call checkLeftPaddleCollision
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 95 "ball = checkRightPaddleCollision(ball, rightPaddle)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # CALL checkRightPaddleCollision 2
    pop rsi
    pop rdi
    call checkRightPaddleCollision
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 97 "if (ball.x < ball.radius+2) {"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 2
    mov rax, 2
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # CMP_LT 
    pop rbx
    pop rax
    cmp rax, rbx
    setl al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end2
    pop rax
    test rax, rax
    jz .LupdateBall_if_end2
    # .line 98 "rightScore = rightScore + 1"
    # LOAD 7
    mov rax, [rbp - 64]
    push rax
    # CONST_I64 1
    mov rax, 1
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # STORE 7
    pop rax
    mov [rbp - 64], rax
    # .line 99 "ball = createBall(600, 300)"
    # CONST_I64 600
    mov rax, 600
    push rax
    # CONST_I64 300
    mov rax, 300
    push rax
    # CALL createBall 2
    pop rsi
    pop rdi
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # LABEL if_end2
.Lmain_if_end2:
    # .line 101 "if (ball.x > 1200 - ball.radius-2) {"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 1200
    mov rax, 1200
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # CONST_I64 2
    mov rax, 2
    push rax
    # SUB_I64 
    pop rbx
    pop rax
    sub rax, rbx
    push rax
    # CMP_GT 
    pop rbx
    pop rax
    cmp rax, rbx
    setg al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end4
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end4
    # .line 102 "leftScore = leftScore + 1"
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # CONST_I64 1
    mov rax, 1
    push rax
    # ADD_I64 
    pop rbx
    pop rax
    add rax, rbx
    push rax
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 103 "ball = createBall(600, 300)"
    # CONST_I64 600
    mov rax, 600
    push rax
    # CONST_I64 300
    mov rax, 300
    push rax
    # CALL createBall 2
    pop rsi
    pop rdi
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # LABEL if_end4
.Lmain_if_end4:
    # .line 106 "BeginDrawing()"
    # CALL BeginDrawing 0 |v
    call BeginDrawing
    push rax
    # .line 107 "ClearBackground(bgColor)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CALL ClearBackground 1 s|v
    pop rdi
    call ClearBackground
    push rax
    # .line 109 "DrawRectangle(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height, paddleColor)"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 5
    mov rax, [rbp - 48]
    push rax
    # CALL DrawRectangle 5 iiiis|v
    pop r8
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawRectangle
    push rax
    # .line 110 "DrawRectangle(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height, paddleColor)"
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 5
    mov rax, [rbp - 48]
    push rax
    # CALL DrawRectangle 5 iiiis|v
    pop r8
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawRectangle
    push rax
    # .line 112 "DrawCircle(ball.x, ball.y, ball.radius, Color(255, 255, 255, 255))"
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
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
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # CONST_I64 255
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    mov [rax], rcx  # increment counter
    mov rcx, rbx
    mov rdx, 256
    imul rcx, rdx  # rcx = instance_id * 256
    pop rax  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 24], rax
    pop rax  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 16], rax
    pop rax  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 8], rax
    pop rax  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rcx + 0], rax
    mov rax, rbx
    shl rax, 16
    or rax, 4
    push rax
    # CALL DrawCircle 4 iifs|v
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawCircle
    push rax
    # .line 114 "DrawText(\"Pong Game\", 450, 20, 40, textColor)"
    # CONST_STR "Pong Game"
    lea rax, [.STR1]
    push rax
    # CONST_I64 450
    mov rax, 450
    push rax
    # CONST_I64 20
    mov rax, 20
    push rax
    # CONST_I64 40
    mov rax, 40
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    pop r8
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawText
    push rax
    # .line 115 "DrawText(f\"Left: {leftScore}\", 100, 50, 30, textColor)"
    # CONST_STR "Left: "
    lea rax, [.STR2]
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
    jz .Lruntime_int_to_str_aligned_0
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_0
.Lruntime_int_to_str_aligned_0: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_0: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_1
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_1
.Lruntime_str_concat_checked_aligned_1: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_1: 
    push rax
    # CONST_I64 100
    mov rax, 100
    push rax
    # CONST_I64 50
    mov rax, 50
    push rax
    # CONST_I64 30
    mov rax, 30
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    pop r8
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawText
    push rax
    # .line 116 "DrawText(f\"Right: {rightScore}\", 1000, 50, 30, textColor)"
    # CONST_STR "Right: "
    lea rax, [.STR3]
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
    jz .Lruntime_int_to_str_aligned_2
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_2
.Lruntime_int_to_str_aligned_2: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_2: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_3
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_3
.Lruntime_str_concat_checked_aligned_3: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_3: 
    push rax
    # CONST_I64 1000
    mov rax, 1000
    push rax
    # CONST_I64 50
    mov rax, 50
    push rax
    # CONST_I64 30
    mov rax, 30
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    pop r8
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    call DrawText
    push rax
    # .line 118 "EndDrawing()"
    # CALL EndDrawing 0 |v
    call EndDrawing
    push rax
    # JUMP while_start0
    jmp .Lmain_while_start0
    # LABEL while_end1
.Lmain_while_end1:
    # .line 121 "CloseWindow()"
    # CALL CloseWindow 0 |v
    call CloseWindow
    push rax
    # .line 122 "println(\"Thanks for playing Pong in Fr!\")"
    # CONST_STR "Thanks for playing Pong in Fr!"
    lea rax, [.STR4]
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
    .asciz "Pong"
.STR1:
    .asciz "Pong Game"
.STR2:
    .asciz "Left: "
.STR3:
    .asciz "Right: "
.STR4:
    .asciz "Thanks for playing Pong in Fr!"
.STR5:
    .asciz "pong.fr"
.STR6:
    .asciz "



















return Paddle(startX, startY, 20, 120, 12)



return Ball(startX, startY, 20, 8, 6)



int newY = p.y
if (IsKeyDown(upKey)) {
newY = p.y - p.speed

if (IsKeyDown(downKey)) {
newY = p.y + p.speed

if (newY < 0) {
newY = 0

if (newY + p.height > 600) {
newY = 600 - p.height

return Paddle(p.x, newY, p.width, p.height, p.speed)



int newX = int(b.x + b.velX)
int newY = int(b.y + b.velY)

if (newY < b.radius) {
newY = b.radius

if (newY > 600 - b.radius) {
newY = 600 - b.radius


return Ball(newX, newY, b.radius, b.velX, b.velY)



if (b.x - b.radius <= p.x + p.width && b.x >= p.x && b.y >= p.y && b.y <= p.y + p.height) {
return Ball(b.x + 12, b.y, b.radius, 0 - b.velX, b.velY)

return b



if (b.x + b.radius >= p.x && b.x <= p.x + p.width && b.y >= p.y && b.y <= p.y + p.height) {
return Ball(b.x - 12, b.y, b.radius, 0 - b.velX, b.velY)

return b



InitWindow(1200, 600, \"Pong\")
SetTargetFPS(60)

Color bgColor = Color(0, 0, 50, 255)
Color paddleColor = Color(0, 255, 0, 255)
Color ballColor = Color(255, 255, 100, 255)
Color textColor = Color(255, 255, 255, 255)

Paddle leftPaddle = createPaddle(30, 250)
Paddle rightPaddle = createPaddle(1160, 250)
Ball ball = createBall(600, 300)

int leftScore = 0
int rightScore = 0

while (!WindowShouldClose()) {
leftPaddle = updatePaddle(leftPaddle, 87, 83)
rightPaddle = updatePaddle(rightPaddle, 265, 264)
ball = updateBall(ball)

ball = checkLeftPaddleCollision(ball, leftPaddle)
ball = checkRightPaddleCollision(ball, rightPaddle)

if (ball.x < ball.radius+2) {
rightScore = rightScore + 1
ball = createBall(600, 300)

if (ball.x > 1200 - ball.radius-2) {
leftScore = leftScore + 1
ball = createBall(600, 300)


BeginDrawing()
ClearBackground(bgColor)

DrawRectangle(leftPaddle.x, leftPaddle.y, leftPaddle.width, leftPaddle.height, paddleColor)
DrawRectangle(rightPaddle.x, rightPaddle.y, rightPaddle.width, rightPaddle.height, paddleColor)

DrawCircle(ball.x, ball.y, ball.radius, Color(255, 255, 255, 255))

\"DrawText(\"Pong
\"DrawText(f\"Left:
\"DrawText(f\"Right:

EndDrawing()


CloseWindow()
\"println(\"Thanks"

.section .bss
global_vars:
    .space 2048  # Space for 256 global variables (8 bytes each)
struct_counter:
    .quad 0  # Counter for dynamic struct allocation
struct_data:
    .space 65536  # Space for struct instances (256 instances * 256 bytes each)
