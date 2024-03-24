
from .parser import Parser
from ..lexers import TokenType

class DiffParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        
    def parse(self):
        
        while self.current_token.type != TokenType.EOF:
            self.eat()