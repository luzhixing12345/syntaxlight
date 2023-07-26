from enum import Enum
from ..error import ErrorCode, LexerError
from typing import Dict, List, Tuple
import re

GLOBAL_TOKEN_ID = 0

# class NewTokenType(Enum):
#     RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
#     RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


class TokenType(Enum):
    # 所有基本 Token 类型
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    ASSIGN = "="
    BACK_SLASH = "\\"
    LPAREN = "("
    RPAREN = ")"
    LSQUAR_PAREN = "["
    RSQUAR_PAREN = "]"
    LCURLY_BRACE = "{"
    RCURLY_BRACE = "}"
    LANGLE_BRACE = "<"  # => LT
    RANGLE_BRACE = ">"  # => GT
    UNDERLINE = "_"
    SEMI = ";"
    DOT = "."
    COLON = ":"
    COMMA = ","
    HASH = "#"
    DOLLAR = "$"
    MOD = "%"
    CARET = "^"
    AMPERSAND = "&"
    PIPE = "|"
    QUSTION = "?"
    APOSTROPHE = "'"
    QUOTO = '"'
    SPACE = " "
    CR = "\r"
    LF = "\n"
    TAB = "\t"
    VERTICAL_TAB = "\v"
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
    STRING = "STRING"  # STRING 表示严格意义上的字符串, 即 "" 两个双引号包裹的
    CHARACTER = "CHARACTER"  # CHARACTER 表示单个字符, 即 'a'
    STR = "STR"  # STR 表示 "" | '' 包裹的字符串
    NUMBER = "NUMBER"  # 整数 | 小数 | 科学计数法
    INT = "INT"  # 整数
    FLOAT = "FLOAT"  # 小数
    COMMENT = "COMMENT"
    SHL = "<<"
    SHR = ">>"
    EQ = "=="
    STRICT_EQ = "==="
    NE = "!="
    NORE = "~="
    STRICT_NE = "!=="
    DOUBLE_DIV = "//"
    LT = "LT"  # => LANGLE_BRACE
    GT = "GT"  # => RANGLE_BRACE
    LE = "<="
    GE = ">="
    MUL_ASSIGN = "*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    ADD_ASSIGN = "+="
    SUB_ASSIGN = "-="
    LSHIFT_ASSIGN = "<<="
    RSHIFT_ASSIGN = ">>="
    AND_ASSIGN = "&="
    XOR_ASSIGN = "^="
    OR_ASSIGN = "|="
    CONCAT = ".."
    VARARGS = "..."
    DOUBLE_COLON = "::"
    INC = "++"
    DEC = "--"
    OR = "||"
    AND = "&&"
    POINT = "->"
    PRODUCTION_SYMBOL = "::="
    DOUBLE_HASH = "##"


class TTYColor(Enum):
    BLACK = 30
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    MAGENTA = 95
    CYAN = 96
    WHITE = 97


