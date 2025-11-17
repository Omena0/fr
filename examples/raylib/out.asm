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
    # .struct 34 5 20 x y width height speed float float int int float
    # .struct 35 5 20 x y radius velX velY float float float float float
    # .struct_type Vector2 0
    # .struct_type Vector3 1
    # .struct_type Vector4 2
    # .struct_type Matrix 3
    # .struct_type Color 4
    # .struct_type Rectangle 5
    # .struct_type Image 6
    # .struct_type Texture 7
    # .struct_type RenderTexture 8
    # .struct_type NPatchInfo 9
    # .struct_type GlyphInfo 10
    # .struct_type Font 11
    # .struct_type Camera3D 12
    # .struct_type Camera2D 13
    # .struct_type Mesh 14
    # .struct_type Shader 15
    # .struct_type MaterialMap 16
    # .struct_type Material 17
    # .struct_type Transform 18
    # .struct_type BoneInfo 19
    # .struct_type Model 20
    # .struct_type ModelAnimation 21
    # .struct_type Ray 22
    # .struct_type RayCollision 23
    # .struct_type BoundingBox 24
    # .struct_type Wave 25
    # .struct_type AudioStream 26
    # .struct_type Sound 27
    # .struct_type Music 28
    # .struct_type VrDeviceInfo 29
    # .struct_type VrStereoConfig 30
    # .struct_type FilePathList 31
    # .struct_type AutomationEvent 32
    # .struct_type AutomationEventList 33
    # .struct_type Paddle 34
    # .struct_type Ball 35
    # .func createPaddle struct:Paddle 2

createPaddle:
    push rbp
    mov rbp, rsp
    sub rsp, 256
    # .arg startX i64
    mov rax, [rbp + 24]
    mov [rbp - 8], rax
    # .arg startY i64
    mov rax, [rbp + 16]
    mov [rbp - 16], rax
    # .local fx f64
    # .local fy f64
    # .line 21 "float fx = float(startX)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 22 "float fy = float(startY)"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 23 "return Paddle(fx, fy, 20, 120, 720.0)"
    # LOAD 2 3
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 32]
    push rax
    # CONST_I64 20 120
    mov rax, 20
    push rax
    mov rax, 120
    push rax
    # CONST_F64 720.0
    movsd xmm0, [.FLOAT0]
    sub rsp, 8
    movsd [rsp], xmm0
    # STRUCT_NEW 34
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_0  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_0:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    mov rax, [rbp + 24]
    mov [rbp - 8], rax
    # .arg startY i64
    mov rax, [rbp + 16]
    mov [rbp - 16], rax
    # .local fx f64
    # .local fy f64
    # .line 27 "float fx = float(startX)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 28 "float fy = float(startY)"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 29 "return Ball(fx, fy, 20.0, -300.0, 100.0)"
    # LOAD 2 3
    mov rax, [rbp - 24]
    push rax
    mov rax, [rbp - 32]
    push rax
    # CONST_F64 20.0 300.0
    movsd xmm0, [.FLOAT1]
    sub rsp, 8
    movsd [rsp], xmm0
    movsd xmm0, [.FLOAT2]
    sub rsp, 8
    movsd [rsp], xmm0
    # NEG 
    movsd xmm0, [rsp]
    mov rax, 0x8000000000000000
    movq xmm1, rax
    xorpd xmm0, xmm1
    movsd [rsp], xmm0
    # CONST_F64 100.0
    movsd xmm0, [.FLOAT3]
    sub rsp, 8
    movsd [rsp], xmm0
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_1  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_1:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    mov rax, [rbp + 32]
    mov [rbp - 8], rax
    # .arg upKey i64
    mov rax, [rbp + 24]
    mov [rbp - 16], rax
    # .arg downKey i64
    mov rax, [rbp + 16]
    mov [rbp - 24], rax
    # .local dt f64
    # .local newY f64
    # .line 33 "float dt = GetFrameTime()"
    # CALL GetFrameTime 0 |f
    # CALL GetFrameTime: struct_args=set(), float_args=set(), stack_types=['f64', 'f64', 'struct:34', 'f64', 'f64', 'struct:35']
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LGetFrameTime_aligned_2
    sub rsp, 8  # Align stack
    call GetFrameTime
    add rsp, 8  # Restore stack
    jmp .LGetFrameTime_done_2
    .LGetFrameTime_aligned_2:
    call GetFrameTime
    .LGetFrameTime_done_2:
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 35 "float newY = p.y"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_3
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_3:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 36 "if (IsKeyDown(upKey)) {"
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CALL IsKeyDown 1 i|b
    # CALL IsKeyDown: struct_args=set(), float_args=set(), stack_types=['i64']
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LIsKeyDown_aligned_4
    sub rsp, 8  # Align stack
    call IsKeyDown
    add rsp, 8  # Restore stack
    jmp .LIsKeyDown_done_4
    .LIsKeyDown_aligned_4:
    call IsKeyDown
    .LIsKeyDown_done_4:
    movzx rax, al  # Zero-extend bool (al) to rax
    push rax
    # JUMP_IF_FALSE if_end0
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end0
    # .line 37 "newY = p.y - p.speed * dt"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_5
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_5:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_6
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_6:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # MUL_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    mulsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # LABEL if_end0
.LupdatePaddle_if_end0:
    # .line 39 "if (IsKeyDown(downKey)) {"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CALL IsKeyDown 1 i|b
    # CALL IsKeyDown: struct_args=set(), float_args=set(), stack_types=['i64']
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LIsKeyDown_aligned_7
    sub rsp, 8  # Align stack
    call IsKeyDown
    add rsp, 8  # Restore stack
    jmp .LIsKeyDown_done_7
    .LIsKeyDown_aligned_7:
    call IsKeyDown
    .LIsKeyDown_done_7:
    movzx rax, al  # Zero-extend bool (al) to rax
    push rax
    # JUMP_IF_FALSE if_end2
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end2
    # .line 40 "newY = p.y + p.speed * dt"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_8
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_8:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_9
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_9:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # MUL_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    mulsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # LABEL if_end2
.LupdatePaddle_if_end2:
    # .line 42 "if (newY < 0) {"
    # LOAD 4
    mov rax, [rbp - 40]
    push rax
    # CMP_LT_CONST 0
    pop rax
    cmp rax, 0
    setl al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end4
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end4
    # .line 43 "newY = 0"
    # STORE_CONST_F64 4 0.0
    movsd xmm0, [.FLOAT4]
    movsd [rbp - 40], xmm0
    # LABEL if_end4
