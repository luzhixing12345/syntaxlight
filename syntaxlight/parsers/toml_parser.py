from syntaxlight.parsers.ast import AST
from .parser import Parser
from ..lexers import TokenType, JsonTokenType
from ..error import ErrorCode
from .ast import AST, NodeVisitor


class TomlParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)

    def parse(self):
        self.node = self.toml()

    def toml(self):
        ...
