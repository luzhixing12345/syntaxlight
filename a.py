
from enum import Enum

class JsonTokenType(Enum):
    # single-character token types
    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # 在这里添加对应语言的保留关键字
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'



class aJsonTokenType(Enum):
    # single-character token types
    RESERVED_KEYWORD_START = 'RESERVED_KEYWORD_START'

    # 在这里添加对应语言的保留关键字
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'

    RESERVED_KEYWORD_END = 'RESERVED_KEYWORD_END'


class Token:
    def __init__(self, type:Enum, value, lineno=None, column=None):
        self.type:Enum = type
        self.value = value
        self.lineno:int = lineno
        self.column:int = column

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER_CONST, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()
    

token = Token(JsonTokenType.FALSE, "false")

print(JsonTokenType.RESERVED_KEYWORD_START == aJsonTokenType.RESERVED_KEYWORD_START)