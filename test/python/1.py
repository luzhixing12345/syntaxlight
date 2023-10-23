class ISA:
    def stage_ex(self):
        """
        EX-执行.对指令的各种操作数进行运算
        """
        self.instruction.stage_ex()

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据
        """
        self.instruction.stage_mem()

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器
        """
        self.instruction.stage_wb()