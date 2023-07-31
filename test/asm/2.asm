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