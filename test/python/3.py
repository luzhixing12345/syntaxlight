class ISA:
    """
    基础处理器架构
    """

    def __init__(self) -> None:
        # 基础配置信息
        register_number = 32
        memory_range = 0x200

        self.pc = 0
        self.registers = [0] * register_number  # 寄存器组
        self.memory = [0] * memory_range  # 内存
        self.instruction: Instruction = None  # 当前指令
        self.instruction_info = InstructionInfo()  # 当前指令的信息拆分
        self.pipeline_register = PipeReg()

class Instruction:
    def __init__(self, isa: "ISA") -> None:
        self.isa = isa
        self.pc_inc = True

    def stage_ex(self):
        """
        EX-执行.对指令的各种操作数进行运算

        IF ID 阶段操作相对固定, EX MEM WB 阶段需要根据具体指令在做调整

        单指令可以继承 Instruction 类并重写此方法
        """

    def stage_mem(self):
        """
        MEM-存储器访问.将数据写入存储器或从存储器中读出数据

        单指令可以继承 Instruction 类并重写此方法
        """

    def stage_wb(self):
        """
        WB-写回.将指令运算结果存入指定的寄存器

        单指令可以继承 Instruction 类并重写此方法
        """
        if self.pc_inc:
            self.isa.pc += 4

class I_ADDI(Instruction):
    
    def stage_ex(self):
        self.isa.pipeline_register.value = self.isa.pipeline_register.rs1 + self.isa.instruction_info.imm

    def stage_wb(self):
        self.isa.registers[self.isa.instruction_info.rd] = self.isa.pipeline_register.value
        return super().stage_wb()
    
def main():
    instructions = [
        0x00A54533,
        0x00050583,
        0x00150603,
        0x00360613,
        0x00158593,
        0xFEC59CE3,
        0x0040076F,
        0x00C501A3,
    ]

    isa = RISCV32()
    isa.memory[0] = 20
    isa.memory[1] = 0
    isa.show_info("before")

    isa.load_instructions(instructions)
    isa.run()
    isa.show_info("after")


if __name__ == "__main__":
    main()

def load_instructions(self, instructions, pc=0x100):
    self.pc = pc
    # 小端存储
    for inst in instructions:
        instruction_str = format(inst, "032b")
        self.memory[pc + 3] = int(instruction_str[:8], 2)
        self.memory[pc + 2] = int(instruction_str[8:16], 2)
        self.memory[pc + 1] = int(instruction_str[16:24], 2)
        self.memory[pc] = int(instruction_str[24:], 2)
        pc += 4

def run(self):
    while True:
        self.stage_if()
        if self.pc == -1:
            break
        self.stage_id()
        self.stage_ex()
        self.stage_mem()
        self.stage_wb()

def stage_if(self):
    """
    IF-取指令.根据PC中的地址在指令存储器中取出一条指令
    """
    # 小端取数
    self.instruction = ""
    self.instruction += format(self.memory[self.pc + 3], "08b")
    self.instruction += format(self.memory[self.pc + 2], "08b")
    self.instruction += format(self.memory[self.pc + 1], "08b")
    self.instruction += format(self.memory[self.pc], "08b")

    # 全 0 默认运行完所有指令, 退出
    if int(self.instruction) == 0:
        self.pc = -1

def stage_id(self):
    """
    ID-译码 解析指令并读取寄存器的值
    """
    raise NotImplementedError("should implement stage ID")


if (
    self.instruction_info.funct3 == RFunct3.SUB
    and self.instruction_info.funct7 == RFunct7.SUB
):
    self.instruction = R_SUB(self)
elif (
    self.instruction_info.funct3 == RFunct3.SRA
    and self.instruction_info.funct7 == RFunct7.SRA
):
    self.instruction = R_SRA(self)
elif self.instruction_info.opcode == OpCode.U_AUIPC:
    self.instruction = U_AUIPC(self)
elif self.instruction_info.opcode == OpCode.U_LUI:
    self.instruction = U_LUI(self)
elif self.instruction_info.opcode == OpCode.J:
    self.instruction = J_JAL(self)
else:
    self.instruction = RISCV_32I_instructions[self.instruction_info.opcode][
        self.instruction_info.funct3
    ](self)