.LupdatePaddle_if_end4:
    # .line 45 "if (newY + p.height > 600) {"
    # LOAD 4 0
    mov rax, [rbp - 40]
    push rax
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_10
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_10:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # CMP_GT_CONST 600
    pop rax
    cmp rax, 600
    setg al
    movzx rax, al
    push rax
    # JUMP_IF_FALSE if_end6
    pop rax
    test rax, rax
    jz .LupdatePaddle_if_end6
    # .line 46 "newY = 600 - p.height"
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
    cmp rbx, 262144
    jb .Linstance_ok_11
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_11:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # LABEL if_end6
.LupdatePaddle_if_end6:
    # .line 48 "return Paddle(p.x, newY, p.width, p.height, p.speed)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_12
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_12:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 4 0
    mov rax, [rbp - 40]
    push rax
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_13
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_13:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_14
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_14:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_15
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_15:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # STRUCT_NEW 34
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_16  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_16:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    mov rax, [rbp + 16]
    mov [rbp - 8], rax
    # .local dt f64
    # .local newVelY f64
    # .local newX f64
    # .local newY f64
    # .line 52 "float dt = GetFrameTime()"
    # CALL GetFrameTime 0 |f
    # CALL GetFrameTime: struct_args=set(), float_args=set(), stack_types=['struct:34']
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LGetFrameTime_aligned_17
    sub rsp, 8  # Align stack
    call GetFrameTime
    add rsp, 8  # Restore stack
    jmp .LGetFrameTime_done_17
    .LGetFrameTime_aligned_17:
    call GetFrameTime
    .LGetFrameTime_done_17:
    push rax
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 54 "float newX = b.x + b.velX * dt"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_18
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_18:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_19
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_19:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # MUL_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    mulsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 55 "float newY = b.y + b.velY * dt"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_20
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_20:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_21
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_21:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # MUL_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    mulsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 56 "float newVelY = b.velY"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_22
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_22:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 58 "if (newY < b.radius) {"
    # LOAD 4 0
    mov rax, [rbp - 40]
    push rax
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_23
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_23:
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
    jz .LupdateBall_if_end0
    # .line 59 "newY = b.radius"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_24
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_24:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 60 "newVelY = 0.0 - newVelY"
    # CONST_F64 0.0
    movsd xmm0, [.FLOAT5]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # LABEL if_end0
