from syntaxlight.lexers.lexer import Token
from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum
import re

class AssemblyTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    ASM_KEYWORD = 'ASM_KEYWORD'
    REGISTER = 'REGISTER'
    FUNCTION_CALL = 'FUNCTION_CALL'
    SECTION = 'SECTION'


class AssemblyLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = AssemblyTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number(accept_bit=True, accept_hex=True)
            
            if self.current_char.isalnum() or self.current_char in ('_'):
                return self.get_id(extend_chars=['@','_'])
            
            if self.current_char == '.':
                result = '.'
                self.advance()
                while self.current_char.isalnum():
                    result += self.current_char
                    self.advance()

                token = Token(AssemblyTokenType.ASM_KEYWORD, result, self.line, self.column-1)
                return token

            if self.current_char == '%':
                result = '%'
                self.advance()
                while self.current_char.isalnum():
                    result += self.current_char
                    self.advance()

                token = Token(AssemblyTokenType.REGISTER, result, self.line, self.column-1)
                return token
            
            if self.current_char == '#':
                return self.get_comment()

            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
                # 考虑一些特殊的情况: test\shell\11.sh
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


