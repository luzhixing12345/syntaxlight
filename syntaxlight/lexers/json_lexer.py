
from .lexer import Lexer, Token
from ..error import ErrorCode
from enum import Enum

class JsonTokenType(Enum):
    # single-character token types
    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # 在这里添加对应语言的保留关键字
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'


class JsonLexer(Lexer):

    def __init__(self, text: str, TokenType: Enum = JsonTokenType):
        super().__init__(text, TokenType)

    def get_next_token(self):

        while self.current_char is not None:

            if self.current_char == self.TokenType.QUOTO_MARK.value:
                return self.get_string()
            
            if self.current_char == self.TokenType.SPACE.value:
                return self.skip_whitespace()     
            
            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()
            
            if self.current_char.isalpha():
                return self.get_id()
            
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = self.TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                token = Token(None, self.current_char, self.line, self.column)
                self.error(ErrorCode.UNKNOWN_CHARACTER, token)
            else:
                # create a token with a single-character lexeme as its value
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
        return Token(type=self.TokenType.EOF, value=None)