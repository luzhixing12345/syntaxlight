from enum import Enum
from .lexer import Lexer, TokenType, Token
from ..token import TokenSet


class RustTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    ABSTRACT = "abstract"
    ALIGNOF = "alignof"
    AS = "as"
    BECOME = "become"
    BOX = "box"
    BREAK = "break"
    CONST = "const"
    CONTINUE = "continue"
    CRATE = "crate"
    DO = "do"
    ELSE = "else"
    ENUM = "enum"
    EXTERN = "extern"
    FALSE = "false"
    FINAL = "final"
    FN = "fn"
    FOR = "for"
    IF = "if"
    IMPL = "impl"
    IN = "in"
    LET = "let"
    LOOP = "loop"
    MACRO = "macro"
    MATCH = "match"
    MOD = "mod"
    MOVE = "move"
    MUT = "mut"
    OFFSETOF = "offsetof"
    OVERRIDE = "override"
    PRIV = "priv"
    PROC = "proc"
    PUB = "pub"
    PURE = "pure"
    REF = "ref"
    RETURN = "return"
    SSELF = "Self"
    SELF = "self"
    SIZEOF = "sizeof"
    STATIC = "static"
    STRUCT = "struct"
    SUPER = "super"
    TRAIT = "trait"
    TRUE = "true"
    TYPE = "type"
    TYPEOF = "typeof"
    UNSAFE = "unsafe"
    UNSIZED = "unsized"
    USE = "use"
    VIRTUAL = "virtual"
    WHERE = "where"
    WHILE = "while"
    YIELD = "yield"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    HASH_BANG = "#!"
    LIFETIME = "LIFETIME"
    STR = "STR"
    DEREF = "*"  # 解引用
    STAR = "*"
    LAMBDA = "LAMBDA"
    LABEL = 'LABEL'
    PATTERN_MATCH = '..='

class RustLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = RustTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(
            [
                "->",
                "<=",
                ">=",
                "#!",
                "::",
                "..",
                "...",
                "==",
                "=>",
                "||",
                "&&",
                "!=",
                "+=",
                "-=",
                "*=",
                "/=",
                "%=",
                "&=",
                "|=",
                "<<=",
                ">>=",
                "<<",
                ">>",
                "..="
            ]
        )

    def get_lifetime(self):
        value = self.current_char
        self.advance()
        while self.current_char is not None and self.current_char.isalnum():
            value += self.current_char
            self.advance()
        token = Token(RustTokenType.LIFETIME, value, self.line, self.column - 1)
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

            if self.current_char == "'" and self.peek().isalnum() and self.peek(2)[-1] != "'":
                return self.get_lifetime()

            if self.current_char == '"':
                return self.get_string()
            
            if self.current_char == "'":
                return self.get_char()
            
            if self.current_char.isdigit():
                token = self.get_number(accept_float=True, accept_hex=True, accept_bit=True)
                if self.current_char in ["i", "u", "f"]:
                    if self.peek() == "8" or self.peek(2) in ["16", "32", "64"] or self.peek(3) == "128":
                        value = token.value + self.current_char
                        self.advance()
                        while self.current_char != None and self.current_char.isalnum():
                            value += self.current_char
                            self.advance()
                        token = Token(TokenType.NUMBER, value, token.line, token.column - 1)
                    elif self.peek(4) == "size":
                        value = token.value + self.current_char
                        self.advance()
                        for _ in range(4):
                            value += self.current_char
                            self.advance()
                        token = Token(TokenType.NUMBER, value, token.line, token.column)
                return token

            if self.current_char.isalpha() or self.current_char == "_":
                return self.get_id()

            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
                token = Token(TokenType.TEXT, self.current_char, self.line, self.column)
                self.advance()
                return token
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # End of File
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)


