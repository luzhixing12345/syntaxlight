from .parser import Parser
from ..lexers import TokenType, AssemblyTokenType, Token
from ..gdt import *
import re


class AssemblyParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        
        section_id = []

        while self.current_token.type != TokenType.EOF:

            if self.current_token.type == TokenType.LANGLE_BRACE:
                if self.peek_next_token().type == TokenType.ID:
                    self.eat()
                    self.current_token.type = AssemblyTokenType.FUNCTION_CALL

            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.COLON:
                    self.current_token.type = AssemblyTokenType.SECTION
                    section_id.append(self.current_token.value)

            self.eat()

        for token in self._token_list:
            if token.value in section_id:
                token.type = AssemblyTokenType.SECTION