from .parser import Parser
from ..lexers import TokenType, DotTokenType, DotTokenSet
from ..gdt import *
from ..error import ErrorCode
from ..asts.ast import add_ast_type, Identifier
from ..asts.dot_ast import *


class DotCSS(Enum):
    ATTRIBUTE_KEY = "AttributeKey"
    ATTRIBUTE_VALUE = "AttributeValue"


class DotParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.first_set = DotTokenSet()

    def parse(self):
        self.root = self.graph()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        # print(self.node)
        return self.root

    def graph(self):
        """
        <graph> ::= strict? (graph | digraph) <ID>? '{' <stmt_list>? '}'
        """
        node = Graph()
        if self.current_token.type == DotTokenType.STRICT:
            node.update(strict=self.get_keyword(DotTokenType.STRICT))
        if self.current_token.type in (DotTokenType.GRAPH, DotTokenType.DIGRAPH):
            node.update(graph=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be graph or digraph")

        if self.current_token.type == TokenType.ID:
            node.update(name=self.get_identifier())

        node.register_token(self.eat(token_type=TokenType.LCURLY_BRACE))
        if self.current_token.type in self.first_set.stmt_list:
            node.update(stmt_list=self.stmt_list())
        node.register_token(self.eat(token_type=TokenType.RCURLY_BRACE))
        return node

    def stmt_list(self):
        """
        <stmt_list> ::= <stmt> (';' <stmt>)* ';'?
        """
        result = [self.stmt()]

        while self.current_token.type in (TokenType.SEMI, self.first_set.stmt):
            if self.current_token.type == TokenType.SEMI:
                self.eat(token_type=TokenType.SEMI)
                if self.current_token.type not in self.first_set.stmt:
                    break
                else:
                    result.append(self.stmt())
            else:
                result.append(self.stmt())

        return result

    def stmt(self):
        """
        <stmt> ::= <node_stmt>
                 | <edge_stmt>
                 | <attr_stmt>
                 | <ID> '=' <ID>
                 | <subgraph>
        """
        node = Stmt()
        if self.current_token.type == TokenType.ID:
            # <ID> '=' <ID>
            if self.peek_next_token().type == TokenType.ASSIGN:
                node.update(key=self.get_identifier())
                node.register_token(self.eat(TokenType.ASSIGN))
                node.update(value=self.get_identifier())
                add_ast_type(node.key, DotCSS.ATTRIBUTE_KEY)
                add_ast_type(node.value, DotCSS.ATTRIBUTE_VALUE)
            # node_stmt 和 edge_stmt 有重叠部分, 需要判断

            # <stmt> ::= <node_stmt>
            # <node_stmt> ::= <node_id> <attr_list>?
            # ----------------------------------------
            # <stmt> ::= <edge_stmt>
            # <edge_stmt> ::= (<node_id> | <subgraph>) <edgeRHS> <attr_list>?
            else:
                sub_node = self.node_id()
                if self.current_token.type in self.first_set.edgeop:
                    node.update(edge_stmt=self.edge_stmt(sub_node))
                else:
                    node.update(node_stmt=self.node_stmt(sub_node))

        elif self.current_token.type == self.first_set.attr_stmt:
            node.update(attr_stmt=self.attr_stmt())

        elif self.current_token.type in self.first_set.subgraph:
            # edge_stmt 和 subgraph 有重叠部分

            # <stmt> ::= <edge_stmt>
            # <edge_stmt> ::= (<node_id> | <subgraph>) <edgeRHS> <attr_list>?
            # ----------------------
            # <stmt> ::=<subgraph>
            sub_node = self.subgraph()
            if self.current_token.type in self.first_set.edgeop:
                node.update(edge_stmt=self.edge_stmt(sub_node))
            else:
                node = sub_node

        return node

    def attr_stmt(self):
        """
        <attr_stmt> ::= ( graph | node | edge) <attr_list>
        """
        node = AttrStmt()
        node.update(keyword=self.get_keyword())
        node.update(attr_list=self.attr_list())
        return node

    def attr_list(self):
        """
        <attr_list> ::= '[' <a_list>? ']' <attr_list>?
        """
        result = []
        while self.current_token.type == TokenType.LSQUAR_PAREN:
            self.eat(TokenType.LSQUAR_PAREN)
            if self.current_token.type == TokenType.ID:
                result.append(self.a_list())
            self.eat(TokenType.RSQUAR_PAREN)
        return result

    def a_list(self):
        """
        <a_list> ::= <ID> '=' <ID> (';' | ',')? <a_list>?
        """
        node = Attribute()
        keys = []
        values = []
        while self.current_token.type == TokenType.ID:
            keys.append(self.get_identifier())
            node.register_token(self.eat(TokenType.ASSIGN))
            values.append(self.get_identifier())
            if self.current_token.type in (TokenType.SEMI, TokenType.COMMA):
                node.register_token(self.eat())

        node.update(keys=keys)
        node.update(values=values)
        add_ast_type(node.keys, DotCSS.ATTRIBUTE_KEY)
        add_ast_type(node.values, DotCSS.ATTRIBUTE_VALUE)
        return node

    def edge_stmt(self, sub_node):
        """
        <edge_stmt> ::= (<node_id> | <subgraph>) <edgeRHS> <attr_list>?
        """
        node = EdgeStmt()
        if isinstance(sub_node, NodeId):
            node.update(node_id=sub_node)
        else:
            # SubGraph
            node.update(subgraph=sub_node)
        node.update(edgeRHS=self.edgeRHS())
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.update(attr_list=self.attr_list())
        return node

    def edgeRHS(self):
        """
        <edgeRHS> ::= <edgeop> (<node_id> | <subgraph>) <edgeRHS>?

        <edgeop> ::= "->" | "--"
        """
        result = []
        while self.current_token.type in self.first_set.edgeop:
            node = EdgeRHS()
            node.register_token(self.eat())
            if self.current_token.type == TokenType.ID:
                node.update(node_id=self.node_id())
            else:
                node.update(subgraph=self.subgraph())
            result.append(node)
        return result

    def node_stmt(self, sub_node):
        """
        <node_stmt> ::= <node_id> <attr_list>?
        """
        node = NodeStmt()
        node.update(node_id=sub_node)
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.update(attr_list=self.attr_list())
        return node

    def node_id(self):
        """
        <node_id> ::= <ID> <port>?
        """
        node = NodeId()
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.COLON:
            node.update(port=self.port())
        return node

    def port(self):
        """
        <port> ::= ':' <ID> (':' <compass_pt>)?
                 | ':' <compass_pt>
        """
        node = Port()
        node.register_token(self.eat(TokenType.COLON))
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(compass_pt=self.get_identifier())
        return node

    def subgraph(self):
        """
        <subgraph> ::= (subgraph <ID>? )? '{' <stmt_list> '}'
        """
        node = SubGraph()
        if self.current_token.type == DotTokenType.SUBGRAPH:
            node.update(keyword=self.get_keyword())
            if self.current_token.type == TokenType.ID:
                node.update(id=self.get_identifier())
        node.register_token(self.eat(token_type=TokenType.LCURLY_BRACE))
        node.update(stmt_list=self.stmt_list())
        node.register_token(self.eat(token_type=TokenType.RCURLY_BRACE))
        return node

    def compass_pt(self):
        """
        <compass_pt> ::= (n | ne | e | se | s | sw | w | nw | c | _)
        """

    def get_identifier(self):
        if self.current_token.type == TokenType.ID:
            node = Identifier(self.current_token.value)
            node.register_token(self.eat(TokenType.ID))
            return node
        elif self.current_token.type == TokenType.STRING:
            return self.get_string()
        elif self.current_token.type == TokenType.NUMBER:
            return self.get_number()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id")
