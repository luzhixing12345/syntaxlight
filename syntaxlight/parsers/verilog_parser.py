from .parser import Parser
from ..lexers import TokenType, VerilogTokenType, Token, VerilogTokenSet
from ..error import ErrorCode
from ..asts.verilog_ast import *
from enum import Enum


class VerilogCSS(Enum):
    NET_TYPE = "NetType"
    STRENGTH0 = "Strength0"
    STRENGTH1 = "Strength1"
    GATE_WAY = "GateWay"


class VerilogParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.verilog_first_set = VerilogTokenSet()

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
            node.update(module=self.module)
        elif self.current_token.type in self.verilog_first_set.udp:
            node.update(udp=self.udp())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should match a module or udp")

        return node

    def module(self):
        """
        <module> ::= module <name_of_module> <list_of_ports>? ; <module_item>* endmodule
                   | macromodule <name_of_module> <list_of_ports>? ; <module_item>* endmodule
        """
        node = Module()
        if self.current_token.type in self.verilog_first_set.module:
            node.update(module=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be module or macromodule")

        node.update(name=self.identifier())
        node.update(list_of_ports=self.list_of_ports())
        node.register_token(self.eat(TokenType.SEMI))
        module_items = []
        while self.current_token.type in self.verilog_first_set.module_item:
            module_items.append(self.module_item())
        node.update(module_items=module_items)
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDMODULE))
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
        <port> ::= <port_expression>?
                 | . <name_of_port> ( <port_expression>? )
        """
        node = Port()
        if self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            node.update(name=self.identifier())
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.verilog_first_set.port_expression:
                node.update(port_expression=self.port_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.verilog_first_set.port_expression:
            node.update(port_expression=self.port_expression())

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
        return port_references

    def port_reference(self):
        """
        <port_reference> ::= <name_of_variable>
                           | <name_of_variable> [ <constant_expression> ]
                           | <name_of_variable> [ <constant_expression> :<constant_expression> ]
        """
        node = PortReference()
        node.update(name=self.identifier())
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
        """
        # TODO
        module_map = {
            VerilogTokenType.PARAMETER: self.parameter_declaration,
            VerilogTokenType.INPUT: self.input_declaration,
            VerilogTokenType.OUTPUT: self.output_declaration,
            VerilogTokenType.INOUT: self.inout_declaration,
            VerilogTokenType.REG: self.reg_declaration,
            VerilogTokenType.TIME: self.time_declaration, 
            VerilogTokenType.INTEGER: self.integer_declaration,
            VerilogTokenType.REAL: self.real_declaration,
            VerilogTokenType.EVENT: self.event_declaration,
            
        }
        
        if self.current_token.type in self.verilog_first_set.net_declaration:
            return self.net_declaration()
        elif self.current_token.type in self.verilog_first_set.gate_declaration:
            return self.gate_declaration()
        elif self.current_token.type in self.verilog_first_set.UDP_instantiation:
            return self.UDP_instantiation()
        else:
            self.error()

    def udp(self):
        """
        <UDP> ::= primitive <name_of_UDP> ( <name_of_variable> <,<name_of_variable>>* ) ; <UDP_declaration>+ <UDP_initial_statement>?   <table_definition> endprimitive
        """
        node = UDP()
        node.update(keyword=self.get_keyword(VerilogTokenType.PRIMITIVE))
        node.update(name=self.identifier())
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
        node.update(name=self.identifier())
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
        node.update(name=self.identifier())
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

        node.update(name=self.identifier())
        tf_declarations = [self.tf_declaration()]
        while self.current_token.type in self.verilog_first_set.tf_declaration:
            tf_declarations.append(self.tf_declaration())
        node.update(stmt=self.statement())
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDFUNCTION))
        return node

    def parameter_declaration(self):
        """
        <parameter_declaration> ::= parameter <list_of_param_assignments> ;

        <list_of_param_assignments> ::=<param_assignment><,<param_assignment>*

        """
        node = Parameter()
        node.update(keyword=self.get_keyword(VerilogTokenType.PARAMETER))

        param_assignments = [self.param_assignment()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat())
            param_assignments.append(self.param_assignment())

        node.update(param_assignments=param_assignments)
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def param_assignment(self):
        """
        <param_assignment> ::=<identifier> = <constant_expression>
        """
        node = ParameterAssign()
        node.update(key=self.identifier())
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
        return self.list_items(self.identifier)

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
        node.update(lvalue=self.lvalue())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(exp=self.expression())
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
            node.update(id=self.identifier())
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
        """
        node = Concatenation()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))

        node.update(expressions=self.list_items(self.expression))
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def expression(self):
        """
        <expression> ::= <primary>
                         ||= <UNARY_OPERATOR> <primary>
                         ||= <expression> <BINARY_OPERATOR> <expression>
                         ||= <expression> <QUESTION_MARK> <expression> : <expression>
                         ||= <STRING>
        """

    def primary(self):
        """
        <primary> ::= <number>
                  ||= <identifier>
                  ||= <identifier> [ <expression> ]
                  ||= <identifier> [ <constant_expression> : <constant_expression> ]
                  ||= <concatenation>
                  ||= <multiple_concatenation>
                  ||= <function_call>
                  ||= ( <mintypmax_expression> )
        """

    def delay(self):
        """
        <delay> ::= '#' <number>
                      | '#' <identifier>
                      | '#' ( <mintypmax_expression> <,<mintypmax_expression>>? <,<mintypmax_expression>>?)
        """
        node = Delay()
        node.register_token(self.eat(TokenType.HASH))
        if self.current_token.type == TokenType.NUMBER:
            node.update(number=self.number())
        elif self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exp1=self.mintypmax_expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
                node.update(exp2=self.mintypmax_expression())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
                node.update(exp3=self.mintypmax_expression())
        return node

    def mintypmax_expression(self):
        """ """

    def range(self):
        """ """

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
        node.update(keyword=self.get_keyword(VerilogTokenType.INOUT))
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

        node.update(event_names=self.list_items(self.identifier))
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
        return node

    def parameter_override(self):
        """
        <parameter_override> ::= defparam <list_of_param_assignments> ;
        """
        node = ParameterOverride()
        node.update(keyword=self.get_keyword(VerilogTokenType.DEFPARAM))
        param_assignments = [self.param_assignment()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat())
            param_assignments.append(self.param_assignment())

        node.update(param_assignments=param_assignments)
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
        """
        node = Statement()
        if self.current_token.type == TokenType.ID:
            # blocking_assignment
            if self.peek_next_token().type in (TokenType.LSQUAR_PAREN, TokenType.ASSIGN, TokenType.LT):
                node.update(assignment = self.blocking_assignment())
                node.register_token(self.eat(TokenType.SEMI))
            else:
                # task_enable
                return self.task_enable()
        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node.update(assignment = self.blocking_assignment())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == VerilogTokenType.IF:
            node.update(keyword = self.get_keyword(VerilogTokenType.IF))
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr = self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt = self.statement_or_null())
            if self.current_token.type == VerilogTokenType.ELSE:
                node.update(end_keyword = self.get_keyword(VerilogTokenType.ELSE))
                node.update(stmt_else = self.statement_or_null())
        elif self.current_token.type in (VerilogTokenType.CASE, VerilogTokenType.CASEZ, VerilogTokenType.CASEX):
            node.update(keyword = self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr = self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            case_items = [self.case_item()]
            while self.current_token.type in self.verilog_first_set.case_item:
                case_items.append(self.case_item())
            node.update(case_items = case_items)
            node.update(end_keyword = self.get_keyword())
        elif self.current_token.type == VerilogTokenType.FOREVER:
            node.update(keyword = self.get_keyword())
            node.update(stmt = self.statement())
        elif self.current_token.type in (VerilogTokenType.REPEAT, VerilogTokenType.WHILE):
            node.update(keyword  = self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr = self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt = self.statement())
        elif self.current_token.type == VerilogTokenType.FOR:
            node.update(keyword = self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(assignment = self.assignment())
            node.register_token(self.eat(TokenType.SEMI))
            node.update(expr = self.expression())
            node.register_token(self.eat(TokenType.SEMI))
            node.update(assignment_plus = self.assignment())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt = self.statement())
        elif self.current_token.type in (TokenType.HASH, TokenType.AT_SIGN, VerilogTokenType.REPEAT):
            node.update(control = self.delay_or_event_control())
            node.update(stmt = self.statement_or_null())
        elif self.current_token.type == VerilogTokenType.WAIT:
            node.update(keyword = self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr = self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt = self.statement_or_null())
        elif self.current_token.type == TokenType.POINT:
            node.register_token(self.eat())
            node.update(name = self.identifier())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == VerilogTokenType.BEGIN:
            # seq_block
            return self.seq_block()
        elif self.current_token.type == VerilogTokenType.FORK:
            return self.par_block()
        elif self.current_token.type == VerilogTokenType.SYSTEM_ID:
            return self.system_task_enable()
        elif self.current_token.type == VerilogTokenType.DISABLE:
            node.update(keyword = self.get_keyword())
            node.update(name = self.identifier())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type in (VerilogTokenType.ASSIGN, VerilogTokenType.FORCE):
            node.update(keyword = self.get_keyword())
            node.update(assignment = self.assignment())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type in (VerilogTokenType.DEASSIGN, VerilogTokenType.RELEASE):
            node.update(keyword = self.get_keyword())
            node.update(Lvalue = self.lvalue())
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "statement miss match")
        return node
        
    def seq_block(self):
        '''
        <seq_block>
                    ::= begin <statement>* end
                    ||= begin : <name_of_block> <block_declaration>* <statement>* end
        '''
        node = SeqBlock()
        node.update(keyword = self.get_keyword(VerilogTokenType.BEGIN))
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat())
            node.update(name = self.identifier())
            block_declarations = []
            while self.current_token.type in self.verilog_first_set.block_declaration:
                block_declarations.append(self.block_declaration())
            node.update(block_declarations = block_declarations)
        stmts = []
        while self.current_token.type in  self.verilog_first_set.statement:
            stmts.append(self.statement())
        node.update(stmts = stmts)
        node.update(end_keyword = self.get_keyword(VerilogTokenType.END))
        return node
                
    def par_block(self):
        '''
        <par_block>
                    ::= fork <statement>* join
                    ||= fork : <name_of_block> <block_declaration>* <statement>* join
        '''
        node = ParBlock()
        node.update(keyword = self.get_keyword(VerilogTokenType.FORK))
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat())
            node.update(name = self.identifier())
            block_declarations = []
            while self.current_token.type in self.verilog_first_set.block_declaration:
                block_declarations.append(self.block_declaration())
            node.update(block_declarations = block_declarations)
        stmts = []
        while self.current_token.type in  self.verilog_first_set.statement:
            stmts.append(self.statement())
        node.update(stmts = stmts)
        node.update(end_keyword = self.get_keyword(VerilogTokenType.JOIN))
        return node
        
    def block_declaration(self):
        '''
        <block_declaration>
                            ::= <parameter_declaration>
                            ||= <reg_declaration>
                            ||= <integer_declaration>
                            ||= <real_declaration>
                            ||= <time_declaration>
                            ||= <event_declaration>
        '''
        kv_map = {
            VerilogTokenType.PARAMETER: self.parameter_declaration, 
            VerilogTokenType.REG: self.reg_declaration,
            VerilogTokenType.INTEGER: self.integer_declaration,
            VerilogTokenType.REAL: self.real_declaration,
            VerilogTokenType.TIME: self.time_declaration, 
            VerilogTokenType.EVENT: self.event_declaration
        }
        if self.current_token.type in kv_map:
            return kv_map[self.current_token.type]()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "output block declaration kv map")
                
    def task_enable(self):
        '''
        <task_enable>
                        ::= <name_of_task>
                        ||= <name_of_task> ( <expression> <,<expression>>* ) ;
        '''
        node = TaskEnable()
        node.update(name = self.identifier())
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exprs = self.list_items(self.expression))
            node.register_token(self.eat(TokenType.RPAREN))
            node.register_token(self.eat(TokenType.SEMI))
        return node
    
    def system_task_enable(self):
        '''
        <system_task_enable>
                            ::= <name_of_system_task> ;
                            ||= <name_of_system_task> ( <expression> <,<expression>>* ) ;
        <name_of_system_task> ::= $<system_identifier> (Note: the $ may not be followed by a space.)
        '''
        node = SystemTaskEnable()
        node.update(name = self.identifier(VerilogTokenType.SYSTEM_ID))
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exprs = self.list_items(self.expression))
            node.register_token(self.eat(TokenType.LPAREN))
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
        node.update(name=self.identifier())
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
            node.update(name=self.identifier())
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
        node.update(name=self.identifier())
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
            node.update(name=self.identifier())
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
        node.update(name=self.identifier())
        if self.current_token.type == TokenType.HASH:
            node.register_token(self.eat())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(parms=self.list_items(self.expression))
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
        node.update(name=self.identifier())
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
        node.update(name=self.identifier())
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
                            ::= <lvalue> =|<= <expression>
                            ||= <lvalue> = <delay_or_event_control> <expression> ;
        
        @扩展文法: 不好区分阻塞和非阻塞, 所以合并二者
        """
        node = BlockingAssign()
        node.update(lvalue=self.lvalue())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
        elif self.current_token.type == TokenType.LE:
            self.current_token.type = VerilogTokenType.NON_BLOCK_ASSIGN
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be = <=")
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
            node.update(number=self.number())
        elif self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
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
            node.update(id=self.identifier())
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
                            ||= posedge <expression>
                            ||= negedge <expression>
                            ||= <event_expression> or <event_expression>
        """
        node = EventExpression()
        if self.current_token.type in self.verilog_first_set.expression:
            node.update(expr=self.expression())
        elif self.current_token.type in (VerilogTokenType.POSEDGE, VerilogTokenType.NEGEDGE):
            node.update(edge=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expr posedge negedge")

        if self.current_token.type == VerilogTokenType.OR:
            node.register_token(self.eat())
            node.update(event_expr=self.event_expression())
        return node

    def case_item(self):
        '''
        <case_item>
                    ::= <expression> <,<expression>>* : <statement_or_null>
                    ||= default : <statement_or_null>
                    ||= default <statement_or_null>
        '''
        node = CaseItem()
        if self.current_token.type in self.verilog_first_set.expression:
            node.update(exprs = self.list_items(self.expression))
            node.register_token(self.eat(TokenType.COLON))
            node.update(stmt = self.statement_or_null())
        elif self.current_token.type == VerilogTokenType.DEFAULT:
            node.update(keyword = self.get_keyword())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat())
            node.update(stmt = self.statement_or_null())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be expr or default")
        return node