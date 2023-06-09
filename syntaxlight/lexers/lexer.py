import argparse
import sys
from enum import Enum

_SHOULD_LOG_SCOPE = False  # see '--scope' command line option
_SHOULD_LOG_STACK = False  # see '--stack' command line option


class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'
    PARAMETERS_NOT_MATCH = 'parameter number not match'


class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'


class LexerError(Error):
    pass


class ParserError(Error):
    pass


class SemanticError(Error):
    pass


class TokenType(Enum):
    # single-character token types
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    SLASH = '/'
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
    BANG = '!'
    BACKTICK = '`'
    TILDE = '~'
    AT_SIGN = '@'
    EOF = 'EOF'

    # misc
    ID = 'ID'
    STRING = 'STRING'

    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # 在这里添加对应语言的保留关键字
    # ...

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'


class Token:
    def __init__(self, type, value, lineno=None, column=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER_CONST, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()


class Lexer:
    '''
    Lexer 基类, 提供了一些基础函数和功能, 比如匹配数字, 匹配字符串

        可能有些编程语言的处理(比如Lua的字符串)不同, 单独覆盖即可
    
    继承 Lexer 的子类需要重写其 get_next_token 方法以提供给后续的 parser 解析
    '''

    def __init__(self, text: str, TokenType: TokenType):
        self.text: str = text
        self.pos: int = 0  # 当前指针指向的字符
        self.current_char: str = self.text[self.pos]  # 当前指针指向的字符
        self.line: int = 1
        self.column: int = 1
        self.TokenType = TokenType

        # 获取 RESERVED_KEYWORD_START - RESERVED_KEYWORD_END 之间的保留关键字
        tt_list = list(TokenType)
        start_index = tt_list.index(TokenType.RESERVED_KEYWORD_START)
        end_index = tt_list.index(TokenType.RESERVED_KEYWORD_END)
        self.reserved_keywords = {
            token_type.value: token_type
            for token_type in tt_list[start_index+1:end_index]
        }
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        self.invisible_characters = {
            TokenType.NEWLINE.value: TokenType.NEWLINE,
            TokenType.TAB.value: TokenType.TAB,
            TokenType.VERTICAL_TAB.value: TokenType.VERTICAL_TAB,
            TokenType.CARRIAGE_RETURN.value: TokenType.CARRIAGE_RETURN,
            TokenType.FORM_FEED.value: TokenType.FORM_FEED
        }

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.line,
            column=self.column,
        )
        raise LexerError(message=s)

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def skip_whitespace(self):
        '''
        通常来说直接跳过空格即可, 这里保留空格是为了不破坏原本的代码格式
        '''
        result = ''
        while self.current_char is not None and self.current_char == ' ':
            result += ' '
            self.advance()
        return Token(self.TokenType.SPACE, result, self.line, self.column)

    def skip_invisiable_character(self):
        token = Token(
            self.invisible_characters[self.current_char], self.current_char, self.line, self.column)
        self.advance()
        return token
    
    def skip_string(self):

        result = self.current_char
        end_match = self.current_char # ' or "
        self.advance()
            
        while self.current_char is not None and self.current_char != end_match:
            result += self.current_char
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.error()
                result += self.current_char
            self.advance()
        self.advance()
        result += end_match

        return Token(self.TokenType.STRING, result, self.line, self.column)


    def peek(self, n = 1):
        peek_pos = self.pos+n
        if peek_pos > len(self.text)-1:
            return None
        else:
            return self.text[self.pos+1:peek_pos]
    
    def get_id(self):
        """Handle identifiers and reserved keywords"""

        token = Token(type=None, value=None,
                      lineno=self.line, column=self.column)

        value = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()

        token_type = self.reserved_keywords.get(value.upper())
        if token_type is None:
            token.type = self.TokenType.ID
            token.value = value
        else:
            # reserved keyword
            token.type = token_type
            token.value = value.upper()

        return token

    def get_next_token(self):
        raise NotImplementedError