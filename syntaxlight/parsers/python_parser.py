from .parser import Parser
from ..lexers import TokenType, PythonTokenType
import re

from ..gdt import CSS, GlobalDescriptorTable

GDT = GlobalDescriptorTable()

class PythonParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):

        while self.current_token.type != TokenType.EOF:

            if self.current_token.type == PythonTokenType.CLASS:
                self.eat()
                self.current_token.add_css(CSS.CLASS_NAME)
                self.eat()
                if self.current_token.type == TokenType.LPAREN:
                    self.eat()
                    self.current_token.add_css(CSS.CLASS_NAME)

            elif self.current_token.type == PythonTokenType.DEF:
                self.eat()
                self.current_token.add_css(CSS.FUNCTION_NAME)

            elif self.current_token.type == PythonTokenType.FROM:
                self.eat()
                while self.current_token.type == TokenType.DOT:
                    self.eat()
                if self.current_token.type == TokenType.ID:
                    self.current_token.add_css(CSS.IMPORT_LIBNAME)

            elif self.current_token.type == PythonTokenType.IMPORT:
                self.eat()
                self.current_token.add_css(CSS.IMPORT_LIBNAME)
                if self.peek_next_token().type == PythonTokenType.AS and self.peek_next_token(2).type == TokenType.ID:
                    self.eat()
                    self.eat()
                    self.current_token.add_css(CSS.IMPORT_LIBNAME)
                    GDT.register_id(self.current_token.value, CSS.IMPORT_LIBNAME)

            elif self.current_token.type == TokenType.ID:
                if self.current_token.value in GDT:
                    self.current_token.add_css(GDT[self.current_token.value])
                elif self.peek_next_token().type == TokenType.LPAREN:
                    if self.current_token.value[0].isupper():
                        self.current_token.add_css(CSS.CLASS_INSTANTIATION)
                    else:
                        self.current_token.add_css(CSS.FUNCTION_CALL)
                elif bool(re.match(r"^[A-Z0-9_]+$", self.current_token.value)):
                    self.current_token.add_css(CSS.ENUM_ID)
                    if len(self._token_list) >= 2:
                        if self._token_list[-1].type == TokenType.DOT:
                            base_class = self._token_list[-2]
                            if base_class.type == TokenType.ID:
                                if base_class.value[0].isupper():
                                    base_class.add_css(CSS.CLASS_INSTANTIATION)
                                else:
                                    self.current_token.class_list.pop()

            elif self.current_token.type == TokenType.COLON:
                self.skip_invis_chars = False
                self.skip_space = False
                typehint_token = self.peek_next_token(2)
                if typehint_token.type == TokenType.ID and typehint_token.value[0].isupper():
                    self.eat()
                    while self.current_token.type not in (
                        TokenType.EOF,
                        TokenType.ASSIGN,
                        TokenType.RPAREN,
                        TokenType.COMMA,
                        TokenType.LF,
                    ):
                        if self.current_token.type == TokenType.ID:
                            self.current_token.add_css(CSS.CLASS_INSTANTIATION)
                        self.eat()
                self.skip_invis_chars = True
                self.skip_space = True

            self.eat()
