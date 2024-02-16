from .parser import Parser
from . import ShellCSS
from ..lexers import TokenType, MakefileTokenType
from enum import Enum
import re


class MakefileCSS(Enum):
    VARIABLE = "Variable"
    KEYWORD = "Keyword"
    MISSION = "Mission"
    FUNCTION = "Function"


class MakefileParser(Parser):
    def __init__(self, lexer, skip_invis_chars=False, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):
        while self.current_token.type != TokenType.EOF:
            if self.current_token.value in self.lexer.reserved_keywords:
                if self.current_token.type == MakefileTokenType.INCLUDE:
                    if len(self._token_list) == 0 or self._token_list[-1].type == TokenType.LF:
                        self.current_token.add_css(MakefileCSS.KEYWORD)
                        self.eat()
                        while self.current_token.type not in (TokenType.EOF, TokenType.LF):
                            # if self.current_token.type == TokenType.ID:
                            if self.current_token.type != TokenType.COMMA:
                                self.current_token.add_css(ShellCSS.URL)
                            self.eat()
                    else:
                        self.current_token.type = TokenType.ID
                else:
                    self.current_token.add_css(MakefileCSS.KEYWORD)

            if self.current_token.type == TokenType.ID:
                if re.match(r"^[A-Z_0-9-]+$", self.current_token.value):
                    self.current_token.add_css(MakefileCSS.VARIABLE)
                elif self.peek_next_token().type == TokenType.COLON:
                    self.current_token.add_css(MakefileCSS.MISSION)
                    # 上一个换行之前的所有 ID 均为 MISSION
                    for i in range(len(self._token_list) - 1, -1, -1):
                        if self._token_list[i].type == TokenType.LF:
                            break
                        elif self._token_list[i].type == TokenType.ID:
                            self._token_list[i].add_css(MakefileCSS.MISSION)
                else:
                    # 如果形如 $(if ...) 那么是一个函数
                    if len(self._token_list) >= 2:
                        if (
                            self._token_list[-1].type == TokenType.LPAREN
                            and self._token_list[-2].type == TokenType.DOLLAR
                            and self.peek_next_token().type != TokenType.RPAREN
                        ):
                            self.current_token.add_css(MakefileCSS.FUNCTION)

            if self.current_token.type == TokenType.LANGLE_BRACE:
                self.current_token.type = MakefileTokenType.REDIRECT_TO
            elif self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = MakefileTokenType.REDIRECT_FROM

            if self.current_token.type == TokenType.AT_SIGN:
                if self.peek_next_token().type == TokenType.ID:
                    self.eat()
                    self.current_token.add_css(ShellCSS.PROGRAM)
            self.eat()
