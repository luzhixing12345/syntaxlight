
from enum import Enum

GLOBAL_TOKEN_ID = 0

class BaseTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    # 之间的是保留关键字
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"


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
    LANGLE_BRACE = "<"  # 左尖括号, 如果想表达小于应转换为 LT
    RANGLE_BRACE = ">"  # 右尖括号, 如果想表达大于应转换为 GT
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
    QUESTION = "?"
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
    TEXT = "TEXT"  # 未知的字符
    COMMENT = "COMMENT"
    SHL = "<<"
    SHR = ">>"
    EQ = "=="
    STRICT_EQ = "==="
    NE = "!="
    NORE = "~="
    STRICT_NE = "!=="
    DOUBLE_DIV = "//"
    LT = "LT"  # 小于, 由 LANGLE_BRACE 转换而来
    GT = "GT"  # 大于, 由 RANGLE_BRACE 转换而来
    LE = "<="
    GE = ">="
    MUL_ASSIGN = "*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    ADD_ASSIGN = "+="
    SUB_ASSIGN = "-="
    SHL_ASSIGN = "<<="
    SHR_ASSIGN = ">>="
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
    LAMBDA_POINT = "=>"
    PRODUCTION_SYMBOL = "::="
    DOUBLE_HASH = "##"


class Token:
    def __init__(self, type: Enum, value, line=None, column=None):
        self.type: Enum = type
        self.value: str = value
        self.line: int = line
        self.column: int = column
        self.ast: None
        self.class_list = ["Token"]  # parser 语法分析阶段赋给 token
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

    def add_css(self, CSS: Enum):
        if CSS is not None:
            self.class_list.append(CSS.value)

    def remove_css(self, CSS: Enum):
        if CSS is not None:
            for class_type in self.class_list:
                if class_type == CSS.value:
                    self.class_list.remove(class_type)
                    break

    def __repr__(self):
        return self.__str__()


class TokenSet:
    """
    用于 first set 的构建
    """

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

    def __eq__(self, __value: object) -> bool:
        return self.__contains__(__value)
