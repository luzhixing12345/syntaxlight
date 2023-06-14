
from ..lexers.lexer import Lexer, Token
from ..error import ParserError, ErrorCode
from enum import Enum

class Parser:
    def __init__(self, lexer, skip_invisible_characters = True, skip_space = True):
        self.lexer: Lexer = lexer
        # set current token to the first token taken from the input
        self.skip_invisible_characters = skip_invisible_characters
        self.skip_space = skip_space
        self.eat(None) # 初始化 current_token, 开头可能会需要跳过空格或不可见字符

    def get_next_token(self):
        return self.lexer.get_next_token()

    def error(self, error_code: ErrorCode, token: Token, message:str = None):
        raise ParserError(
            error_code=error_code,
            token=token,
            context=self.lexer.get_context(token),
            file_path=self.lexer.file_path,
            message=message
        )

    def eat(self, token_type: Enum):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if  token_type is None or self.current_token.type == token_type:
            self.current_token = self.get_next_token()
            if self.skip_invisible_characters:
                while self.current_token.value in self.lexer.invisible_characters:
                    self.current_token = self.get_next_token()
            if self.skip_space:
                while self.current_token.type == self.lexer.TokenType.SPACE:
                    self.current_token = self.get_next_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
                message = f'should match {token_type.value} but got {self.current_token.value}'
            )

    def parse(self):

        raise NotImplementedError
