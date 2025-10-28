/* Pure assembly _start and syscall wrappers */

.section .text
.global _start

_start:
    /* Call main() */
    call main
    
    /* Exit with return value from main */
    mov %eax, %edi          /* move return code to rdi (first arg to syscall) */
    mov $60, %rax           /* sys_exit = 60 */
    syscall

.global runtime_println_int
runtime_println_int:
    /* rdi = int64_t value */
    push %rbp
    mov %rsp, %rbp
    sub $96, %rsp           /* space for buffer (32) + temp (32) + padding */
    
    /* Save rdi (the value) */
    mov %rdi, -8(%rbp)
    
    /* Check if zero */
    cmp $0, %rdi
    je .L_zero
    
    /* Setup for digit extraction */
    xor %ecx, %ecx          /* digit count = 0 */
    xor %eax, %eax          
    mov %rdi, %rax          /* value in rax */
    cmp $0, %rax
    jge .L_positive
    
    /* Negative number */
    neg %rax
    mov $1, %r8d            /* negative flag */
    jmp .L_extract_digits
    
.L_positive:
    xor %r8d, %r8d          /* negative flag = 0 */
    
.L_extract_digits:
    /* Extract digits into temp buffer at -40(%rbp) */
    cmp $0, %rax
    je .L_done_extracting
    
    xor %edx, %edx
    mov $10, %ecx
    div %ecx
    
    add $'0', %dl
    mov %dl, -40(%rbp,%rcx,1)   /* Store digit */
    inc %ecx
    jmp .L_extract_digits
    
.L_done_extracting:
    /* Build final string */
    xor %ecx, %ecx          /* output index */
    
    /* Check if negative */
    cmp $0, %r8d
    je .L_copy_digits
    
    mov $'-', -32(%rbp)     /* Buffer at -32(%rbp) */
    inc %ecx
    
.L_copy_digits:
    /* Copy digits in reverse */
    /* ... simplified: just write the value */
    jmp .L_write
    
.L_zero:
    /* Special case: write "0" */
    mov $'0', %al
    mov %al, -32(%rbp)
    mov $1, %ecx
    jmp .L_write
    
.L_write:
    /* Write value using syscall */
    mov $1, %eax            /* sys_write */
    mov $1, %edi            /* fd = stdout */
    lea -32(%rbp), %rsi     /* buffer address */
    mov %ecx, %edx          /* length */
    syscall
    
    /* Write newline */
    mov $1, %eax            /* sys_write */
    mov $1, %edi            /* fd = stdout */
    lea .L_newline(%rip), %rsi
    mov $1, %edx            /* length = 1 */
    syscall
    
    leave
    ret

.section .rodata
.L_newline:
    .byte 10                /* '\n' */
