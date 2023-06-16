from ..lexers.lexer import Lexer, Token, TokenType
from ..error import ParserError, ErrorCode
from enum import Enum
from ..ast import AST, NodeVisitor
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
        if message == "":
            if token.value in self.lexer.invisible_characters:
                message = token.type.name
            else:    
                message = token.value
        raise ParserError(
            error_code=error_code,
            token=token,
            context=self.lexer.get_context(token),
            file_path=self.lexer.file_path,
            message=message,
        )

    def eat(self, token_type: Enum) -> List[Token]:
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        tokens = [self.current_token]
        if self.current_token.type == token_type:
            self._register_token()
            self.current_token = self.lexer.get_next_token()
            tokens.extend(self.skip())
        else:
            current_value = self.current_token.value
            expected_value = token_type.value
            if current_value in self.lexer.invisible_characters:
                current_value = self.current_token.type.name
            if expected_value in self.lexer.invisible_characters:
                expected_value = token_type.name
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
                message=f"should match {expected_value} but got {current_value}",
            )
        return tokens

    def skip(self):
        tokens = []
        if self.skip_invisible_characters and self.skip_space:
            while (
                self.current_token.value in self.lexer.invisible_characters
                or self.current_token.type == TokenType.SPACE
            ):
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()

        elif self.skip_invisible_characters and not self.skip_space:
            while self.current_token.value in self.lexer.invisible_characters:
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()
        elif not self.skip_invisible_characters and self.skip_space:
            while self.current_token.type == TokenType.SPACE:
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()

        return tokens

    def skip_crlf(self):
        '''
        set `skip_invisible_characters` to False \n
        skip `\\n` or `\\r\\n`
        '''
        while self.current_token.type in (TokenType.LF, TokenType.CR):
            self.eat(self.current_token.type)

    def skip_comment(self, end_token_type: Enum) -> str:

        result = ''
        while self.current_token.type != end_token_type and self.current_token != TokenType.EOF:
            result += self.current_token.value
            self.current_token = self.lexer.get_next_token()
        
        return result

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
    
    def type_hint(self, array: List[Enum]):

        result = ''
        for i in array:
            result += ' ' + i.value
        return result

    def parse(self):
        raise NotImplementedError