.LupdateBall_if_end0:
    # .line 62 "if (newY > 600 - b.radius) {"
    # LOAD 4
    mov rax, [rbp - 40]
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
    cmp rbx, 262144
    jb .Linstance_ok_25
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_25:
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
    jz .LupdateBall_if_end2
    # .line 63 "newY = 600 - b.radius"
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
    cmp rbx, 262144
    jb .Linstance_ok_26
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_26:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # STORE 4
    pop rax
    mov [rbp - 40], rax
    # .line 64 "newVelY = 0.0 - newVelY"
    # CONST_F64 0.0
    movsd xmm0, [.FLOAT6]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # LABEL if_end2
.LupdateBall_if_end2:
    # .line 67 "return Ball(newX, newY, b.radius, b.velX, newVelY)"
    # LOAD 3 4 0
    mov rax, [rbp - 32]
    push rax
    mov rax, [rbp - 40]
    push rax
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_27
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_27:
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
    cmp rbx, 262144
    jb .Linstance_ok_28
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_28:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_29  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_29:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    mov rax, [rbp + 24]
    mov [rbp - 8], rax
    # .arg p struct:Paddle
    mov rax, [rbp + 16]
    mov [rbp - 16], rax
    # .line 71 "if (b.x - b.radius <= p.x + p.width && b.x >= p.x && b.y >= p.y && b.y <= p.y + p.height) {"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_30
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_30:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_31
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_31:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_32
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_32:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_33
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_33:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_34
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_34:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_35
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_35:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_36
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_36:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_37
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_37:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_38
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_38:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_39
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_39:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_40
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_40:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    # .line 72 "return Ball(b.x + 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_41
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_41:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # ADD_CONST_F64 12.0
    movsd xmm0, [.FLOAT7]
    movsd xmm1, [rsp]
    add rsp, 8
    addsd xmm1, xmm0
    sub rsp, 8
    movsd [rsp], xmm1
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_42
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_42:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_43
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_43:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # CONST_F64 0.0
    movsd xmm0, [.FLOAT8]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_44
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_44:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_45
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_45:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_46  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_46:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    # .line 74 "return b"
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
    mov rax, [rbp + 24]
    mov [rbp - 8], rax
    # .arg p struct:Paddle
    mov rax, [rbp + 16]
    mov [rbp - 16], rax
    # .line 78 "if (b.x + b.radius >= p.x && b.x <= p.x + p.width && b.y >= p.y && b.y <= p.y + p.height) {"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_47
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_47:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_48
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_48:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_49
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_49:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_50
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_50:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_51
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_51:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_52
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_52:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_53
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_53:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_54
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_54:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    cmp rbx, 262144
    jb .Linstance_ok_55
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_55:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_56
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_56:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_57
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_57:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
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
    jz .LcheckRightPaddleCollision_if_end0
    # .line 79 "return Ball(b.x - 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_58
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_58:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # SUB_CONST_F64 12.0
    movsd xmm0, [.FLOAT9]
    movsd xmm1, [rsp]
    add rsp, 8
    subsd xmm1, xmm0
    sub rsp, 8
    movsd [rsp], xmm1
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_59
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_59:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_60
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_60:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # CONST_F64 0.0
    movsd xmm0, [.FLOAT10]
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 3
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_61
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_61:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 24  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # TO_FLOAT 
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 4
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_62
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_62:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 32  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    movsd xmm0, [rdx + rax]
    sub rsp, 8
    movsd [rsp], xmm0
    # STRUCT_NEW 35
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_63  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_63:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 4
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 32], rbx
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
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
    # .line 81 "return b"
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
    jz .Lruntime_init_aligned_101
    sub rsp, 8
    call runtime_init
    add rsp, 8
    jmp .Lruntime_init_done_101
.Lruntime_init_aligned_101: 
    call runtime_init
.Lruntime_init_done_101: 
    lea rdi, [.STR16]  # filename
    lea rsi, [.STR17]  # source
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_set_source_info_aligned_102
    sub rsp, 8
    call runtime_set_source_info
    add rsp, 8
    jmp .Lruntime_set_source_info_done_102
.Lruntime_set_source_info_aligned_102: 
    call runtime_set_source_info
