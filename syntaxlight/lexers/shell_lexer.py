

from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum

class ShellTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    ALIAS = 'alias'
    BG = 'bg'
    BIND = 'bind'
    BREAK = 'break'
    BUILTIN = 'builtin'
    CALLER = 'caller'
    CASE = 'case'
    CD = 'cd'
    
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

class ShellLexer(Lexer):

    def __init__(self, text: str, LanguageTokenType: Enum = ShellTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                    return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char.isalnum() or self.current_char == '_':
                return self.get_id(extend_chars=['_','-'])
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