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

    POINTER = "*"


class CLexer(Lexer):
    def __init__(self, text: str, TokenType: TokenType = CTokenType):
        super().__init__(text, TokenType)
        disable_long_op = ["===","!==","::"]
        self.build_long_op_dict(disable_long_op)

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

            if self.current_char in self.long_op_dict:
                return self.get_long_op()
            try:
                token_type = TokenType(self.current_char)
            except ValueError:
                self.error()
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)


class CTokenSet:
    def __init__(self) -> None:
        self.storage_class_specifier = TokenSet(
            CTokenType.AUTO,
            CTokenType.REGISTER,
            CTokenType.STATIC,
            CTokenType.EXTERN,
            CTokenType.TYPEDEF,
        )
        self.struct_or_union = TokenSet(CTokenType.STRUCT, CTokenType.UNION)
        self.struct_or_union_specifier = TokenSet(self.struct_or_union)
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
            TokenType.ID,  # identifier
        )
        self.type_qualifier = TokenSet(CTokenType.CONST, CTokenType.VOLATILE)
        self.declaration_specifier = TokenSet(
            self.storage_class_specifier, self.type_specifier, self.type_qualifier
        )
        self.declarator = TokenSet(
            TokenType.MUL, TokenType.ID, TokenType.LPAREN  # => CTokenType.POINTER
        )
        self.function_definition = TokenSet(self.declaration_specifier, self.declarator)
        self.declaration = TokenSet(self.declaration_specifier)
        self.external_declaration = TokenSet(self.function_definition, self.declaration)
        self.typedef_name = TokenSet(TokenType.ID)
        self.specifier_qualifier = TokenSet(self.type_qualifier, self.type_specifier)
        self.struct_declarator = TokenSet(self.declarator, TokenType.COLON)
        self.struct_declaration = TokenSet(self.specifier_qualifier, self.struct_declarator)
        self.direct_declaractor = TokenSet(TokenType.ID, TokenType.LPAREN)
        self.direct_delcartor_postfix = TokenSet(
            TokenType.LPAREN, TokenType.LSQUAR_PAREN, TokenType.LPAREN
        )
        self.compound_statement = TokenSet(TokenType.LCURLY_BRACE)
        self.assignment_operator = TokenSet(
            TokenType.ASSIGN,
            TokenType.MUL_ASSIGN,
            TokenType.DIV_ASSIGN,
            TokenType.MOD_ASSIGN,
            TokenType.ADD_ASSIGN,
            TokenType.SUB_ASSIGN,
            TokenType.LSHIFT_ASSIGN,
            TokenType.RSHIFT_ASSIGN,
            TokenType.AND_ASSIGN,
            TokenType.XOR_ASSIGN,
            TokenType.OR_ASSIGN,
        )
        self.unary_operator = TokenSet(
            TokenType.AMPERSAND,
            TokenType.MUL,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.TILDE,
            TokenType.BANG,
        )
        self.constant_expression = TokenSet(
            TokenType.LPAREN,
            CTokenType.SIZEOF,
            TokenType.PLUS_PLUS,
            TokenType.MINUS_MINUS,
            TokenType.STRING,
            TokenType.ID,
            TokenType.NUMBER,
            self.assignment_operator,
            self.unary_operator,
        )
        self.identifier = TokenSet(TokenType.ID, TokenType.NUMBER, TokenType.STRING, TokenType.CHAR)

        self.parameter_list = TokenSet(self.declaration_specifier)
