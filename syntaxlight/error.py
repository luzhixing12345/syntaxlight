from enum import Enum

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
        token_info: str = None,
        error_code: ErrorCode = None,
        error_position: str = None,
        error_context: str = None,
        error_info: str = None,
    ):
        self.message = f'\n{ttyinfo(self.__class__.__name__)}: {error_code.value} {token_info}\n'
        self.message += f'{error_position}{error_context}{error_info}\n\n'

class LexerError(Error):
    def __init__(
        self,
        token_info: str = None,
        error_code: ErrorCode = None,
        error_position: str = None,
        error_context: str = None,
        error_info: str = None,
    ):
        super().__init__(token_info, error_code, error_position, error_context, error_info)


class ParserError(Error):
    def __init__(
        self,
        token_info: str = None,
        error_code: ErrorCode = None,
        error_position: str = None,
        error_context: str = None,
        error_info: str = None,
    ):
        super().__init__(token_info, error_code, error_position, error_context, error_info)
