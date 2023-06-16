from syntaxlight.lexers.lexer import TokenType
from .lexer import Lexer, Token
from enum import Enum


class LuaTokenType(Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    SLASH = "/"
    ASSIGN = "="
    BACK_SLASH = "\\"
    LPAREN = "("
    RPAREN = ")"
    LSQUAR_PAREN = "["
    RSQUAR_PAREN = "["
    LCURLY_BRACE = "{"
    RCURLY_BRACE = "}"
    LANGLE_BRACE = "<"
    RANGLE_BRACE = ">"
    SEMI = ";"
    DOT = "."
    COLON = ":"
    COMMA = ","
    HASH = "#"
    DOLLAR = "$"
    PERCENT = "%"
    CARET = "^"
    AMPERSAND = "&"
    PIPE = "|"
    QUSTION_MARK = "?"
    APOSTROPHE = "'"
    QUOTO_MARK = '"'
    SPACE = " "
    NEWLINE = "\n"
    TAB = "\t"
    VERTICAL_TAB = "\v"
    CR = "\r"
    FORM_FEED = "\f"
    BELL = "\a"
    BACKSPACE = "\b"
    NULL = "\0"
    BANG = "!"
    BACKTICK = "`"
    TILDE = "~"
    AT_SIGN = "@"
    EOF = "EOF"
    ID = "ID"
    STRING = "STRING"
    NUMBER = "NUMBER"
    SHL = "<<"
    SHR = ">>"
    EQ = "=="
    NE = "~="  # 这里不一样
    LE = "<="
    GE = ">="
    VARARGS = "..."
    DB_COLON = "::"
    CONCAT = ".."

    # -----------------------------------------------
    # start - end 之间为对应语言的保留关键字
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"

    # https://www.lua.org/manual/5.4/manual.html#8

    AND = "and"
    BREAK = "break"
    DO = "do"
    ELSE = "else"
    ELSEIF = "elseif"
    END = "end"
    FALSE = "false"
    FOR = "for"
    FUNCTION = "function"
    GOTO = "goto"
    IF = "if"
    IN = "in"
    LOCAL = "local"
    NIL = "nil"
    NOT = "not"
    OR = "or"
    REPEAT = "repeat"
    RETURN = "return"
    THEN = "then"
    TRUE = "true"
    UNTIL = "until"
    WHILE = "while"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------


class LuaLexer(Lexer):
    def __init__(self, text: str, TokenType: TokenType = LuaTokenType):
        super().__init__(text, TokenType)

    def get_number(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        return Token(TokenType.NUMBER, result, self.line, self.column)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char.isalpha() or self.current_char == "_":
                return self.get_id()

            if self.current_char in ("'", '"'):
                return self.get_string()

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
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
        return Token(type=TokenType.EOF, value=None)
