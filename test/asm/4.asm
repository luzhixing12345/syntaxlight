# Execution begins at address 0
        .pos 0
        irmovq stack, %rsp      # Set up stack pointer
        call main               # Execute main program
        halt                    # Terminate program
# Sample linked list
        .align 8
ele1:
        .quad 0x00a
        .quad ele2
ele2:
        .quad 0x0b0
        .quad ele3
ele3:
        .quad 0xc00
        .quad 0
main:
        irmovq ele1,%rdi
        call sum_list
        ret
# long sum_list(list_ptr ls)
# start in %rdi
sum_list:
        irmovq $0, %rax
        jmp test
loop:
        mrmovq (%rdi), %rsi
        addq %rsi, %rax
        mrmovq 8(%rdi), %rdi
test:
        andq %rdi, %rdi
        jne loop
        ret
# Stack starts here and grows to lower addresses
        .pos 0x200
stack:
