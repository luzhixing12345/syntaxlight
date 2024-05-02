
from .lexer import Lexer, Token, TokenType
from enum import Enum
import re


class X86AssemblyTokenType(Enum):
    ASM_KEYWORD = "ASM_KEYWORD"
    REGISTER = "REGISTER"
    FUNCTION_CALL = "FUNCTION_CALL"
    SECTION = "SECTION"


class X86AssemblyLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = X86AssemblyTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                result = ''
                while self.current_char is not None:
                    if bool(re.match(r'^[0-9a-fA-FxX]$', self.current_char)):
                        result += self.current_char
                        self.advance()
                    else:
                        break
                return Token(TokenType.NUMBER, result, self.line ,self.column-1)

            if self.current_char.isalnum() or self.current_char in ("_"):
                return self.get_id(extend_chars=["@", "_",'.'])

            if self.current_char == ".":
                result = "."
                self.advance()
                while self.current_char is not None and self.current_char.isalnum():
                    result += self.current_char
                    self.advance()

                token = Token(X86AssemblyTokenType.ASM_KEYWORD, result, self.line, self.column - 1)
                return token

            if self.current_char == "%":
                result = "%"
                self.advance()
                while self.current_char is not None and self.current_char.isalnum():
                    result += self.current_char
                    self.advance()

                token = Token(X86AssemblyTokenType.REGISTER, result, self.line, self.column - 1)
                return token

            if self.current_char == "#":
                return self.get_comment()
            
            if self.current_char == '/' and self.peek() == '*':
                return self.get_comment('/*','*/')

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


class RISCVAssemblyTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    INCLUDE = "include"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    ASM_KEYWORD = "ASM_KEYWORD"
    REGISTER = "REGISTER"
    SECTION = "SECTION"
    ADDRESS = 'ADDRESS'
    HEADER_NAME = "HeaderName"


class RISCVAssemblyLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = RISCVAssemblyTokenType):
        super().__init__(text, LanguageTokenType)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                
                result = ''
                while self.current_char is not None:
                    if bool(re.match(r'^[0-9a-fA-FxX]$', self.current_char)):
                        result += self.current_char
                        self.advance()
                    else:
                        break

                return Token(TokenType.NUMBER, result, self.line ,self.column-1)

            if self.current_char.isalnum() or self.current_char in ("_"):
                return self.get_id(extend_chars=["@", "_", "."])

            if self.current_char == ".":
                result = "."
                self.advance()
                while self.current_char is not None and self.current_char.isalnum():
                    result += self.current_char
                    self.advance()

                token = Token(
                    RISCVAssemblyTokenType.ASM_KEYWORD, result, self.line, self.column - 1
                )
                return token

            if self.current_char == "#":
                if self.peek(7) == "include":
                    token = Token(TokenType.HASH, self.current_char, self.line, self.column)
                    self.advance()
                    return token
                else:
                    return self.get_comment()
                
            if self.current_char == '/' and self.peek() == '*':
                return self.get_comment('/*','*/')

            if self.current_char == '"':
                return self.get_string()

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
