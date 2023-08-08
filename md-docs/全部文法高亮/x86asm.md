
# x86asm
## [1.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/1.asm)

```x86asm
0x000000000040145c <+0>:     sub    $0x18,%rsp
0x0000000000401460 <+4>:     mov    %rsi,%rdx                        # rdx = rsp
0x0000000000401463 <+7>:     lea    0x4(%rsi),%rcx                   # rcx = rsp + 4
0x0000000000401467 <+11>:    lea    0x14(%rsi),%rax                  # rax = rsp + 20
0x000000000040146b <+15>:    mov    %rax,0x8(%rsp)                   # (rsp+8) = rsp + 20
0x0000000000401470 <+20>:    lea    0x10(%rsi),%rax                  # rax = rsp + 16
0x0000000000401474 <+24>:    mov    %rax,(%rsp)                      # (rsp) = rsp + 16
0x0000000000401478 <+28>:    lea    0xc(%rsi),%r9                    # r9 = rsi + 12
0x000000000040147c <+32>:    lea    0x8(%rsi),%r8                    # r8 = rsi + 8
0x0000000000401480 <+36>:    mov    $0x4025c3,%esi                   # esi = 0x4025c3
0x0000000000401485 <+41>:    mov    $0x0,%eax                        # eax = 0
0x000000000040148a <+46>:    call   0x400bf0 <__isoc99_sscanf@plt>   # 调用sccanf函数
0x000000000040148f <+51>:    cmp    $0x5,%eax                        # 返回值应该大于5,即至少读取六个
0x0000000000401492 <+54>:    jg     0x401499 <read_six_numbers+61>
0x0000000000401494 <+56>:    call   0x40143a <explode_bomb>
0x0000000000401499 <+61>:    add    $0x18,%rsp
0x000000000040149d <+65>:    ret
```
## [2.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/2.asm)

```x86asm
 0x0000000000400f0a <+14>:    cmpl   $0x1,(%rsp)             # 第一个输入的整数(number[0])应该为 1
 0x0000000000400f0e <+18>:    je     0x400f30 <phase_2+52>
 0x0000000000400f10 <+20>:    call   0x40143a <explode_bomb>
 0x0000000000400f15 <+25>:    jmp    0x400f30 <phase_2+52>
 0x0000000000400f17 <+27>:    mov    -0x4(%rbx),%eax         # eax = (rbx-4)=(rsp)=number[0]
 0x0000000000400f1a <+30>:    add    %eax,%eax               # eax = 2*number[0]
 0x0000000000400f1c <+32>:    cmp    %eax,(%rbx)             # (rbx) = eax, 即 (rsp+4)=number[1]=eax=2*number[0]
 0x0000000000400f1e <+34>:    je     0x400f25 <phase_2+41>
 0x0000000000400f20 <+36>:    call   0x40143a <explode_bomb>
 0x0000000000400f25 <+41>:    add    $0x4,%rbx               # rbx += 4,开始循环
 0x0000000000400f29 <+45>:    cmp    %rbp,%rbx               # 判断是否越界,越界则结束
 0x0000000000400f2c <+48>:    jne    0x400f17 <phase_2+27>
 0x0000000000400f2e <+50>:    jmp    0x400f3c <phase_2+64>
 0x0000000000400f30 <+52>:    lea    0x4(%rsp),%rbx          # rbx = rsp+4 (number[1])
 0x0000000000400f35 <+57>:    lea    0x18(%rsp),%rbp         # rbp = rsp+0x18 (0x18=24,相当于数组的边界number[6])
 0x0000000000400f3a <+62>:    jmp    0x400f17 <phase_2+27>
 0x0000000000400f3c <+64>:    add    $0x28,%rsp
 0x0000000000400f40 <+68>:    pop    %rbx
 0x0000000000400f41 <+69>:    pop    %rbp
 0x0000000000400f42 <+70>:    ret
```
## [3.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/3.asm)

