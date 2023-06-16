from .lexer import Lexer, Token, TokenType
from ..error import ErrorCode
from enum import Enum


class JsonTokenType(Enum):
    # single-character token types
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"

    # keyword
    TRUE = "true"
    FALSE = "false"
    NULL = "null"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class JsonLexer(Lexer):
    def __init__(self, text: str, TokenType: Enum = JsonTokenType):
        super().__init__(text, TokenType)

    def get_next_token(self):
        while self.current_char is not None:
            # json only support '
            if self.current_char == TokenType.QUOTO.value:
                return self.get_string()

            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit() or self.current_char == TokenType.MINUS.value:
                return self.get_number()

            if self.current_char.isalpha():
                return self.get_id()

            try:
                token_type = TokenType(self.current_char)
            except ValueError:
                token = Token(None, self.current_char, self.line, self.column)
                self.error(ErrorCode.UNKNOWN_CHARACTER, token)
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value=None)
