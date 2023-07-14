from .lexer import Lexer, Token, TokenType, TokenSet
from enum import Enum


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
    VOLATITLE = "volatile"
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

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------

    POINTER = "*"
    STAR = '*'


class CLexer(Lexer):
    def __init__(self, text: str, TokenType: TokenType = CTokenType):
        super().__init__(text, TokenType)
        disable_long_op = ["===", "!==", "::"]
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
        self.atomic_type_specifier = TokenSet(CTokenType._ATOMIC)
        self.struct_or_union_specifier = TokenSet(self.struct_or_union)
        self.enum_specifier = TokenSet(CTokenType.ENUM)
        self.typedef_name = TokenSet(TokenType.ID)
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
            self.atomic_type_specifier,
            self.struct_or_union_specifier,
            self.enum_specifier,
            self.typedef_name,
        )
        self.type_qualifier = TokenSet(CTokenType.CONST, CTokenType.VOLATITLE)
        self.function_speficier = TokenSet(CTokenType.INLINE, CTokenType._NORETURN)
        self.alignment_specifier = TokenSet(CTokenType._ALIGNAS)
        self.declaration_specifier = TokenSet(
            self.storage_class_specifier, self.type_specifier, self.type_qualifier
        )
        self.declarator = TokenSet(
            TokenType.MUL, TokenType.ID, TokenType.LPAREN  # => CTokenType.POINTER
        )
        self.function_definition = TokenSet(self.declaration_specifier, self.declarator)
        self.declaration = TokenSet(self.declaration_specifier)
        self.external_declaration = TokenSet(self.function_definition, self.declaration)
        self.static_assert_declaration = TokenSet(CTokenType._STATIC_ASSERT)
        self.specifier_qualifier = TokenSet(self.type_qualifier, self.type_specifier)
        self.struct_declarator = TokenSet(self.declarator, TokenType.COLON)
        self.struct_declaration = TokenSet(self.specifier_qualifier, self.struct_declarator)
        self.direct_declaractor = TokenSet(TokenType.ID, TokenType.LPAREN)
        self.compound_statement = TokenSet(TokenType.LCURLY_BRACE)
        self.generic_selection = TokenSet(CTokenType._GENERIC)
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

        self.identifier = TokenSet(TokenType.ID, TokenType.NUMBER, TokenType.STRING, TokenType.CHAR)
        self.parameter_declaration = TokenSet(self.declaration_specifier)
        self.parameter_list = TokenSet(self.parameter_declaration)
        self.primary_expression = TokenSet(
            TokenType.ID, TokenType.NUMBER, TokenType.STRING, TokenType.LPAREN
        )
        self.postfix_expression = TokenSet(self.primary_expression)
        # postfix_expression 内部的
        self.postfix_expression_inside = TokenSet(
            TokenType.LSQUAR_PAREN,
            TokenType.LPAREN,
            TokenType.DOT,
            TokenType.POINT,
            TokenType.INC,
            TokenType.DEC,
        )
        self.type_name = TokenSet(self.specifier_qualifier)
        
        self.unary_expression = TokenSet(
            self.unary_operator,
            TokenType.INC,
            TokenType.DEC,
            CTokenType.SIZEOF,
            self.postfix_expression,
            CTokenType._ALIGNOF,
            TokenType.LPAREN
        )
        self.conditinal_expression = TokenSet(self.unary_expression, TokenType.LPAREN)
        self.constant_expression = TokenSet(self.conditinal_expression)
        self.assignment_expression = TokenSet(self.unary_expression, self.conditinal_expression)
        self.expression = TokenSet(self.assignment_expression)
        self.direct_abstract_declarator = TokenSet(TokenType.LPAREN, TokenType.LSQUAR_PAREN)
        self.abstract_declarator = TokenSet(TokenType.MUL, self.direct_abstract_declarator)
