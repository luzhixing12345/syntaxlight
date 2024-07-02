from .lexer import Lexer, Token, TokenType
from enum import Enum


class TxtTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    YES = "yes"
    NO = "no"
    OK = "ok"
    FAIL = "fail"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class TxtLexer(Lexer):

    def __init__(self, text: str, LanguageTokenType: Enum = TxtTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:

        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number(accept_hex=True, accept_bit=True)

            if self.current_char.isalpha():
                return self.get_id(ignore_case=True)

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
