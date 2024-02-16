from .parser import Parser
from ..lexers import TokenType, VerilogTokenType, Token, VerilogTokenSet
from ..error import ErrorCode
from ..gdt import CSS
from ..asts.ast import add_ast_type, Number
from ..asts.verilog_ast import *
from enum import Enum
import re


class VerilogCSS(Enum):
    NET_TYPE = "NetType"
    STRENGTH0 = "Strength0"
    STRENGTH1 = "Strength1"
    GATE_WAY = "GateWay"
    MODULE_NAME = "ModuleName"
    DEFINED_MODULE = "DefinedModule"
    PORT_NAME = "PortName"
    BIT_WIDTH = "BitWidth"


class VerilogParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.verilog_first_set = VerilogTokenSet()

        self.module_map = {
            VerilogTokenType.PARAMETER: self.parameter_declaration,
            VerilogTokenType.INPUT: self.input_declaration,
            VerilogTokenType.OUTPUT: self.output_declaration,
            VerilogTokenType.INOUT: self.inout_declaration,
            VerilogTokenType.REG: self.reg_declaration,
            VerilogTokenType.TIME: self.time_declaration,
            VerilogTokenType.INTEGER: self.integer_declaration,
            VerilogTokenType.REAL: self.real_declaration,
            VerilogTokenType.EVENT: self.event_declaration,
            VerilogTokenType.DEFPARAM: self.parameter_override,
            VerilogTokenType.ASSIGN: self.continuous_assign,
            VerilogTokenType.SPECIFY: self.specify_block,
            VerilogTokenType.INITIAL: self.initial_statement,
            VerilogTokenType.ALWAYS: self.always_statement,
            VerilogTokenType.TASK: self.task,
            VerilogTokenType.FUNCTION: self.function,
            VerilogTokenType.GENERATE: self.generate_statement,
            VerilogTokenType.GENVAR: self.genvar_declaration,
        }

    def parse(self):
        self.root = self.source_text()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.root

    def source_text(self):
        """
        <source_text> ::= <description>*
        """
        node = Verilog()
        descriptions = []
        while self.current_token.type in self.verilog_first_set.description:
            descriptions.append(self.description())
        node.update(descriptions=descriptions)
        return node

    def description(self):
        """
        <description> ::= <module>
                        | <UDP>
        """
        node = Description()
        if self.current_token.type in self.verilog_first_set.module:
            node.update(module=self.module())
        elif self.current_token.type in self.verilog_first_set.udp:
            node.update(udp=self.udp())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should match a module or udp")

        return node

    def module(self):
        """
        <module> ::= module <name_of_module> <module_parameters>? <list_of_ports>? ; <module_item>* endmodule
                   | macromodule <name_of_module> <list_of_ports>? ; <module_item>* endmodule
        """
        node = Module()
        if self.current_token.type in self.verilog_first_set.module:
            node.update(module=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be module or macromodule")

        node.update(name=self.get_identifier())
        add_ast_type(node.name, VerilogCSS.MODULE_NAME)

        if self.current_token.type == TokenType.HASH:
            node.update(parameter=self.module_parameters())

        node.update(list_of_ports=self.list_of_ports())
        node.register_token(self.eat(TokenType.SEMI))
        module_items = []
        while self.current_token.type in self.verilog_first_set.module_item:
            module_items.append(self.module_item())
        node.update(module_items=module_items)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDMODULE))
        return node

    def module_parameters(self):
        """
        <module_parameters> ::= # ( <parameter_declaration>* )
        """
        node = ModuleParameters()
        node.register_token(self.eat(TokenType.HASH))
        node.register_token(self.eat(TokenType.LPAREN))
        paramters = []
        while self.current_token.type in self.verilog_first_set.parameter_declaration:
            paramters.append(self.parameter_declaration())
        node.update(paramters=paramters)
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def list_of_ports(self):
        """
        <list_of_ports> ::= ( <port> <,<port>>* )
        """
        self.eat(TokenType.LPAREN)
        ports = self.list_items(self.port)
        self.eat(TokenType.RPAREN)
        return ports

    def port(self):
        """
        <port> ::= (input | output)? (wire|reg|logic)? <range>? <port_expression>?
                 | . <name_of_port> ( <port_expression>? )

        @EXTEND-GRAMMAR: 添加 input/output wire/reg/logic
        """
        node = Port()
        if self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            node.update(name=self.get_identifier())
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.verilog_first_set.port_expression:
                node.update(port_expression=self.port_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in (VerilogTokenType.INPUT, VerilogTokenType.OUTPUT):
            node.update(port_type=self.get_keyword())
            if self.current_token.type in (VerilogTokenType.WIRE, VerilogTokenType.REG, VerilogTokenType.LOGIC):
                node.update(data_type=self.get_keyword())
            if self.current_token.type in self.verilog_first_set.range:
                node.update(range=self.range())
            node.update(port_expression=self.port_expression())
        elif self.current_token.type in self.verilog_first_set.port_expression:
            node.update(port_expression=self.port_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be port or port_expression")
        return node

    def port_expression(self):
        """
        <port_expression> ::= <port_reference>
                            | { <port_reference> <,<port_reference>>* }
        """
        port_references = []
        if self.current_token.type == TokenType.ID:
            port_references.append(self.port_reference())
        elif self.current_token.type == TokenType.LCURLY_BRACE:
            self.eat(TokenType.LCURLY_BRACE)
            port_references.append(self.port_reference())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                port_references.append(self.port_reference())
            self.eat(TokenType.RCURLY_BRACE)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be port_reference or LCURLY_BRACE")
        return port_references

    def port_reference(self):
        """
        <port_reference> ::= <name_of_variable>
                           | <name_of_variable> [ <constant_expression> ]
                           | <name_of_variable> [ <constant_expression> :<constant_expression> ]
        """
        node = PortReference()
        node.update(name=self.get_identifier())
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(index_begin=self.expression())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
            node.update(index_end=self.expression())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def module_item(self):
        """
        <module_item> ::= <parameter_declaration>
                        | <input_declaration>
                        | <output_declaration>
                        | <inout_declaration>
                        | <net_declaration>
                        | <reg_declaration>
                        | <time_declaration>
                        | <integer_declaration>
                        | <real_declaration>
                        | <event_declaration>
                        | <gate_declaration>
                        | <UDP_instantiation>
                        | <module_instantiation>
                        | <parameter_override>
                        | <continuous_assign>
                        | <specify_block>
                        | <initial_statement>
                        | <always_statement>
                        | <task>
                        | <function>
                        | <generate_statement>
                        | <genvar_declaration>

        @EXTEND-GRAMMAR: 添加 generate statement, genvar_declaration
        """
        # TODO

        if self.current_token.type in self.module_map:
            return self.module_map[self.current_token.type]()
        elif self.current_token.type in self.verilog_first_set.net_declaration:
            return self.net_declaration()
        elif self.current_token.type in self.verilog_first_set.gate_declaration:
            return self.gate_declaration()
        elif self.current_token.type in self.verilog_first_set.UDP_instantiation:
            return self.module_instantiation()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should match a module item")

    def udp(self):
        """
        <UDP> ::= primitive <name_of_UDP> ( <name_of_variable> <,<name_of_variable>>* ) ; <UDP_declaration>+ <UDP_initial_statement>?   <table_definition> endprimitive
        """
        node = UDP()
        node.update(keyword=self.get_keyword(VerilogTokenType.PRIMITIVE))
        node.update(name=self.get_identifier())
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(variable_names=self.list_of_variables())
        node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.SEMI))
        udp_declarations = [self.UDP_declaration()]
        while self.current_token.type in self.verilog_first_set.UDP_declaration:
            udp_declarations.append(self.UDP_declaration())
        node.update(udp_declarations=udp_declarations)
        if self.current_token.type == VerilogTokenType.INITIAL:
            node.update(udp_initial_statement=self.UDP_initial_statement())
        node.update(table_definition=self.table_definition())
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDPRIMITIVE))
        return node

    def UDP_declaration(self):
        """
        <UDP_declaration> ::= <output_declaration>
                            | <reg_declaration>
                            | <input_declaration>
        """
        if self.current_token.type in self.verilog_first_set.output_declaration:
            return self.output_declaration()
        elif self.current_token.type in self.verilog_first_set.reg_declaration:
            return self.reg_declaration()
        elif self.current_token.type in self.verilog_first_set.input_declaration:
            return self.input_declaration()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "shoud be output/reg/input")

    def UDP_initial_statement(self):
        """
        <UDP_initial_statement> ::= initial <output_terminal_name> = <init_val> ;
        """
        node = UdpInitialStatement()
        node.update(keyword=self.get_keyword(VerilogTokenType.INITIAL))
        node.update(name=self.get_identifier())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(init_val=self.init_val())
        return node

    def init_val(self):
        """
        <init_val> ::= 1'b0
                     | 1'b1
                     | 1'bx
                     | 1'bX
                     | 1'B0
                     | 1'B1
                     | 1'Bx
                     | 1'BX
                     | 1
                     | 0
        """
        # TODO

    def table_definition(self):
        """
        <table_definition> ::= table <table_entries> endtable
        """
        node = TableDefinition()
        node.update(keyword=self.get_keyword(VerilogTokenType.TABLE))
        node.update(entries=self.table_entries())
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDTABLE))
        return node

    def table_entries(self):
        """
        <table_entries> ::= <combinational_entry>+
                          | <sequential_entry>+

        <combinational_entry> ::= <level_input_list> : <OUTPUT_SYMBOL> ;
        <sequential_entry> ::= <input_list> : <state> : <next_state> ;

        <input_list> ::= <level_input_list>
                       | <edge_input_list>

        <level_input_list> ::= <LEVEL_SYMBOL>+

        <edge_input_list> ::= <LEVEL_SYMBOL>* <edge> <LEVEL_SYMBOL>*

        <edge> ::= ( <LEVEL_SYMBOL> <LEVEL_SYMBOL> )
                 | <EDGE_SYMBOL>

        <state> ::= <LEVEL_SYMBOL>

        <next_state> ::= <OUTPUT_SYMBOL>
                       | - (This is a literal hyphen, see Chapter 5 for details).
        """
        entries = []

        while self.current_token.type in (VerilogTokenType.LEVEL_SYMBOL, VerilogTokenType.EDGE_SYMBOL):
            entry = TableEntry()
            while self.current_token.type == VerilogTokenType.LEVEL_SYMBOL:
                entry.register_token(self.eat(VerilogTokenType.LEVEL_SYMBOL))
            if self.current_token.type == TokenType.LPAREN:
                entry.register_token(self.eat(TokenType.LPAREN))
                entry.register_token(self.eat(VerilogTokenType.LEVEL_SYMBOL))
                entry.register_token(self.eat(VerilogTokenType.LEVEL_SYMBOL))
                entry.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type in (VerilogTokenType.EDGE_SYMBOL, TokenType.MUL):
                if self.current_token.type == TokenType.MUL:
                    self.current_token.type = VerilogTokenType.EDGE_SYMBOL
                entry.register_token(self.eat())

            while self.current_token.type == VerilogTokenType.LEVEL_SYMBOL:
                entry.register_token(self.eat(VerilogTokenType.LEVEL_SYMBOL))

            entry.register_token(self.eat(TokenType.COLON))
            if self.current_token.type == VerilogTokenType.LEVEL_SYMBOL:
                if self.peek_next_token().type == TokenType.SEMI:
                    if self.current_token.value in VerilogTokenType.OUTPUT_SYMBOL.value:
                        # 修改为 OUTPUT_SYMBOL
                        self.current_token.type = VerilogTokenType.OUTPUT_SYMBOL
                    else:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, f"should be {VerilogTokenType.OUTPUT_SYMBOL.value}")

                    entry.register_token(self.eat(VerilogTokenType.OUTPUT_SYMBOL))
                    entry.register_token(self.eat(TokenType.SEMI))
                else:
                    entry.register_token(self.eat(VerilogTokenType.LEVEL_SYMBOL))
                    entry.register_token(self.eat(TokenType.COLON))
                    if self.current_token.value in VerilogTokenType.OUTPUT_SYMBOL.value:
                        # 修改为 OUTPUT_SYMBOL
                        self.current_token.type = VerilogTokenType.OUTPUT_SYMBOL
                        entry.register_token(self.eat(VerilogTokenType.OUTPUT_SYMBOL))
                    else:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, f"should be {VerilogTokenType.OUTPUT_SYMBOL.value}")
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "should be level symbol")
            entries.append(entry)

        return entries

    def task(self):
        """
        <task> ::= task <name_of_task> ; <tf_declaration>* <statement_or_null> endtask
        """
        node = Task()
        node.update(keyword=self.get_keyword(VerilogTokenType.TASK))
        node.update(name=self.get_identifier())
        node.register_token(self.eat(TokenType.SEMI))
        tf_declarations = []
        while self.current_token.type in self.verilog_first_set.tf_declaration:
            tf_declarations.append(self.tf_declaration())
        node.update(tf_declarations=tf_declarations)
        node.update(stmt=self.statement_or_null())
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDTASK))
        return node

    def statement_or_null(self):
        """
        <statement_or_null>
                            ::= <statement>
                            ||= ;
        """
        if self.current_token.type in self.verilog_first_set.statement:
            return self.statement()
        elif self.current_token.type == TokenType.SEMI:
            self.eat()
            return None
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be statement or ;")

    def tf_declaration(self):
        """
        <tf_declaration> ::= <parameter_declaration>
                           | <input_declaration>
                           | <output_declaration>
                           | <inout_declaration>
                           | <reg_declaration>
                           | <time_declaration>
                           | <integer_declaration>
                           | <real_declaration>
        """
        kv_map = {
            VerilogTokenType.PARAMETER: self.parameter_declaration,
            VerilogTokenType.INPUT: self.input_declaration,
            VerilogTokenType.OUTPUT: self.output_declaration,
            VerilogTokenType.INOUT: self.inout_declaration,
            VerilogTokenType.REG: self.reg_declaration,
            VerilogTokenType.INTEGER: self.integer_declaration,
            VerilogTokenType.REAL: self.real_declaration,
            VerilogTokenType.TIME: self.time_declaration,
        }
        if self.current_token.type in kv_map:
            return kv_map[self.current_token.type]()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "output tf declaration kv map")

    def function(self):
        """
        <function> ::= function <range_or_type>? <name_of_function> ; <tf_declaration>+ <statement> endfunction

        <range_or_type> ::= <range>
                          | integer
                          | real
        """
        node = Function()
        node.update(keyword=self.get_keyword(VerilogTokenType.FUNCTION))
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())
        elif self.current_token.type in (VerilogTokenType.INTEGER, VerilogTokenType.REAL):
            node.update(type=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be range or type")

        node.update(name=self.get_identifier())
        tf_declarations = [self.tf_declaration()]
        while self.current_token.type in self.verilog_first_set.tf_declaration:
            tf_declarations.append(self.tf_declaration())
        node.update(stmt=self.statement())
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDFUNCTION))
        return node

    def generate_statement(self):
        """
        <generate_statement> ::= generate <statement>* endgenerate
        """
        node = GenerateStmt()
        node.update(keyword=self.get_keyword(VerilogTokenType.GENERATE))
        stmts = []
        while self.current_token.type in self.verilog_first_set.statement:
            stmts.append(self.statement())
        node.update(stmts=stmts)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDGENERATE))
        return node

    def genvar_declaration(self):
        """
        genvar <list_of_register_variables> ;
        """
        node = GenvarDeclaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.GENVAR))
        node.update(vars=self.list_of_register_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def parameter_declaration(self):
        """
        <parameter_declaration> ::= parameter <list_of_param_assignments> ;

        <list_of_param_assignments> ::=<param_assignment><,<param_assignment>*

        """
        node = Parameter()
        node.update(keyword=self.get_keyword(VerilogTokenType.PARAMETER))
        node.update(param_assignments=self.list_items(self.param_assignment))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def param_assignment(self):
        """
        <param_assignment> ::=<identifier> = <constant_expression>
        """
        node = ParameterAssign()
        node.update(key=self.get_identifier())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(value=self.expression())
        return node

    def list_of_variables(self):
        """
        <list_of_variables> ::= ;
                              | <NETTYPE> <drive_strength>? <expandrange>? <delay>? <list_of_assignments> ;
        """
        # if self.current_token.type == TokenType.SEMI:
        #     return None

        # node = ListofVariables()
        # if self.current_token.type not in self.verilog_first_set.net_type:
        #     self.error(ErrorCode.UNEXPECTED_TOKEN, "should be a net type")

        # node.update(net_type=self.get_keyword(css_type=VerilogCSS.NET_TYPE))
        # if self.current_token.type == TokenType.LPAREN:
        #     node.update(drive_strength=self.drive_strength())
        # if self.current_token.type in self.verilog_first_set.expandrange:
        #     node.update(expandrange=self.expandrange())
        # if self.current_token.type in self.verilog_first_set.delay:
        #     node.update(delay=self.delay())
        # node.update(list_of_assignments=self.list_of_assignments())
        # node.register_token(self.eat(TokenType.SEMI))
        # return node
        return self.list_items(self.get_identifier)

    def drive_strength(self):
        """
        <drive_strength> ::= ( <STRENGTH0> , <STRENGTH1> )
                           | ( <STRENGTH1> , <STRENGTH0> )
        """
        node = DriveStrength()
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.verilog_first_set.strength0:
            node.update(pos1=self.get_keyword(css_type=VerilogCSS.STRENGTH0))
            node.register_token(self.eat(TokenType.COMMA))
            if self.current_token.type in self.verilog_first_set.strength1:
                node.update(pos2=self.get_keyword(css_type=VerilogCSS.STRENGTH1))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "should be strength1")
        elif self.current_token.type in self.verilog_first_set.strength1:
            node.update(pos1=self.get_keyword(css_type=VerilogCSS.STRENGTH1))
            node.register_token(self.eat(TokenType.COMMA))
            if self.current_token.type in self.verilog_first_set.strength0:
                node.update(pos2=self.get_keyword(css_type=VerilogCSS.STRENGTH0))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "should be strength0")
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be strength0 or strength1")

        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def expandrange(self):
        """
        <expandrange> ::= <range>
                        | scalared <range>
                        | vectored <range>
        """
        if self.current_token.type in self.verilog_first_set.range:
            return self.range()
        elif self.current_token.type in (VerilogTokenType.SCALARED, VerilogTokenType.VECTORED):
            node = ExpandRange()
            node.update(keyword=self.get_keyword())
            node.update(range=self.range())
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "expandrange error")

    def list_of_assignments(self):
        """
        <list_of_assignments> ::= <assignment> <,<assignment>>*
        """
        return self.list_items(self.assignment)

    def assignment(self):
        """
        <assignment> ::= <lvalue> = <expression>
        """
        node = Assignment()
        # @EXTEND-GRAMMAR for system verilog
        # for (int i=0;i<100;i++)
        if self.current_token.type in (VerilogTokenType.INTEGER, VerilogTokenType.INT):
            node.update(keyword=self.get_keyword())
        node.update(lvalue=self.lvalue())

        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(exp=self.expression())
        elif self.current_token.type in (TokenType.INC, TokenType.DEC):
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be = or ++ or --")
        return node

    def lvalue(self):
        """
        <lvalue> ::= <identifier>
                 ||= <identifier> [ <expression> ]
                 ||= <identifier> [ <constant_expression> : <constant_expression> ]
                 ||= <concatenation>
        """

        if self.current_token.type == TokenType.LCURLY_BRACE:
            return self.concatenation()
        elif self.current_token.type == TokenType.ID:
            node = Lvalue()
            node.update(id=self.get_identifier())
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                node.update(exp1=self.expression())
                if self.current_token.type == TokenType.COLON:
                    node.register_token(self.eat())
                    node.update(exp2=self.expression())
                node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id or {")

    def concatenation(self):
        """
        <concatenation> ::= { <expression> <,<expression>>* }

        <multiple_concatenation> ::= { <expression> { <expression> <,<expression>>* } }

        两个合并到一起处理
        """
        node = Concatenation()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))

        exprs = [self.expression()]
        if self.current_token.type == TokenType.LCURLY_BRACE:
            # multiple_concatenation 的情况
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            exprs += self.list_items(self.expression)
            node.register_token(self.eat(TokenType.RCURLY_BRACE))
            node.update(expressions=exprs)
        elif self.current_token.type == TokenType.COMMA:
            while self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                exprs.append(self.expression())
            node.update(expressions=exprs)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be , or {")

        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def constant_expression(self):
        return self.expression()

    def expression(self):
        """
        <expression> ::= <primary>
                     ||= <UNARY_OPERATOR> <primary>
                     ||= <expression> <BINARY_OPERATOR> <expression>
                     ||= <expression> <QUESTION_MARK> <expression> : <expression>
                     ||= <STRING>
        """
        node = Expression()
        if self.current_token.type in self.verilog_first_set.unary_operator:
            node.update(op=self.get_punctuator())
            node.update(primary=self.primary())
        elif self.current_token.type in self.verilog_first_set.primary:
            node.update(primary=self.primary())
        elif self.current_token.type == TokenType.STRING:
            return self.get_string()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be unary_operator or primary or string")

        if self.current_token.type in self.verilog_first_set.binary_operator:
            node.update(bin_op=self.get_punctuator())
            node.update(expr=self.expression())
        elif self.current_token.type == TokenType.QUESTION:
            node.register_token(self.eat(TokenType.QUESTION))
            node.update(expr1=self.expression())
            node.register_token(self.eat(TokenType.COLON))
            node.update(expr2=self.expression())
        return node

    def primary(self):
        """
        <primary> ::= <number>
                  ||= <identifier>
                  ||= <identifier> [ <expression> ]
                  ||= <identifier> [ <constant_expression> : <constant_expression> ]
                  ||= <concatenation> | <multiple_concatenation>
                  ||= <function_call>
                  ||= ( <mintypmax_expression> )
        """
        if self.current_token.type == TokenType.NUMBER:
            return self.get_number()
        elif self.current_token.type == TokenType.ID:
            if self.peek_next_token().type == TokenType.LPAREN:
                # function call
                return self.function_call()
            else:
                node = Primary()
                node.update(id=self.get_identifier())
                if self.current_token.type == TokenType.LSQUAR_PAREN:
                    node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                    node.update(expr1=self.expression())
                    if self.current_token.type == TokenType.COLON:
                        node.register_token(self.eat(TokenType.COLON))
                        node.update(expr2=self.expression())
                    node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                return node
        elif self.current_token.type in self.verilog_first_set.concatenation:
            return self.concatenation()
        elif self.current_token.type == VerilogTokenType.SYSTEM_ID:
            return self.function_call()
        elif self.current_token.type == TokenType.LPAREN:
            node = Primary()
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.mintypmax_expression())
            node.register_token(self.eat(TokenType.RPAREN))
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be number or id or $id or { or (")

    def get_number(self):
        """
        对于 4'h111 的类型做分割
        """
        pattern = re.compile(r"(\d*\'[bBoOdDhH])([0-9a-fA-FxXzZ\?]+)")
        match = pattern.match(self.current_token.value)
        if match:
            line = self.current_token.line

            new_asts = []
            # 前面的 4'b
            value = match.group(1)
            token = Token(
                self.current_token.type,
                value,
                line,
                self.current_token.column - len(self.current_token.value) + len(value),
            )
            self.manual_register_token(token)
            node = Number(value)
            node.register_token([token])
            add_ast_type(node, VerilogCSS.BIT_WIDTH)
            new_asts.append(node)

            # 后面的 111
            token = Token(self.current_token.type, match.group(2), line, self.current_token.column)
            self.manual_register_token(token)
            node = Number(match.group(2))
            node.register_token([token])
            new_asts.append(node)

            self.manual_get_next_token()
            return new_asts
        else:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TokenType.NUMBER))
            return node

    def get_identifier(self, token_type=TokenType.ID):
        """
        hierarchical_path.mem_1.ADDR_WIDTH
        """
        nodes = [super().get_identifier(token_type)]
        while self.current_token.type == TokenType.DOT:
            self.eat(TokenType.DOT)
            nodes.append(super().get_identifier(token_type))

        for node in nodes:
            if bool(re.match(r"^[A-Z0-9_]+$", node.id)):
                # ID 全部为 大写/数字/下划线, 很可能为宏
                add_ast_type(node, CSS.ENUM_ID)
        return nodes

    def delay(self):
        """
        <delay> ::= '#' <number>
                  | '#' <identifier>
                  | '#' ( <mintypmax_expression> <,<mintypmax_expression>>? <,<mintypmax_expression>>?)
        """
        node = Delay()
        node.register_token(self.eat(TokenType.HASH))
        if self.current_token.type == TokenType.NUMBER:
            node.update(number=self.get_number())
        elif self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exp1=self.mintypmax_expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
                node.update(exp2=self.mintypmax_expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
                node.update(exp3=self.mintypmax_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        return node

    def mintypmax_expression(self):
        """
        <mintypmax_expression>
            ::= <expression>
            ||= <expression> : <expression> : <expression>
        """
        node = MintypmaxExpression()
        node.update(expr1=self.expression())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat())
            node.update(expr2=self.expression())
            node.register_token(self.eat(TokenType.COLON))
            node.update(expr3=self.expression())
        return node

    def range(self):
        """
        <range> ::= [ <constant_expression> : <constant_expression> ]
        """
        node = Range()
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(expr1=self.constant_expression())
        node.register_token(self.eat(TokenType.COLON))
        node.update(expr2=self.constant_expression())
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def input_declaration(self):
        """
        <input_declaration> ::= input <range>? <list_of_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.INPUT))
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())

        node.update(list_of_variables=self.list_of_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def output_declaration(self):
        """
        <output_declaration> ::= output <range>? <list_of_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.OUTPUT))
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())

        node.update(list_of_variables=self.list_of_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def inout_declaration(self):
        """
        <inout_declaration> ::= inout <range>? <list_of_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.INOUT))
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())

        node.update(list_of_variables=self.list_of_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def net_declaration(self):
        """
        <net_declaration> ::= <NETTYPE> <expandrange>? <delay>? <list_of_variables> ;
                            | trireg <charge_strength>? <expandrange>? <delay>?

        <charge_strength> ::= ( small )
                            | ( medium )
                            | ( large )
        """
        node = Declaration()
        if self.current_token.type == VerilogTokenType.TRIREG:
            node.update(keyword=self.get_keyword(css_type=VerilogCSS.NET_TYPE))
            if self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in (VerilogTokenType.SMALL, VerilogTokenType.MEDIUM, VerilogTokenType.LARGE):
                    node.update(charge_strength=self.get_keyword())
                    node.register_token(self.eat(TokenType.RPAREN))
                else:
                    self.error(ErrorCode.UNEXPECTED_TOKEN, "should be small/medium/large")
                if self.current_token.type in self.verilog_first_set.expandrange:
                    node.update(expandrange=self.expandrange())
                if self.current_token.type in self.verilog_first_set.delay:
                    node.update(delay=self.delay())

        elif self.current_token.type in self.verilog_first_set.net_type:
            node.update(keyword=self.get_keyword(css_type=VerilogCSS.NET_TYPE))
            if self.current_token.type in self.verilog_first_set.expandrange:
                node.update(expandrange=self.expandrange())
            if self.current_token.type in self.verilog_first_set.delay:
                node.update(delay=self.delay())
            node.update(list_of_variables=self.list_of_variables())
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be net type")

        return node

    def reg_declaration(self):
        """
        <reg_declaration> ::= reg <range>? <list_of_register_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.REG))
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())

        node.update(list_of_variables=self.list_of_register_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def time_declaration(self):
        """
        <time_declaration> ::= time <list_of_register_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.TIME))
        node.update(list_of_variables=self.list_of_register_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def integer_declaration(self):
        """
        <integer_declaration> ::= integer <list_of_register_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.INTEGER))
        node.update(list_of_variables=self.list_of_register_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def real_declaration(self):
        """
        <real_declaration> ::= real <list_of_variables> ;
        """
        node = Declaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.INTEGER))
        node.update(list_of_variables=self.list_of_variables())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def event_declaration(self):
        """
        <event_declaration> ::= event <name_of_event> <,<name_of_event>>* ;
        """
        node = EventDeclaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.EVENT))

        node.update(event_names=self.list_items(self.get_identifier))
        return node

    def continuous_assign(self):
        """
        <continuous_assign> ::= assign <drive_strength>? <delay>? <list_of_assignments> ;
                              | <NETTYPE> <drive_strength>? <expandrange>? <delay>? <list_of_assignments> ;
        """
        node = ContinuousAssign()
        if self.current_token.type == VerilogTokenType.ASSIGN:
            node.update(keyword=self.get_keyword(VerilogTokenType.ASSIGN))
            if self.current_token.type in self.verilog_first_set.drive_strength:
                node.update(drive_strength=self.drive_strength())
            if self.current_token.type in self.verilog_first_set.expandrange:
                node.update(expandrange=self.expandrange())
        elif self.current_token.type in self.verilog_first_set.net_type:
            node.update(keyword=self.get_keyword(css_type=VerilogCSS.NET_TYPE))
            if self.current_token.type in self.verilog_first_set.drive_strength:
                node.update(drive_strength=self.drive_strength())
        if self.current_token.type in self.verilog_first_set.delay:
            node.update(delay=self.delay())
        node.update(list_of_assignments=self.list_of_assignments())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def parameter_override(self):
        """
        <parameter_override> ::= defparam <list_of_param_assignments> ;
        """
        node = ParameterOverride()
        node.update(keyword=self.get_keyword(VerilogTokenType.DEFPARAM))
        node.update(param_assignments=self.list_items(self.param_assignment))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def statement(self):
        """
        <statement> ::= <blocking_assignment> ;
                    ||= <non_blocking_assignment> ;
                    ||= if ( <expression> ) <statement_or_null>
                    ||= if ( <expression> ) <statement_or_null> else <statement_or_null>
                    ||= case ( <expression> ) <case_item>+ endcase
                    ||= casez ( <expression> ) <case_item>+ endcase
                    ||= casex ( <expression> ) <case_item>+ endcase
                    ||= forever <statement>
                    ||= repeat ( <expression> ) <statement>
                    ||= while ( <expression> ) <statement>
                    ||= for ( <assignment> ; <expression> ; <assignment> ) <statement>
                    ||= <delay_or_event_control> <statement_or_null>
                    ||= wait ( <expression> ) <statement_or_null>
                    ||= -> <name_of_event> ;
                    ||= <seq_block>
                    ||= <par_block>
                    ||= <task_enable>
                    ||= <system_task_enable>
                    ||= disable <name_of_task> ;
                    ||= disable <name_of_block> ;
                    ||= assign <assignment> ;
                    ||= deassign <lvalue> ;
                    ||= force <assignment> ;
                    ||= release <lvalue> ;
                    ||= <genvar_declaration>

        @EXTEND-GRAMMAR: 不好区分阻塞和非阻塞, 所以合并二者
        @EXTEND-GRAMMAR: 添加 genvar
        """
        node = Statement()
        if self.current_token.type == TokenType.ID:
            # blocking_assignment
            if self.peek_next_token().type in (
                TokenType.LSQUAR_PAREN,
                TokenType.ASSIGN,
                VerilogTokenType.NON_BLOCK_ASSIGN,
            ):
                node.update(assignment=self.blocking_assignment())
                node.register_token(self.eat(TokenType.SEMI))
            else:
                # task_enable
                return self.task_enable()
        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node.update(assignment=self.blocking_assignment())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == VerilogTokenType.IF:
            node.update(keyword=self.get_keyword(VerilogTokenType.IF))
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement_or_null())
            if self.current_token.type == VerilogTokenType.ELSE:
                node.update(end_keyword=self.get_keyword(VerilogTokenType.ELSE))
                node.update(stmt_else=self.statement_or_null())
        elif self.current_token.type in (VerilogTokenType.CASE, VerilogTokenType.CASEZ, VerilogTokenType.CASEX):
            node.update(keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            case_items = [self.case_item()]
            while self.current_token.type in self.verilog_first_set.case_item:
                case_items.append(self.case_item())
            node.update(case_items=case_items)
            node.update(end_keyword=self.get_keyword())
        elif self.current_token.type == VerilogTokenType.FOREVER:
            node.update(keyword=self.get_keyword())
            node.update(stmt=self.statement())
        elif self.current_token.type in (VerilogTokenType.REPEAT, VerilogTokenType.WHILE):
            node.update(keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement())
        elif self.current_token.type == VerilogTokenType.FOR:
            node.update(keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(assignment=self.assignment())
            node.register_token(self.eat(TokenType.SEMI))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.SEMI))
            node.update(assignment_plus=self.assignment())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement())
        elif self.current_token.type in (TokenType.HASH, TokenType.AT_SIGN, VerilogTokenType.REPEAT):
            node.update(control=self.delay_or_event_control())
            node.update(stmt=self.statement_or_null())
        elif self.current_token.type == VerilogTokenType.WAIT:
            node.update(keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement_or_null())
        elif self.current_token.type == TokenType.POINT:
            node.register_token(self.eat())
            node.update(name=self.get_identifier())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == VerilogTokenType.BEGIN:
            # seq_block
            return self.seq_block()
        elif self.current_token.type == VerilogTokenType.FORK:
            return self.par_block()
        elif self.current_token.type == VerilogTokenType.SYSTEM_ID:
            return self.system_task_enable()
        elif self.current_token.type == VerilogTokenType.DISABLE:
            node.update(keyword=self.get_keyword())
            node.update(name=self.get_identifier())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type in (VerilogTokenType.ASSIGN, VerilogTokenType.FORCE):
            node.update(keyword=self.get_keyword())
            node.update(assignment=self.assignment())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type in (VerilogTokenType.DEASSIGN, VerilogTokenType.RELEASE):
            node.update(keyword=self.get_keyword())
            node.update(Lvalue=self.lvalue())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == VerilogTokenType.GENVAR:
            return self.genvar_declaration()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "statement miss match")
        return node

    def seq_block(self):
        """
        <seq_block>
                    ::= begin <statement>* end
                    ||= begin : <name_of_block> <block_declaration>* <statement>* end
        """
        node = SeqBlock()
        node.update(keyword=self.get_keyword(VerilogTokenType.BEGIN))
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat())
            node.update(name=self.get_identifier())
            block_declarations = []
            while self.current_token.type in self.verilog_first_set.block_declaration:
                block_declarations.append(self.block_declaration())
            node.update(block_declarations=block_declarations)
        stmts = []
        while self.current_token.type in self.verilog_first_set.statement:
            stmts.append(self.statement())
        node.update(stmts=stmts)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.END))
        return node

    def par_block(self):
        """
        <par_block>
                    ::= fork <statement>* join
                    ||= fork : <name_of_block> <block_declaration>* <statement>* join
        """
        node = ParBlock()
        node.update(keyword=self.get_keyword(VerilogTokenType.FORK))
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat())
            node.update(name=self.get_identifier())
            block_declarations = []
            while self.current_token.type in self.verilog_first_set.block_declaration:
                block_declarations.append(self.block_declaration())
            node.update(block_declarations=block_declarations)
        stmts = []
        while self.current_token.type in self.verilog_first_set.statement:
            stmts.append(self.statement())
        node.update(stmts=stmts)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.JOIN))
        return node

    def block_declaration(self):
        """
        <block_declaration>
                            ::= <parameter_declaration>
                            ||= <reg_declaration>
                            ||= <integer_declaration>
                            ||= <real_declaration>
                            ||= <time_declaration>
                            ||= <event_declaration>
                            ||= <module_instantiation>

        @EXTEND-GRAMMAR: 添加 module_instantiation
        """
        kv_map = {
            VerilogTokenType.PARAMETER: self.parameter_declaration,
            VerilogTokenType.REG: self.reg_declaration,
            VerilogTokenType.INTEGER: self.integer_declaration,
            VerilogTokenType.REAL: self.real_declaration,
            VerilogTokenType.TIME: self.time_declaration,
            VerilogTokenType.EVENT: self.event_declaration,
        }
        if self.current_token.type in kv_map:
            return kv_map[self.current_token.type]()
        elif self.current_token.type == TokenType.ID and self.peek_next_token().type in (TokenType.ID, TokenType.HASH):
            return self.module_instantiation()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "output block declaration kv map")

    def task_enable(self):
        """
        <task_enable>
                        ::= <name_of_task>
                        ||= <name_of_task> ( <expression> <,<expression>>* ) ;
        """
        node = TaskEnable()
        node.update(name=self.get_identifier())
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exprs=self.list_items(self.expression))
            node.register_token(self.eat(TokenType.RPAREN))
            node.register_token(self.eat(TokenType.SEMI))
        return node

    def system_task_enable(self):
        """
        <system_task_enable>
                            ::= <name_of_system_task> ;
                            ||= <name_of_system_task> ( <expression> <,<expression>>* ) ;
        <name_of_system_task> ::= $<system_identifier> (Note: the $ may not be followed by a space.)
        """
        node = SystemTaskEnable()
        node.update(name=self.get_identifier(VerilogTokenType.SYSTEM_ID))
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exprs=self.list_items(self.expression))
            node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def list_of_register_variables(self):
        """
        <list_of_register_variables> ::= <register_variable> <,<register_variable>>*
        """
        return self.list_items(self.register_variable)

    def register_variable(self):
        """
        <register_variable> ::= <name_of_register>
                              | <name_of_memory> [ <constant_expression> : <constant_expression> ]
        """
        node = RegVar()
        node.update(name=self.get_identifier())
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(index_begin=self.expression())
            node.register_token(self.eat(TokenType.COLON))
            node.update(index_end=self.expression())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def gate_declaration(self):
        """
        <gate_declaration> ::= <GATETYPE> <drive_strength>? <delay>?  <gate_instance> <,<gate_instance>>* ;
        """

        if self.current_token.type not in self.verilog_first_set.gate_type:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be gate type")

        node = GateDeclaration()
        node.update(keyword=self.get_keyword(css_type=VerilogCSS.GATE_WAY))
        if self.current_token.type in self.verilog_first_set.drive_strength:
            node.update(drive_strength=self.drive_strength())
        if self.current_token.type in self.delay:
            node.update(delay=self.delay())

        node.update(gate_instances=self.list_items(self.gate_instance))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def gate_instance(self):
        """
        <gate_instance> ::= <name_of_gate_instance>? ( <terminal> <,<terminal>>* )

        <name_of_gate_instance> ::= <IDENTIFIER> <range>?
        """
        node = GateInstance()
        if self.current_token.type == TokenType.ID:
            node.update(name=self.get_identifier())
            if self.current_token.type in self.verilog_first_set.range:
                node.update(range=self.range())
        node.register_token(self.eat(TokenType.LPAREN))

        node.update(terminals=self.list_items(self.terminal))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def terminal(self):
        """
        <terminal> ::= <expression>
        """
        return self.expression()

    def UDP_instantiation(self):
        """
        <UDP_instantiation> ::= <name_of_UDP> <drive_strength>? <delay>? <UDP_instance> <,<UDP_instance>>* ;
        """
        node = UDPInstantiation()
        node.update(name=self.get_identifier())
        if self.current_token.type in self.verilog_first_set.drive_strength:
            node.update(drive_strength=self.drive_strength())
        if self.current_token.type in self.verilog_first_set.delay:
            node.update(delay=self.delay())

        node.update(udp_instances=self.list_items(self.UDP_instance))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def UDP_instance(self):
        """
        <UDP_instance> ::= <name_of_UDP_instance>? ( <terminal> <,<terminal>>* )
        """
        node = UDPInstance()
        if self.current_token.type == TokenType.ID:
            node.update(name=self.get_identifier())
            if self.current_token.type in self.verilog_first_set.range:
                node.update(range=self.range())
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(terminals=self.list_items(self.terminal))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def module_instantiation(self):
        """
        <module_instantiation> ::= <name_of_module> <parameter_value_assignment>? <module_instance> <,<module_instance>>* ;

        <parameter_value_assignment> ::= # ( <expression> <,<expression>>* )
        """
        node = ModuleInstantiation()
        node.update(name=self.get_identifier())
        add_ast_type(node.name, VerilogCSS.DEFINED_MODULE)
        if self.current_token.type == TokenType.HASH:
            node.register_token(self.eat())
            node.register_token(self.eat(TokenType.LPAREN))
            parms = []
            if self.current_token.type in self.verilog_first_set.expression:
                parms.append(self.expression())
                if self.current_token.type == TokenType.ASSIGN:
                    node.register_token(self.eat(TokenType.ASSIGN))
                    self.expression()
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                parms.append(self.expression())
                if self.current_token.type == TokenType.ASSIGN:
                    node.register_token(self.eat(TokenType.ASSIGN))
                    self.expression()
            node.update(parms=parms)
            node.register_token(self.eat(TokenType.RPAREN))

        node.update(module_instances=self.list_items(self.module_instance))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def module_instance(self):
        """
        <module_instance> ::= <name_of_instance> ( <list_of_module_connections>? )

        <list_of_module_connections> ::= <module_port_connection> <,<module_port_connection>>*
                                     ||= <named_port_connection> <,<named_port_connection>>*
        """
        node = ModuleInstance()
        node.update(name=self.get_identifier())
        if self.current_token.type in self.verilog_first_set.range:
            node.update(range=self.range())
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in (self.verilog_first_set.expression, TokenType.DOT, TokenType.COMMA):
            if self.current_token.type == TokenType.DOT:
                node.update(connections=self.list_items(self.named_port_connection))
            else:
                node.update(connections=self.list_items(self.module_port_connection))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def named_port_connection(self):
        """
        <named_port_connection> ::= .< IDENTIFIER> ( <expression> )
        """
        node = NamePortConnection()
        node.register_token(self.eat(TokenType.DOT))
        node.update(name=self.get_identifier())
        add_ast_type(node.name, VerilogCSS.PORT_NAME)
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(expr=self.expression())
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def module_port_connection(self):
        """
        <module_port_connection>
            ::= <expression>
            ||= <NULL>

        <NULL>
            ::= nothing - this form covers the case of an empty item in a list - for example:
                (a, b, , d)
        """
        if self.current_token.type in self.verilog_first_set.expression:
            return self.expression()
        elif self.current_token.type == TokenType.COMMA:
            return None
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expression or NULL")

    def initial_statement(self):
        """
        <initial_statement> ::= initial <statement>
        """
        node = InitialStmt()
        node.update(keyword=self.get_keyword(VerilogTokenType.INITIAL))
        node.update(stmt=self.statement())
        return node

    def always_statement(self):
        """
        <always_statement> ::= always <statement>
        """
        node = AlwaysStmt()
        node.update(keyword=self.get_keyword(VerilogTokenType.ALWAYS))
        node.update(stmt=self.statement())
        return node

    def blocking_assignment(self):
        """
        <blocking_assignment>
                            ::= <lvalue> (=|<=) <expression>
                            ||= <lvalue> = <delay_or_event_control> <expression> ;

        @EXTEND-GRAMMAR: 不好区分阻塞和非阻塞, 所以合并二者
        """
        node = BlockingAssign()
        node.update(lvalue=self.lvalue())
        if self.current_token.type in (TokenType.ASSIGN, VerilogTokenType.NON_BLOCK_ASSIGN):
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be '=' or '<='")
        if self.current_token.type in self.verilog_first_set.expression:
            node.update(expr=self.expression())
        elif self.current_token.type in self.verilog_first_set.delay_or_event_control:
            node.update(control=self.delay_or_event_control())
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expression or delay or event control")
        return node

    def delay_or_event_control(self):
        """
        <delay_or_event_control>
                                ::= <delay_control>
                                ||= <event_control>
                                ||= repeat ( <expression> ) <event_control>
        """
        if self.current_token.type == TokenType.HASH:
            return self.delay_control()
        elif self.current_token.type == TokenType.AT_SIGN:
            return self.event_control()
        elif self.current_token.type == VerilogTokenType.REPEAT:
            node = Control()
            node.update(keyword=self.get_keyword(VerilogTokenType.REPEAT))
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(event_control=self.event_control())
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be # @ repeat")

    def delay_control(self):
        """
        <delay_control>
            ::= # <number>
            ||= # <identifier>
            ||= # ( <mintypmax_expression> )
        """
        node = Control()
        node.register_token(self.eat(TokenType.HASH))
        if self.current_token.type == TokenType.NUMBER:
            node.update(number=self.get_number())
        elif self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.mintypmax_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be number id (")
        return node

    def event_control(self):
        """
        <event_control>
            ::= @ <identifier>
            ||= @ ( <event_expression> )
        """
        node = Control()
        node.register_token(self.eat(TokenType.AT_SIGN))
        if self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.event_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "id or (")
        return node

    def event_expression(self):
        """
        <event_expression>
                            ::= <expression>
                            ||= (posedge|negedge) <expression> ',' <event_expression>
                            ||= <event_expression> or <event_expression>
                            ||= *
        """
        node = EventExpression()
        if self.current_token.type == TokenType.MUL:
            # always @(*)
            self.current_token.type = VerilogTokenType.STAR
            node.register_token(self.eat(VerilogTokenType.STAR))
        elif self.current_token.type in self.verilog_first_set.expression:
            node.update(expr=self.expression())
        elif self.current_token.type in (VerilogTokenType.POSEDGE, VerilogTokenType.NEGEDGE):
            node.update(edge=self.get_keyword())
            node.update(expr=self.expression())
            while self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(event_expr=self.event_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expr posedge negedge")

        if self.current_token.type == VerilogTokenType.OR:
            node.register_token(self.eat())
            node.update(event_expr=self.event_expression())
        return node

    def case_item(self):
        """
        <case_item>
                    ::= <expression> <,<expression>>* : <statement_or_null>
                    ||= default : <statement_or_null>
                    ||= default <statement_or_null>
        """
        node = CaseItem()
        if self.current_token.type in self.verilog_first_set.expression:
            node.update(exprs=self.list_items(self.expression))
            node.register_token(self.eat(TokenType.COLON))
            node.update(stmt=self.statement_or_null())
        elif self.current_token.type == VerilogTokenType.DEFAULT:
            node.update(keyword=self.get_keyword())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat())
            node.update(stmt=self.statement_or_null())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expr or default")
        return node

    def specify_block(self):
        """
        <specify_block> ::= specify <specify_item>* endspecify
        """
        node = SpecifyBlock()
        node.update(keyword=self.get_keyword(VerilogTokenType.SPECIFY))
        specify_items = []
        while self.current_token.type in self.verilog_first_set.specify_item:
            specify_items.append(self.specify_item())
        node.update(specify_items=specify_items)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDSPECIFY))
        return node

    def specify_item(self):
        """
        <specify_item>
                        ::= <specparam_declaration>
                        ||= <path_declaration>
                        ||= <level_sensitive_path_declaration>
                        ||= <edge_sensitive_path_declaration>
                        ||= <system_timing_check>
                        ||= <sdpd>
        """
        if self.current_token.type == VerilogTokenType.SPECPARAM:
            node = self.specparam_declaration()
        elif self.current_token.type == TokenType.LPAREN:
            node = self.path_declaration()
        elif self.current_token.type == VerilogTokenType.IF:
            # 扩展 path_description 文法, 合并处理
            # - level_sensitive_path_declaration
            # - edge_sensitive_path_declaration
            # - sdpd
            node = self.level_sensitive_path_declaration()
        elif self.current_token.type in self.verilog_first_set.edge_sensitive_path_declaration:
            node = self.edge_sensitive_path_declaration()
        elif self.current_token.type == VerilogTokenType.SYSTEM_ID:
            node = self.system_timing_check()
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                "should be specparam, path, level_sensitive_path, edge_sensitive_path, system_timing_check, sdpd",
            )
        return node

    def specparam_declaration(self):
        """
        <specparam_declaration> ::= specparam <list_of_specparam_assignment> ;

        <list_of_param_assignments> ::=<param_assignment><,<param_assignment>>*
        """
        node = SpecparamDeclaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.SPECPARAM))
        node.update(assignments=self.list_items(self.param_assignment))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def path_declaration(self):
        """
        <path_declaration> ::= <path_description> = <path_delay_value> ;
        """
        node = PathDeclaration()
        node.update(path_declaration=self.path_description())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(path_delay_value=self.path_delay_value())
        return node

    def path_description(self):
        """
        @EXTEND-GRAMMAR: <polarity_operator>?
        补充 edge_sensitive_path_declaration 的情况

        <path_description>
            ::= ( <specify_input_terminal_descriptor> <polarity_operator>? => <specify_output_terminal_descriptor> )
            ||= ( <list_of_path_inputs> <polarity_operator>? *> <list_of_path_outputs> )

        <specify_input_terminal_descriptor>
            ::= <input_identifier>
            ||= <input_identifier> [ <constant_expression> ]
            ||= <input_identifier> [ <constant_expression> : <constant_expression> ]

        <specify_output_terminal_descriptor>
            ::= <output_identifier>
            ||= <output_identifier> [ <constant_expression> ]
            ||= <output_identifier> [ <constant_expression> : <constant_expression> ]

        <input_identifier>
            ::= the <IDENTIFIER> of a module input or inout terminal

        <output_identifier>
            ::= the <IDENTIFIER> of a module output or inout terminal.

        <polarity_operator>
            ::= +
            ||= -

        <edge_identifier>
            ::= posedge
            ||= negedge
        """
        node = PathDescription()
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.verilog_first_set.edge_identifier:
            node.update(edge_id=self.get_keyword())
        node.update(specify_input_terminal_descriptors=self.list_items(self.specify_terminal_descriptor))
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            node.update(polarity_operator1=self.get_punctuator())
        if len(node.specify_input_terminal_descriptors) == 1:
            # 说明是单个变量, 匹配 =>
            node.register_token(self.eat(TokenType.LAMBDA_POINT))
        else:
            node.register_token(self.eat(VerilogTokenType.MULTI_ASSIGN))

        if self.current_token.type == TokenType.LPAREN:
            # edge_sensitive_path_declaration
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(specify_output_terminal_descriptors=self.list_items(self.specify_terminal_descriptor))
            if self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
                node.update(polarity_operator2=self.get_punctuator())
            node.register_token(self.eat(TokenType.COLON))
            node.update(data_source_expression=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            node.update(specify_output_terminal_descriptors=self.list_items(self.specify_terminal_descriptor))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def specify_terminal_descriptor(self):
        """
        <specify_input_terminal_descriptor>
            ::= <input_identifier>
            ||= <input_identifier> [ <constant_expression> ]
            ||= <input_identifier> [ <constant_expression> : <constant_expression> ]
        """
        node = SpecifyTerminalDescriptor()
        node.update(identifier=self.get_identifier())
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(index_begin=self.constant_expression())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
                node.update(index_end=self.constant_expression())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def path_delay_value(self):
        """
        <path_delay_value>
            ::= <path_delay_expression>
            ||= ( <path_delay_expression>, <path_delay_expression> )
            ||= ( <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>)
            ||= ( <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression> )
            ||= ( <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression>,
                <path_delay_expression>, <path_delay_expression> )

        <path_delay_expression>
            ::= <mintypmax_expression>
        """
        node = PathDelayValue()
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expressions=self.list_items(self.mintypmax_expression))
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            node.update(expression=self.mintypmax_expression())
        return node

    def function_call(self):
        """
        <function_call>
            ::= <name_of_function> ( <expression> <,<expression>>* )
            ||= <name_of_system_function> ( <expression> <,<expression>>* )
            ||= <name_of_system_function>

        <name_of_function>
            ::= <identifier>

        <name_of_system_function>
            ::= $<SYSTEM_IDENTIFIER>
            (Note: the $ may not be followed by a space.)
        """
        node = FunctionCall()
        if self.current_token.type == VerilogTokenType.SYSTEM_ID:
            node.update(name=self.get_identifier(VerilogTokenType.SYSTEM_ID))
        else:
            node.update(name=self.get_identifier())

        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(arguments=self.list_items(self.expression))
            node.register_token(self.eat(TokenType.RPAREN))
        return node

    def level_sensitive_path_declaration(self):
        """
        <level_sensitive_path_declaration>
            ::= if (<conditional_port_expression>) <path_declaration>

        @文法修正
        """
        node = LevelSensitivePathDeclaration()
        node.update(keyword=self.get_keyword(VerilogTokenType.IF))
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(conditional_port_expression=self.conditional_port_expression())
        node.register_token(self.eat(TokenType.RPAREN))
        node.update(path_declaration=self.path_declaration())
        return node

    def conditional_port_expression(self):
        """
        <conditional_port_expression>
            ::= <port_reference>
            ||= <UNARY_OPERATOR><port_reference>
            ||= <port_reference><BINARY_OPERATOR><port_reference>
        """
        if self.current_token.type == TokenType.ID:
            port_ref = self.port_reference()
            if self.current_token.type in self.verilog_first_set.binary_operator:
                node = BinaryOp()
                node.update(expr1=port_ref)
                node.update(op=self.get_punctuator())
                node.update(expr2=self.port_reference())
                return node
            else:
                return port_ref
        elif self.current_token.type in self.verilog_first_set.unary_operator:
            node = UnaryOp()
            node.register_token(self.eat())
            node.update(expr=self.port_reference())
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be port_reference or unary_operator")

    def edge_sensitive_path_declaration(self):
        """
        <edge_sensitive_path_declaration>
            ::= <if (<expression>)>? (<edge_identifier>?
                <specify_input_terminal_descriptor> =>
                (<specify_output_terminal_descriptor> <polarity_operator>?
                : <data_source_expression>)) = <path_delay_value>;
            ||= <if (<expression>)>? (<edge_identifier>?
                <specify_input_terminal_descriptor> "*>"
                (<list_of_path_outputs> <polarity_operator>?
                : <data_source_expression>)) =<path_delay_value>;

        <data_source_expression>
            Any expression, including constants and lists. Its width must be one bit or
            equal to the  destination's width. If the destination is a list, the data
            source must be as wide as the sum of  the bits of the members.

        <edge_identifier>
            ::= posedge
            ||= negedge
        """
        node = EdgeSensitivePathDeclaration()
        if self.current_token.type == VerilogTokenType.IF:
            node.update(keyword=self.get_keyword(VerilogTokenType.IF))
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expression=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in (VerilogTokenType.POSEDGE, VerilogTokenType.NEGEDGE):
            node.update(edge_id=self.get_keyword())
        node.update(specify_input_terminal_descriptors=self.list_items(self.specify_terminal_descriptor))

        if len(node.specify_input_terminal_descriptors) == 1:
            node.register_token(self.eat(TokenType.LAMBDA_POINT))
        else:
            node.register_token(self.eat(VerilogTokenType.MULTI_ASSIGN))

        node.register_token(self.eat(TokenType.LPAREN))
        node.update(specify_output_terminal_descriptors=self.list_items(self.specify_terminal_descriptor))
        if self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            node.update(polarity_operator=self.get_punctuator())
        node.register_token(self.eat(TokenType.COLON))
        node.update(data_source_expression=self.expression())
        node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(path_delay_value=self.path_delay_value())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def system_timing_check(self):
        """
        <system_timing_check>
            ::= $setup( <timing_check_event>, <timing_check_event>,
                <timing_check_limit>
                <,<notify_register>>? ) ;
            ||= $hold( <timing_check_event>, <timing_check_event>,
                <timing_check_limit>
                <,<notify_register>>? ) ;
            ||= $period( <controlled_timing_check_event>, <timing_check_limit>
                <,<notify_register>>? ) ;
            ||= $width( <controlled_timing_check_event>, <timing_check_limit>
                <,<constant_expression>,<notify_register>>? ) ;
            ||= $skew( <timing_check_event>, <timing_check_event>,
                <timing_check_limit>
                <,<notify_register>>? ) ;
            ||= $recovery( <controlled_timing_check_event>,
                <timing_check_event>,
                <timing_check_limit> <,<notify_register>>? ) ;
            ||= $setuphold( <timing_check_event>, <timing_check_event>,
                <timing_check_limit>, <timing_check_limit> <,<notify_register>>? ) ;

        <timing_check_limit> ::= <expression>
        <notify_register> ::= <identifier>
        """
        node = SystemTimingCheck()
        node.update(sysid=self.get_identifier(VerilogTokenType.SYSTEM_ID))

        node.register_token(self.eat(TokenType.LPAREN))
        if node.sysid.value == "$setup":
            node.update(event1=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(event2=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$hold":
            node.update(event1=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(event2=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$period":
            node.update(event=self.time_check_event(is_controlled=True))
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$width":
            node.update(event=self.time_check_event(is_controlled=True))
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(constant_expr=self.expression())
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$skew":
            node.update(event1=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(event2=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$recovery":
            node.update(event1=self.time_check_event(is_controlled=True))
            node.register_token(self.eat(TokenType.COMMA))
            node.update(event2=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        elif node.sysid.value == "$setuphold":
            node.update(event1=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(event2=self.time_check_event())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit1=self.expression())
            node.register_token(self.eat(TokenType.COMMA))
            node.update(limit2=self.expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(notify_register=self.get_identifier())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "System timing check system identifier")
        node.register_token(self.eat(TokenType.RPAREN))
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def time_check_event(self, is_controlled=False):
        """
        <timing_check_event>
            ::= <timing_check_event_control>? <specify_terminal_descriptor>
                <&&& <timing_check_condition>>?

        <controlled_timing_check_event>
            ::= <timing_check_event_control> <specify_terminal_descriptor>
                <&&&  <timing_check_condition>>?
        """
        node = TimeCheckEvent()
        if is_controlled or self.current_token.type in self.verilog_first_set.timing_check_event_control:
            node.update(control=self.timing_check_event_control())
        node.update(specify_terminal_descriptor=self.specify_terminal_descriptor())
        if self.current_token.type == VerilogTokenType.TIME_CHECK_AND:
            node.register_token(self.eat(VerilogTokenType.TIME_CHECK_AND))
            node.update(condition=self.timing_check_condition())
        return node

    def timing_check_event_control(self):
        """
        <timing_check_event_control>
            ::= posedge
            ||= negedge
            ||= <edge_control_specifier>
        """
        if self.current_token.type in (VerilogTokenType.POSEDGE, VerilogTokenType.NEGEDGE):
            return self.get_keyword()
        elif self.current_token.type == VerilogTokenType.EDGE:
            return self.edge_control_specifier()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "Expected edge or posedge or negedge")

    def edge_control_specifier(self):
        """
        <edge_control_specifier> ::= edge  [ <edge_descriptor><,<edge_descriptor>>*]
        """
        node = EdgeControlSpecifier()
        node.update(keyword=self.get_keyword(VerilogTokenType.EDGE))
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(edge_descriptors=self.list_items(self.edge_descriptor))
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def edge_descriptor(self):
        """
        <edge_descriptor>
            ::= 01
            ||= 10
            ||= 0x
            ||= x1
            ||= 1x
            ||= x0
        """
        # TODO

    def timing_check_condition(self):
        """
        <timing_check_condition>
            ::= <scalar_timing_check_condition>
            ||= ( <scalar_timing_check_condition> )
        """
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.scalar_timing_check_condition()
            self.eat(TokenType.RPAREN)
            return node
        else:
            return self.scalar_timing_check_condition()

    def scalar_timing_check_condition(self):
        """
        <scalar_timing_check_condition>
            ::= <scalar_expression>
            ||= ~<scalar_expression>
            ||= <scalar_expression> == <scalar_constant>
            ||= <scalar_expression> === <scalar_constant>
            ||= <scalar_expression> != <scalar_constant>
            ||= <scalar_expression> !== <scalar_constant>
        """
        node = ScalarTimingCheckCondition()
        if self.current_token.type == TokenType.TILDE:
            node.update(op=self.unary_operator())
            node.update(expr=self.expression())
        else:
            node.update(expr=self.expression())
            if self.current_token.type in (TokenType.EQ, TokenType.STRICT_EQ, TokenType.NE, TokenType.STRICT_NE):
                node.update(op=self.get_punctuator())
                node.update(constant=self.scalar_constant())

        return node

    def scalar_constant(self):
        """
        <scalar_constant>
            ::= 1'b0
            ||= 1'b1
            ||= 1'B0
            ||= 1'B1
            ||= 'b0
            ||= 'b1
            ||= 'B0
            ||= 'B1
            ||= 1
            ||= 0
        """
        # TODO

    def unary_operator(self):
        """
        <UNARY_OPERATOR> is one of the following tokens:
                +  -  !  ~  &  ~&  |  ^|  ^  ~^
        """
        return self.get_punctuator()

    def binary_operator(self):
        """
        <BINARY_OPERATOR> is one of the following tokens:
                    +  -  *  /  %  ==  !=  ===  !==  &&  ||  <  <=  >  >=  &  |  ^  ^~  >>  <<
        """
        return self.get_punctuator()
