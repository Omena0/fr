.global syscall1, syscall3, syscall6
.type syscall1,@function
syscall1:
    movq %rdi, %rax
    movq %rsi, %rdi
    syscall
    ret
.size syscall1, .-syscall1

.type syscall3,@function
syscall3:
    movq %rdi, %rax
    movq %rsi, %rdi
    movq %rdx, %rsi
    movq %rcx, %rdx
    syscall
    ret
.size syscall3, .-syscall3

.type syscall6,@function
syscall6:
    movq %rdi, %rax
    movq %rsi, %rdi
    movq %rdx, %rsi
    movq %rcx, %rdx
    movq %r8, %r10
    movq %r9, %r8
    movq 8(%rsp), %r9
    syscall
    ret
.size syscall6, .-syscall6
