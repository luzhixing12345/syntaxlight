from .parser import Parser
from ..lexers import EBNFLexer, EBNFTokenType, EBNFErrorCode
from ..lexers import TokenType


class EBNFParser(Parser):
    def __init__(self, lexer):
        super().__init__(lexer)

    def parse(self):
        node = self.grammar()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=EBNFErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )
        return node

    def S(self):
        if self.current_token.type in self.lexer.invisible_characters:
            self.eat(self.current_token.type)
        else:
            self.error(EBNFErrorCode.UNEXPECTED_TOKEN, self.current_token)

    def grammar(self):
        self.eat(TokenType.LPAREN)
        self.S()
        self.eat(TokenType.COMMA)
        node = self.rule()
        self.eat(TokenType.COMMA)
        self.S()
        self.eat(TokenType.RPAREN)

    def rule(self):
        ...
