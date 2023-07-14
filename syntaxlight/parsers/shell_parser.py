from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from ..ast import Object, Array, Pair, String, Number, Keyword, UnaryOp

class ShellParser(Parser):

    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

