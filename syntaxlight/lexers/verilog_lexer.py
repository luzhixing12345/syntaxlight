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
    EDGE_SYMBOL = "EDGE_SYMBOL"  # r   R   f   F   p   P   n   N   *


class VerilogLexer(Lexer):
    def __init__(self, text: str, LanguageTokenType: Enum = VerilogTokenType):
        super().__init__(text, LanguageTokenType)

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

        self.parameter_declaration = TokenSet()
        self.input_declaration = TokenSet()
        self.output_declaration = TokenSet()
        self.inout_declaration = TokenSet()
        self.net_declaration = TokenSet()
        self.reg_declaration = TokenSet()
        self.time_declaration = TokenSet()
        self.integer_declaration = TokenSet()
        self.real_declaration = TokenSet()
        self.event_declaration = TokenSet()
        self.gate_declaration = TokenSet()
        self.UDP_instantiation = TokenSet()
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
        self.port_expression = TokenSet(TokenType.LCURLY_BRACE, TokenType.ID)

        self.UDP_declaration = TokenSet(self.output_declaration, self.reg_declaration, self.input_declaration)
        self.statement = TokenSet()