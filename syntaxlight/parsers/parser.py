
from ..lexers.lexer import Lexer, Token
from ..error import ParserError, ErrorCode
from enum import Enum
from ..ast import AST
from typing import List

class Parser:
    def __init__(self, lexer, skip_invisible_characters = True, skip_space = True):
        self.lexer: Lexer = lexer
        # set current token to the first token taken from the input
        self.skip_invisible_characters = skip_invisible_characters
        self.skip_space = skip_space
        self.token_list:List[Token] = [] # 记录所有 token, 用于后期恢复原始文本
        self.current_token:Token = None
        self.node = None
        self.eat() # 初始化 current_token, 开头可能会需要跳过空格或不可见字符

    def error(self, error_code: ErrorCode, token: Token, message:str = None):
        raise ParserError(
            error_code=error_code,
            token=token,
            context=self.lexer.get_context(token),
            file_path=self.lexer.file_path,
            message=message
        )

    def eat(self, token_type: Enum = None, AST_type: AST = None):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if  token_type is None or self.current_token.type == token_type:
            # assert AST_type is not None, "ast type should not be None"
            self._register_token(AST_type)
            self.current_token = self.lexer.get_next_token()
            self.skip()
        else:
            
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
                message = f'should match {token_type.value} but got {self.current_token.value}'
            )

    def skip(self):

        if self.skip_invisible_characters and self.skip_space:
            while self.current_token.value in self.lexer.invisible_characters or self.current_token.type == self.lexer.TokenType.SPACE:
                self._register_token()
                self.current_token = self.lexer.get_next_token()

        elif self.skip_invisible_characters and not self.skip_space:
            while self.current_token.value in self.lexer.invisible_characters:
                self._register_token()
                self.current_token = self.lexer.get_next_token()
        elif not self.skip_invisible_characters and self.skip_space:
            while self.current_token.type == self.lexer.TokenType.SPACE:
                self._register_token()
                self.current_token = self.lexer.get_next_token()

        

    def _register_token(self, AST_type: AST = None):
        # AST_type == None 对于特殊的字符(空格/换行)
        if self.current_token is None:
            return
        token = self.current_token
        token.ast_type = AST_type
        # print(token)
        self.token_list.append(token)
        
    def to_html(self, node:AST = None):
        
        if node is None:
            node = self.node
        html = ''
        for token in self.token_list:
            html += token.value
        return html

    def parse(self):

        raise NotImplementedError
