from .parser import Parser
from ..lexers import TokenType, X86AssemblyTokenType, RISCVAssemblyTokenType
import re


class X86AssemblyParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        section_id = []

        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.LANGLE_BRACE:
                if self.peek_next_token().type == TokenType.ID:
                    self.eat()
                    self.current_token.type = X86AssemblyTokenType.FUNCTION_CALL

            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.COLON:
                    self.current_token.type = X86AssemblyTokenType.SECTION
                    section_id.append(self.current_token.value)

            self.eat()

        for token in self._token_list:
            if token.value in section_id:
                token.type = X86AssemblyTokenType.SECTION


class RISCVAssmemblyParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        # https://zhuanlan.zhihu.com/p/295439950
        integer_registers = [
            "zero",
            "ra",
            "sp",
            "gp",
            "tp",
            "t0",
            "t1",
            "t2",
            "s0",
            "s1",
            "a0",
            "a1",
            "a2",
            "a3",
            "a4",
            "a5",
            "a6",
            "a7",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "s9",
            "s10",
            "s11",
            "t3",
            "t4",
            "t5",
            "t6",
        ]

        # RISC-V Floating-Point Registers
        floating_point_registers = [
            "ft0",
            "ft1",
            "ft2",
            "ft3",
            "ft4",
            "ft5",
            "ft6",
            "ft7",
            "fs0",
            "fs1",
            "fa0",
            "fa1",
            "fa2",
            "fa3",
            "fa4",
            "fa5",
            "fa6",
            "fa7",
            "fs2",
            "fs3",
            "fs4",
            "fs5",
            "fs6",
            "fs7",
            "fs8",
            "fs9",
            "fs10",
            "fs11",
            "ft8",
            "ft9",
            "ft10",
            "ft11",
        ]

        # Regular expression pattern to match the register names
        self.register_pattern = re.compile(
            r"\b(" + "|".join(integer_registers + floating_point_registers) + r")\b"
        )

    def parse(self):
        section_id = []

        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.COLON:
                    self.current_token.type = RISCVAssemblyTokenType.SECTION
                    section_id.append(self.current_token.value)
                
                elif bool(re.match(self.register_pattern, self.current_token.value)):
                    self.current_token.type = RISCVAssemblyTokenType.REGISTER

                elif len(self._token_list) >= 2:
                    if self._token_list[-2].type == RISCVAssemblyTokenType.ASM_KEYWORD:
                        self.current_token.type = RISCVAssemblyTokenType.SECTION
                        section_id.append(self.current_token.value)
                
                if self.current_token.type != RISCVAssemblyTokenType.REGISTER:
                    if bool(re.search(r'\d+', self.current_token.value)):
                        self.current_token.type = TokenType.NUMBER

            if self.current_token.type == TokenType.STRING:
                if self._token_list[-2].type == RISCVAssemblyTokenType.INCLUDE:
                    self.current_token.add_css(RISCVAssemblyTokenType.HEADER_NAME)
                else:
                    self.string_inside_format()

            self.eat()

        for token in self._token_list:
            if token.value in section_id:
                token.type = RISCVAssemblyTokenType.SECTION
