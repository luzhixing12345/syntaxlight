
from .lexer import Token, Lexer
from enum import Enum

class CTokenType(Enum):
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
    ID  = 'ID'
    STRING = 'STRING'

    # -----------------------------------------------
    # start - end 之间为对应语言的保留关键字
    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # https://zhuanlan.zhihu.com/p/37908790
    # 基本数据类型
    VOID = 'void'
    CHAR = 'char'
    INT  = 'int'
    FLOAT = 'float'
    DOUBLE = 'double'

    # 修饰性关键字
    SHORT = 'short'
    LONG = 'long'
    SIGNED = 'signed'
    UNSIGNED = 'unsigned'

    # 复杂类型关键字
    STRUCT = 'struct'
    UNION = 'union'
    ENUM = 'enum'
    TYPEDEF = 'typedef'
    SIZEOF = 'sizeof'

    # 存储级别关键字
    AUTO = 'auto'
    STATIC = 'static'
    REGISTER = 'register'
    EXTERN = 'extern'
    CONST = 'const'
    VOLATILE = 'volatile'

    # 流程跳转
    RETURN = 'return'
    CONTINUE = 'continue'
    BREAK = 'break'
    GOTO = 'goto'

    # 分支结构
    IF = 'if'
    ELSE = 'else'
    SWITCH = 'switch'
    CASE = 'case'
    DEFAULT = 'default'
    
    # 循环结构
    FOR = 'for'
    DO    = 'do'
    WHILE = 'while'

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------

class CLexer(Lexer):

    def __init__(self, text):
        
        super().__init__(text, CTokenType)

    def get_number(self):

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        return Token(CTokenType.ID, result, self.line, self.column)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char == CTokenType.SPACE.value:
                return self.skip_whitespace()     
            
            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.get_id()
        
            if self.current_char in ('\'','\"'):
                return self.skip_string()

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = CTokenType(self.current_char)
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
        return Token(type=CTokenType.EOF, value=None)
    
