from .parser import Parser
from ..lexers import TokenType
from ..error import ErrorCode
from ..ast import String, AST, Identifier, Expression, NodeVisitor, Punctuator, add_ast_type
from enum import Enum

class BNF_CSS(Enum):
    BUILTIN_SYMBOL = "BuiltinSymbol"


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
        self.op = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        node_visitor.link(self, self.op)
        return super().visit(node_visitor)


class Term(AST):
    def __init__(self) -> None:
        super().__init__()
        self.exprs = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.exprs)
        return super().visit(node_visitor)


class GroupTerm(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.op = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.op)
        return super().visit(node_visitor)


class Item(AST):
    def __init__(self) -> None:
        super().__init__()
        self.value = None
        self.op = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.value)
        node_visitor.link(self, self.op)
        return super().visit(node_visitor)


class BNFParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=False, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.punctuator_first_set = [TokenType.PLUS, TokenType.MUL, TokenType.QUSTION]
        self.term_first_set = [
            TokenType.STR,
            TokenType.LANGLE_BRACE,
            TokenType.LPAREN,
            TokenType.LCURLY_BRACE,
            TokenType.ID,
        ]

    def parse(self):
        self.skip_crlf()
        self.root = self.syntax()
        if self.current_token.type != TokenType.EOF:  # pragma: no cover
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.root

    def syntax(self):
        """
        <syntax>     ::= <rule>+
        """
        node = Syntax()
        rules = []
        while self.current_token.type == TokenType.LANGLE_BRACE:
            rules.append(self.rule())
        node.update(rules=rules)
        return node

    def rule(self):
        """
        <rule>       ::= <rule-name> "::="  <expression>
        """
        node = Rule()
        node.update(rule_name=self.rule_name())
        node.register_token(self.eat(TokenType.PRODUCTION_SYMBOL))
        node.update(expr=self.expression())
        return node

    def rule_name(self):
        """
        <rule-name> ::= "<" <ID> ">" <punctuator>?
        """
        node = RuleName()
        node.register_token(self.eat(TokenType.LANGLE_BRACE))
        node.update(id=self.identifer())
        node.register_token(self.eat(TokenType.RANGLE_BRACE))
        if self.current_token.type in self.punctuator_first_set:
            node.update(op=self.punctuator())
        return node

    def expression(self):
        """
        <expression> ::= <term> ("|" <term>)*
        """
        node = Expression()
        exprs = [self.term()]
        while self.current_token.type == TokenType.PIPE:
            node.register_token(self.eat(TokenType.PIPE))
            exprs.append(self.term())
        node.update(exprs=exprs)
        return node

    def term(self):
        """
        <term>  ::= (<item> | <rule-name> | <group-term>)* <CRLF>?
        """
        node = Term()
        exprs = []
        while self.current_token.type in self.term_first_set:
            if self.current_token.type in (TokenType.STR, TokenType.ID):
                exprs.append(self.item())
            elif self.current_token.type == TokenType.LANGLE_BRACE:
                exprs.append(self.rule_name())
            else:
                exprs.append(self.group_term())
        node.update(exprs=exprs)
        if self.current_token.type == TokenType.LF:
            self.eat_lf()
        return node

    def item(self):
        """
        <item> ::= (<STR> | <ID>) <punctuator>?
        """
        node = Item()
        if self.current_token.type == TokenType.STR:
            node.update(value=self.string())
        elif self.current_token.type == TokenType.ID:
            node.update(value=self.identifer())
        else:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be str or id")
        if self.current_token.type in self.punctuator_first_set:
            node.update(op=self.punctuator())
        return node

    def group_term(self):
        """
        <group-term> ::= "(" <expression> ")" <punctuator>?
                       | "{" <expression> "}" <punctuator>?
        """
        node = GroupTerm()
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            # TokenType.LCURLY_BRACE
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

        if self.current_token.type in self.punctuator_first_set:
            node.update(op=self.punctuator())
        return node

    def punctuator(self):
        """
        <punctuator> ::= '+' | '*' | '?'
        """
        node = Punctuator(self.current_token.value)
        node.register_token(self.eat())
        return node

    def string(self):
        node = String(self.current_token.value)
        node.register_token(self.eat(TokenType.STR))
        return node

    def identifer(self):
        node = Identifier(self.current_token.value)
        node.register_token(self.eat(TokenType.ID))
        if node.id.isupper():
            add_ast_type(node, BNF_CSS.BUILTIN_SYMBOL)
        return node
