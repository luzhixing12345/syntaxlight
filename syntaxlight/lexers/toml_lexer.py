from .lexer import Lexer, Token, TokenType
from ..error import ErrorCode
from enum import Enum


class TomlTokenType(Enum):
    
    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'
    TRUE = 'true'
    FALSE = 'false'
    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'


class TomlLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = TomlTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self):
        while self.current_char is not None:
            # TOML 单双引号都可以
            if (
                self.current_char == TokenType.QUOTO.value
                or self.current_char == TokenType.APOSTROPHE.value
            ):
                return self.get_str()

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
                    lineno=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value=None)
