from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, TomlTokenType, Token
from ..error import ErrorCode
from ..ast import (
    AST,
    NodeVisitor,
    Object,
    Array,
    String,
    Number,
    Keyword,
    Expression,
    UnaryOp,
)

from typing import List


class Toml(AST):
    def __init__(self, expressions=None) -> None:
        super().__init__()
        self.expressions: List[AST] = expressions
        self.graph_node_info = f"expression = {len(self.expressions)}"

    def visit(self, node_visitor: NodeVisitor = None):
        for expression in self.expressions:
            node_visitor.link(self, expression)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        result = ""
        for expression in self.expressions:
            result += expression.formatter(depth + 1)
        return result


class Pair(AST):
    def __init__(self, path: "Path", value: AST = None) -> None:
        super().__init__()
        self.path: Path = path
        self.value: AST = value

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.value)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        return f"{self.path.formatter(depth+1)} = {self.value.formatter(depth+1)}"


class Path(AST):
    def __init__(self, path: str = None) -> None:
        super().__init__()
        self.path = path

    def formatter(self, depth: int = 0):
        return self.path


class Table(AST):
    def __init__(self, header: AST = None, entries: AST = None) -> None:
        super().__init__()
        # table_header or table_array_header
        self.header: AST = header
        self.entries = entries

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.header)
        node_visitor.link(self, self.entries)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        header_formatter = self.header.formatter(depth + 1)
        entries_formatter = self.entries.formatter(depth + 1)
        return f"{header_formatter}{entries_formatter}"


class TableHeader(AST):
    def __init__(self, path: AST = None) -> None:
        super().__init__()
        self.path = path

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.path)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0):
        return f"[{self.path.formatter(depth+1)}]"


class TableArrayHeader(AST):
    def __init__(self, path: AST = None) -> None:
        super().__init__()
        self.path = path

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.path)
        return super().visit(node_visitor)

    def formatter(self, depth):
        return f"[[{self.path.formatter(depth+1)}]]"


class TableEntry(AST):
    def __init__(self, pairs: List[Pair]) -> None:
        super().__init__()
        self.pairs = pairs

    def visit(self, node_visitor: NodeVisitor = None):
        # print(self.pairs,'!')
        for pair in self.pairs:
            node_visitor.link(self, pair)
        return super().visit(node_visitor)

    def formatter(self, depth):
        result = ""
        for pair in self.pairs:
            result += pair.formatter(depth + 1) + "\n"

        return result[:-1]


