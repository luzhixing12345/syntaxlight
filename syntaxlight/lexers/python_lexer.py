from .lexer import Lexer, Token, TokenType
from ..token import TokenSet
from enum import Enum
import re


class PythonTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    AND = "and"
    AS = "as"
    ASYNC = "async"
    ASSERT = "assert"
    AWAIT = "await"
    BREAK = "break"
    CLASS = "class"
    CONTINUE = "continue"
    DEF = "def"
    DEL = "del"
    ELIF = "elif"
    ELSE = "else"
    EXCEPT = "except"
    FALSE = "False"
    FINALLY = "finally"
    FOR = "for"
    FROM = "from"
    GLOBAL = "global"
    IF = "if"
    IMPORT = "import"
    IN = "in"
    IS = "is"
    LAMBDA = "lambda"
    NONE = "None"
    NONLOCAL = "nonlocal"
    NOT = "not"
    OR = "or"
    PASS = "pass"
    RAISE = "raise"
    RETURN = "return"
    TRUE = "True"
    TRY = "try"
    WHILE = "while"
    WITH = "with"
    YIELD = "yield"
    

    INT = 'int'
    STRR = 'str'
    BOOL = 'bool'
    SUPER = 'super'
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    SOFT_CASE = "case"
    SOFT_MATCH = "match"
    SOFT_TYPE = "type"
    FLOOR_ASSIGN = "//="
    MATRIX_ASSIGN = "@="
    POWER = "**"
    POWER_ASSIGN = "**="
    WALRUS = ":="
class PythonLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = PythonTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(
            [
                "**=",
                "//=",
                "<<=",
                ">>=",
                "...",
                "+=",
                "-=",
                "*=",
                "@=",
                "/=",
                "%=",
                "&=",
                "|=",
                "^=",
                ":=",
                "==",
                "!=",
                ">=",
                "<=",
                "<<",
                ">>",
                "**",
                "//",
                "->",
            ]
        )

    def get_python_number(self):
        digits = r"[0-9](?:_?[0-9])*"
        exponent = rf"[eE][+-]?{digits}"
        pattern = re.compile(
            rf"""
            (?:
                0[xX](?:_?[0-9a-fA-F])+
                | 0[oO](?:_?[0-7])+
                | 0[bB](?:_?[01])+
                | (?:
                    (?:{digits})?\.(?:{digits})
                    | (?:{digits})\.(?:{digits})?
                  )(?:{exponent})?
                | (?:{digits})(?:{exponent})
                | (?:{digits})
            )
            [jJ]?
            """,
            re.VERBOSE,
        )
        match = pattern.match(self.text, self.pos)
        value = match.group(0)
        for _ in value:
            self.advance()
        return Token(TokenType.NUMBER, value, self.line, self.column - 1)

    def get_prefixed_string(self):
        prefix = ""
        while self.current_char is not None and self.current_char.lower() in "rubf":
            prefix += self.current_char
            self.advance()

        if self.current_char == "'" and self.peek(2) == "''":
            token = self.get_extend_str(("'''", "'''"))
        elif self.current_char == '"' and self.peek(2) == '""':
            token = self.get_extend_str(('"""', '"""'))
        else:
            token = self.get_str()
        token.value = prefix + token.value
        return token

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()
            
            if self.current_char == '#':
                return self.get_comment()

            if self.current_char == "'" and self.peek(2) == "''":
                return self.get_extend_str(("'''", "'''"))
            if self.current_char == '"' and self.peek(2) == '""':
                return self.get_extend_str(('"""', '"""'))

            if self.current_char in ('"', "'"):
                return self.get_str()

            if self.is_ascii_digit(self.current_char) or (
                self.current_char == "." and self.is_ascii_digit(self.peek())
            ):
                return self.get_python_number()
            
            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            if self.current_char.isalpha() or self.current_char == "_":
                prefix = self.current_char
                next_char = self.peek()
                if next_char is not None and next_char.lower() in "rubf":
                    prefix += next_char
                quote = self.text[self.pos + len(prefix) : self.pos + len(prefix) + 1]
                if prefix.lower() in {"r", "u", "b", "f", "br", "rb", "fr", "rf"} and quote in ('"', "'"):
                    return self.get_prefixed_string()
                return self.get_id()

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

class PythonTokenSet:
    def __init__(self) -> None:
        self.compound_stmt = TokenSet(
            PythonTokenType.ASYNC,
            PythonTokenType.CLASS,
            PythonTokenType.DEF,
            PythonTokenType.FOR,
            PythonTokenType.IF,
            PythonTokenType.TRY,
            PythonTokenType.WHILE,
            PythonTokenType.WITH,
            TokenType.AT_SIGN,
        )
        self.simple_stmt = TokenSet(
            PythonTokenType.ASSERT,
            PythonTokenType.BREAK,
            PythonTokenType.CONTINUE,
            PythonTokenType.DEL,
            PythonTokenType.FROM,
            PythonTokenType.GLOBAL,
            PythonTokenType.IMPORT,
            PythonTokenType.NONLOCAL,
            PythonTokenType.PASS,
            PythonTokenType.RAISE,
            PythonTokenType.RETURN,
            PythonTokenType.YIELD,
            TokenType.ID,
        )
        self.stmt = TokenSet(self.compound_stmt, self.simple_stmt)