.Lruntime_set_source_info_done_102: 
    # .local ball struct:Ball
    # .local ballColor struct:Color
    # .local bgColor struct:Color
    # .local leftPaddle struct:Paddle
    # .local leftScore i64
    # .local paddleColor struct:Color
    # .local rightPaddle struct:Paddle
    # .local rightScore i64
    # .local textColor struct:Color
    # .line 85 "InitWindow(1200, 600, \"Pong\")"
    # CONST_I64 1200 600
    mov rax, 1200
    push rax
    mov rax, 600
    push rax
    # CONST_STR "Pong"
    lea rax, [.STR11]
    push rax
    # CALL InitWindow 3 iii|v
    # CALL InitWindow: struct_args=set(), float_args=set(), stack_types=['i64', 'i64', 'str']
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LInitWindow_aligned_64
    sub rsp, 8  # Align stack
    call InitWindow
    add rsp, 8  # Restore stack
    jmp .LInitWindow_done_64
    .LInitWindow_aligned_64:
    call InitWindow
    .LInitWindow_done_64:
    # .line 86 "SetTargetFPS(60)"
    # CONST_I64 60
    mov rax, 60
    push rax
    # CALL SetTargetFPS 1 i|v
    # CALL SetTargetFPS: struct_args=set(), float_args=set(), stack_types=['i64']
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LSetTargetFPS_aligned_65
    sub rsp, 8  # Align stack
    call SetTargetFPS
    add rsp, 8  # Restore stack
    jmp .LSetTargetFPS_done_65
    .LSetTargetFPS_aligned_65:
    call SetTargetFPS
    .LSetTargetFPS_done_65:
    # .line 88 "Color bgColor = Color(0, 0, 50, 255)"
    # CONST_I64 0 0 50 255
    mov rax, 0
    push rax
    mov rax, 0
    push rax
    mov rax, 50
    push rax
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_66  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_66:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
    shl rax, 16
    or rax, 4
    push rax
    # STORE 2
    pop rax
    mov [rbp - 24], rax
    # .line 89 "Color paddleColor = Color(0, 255, 0, 255)"
    # CONST_I64 0 255 0 255
    mov rax, 0
    push rax
    mov rax, 255
    push rax
    mov rax, 0
    push rax
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_67  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_67:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
    shl rax, 16
    or rax, 4
    push rax
    # STORE 5
    pop rax
    mov [rbp - 48], rax
    # .line 90 "Color ballColor = Color(255, 255, 100, 255)"
    # CONST_I64 255 255 100 255
    mov rax, 255
    push rax
    mov rax, 255
    push rax
    mov rax, 100
    push rax
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_68  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_68:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
    shl rax, 16
    or rax, 4
    push rax
    # STORE 1
    pop rax
    mov [rbp - 16], rax
    # .line 91 "Color textColor = Color(255, 255, 255, 255)"
    # CONST_I64 255 255 255 255
    mov rax, 255
    push rax
    mov rax, 255
    push rax
    mov rax, 255
    push rax
    mov rax, 255
    push rax
    # STRUCT_NEW 4
    lea rax, [rip + struct_counter]
    mov rbx, [rax]  # rbx = current counter
    mov rcx, rbx
    inc rcx
    cmp rcx, 262144
    jb .Lstruct_no_wrap_69  # Jump if below 262144
    mov rcx, 1024  # Wrap to 1024 to preserve early instances
    .Lstruct_no_wrap_69:
    mov [rax], rcx  # store counter
    mov rax, rcx  # rax = new instance_id after wrap
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    pop rbx  # field 3
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 24], rbx
    pop rbx  # field 2
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 16], rbx
    pop rbx  # field 1
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 8], rbx
    pop rbx  # field 0
    lea rdx, [rip + struct_data]
    mov [rdx + rax + 0], rbx
    mov rax, rcx  # rax = new instance_id
    shl rax, 16
    or rax, 4
    push rax
    # STORE 8
    pop rax
    mov [rbp - 72], rax
    # .line 93 "Paddle leftPaddle = createPaddle(30, 250)"
    # CONST_I64 30 250
    mov rax, 30
    push rax
    mov rax, 250
    push rax
    # CALL createPaddle 2
    # CALL createPaddle: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call createPaddle
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 94 "Paddle rightPaddle = createPaddle(1160, 250)"
    # CONST_I64 1160 250
    mov rax, 1160
    push rax
    mov rax, 250
    push rax
    # CALL createPaddle 2
    # CALL createPaddle: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call createPaddle
    push rax
    # STORE 6
    pop rax
    mov [rbp - 56], rax
    # .line 95 "Ball ball = createBall(600, 300)"
    # CONST_I64 600 300
    mov rax, 600
    push rax
    mov rax, 300
    push rax
    # CALL createBall 2
    # CALL createBall: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 97 "int leftScore = 0"
    # STORE_CONST_I64 4 0
    mov rax, 0
    mov [rbp - 40], rax
    # .line 98 "int rightScore = 0"
    # STORE_CONST_I64 7 0
    mov rax, 0
    mov [rbp - 64], rax
    # .line 100 "while (!WindowShouldClose()) {"
    # LABEL while_start0
