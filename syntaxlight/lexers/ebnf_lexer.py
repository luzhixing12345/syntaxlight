from .lexer import Lexer, Token, TokenType
from enum import Enum


class EBNFTokenType(Enum):
    S = "SEPARATOR"
    GRAMMAR = "GRAMMAR"
    RULE = "RULE"
    LHS = "LHS"
    RHS = "RHS"
    TERMINATOR = "TERMINATOR"
    ALTERNATION = "ALTERNATION"
    IDENTIFIER = "IDENTIFIER"
    CONCATENATION = "CONCATENATION"
    FACTOR = "FACTOR"
    LETTER = "LETTER"
    DIGIT = "DIGIT"
    TERM = "TERM"
    SYMBOL = "SYMBOL"
    CHARACTER = "CHARACTER"
    TERMINAL = "TERMINAL"
    RESERVED_KEYWORD_START = ""
    RESERVED_KEYWORD_END = ""


class EBNFErrorCode(Enum):
    UNEXPECTED_TOKEN = "Unexpected token"  # 不匹配的 Token 类型
    ID_NOT_FOUND = "Identifier not found"
    DUPLICATE_ID = "Duplicate id found"
    PARAMETERS_NOT_MATCH = "parameter number not match"


class EBNFLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = EBNFTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isalpha():
                return self.get_id()

            if self.current_char in ("'", '"'):
                return self.get_str()

            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        return Token(type=TokenType.EOF, value=None)
