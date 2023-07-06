
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from ..ast import AST, Object, Array, Pair, String, Number, Keyword, UnaryOp

class TranslationUnit(AST):

    def __init__(self) -> None:
        super().__init__()


class CParser(Parser):

    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)

    
    def parse(self):
        self.node = self.translation_unit()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.node

    def translation_unit(self):
        
        declarations = []
        