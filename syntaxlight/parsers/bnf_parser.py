
from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType
from ..error import ErrorCode
from ..ast import String, AST, Identifier, Expression, NodeVisitor


class Syntax(AST):
    def __init__(self) -> None:
        super().__init__()
        self.rules = None
    
    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.rules)
        return super().visit(node_visitor)

class Rule(AST):
    def __init__(self) -> None:
        super().__init__()
        self.rule_name = None
        self.expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.rule_name)
        node_visitor.link(self, self.expr)
        return super().visit(node_visitor)
    
class RuleName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        return super().visit(node_visitor)

class ExprList(AST):
    def __init__(self) -> None:
        super().__init__()
        self.exprs = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.exprs)
        return super().visit(node_visitor)


class BNFParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=False, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)


    def parse(self):
        self.node = self.syntax()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.node

    def syntax(self):
        '''
        <syntax>     ::= <rule>+
        '''
        node = Syntax()
        rules = []
        while self.current_token.type == TokenType.LANGLE_BRACE:
            rules.append(self.rule())
        node.update(rules = rules)
        return node

    def rule(self):
        '''
        <rule>       ::= <rule-name> "::="  <expression> <CRLF> 
        '''
        node = Rule()
        node.pass_total = True
        node.update(rule_name = self.rule_name())
        node.register_token(self.eat(TokenType.PRODUCTION_SYMBOL))
        node.update(expr = self.expression())
        self.eat_lf()
        return node
    
    def rule_name(self):
        '''
        <rule-name> ::= "<" <ID> ">" 
        '''
        node = RuleName()
        node.register_token(self.eat(TokenType.LANGLE_BRACE))
        node.update(id = self.identifier())
        node.register_token(self.eat(TokenType.RANGLE_BRACE))
        return node

    def expression(self):
        '''
        <expression> ::= <expr-list> ("|" <expr-list>)*
        '''
        node = Expression()
        exprs = [self.expr_list()]
        while self.current_token.type == TokenType.PIPE:
            node.register_token(self.eat(TokenType.PIPE))
            exprs.append(self.expr_list())
        node.update(exprs = exprs)
        return node

    def expr_list(self):
        '''
        <expr-list>  ::= (<string> | <rule-name>)*
        '''
        node = ExprList()
        exprs = []
        while self.current_token.type in (TokenType.STR, TokenType.LANGLE_BRACE):
            if self.current_token.type == TokenType.STR:
                exprs.append(self.string())
            else:
                exprs.append(self.rule_name())
        node.update(exprs = exprs)
        return node

    def identifier(self):

        node = Identifier(self.current_token.value)
        node.register_token(self.eat())
        return node

    def string(self):
        
        node = String(self.current_token.value)
        node.register_token(self.eat(TokenType.STR))
        return node
        