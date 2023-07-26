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
            # json 仅支持 ""
            if self.current_char == TokenType.QUOTO.value:
                return self.get_string()

            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char.isalnum() or self.current_char == '_':
                return self.get_id()
            
            if self.current_char == '/' and self.peek() == '/':
                return self.get_comment('//','\n')
            
            try:
                token_type = TokenType(self.current_char)
            except ValueError: # pragma: no cover
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
        
        # End of File
        return Token(type=TokenType.EOF, value='EOF', line=self.line, column=self.column)
