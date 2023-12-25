from .parser import Parser
from ..lexers import TokenType, VerilogTokenType, Token, VerilogTokenSet
from ..error import ErrorCode
from ..asts.verilog_ast import *


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
        ports = [self.port()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            ports.append(self.port())
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
            node.update(index_begin=self.constant_expression())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
            node.update(index_end=self.constant_expression())
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
        module_map = {}

    def udp(self):
        """
        <UDP> ::= primitive <name_of_UDP> ( <name_of_variable> <,<name_of_variable>>* ) ; <UDP_declaration>+ <UDP_initial_statement>?   <table_definition> endprimitive
        """
        node = UDP()
        node.update(keyword=self.get_keyword(VerilogTokenType.PRIMITIVE))
        node.update(name=self.identifier())
        node.register_token(self.eat(TokenType.LPAREN))
        variable_names = [self.identifier()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))
            variable_names.append(self.identifier())
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
            elif self.current_token.type == VerilogTokenType.EDGE_SYMBOL:
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
        if self.current_token.type in self.verilog_first_set.statement:
            node.update(stmt=self.statement())
        elif self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be statement or ;")
        node.update(end_keyword=self.get_keyword(VerilogTokenType.ENDTASK))
        return node

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

    def function(self):
        """
        <function> ::= function <range_or_type>? <name_of_function> ; <tf_declaration>+ <statement> endfunction
        
        <range_or_type> ::= <range>
                          | integer
                          | real
        """
        node = Function()
        node.update(keyword=self.get_keyword(VerilogTokenType.FUNCTION))
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.update(range = self.range())
        elif self.current_token.type in (VerilogTokenType.INTEGER, VerilogTokenType.REAL):
            node.update(type = self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be range or type")
            
        node.update(name = self.identifier())
        tf_declarations = [self.tf_declaration()]
        while self.current_token.type in self.verilog_first_set.tf_declaration:
            tf_declarations.append(self.tf_declaration())
        node.update(stmt = self.statement())
        node.update(end_keyword = self.get_keyword(VerilogTokenType.ENDFUNCTION))
        return node
    
    def parameter_declaration(self):
        '''
        <parameter_declaration> ::= parameter <list_of_param_assignments> ;
        
        <list_of_param_assignments> ::=<param_assignment><,<param_assignment>*
        <param_assignment> ::=<identifier> = <constant_expression>
        '''
        node = Parameter()
        node.update(keyword = self.get_keyword(VerilogTokenType.PARAMETER))
        
        param_assignments = [self.param_assignment()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat())
            param_assignments.append(self.param_assignment())
            
        node.register_token(self.eat(TokenType.SEMI))
        return node
        
    def param_assignment(self):
        node = ParameterAssign()
        node.update(key = self.identifier())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(value = self.constant_expression())
        return node
        
    def range(self):
        '''
        
        '''

    def constant_expression(self):
        """ """

    def output_declaration(self):
        """ """

    def reg_declaration(self):
        """ """

    def input_declaration(self):
        """"""

    def statement(self):
        """ """
