
from enum import Enum
from ..error import *

class TokenType(Enum):
    # 所有基本 Token 类型
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
    UNDERLINE = '_'
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
    ID = 'ID'
    STRING = 'STRING'  # STRING 表示严格意义上的字符串, 即 "" 两个双引号包裹的
    CHAR = 'CHAR'  # CHAR 表示单个字符, 即 'a'
    STR = 'STR'    # STR 表示 "" | '' 包裹的字符串
    NUMBER = 'NUMBER' # 整数 | 小数 | 科学计数法
    INT = 'INT' # 整数
    FLOAT = 'FLOAT' # 小数
    SHL = '<<'
    SHR = '>>'
    EQ = '=='
    NE = '!='
    LE = '<='
    GE = '>='
    VARARGS = '...'
    DB_COLON = '::'

class Token:
    def __init__(self, type:Enum, value, lineno=None, column=None):
        self.type:Enum = type
        self.value = value
        self.lineno:int = lineno
        self.column:int = column

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

    def __init__(self, text: str, LanguageTokenType: Enum):
        self.text: str = text
        self.pos: int = 0  # 当前指针指向的字符
        self.current_char: str = self.text[self.pos]  # 当前指针指向的字符
        self.line: int = 1
        self.column: int = 1
        self.BaseTokenType:TokenType = TokenType
        self.context_bias = 3 # 发生错误时 token 的前后文行数

        # 获取 RESERVED_KEYWORD_START - RESERVED_KEYWORD_END 之间的保留关键字
        # tt_list = list(LanguageTokenType)
        # try:
        #     start_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_START)
        #     end_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_END)
        # except:
        #     print("LanguageTokenType should keep the keywords between RESERVED_KEYWORD_START and RESERVED_KEYWORD_END")
        #     exit(1)
        # self.reserved_keywords = {
        #     token_type.value: token_type
        #     for token_type in tt_list[start_index+1:end_index]
        # }
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        # \n \t \v \r \f \b
        self.invisible_characters = {
            TokenType.NEWLINE.value: TokenType.NEWLINE,
            TokenType.TAB.value: TokenType.TAB,
            TokenType.VERTICAL_TAB.value: TokenType.VERTICAL_TAB,
            TokenType.CARRIAGE_RETURN.value: TokenType.CARRIAGE_RETURN,
            TokenType.FORM_FEED.value: TokenType.FORM_FEED,
            TokenType.BACKSPACE.value: TokenType.BACKSPACE
        }

    def error(self, error_code: LexerErrorCode = None, token:Token = None):
        context = self.get_context(token)
        raise LexerError(error_code=error_code, token=token, context=context)
    
    def get_context(self, token: Token):
        # 出错时获取上下文
        lines = self.text.split('\n')
        start_line = max(token.lineno-self.context_bias,0)
        end_line = min(token.lineno+self.context_bias, len(lines)-1)
        context = '\n'
        for i in range(start_line, end_line+1):
            # print(i, token.lineno)
            if i != token.lineno -1:
                context += lines[i] + '\n'
            else:
                token_length = len(token.value)
                if token.column == token_length + 1:
                    pre_context = ''
                else:
                    pre_context = lines[i][:token.column-token_length-1]
                if token.column == len(lines[i]):
                    end_context = ''
                else:
                    end_context = lines[i][token.column-1:]
                context += pre_context + f'\033[31m{token.value}\033[0m' + end_context + '\n'
                context += ' ' * (token.column - token_length - 1) + '^' * token_length + '\n'
        context += '\n'
        return context

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
        return Token(self.BaseTokenType.SPACE, result, self.line, self.column)

    def skip_invisiable_character(self):
        token = Token(
            self.invisible_characters[self.current_char], self.current_char, self.line, self.column)
        self.advance()
        return token

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text)-1:
            return None
        else:
            return self.text[peek_pos]

    def get_number(self):

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        use_scientific_notation = False # 科学计数法
        if self.current_char == 'e' or self.current_char == 'E':
            result += self.current_char
            self.advance()
            use_scientific_notation = True

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == self.BaseTokenType.DOT.value:
            result += self.current_char
            self.advance()
            if use_scientific_notation:
                self.error(LexerErrorCode.ERROR_NUMBER_INVALID, Token(self.BaseTokenType.NUMBER, result,self.line, self.column))

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == 'e' or self.current_char == 'E':
            result += self.current_char
            self.advance()
            if use_scientific_notation:
                self.error(LexerErrorCode.ERROR_NUMBER_INVALID, Token(self.BaseTokenType.NUMBER, result,self.line, self.column))
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == self.BaseTokenType.DOT.value or self.current_char == 'e' or self.current_char == 'E':
            result += self.current_char
            self.advance()
            self.error(LexerErrorCode.ERROR_NUMBER_INVALID, Token(self.BaseTokenType.NUMBER, result,self.line, self.column))

        if result[-1] == 'e' or result[-1] == 'E':
            self.error(LexerErrorCode.ERROR_EXPONENT_NO_DIGITS, Token(self.BaseTokenType.NUMBER, result,self.line, self.column))

        return Token(self.BaseTokenType.NUMBER, result, self.line, self.column)

    def get_string(self):
        '''
        严格双引号 ""
        '''
        result = self.current_char
        assert result == self.BaseTokenType.QUOTO_MARK.value
        end_match = self.BaseTokenType.QUOTO_MARK.value
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

        return Token(self.BaseTokenType.STRING, result, self.line, self.column)

    def get_str(self):
        '''
        单引号 ' 和 双引号 " 都可以
        '''
        result = self.current_char
        assert result == self.BaseTokenType.AMPERSAND.value or result == self.BaseTokenType.QUOTO_MARK.value
        end_match = self.current_char  # ' or "
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

        return Token(self.BaseTokenType.STRING, result, self.line, self.column)

    def get_id(self):
        """Handle identifiers and reserved keywords"""

        token = Token(type=None, value=None,
                      lineno=self.line, column=self.column)

        value = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()

        token_type = self.reserved_keywords.get(value)
        if token_type is None:
            token.type = self.BaseTokenType.ID
            token.value = value
        else:
            # reserved keyword
            token.type = token_type
            token.value = value

        return token

    def get_next_token(self) -> Token:
        '''
        while self.current_char is not None:
            # do something
        '''
        raise NotImplementedError
