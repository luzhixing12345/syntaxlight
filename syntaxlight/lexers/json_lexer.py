
from .lexer import Lexer, Token
from enum import Enum

class JsonTokenType(Enum):
    # single-character token types
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    SLASH = '/'
    ASSIGN = '='
    BACK_SLASH = '\\'
    LPAREN = '('
    RPAREN = ')'
    LSQUAR_PAREN = '['
    RSQUAR_PAREN = '['
    LCURLY_BRACE = '{'
    RCURLY_BRACE = '}'
    LANGLE_BRACE = '<'
    RANGLE_BRACE = '>'
    SEMI = ';'
    DOT = '.'
    COLON = ':'
    COMMA = ','
    HASH = '#'
    DOLLAR = '$'
    PERCENT = '%'
    CARET = '^'
    AMPERSAND = '&'
    PIPE = '|'
    QUSTION_MARK = '?'
    APOSTROPHE = '\''
    QUOTO_MARK = '\"'
    SPACE = ' '
    NEWLINE = '\n'
    TAB = '\t'
    VERTICAL_TAB = '\v'
    CARRIAGE_RETURN = '\r'
    FORM_FEED = '\f'
    BELL = '\a'
    BACKSPACE = '\b'
    NULL = '\0'
    BANG = '!'
    BACKTICK = '`'
    TILDE = '~'
    AT_SIGN = '@'
    EOF = 'EOF'
    ID  = 'ID'
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    SHL = '<<'
    SHR = '>>'
    EQ = '=='
    NE = '!='
    LE = '<='
    GE = '>='
    VARARGS = '...'
    DB_COLON = '::'

    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # 在这里添加对应语言的保留关键字
    # ...

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'


class JsonErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'      # 不匹配的 Token 类型
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'
    PARAMETERS_NOT_MATCH = 'parameter number not match'


class JsonLexer(Lexer):

    def __init__(self, text: str, TokenType: JsonTokenType = JsonTokenType):
        super().__init__(text, TokenType)

    def get_next_token(self):

        while self.current_char is not None:

            if self.current_char == self.BaseTokenType.QUOTO_MARK.value:
                return self.get_string()
            
            if self.current_char == self.BaseTokenType.SPACE.value:
                return self.skip_whitespace()     
            
            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()
            
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = self.BaseTokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    lineno=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=self.BaseTokenType.EOF, value=None)