```x86asm
0x0000000000400f60 <+29>:    cmp    $0x1,%eax               # 获取的值应该大于1
0x0000000000400f63 <+32>:    jg     0x400f6a <phase_3+39>
0x0000000000400f65 <+34>:    call   0x40143a <explode_bomb>
0x0000000000400f6a <+39>:    cmpl   $0x7,0x8(%rsp)          # 第一个值应该小于等于7
0x0000000000400f6f <+44>:    ja     0x400fad <phase_3+106>
0x0000000000400f71 <+46>:    mov    0x8(%rsp),%eax          # eax = number[0]
0x0000000000400f75 <+50>:    jmp    *0x402470(,%rax,8)      # 跳转到0x402470+8*number[0]的位置
0x0000000000400f7c <+57>:    mov    $0xcf,%eax
0x0000000000400f81 <+62>:    jmp    0x400fbe <phase_3+123>
0x0000000000400f83 <+64>:    mov    $0x2c3,%eax
0x0000000000400f88 <+69>:    jmp    0x400fbe <phase_3+123>
0x0000000000400f8a <+71>:    mov    $0x100,%eax
0x0000000000400f8f <+76>:    jmp    0x400fbe <phase_3+123>
0x0000000000400f91 <+78>:    mov    $0x185,%eax
0x0000000000400f96 <+83>:    jmp    0x400fbe <phase_3+123>
0x0000000000400f98 <+85>:    mov    $0xce,%eax
0x0000000000400f9d <+90>:    jmp    0x400fbe <phase_3+123>
0x0000000000400f9f <+92>:    mov    $0x2aa,%eax
0x0000000000400fa4 <+97>:    jmp    0x400fbe <phase_3+123>
0x0000000000400fa6 <+99>:    mov    $0x147,%eax
0x0000000000400fab <+104>:   jmp    0x400fbe <phase_3+123>
0x0000000000400fad <+106>:   call   0x40143a <explode_bomb>
0x0000000000400fb2 <+111>:   mov    $0x0,%eax
0x0000000000400fb7 <+116>:   jmp    0x400fbe <phase_3+123>
0x0000000000400fb9 <+118>:   mov    $0x137,%eax
0x0000000000400fbe <+123>:   cmp    0xc(%rsp),%eax          #number[1]应该等于eax
0x0000000000400fc2 <+127>:   je     0x400fc9 <phase_3+134>
0x0000000000400fc4 <+129>:   call   0x40143a <explode_bomb>
0x0000000000400fc9 <+134>:   add    $0x18,%rsp
0x0000000000400fcd <+138>:   ret
```
## [4.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/4.asm)

```x86asm
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

```
## [5.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/5.asm)

```x86asm
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

```
## [6.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/6.asm)

```x86asm
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

```
## [7.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/7.asm)

```x86asm
0x000000000040100c <+0>:     sub    $0x18,%rsp
0x0000000000401010 <+4>:     lea    0xc(%rsp),%rcx                 # number[1]
0x0000000000401015 <+9>:     lea    0x8(%rsp),%rdx                 # number[0]
0x000000000040101a <+14>:    mov    $0x4025cf,%esi                 # %d %d
0x000000000040101f <+19>:    mov    $0x0,%eax
0x0000000000401024 <+24>:    call   0x400bf0 <__isoc99_sscanf@plt>
0x0000000000401029 <+29>:    cmp    $0x2,%eax
0x000000000040102c <+32>:    jne    0x401035 <phase_4+41>
0x000000000040102e <+34>:    cmpl   $0xe,0x8(%rsp)                 # number[0]<=14
0x0000000000401033 <+39>:    jbe    0x40103a <phase_4+46>
0x0000000000401035 <+41>:    call   0x40143a <explode_bomb>
0x000000000040103a <+46>:    mov    $0xe,%edx                      # edx = 14
0x000000000040103f <+51>:    mov    $0x0,%esi                      # esi = 0
0x0000000000401044 <+56>:    mov    0x8(%rsp),%edi                 # edi = number[0]
0x0000000000401048 <+60>:    call   0x400fce <func4>               # 进入func4
0x000000000040104d <+65>:    test   %eax,%eax                      # 返回值应为0
0x000000000040104f <+67>:    jne    0x401058 <phase_4+76>
0x0000000000401051 <+69>:    cmpl   $0x0,0xc(%rsp)                 # number[1]=0
0x0000000000401056 <+74>:    je     0x40105d <phase_4+81>
0x0000000000401058 <+76>:    call   0x40143a <explode_bomb>
0x000000000040105d <+81>:    add    $0x18,%rsp
0x0000000000401061 <+85>:    ret
```
## [8.asm](https://github.com/luzhixing12345/syntaxlight/tree/main/test/x86asm/8.asm)

```x86asm
.section .data
    num1:   .quad 10    # 第一个整数,可以更改为其他值
    num2:   .quad 20    # 第二个整数,可以更改为其他值
    result: .quad 0     # 存储结果的变量,初始化为0

.section .text
    .globl _start

_start:
    # 将第一个整数加载到 %rax 寄存器
    movq num1(%rip), %rax

    # 将第二个整数加载到 %rbx 寄存器
    movq num2(%rip), %rbx

    # 将两个整数相加,并将结果存储在 %rax 寄存器中
    addq %rbx, %rax

    # 将结果存储到 result 变量中
    movq %rax, result(%rip)

    # 在此处可以添加更多的操作,如果需要的话

    # 退出程序
    movq $60, %rax     # 使用系统调用 60 表示退出程序
    xorq %rdi, %rdi    # 退出码为0
    syscall            # 调用系统调用

```
