from .lexer import Lexer, ErrorCode
from enum import Enum
from ..token import Token, TokenType
from ..token import TokenSet

class CTokenType(Enum):
    # -----------------------------------------------
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    _ALIGNOF = "alignof"
    AUTO = "auto"
    BOOL = "bool"
    BREAK = "break"
    CASE = "case"
    CHAR = "char"
    CONST = "const"
    CONSTEXPR = "constexpr"
    CONTINUE = "continue"
    DEFAULT = "default"
    DO = "do"
    DOUBLE = "double"
    ELSE = "else"
    ENUM = "enum"
    EXTERN = "extern"
    FALSE = "false"  # C23
    FLOAT = "float"
    FOR = "for"
    GOTO = "goto"
    IF = "if"
    INLINE = "inline"
    INT = "int"
    LONG = "long"
    NULLPTR = "nullptr"  # C23
    REGISTER = "register"
    RESTRICT = "restrict"
    RETURN = "return"
    SHORT = "short"
    SIGNED = "signed"
    SIZEOF = "sizeof"
    STATIC = "static"
    STATIC_ASSERT = "static_assert"
    STRUCT = "struct"
    SWITCH = "switch"
    THREAD_LOCAL = "thread_local"
    TRUE = "true"  # C23
    TYPEDEF = "typedef"
    TYPEOF = "typeof"  # C23
    TYPEOF_UNQUAL = "typeof_unqual"  # C23
    UNION = "union"
    UNSIGNED = "unsigned"
    VOID = "void"
    VOLATILE = "volatile"
    WHILE = "while"
    _ALIGNAS = "_Alignas"  # C23 => ALIGNAS
    ALIGNAS = "alignas"
    _ATOMIC = "_Atomic"
    _BITINT = "_BitInt"
    _BOOL = "_Bool"  # C23 => BOOL
    _COMPLEX = "_Complex"
    _DECIMAL128 = "_Decimal128"  # C23
    _DECIMAL32 = "_Decimal32"  # C23
    _DECIMAL64 = "_Decimal64"  # C23
    _GENERIC = "_Generic"
    _IMAGINARY = "_Imaginary"
    _NORETURN = "_Noreturn"
    _STATIC_ASSERT = "_Static_assert"  # C23 => STATIC_ASSERT
    _THREAD_LOCAL = "_Thread_local"  # C23 => THREAD_LOCAL

    # GNU C extension
    ASM = "asm"
    _ASM = "__asm__"
    _ATTRIBUTE = "__attribute__"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------

    POINTER = "POINTER"  # 指针 *
    STAR = "STAR"  # 任意占位符 *
    TYPEDEF_ID = "typedef-id"

    # 预处理关键字, 除if else外默认被解析为 ID, 在解析过程中处理
    IF_P = "ifp"  # 预处理命令中的 if
    IFDEF = "ifdef"
    IFNDEF = "ifndef"
    ELIF = "elif"
    ELSE_P = "elsep"  # 预处理命令中的 else
    ENDIF = "endif"
    INCLUDE = "include"
    DEFINE = "define"
    UNDEF = "undef"
    LINE = "line"
    ERROR = "error"
    PRAGMA = "pragma"


