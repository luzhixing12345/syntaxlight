
from .parser import Parser


class CParser(Parser):

    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)