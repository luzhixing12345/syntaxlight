
from .parser import Parser
from ..lexers import TokenType, ShellTokenType
from ..gdt import *
import re

class ShellCSS(Enum):
    KEYWORD = 'Keyword'
    PROGRAM = 'Program'
    VARIANT = 'Variant'
    GLOBAL_VARIANT = 'GlobalVariant'
    FUNCTION = 'Function'

class ShellParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=False, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        """
        bash 的文法可变因素太多, 这里直接不使用 BNF 采取匹配的方式
        """
        is_program_name = True
        new_program_token_type = [TokenType.LF, TokenType.PIPE, TokenType.SEMI]
        while self.current_token.type != TokenType.EOF:
            # print(self.current_token, is_program_name)
            if self.current_token.value in self.lexer.reserved_keywords:
                self.current_token.add_css(ShellCSS.KEYWORD)
                if is_program_name:
                    is_program_name = False

            if self.current_token.type == TokenType.DOLLAR and self.peek_next_token().type == TokenType.LPAREN:
                is_program_name = True

            if is_program_name:
                if self.current_token.type in (TokenType.ID, ShellTokenType.PATH):
                    is_program_name = False
                    self.current_token.add_css(ShellCSS.PROGRAM) 
            else:
                if self.current_token.type in new_program_token_type:
                    is_program_name = True

            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.LPAREN:
                    # function
                    self.current_token.add_css(ShellCSS.FUNCTION)
                elif bool(re.match(r'$[A-Z][0-9A-Z]+$', self.current_token.value)):
                    self.current_token.add_css(ShellCSS.GLOBAL_VARIANT)
                

            if self.peek_next_token().type == TokenType.ASSIGN:
                self.current_token.add_css(ShellCSS.VARIANT)

            if self.current_token.type == TokenType.STR:
                self.string_inside_format(self.current_token)
                continue
                
            self.eat()