class CLexer(Lexer):
    def __init__(self, text: str, TokenType: TokenType = CTokenType):
        super().__init__(text, TokenType)
        supported_long_op = [
            "<<=",
            ">>=",
            "<<",
            ">>",
            "==",
            "!=",
            "<=",
            ">=",
            "*=",
            "/=",
            "%=",
            "+=",
            "-=",
            "&=",
            "^=",
            "|=",
            "...",
            "++",
            "--",
            "||",
            "&&",
            "->",
            "##",
        ]
        self.build_long_op_dict(supported_long_op)

    def get_char(self):
        """
        单字符
        """
        self.advance()
        result = "'" + self.current_char
        if self.current_char == "\\":
            self.advance()
            result += self.current_char
        self.advance()
        if self.current_char != "'":
            token = Token(TokenType.CHARACTER, result, self.line, self.column)
            self.error(ErrorCode.MULTICHARACTER_CONSTANT, token)
        result += "'"
        token = Token(TokenType.CHARACTER, result, self.line, self.column)
        self.advance()
        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == "/" and self.peek() == "/":
                return self.get_comment("//", "\n")
            if self.current_char == "/" and self.peek() == "*":
                return self.get_comment("/*", "*/")

            if self.current_char.isdigit():
                return self.get_number(
                    accept_hex=True,
                    accept_bit=True,
                    end_chars="fFlLUup",
                )

            if self.current_char.isalpha() or self.current_char == TokenType.UNDERLINE.value:
                return self.get_id()

            if self.current_char == '"':
                return self.get_string()

            if self.current_char == "'":
                return self.get_char()

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
        self.atomic_type_specifier = TokenSet(CTokenType._ATOMIC)
        self.struct_or_union_specifier = TokenSet(self.struct_or_union)
        self.enum_specifier = TokenSet(CTokenType.ENUM)
        self.typedef_name = TokenSet(CTokenType.TYPEDEF_ID)
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
            CTokenType._BOOL,
            CTokenType._COMPLEX,
            CTokenType.BOOL,
            self.atomic_type_specifier,
            self.struct_or_union_specifier,
            self.enum_specifier,
            self.typedef_name,
        )
        self.type_qualifier = TokenSet(CTokenType.CONST, CTokenType.VOLATILE, CTokenType.RESTRICT, CTokenType._ATOMIC)
        self.function_speficier = TokenSet(CTokenType.INLINE, CTokenType._NORETURN)
        self.alignment_specifier = TokenSet(CTokenType._ALIGNAS)
        self.declaration_specifier = TokenSet(
            self.storage_class_specifier,
            self.type_specifier,
            self.type_qualifier,
            self.function_speficier,
            self.alignment_specifier,
        )
        # declarator 这里添加 [ 是为了匹配无形参名类型的参数, 例如 int[]
        self.declarator = TokenSet(
            TokenType.MUL, TokenType.ID, TokenType.LPAREN, TokenType.LSQUAR_PAREN  # => CTokenType.POINTER
        )
        self.function_definition = TokenSet(self.declaration_specifier, self.declarator)
        self.declaration = TokenSet(self.declaration_specifier, CTokenType._ATTRIBUTE)
        self.group_part = TokenSet(TokenType.HASH)
        self.group = TokenSet(self.group_part)

        self.static_assert_declaration = TokenSet(CTokenType._STATIC_ASSERT)
        self.specifier_qualifier_list = TokenSet(self.type_qualifier, self.type_specifier)
        self.struct_declarator = TokenSet(self.declarator, TokenType.COLON)
        self.struct_declarator_list = TokenSet(self.struct_declarator)
        self.struct_declaration = TokenSet(self.specifier_qualifier_list, self.struct_declarator, TokenType.VARARGS)
        self.direct_declaractor = TokenSet(TokenType.ID, TokenType.LPAREN)

        self.generic_selection = TokenSet(CTokenType._GENERIC)
        self.assignment_operator = TokenSet(
            TokenType.ASSIGN,
            TokenType.MUL_ASSIGN,
            TokenType.DIV_ASSIGN,
            TokenType.MOD_ASSIGN,
            TokenType.ADD_ASSIGN,
            TokenType.SUB_ASSIGN,
            TokenType.SHL_ASSIGN,
            TokenType.SHR_ASSIGN,
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

        self.identifier = TokenSet(TokenType.ID)
        self.parameter_declaration = TokenSet(self.declaration_specifier)
        self.parameter_list = TokenSet(self.parameter_declaration)
        self.constant = TokenSet(TokenType.NUMBER, CTokenType.TRUE, CTokenType.FALSE)
        self.primary_expression = TokenSet(
            TokenType.ID, TokenType.STRING, TokenType.LPAREN, TokenType.CHARACTER, self.constant
        )
        self.postfix_expression = TokenSet(self.primary_expression, TokenType.LPAREN)
        # postfix_expression 内部的
        self.postfix_expression_inside = TokenSet(
            TokenType.LSQUAR_PAREN,
            TokenType.LPAREN,
            TokenType.DOT,
            TokenType.POINT,
            TokenType.INC,
            TokenType.DEC,
        )
        self.type_name = TokenSet(self.specifier_qualifier_list)

        self.unary_expression = TokenSet(
            self.unary_operator,
            TokenType.INC,
            TokenType.DEC,
            CTokenType.SIZEOF,
            self.postfix_expression,
            CTokenType._ALIGNOF,
            TokenType.LPAREN,
        )
        self.conditinal_expression = TokenSet(self.unary_expression, TokenType.LPAREN)

        self.constant_expression = TokenSet(self.conditinal_expression)
        self.assignment_expression = TokenSet(self.unary_expression, self.conditinal_expression)
        self.expression = TokenSet(self.assignment_expression)
        self.direct_abstract_declarator = TokenSet(TokenType.LPAREN, TokenType.LSQUAR_PAREN)
        self.abstract_declarator = TokenSet(TokenType.MUL, self.direct_abstract_declarator)
        self.initializer = TokenSet(self.assignment_expression, TokenType.LCURLY_BRACE)
        self.designator = TokenSet(TokenType.LSQUAR_PAREN, TokenType.DOT)
        self.designation = TokenSet(self.designator)
        self.initializer_list = TokenSet(self.designation, self.initializer)

        self.labeled_statement = TokenSet(self.identifier, CTokenType.CASE, CTokenType.DEFAULT)
        self.expression_statement = TokenSet(self.expression, TokenType.SEMI)
        self.compound_statement = TokenSet(TokenType.LCURLY_BRACE)
        self.selection_statement = TokenSet(CTokenType.IF, CTokenType.SWITCH)
        self.iteration_statement = TokenSet(CTokenType.WHILE, CTokenType.DO, CTokenType.FOR)
        self.jump_statement = TokenSet(CTokenType.GOTO, CTokenType.CONTINUE, CTokenType.BREAK, CTokenType.RETURN)
        self.gnu_c_statement_extension = TokenSet(CTokenType._ASM, CTokenType.ASM)
        self.statement = TokenSet(
            self.labeled_statement,
            self.expression_statement,
            self.compound_statement,
            self.selection_statement,
            self.iteration_statement,
            self.jump_statement,
            self.gnu_c_statement_extension,
        )
        self.external_declaration = TokenSet(
            self.function_definition, self.declaration, self.group_part, self.statement
        )
        self.block_item = TokenSet(self.declaration, self.statement, TokenType.VARARGS)
        self.init_declarator_list = TokenSet(self.declarator)
        self.identifier_list = TokenSet(TokenType.ID)
        self.if_group = TokenSet(CTokenType.IF_P, CTokenType.IFDEF, CTokenType.IFNDEF)
        self.elif_group = TokenSet(CTokenType.ELIF)
        self.else_group = TokenSet(CTokenType.ELSE_P)
        self.endif_group = TokenSet(CTokenType.ENDIF)
        self.if_section = TokenSet(self.if_group, self.elif_group, self.endif_group, self.else_group)
        self.control_line = TokenSet(
            CTokenType.INCLUDE,
            CTokenType.DEFINE,
            CTokenType.UNDEF,
            CTokenType.LINE,
            CTokenType.ERROR,
            CTokenType.PRAGMA,
            TokenType.LF,
            TokenType.EOF,
        )
        # eof 是考虑结尾
