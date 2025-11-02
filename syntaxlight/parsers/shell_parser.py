from .parser import Parser
from ..lexers import TokenType, ShellTokenType, Token
from ..gdt import *
import re


class ShellCSS(Enum):
    KEYWORD = "Keyword"
    PROGRAM = "Program"
    VARIANT = "Variant"
    FUNCTION = "Function"
    URL = "Url"
    HOST_NAME = "HostName"
    DIR_PATH = "DirPath"
    SUCCESS = "Success"
    FAIL = "Fail"
    # TREE_NORMAL = "TreeNormal"  # 常规文件
    # TREE_EXE = "TreeExe"  # 可执行文件
    # TREE_IGNORE = "TreeIgnore"  # 类似 .o 的中间文件
    # TREE_DIR = "TreeDir"  # 目录


class ShellParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)

    def parse(self):
        """
        bash 的文法可变因素太多, 这里直接不使用 BNF 采取匹配的方式
        """
        is_program_output = False
        while self.current_token.type != TokenType.EOF:
            # print(self.current_token, is_program_name)
            if self.current_token.value in self.lexer.reserved_keywords:
                self.current_token.add_css(ShellCSS.KEYWORD)
                
            if self.current_token.type == ShellTokenType.LINUX_USER_PATH:
                match_result = re.match(
                    r"^(?P<HostName>\w+@[\w.-]+)(?P<colon>:)(?P<DirPath>[~\w/]+)(?P<Tag>[$#]?)",
                    self.current_token.value,
                )
                line = self.current_token.line
                column = self.current_token.column - len(self.current_token.value)
                linux_path_type = [
                    ShellTokenType.HOST_NAME,
                    TokenType.COLON,
                    ShellTokenType.DIR_PATH,
                    ShellTokenType.TAG,
                ]
                for name, path_type in zip(match_result.groupdict(), linux_path_type):
                    value = match_result.group(name)
                    column += len(value)
                    token = Token(path_type, value, line, column)
                    self.manual_register_token(token)
                self.manual_get_next_token()
                continue

            if self.current_token.type == TokenType.ID:
                if bool(
                    re.match(
                        r"^https?:\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?(?:;[\w\-\.,@?^=%&:\/~\+#=]*)?$",
                        self.current_token.value,
                    )
                ):
                    self.current_token.add_css(ShellCSS.URL)

            if self.current_token.type == TokenType.STRING:
                self.get_string()
                continue

            self.eat()

    def is_valid_path(self, path):
        # 匹配Linux系统的绝对路径或相对路径
        linux_path_pattern = r"^/[^/\0]+(/[^/\0]+)*$|^(\./[^/\0]+)+$"

        # 匹配Windows系统的绝对路径或相对路径
        windows_path_pattern = r"^[a-zA-Z]:\\(\\[^\\/\0]+)*$|^(\.\\[^\\/\0]+)+$"

        any_path_pattern = r"[0-9a-zA-Z/\.\-\_]*/[0-9a-zA-Z/\.\-\_]*"

        return (
            re.match(linux_path_pattern, path) is not None
            or re.match(windows_path_pattern, path) is not None
            or re.match(any_path_pattern, path) is not None
        )

    def has_chinese_word(self, text):
        pattern = re.compile(r"[\u4e00-\u9fa5]+")
        return pattern.search(text) is not None
