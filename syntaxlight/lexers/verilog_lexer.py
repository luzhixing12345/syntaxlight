from .lexer import Lexer, Token, TokenType, ErrorCode, TokenSet
from enum import Enum


class VerilogTokenType(Enum):
    RESERVED_KEYWORD_START = "RESERVED_KEYWORD_START"
    AND = "and"
    ALWAYS = "always"
    ASSIGN = "assign"
    BEGIN = "begin"
    BUF = "buf"
    BUFIF0 = "bufif0"
    BUFIF1 = "bufif1"
    CASE = "case"
    CASEX = "casex"
    CASEZ = "casez"
    CMOS = "cmos"
    DEASSIGN = "deassign"
    DEFAULT = "default"
    DEFPARAM = "defparam"
    DISABLE = "disable"
    EDGE = "edge"
    ELSE = "else"
    END = "end"
    ENDCASE = "endcase"
    ENDFUNCTION = "endfunction"
    ENDPRIMITIVE = "endprimitive"
    ENDMODULE = "endmodule"
    ENDSPECIFY = "endspecify"
    ENDTABLE = "endtable"
    ENDTASK = "endtask"
    EVENT = "event"
    FOR = "for"
    FORCE = "force"
    FOREVER = "forever"
    FORK = "fork"
    FUNCTION = "function"
    HIGHZ0 = "highz0"
    HIGHZ1 = "highz1"
    IF = "if"
    IFNONE = "ifnone"
    INITIAL = "initial"
    INOUT = "inout"
    INPUT = "input"
    INTEGER = "integer"
    JOIN = "join"
    LARGE = "large"
    MACROMODULE = "macromodule"
    MEDIUM = "medium"
    MODULE = "module"
    NAND = "nand"
    NEGEDGE = "negedeg"
    NOR = "nor"
    NOT = "not"
    NOTIF0 = "notif0"
    NOTIF1 = "notif1"
    NMOS = "nmos"
    OR = "or"
    OUTPUT = "output"
    PARAMETER = "parameter"
    PMOS = "pmos"
    POSEDGE = "posedge"
    PRIMITIVE = "primitive"
    PULLDOWN = "pulldown"
    PULLUP = "pullup"
    PULL0 = "pull0"
    PULL1 = "pull1"
    RCMOS = "rcmos"
    REAL = "real"
    REALTIME = "realtime"
    REG = "reg"
    RELEASE = "release"
    REPEAT = "repeat"
    RNMOS = "rnmos"
    RPMOS = "rpmos"
    RTRAN = "rtran"
    RTRANIF0 = "rtranif0"
    RTRANIF1 = "rtranif1"
    SCALARED = "scalared"
    SMALL = "small"
    SPECIFY = "specify"
    SPECPARAM = "specparam"
    STRENGTH = "strength"
    STRONG0 = "strong0"
    STRONG1 = "strong1"
    SUPPLY0 = "supply0"
    SUPPLY1 = "supply1"
    TABLE = "table"
    TASK = "task"
    TRAN = "tran"
    TRANIF0 = "tranif0"
    TRANIF1 = "tranif1"
    TIME = "time"
    TRI = "tri"
    TRIAND = "triand"
    TRIOR = "trior"
    TRIREG = "trireg"
    TRI0 = "tri0"
    TRI1 = "tri1"
    VECTORED = "vectored"
    WAIT = "wait"
    WAND = "wand"
    WEAK0 = "weak0"
    WEAK1 = "weak1"
    WHILE = "while"
    WIRE = "wire"
    WOR = "wor"
    XNOR = "xnor"
    XOR = "xor"
    RESERVED_KEYWORD_END = "RESERVED_KEYWORD_END"

    OUTPUT_SYMBOL = "01xX"  # 0   1   x   X
    LEVEL_SYMBOL = "01xX?bB"  # 0   1   x   X   ?   b   B
    EDGE_SYMBOL = "rRfFpPnN"  # r   R   f   F   p   P   n   N   *
    NON_BLOCK_ASSIGN = "<="
    SYSTEM_ID = "SYSTEM_ID"


class VerilogLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = VerilogTokenType):
        super().__init__(text, LanguageTokenType)
        self.build_long_op_dict(["<=", "->"])

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            if self.current_char == "/":
                if self.peek() == "/":
                    return self.get_comment("//", "\n")
                elif self.peek() == "*":
                    return self.get_comment("/*", "*/")

            if self.current_char.isalpha() or self.current_char == "_":
                token = self.get_id(extend_chars=["_", "$"])
                if len(token.value) == 1:
                    if token.value in VerilogTokenType.EDGE_SYMBOL.value:
                        token.type = VerilogTokenType.EDGE_SYMBOL
                    elif token.value in VerilogTokenType.LEVEL_SYMBOL.value:
                        token.type = VerilogTokenType.LEVEL_SYMBOL

                return token

            if self.current_char.isdigit():
                token = self.get_number()
                if len(token.value) == 1 and token.value in ("0", "1"):
                    token.type = VerilogTokenType.LEVEL_SYMBOL
                return token

            if self.current_char == "$" and self.peek() != " ":
                token_value = "$"
                self.advance()
                while self.current_char is not None and (
                    self.current_char.isalnum() or self.current_char in ("$", "_")
                ):
                    token_value += self.current_char
                    self.advance()
                token = Token(VerilogTokenType.SYSTEM_ID, token_value, self.line, self.column - 1)
                return token

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