.Lmain_while_start0:
    # CALL WindowShouldClose 0 |b
    # CALL WindowShouldClose: struct_args=set(), float_args=set(), stack_types=[]
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LWindowShouldClose_aligned_70
    sub rsp, 8  # Align stack
    call WindowShouldClose
    add rsp, 8  # Restore stack
    jmp .LWindowShouldClose_done_70
    .LWindowShouldClose_aligned_70:
    call WindowShouldClose
    .LWindowShouldClose_done_70:
    movzx rax, al  # Zero-extend bool (al) to rax
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
    # .line 101 "leftPaddle = updatePaddle(leftPaddle, 265, 264)"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # CONST_I64 265 264
    mov rax, 265
    push rax
    mov rax, 264
    push rax
    # CALL updatePaddle 3
    # CALL updatePaddle: struct_args=set(), float_args=set(), stack_types=['i64', 'i64', 'i64']
    call updatePaddle
    push rax
    # STORE 3
    pop rax
    mov [rbp - 32], rax
    # .line 102 "rightPaddle = updatePaddle(rightPaddle, 87, 83)"
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # CONST_I64 87 83
    mov rax, 87
    push rax
    mov rax, 83
    push rax
    # CALL updatePaddle 3
    # CALL updatePaddle: struct_args=set(), float_args=set(), stack_types=['i64', 'i64', 'i64']
    call updatePaddle
    push rax
    # STORE 6
    pop rax
    mov [rbp - 56], rax
    # .line 103 "ball = updateBall(ball)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # CALL updateBall 1
    # CALL updateBall: struct_args=set(), float_args=set(), stack_types=['i64']
    call updateBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 105 "ball = checkLeftPaddleCollision(ball, leftPaddle)"
    # LOAD 0 3
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 32]
    push rax
    # CALL checkLeftPaddleCollision 2
    # CALL checkLeftPaddleCollision: struct_args=set(), float_args=set(), stack_types=['i64', 'bool']
    call checkLeftPaddleCollision
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 106 "ball = checkRightPaddleCollision(ball, rightPaddle)"
    # LOAD 0 6
    mov rax, [rbp - 8]
    push rax
    mov rax, [rbp - 56]
    push rax
    # CALL checkRightPaddleCollision 2
    # CALL checkRightPaddleCollision: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call checkRightPaddleCollision
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # .line 108 "if (ball.x < ball.radius+2) {"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_71
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_71:
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
    cmp rbx, 262144
    jb .Linstance_ok_72
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_72:
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
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # ADD_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    addsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
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
    jz .Lmain_if_end2
    # .line 109 "leftScore = leftScore + 1"
    # INC_LOCAL 4
    inc qword ptr [rbp - 40]
    # .line 110 "ball = createBall(600, 300)"
    # CONST_I64 600 300
    mov rax, 600
    push rax
    mov rax, 300
    push rax
    # CALL createBall 2
    # CALL createBall: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # LABEL if_end2
.Lmain_if_end2:
    # .line 112 "if (ball.x > 1200 - ball.radius-2) {"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_73
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_73:
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
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_74
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_74:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
    # CONST_I64 2
    mov rax, 2
    push rax
    # TO_FLOAT 
    pop rax
    cvtsi2sd xmm0, rax
    sub rsp, 8
    movsd [rsp], xmm0
    # SUB_F64 
    movsd xmm1, [rsp]
    add rsp, 8
    movsd xmm0, [rsp]
    add rsp, 8
    subsd xmm0, xmm1
    sub rsp, 8
    movsd [rsp], xmm0
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
    jz .Lmain_if_end4
    # .line 113 "rightScore = rightScore + 1"
    # INC_LOCAL 7
    inc qword ptr [rbp - 64]
    # .line 114 "ball = createBall(600, 300)"
    # CONST_I64 600 300
    mov rax, 600
    push rax
    mov rax, 300
    push rax
    # CALL createBall 2
    # CALL createBall: struct_args=set(), float_args=set(), stack_types=['i64', 'i64']
    call createBall
    push rax
    # STORE 0
    pop rax
    mov [rbp - 8], rax
    # LABEL if_end4