class Token:
    def __init__(self, type: Enum, value, line=None, column=None):
        self.type: Enum = type
        self.value = value
        self.line: int = line
        self.column: int = column
        self.ast: None
        self.class_list = set()  # parser 语法分析阶段赋给 token
        self.class_list.add("Token")
        global GLOBAL_TOKEN_ID
        self._id = GLOBAL_TOKEN_ID
        GLOBAL_TOKEN_ID += 1

    def get_css_class(self):
        # 转 html 时的 span class
        css_class = ""

        for class_type in self.class_list:
            css_class += f"{class_type} "

        css_class += self.type.name
        return css_class

    def __str__(self):
        """
        ID 指创建的索引值
        column 指该 token 最后一个字符的位置
        """
        return "Token[{ID}]({type}, {value}, position={lineno}:{column})".format(
            ID=self._id,
            type=self.type,
            value=repr(self.value),
            lineno=self.line,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()


class Lexer:
    """
    Lexer 基类, 提供了一些基础函数和功能, 比如匹配数字, 匹配字符串

        可能有些编程语言的处理(比如Lua的字符串)不同, 单独覆盖即可

    继承 Lexer 的子类需要重写其 get_next_token 方法以提供给后续的 parser 解析
    """

    def __init__(self, text: str, LanguageTokenType: Enum):
        self.text: str = text
        self.pos: int = 0  # 当前指针指向的字符
        self.current_char: str = self.text[self.pos]  # 当前指针指向的字符
        self.line: int = 1
        self.column: int = 1  # 指向 token 的 value 中最后出现的字符的位置
        self.LanguageTokenType: Enum = LanguageTokenType
        self.context_bias = 10  # 发生错误时 token 的前后文行数
        self.file_path = None  # 手动修改文件路径, 用于后期错误处理的输出
        self._status_stack = []  # 状态栈

        # 获取 RESERVED_KEYWORD_START - RESERVED_KEYWORD_END 之间的保留关键字
        tt_list = list(LanguageTokenType)
        start_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_START)
        end_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_END)
        self.reserved_keywords = {
            token_type.value: token_type for token_type in tt_list[start_index + 1 : end_index]
        }
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        # \n \t \v \r \f \b
        self.invisible_characters = [
            TokenType.LF.value,
            TokenType.TAB.value,
            TokenType.VERTICAL_TAB.value,
            TokenType.CR.value,
            TokenType.FORM_FEED.value,
            TokenType.BACKSPACE.value,
        ]

        # 匹配长字符串时使用
        # if self.current_char in self.long_op_dict:
        #     return self.get_long_op()
        self.long_op_dict: Dict[str, List] = {}

    def build_long_op_dict(self, supported_long_op: List[str]):
        """
        构造长运算符的匹配模式
        """
        self._long_ops = sorted(supported_long_op, key=len, reverse=True)
        for long_op in self._long_ops:
            assert len(long_op) >= 2, f"{long_op} should be longer"
            if self.long_op_dict.get(long_op[0]) is None:
                self.long_op_dict[long_op[0]] = []
            self.long_op_dict[long_op[0]].append(long_op[1:])

    def ttyinfo(self, text: str, color: TTYColor = TTYColor.RED, underline=True) -> str:
        """
        tty 彩色输出, 默认红色
        """
        ESC = "\033"
        UNDERLINE = 4
        if underline:
            return f"{ESC}[{color.value}m{ESC}[{UNDERLINE}m{text}{ESC}[0m"
        else:
            return f"{ESC}[{color.value}m{text}{ESC}[0m"

    def _record(self):
        """
        用于 parser 中 peek_next_token

        记录当前 lexer 解析状态, 被 _reset 调用时恢复
        """
        # 采用栈的方式保存数据状态, 避免由于 peek_next_token 中的 eat 导致多次嵌套调用覆盖数据
        self._status_stack.append(
            {"pos": self.pos, "c": self.current_char, "line": self.line, "column": self.column}
        )

    def _reset(self):
        """
        用于 parser 中 peek_next_token

        恢复为 lexer 之前的状态
        """
        status = self._status_stack.pop()
        self.pos = status["pos"]
        self.current_char = status["c"]
        self.line = status["line"]
        self.column = status["column"]

    def error(self, error_code: ErrorCode = None, token: Token = None, message: str = ""):
        raise LexerError(
            error_code=error_code,
            token=token,
            context=self.get_error_token_context(token),
            file_path=self.file_path,
            message=message,
        )

    def get_error_token_context(self, token: Token) -> str:
        """
        出错时获取上下文
        """
        lines = self.text.split("\n")
        lines.insert(0, [])

        if token.type == TokenType.EOF:
            return ""
        context_start_line = max(token.line - self.context_bias, 1)
        context_end_line = min(token.line + self.context_bias, len(lines))
        context = ""

        # token 为多行文本的处理
        current_context_line = token.line  # 当前处于哪一行, 从下往上找
        token_length = len(token.value)
        token_lines = []  # token 的所占行
        column = token.column  # 当前行

        #  如果当前行的列数少于 token 的长度, 说明 token 跨行, 将当前行加入到 token_lines 中并且继续到上一行去找
        while column < token_length:
            token_length -= column
            token_lines.insert(0, current_context_line)
            current_context_line -= 1
            column = len(lines[current_context_line]) + 1  # +1 是考虑结尾的换行符

        # 多行退出时和单行的情况
        if token_length != 0:
            token_lines.insert(0, current_context_line)

        # 单行 token
        if len(token_lines) == 0:
            token_lines.append(token.line)
            token_length = len(token.value)

        for i in range(context_start_line, context_end_line):
            # print(i, token.lineno)
            if i not in token_lines:
                context += lines[i] + "\n"
            else:
                if len(token_lines) == 1:
                    # token 前面的部分
                    pre_context = lines[i][: token.column - token_length]
                    # token 后面的部分
                    end_context = lines[i][token.column :]
                    context += pre_context + self.ttyinfo(token.value) + end_context + "\n"
                else:
                    if i == token_lines[0]:
                        pre_context = lines[i][: column - token_length]
                        context += (
                            pre_context + self.ttyinfo(lines[i][column - token_length :]) + "\n"
                        )
                    elif i == token_lines[-1]:
                        end_context = lines[i][token.column + 1 :]
                        context += self.ttyinfo(lines[i][: token.column + 1]) + f"{end_context}\n"
                    else:
                        context += self.ttyinfo(lines[i]) + "\n"

        return context

    def advance(self):
        """
        获取下一个字符, 遇到换行则更新 line
        """
        if self.current_char == "\n":
            self.line += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # 结束
            self.column += 1
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def skip_whitespace(self):
        """
        通常来说直接跳过空格即可, 这里保留空格是为了不破坏原本的代码格式
        """
        result = ""
        while self.current_char is not None and self.current_char == " ":
            result += " "
            self.advance()
        return Token(TokenType.SPACE, result, self.line, self.column - 1)

    def skip_invisiable_character(self):
        token = Token(
            TokenType(self.current_char),
            self.current_char,
            self.line,
            self.column,
        )
        self.advance()
        return token

    def peek(self, n: int = 1):
        """
        向后看 n 个字符
        """
        peek_pos = self.pos + n
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[self.pos + 1 : peek_pos + 1]

    def get_number(self, accept_float = True, accept_hex = False, accept_bit = False, accept_p = False) -> Token:
        """
         <digit> ::= [0-9]
        <digits> ::= <digit>*
        <number> ::= <digits>(.<digits>)?(E|e[+-]?<digits>)?

        @accept_float: 允许小数和科学计数法
        @accept_hex  : 允许16进制表示 0xfff
        @accept_bit  : 允许二进制表示 0b111
        """
        bit_matching_status = False
        hex_matching_status = False
        def is_match_char(char:str) -> bool:
            
            if hex_matching_status:
                return bool(re.match(r'[0-9a-fA-F]',char))
            if bit_matching_status:
                return bool(re.match(r'[01]',char))
            return char.isdigit()

        result = ""

        if accept_hex:
            if self.current_char == '0' and self.peek() in ('x', 'X'):
                result = self.current_char
                self.advance()
                result += self.current_char
                self.advance()
                hex_matching_status = True

        if accept_bit:
            if self.current_char == '0' and self.peek() in ('b', 'B'):
                result = self.current_char
                self.advance()
                result += self.current_char
                self.advance()
                # 如果此时已经处于 hex_matching_status 状态了则忽略 
                if not hex_matching_status:
                    bit_matching_status = True


        # <digits>
        while self.current_char is not None and is_match_char(self.current_char):
            result += self.current_char
            self.advance()

        if accept_float:
            # (.<digits>)?
            if self.current_char == ".":
                result += self.current_char
                self.advance()
                while self.current_char is not None and is_match_char(self.current_char):
                    result += self.current_char
                    self.advance()

            # (E|e[+-]?<digits>)?
            if self.current_char == "e" or self.current_char == "E":
                result += self.current_char
                self.advance()
                if self.current_char in (TokenType.MINUS.value, TokenType.PLUS.value):
                    result += self.current_char
                    self.advance()
                while self.current_char is not None and is_match_char(self.current_char):
                    result += self.current_char
                    self.advance()
        
        if accept_p:
            if self.current_char in ('P','p'):
                result += self.current_char
                self.advance()
                if self.current_char in (TokenType.MINUS.value, TokenType.PLUS.value):
                    result += self.current_char
                    self.advance()
                while self.current_char is not None and is_match_char(self.current_char):
                    result += self.current_char
                    self.advance()

        # column - 1, 因为判断结束需要跳出 number
        return Token(TokenType.NUMBER, result, self.line, self.column - 1)

    def get_string(self):
        """
        严格双引号 ""
        """
        result = self.current_char
        if result != TokenType.QUOTO.value:
            token = Token(TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)
        end_character = TokenType.QUOTO.value
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            result += self.current_char
            if self.current_char == "\\":
                self.advance()
                if self.current_char is None:
                    self.error()
                result += self.current_char
            self.advance()

        result += end_character
        token = Token(TokenType.STRING, result, self.line, self.column)
        self.advance()
        return token

    def get_str(self):
        """
        匹配 "" 和 '' 之间的字符
        """
        result = self.current_char
        if result not in ("'", '"'):
            token = Token(TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token)
        end_character = self.current_char  # 结束标志一定是和开始标志相同的
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            result += self.current_char
            if self.current_char == "\\":
                self.advance()
                if self.current_char is None:
                    self.error(
                        ErrorCode.UNEXPECTED_TOKEN,
                        Token(TokenType.STRING, result, self.line, self.column - 1),
                    )
                result += self.current_char
            self.advance()

        result += end_character
        token = Token(TokenType.STR, result, self.line, self.column)
        self.advance()
        return token

    def get_extend_str(self, extend_symbol_pair: Tuple[str, str], token_type: Enum = TokenType.STR):
        """
        扩展匹配字符串, 比如 """ """ 和 ''' '''
        """
        start_symbol, end_symbol = extend_symbol_pair
        assert len(start_symbol) > 0 and len(end_symbol) > 0
        assert self.current_char == start_symbol[0]
        if len(start_symbol) > 1:
            assert self.peek(len(start_symbol) - 1) == start_symbol[1:]

        result = start_symbol
        for _ in range(len(start_symbol)):
            self.advance()

        end_symbol_length = len(end_symbol)
        while self.current_char is not None:
            if (
                self.current_char == end_symbol[0]
                and self.peek(end_symbol_length - 1) == end_symbol[1:]
            ):
                break
            else:
                if self.current_char == "\\":
                    result += self.current_char
                    self.advance()
                result += self.current_char
                self.advance()

        if self.current_char is None:
            token = Token(token_type, result, self.line, self.column - 1)
        else:
            result += end_symbol
            for _ in range(end_symbol_length):
                self.advance()
            token = Token(token_type, result, self.line, self.column - 1)

        return token

    def get_id(self, ignore_case=False, extend_chars: List[str] = ["_"]):
        """
        获取标识符, 留给后续的语法分析处理
        @ignore_case : 是否忽略大小写
        @extend_chars: 扩展字符, 默认扩展 "_", 一般还可修改为 ["_", "-"]

        <letter> ::= [A-Za-z]
         <digit> ::= [0-9]
            <id> ::= (<letter>|_)(<letter>|_|<digit>)*

        此函数应次于 get_number 调用
        """
        result = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char in extend_chars
        ):
            result += self.current_char
            self.advance()

        # 忽略关键字的大小写
        if ignore_case:
            token_type = self.reserved_keywords.get(result.upper())
        else:
            token_type = self.reserved_keywords.get(result)

        if token_type is None:
            token = Token(type=TokenType.ID, value=result, line=self.line, column=self.column - 1)
        else:
            # 作为保留关键字
            token = Token(type=token_type, value=result, line=self.line, column=self.column - 1)
        return token

    def get_comment(self, start_symbol="#", end_symbol="\n"):
        """
        跳过注释部分, 单行注释不包括最后的换行

        多个注释的情况分多个 get_comment 函数处理

        python 风格: ("#", "\n")
             C 风格: ("//", "\n"), ("/*", "*/")
        pascal 风格: ("//", "\n"), ("{", "}"), ("(*", "*)")
        """

        assert start_symbol[0] == self.current_char

        result = start_symbol
        for _ in range(len(start_symbol)):
            self.advance()

        end_symbol_length = len(end_symbol)
        while self.current_char is not None:
            if self.current_char == end_symbol[0]:
                if end_symbol_length == 1:
                    # 单行注释不包括最后的换行
                    result += self.current_char
                    break
                elif self.peek(end_symbol_length - 1) == end_symbol[1:]:
                    result += self.current_char
                    for _ in range(end_symbol_length - 1):
                        self.advance()
                        result += self.current_char
                    break
            result += self.current_char
            self.advance()

        # 除单行注释外抛异常
        if self.current_char is None and end_symbol != "\n":
            token = Token(TokenType.COMMENT, result, self.line, self.column - 1)
            self.error(ErrorCode.UNTERMINATED_COMMENT, token)

        if end_symbol == "\n":
            result = result[:-1]
            token = Token(TokenType.COMMENT, result, self.line, self.column - 1)
        else:
            token = Token(TokenType.COMMENT, result, self.line, self.column)
            self.advance()
        return token

    def get_long_op(self):
        """
        对于 '+','-','=','!','<','>','*','/','&','^','|','.',':'
        字符可能需要读入多个以匹配完整
        """
        assert self.current_char in self.long_op_dict
        token_type = TokenType(self.current_char)
        result = self.current_char

        for long_op in self.long_op_dict[self.current_char]:
            if self.peek(len(long_op)) == long_op:
                result = self.current_char + long_op
                token_type = TokenType(result)
                for _ in range(len(long_op)):
                    self.advance()
                break

        token = Token(token_type, result, self.line, self.column)
        self.advance()
        return token

    def get_next_token(self) -> Token:
        """
        while self.current_char is not None:
            # do something
        """
        raise NotImplementedError


class TokenSet:
    def __init__(self, *args) -> None:
        self._token_set = set()
        for arg in args:
            if isinstance(arg, Enum):
                self._token_set.add(arg)

            elif isinstance(arg, TokenSet):
                for token_type in arg._token_set:
                    self._token_set.add(token_type)
            else:
                raise TypeError(args)

    def __contains__(self, item):
        return item in self._token_set