class RustTokenSet:
    def __init__(self) -> None:
        self.inner_attr = TokenSet(RustTokenType.HASH_BANG)
        self.outer_attr = TokenSet(TokenType.HASH)

        self.visibility = TokenSet(RustTokenType.PUB)
        self.attrs_and_vis = TokenSet(self.outer_attr, self.visibility)

        self.path_glob = TokenSet(TokenType.ID, RustTokenType.SELF, TokenType.LCURLY_BRACE, TokenType.MUL)
        self.path_item = TokenSet(TokenType.ID, RustTokenType.SELF, RustTokenType.CRATE)
        self.block_item = TokenSet(
            RustTokenType.FN,
            RustTokenType.MOD,
            RustTokenType.STRUCT,
            RustTokenType.ENUM,
            RustTokenType.IMPL,
            RustTokenType.TRAIT,
            RustTokenType.EXTERN,
            self.outer_attr, self.inner_attr
        )
        self.stmt_item = TokenSet(RustTokenType.STATIC, RustTokenType.CONST, RustTokenType.TYPE, self.block_item, RustTokenType.USE, RustTokenType.LET)

        self.item = TokenSet(self.stmt_item, RustTokenType.USE, RustTokenType.EXTERN)
        self.generic_params = TokenSet(TokenType.LANGLE_BRACE)

        self.ret_ty = TokenSet(TokenType.POINT)
        self.where_clause = TokenSet(RustTokenType.WHERE)
        self.record_struct_body = TokenSet(TokenType.LCURLY_BRACE)
        self.tuple_struct_body = TokenSet(TokenType.LPAREN)

        self.block_expr = TokenSet(TokenType.LCURLY_BRACE)
        self.lit = TokenSet(
            TokenType.CHARACTER,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.LPAREN,
            RustTokenType.TRUE,
            RustTokenType.FALSE,
            RustTokenType.STR,
            TokenType.CONCAT
        )
        self.path = TokenSet(TokenType.ID, RustTokenType.SSELF)
        self.pat = TokenSet(
            TokenType.ID,
            TokenType.AMPERSAND,
            RustTokenType.MUT,
            RustTokenType.REF,
            self.lit,
            self.path,
            TokenType.LPAREN,
            TokenType.LSQUAR_PAREN
        )
        self.pat_field = TokenSet(TokenType.ID, RustTokenType.REF, RustTokenType.MUT)
        self.fn_param = TokenSet(self.pat)

        self.impl_member = TokenSet(RustTokenType.TYPE, RustTokenType.CONST, RustTokenType.FN)
        self.self_param = TokenSet(TokenType.AMPERSAND, RustTokenType.MUT, RustTokenType.SELF)

        self.type_path = TokenSet(TokenType.ID, RustTokenType.SSELF)
        self.ty = TokenSet(
            TokenType.LPAREN,
            TokenType.MUL,
            TokenType.LSQUAR_PAREN,
            TokenType.AMPERSAND,
            self.type_path,
        )
        self.ty_sum = TokenSet(self.ty)
        self.generic_values = TokenSet(TokenType.LANGLE_BRACE)

        self.unary_group = TokenSet(RustTokenType.BOX, TokenType.MINUS, TokenType.MUL, TokenType.AMPERSAND, TokenType.BANG)
        self.ref_group = TokenSet(TokenType.DOT, TokenType.LSQUAR_PAREN, TokenType.DOUBLE_COLON, TokenType.LPAREN)

        self.lambda_expr = TokenSet(TokenType.OR, TokenType.PIPE)
        self.statement_like_expr = TokenSet(
            self.block_expr,
            RustTokenType.UNSAFE,
            RustTokenType.IF,
            RustTokenType.WHILE,
            RustTokenType.LOOP,
            RustTokenType.MATCH,
            RustTokenType.FOR,
        )
        self.primary_group = TokenSet(
            TokenType.ID,
            TokenType.AMPERSAND,
            RustTokenType.SELF,
            TokenType.LPAREN,
            TokenType.LSQUAR_PAREN,
            self.lambda_expr,
            RustTokenType.RETURN,
            self.statement_like_expr,
            self.lit,
            RustTokenType.CONTINUE,
            RustTokenType.BREAK,
        )
        self.expr = TokenSet(TokenType.ID, self.unary_group, self.ref_group, self.primary_group)
        self.stmt = TokenSet(self.stmt_item, RustTokenType.LET, self.statement_like_expr, self.expr, TokenType.SEMI, RustTokenType.LIFETIME)
        self.item_with_attrs = TokenSet(self.attrs_and_vis, self.visibility, self.item)
