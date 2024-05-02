from .lexer import Lexer, Token, TokenType, ErrorCode
from enum import Enum
from ..token import TokenSet

class LuaTokenType(Enum):
    # -----------------------------------------------
    # start - end 之间为对应语言的保留关键字
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"

    # https://www.lua.org/manual/5.4/manual.html#8

    AND = "and"
    BREAK = "break"
    DO = "do"
    ELSE = "else"
    ELSEIF = "elseif"
    END = "end"
    FALSE = "false"
    FOR = "for"
    FUNCTION = "function"
    GOTO = "goto"
    IF = "if"
    IN = "in"
    LOCAL = "local"
    NIL = "nil"
    NOT = "not"
    OR = "or"
    REPEAT = "repeat"
    RETURN = "return"
    THEN = "then"
    TRUE = "true"
    UNTIL = "until"
    WHILE = "while"

    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"
    # start - end 之间为对应语言的保留关键字
    # -----------------------------------------------


class LuaLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = LuaTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(["//", ">>", "<<", "..", "...", "<=", ">=", "==", "~=", "::"])

    def get_literal_str(self):
        """
        [[ ... ]]
        [====[ ]====]
        数量相等的匹配长换行字符串

        保留内部所有字符串的原始值, 包括转义字符 \\
        """
        assert self.current_char == "["
        result = "["
        self.advance()
        assign_op_number = 0
        while self.current_char == "=":
            assign_op_number += 1
            result += self.current_char
            self.advance()
        
        assert self.current_char == "["
        result += self.current_char
        self.advance()

        end_symbol = f']{"="*assign_op_number}]'
        is_match = False
        while self.current_char is not None:
            if self.current_char == "]" and self.peek(len(end_symbol) - 1) == end_symbol[1:]:
                result += end_symbol
                for _ in range(len(end_symbol)):
                    self.advance()
                is_match = True
                break
            else:
                # 保留内部所有字符串的原始值, 包括转义字符 \\
                result += self.current_char
                self.advance()

        if is_match is False: # pragma: no cover
            token = Token(TokenType.STR, result, self.line, self.column-1)
            self.error(ErrorCode.UNTERMINATED_STRING, token, f"miss end symbol {end_symbol}")
        else:
            token = Token(TokenType.STR, result, self.line, self.column - 1)
        return token

    def get_long_comment(self):
        '''
        --[[...]]
        --[===[ ... ]===]
        '''
        result = '--'
        self.advance()
        self.advance()
        token = self.get_literal_str()
        token.type = TokenType.COMMENT
        token.value = result + token.value
        return token


    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char.isdigit():
                return self.get_number(accept_hex=True)

            if self.current_char.isalpha() or self.current_char == "_":
                return self.get_id()

            if self.current_char in self.long_op_dict:
                return self.get_long_op()

            if self.current_char == "-":
                # --[ xxx 短注释
                # --[[ ... ]] 长注释
                # --[==[ ... ]==] 长注释
                # -- [[ 第一行是短注释
                # ... ]]  
                next_three_chars = self.peek(3)
                if next_three_chars[0] == '-':
                    if next_three_chars[1] == '[' and next_three_chars[2] in ('[','='):
                        return self.get_long_comment()
                    else:
                        return self.get_comment("--", "\n")

            if self.current_char in ("'", '"'):
                return self.get_str()

            if self.current_char == "[" and self.peek() in ("[", "="):
                return self.get_literal_str()

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError: # pragma: no cover
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

        return Token(type=TokenType.EOF, value=None)


class LuaTokenSet:
    def __init__(self) -> None:
        self.unop = TokenSet(TokenType.MINUS, TokenType.HASH, TokenType.TILDE, LuaTokenType.NOT)
        self.binop = TokenSet(
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.DIV,
            TokenType.DOUBLE_DIV,
            TokenType.CARET,
            TokenType.MOD,
            TokenType.AMPERSAND,
            TokenType.TILDE,
            TokenType.PIPE,
            TokenType.SHL,
            TokenType.SHR,
            TokenType.CONCAT,
            TokenType.LANGLE_BRACE,
            TokenType.LE,
            TokenType.RANGLE_BRACE,
            TokenType.GE,
            TokenType.EQ,
            TokenType.NORE,
            LuaTokenType.AND,
            LuaTokenType.OR,
        )
        self.fieldsep = TokenSet(TokenType.COMMA, TokenType.SEMI)
        self.funcname = TokenSet(TokenType.ID)
        self.label = TokenSet(TokenType.DOUBLE_COLON)
        self.retstat = TokenSet(LuaTokenType.RETURN)
        self.attnamelist = TokenSet(TokenType.ID)
        self.tableconstructor = TokenSet(TokenType.LCURLY_BRACE)
        self.namelist = TokenSet(TokenType.ID)
        self.parlist = TokenSet(self.namelist, TokenType.VARARGS)
        self.args = TokenSet(TokenType.LPAREN, self.tableconstructor, TokenType.STR)
        self.prefix_exp_suffix = TokenSet(self.args, TokenType.COLON)
        self.funcbody = TokenSet(TokenType.LPAREN)
        self.functiondef = TokenSet(LuaTokenType.FUNCTION)
        self.var = TokenSet(TokenType.ID, TokenType.LPAREN)
        self.prefixexp = TokenSet(TokenType.ID, TokenType.LPAREN)
        self.functioncall = TokenSet(self.prefixexp)
        self.exp = TokenSet(
            LuaTokenType.NIL,
            LuaTokenType.FALSE,
            LuaTokenType.TRUE,
            TokenType.NUMBER,
            TokenType.STR,
            TokenType.VARARGS,
            self.functiondef,
            self.prefixexp,
            self.tableconstructor,
            self.unop,
        )
        self.explist = TokenSet(self.exp)
        self.varlist = TokenSet(self.var)
        self.field = TokenSet(TokenType.LSQUAR_PAREN, TokenType.ID, self.exp)
        self.fieldlist = TokenSet(self.field)
        self.attrib = TokenSet(TokenType.LANGLE_BRACE)
        self.stat = TokenSet(
            TokenType.SEMI,
            self.varlist,
            self.functioncall,
            self.label,
            LuaTokenType.BREAK,
            LuaTokenType.GOTO,
            LuaTokenType.DO,
            LuaTokenType.WHILE,
            LuaTokenType.WHILE,
            LuaTokenType.REPEAT,
            LuaTokenType.IF,
            LuaTokenType.FOR,
            LuaTokenType.FUNCTION,
            LuaTokenType.LOCAL,
        )
        self.block = TokenSet(self.stat, self.retstat)
