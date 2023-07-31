from .parser import Parser
from ..lexers import TokenType, CSSTokenType


class CSSParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.ID:
                next_token_type = self.peek_next_token().type
                if next_token_type == TokenType.COLON:
                    self.current_token.type = CSSTokenType.KEY
                elif next_token_type in (TokenType.LCURLY_BRACE, TokenType.ID, TokenType.COMMA):
                    self.current_token.type = CSSTokenType.CLASS_NAME
                elif next_token_type == TokenType.LPAREN:
                    self.current_token.type = CSSTokenType.FUNCTION
            self.eat()
