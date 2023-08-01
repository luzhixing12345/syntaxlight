from syntaxlight.lexers.lexer import Token
from .lexer import Lexer, Token, TokenType, ErrorCode,TokenSet
from enum import Enum

class MakefileTokenType(Enum):
    
    PATH_SLASH = '/'
    LATER_ASSIGN = ':='


class MakefileLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = MakefileTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict([':='])

    def get_next_token(self) -> Token:
        
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()
            
            if self.current_char in ('"', "'"):
                return self.get_str()
            
            if self.current_char == TokenType.HASH.value:
                # match comment
                return self.get_comment()
            
            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            if self.current_char.isdigit():
                return self.get_number()
            
            if self.current_char.isalpha() or self.current_char in ('-','_','.'):
                return self.get_id(extend_chars=["_",'-','.'])
            
            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
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
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)
    

class MakefileTokenSet:

    def __init__(self) -> None:
        
        self.variable = TokenSet(TokenType.DOLLAR, TokenType.ID)
        self.target = TokenSet(self.variable)
        self.statement = TokenSet(self.variable)
        self.assign_op = TokenSet(TokenType.ASSIGN,MakefileTokenType.LATER_ASSIGN)