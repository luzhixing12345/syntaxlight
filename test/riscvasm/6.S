00000000 <loop_test>:
   0:   000017b7                lui     a5,0x1
   4:   f9c78793                addi    a5,a5,-100 # f9c <.L2+0xf90>
   8:   00f507b3                add     a5,a0,a5

0000000c <.L2>:
   c:   0007a703                lw      a4,0(a5)
  10:   00078693                mv      a3,a5
  14:   ffc78793                addi    a5,a5,-4
  18:   00b70733                add     a4,a4,a1
  1c:   00e7a223                sw      a4,4(a5)
  20:   fed516e3                bne     a0,a3,c <.L2>
  24:   00008067                ret