.Lmain_if_end4:
    # .line 117 "BeginDrawing()"
    # CALL BeginDrawing 0 |v
    # CALL BeginDrawing: struct_args=set(), float_args=set(), stack_types=[]
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LBeginDrawing_aligned_75
    sub rsp, 8  # Align stack
    call BeginDrawing
    add rsp, 8  # Restore stack
    jmp .LBeginDrawing_done_75
    .LBeginDrawing_aligned_75:
    call BeginDrawing
    .LBeginDrawing_done_75:
    # .line 118 "ClearBackground(bgColor)"
    # LOAD 2
    mov rax, [rbp - 24]
    push rax
    # CALL ClearBackground 1 s|v
    # CALL ClearBackground: struct_args={0}, float_args=set(), stack_types=['struct:4']
    # Packing struct 4 for arg 0
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor rdi, rdi  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or rdi, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or rdi, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or rdi, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or rdi, rbx
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LClearBackground_aligned_76
    sub rsp, 8  # Align stack
    call ClearBackground
    add rsp, 8  # Restore stack
    jmp .LClearBackground_done_76
    .LClearBackground_aligned_76:
    call ClearBackground
    .LClearBackground_done_76:
    # .line 120 "DrawRectangle(int(leftPaddle.x), int(leftPaddle.y), leftPaddle.width, leftPaddle.height, paddleColor)"
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_77
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_77:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_78
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_78:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 3
    mov rax, [rbp - 32]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_79
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_79:
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
    cmp rbx, 262144
    jb .Linstance_ok_80
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_80:
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
    # CALL DrawRectangle: struct_args={4}, float_args=set(), stack_types=['i64', 'i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 4
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawRectangle_aligned_81
    sub rsp, 8  # Align stack
    call DrawRectangle
    add rsp, 8  # Restore stack
    jmp .LDrawRectangle_done_81
    .LDrawRectangle_aligned_81:
    call DrawRectangle
    .LDrawRectangle_done_81:
    # .line 121 "DrawRectangle(int(rightPaddle.x), int(rightPaddle.y), rightPaddle.width, rightPaddle.height, paddleColor)"
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_82
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_82:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_83
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_83:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 6
    mov rax, [rbp - 56]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_84
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_84:
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
    cmp rbx, 262144
    jb .Linstance_ok_85
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_85:
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
    # CALL DrawRectangle: struct_args={4}, float_args=set(), stack_types=['i64', 'i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 4
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawRectangle_aligned_86
    sub rsp, 8  # Align stack
    call DrawRectangle
    add rsp, 8  # Restore stack
    jmp .LDrawRectangle_done_86
    .LDrawRectangle_aligned_86:
    call DrawRectangle
    .LDrawRectangle_done_86:
    # .line 123 "DrawCircle(int(ball.x), int(ball.y), ball.radius, ballColor)"
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 0
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_87
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_87:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 0  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 1
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_88
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_88:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 8  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # TO_INT 
    # LOAD 0
    mov rax, [rbp - 8]
    push rax
    # STRUCT_GET 2
    pop rax  # struct reference
    mov rbx, rax
    shr rbx, 16  # rbx = instance_id
    mov rcx, rax
    and rcx, 0xFFFF  # rcx = struct_id
    cmp rbx, 262144
    jb .Linstance_ok_89
    and rbx, 0x3FFFF  # Wrap to 0-262143
    .Linstance_ok_89:
    mov rax, rbx
    mov rdx, 256
    imul rax, rdx  # rax = instance_id * 256
    add rax, 16  # rax += field_idx * 8
    lea rdx, [rip + struct_data]
    mov rax, [rdx + rax]
    push rax
    # LOAD 1
    mov rax, [rbp - 16]
    push rax
    # CALL DrawCircle 4 iifs|v
    # CALL DrawCircle: struct_args={3}, float_args={2}, stack_types=['i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 3
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor rdx, rdx  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or rdx, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or rdx, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or rdx, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or rdx, rbx
    # Float arg 2 -> xmm0
    pop rax  # Load value
    cvtsi2ss xmm0, rax  # Convert int64 to float
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawCircle_aligned_90
    sub rsp, 8  # Align stack
    call DrawCircle
    add rsp, 8  # Restore stack
    jmp .LDrawCircle_done_90
    .LDrawCircle_aligned_90:
    call DrawCircle
    .LDrawCircle_done_90:
    # .line 125 "DrawText(\"Pong Game\", 450, 20, 40, textColor)"
    # CONST_STR "Pong Game"
    lea rax, [.STR12]
    push rax
    # CONST_I64 450 20 40
    mov rax, 450
    push rax
    mov rax, 20
    push rax
    mov rax, 40
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    # CALL DrawText: struct_args={4}, float_args=set(), stack_types=['str', 'i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 4
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawText_aligned_91
    sub rsp, 8  # Align stack
    call DrawText
    add rsp, 8  # Restore stack
    jmp .LDrawText_done_91
    .LDrawText_aligned_91:
    call DrawText
    .LDrawText_done_91:
    # .line 126 "DrawText(f\"Left: {leftScore}\", 100, 50, 30, textColor)"
    # CONST_STR "Left: "
    lea rax, [.STR13]
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
    jz .Lruntime_int_to_str_aligned_92
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_92
.Lruntime_int_to_str_aligned_92: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_92: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_93
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_93
.Lruntime_str_concat_checked_aligned_93: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_93: 
    push rax
    # CONST_I64 100 50 30
    mov rax, 100
    push rax
    mov rax, 50
    push rax
    mov rax, 30
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    # CALL DrawText: struct_args={4}, float_args=set(), stack_types=['str', 'i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 4
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawText_aligned_94
    sub rsp, 8  # Align stack
    call DrawText
    add rsp, 8  # Restore stack
    jmp .LDrawText_done_94
    .LDrawText_aligned_94:
    call DrawText
    .LDrawText_done_94:
    # .line 127 "DrawText(f\"Right: {rightScore}\", 1000, 50, 30, textColor)"
    # CONST_STR "Right: "
    lea rax, [.STR14]
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
    jz .Lruntime_int_to_str_aligned_95
    sub rsp, 8
    call runtime_int_to_str
    add rsp, 8
    jmp .Lruntime_int_to_str_done_95
