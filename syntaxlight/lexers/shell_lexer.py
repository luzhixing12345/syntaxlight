from .lexer import Lexer, Token, TokenType
from enum import Enum
import re


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
    CD = "cd"
    EXPORT = "export"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    OPTION = "option"
    PATH = "path"
    VARIANT = "variant"
    REDIRECT_TO = ">"
    REDIRECT_FROM = "<"
    LINUX_USER_PATH = "root@kamilu"
    HOST_NAME = "HostName"
    DIR_PATH = "DirPath"
    TAG = "Tag"


class ShellLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = ShellTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(["&&", ">>", "<<", "==", "==="])

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
                return self.get_number(accept_bit=True, accept_hex=True, end_chars="sMGK")

            if self.current_char.isalpha() or self.current_char in ("_", ".", "/"):
                token = self.get_id(extend_chars=["_", "-", ".", "/", ":", "+", "-", "@", "~"])
                if bool(re.match(r"^\w+@[\w.-]+:[~\w/]+", token.value)):
                    if self.current_char in ("#", "$"):
                        token.value += self.current_char
                        token.column += 1
                        self.advance()
                    token.type = ShellTokenType.LINUX_USER_PATH

                return token

            # 只接受双引号, 因为无法判断 can't ... 这种
            if self.current_char == '"':
                return self.get_string()

            if self.current_char == "-":
                next_char = self.peek()
                if next_char is not None and (next_char.isalpha() or next_char == "-"):
                    return self.get_option()

            if self.current_char == "#":
                return self.get_comment()

            if self.current_char == "$" and self.peek() != "(":
                return self.shell_variant()

            if self.current_char in ("<", ">") and self.peek() != self.current_char:
                token = Token(ShellTokenType(self.current_char), self.current_char, self.line, self.column)
                self.advance()
                return token

            if self.current_char in self.long_op_dict:
                return self.get_long_op()

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
