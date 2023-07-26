from enum import Enum

# Common error type


class ErrorCode(Enum):
    # lexer error code
    EXPONENT_NO_DIGITS = "Exponent has no digits"
    NUMBER_INVALID = "Number invalid"
    UNKNOWN_CHARACTER = "unknown character"
    UNTERMINATED_COMMENT = "unterminated comment"
    UNTERMINATED_STRING = 'unterminated string'
    MULTICHARACTER_CONSTANT = 'Multi-character character constant'

    # parser error code
    UNEXPECTED_TOKEN = "Unexpected token"
    MISS_EXPECTED_TOKEN = "Miss expected token"
    TRAILING_COMMA = "Trailing comma not allowed"


class Error(Exception):
    def __init__(
        self,
        error_code=None,
        token=None,
        message: str = None,
        context: str = None,
        file_path: str = None,
    ):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.context = context

        if self.token is not None:
            if file_path is not None:
                error_place = f"[{file_path}][{self.token.line}:{self.token.column}]"
            else:
                error_place = f"[{self.token.line}:{self.token.column}]"
            self.message = f"{error_place} {self.__class__.__name__} {message}\n"
        else:
            self.message = message

class LexerError(Error):
    def __init__(
        self,
        error_code: ErrorCode = None,
        token=None,
        context: str = None,
        file_path: str = None,
        message: str = None,
    ):
        if error_code is not None:
            if error_code == ErrorCode.UNEXPECTED_TOKEN:
                message = error_code.value + f" {token.type.name}: " + message
            else:
                message = error_code.value + ": " + message
        super().__init__(error_code, token, message, context, file_path)


class ParserError(Error):
    def __init__(
        self,
        error_code: ErrorCode = None,
        token=None,
        context: str = None,
        file_path: str = None,
        message: str = None,
    ):
        if error_code is not None:
            if error_code == ErrorCode.UNEXPECTED_TOKEN:
                message = error_code.value + f" {token.type.name}: " + message
            else:
                message = error_code.value + ": " + message
        super().__init__(error_code, token, message, context, file_path)
