
from ..lexers.lexer import Lexer, Token
from ..error import *

class Parser:
    def __init__(self, lexer):
        self.lexer:Lexer = lexer
        # set current token to the first token taken from the input
        self.current_token:Token = self.get_next_token()
        
    def get_next_token(self):
        return self.lexer.get_next_token()

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

    def parse(self):

        raise NotImplementedError