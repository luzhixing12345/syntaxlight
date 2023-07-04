from .lexer import Lexer, Token, TokenType
from ..error import ErrorCode
from enum import Enum


class TomlTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    TRUE = "true"
    FALSE = "false"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    DATE = "DATE"


class TomlLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = TomlTokenType):
        super().__init__(text, LanguageTokenType)
        self.match_comment = False

    def get_id(self):
        """Handle identifiers and reserved keywords"""
        value = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_" or self.current_char == '-'
        ):
            value += self.current_char
            self.advance()

        token_type = self.reserved_keywords.get(value)

        if token_type is None:
            token = Token(type=TokenType.ID, value=value, line=self.line, column=self.column - 1)
        else:
            # reserved keyword
            token = Token(type=token_type, value=value, line=self.line, column=self.column - 1)
        return token

    def get_comment(self):
        self.match_comment = False
        result = ''
        while self.current_char is not None and self.current_char != TokenType.LF.value:
            result += self.current_char
            self.advance()
        
        return Token(TokenType.COMMENT, result, self.line, self.column -1)

    def get_next_token(self):
        while self.current_char is not None:
            if self.match_comment:
                return self.get_comment()
            # TOML 单双引号都可以
            if (
                self.current_char == TokenType.QUOTO.value
                or self.current_char == TokenType.APOSTROPHE.value
            ):
                return self.get_str()

            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()
            
            if self.current_char == TokenType.HASH.value:
                # match comment in next token
                self.match_comment = True

            if self.current_char.isdigit():
                token = self.get_number()
                # https://datatracker.ietf.org/doc/html/rfc3339
                # a tricky implementation
                if self.current_char in (TokenType.MINUS.value, TokenType.COLON.value):
                    result = token.value
                    while self.current_char is not None and self.current_char not in (
                        TokenType.HASH.value,
                        TokenType.CR.value,
                        TokenType.LF.value,
                    ):
                        result += self.current_char
                        self.advance()
                    return Token(TomlTokenType.DATE, result, self.line, self.column - 1)
                else:
                    return token

            if self.current_char.isalpha():
                return self.get_id()

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

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value='EOF', line=self.line, column=self.column)
