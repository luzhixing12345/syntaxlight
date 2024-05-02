
from .lexer import Lexer, Token, TokenType
from ..token import TokenSet
from enum import Enum


class DotTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    STRICT = "strict"
    GRAPH = "graph"
    DIGRAPH = "digraph"
    NODE = "node"
    EDGE = "edge"
    SUBGRAPH = "subgraph"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    UNDIRECT_POINT = "--"


class DotLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = DotTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isalpha() or self.current_char == "_":
                return self.get_id()

            if self.current_char.isdigit() or self.current_char == ".":
                return self.get_number()

            if self.current_char == "/":
                if self.peek() == "*":
                    return self.get_comment("/*", "*/")
                elif self.peek() == "/":
                    return self.get_comment("//", "\n")

            if self.current_char == "-" and self.current_char == "-":
                self.advance()
                token = Token(DotTokenType.UNDIRECT_POINT, "--", self.line, self.column)
                self.advance()
                return token

            if self.current_char == '"':
                return self.get_string()

            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
                token = Token(TokenType.TEXT, self.current_char, self.line, self.column)
                self.advance()
                return token
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # End of File
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)


class DotTokenSet:
    def __init__(self) -> None:
        self.subgraph = TokenSet(DotTokenType.SUBGRAPH, TokenType.LCURLY_BRACE)
        self.edgeop = TokenSet(TokenType.POINT, DotTokenType.UNDIRECT_POINT)
        self.attr_stmt = TokenSet(DotTokenType.GRAPH, DotTokenType.NODE, DotTokenType.EDGE)
        self.node_stmt = TokenSet(TokenType.ID)
        self.stmt = TokenSet(TokenType.ID, self.attr_stmt, self.subgraph)
        self.stmt_list = TokenSet(self.stmt)
