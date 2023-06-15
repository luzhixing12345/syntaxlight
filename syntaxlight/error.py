
from enum import Enum

# 常见 Error 类型

class ErrorCode(Enum):

    # lexer error code
    EXPONENT_NO_DIGITS = 'Exponent has no digits'
    NUMBER_INVALID = "Number invalid"
    UNKNOWN_CHARACTER = 'unknown character'

    # parser error code
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'
    PARAMETERS_NOT_MATCH = 'parameter number not match'    


class Error(Exception):
    def __init__(self, error_code=None, token=None, message: str = None, context: str = None, file_path:str = None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.context = context

        if file_path is not None:
            error_place = f'[{file_path}][{self.token.lineno}:{self.token.column}]'
        else:
            error_place = f'[{self.token.lineno}:{self.token.column}]'
        self.message = f'{error_place} {self.__class__.__name__} {message}\n'


class LexerError(Error):

    def __init__(self, error_code: ErrorCode = None, token=None, context: str = None, file_path:str = None, message:str = None):
        if error_code is not None:
            message = error_code.value + ' : ' + message
        super().__init__(error_code, token, message, context, file_path)


class ParserError(Error):

    def __init__(self, error_code: ErrorCode=None, token=None, context:str=None, file_path:str = None, message:str = None):
        if error_code is not None:
            message = error_code.value + ' : ' + message
        super().__init__(error_code, token,message, context, file_path)
