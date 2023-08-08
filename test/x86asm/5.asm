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
        call rsum_list
        ret
# long rsum_list(list_ptr ls)
# start in %rdi
rsum_list:
        andq %rdi, %rdi
        je return               # if(!ls)
        mrmovq (%rdi), %rbx     # val = ls->val
        mrmovq 8(%rdi), %rdi    # ls = ls->next
        pushq %rbx
        call rsum_list          # rsum_list(ls->next)
        popq %rbx
        addq %rbx, %rax         # val + rest
        ret
return:
        irmovq $0, %rax
        ret
# Stack starts here and grows to lower addresses
        .pos 0x200
stack:
