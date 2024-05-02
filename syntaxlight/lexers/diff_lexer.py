from .lexer import Lexer, Token, TokenType
from enum import Enum
from ..token import TokenSet


class DiffTokenType(Enum):
    ADD_LINE = "+"
    ADD_FILE = "+++"
    SUB_LINE = "-"
    SUB_FILE = "---"
    TAG_LINE = "@@"


class DiffLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = DiffTokenType):
        super().__init__(text, LanguageTokenType)

    def get_line_token(self, token_type: Enum) -> Token:
        '''
        读取一行
        '''
        token_value = ""
        while self.current_char != TokenType.LF.value and self.current_char is not None:
            token_value += self.current_char
            self.advance()

        token = Token(
            type=token_type,
            value=token_value,
            line=self.line,
            column=self.column-1,
        )
        return token

    def get_next_token(self) -> Token:
        """
        diff 很特别,只需要按行分割, 判断开头 +-@ 即可
        """
        while self.current_char is not None:
            if self.current_char in ("+", "-"):
                if self.peek(2) == self.current_char * 2:
                    token_type = DiffTokenType.ADD_FILE if self.current_char == "+" else DiffTokenType.SUB_FILE
                    token = self.get_line_token(token_type)
                    return token
                else:
                    token_type = DiffTokenType.ADD_LINE if self.current_char == "+" else DiffTokenType.SUB_LINE
                    token = self.get_line_token(token_type)
                    return token
            elif self.current_char == "@" and self.peek() == "@":
                token = self.get_line_token(DiffTokenType.TAG_LINE)
                return token
            elif self.current_char == TokenType.LF.value:
                return self.skip_invisiable_character()
            else:
                token = self.get_line_token(TokenType.TEXT)
                return token

        # End of File
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)