.Lruntime_int_to_str_aligned_95: 
    call runtime_int_to_str
.Lruntime_int_to_str_done_95: 
    push rax
    # ADD_STR 
    pop rsi
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_str_concat_checked_aligned_96
    sub rsp, 8
    call runtime_str_concat_checked
    add rsp, 8
    jmp .Lruntime_str_concat_checked_done_96
.Lruntime_str_concat_checked_aligned_96: 
    call runtime_str_concat_checked
.Lruntime_str_concat_checked_done_96: 
    push rax
    # CONST_I64 1000 50 30
    mov rax, 1000
    push rax
    mov rax, 50
    push rax
    mov rax, 30
    push rax
    # LOAD 8
    mov rax, [rbp - 72]
    push rax
    # CALL DrawText 5 iiiis|v
    # CALL DrawText: struct_args={4}, float_args=set(), stack_types=['str', 'i64', 'i64', 'i64', 'struct:4']
    # Packing struct 4 for arg 4
    pop rax
    shr rax, 16
    and rax, 0x3FFF  # Ensure instance_id < 16384
    mov rbx, 256
    imul rax, rbx
    lea r10, [rip + struct_data]
    xor r8, r8  # Clear target
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 0]  # R
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 8]  # G
    shl rbx, 8
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 16]  # B
    shl rbx, 16
    or r8, rbx
    xor rbx, rbx  # Clear rbx
    mov bl, byte ptr [r10 + rax + 24]  # A
    shl rbx, 24
    or r8, rbx
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LDrawText_aligned_97
    sub rsp, 8  # Align stack
    call DrawText
    add rsp, 8  # Restore stack
    jmp .LDrawText_done_97
    .LDrawText_aligned_97:
    call DrawText
    .LDrawText_done_97:
    # .line 129 "EndDrawing()"
    # CALL EndDrawing 0 |v
    # CALL EndDrawing: struct_args=set(), float_args=set(), stack_types=['i64', 'i64', 'i64', 'i64', 'i64', 'i64']
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LEndDrawing_aligned_98
    sub rsp, 8  # Align stack
    call EndDrawing
    add rsp, 8  # Restore stack
    jmp .LEndDrawing_done_98
    .LEndDrawing_aligned_98:
    call EndDrawing
    .LEndDrawing_done_98:
    # JUMP while_start0
    jmp .Lmain_while_start0
    # LABEL while_end1
.Lmain_while_end1:
    # .line 132 "CloseWindow()"
    # CALL CloseWindow 0 |v
    # CALL CloseWindow: struct_args=set(), float_args=set(), stack_types=[]
    # Stack alignment for external call
    mov r11, rsp
    and r11, 0xF
    jz .LCloseWindow_aligned_99
    sub rsp, 8  # Align stack
    call CloseWindow
    add rsp, 8  # Restore stack
    jmp .LCloseWindow_done_99
    .LCloseWindow_aligned_99:
    call CloseWindow
    .LCloseWindow_done_99:
    # .line 133 "println(\"Thanks for playing Pong in Fr!\")"
    # CONST_STR "Thanks for playing Pong in Fr!"
    lea rax, [.STR15]
    push rax
    # BUILTIN_PRINTLN 
    pop rdi
    push rax  # Save rax and check alignment
    mov rax, rsp
    add rax, 8  # Account for the push
    test rax, 0xF
    pop rax
    jz .Lruntime_println_str_aligned_100
    sub rsp, 8
    call runtime_println_str
    add rsp, 8
    jmp .Lruntime_println_str_done_100
