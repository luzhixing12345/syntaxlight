
from enum import Enum

# 常见 Error 类型

class ErrorCode(Enum):

    # lexer error code
    EXPONENT_NO_DIGITS = 'Exponent has no digits'
    NUMBER_INVALID = "Number invalid"

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
            error_place = f'[file:{file_path}, line:{self.token.lineno}, column:{self.token.column}]'
        else:
            error_place = f'[line:{self.token.lineno}, column:{self.token.column}]'
        self.message = f'{self.__class__.__name__} {error_place}: {message}'


class LexerError(Error):

    def __init__(self, error_code: ErrorCode = None, token=None, context: str = None, file_path:str = None):
        if error_code is None:
            message = None
        else:
            message = error_code.value
        super().__init__(error_code, token, message, context, file_path)


class ParserError(Error):

    def __init__(self, error_code: ErrorCode=None, token=None, context:str=None, file_path:str = None):
        if error_code is None:
            message = None
        else:
            message = error_code.value
        super().__init__(error_code, token,message, context, file_path)
