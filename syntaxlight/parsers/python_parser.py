from .parser import Parser
from ..lexers import TokenType, X86AssemblyTokenType, RISCVAssemblyTokenType
import re

class PythonParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        
        while self.current_token.type != TokenType.EOF:
            self.eat()