
# txt
## [1.txt](https://github.com/luzhixing12345/syntaxlight/tree/main/test/txt/1.txt)

```txt
before
####################
mem[ 0] =  20 |mem[ 1] =   0 |mem[ 2] =   0 |mem[ 3] =   0 |
mem[ 4] =   0 |mem[ 5] =   0 |mem[ 6] =   0 |mem[ 7] =   0 |
mem[ 8] =   0 |mem[ 9] =   0 |mem[10] =   0 |mem[11] =   0 |
mem[12] =   0 |mem[13] =   0 |mem[14] =   0 |mem[15] =   0 |
mem[16] =   0 |mem[17] =   0 |mem[18] =   0 |mem[19] =   0 |
####################
r0  =   0 |r1  =   0 |r2  =   0 |r3  =   0 |r4  =   0 |r5  =   0 |r6  =   0 |r7  =   0 |
r8  =   0 |r9  =   0 |r10 =   0 |r11 =   0 |r12 =   0 |r13 =   0 |r14 =   0 |r15 =   0 |
r16 =   0 |r17 =   0 |r18 =   0 |r19 =   0 |r20 =   0 |r21 =   0 |r22 =   0 |r23 =   0 |
r24 =   0 |r25 =   0 |r26 =   0 |r27 =   0 |r28 =   0 |r29 =   0 |r30 =   0 |r31 =   0 |
####################
after
####################
mem[ 0] =  20 |mem[ 1] =   0 |mem[ 2] =   0 |mem[ 3] =  30 |
mem[ 4] =   0 |mem[ 5] =   0 |mem[ 6] =   0 |mem[ 7] =   0 |
mem[ 8] =   0 |mem[ 9] =   0 |mem[10] =   0 |mem[11] =   0 |
mem[12] =   0 |mem[13] =   0 |mem[14] =   0 |mem[15] =   0 |
mem[16] =   0 |mem[17] =   0 |mem[18] =   0 |mem[19] =   0 |
####################
r0  =   0 |r1  =   0 |r2  =   0 |r3  =   0 |r4  =   0 |r5  =   0 |r6  =   0 |r7  =   0 |
r8  =   0 |r9  =   0 |r10 =   0 |r11 =  30 |r12 =  30 |r13 =   0 |r14 = 284 |r15 =   0 |
r16 =   0 |r17 =   0 |r18 =   0 |r19 =   0 |r20 =   0 |r21 =   0 |r22 =   0 |r23 =   0 |
r24 =   0 |r25 =   0 |r26 =   0 |r27 =   0 |r28 =   0 |r29 =   0 |r30 =   0 |r31 =   0 |
####################
```
## [2.txt](https://github.com/luzhixing12345/syntaxlight/tree/main/test/txt/2.txt)

```txt
[instruction status]

    Op   dest j   k  | Issue  Read  Exec  Write
    Load F6   34  R2 |
    Load F2   45  R3 |
    Mul  F0   F2  F4 |
    Sub  F8   F6  F2 |
    Div  F10  F0  F6 |
    Add  F6   F8  F2 |


[functional unit status]

    Time   Name    | Busy  Op    Fi  Fj  Fk  Qj      Qk      Rj  Rk
           Integer |   No                                    yes  No
           Mult1   |   No                                    Yes  No
           Mult2   |   No                                    No  No
           Add     |   No                                    No  No
           Divide  |   No                                    No  No


[register result status]

             F0 F2 F4 F6 F8 F10
   Cycle 0

.
.
.

----------------------------------------------------------------------
[instruction status]

    Op   dest j   k  | Issue  Read  Exec  Write
    Load F6   34  R2 |     1     2     3     4
    Load F2   45  R3 |     5     6     7     8
    Mul  F0   F2  F4 |     6     9    19    20
    Sub  F8   F6  F2 |     7     9    11    12
    Div  F10  F0  F6 |     8    21    61    62
    Add  F6   F8  F2 |    13    14    16    22


[functional unit status]

    Time   Name    | Busy  Op    Fi  Fj  Fk  Qj      Qk      Rj  Rk
           Integer |   No                                    No  No
           Mult1   |   No                                    No  No
           Mult2   |   No                                    No  No
           Add     |   No                                    No  No
           Divide  |   No                                    No  No


[register result status]

             F0 F2 F4 F6 F8 F10
   Cycle 62
```
## [3.txt](https://github.com/luzhixing12345/syntaxlight/tree/main/test/txt/3.txt)

```txt
Unit     Instruction     start   end     theoretical/running
Integer  LOAD F6 34 R2       1     4     4/4
         LOAD F2 45 R3       5     8     4/4

Mult1    MUL F0 F2 F4        6    20     13/15

Mult2
Add      SUB F8 F6 F2        7    12     5/6
         ADD F6 F8 F2       13    22     5/10

Divide   DIV F10 F0 F6       8    62     43/55
```
