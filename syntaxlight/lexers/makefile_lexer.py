from syntaxlight.lexers.lexer import Token
from .lexer import Lexer, Token, TokenType, ErrorCode, TokenSet
from enum import Enum


class MakefileTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    INCLUDE = "include"
    IFEQ = "ifeq"
    IFNEQ = "ifneq"
    IFDEF = "ifdef"
    IFNDEF = "ifndef"
    ENDIF = "endif"
    EXPORT = "export"
    UNEXPORT = "unexport"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    PATH_SLASH = "/"
    LATER_ASSIGN = ":="
    REDIRECT_TO = ">"
    REDIRECT_FROM = "<"
    AUTO_VARIABLE = "AUTO_VARIABLE"


class MakefileLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = MakefileTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict([":=", "+="])

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

            if self.current_char.isalpha() or self.current_char in ("-", "_", ".", "%"):
                return self.get_id(extend_chars=["_", "-", ".", "%"])

            if self.current_char == "$" and self.peek() in ["@", "%", "<", "?", "^", "+", "*"]:
                result = "$"
                self.advance()
                result += self.current_char
                token = Token(MakefileTokenType.AUTO_VARIABLE, result, self.line, self.column)
                self.advance()
                return token

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
        self.variable = TokenSet(
            TokenType.DOLLAR,
            TokenType.ID,
            TokenType.NUMBER,
            MakefileTokenType.INCLUDE,
            TokenType.STR,
        )
        self.target = TokenSet(self.variable)
        self.condition_stmt = TokenSet(
            MakefileTokenType.IFEQ,
            MakefileTokenType.IFNEQ,
            MakefileTokenType.IFNDEF,
            MakefileTokenType.IFDEF,
        )
        self.export = TokenSet(MakefileTokenType.EXPORT, MakefileTokenType.UNEXPORT)
        self.statement = TokenSet(
            self.variable, MakefileTokenType.INCLUDE, self.condition_stmt, self.export
        )
        self.assign_op = TokenSet(
            TokenType.ASSIGN, MakefileTokenType.LATER_ASSIGN, TokenType.ADD_ASSIGN
        )
