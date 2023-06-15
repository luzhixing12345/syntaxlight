
from enum import Enum
from ..error import *

GLOBAL_TOKEN_ID = 0

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
    RSQUAR_PAREN = ']'
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
        self.ast: None
        self.ast_types = ['Token'] # parser 语法分析阶段赋给 token
        self.brace_depth = -1 # ([{<>}]) 的深度
        global GLOBAL_TOKEN_ID
        self._id = GLOBAL_TOKEN_ID
        GLOBAL_TOKEN_ID += 1
        

    def get_css_class(self):
        # 转 html 时的 span class
        css_class = ''
        for ast_type in self.ast_types:
            css_class += f'{ast_type} '
        
        if self.brace_depth != -1:
            css_class += f'depth-{self.brace_depth%3} '
        css_class += self.type.name
        return css_class
    
    def __str__(self):
        """
        String representation of the class instance.
        """
        return 'Token[id:{ID}]({type}, {value}, position={lineno}:{column}) {AST_type}'.format(
            ID=self._id,
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
            AST_type=self.get_css_class()
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
        self.TokenType:TokenType = TokenType
        self.LanguageTokenType:Enum = LanguageTokenType
        self.context_bias = 10 # 发生错误时 token 的前后文行数
        self.file_path = None # 手动修改文件路径, 用于后期错误处理的输出

        # 获取 RESERVED_KEYWORD_START - RESERVED_KEYWORD_END 之间的保留关键字
        tt_list = list(LanguageTokenType)
        try:
            start_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_START)
            end_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_END)
        except:
            print("LanguageTokenType should keep the keywords between RESERVED_KEYWORD_START and RESERVED_KEYWORD_END")
            exit(1)
        self.reserved_keywords = {
            token_type.value: token_type
            for token_type in tt_list[start_index+1:end_index]
        }
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        # \n \t \v \r \f \b
        self.invisible_characters = {
            TokenType.NEWLINE.value: TokenType.NEWLINE,
            TokenType.TAB.value: TokenType.TAB,
            TokenType.VERTICAL_TAB.value: TokenType.VERTICAL_TAB,
            TokenType.CARRIAGE_RETURN.value: TokenType.CARRIAGE_RETURN,
            TokenType.FORM_FEED.value: TokenType.FORM_FEED,
            TokenType.BACKSPACE.value: TokenType.BACKSPACE,
        }

    def error(self, error_code: ErrorCode = None, token:Token = None, message:str = None):
        context = self.get_context(token)
        raise LexerError(error_code=error_code, token=token, context=context, file_path=self.file_path, message=message)
    
    def get_context(self, token: Token):
        # 出错时获取上下文
        
        # token 的 lineno 和 column 从 1 开始的
        #  abcdajk123123
        #
        # |
        # column 指的是前面的位置
        lines = self.text.split('\n')
        lines.insert(0, [])
        start_line = max(token.lineno-self.context_bias,1)
        end_line = min(token.lineno+self.context_bias, len(lines))
        context = ''
        for i in range(start_line, end_line):
            # print(i, token.lineno)
            if i != token.lineno:
                context += lines[i] + '\n'
            else:        
                token_length = len(token.value)
                # token 前面的部分
                pre_context = lines[i][:token.column - token_length]
                end_context = lines[i][token.column:]

                context += pre_context + f'\033[31m{token.value}\033[0m' + end_context + '\n'
                context += ' ' * len(pre_context) + '^' * token_length + '\n'
                print("error", token)
                # print(len(lines[i]), token.column - token_length, lines[i][:token.column - token_length])
                # print(pre_context)

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
        return Token(self.TokenType.SPACE, result, self.line, self.column - 1)

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

        if self.current_char == self.TokenType.DOT.value:
            result += self.current_char
            self.advance()
            if use_scientific_notation:
                self.error(ErrorCode.NUMBER_INVALID, Token(self.TokenType.NUMBER, result,self.line, self.column))

        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == 'e' or self.current_char == 'E':
            result += self.current_char
            self.advance()
            if use_scientific_notation:
                self.error(ErrorCode.NUMBER_INVALID, Token(self.TokenType.NUMBER, result,self.line, self.column))
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == self.TokenType.DOT.value or self.current_char == 'e' or self.current_char == 'E':
            result += self.current_char
            self.advance()
            self.error(ErrorCode.NUMBER_INVALID, Token(self.TokenType.NUMBER, result,self.line, self.column))

        if result[-1] == 'e' or result[-1] == 'E':
            self.error(ErrorCode.EXPONENT_NO_DIGITS, Token(self.TokenType.NUMBER, result,self.line, self.column))

        return Token(self.TokenType.NUMBER, result, self.line, self.column -1)

    def get_string(self):
        '''
        严格双引号 ""
        '''
        result = self.current_char
        if result != self.TokenType.QUOTO_MARK.value:
            token = Token(self.TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)
        end_character = self.TokenType.QUOTO_MARK.value
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            result += self.current_char
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.error()
                result += self.current_char
            self.advance()
        
        result += end_character
        token = Token(self.TokenType.STRING, result, self.line, self.column)
        self.advance()
        return token

    def get_str(self):
        '''
        单引号 ' 和 双引号 " 都可以
        '''
        result = self.current_char
        if result not in (self.TokenType.QUOTO_MARK.value, self.TokenType.APOSTROPHE.value):
            token = Token(self.TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)
        end_character = self.current_char  # 结束标志一定是和开始标志相同的
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            result += self.current_char
            if self.current_char == '\\':
                self.advance()
                if self.current_char is None:
                    self.error(ErrorCode.UNEXPECTED_TOKEN, Token(self.TokenType.STRING, result, self.line, self.column))
                result += self.current_char
            self.advance()
        
        result += end_character
        token = Token(self.TokenType.STRING, result, self.line, self.column)
        self.advance()
        return token

    def get_id(self):
        """Handle identifiers and reserved keywords"""
        value = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()

        token_type = self.reserved_keywords.get(value)
        
        if token_type is None:
            token = Token(type=self.TokenType.ID, value=value,lineno=self.line, column=self.column -1)
        else:
            # reserved keyword
            token = Token(type=token_type, value=value,lineno=self.line, column=self.column -1)
        return token

    def get_next_token(self) -> Token:
        '''
        while self.current_char is not None:
            # do something
        '''
        raise NotImplementedError
