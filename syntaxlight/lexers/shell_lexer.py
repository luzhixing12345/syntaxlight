from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum


class ShellTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    THEN = "then"
    FI = "fi"
    FOR = "for"
    DO = "do"
    IN = "in"
    DONE = "done"
    WHILE = "while"
    BREAK = "break"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    OPTION = "option"
    PATH = "path"
    VARIANT = "variant"
    REDIRECT_TO = ">"
    REDIRECT_FROM = "<"


class ShellLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = ShellTokenType):
        super().__init__(text, LanguageTokenType)

    def get_option(self):
        """
        长短选项
        -s --options
        """
        result = ""
        while self.current_char is not None:
            if self.current_char.isalnum() or self.current_char in ("-", "_"):
                result += self.current_char
                self.advance()
            else:
                break

        return Token(ShellTokenType.OPTION, result, self.line, self.column - 1)

    def get_path(self):
        """
        /proc/xxx
        /usr/lib/...
        """
        result = ""
        while self.current_char is not None:
            if self.current_char.isalnum() or self.current_char in ("/", "-", "_", "."):
                result += self.current_char
                self.advance()
            else:
                break
        return Token(ShellTokenType.PATH, result, self.line, self.column - 1)

    def shell_variant(self):
        """
        $i
        $mysh
        """
        result = "$"
        self.advance()
        while self.current_char is not None:
            if self.current_char.isalnum() or self.current_char in ("-", "_"):
                result += self.current_char
                self.advance()
            else:
                break
        return Token(ShellTokenType.VARIANT, result, self.line, self.column - 1)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number(accept_bit=True, accept_hex=True)

            if self.current_char.isalnum() or self.current_char == "_":
                return self.get_id(extend_chars=["_", "-", "."])

            if self.current_char in ('"', "'"):
                return self.get_str()

            if self.current_char == "-":
                return self.get_option()

            if self.current_char == "#":
                return self.get_comment()

            if self.current_char in ("/", "."):
                return self.get_path()

            if self.current_char == "$" and self.peek() != '(':
                return self.shell_variant()

            if self.current_char in ("<", ">"):
                
                token = Token(
                    ShellTokenType(self.current_char), self.current_char, self.line, self.column
                )
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
