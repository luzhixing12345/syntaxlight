class ControlSignal:
    """
    控制信号, 决策对应 MUX 应该选择使用哪一个作为输入
    """

    ALU_Asrc: ALU_Asrc
    ALU_Bsrc: ALU_Bsrc  # ALU 的第二个输入选择哪一个
    ALUop: ALUop  # ALU 如何进行计算
    RegWrite: bool  # 是否写寄存器
    MemRead: bool  # 是否读内存
    MemWrite: bool  # 是否写内存
    MemtoReg: MemtoReg  # 选择写回寄存器的值
    MemOp: MemOp  # 读取内存的方式
    PCsrc: PCsrc  # 选择更新 PC 的方式
