int g(int x) {
   0:   1141                    addi    sp,sp,-16
   2:   e422                    sd  s0,8(sp)
   4:   0800                    addi    s0,sp,16
  return x+3;
}
   6:   250d                    addiw   a0,a0,3
   8:   6422                    ld  s0,8(sp)
   a:   0141                    addi    sp,sp,16
   c:   8082                    ret
000000000000000e <f>:

int f(int x) {
   e:   1141                    addi    sp,sp,-16
  10:   e422                    sd  s0,8(sp)
  12:   0800                    addi    s0,sp,16
  return g(x);
}
  14:   250d                    addiw   a0,a0,3
  16:   6422                    ld  s0,8(sp)
  18:   0141                    addi    sp,sp,16
  1a:   8082                    ret
000000000000001c <main>:

void main(void) {
  1c:   1141                    addi    sp,sp,-16
  1e:   e406                    sd  ra,8(sp)
  20:   e022                    sd  s0,0(sp)
  22:   0800                    addi    s0,sp,16
  printf("%d %d\n", f(8)+1, 13);
  24:   4635                    li  a2,13
  26:   45b1                    li  a1,12
  28:   00000517            auipc   a0,0x0
  2c:   7b850513            addi    a0,a0,1976 # 7e0 <malloc+0xe6>
  30:   00000097            auipc   ra,0x0
  34:   612080e7            jalr    1554(ra) # 642 <printf>
  exit(0);
  38:   4501                    li  a0,0
  3a:   00000097            auipc   ra,0x0
  3e:   28e080e7            jalr    654(ra) # 2c8 <exit>