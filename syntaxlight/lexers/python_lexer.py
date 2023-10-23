from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum


class PythonTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    AND = "and"
    AS = "as"
    ASSERT = "assert"
    BREAK = "break"
    CLASS = "class"
    CONTINUE = "continue"
    DEF = "def"
    DEL = "del"
    ELIF = "elif"
    ELSE = "else"
    EXCEPT = "except"
    FLASE = "False"
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
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class PythonLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = PythonTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(
            ["+=", "-=", "*=", "@=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "**=", "//="]
        )

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

            if self.current_char.isdigit():
                return self.get_number(accept_bit=True, accept_hex=True)
            
            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            if self.current_char.isalnum() or self.current_char == "_":
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
