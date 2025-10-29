from .lexer import Lexer, Token, TokenType
from enum import Enum


class TreeTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class TreeLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = TreeTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(["->"])

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            if self.current_char.isalpha() or self.current_char.isdigit() or self.current_char in [".", "_", '\\']:
                token = self.get_id(extend_chars=[".", "_", "-", "/", "+", "@", "~", "\\"])
                return token

            if self.current_char == TokenType.SPACE.value:
                token = Token(TokenType.SPACE, self.current_char, self.line, self.column)
                self.advance()
                return token

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
