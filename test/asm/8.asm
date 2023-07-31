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
