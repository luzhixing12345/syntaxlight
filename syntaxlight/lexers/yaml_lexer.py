


from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum

class YamlTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    TRUE = 'true'
    FALSE = 'false'
    BOOL = 'bool'
    INT = 'int'
    STRING = 'str'
    NULL = 'null'
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    KEY = 'Key'
    URL = 'Url'
    STAR = 'STAR'
    ANCHOR = 'Anchor'
    ALIAS = 'Alias'
    MAP = 'MAP'
    INHERIT = 'INHERIT'
    TIME = 'TIME'
    ENV_VAR = 'Env-var'

class YamlLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = YamlTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(['<<'])

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == '#':
                return self.get_comment('#','\n')
            
            if self.current_char.isdigit() or (self.current_char == '.' and self.peek().isdigit()):
                return self.get_number()

            if self.current_char.isalpha() or self.current_char in ('_','/','.'):
                return self.get_id(extend_chars=['_','.','@','-','/','?','|'], ignore_case=True)
            
            if self.current_char in ('"',"'"):
                return self.get_str()

            if self.current_char in self.long_op_dict:
                return self.get_long_op()

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