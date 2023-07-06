from .lexer import Lexer, Token, TokenType, TokenSet
from enum import Enum


class CTokenType(Enum):
    # -----------------------------------------------
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"

    # https://zhuanlan.zhihu.com/p/37908790
    # basic
    VOID = "void"
    CHAR = "char"
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"

    # 修饰性关键字
    SHORT = "short"
    LONG = "long"
    SIGNED = "signed"
    UNSIGNED = "unsigned"

    # 复杂类型关键字
    STRUCT = "struct"
    UNION = "union"
    ENUM = "enum"
    TYPEDEF = "typedef"
    SIZEOF = "sizeof"

    # 存储级别关键字
    AUTO = "auto"
    STATIC = "static"
    REGISTER = "register"
    EXTERN = "extern"
    CONST = "const"
    VOLATILE = "volatile"

    # 流程跳转
    RETURN = "return"
    CONTINUE = "continue"
    BREAK = "break"
    GOTO = "goto"

    # 分支结构
    IF = "if"
    ELSE = "else"
    SWITCH = "switch"
    CASE = "case"
    DEFAULT = "default"

    # 循环结构
    FOR = "for"
    DO = "do"
    WHILE = "while"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------

    POINTER = '*'


class CLexer(Lexer):
    def __init__(self, text: str, TokenType: TokenType = CTokenType):
        super().__init__(text, TokenType)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == "/" and self.peek() == "/":
                return self.get_comment(("//", "\n"))
            if self.current_char == "/" and self.peek() == "*":
                return self.get_comment(("/*", "*/"))

            if self.current_char.isdigit() or self.current_char == TokenType.DOT.value:
                return self.get_number()

            if self.current_char.isalpha() or self.current_char == TokenType.UNDERLINE.value:
                return self.get_id()

            if self.current_char in ("'", '"'):
                return self.get_string()

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)


class CTokenSet:
    def __init__(self) -> None:
        self.storage_class_specifier = TokenSet(
            CTokenType.AUTO,
            CTokenType.REGISTER,
            CTokenType.STATIC,
            CTokenType.EXTERN,
            CTokenType.TYPEDEF
        )
        self.struct_or_union_specifier = TokenSet(
            CTokenType.STRUCT,
            CTokenType.UNION
        )
        self.enum_specifier = TokenSet(CTokenType.ENUM)
        self.type_specifier = TokenSet(
            CTokenType.VOID,
            CTokenType.CHAR,
            CTokenType.SHORT,
            CTokenType.INT,
            CTokenType.LONG,
            CTokenType.FLOAT,
            CTokenType.DOUBLE,
            CTokenType.SIGNED,
            CTokenType.UNSIGNED,
            self.struct_or_union_specifier,
            self.enum_specifier,
            TokenType.ID # identifier
        )
        self.type_qualifier = TokenSet(
            CTokenType.CONST,
            CTokenType.VOLATILE
        )
        self.declaration_specifier = TokenSet(
            self.storage_class_specifier,
            self.type_specifier,
            self.type_qualifier
        )
        self.declarator = TokenSet(
            CTokenType.POINTER,
            TokenType.ID,
            TokenType.LPAREN
        )
        self.function_definition = TokenSet(
            self.declaration_specifier,
            self.declarator
        )
        self.declaration = TokenSet(
            self.declaration_specifier
        )
        self.external_declaration = TokenSet(
            self.function_definition,
            self.declaration
        )
        self.typedef_name = TokenSet(TokenType.ID)
        self.specifier_qualifier = TokenSet(
            self.type_qualifier,
            self.type_specifier
        )
        self.struct_declarator = TokenSet(
            self.declarator,
            TokenType.COLON
        )
        self.struct_declaration = TokenSet(
            self.specifier_qualifier,
            self.struct_declarator
        )