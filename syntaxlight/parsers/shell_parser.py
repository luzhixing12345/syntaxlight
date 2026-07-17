from .parser import Parser
from ..lexers import TokenType, ShellTokenType, Token
from enum import Enum
import re


class ShellCSS(Enum):
    KEYWORD = "Keyword"
    PROGRAM = "Program"
    VARIANT = "Variant"
    FUNCTION = "Function"
    URL = "Url"
    HOST_NAME = "HostName"
    DIR_PATH = "DirPath"
    IP_ADDRESS = "IpAddress"
    # TREE_NORMAL = "TreeNormal"  # 常规文件
    # TREE_EXE = "TreeExe"  # 可执行文件
    # TREE_IGNORE = "TreeIgnore"  # 类似 .o 的中间文件
    # TREE_DIR = "TreeDir"  # 目录


class ShellLineMode(Enum):
    SCRIPT = "script"
    COMMAND = "command"
    OUTPUT = "output"


class ShellParser(Parser):
    STRUCTURAL_KEYWORDS = {
        ShellTokenType.IF,
        ShellTokenType.ELIF,
        ShellTokenType.ELSE,
        ShellTokenType.THEN,
        ShellTokenType.FI,
        ShellTokenType.FOR,
        ShellTokenType.DO,
        ShellTokenType.IN,
        ShellTokenType.DONE,
        ShellTokenType.WHILE,
        ShellTokenType.BREAK,
    }
    COMMAND_SEPARATORS = {
        TokenType.AND,
        TokenType.OR,
        TokenType.PIPE,
        TokenType.SEMI,
    }
    COMMON_COMMANDS = {
        "alias", "apt", "apt-get", "awk", "bash", "bison", "brew", "cat",
        "cd", "chmod", "chown", "cmake", "command", "cp", "curl", "cut",
        "date", "df", "diff", "docker", "dot", "echo", "env", "exec",
        "export", "find", "g++", "gawk", "gcc", "git", "grep", "gzip",
        "head", "kill", "ld", "ln", "ls", "m4", "make", "makeinfo",
        "mkdir", "mv", "node", "npm", "numactl", "patch", "perl", "pip",
        "pip3", "poetry", "printf", "python", "python3", "qemu-img", "read",
        "readlink", "rm", "rsync", "sed", "scons", "sh", "sleep", "sort",
        "source", "sudo", "tail", "tar", "tee", "test", "time", "touch",
        "tr", "unset", "wait", "wc", "wget", "which", "xargs", "xz", "zood",
    }

    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.line_info = self._classify_lines(lexer.text)
        self.active_line = None
        self.line_mode = ShellLineMode.OUTPUT
        self.command_start = None
        self.expect_program = False
        self.seen_for = False
        self.in_backticks = False

    def parse(self):
        """
        bash 的文法可变因素太多, 这里直接不使用 BNF 采取匹配的方式
        """
        while self.current_token.type != TokenType.EOF:
            self._enter_line()

            if self._in_command_region():
                self._highlight_shell_syntax()
                
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
                if self._is_url(self.current_token.value):
                    self.current_token.add_css(ShellCSS.URL)
            elif self.current_token.type == ShellTokenType.IP_ADDRESS:
                self.current_token.add_css(ShellCSS.IP_ADDRESS)

            if self.current_token.type == TokenType.STRING:
                self.get_string()
                continue

            self.eat()

    def _enter_line(self):
        if self.current_token.line == self.active_line:
            return
        previous_line = self.active_line
        previous_expect_program = self.expect_program
        previous_seen_for = self.seen_for
        previous_in_backticks = self.in_backticks
        self.active_line = self.current_token.line
        info = self.line_info.get(
            self.active_line,
            {
                "mode": ShellLineMode.OUTPUT,
                "command_start": None,
                "continuation": False,
            },
        )
        self.line_mode = info["mode"]
        self.command_start = info["command_start"]
        if info["continuation"] and previous_line is not None:
            self.expect_program = previous_expect_program
            self.seen_for = previous_seen_for
            self.in_backticks = previous_in_backticks
        else:
            self.expect_program = self.line_mode in (
                ShellLineMode.SCRIPT,
                ShellLineMode.COMMAND,
            )
            self.seen_for = False
            self.in_backticks = False

    def _in_command_region(self):
        if self.line_mode == ShellLineMode.OUTPUT or self.command_start is None:
            return False
        return self._token_start_column(self.current_token) >= self.command_start

    def _highlight_shell_syntax(self):
        token_type = self.current_token.type

        if token_type == TokenType.BACKTICK:
            self.in_backticks = not self.in_backticks
            self.expect_program = self.in_backticks
            return
        if token_type == TokenType.LPAREN and self._previous_significant_value() == "$":
            self.expect_program = True
            return
        if token_type in self.COMMAND_SEPARATORS:
            self.expect_program = True
            return
        if self._is_assignment_start():
            self.current_token.add_css(ShellCSS.VARIANT)
            return

        if token_type in self.STRUCTURAL_KEYWORDS:
            if self._is_contextual_keyword(token_type):
                self.current_token.add_css(ShellCSS.KEYWORD)
                if token_type == ShellTokenType.FOR:
                    self.seen_for = True
                    self.expect_program = False
                elif token_type in (
                    ShellTokenType.IF,
                    ShellTokenType.WHILE,
                    ShellTokenType.ELIF,
                    ShellTokenType.ELSE,
                    ShellTokenType.THEN,
                    ShellTokenType.DO,
                ):
                    self.expect_program = True
                else:
                    self.expect_program = False
                return

        if self.expect_program:
            if self._is_function_definition():
                self.current_token.add_css(ShellCSS.FUNCTION)
                self.expect_program = False
                return
            if self._is_command_word(self.current_token):
                self.current_token.add_css(ShellCSS.PROGRAM)
                self.expect_program = False

    def _is_contextual_keyword(self, token_type):
        if token_type == ShellTokenType.IN:
            return self.seen_for
        if token_type in (
            ShellTokenType.THEN,
            ShellTokenType.DO,
            ShellTokenType.ELSE,
            ShellTokenType.ELIF,
            ShellTokenType.FI,
            ShellTokenType.DONE,
        ):
            return self.expect_program
        if token_type in (
            ShellTokenType.IF,
            ShellTokenType.FOR,
            ShellTokenType.WHILE,
            ShellTokenType.BREAK,
        ):
            return self.expect_program
        return False

    def _is_assignment_start(self):
        return (
            self.current_token.type == TokenType.ID
            and self.peek_next_token().type == TokenType.ASSIGN
        )

    def _is_function_definition(self):
        return (
            self.current_token.type == TokenType.ID
            and self.peek_next_token().type == TokenType.LPAREN
            and self.peek_next_token(2).type == TokenType.RPAREN
        )

    @staticmethod
    def _is_command_word(token):
        return token.type in (
            TokenType.ID,
            TokenType.LSQUAR_PAREN,
            ShellTokenType.CD,
            ShellTokenType.EXPORT,
        )

    def _previous_significant_value(self):
        ignored = {
            TokenType.BACKSPACE,
            TokenType.COMMENT,
            TokenType.CR,
            TokenType.FORM_FEED,
            TokenType.LF,
            TokenType.SPACE,
            TokenType.TAB,
            TokenType.VERTICAL_TAB,
        }
        for token in reversed(self.token_list):
            if token.type not in ignored:
                return token.value
        return None

    @staticmethod
    def _token_start_column(token):
        return token.column - len(token.value) + 1

    def _classify_lines(self, text):
        lines = text.splitlines()
        first_content = next((line.strip() for line in lines if line.strip()), "")
        is_script = first_content.startswith("#!")
        line_info = {}
        previous_command = False
        previous_continues = False

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            command_start = None
            mode = ShellLineMode.OUTPUT
            continuation = False

            prompt_match = re.match(
                r"^\s*(?:\([^)]+\)\s*)?"
                r"(?:[\w.-]+@[\w.-]+:[^\s]*[$#]|\$)\s+"
                r"(?P<command>\S)",
                line,
            )
            if not stripped or (stripped.startswith("#") and not stripped.startswith("#!")):
                mode = ShellLineMode.SCRIPT if is_script else ShellLineMode.OUTPUT
            elif previous_command and previous_continues:
                mode = ShellLineMode.SCRIPT if is_script else ShellLineMode.COMMAND
                command_start = len(line) - len(line.lstrip()) + 1
                continuation = True
            elif is_script:
                mode = ShellLineMode.SCRIPT
                command_start = len(line) - len(line.lstrip()) + 1
            elif prompt_match is not None:
                mode = ShellLineMode.COMMAND
                command_start = prompt_match.start("command") + 1
            elif line[:1].isspace():
                mode = ShellLineMode.OUTPUT
            elif self._looks_like_command_line(stripped):
                mode = ShellLineMode.COMMAND
                command_start = len(line) - len(line.lstrip()) + 1

            line_info[line_number] = {
                "mode": mode,
                "command_start": command_start,
                "continuation": continuation,
            }
            previous_command = mode in (ShellLineMode.SCRIPT, ShellLineMode.COMMAND)
            previous_continues = line.rstrip().endswith("\\")
        return line_info

    def _looks_like_command_line(self, stripped):
        if stripped.startswith(("./", "../")):
            return True
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", stripped):
            return True
        first_word = re.match(r"^[^\s;|&]+", stripped)
        if first_word is None:
            return False
        word = first_word.group(0)
        return (
            word in self.COMMON_COMMANDS
            or word in self.lexer.reserved_keywords
        )

    @staticmethod
    def _is_url(value):
        return bool(
            re.match(
                r"^(?:(?:https?|ftp)://|www\.)"
                r"[A-Za-z0-9.-]+(?::\d{1,5})?"
                r"(?:/[^\s]*)?$",
                value,
            )
        )

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
