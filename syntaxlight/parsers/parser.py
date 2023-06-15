from ..lexers.lexer import Lexer, Token, TokenType
from ..error import ParserError, ErrorCode
from enum import Enum
from .ast import AST, NodeVisitor
from typing import List


class Parser:
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        self.lexer: Lexer = lexer
        # set current token to the first token taken from the input
        self.skip_invisible_characters = skip_invisible_characters
        self.skip_space = skip_space
        self.token_list: List[Token] = []
        self.node = None
        self.current_token: Token = self.lexer.get_next_token()
        self.skip()

    def error(self, error_code: ErrorCode, token: Token, message: str = ""):
        raise ParserError(
            error_code=error_code,
            token=token,
            context=self.lexer.get_context(token),
            file_path=self.lexer.file_path,
            message=message,
        )

    def eat(self, token_type: Enum):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        token = self.current_token
        if self.current_token.type == token_type:
            self._register_token()
            self.current_token = self.lexer.get_next_token()
            self.skip()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
                message=f"should match {token_type.value} but got {self.current_token.value}",
            )
        return token

    def skip(self):
        if self.skip_invisible_characters and self.skip_space:
            while (
                self.current_token.value in self.lexer.invisible_characters
                or self.current_token.type == TokenType.SPACE
            ):
                self._register_token()
                self.current_token = self.lexer.get_next_token()

        elif self.skip_invisible_characters and not self.skip_space:
            while self.current_token.value in self.lexer.invisible_characters:
                self._register_token()
                self.current_token = self.lexer.get_next_token()
        elif not self.skip_invisible_characters and self.skip_space:
            while self.current_token.type == TokenType.SPACE:
                self._register_token()
                self.current_token = self.lexer.get_next_token()

    def _register_token(self):
        if self.current_token is None:
            return
        token = self.current_token
        # print(token)
        self.token_list.append(token)

    def to_html(self, node: AST = None):
        if node is None:
            node = self.node

        node_visitor = NodeVisitor()
        node.visit(node_visitor)
        assert node_visitor.depth == -1
        html = ""

        for token in self.token_list:
            html += f'<span class="{token.get_css_class()}">{token.value}</span>'
        return html

    def parse(self):
        raise NotImplementedError
