from enum import Enum
from .token import Token, TokenType

# Common error type


class ErrorCode(Enum):
    # lexer error code
    EXPONENT_NO_DIGITS = "Exponent has no digits"
    NUMBER_INVALID = "Number invalid"
    UNKNOWN_CHARACTER = "unknown character"
    UNTERMINATED_COMMENT = "unterminated comment"
    UNTERMINATED_STRING = "unterminated string"
    MULTICHARACTER_CONSTANT = "Multi-character character constant"

    # parser error code
    UNEXPECTED_TOKEN = "Unexpected token"
    MISS_EXPECTED_TOKEN = "Miss expected token"
    TRAILING_COMMA = "Trailing comma not allowed"
    BRACE_MISS_MATCH = "brace number miss match"


class TTYColor(Enum):
    BLACK = 30
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    MAGENTA = 95
    CYAN = 96
    WHITE = 97


def ttyinfo(text: str, color: TTYColor = TTYColor.RED, underline=False) -> str:
    """
    tty 彩色输出, 默认红色
    """
    ESC = "\033"
    UNDERLINE = 4
    if underline:
        return f"{ESC}[{color.value}m{ESC}[{UNDERLINE}m{text}{ESC}[0m"
    else:
        return f"{ESC}[{color.value}m{text}{ESC}[0m"


class Error(Exception):
    def __init__(
        self,
        token: Token = None,
        error_code: ErrorCode = None,
        error_context: str = None,
        error_message: str = None,
        file_path: str = None,
    ):
        self.token = token  # 当前 token 信息
        self.error_code = error_code  # 错误类型
        self.error_context = error_context  # 错误上下文
        self.error_message = error_message  # 错误信息
        self.file_path = file_path

        # 自定义错误信息, 如果不为 None 则覆盖默认错误信息
        self.self_error_info = None
        
        # 错误信息输出格式配置
        self.context_range = 3  # 发生错误时 token 的前后文行数, 默认上下 3 行

    def __str__(self) -> str:
        return self.__repr__()
    
    def error_format(self) -> str:
        """
        仿 rust 错误输出格式

          --> src/main.rs:33:9
           |
        33 |     let result = loop {
           |         ^^^^^^ help: if this is intentional, prefix it with an underscore: `_result`
           |
           = note: `#[warn(unused_variables)]` on by default
        """
        lines = self.error_context.split("\n")
        lines.insert(0, [])

        # 对于 EOF 特殊处理
        if self.token.type == TokenType.EOF:
            # token.line += 1
            self.token.value = " "

        context_start_line = max(self.token.line - self.context_range, 1)
        context_end_line = min(self.token.line + self.context_range, len(lines))
        context = ""

        # token 为多行文本的处理
        current_context_line = self.token.line  # 当前处于哪一行, 从下往上找
        token_length = len(self.token.value)
        token_lines = []  # token 的所占行
        column = self.token.column  # 当前列

        #  如果当前行的列数少于 token 的长度, 说明 token 跨行, 将当前行加入到 token_lines 中并且继续到上一行去找
        while column < token_length:
            token_length -= column
            token_lines.insert(0, current_context_line)
            current_context_line -= 1
            column = len(lines[current_context_line]) + 1  # +1 是考虑结尾的换行符

        # 多行退出时和单行的情况
        if token_length != 0:
            token_lines.insert(0, current_context_line)

        left_space_length = len(str(token_lines[-1]))
        for i in range(context_start_line, context_end_line):
            # print(i, token.lineno)
            if i not in token_lines:
                context += ttyinfo(" " * left_space_length + " | ", TTYColor.BLUE)
                context += lines[i] + "\n"
            else:
                if len(token_lines) == 1:
                    # token 前面的部分
                    pre_context = lines[i][: self.token.column - token_length]
                    # token 后面的部分
                    end_context = lines[i][self.token.column :]

                    context += (
                        ttyinfo(str(i) + " | ", TTYColor.BLUE)
                        + pre_context
                        + ttyinfo(self.token.value, underline=True)
                        + end_context
                        + "\n"
                    )
                else:
                    if i == token_lines[0]:
                        context += ttyinfo(str(i) + " | ", TTYColor.BLUE)
                        pre_context = lines[i][: column - token_length]
                        context += pre_context + ttyinfo(lines[i][column - token_length :], underline=True) + "\n"
                    elif i == token_lines[-1]:
                        end_context = lines[i][self.token.column + 1 :]
                        context += ttyinfo(" " * left_space_length + " | ", TTYColor.BLUE)
                        context += ttyinfo(lines[i][: self.token.column + 1]) + f"{end_context}\n"
                    else:
                        context += ttyinfo(" " * left_space_length + " | ", TTYColor.BLUE)
                        context += ttyinfo(lines[i]) + "\n"

        return context

    def __repr__(self) -> str:
        
        # 自定义错误信息
        if self.self_error_info is not None:
            return self.self_error_info

        # 默认错误信息
        token_info = f"{repr(self.token.value)} [{self.token.type.name}]"
        error_position = (
            " " * len(str(self.token.line))
            + ttyinfo("--> ", TTYColor.BLUE)
            + self.file_path
            + f":{self.token.line}:{self.token.column}\n"
        )
        error_context = self.error_format()
        error_info = (
            (
                " " * len(str(self.token.line))
                + ttyinfo(" = ", TTYColor.BLUE)
                + f"{ttyinfo('note', TTYColor.YELLOW)}: {self.error_message}"
            )
            if self.error_message != ""
            else ""
        )

        message = f"\n{ttyinfo(self.__class__.__name__)}: {self.error_code.value} {token_info}\n"
        message += f"{error_position}\n{error_context}{error_info}\n\n"
        return message


class LexerError(Error):
    def __init__(
        self,
        token: Token = None,
        error_code: ErrorCode = None,
        error_context: str = None,
        error_message: str = None,
        file_path: str = None,
    ):
        super().__init__(token, error_code, error_context, error_message, file_path)


class ParserError(Error):
    def __init__(
        self,
        token: Token = None,
        error_code: ErrorCode = None,
        error_context: str = None,
        error_message: str = None,
        file_path: str = None,
    ):
        super().__init__(token, error_code, error_context, error_message, file_path)
