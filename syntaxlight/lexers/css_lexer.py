from syntaxlight.lexers.lexer import Token
from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum


class CSSTokenType(Enum):
    # RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    # RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    COLOR = "COLOR"
    KEY = "KEY"
    CLASS_NAME = "CLASS_NAME"
    FUNCTION = 'FUNCTION'


class CSSLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = CSSTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                # CSS 单位
                # https://www.zhihu.com/question/602061531/answer/3037149631
                return self.get_number(
                    accept_hex=True,
                    end_chars=[
                        "%",
                        "s",
                        "v",
                        "b",
                        "p",
                        "x",
                        "d",
                        "l",
                        "m",
                        "i",
                        "n",
                        "a",
                        "c",
                        "h",
                        "q",
                        "t",
                        "g",
                        "r",
                        "u",
                    ],
                )

            if self.current_char.isalnum() or self.current_char in (".", "_", "-"):
                return self.get_id(extend_chars=["_", "-", "."])

            if self.current_char == "/" and self.peek() == "*":
                return self.get_comment("/*", "*/")

            if self.current_char == '#':
                result = '#'
                self.advance()
                while self.current_char.isalnum():
                    result += self.current_char
                    self.advance()
                token = Token(CSSTokenType.COLOR, result, self.line, self.column-1)
                return token

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
