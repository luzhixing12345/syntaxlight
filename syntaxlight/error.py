
from enum import Enum


# 常见 Error 类型

class ErrorCode(Enum):
    ERROR_UNEXPECTED_TOKEN = 'Unexpected token'
    ERROR_ID_NOT_FOUND = 'Identifier not found'
    ERROR_DUPLICATE_ID = 'Duplicate id found'
    ERROR_PARAMETERS_NOT_MATCH = 'parameter number not match'


class LexerErrorCode(Enum):

    ERROR_UNEXPECTED_TOKEN = 'Unexpected token'
    ERROR_EXPONENT_NO_DIGITS = 'Exponent has no digits'
    ERROR_NUMBER_INVALID = "Number invalid"


class Error(Exception):
    def __init__(self, error_code=None, token=None, message: str = None, context: str = None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.context = context
        self.message = f'{self.__class__.__name__} [line:{self.token.lineno}, column:{self.token.column}]: {message}'


class LexerError(Error):

    def __init__(self, error_code: LexerErrorCode = None, token=None, context: str = None):
        message = error_code.value
        super().__init__(error_code, token, message, context)


class ParserError(Error):

    def __init__(self, error_code=None, token=None, message=None):
        super().__init__(error_code, token, message)