class TomlParser(Parser):
    """
    TOML do not skip invisible character `\\r\\n`
    """

    def __init__(self, lexer, skip_invisible_characters=False, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)
        self.value_first_set = [
            TokenType.STR,
            TokenType.MINUS,
            TokenType.PLUS,
            TokenType.NUMBER,
            TomlTokenType.DATE,
            TomlTokenType.TRUE,
            TomlTokenType.FALSE,
            TokenType.LSQUAR_PAREN,
            TokenType.LCURLY_BRACE,
        ]
        self.path_first_set = [TokenType.ID, TokenType.STR]

    def parse(self):
        self.root = self.toml()
        if self.current_token.type != TokenType.EOF:
            self.error(ErrorCode.UNEXPECTED_TOKEN)
        # print(self.node)
        return self.root

    def toml(self):
        """
        <toml> ::= <expression> ( <CRLF> expression )*
        """
        expressions = []
        self.skip_crlf()
        while self.current_token.type in [
            TokenType.STR,  # "key" - value
            TokenType.ID,  # key - value
            TokenType.LSQUAR_PAREN,  # [] | [[]]
        ]:
            expressions.append(self.expression())

        return Toml(expressions)

    def expression(self):
        """
        <expression> ::= (<pair> | <table>)?
        """
        exprs = []
        if self.current_token.type in (TokenType.ID, TokenType.STR):
            exprs.append(self.pair())
            self.eat_lf()
            self.skip_crlf()
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            exprs.append(self.table())

        return Expression(exprs)

    def pair(self) -> Pair:
        """
        <pair> ::= <path> '=' <value>
        """
        path = self.path()
        node = Pair(path)
        node.register_token(self.eat(TokenType.ASSIGN))
        value = self.value()
        node.update(value=value)
        return node

    def path(self):
        """
        <path> ::= (<ID> | <STRING>) ( '.' (<ID> | <STRING>)) *
        """
        if self.current_token.type not in self.path_first_set:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be ID or str")

        node = Path()
        path = self.current_token.value
        node.register_token(self.eat(self.current_token.type))
        while self.current_token.type == TokenType.DOT:
            path += TokenType.DOT.value
            node.register_token(self.eat(TokenType.DOT))
            if self.current_token.type not in self.path_first_set:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "should be ID or str")
            path += self.current_token.value
            node.register_token(self.eat(self.current_token.type))

        node.update(path=path)
        return node

    def table(self):
        """
        <table> ::= <table_header>       <CRLF> <table_entry>
                  | <table_array_header> <CRLF> <table_entry>

        <table_header>       ::=  '['     <path>     ']'
        <table_array_header> ::=  '[' '[' <path> ']' ']'
        """
        node = Table()
        token = self.eat(TokenType.LSQUAR_PAREN)
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            # [[ ... ]]
            table_array_header = TableArrayHeader()
            table_array_header.register_token(token)  # [
            table_array_header.register_token(self.eat(TokenType.LSQUAR_PAREN))  # [
            path = self.path()
            table_array_header.update(path=path)
            table_array_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]
            table_array_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]

            node.header = table_array_header

        else:
            # [ ... ]
            table_header = TableHeader()
            table_header.register_token(token)  # [
            path = self.path()
            table_header.update(path=path)
            table_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]

            node.header = table_header

        self.eat_lf()
        entries = self.table_entry()
        node.update(entries=entries)
        return node

    def table_entry(self):
        """
        <table_entry> ::= (<pair>)? ( <CRLF> <pair> )*
        """
        pairs = []
        accepted_token_types = [TokenType.ID, TokenType.STR]
        while self.current_token.type in accepted_token_types:
            pairs.append(self.pair())
            self.eat_lf()
            self.skip_crlf()

        return TableEntry(pairs)

    def value(self):
        """
        <value> ::= <STRING> | <NUMBER> | <DATE> | true | false | <array> | <inline_table>
        """

        if self.current_token.type not in self.value_first_set:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                f"should be a value",
            )

        if self.current_token.type == TokenType.STR:
            node = String(self.current_token.value)
            node.register_token(self.eat(TokenType.STR))

        elif self.current_token.type == TokenType.NUMBER:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TokenType.NUMBER))

        elif self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            node = UnaryOp(op=self.current_token.value)
            node.register_token(self.eat(self.current_token.type))
            if self.current_token.type == TokenType.NUMBER:
                number = Number(self.current_token.value)
                number.register_token(self.eat(TokenType.NUMBER))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, f"should match number")
            node.update(expr=number)

        elif self.current_token.type == TomlTokenType.DATE:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TomlTokenType.DATE), "Date")

        elif self.current_token.type in (TomlTokenType.TRUE, TomlTokenType.FALSE):
            node = Keyword(self.current_token.value)
            node.register_token(self.eat(self.current_token.type))

        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node = self.array()

        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node = self.inline_table()

        else:  # pragma: no cover
            # should never reach here
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                f"should be a value",
            )
        return node

    def array(self):
        """
        <array> ::= '[' ( <value> (',' <value> )* ','?)? ']'
        """

        node = Array()
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        self.skip_crlf()
        elements: List[AST] = []
        while self.current_token.type in self.value_first_set:
            elements.append(self.value())
            self.skip_crlf()
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                self.skip_crlf()
            elif self.current_token.type in self.value_first_set:
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, TokenType.COMMA.value)

        node.update(elements=elements)
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def inline_table(self):
        """
        <inline_table> ::= '{' ( <pair> (',' <pair>)* ','?)? '}'
        """

        node = Object()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))

        pairs = []
        while self.current_token.type in self.path_first_set:
            pairs.append(self.pair())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
            elif self.current_token.type in self.path_first_set:
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, TokenType.COMMA.value)

        node.update(pairs=pairs)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node
