.
├── Makefile            # make 编译 + 反汇编
├── example.S           # 汇编程序
├── instructions.py     # 所有指令实现
├── isa.py              # ISA 实现
├── main.ipynb          # 需要提交的作业(没用到, 不重要)
└── main.py             # 主函数, RISCV ISA 实现

├── touch
├── touch.c
├── touch.o
├── tree
├── tree.c
└── tree.o

.
├── asmcode             # 测试用例
│   ├── CTL1.S
│   ├── DH1.S
│   ├── DH2.S
│   ├── DH3.S
│   ├── DH_RAW.S
│   ├── DH_WAR.S
│   └── DH_WAW.S
├── base.py             # 基础枚举类型和类定义
├── instructions.py     # RISCV 32I 指令集
├── isa.py              # Pipeline ISA
├── loop.S              # 汇编代码
├── loop.c              # C 代码
├── main.py             # 主函数入口
├── schedule_loop.S     # 汇编的重排序
└── test.py             # Pipeline ISA 正确性测试文件