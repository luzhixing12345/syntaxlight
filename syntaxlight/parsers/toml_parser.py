from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, TomlTokenType, Token
from ..error import ErrorCode
from ..ast import AST, NodeVisitor, Object, Array, String, Number, Keyword, Comment, Expression

from typing import List


class Toml(AST):
    def __init__(self, expressions=None) -> None:
        super().__init__()
        self.expressions: List[AST] = expressions
        self.graph_node_info = f"expression = {len(self.expressions)}"

    def visit(self, node_visitor: NodeVisitor = None, brace=False):
        for expression in self.expressions:
            node_visitor.link(self, expression)
        return super().visit(node_visitor, brace)

    def format(self, depth: int = 0):
        result = ''
        for expression in self.expressions:
            result += expression.format(depth+1)
        return result


class Pair(AST):
    def __init__(self, path: "Path", value: AST = None) -> None:
        super().__init__()
        self.path: Path = path
        self.value: AST = value

    def update(self, **kwargs):
        self.value: AST = kwargs["value"]
        self.graph_node_info = f"{self.path}:{self.value.class_name}"

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.value)
        return super().visit(node_visitor)

    def format(self, depth: int = 0):
        return f"{self.path.format(depth+1)} = {self.value.format(depth+1)}"


class Path(AST):
    def __init__(self, path: str = None) -> None:
        super().__init__()
        self.path = path

    def update(self, **kwargs):
        self.path = kwargs["path"]
        self.graph_node_info = f"path = {self.path}"

    def format(self, depth: int = 0):
        return self.path


class Table(AST):
    def __init__(self, header: AST = None, entries: AST = None) -> None:
        super().__init__()
        # table_header or table_array_header
        self.header: AST = header
        self.entries = entries

    def visit(self, node_visitor: NodeVisitor = None, brace=False):
        node_visitor.link(self, self.header)
        node_visitor.link(self, self.entries)
        return super().visit(node_visitor, brace)

    def update(self, **kwargs):
        self.entries = kwargs["entries"]
        self.graph_node_info = f"{self.header.class_name} : entries"

    def format(self, depth: int = 0):
        return f'{self.header.format(depth+1)}{self.entries.format(depth+1)}'


class TableHeader(AST):
    def __init__(self, path: AST = None) -> None:
        super().__init__()
        self.path = path

    def visit(self, node_visitor: NodeVisitor = None, brace=False):
        for token in self._tokens:
            token.brace_depth = 0
        node_visitor.link(self, self.path)
        return super().visit(node_visitor, brace=brace)

    def update(self, **kwargs):
        self.path = kwargs["path"]
        self.graph_node_info = "path"

    def format(self, depth):
        return f'[{self.path.format(depth+1)}]'


class TableArrayHeader(AST):
    def __init__(self, path: AST = None) -> None:
        super().__init__()
        self.path = path

    def visit(self, node_visitor: NodeVisitor = None, brace=False):
        
        square_paren_tokens:List[Token] = []
        for token in self._tokens:
            if token.type in (TokenType.LSQUAR_PAREN, TokenType.RSQUAR_PAREN):
                square_paren_tokens.append(token)

        square_paren_tokens[0].brace_depth = 0
        square_paren_tokens[1].brace_depth = 1
        square_paren_tokens[2].brace_depth = 1
        square_paren_tokens[3].brace_depth = 0

        node_visitor.link(self, self.path)
        return super().visit(node_visitor, brace)

    def update(self, **kwargs):
        self.path = kwargs["path"]
        self.graph_node_info = "path"

    def format(self, depth):
        return f'[[{self.path.format(depth+1)}]]'


class TableEntry(AST):
    def __init__(self, pairs: List[Pair]) -> None:
        super().__init__()
        self.pairs = pairs
        self.graph_node_info = f"paris = {len(self.pairs)}"

    def visit(self, node_visitor: NodeVisitor = None, brace=False):
        for pair in self.pairs:
            node_visitor.link(self, pair)
        return super().visit(node_visitor, brace)
    
    def format(self, depth):

        result = ''
        for pair in self.pairs:
            result += pair.format(depth+1) + '\n'

        return result[:-1]

