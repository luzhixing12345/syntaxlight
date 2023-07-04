from enum import Enum
from ..error import ErrorCode, LexerError

GLOBAL_TOKEN_ID = 0


class TokenType(Enum):
    # 所有基本 Token 类型
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    SLASH = "/"
    ASSIGN = "="
    BACK_SLASH = "\\"
    LPAREN = "("
    RPAREN = ")"
    LSQUAR_PAREN = "["
    RSQUAR_PAREN = "]"
    LCURLY_BRACE = "{"
    RCURLY_BRACE = "}"
    LANGLE_BRACE = "<"
    RANGLE_BRACE = ">"
    UNDERLINE = "_"
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
    CHAR = "CHAR"  # CHAR 表示单个字符, 即 'a'
    STR = "STR"  # STR 表示 "" | '' 包裹的字符串
    NUMBER = "NUMBER"  # 整数 | 小数 | 科学计数法
    INT = "INT"  # 整数
    FLOAT = "FLOAT"  # 小数
    COMMENT = "COMMENT"
    SHL = "<<"
    SHR = ">>"
    EQ = "=="
    NE = "!="
    LE = "<="
    GE = ">="
    VARARGS = "..."
    DB_COLON = "::"


class TTYColor(Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class Token:
    def __init__(self, type: Enum, value, line=None, column=None):
        self.type: Enum = type
        self.value = value
        self.line: int = line
        self.column: int = column
        self.ast: None
        self.ast_types = ["Token"]  # parser 语法分析阶段赋给 token
        self.brace_depth = -1  # ([{<>}]) 的深度
        global GLOBAL_TOKEN_ID
        self._id = GLOBAL_TOKEN_ID
        GLOBAL_TOKEN_ID += 1

    def get_css_class(self):
        # 转 html 时的 span class
        css_class = ""
        for ast_type in self.ast_types:
            css_class += f"{ast_type} "

        if self.brace_depth != -1:
            css_class += f"depth-{self.brace_depth%3} "
        css_class += self.type.name
        return css_class

    def __str__(self):
        """
        ID 指创建的索引值
        column 指该 token 最后一个字符的位置
        """
        return "Token[id:{ID}]({type}, {value}, position={lineno}:{column}) {AST_type}".formatter(
            ID=self._id,
            type=self.type,
            value=repr(self.value),
            lineno=self.line,
            column=self.column,
            AST_type=self.get_css_class(),
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

        # 获取 RESERVED_KEYWORD_START - RESERVED_KEYWORD_END 之间的保留关键字
        tt_list = list(LanguageTokenType)
        start_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_START)
        end_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_END)
        self.reserved_keywords = {
            token_type.value: token_type for token_type in tt_list[start_index + 1 : end_index]
        }
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        # \n \t \v \r \f \b
        self.invisible_characters = {
            TokenType.LF.value: TokenType.LF,
            TokenType.TAB.value: TokenType.TAB,
            TokenType.VERTICAL_TAB.value: TokenType.VERTICAL_TAB,
            TokenType.CR.value: TokenType.CR,
            TokenType.FORM_FEED.value: TokenType.FORM_FEED,
            TokenType.BACKSPACE.value: TokenType.BACKSPACE,
        }

    def colorful_info(self, text: str, color: TTYColor = TTYColor.RED) -> str:
        """
        tty 彩色输出, 默认红色
        """
        ESC = "\033"
        UNDERLINE = 4
        return f"{ESC}[{color.value}m{ESC}[{UNDERLINE}m{text}{ESC}[0m"

    def error(self, error_code: ErrorCode = None, token: Token = None, message: str = ""):
        context = self.get_error_token_context(token)
        raise LexerError(
            error_code=error_code,
            token=token,
            context=context,
            file_path=self.file_path,
            message=message,
        )

    def get_error_token_context(self, token: Token) -> str:
        # 出错时获取上下文

        lines = self.text.split("\n")
        lines.insert(0, [])

        if token.type == TokenType.EOF:
            return ""
        context_start_line = max(token.line - self.context_bias, 1)
        context_end_line = min(token.line + self.context_bias, len(lines))
        context = ""

        # token 为多行文本的处理
        token_line = token.line  # 当前处于哪一行, 从后往前找
        token_length = len(token.value)
        token_lines = []  # token 的行列数
        column = token.column + 1
        while column < token_length:
            token_length -= column
            token_lines.insert(0, token_line)
            token_line -= 1
            column = len(lines[token_line]) + 1

        if token_length != 0:
            token_lines.insert(0, token_line)

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
                    context += pre_context + self.colorful_info(token.value) + end_context + "\n"
                else:
                    if i == token_lines[0]:
                        pre_context = lines[i][: column - token_length]
                        context += (
                            pre_context
                            + self.colorful_info(lines[i][column - token_length :])
                            + "\n"
                        )
                    elif i == token_lines[-1]:
                        end_context = lines[i][token.column + 1 :]
                        context += (
                            self.colorful_info(lines[i][: token.column + 1]) + f"{end_context}\n"
                        )
                    else:
                        context += self.colorful_info(lines[i]) + "\n"

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
            self.invisible_characters[self.current_char],
            self.current_char,
            self.line,
            self.column,
        )
        self.advance()
        return token

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def get_number(self) -> Token:
        """
         <digit> ::= [0-9]
        <digits> ::= <digit>*
        <number> ::= <digits>(.<digits>)?(E|e[+-]?<digits>)?
        """

        result = ""
        # <digits>
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        # (.<digits>)?
        if self.current_char == ".":
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        # (E|e[+-]?<digits>)?
        if self.current_char == "e" or self.current_char == "E":
            result += self.current_char
            self.advance()
            if self.current_char in (TokenType.MINUS.value, TokenType.PLUS.value):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
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
        'xxx' "xxx" \"\"\"xxx\"\"\" '''xxx''' 都可以
        """
        result = self.current_char
        if result not in (TokenType.QUOTO.value, TokenType.APOSTROPHE.value):
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
                        Token(TokenType.STRING, result, self.line, self.column),
                    )
                result += self.current_char
            self.advance()

        result += end_character
        self.advance()
        # ''' or """
        if len(result) == 2 and self.current_char == end_character:
            result += self.current_char
            self.advance()
            count = 0
            while self.current_char is not None and count != 3:
                if self.current_char == end_character:
                    count += 1
                else:
                    count = 0
                result += self.current_char
                if self.current_char == "\\":
                    self.advance()
                    if self.current_char is None:
                        self.error(
                            ErrorCode.UNEXPECTED_TOKEN,
                            Token(TokenType.STRING, result, self.line, self.column),
                        )
                    count = 0
                    result += self.current_char
                self.advance()

        token = Token(TokenType.STR, result, self.line, self.column)
        return token

    def get_id(self):
        """
        获取标识符, 留给后续的语法分析处理

        <letter> ::= [A-Za-z]
         <digit> ::= [0-9]
            <id> ::= (<letter>|_)(<letter>|_|<digit>)*

        此函数应次于 get_number 调用
        """
        result = ""
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()

        token_type = self.reserved_keywords.get(result)

        if token_type is None:
            token = Token(type=TokenType.ID, value=result, line=self.line, column=self.column - 1)
        else:
            # reserved keyword
            token = Token(type=token_type, value=result, line=self.line, column=self.column - 1)
        return token

    def get_next_token(self) -> Token:
        """
        while self.current_char is not None:
            # do something
        """
        raise NotImplementedError
