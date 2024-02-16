from .parser import Parser
from ..lexers import TokenType, YamlTokenType, Token


class YamlParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.SHL:
                self.current_token.type = YamlTokenType.INHERIT
            if self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = YamlTokenType.MAP
            if self.current_token.type == TokenType.MUL:
                self.current_token.type = YamlTokenType.STAR
                self.eat()
                if self.current_token.type == TokenType.ID:
                    self.current_token.add_css(YamlTokenType.ALIAS)
            if self.current_token.type == TokenType.AMPERSAND:
                if self.peek_next_token().type == TokenType.ID:
                    self.eat()
                    self.current_token.add_css(YamlTokenType.ANCHOR)
            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.COLON:
                    if self.current_token.value in ("http", "https"):
                        new_token = self.current_token
                        self.skip_invis_chars = False
                        self.manual_get_next_token()
                        while self.current_token.type not in (TokenType.EOF, TokenType.LF):
                            new_token.value += self.current_token.value
                            new_token.column = self.current_token.column
                            self.manual_get_next_token()
                        new_token.add_css(YamlTokenType.URL)
                        self.manual_register_token(new_token)
                        self.skip_invis_chars = True

                        continue
                    else:
                        self.current_token.add_css(YamlTokenType.KEY)
            if self.current_token.type == TokenType.NUMBER:
                if self.peek_next_token().type == TokenType.MINUS and self.peek_next_token(2).type == TokenType.NUMBER:
                    new_token = self.current_token
                    self.skip_invis_chars = False
                    self.manual_get_next_token()
                    while self.current_token.type not in (TokenType.EOF, TokenType.LF):
                        new_token.value += self.current_token.value
                        new_token.column = self.current_token.column
                        self.manual_get_next_token()
                    new_token.add_css(YamlTokenType.TIME)
                    self.manual_register_token(new_token)
                    self.skip_invis_chars = True

            if self.current_token.type == TokenType.DOLLAR:
                self.eat()
                if self.current_token.type == TokenType.LCURLY_BRACE:
                    self.eat()
                    if self.current_token.type == TokenType.LCURLY_BRACE:
                        self.eat()
                        if self.current_token.type == TokenType.ID:
                            self.current_token.add_css(YamlTokenType.ENV_VAR)

            self.eat()
