from .parser import Parser
from ..lexers import TokenType, ShellTokenType
from ..gdt import *
import re


class ShellCSS(Enum):
    KEYWORD = "Keyword"
    PROGRAM = "Program"
    VARIANT = "Variant"
    FUNCTION = "Function"
    URL = 'Url'


class ShellParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=False, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)

    def parse(self):
        """
        bash 的文法可变因素太多, 这里直接不使用 BNF 采取匹配的方式
        """
        is_program_name = True
        new_program_token_type = [TokenType.LF, TokenType.PIPE, TokenType.SEMI, TokenType.AND]
        while self.current_token.type != TokenType.EOF:

            if self.current_token.type == TokenType.BACK_SLASH:
                self.eat()
                self.eat_lf()
                continue

            # print(self.current_token, is_program_name)
            if self.current_token.value in self.lexer.reserved_keywords:
                self.current_token.add_css(ShellCSS.KEYWORD)
                if is_program_name:
                    is_program_name = False

            if (
                self.current_token.type == TokenType.DOLLAR
                and self.peek_next_token().type == TokenType.LPAREN
            ):
                is_program_name = True

            if self.current_token.type == TokenType.ID:
                if self.peek_next_token().type == TokenType.LPAREN:
                    # function
                    self.current_token.add_css(ShellCSS.FUNCTION)
                elif bool(
                    re.match(
                        r"^https?:\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?(?:;[\w\-\.,@?^=%&:\/~\+#=]*)?$",
                        self.current_token.value,
                    )
                ):
                    self.current_token.add_css(ShellCSS.URL)
                elif self.is_valid_path(self.current_token.value):
                    self.current_token.type = ShellTokenType.PATH

            if is_program_name:
                if self.current_token.type in (TokenType.ID, ShellTokenType.PATH):
                    is_program_name = False
                    self.current_token.add_css(ShellCSS.PROGRAM)
            else:
                if self.current_token.type in new_program_token_type:
                    is_program_name = True

            if self.peek_next_token().type == TokenType.ASSIGN:
                self.current_token.add_css(ShellCSS.VARIANT)

            if self.current_token.type == TokenType.STRING:
                self.string_inside_format(self.current_token)
                continue

            self.eat()

    def is_valid_path(self, path):
        # 匹配Linux系统的绝对路径或相对路径
        linux_path_pattern = r'^/[^/\0]+(/[^/\0]+)*$|^(\./[^/\0]+)+$'

        # 匹配Windows系统的绝对路径或相对路径
        windows_path_pattern = r'^[a-zA-Z]:\\(\\[^\\/\0]+)*$|^(\.\\[^\\/\0]+)+$'

        any_path_pattern = r'[0-9a-zA-Z/.-_]*/[0-9a-zA-Z/.-_]*'

        return re.match(linux_path_pattern, path) is not None or \
            re.match(windows_path_pattern, path) is not None or \
            re.match(any_path_pattern, path) is not None