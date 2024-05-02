from .lexer import Lexer, Token, TokenType, ErrorCode
from ..token import TokenSet
from enum import Enum


class XmlTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    PROLOG_START = "<?xml"
    PROLOG_END = "?>"
    TAG_START_BEGIN = "<"
    TAG_END = ">"
    TAG_COMPLETE_BEGIN = '</'
    TAG_SELF_END = "/>"
    NAME = "NAME"
    CONTENT = "CONTENT"


class XmlLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = XmlTokenType):
        super().__init__(text, LanguageTokenType)
        self.content_matching = False

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.content_matching:
                result = ""
                while self.current_char is not None and self.current_char != "<":
                    result += self.current_char
                    self.advance()
                self.content_matching = False
                return Token(XmlTokenType.CONTENT, result, self.line, self.column - 1)

            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == "<":
                if self.peek(4) == "?xml":
                    result = "<?xml"
                    self.advance()
                    self.advance()
                    self.advance()
                    self.advance()
                    token = Token(XmlTokenType.PROLOG_START, result, self.line, self.column)
                    self.advance()
                    return token
                elif self.peek(3) == "!--":
                    return self.get_comment("<!--", "-->")
                elif self.peek() == "/":
                    self.advance()
                    token = Token(XmlTokenType.TAG_COMPLETE_BEGIN, "</", self.line, self.column)
                    self.advance()
                    return token
                else:
                    token = Token(
                        XmlTokenType.TAG_START_BEGIN, self.current_char, self.line, self.column
                    )
                    self.advance()
                    return token
            if self.current_char == "/" and self.peek() == ">":
                self.advance()
                token = Token(XmlTokenType.TAG_SELF_END, "/>", self.line, self.column)
                self.advance()
                return token
            if self.current_char == ">":
                token = Token(XmlTokenType.TAG_END, self.current_char, self.line, self.column)
                self.content_matching = True
                self.advance()
                return token
            if self.current_char == "?" and self.peek() == ">":
                self.advance()
                token = Token(XmlTokenType.PROLOG_END, "?>", self.line, self.column)
                self.advance()
                return token
            
            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char.isalpha() or self.current_char in ("_", ":"):
                result = ""
                # <Name> ::= (Letter | '_' | ':') (<NameChar>)*
                # <NameChar> ::= <Letter> | <Digit> | '.' | '-' | '_' | ':'
                while self.current_char is not None and (
                    self.current_char.isalnum() or self.current_char in ("_", ":", ".", "-")
                ):
                    result += self.current_char
                    self.advance()

                return Token(XmlTokenType.NAME, result, self.line, self.column - 1)

            if self.current_char in ('"', "'"):
                return self.get_str()

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