class Date(AST):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.graph_node_info = self.value

    def format(self, depth: int = 0):
        return self.value


class TomlParser(Parser):
    """
    TOML do not skip invisible character `\\r\\n`
    """

    def __init__(self, lexer, skip_invisible_characters=False, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)
        self.value_first_set = [
            TokenType.STR,
            TokenType.NUMBER,
            TomlTokenType.DATE,
            TomlTokenType.TRUE,
            TomlTokenType.FALSE,
            TokenType.LSQUAR_PAREN,
            TokenType.LCURLY_BRACE,
        ]
        self.path_first_set = [TokenType.ID, TokenType.STR]

    def parse(self):
        self.node = self.toml()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        # print(self.node)
        return self.node

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
            TokenType.HASH,  # comment
        ]:
            expressions.append(self.expression())
            self.skip_cr()
            if self.current_token.type != TokenType.EOF:
                self.eat(TokenType.LF)
            self.skip_crlf()
        
        return Toml(expressions)

    def expression(self):
        """
        <expression> ::= (<pair> | <table>)? (<comment>)?
        """
        node = None
        comment = None
        if self.current_token.type in (TokenType.ID, TokenType.STR):
            node = self.pair()
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node = self.table()
        
        if self.current_token.type == TokenType.HASH:
            comment = Comment(self.current_token.value)
            comment.register_token(self.eat(TokenType.HASH))
            comment.update(comment = self.current_token.value)
            comment.register_token(self.eat(TokenType.COMMENT))
        
        return Expression(node, comment)
        

    def pair(self):
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
        <path> ::= (<ID> | <str>) ('.' (<ID> | <str>)) *
        """
        if self.current_token.type not in self.path_first_set:
            self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token, "should be ID or str")

        node = Path()
        path = self.current_token.value
        node.register_token(self.eat(self.current_token.type))
        while self.current_token.type == TokenType.DOT:
            path += TokenType.DOT.value
            node.register_token(self.eat(TokenType.DOT))
            if self.current_token.type not in self.path_first_set:
                self.error(ErrorCode.UNEXPECTED_TOKEN, self.current_token, "should be ID or str")
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
            path.add_ast_type(table_array_header.class_name)
            table_array_header.update(path=path)
            table_array_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]
            table_array_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]

            node.header = table_array_header

        else:
            # [ ... ]
            table_header = TableHeader()
            table_header.register_token(token)  # [
            path = self.path()
            path.add_ast_type(table_header.class_name)
            table_header.update(path=path)
            table_header.register_token(self.eat(TokenType.RSQUAR_PAREN))  # ]

            node.header = table_header

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
            self.skip_crlf()

        return TableEntry(pairs)

    def value(self):
        """
        <value> ::= <str> | <number> | <date> | 'true' | 'false' | <array> | <inline_table>
        """

        if self.current_token.type not in self.value_first_set:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                self.current_token,
                f"should be {self.type_hint(self.value_first_set)}",
            )

        if self.current_token.type == TokenType.STR:
            node = String(self.current_token.value)
            node.register_token(self.eat(TokenType.STR))

        elif self.current_token.type == TokenType.NUMBER:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TokenType.NUMBER))
        
        elif self.current_token.type == TomlTokenType.DATE:
            node = Date(self.current_token.value)
            node.register_token(self.eat(TomlTokenType.DATE))

        elif self.current_token.type in (TomlTokenType.TRUE, TomlTokenType.FALSE):
            node = Keyword(self.current_token.value)
            node.register_token(self.eat(self.current_token.type))

        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node = self.array()

        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node = self.inline_table()

        else:
            # should never reach here
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                self.current_token,
                f"should be {self.type_hint(self.value_first_set)}",
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
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, self.current_token, TokenType.COMMA.value)

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
                self.error(ErrorCode.MISS_EXPECTED_TOKEN, self.current_token, TokenType.COMMA.value)

        node.update(pairs=pairs)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node
