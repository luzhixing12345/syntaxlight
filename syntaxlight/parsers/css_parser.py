from .parser import Parser
from ..lexers import TokenType, CSSTokenType


class CSSParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):
        inside_css_block = False
        brace_number = 0

        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = CSSTokenType.UNDER

            if self.current_token.type == TokenType.LCURLY_BRACE:
                brace_number += 1
                inside_css_block = True
            if self.current_token.type == TokenType.RCURLY_BRACE:
                brace_number -= 1
                if brace_number == 0:
                    inside_css_block = False

            if self.current_token.type == CSSTokenType.COLOR and not inside_css_block:
                self.current_token.type = TokenType.ID

            if self.current_token.type == TokenType.ID:
                next_token_type = self.peek_next_token().type
                if next_token_type == TokenType.COLON:
                    if inside_css_block:
                        self.current_token.type = CSSTokenType.KEY
                    else:
                        self.current_token.type = CSSTokenType.CLASS_NAME
                elif next_token_type == TokenType.LPAREN:
                    self.current_token.type = CSSTokenType.FUNCTION
                elif not inside_css_block:
                    self.current_token.type = CSSTokenType.CLASS_NAME
            self.eat()
