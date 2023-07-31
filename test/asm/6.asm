# Execution begins at address 0
        .pos 0
        irmovq stack, %rsp      # Set up stack pointer
        call main               # Execute main program
        halt                    # Terminate program
        .align 8
# Source block
src:
        .quad 0x00a
        .quad 0x0b0
        .quad 0xc00
# Destination block
dest:
        .quad 0x111
        .quad 0x222
        .quad 0x333
main:
        irmovq src, %rdi
        irmovq dest, %rsi
        irmovq $3, %rdx
        call copy_block
        ret
# long copy_block(long *src, long *dest, long len)
# start in %rdi, %rsi, %rdx
copy_block:
        irmovq $0, %rax
        irmovq $8, %r8
        irmovq $1, %r9
        andq %rdx, %rdx
        jne loop
        ret
loop:
        mrmovq (%rdi), %r10
        addq %r8, %rsi
        rmmovq %r10, (%rsi)
        addq %r8, %rdi
        xorq %r10, %rax
        subq %r9, %rdx
        jne loop
        ret
# Stack starts here and grows to lower addresses
        .pos 0x200
stack:
