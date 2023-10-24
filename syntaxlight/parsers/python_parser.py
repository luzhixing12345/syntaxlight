from .parser import Parser
from ..lexers import TokenType, PythonTokenType

from ..gdt import CSS

class PythonParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        
        while self.current_token.type != TokenType.EOF:

            if self.current_token.type == PythonTokenType.CLASS:
                self.eat()
                self.current_token.add_css(CSS.CLASS_NAME)
                self.eat()
                if self.current_token.type == TokenType.LPAREN:
                    self.eat()
                    self.current_token.add_css(CSS.CLASS_NAME)

            elif self.current_token.type == PythonTokenType.DEF:
                self.eat()
                self.current_token.add_css(CSS.FUNCTION_NAME)

            elif self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.LPAREN:
                    if self.current_token.value[0].isupper():
                        self.current_token.add_css(CSS.CLASS_INSTANTIATION)
                    else:
                        self.current_token.add_css(CSS.FUNCTION_CALL)

            self.eat()