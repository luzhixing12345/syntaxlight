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