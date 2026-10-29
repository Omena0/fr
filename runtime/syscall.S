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

/* Freestanding setjmp/longjmp used by the native exception machinery. */
.global _setjmp
.type _setjmp,@function
_setjmp:
    movq (%rsp), %rax
    movq %rbx, 0(%rdi)
    movq %rbp, 8(%rdi)
    movq %r12, 16(%rdi)
    movq %r13, 24(%rdi)
    movq %r14, 32(%rdi)
    movq %r15, 40(%rdi)
    leaq 8(%rsp), %rcx
    movq %rcx, 48(%rdi)
    movq %rax, 56(%rdi)
    xorl %eax, %eax
    ret
.size _setjmp, .-_setjmp

.type longjmp,@function
.global longjmp
longjmp:
    movq 0(%rdi), %rbx
    movq 8(%rdi), %rbp
    movq 16(%rdi), %r12
    movq 24(%rdi), %r13
    movq 32(%rdi), %r14
    movq 40(%rdi), %r15
    movq 48(%rdi), %rsp
    movq 56(%rdi), %rdx
    movl %esi, %eax
    testl %eax, %eax
    jne 1f
    movl $1, %eax
1:
    jmp *%rdx
.size longjmp, .-longjmp