.Lruntime_println_str_aligned_100: 
    call runtime_println_str
.Lruntime_println_str_done_100: 
    # RETURN_VOID 
.Lmain_skip_labels:
    xor rax, rax
    mov rsp, rbp
    pop rbp
    ret
    # .end 
    # .entry main

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
    .double 0.0
.FLOAT7:
    .double 12.0
.FLOAT8:
    .double 0.0
.FLOAT9:
    .double 12.0
.FLOAT10:
    .double 0.0
.STR11:
    .asciz "Pong"
.STR12:
    .asciz "Pong Game"
.STR13:
    .asciz "Left: "
.STR14:
    .asciz "Right: "
.STR15:
    .asciz "Thanks for playing Pong in Fr!"
.STR16:
    .asciz "pong.fr"
.STR17:
    .asciz "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nfloat fx = float(startX)\nfloat fy = float(startY)\nreturn Paddle(fx, fy, 20, 120, 720.0)\n\n\n\nfloat fx = float(startX)\nfloat fy = float(startY)\nreturn Ball(fx, fy, 20.0, -300.0, 100.0)\n\n\n\nfloat dt = GetFrameTime()\n\nfloat newY = p.y\nif (IsKeyDown(upKey)) {\nnewY = p.y - p.speed * dt\n\nif (IsKeyDown(downKey)) {\nnewY = p.y + p.speed * dt\n\nif (newY < 0) {\nnewY = 0\n\nif (newY + p.height > 600) {\nnewY = 600 - p.height\n\nreturn Paddle(p.x, newY, p.width, p.height, p.speed)\n\n\n\nfloat dt = GetFrameTime()\n\nfloat newX = b.x + b.velX * dt\nfloat newY = b.y + b.velY * dt\nfloat newVelY = b.velY\n\nif (newY < b.radius) {\nnewY = b.radius\nnewVelY = 0.0 - newVelY\n\nif (newY > 600 - b.radius) {\nnewY = 600 - b.radius\nnewVelY = 0.0 - newVelY\n\n\nreturn Ball(newX, newY, b.radius, b.velX, newVelY)\n\n\n\nif (b.x - b.radius <= p.x + p.width && b.x >= p.x && b.y >= p.y && b.y <= p.y + p.height) {\nreturn Ball(b.x + 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)\n\nreturn b\n\n\n\nif (b.x + b.radius >= p.x && b.x <= p.x + p.width && b.y >= p.y && b.y <= p.y + p.height) {\nreturn Ball(b.x - 12.0, b.y, b.radius, 0.0 - b.velX, b.velY)\n\nreturn b\n\n\n\nInitWindow(1200, 600, \"Pong\")\nSetTargetFPS(60)\n\nColor bgColor = Color(0, 0, 50, 255)\nColor paddleColor = Color(0, 255, 0, 255)\nColor ballColor = Color(255, 255, 100, 255)\nColor textColor = Color(255, 255, 255, 255)\n\nPaddle leftPaddle = createPaddle(30, 250)\nPaddle rightPaddle = createPaddle(1160, 250)\nBall ball = createBall(600, 300)\n\nint leftScore = 0\nint rightScore = 0\n\nwhile (!WindowShouldClose()) {\nleftPaddle = updatePaddle(leftPaddle, 265, 264)\nrightPaddle = updatePaddle(rightPaddle, 87, 83)\nball = updateBall(ball)\n\nball = checkLeftPaddleCollision(ball, leftPaddle)\nball = checkRightPaddleCollision(ball, rightPaddle)\n\nif (ball.x < ball.radius+2) {\nleftScore = leftScore + 1\nball = createBall(600, 300)\n\nif (ball.x > 1200 - ball.radius-2) {\nrightScore = rightScore + 1\nball = createBall(600, 300)\n\n\nBeginDrawing()\nClearBackground(bgColor)\n\nDrawRectangle(int(leftPaddle.x), int(leftPaddle.y), leftPaddle.width, leftPaddle.height, paddleColor)\nDrawRectangle(int(rightPaddle.x), int(rightPaddle.y), rightPaddle.width, rightPaddle.height, paddleColor)\n\nDrawCircle(int(ball.x), int(ball.y), ball.radius, ballColor)\n\n\"DrawText(\"Pong\n\"DrawText(f\"Left:\n\"DrawText(f\"Right:\n\nEndDrawing()\n\n\nCloseWindow()\n\"println(\"Thanks"

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
