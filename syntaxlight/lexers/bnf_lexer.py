
from .lexer import Lexer, Token, TokenType, TokenSet, ErrorCode
from enum import Enum

class BNFTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class BNFLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = BNFTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(["::="])

    def get_next_token(self) -> Token:
        
        while self.current_char is not None:
            
            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()
            
            if self.current_char == ' ':
                return self.skip_whitespace()

            if self.current_char in ("'", '"'):
                return self.get_str()
            
            if self.current_char.isalnum() or self.current_char == '_':
                return self.get_id(extend_chars=['_','-'])
            
            if self.current_char == '#':
                return self.get_comment("#",'\n')
            
            if self.current_char in self.long_op_dict:
                return self.get_long_op()
            
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
            

        return Token(type=TokenType.EOF, value='EOF', line=self.line, column=self.column)