class VerilogTokenSet:
    def __init__(self) -> None:
        self.module = TokenSet(VerilogTokenType.MODULE, VerilogTokenType.MACROMODULE)
        self.udp = TokenSet(VerilogTokenType.PRIMITIVE)
        self.description = TokenSet(self.module, self.udp)

        self.parameter_declaration = TokenSet(VerilogTokenType.PARAMETER)
        self.input_declaration = TokenSet(VerilogTokenType.INPUT)
        self.output_declaration = TokenSet(VerilogTokenType.OUTPUT)
        self.inout_declaration = TokenSet(VerilogTokenType.INOUT)
        self.net_type = TokenSet(
            VerilogTokenType.WIRE,
            VerilogTokenType.TRI,
            VerilogTokenType.TRI1,
            VerilogTokenType.SUPPLY0,
            VerilogTokenType.WAND,
            VerilogTokenType.TRIAND,
            VerilogTokenType.WOR,
            VerilogTokenType.TRIOR,
            VerilogTokenType.TRIREG,
        )
        self.net_declaration = TokenSet(self.net_type)
        self.reg_declaration = TokenSet(VerilogTokenType.REG)
        self.time_declaration = TokenSet(VerilogTokenType.TIME)
        self.integer_declaration = TokenSet(VerilogTokenType.INTEGER)
        self.real_declaration = TokenSet(VerilogTokenType.REAL)
        self.event_declaration = TokenSet(VerilogTokenType.EVENT)
        self.block_declaration = TokenSet(
            self.parameter_declaration,
            self.reg_declaration,
            self.integer_declaration,
            self.real_declaration,
            self.time_declaration,
            self.event_declaration,
        )
        self.gate_type = TokenSet(
            VerilogTokenType.AND,
            VerilogTokenType.NAND,
            VerilogTokenType.OR,
            VerilogTokenType.NOR,
            VerilogTokenType.XOR,
            VerilogTokenType.XNOR,
            VerilogTokenType.BUF,
            VerilogTokenType.BUFIF0,
            VerilogTokenType.BUFIF1,
            VerilogTokenType.NOT,
            VerilogTokenType.NOTIF0,
            VerilogTokenType.NOTIF1,
            VerilogTokenType.PULLDOWN,
            VerilogTokenType.PULLUP,
            VerilogTokenType.NMOS,
            VerilogTokenType.RNMOS,
            VerilogTokenType.PMOS,
            VerilogTokenType.CMOS,
            VerilogTokenType.RCMOS,
            VerilogTokenType.TRAN,
            VerilogTokenType.RTRAN,
            VerilogTokenType.TRANIF0,
            VerilogTokenType.RTRANIF1,
        )
        self.gate_declaration = TokenSet(self.gate_type)
        self.UDP_instantiation = TokenSet(TokenType.ID)
        self.module_instantiation = TokenSet()
        self.parameter_override = TokenSet()
        self.continuous_assign = TokenSet()
        self.specify_block = TokenSet()
        self.initial_statement = TokenSet()
        self.always_statement = TokenSet()
        self.task = TokenSet(VerilogTokenType.TASK)
        self.function = TokenSet(VerilogTokenType.FUNCTION)

        self.module_item = TokenSet(
            self.parameter_declaration,
            self.input_declaration,
            self.output_declaration,
            self.inout_declaration,
            self.net_declaration,
            self.reg_declaration,
            self.time_declaration,
            self.integer_declaration,
            self.real_declaration,
            self.event_declaration,
            self.gate_declaration,
            self.UDP_instantiation,
            self.module_instantiation,
            self.parameter_override,
            self.continuous_assign,
            self.specify_block,
            self.initial_statement,
            self.always_statement,
            self.task,
            self.function,
        )
        self.tf_declaration = TokenSet(
            self.parameter_declaration,
            self.input_declaration,
            self.output_declaration,
            self.inout_declaration,
            self.reg_declaration,
            self.time_declaration,
            self.integer_declaration,
            self.real_declaration,
        )
        self.range = TokenSet(TokenType.LSQUAR_PAREN)
        self.port_expression = TokenSet(TokenType.LCURLY_BRACE, TokenType.ID)

        self.UDP_declaration = TokenSet(self.output_declaration, self.reg_declaration, self.input_declaration)

        self.strength0 = TokenSet(
            VerilogTokenType.SUPPLY0,
            VerilogTokenType.STRONG0,
            VerilogTokenType.PULL0,
            VerilogTokenType.WEAK0,
            VerilogTokenType.HIGHZ0,
        )
        self.strength1 = TokenSet(
            VerilogTokenType.SUPPLY1,
            VerilogTokenType.STRONG1,
            VerilogTokenType.PULL1,
            VerilogTokenType.WEAK1,
            VerilogTokenType.HIGHZ1,
        )
        self.expandrange = TokenSet(self.range, VerilogTokenType.SCALARED, VerilogTokenType.VECTORED)
        self.delay = TokenSet(TokenType.HASH)
        self.mintypmax_expression = TokenSet()
        self.drive_strength = TokenSet(TokenType.LPAREN)

        self.expression = TokenSet()
        self.lvalue = TokenSet(TokenType.LCURLY_BRACE, TokenType.ID)
        self.delay_or_event_control = TokenSet(VerilogTokenType.REPEAT, TokenType.HASH, TokenType.AT_SIGN)
        self.case_item = TokenSet(self.expression, VerilogTokenType.DEFAULT)

        self.statement = TokenSet(
            self.lvalue,
            VerilogTokenType.IF,
            VerilogTokenType.CASE,
            VerilogTokenType.CASEX,
            VerilogTokenType.CASEZ,
            VerilogTokenType.FOREVER,
            VerilogTokenType.REPEAT,
            VerilogTokenType.WHILE,
            VerilogTokenType.FOR,
            self.delay_or_event_control,
            VerilogTokenType.WAIT,
            TokenType.POINT,
            VerilogTokenType.BEGIN,
            VerilogTokenType.FORK,
            VerilogTokenType.DISABLE,
            VerilogTokenType.ASSIGN,
            VerilogTokenType.DEASSIGN,
            VerilogTokenType.FORCE,
            VerilogTokenType.RELEASE,
        )
