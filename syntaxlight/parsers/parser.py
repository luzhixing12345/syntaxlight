from ..lexers.lexer import Lexer, Token, TokenType, TTYColor
from ..error import ParserError, ErrorCode
from enum import Enum
from ..ast import AST
from typing import List
import sys
import html
import traceback


class Parser:
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        self.lexer: Lexer = lexer
        # set current token to the first token taken from the input
        self.skip_invisible_characters = skip_invisible_characters
        self.skip_space = skip_space
        self.display_warning = display_warning
        self._token_list: List[Token] = []  # lexer 解析后经过 parser 确定类型后的 tokens
        self.brace_list: List[TokenType] = [
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.LSQUAR_PAREN,
            TokenType.RSQUAR_PAREN,
            TokenType.LCURLY_BRACE,
            TokenType.RCURLY_BRACE,
            TokenType.LANGLE_BRACE,
            TokenType.RANGLE_BRACE,
        ]
        self.brace_max_depth = 3  # 深度循环轮次
        self.node: AST = None
        self.current_token: Token = self.lexer.get_next_token()
        self._skip()

    def error(
        self,
        error_code: ErrorCode,
        message: str = "",
        token: Token = None,
    ):
        traceback.print_stack()
        if token is None:
            token = self.current_token

        if message == "":
            if token.value in self.lexer.invisible_characters:
                message = token.type.name
            else:
                message = token.value

        raise ParserError(
            error_code=error_code,
            token=token,
            context=self.lexer.get_error_token_context(token),
            file_path=self.lexer.file_path,
            message=message,
        )

    def warning(self, message=None, ast: AST = None):
        """
        语法解析过程中的警告信息
        """
        if not self.display_warning:
            return

        warning_color = TTYColor.MAGENTA

        sys.stderr.write(self.lexer.ttyinfo("warning: ", warning_color) + message + "\n")
        sys.stderr.write(self.lexer.ttyinfo(str(ast), warning_color))

    def eat(self, token_type: Enum) -> List[Token]:
        # print(self.current_token)
        tokens = [self.current_token]
        if self.current_token.type == token_type:
            self._register_token()
            self.current_token = self.lexer.get_next_token()
            tokens.extend(self._skip())
        else:
            current_value = self.current_token.value
            expected_value = token_type.value
            if current_value in self.lexer.invisible_characters:
                current_value = self.current_token.type.name
            if self.current_token.type == TokenType.EOF:
                current_value = "EOF"
            if expected_value in self.lexer.invisible_characters:
                expected_value = token_type.name
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
                message=f"should match {expected_value} but got {current_value}",
            )
        return tokens

    def _skip(self) -> List[Token]:
        tokens = []

        if self.current_token.type == TokenType.COMMENT:
            self._register_token()
            tokens.append(self.current_token)
            self.current_token = self.lexer.get_next_token()

        if self.skip_invisible_characters and self.skip_space:
            while (
                self.current_token.value in self.lexer.invisible_characters
                or self.current_token.type == TokenType.SPACE
            ):
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()

        elif self.skip_invisible_characters and not self.skip_space:
            while self.current_token.value in self.lexer.invisible_characters:
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()
        elif not self.skip_invisible_characters and self.skip_space:
            while self.current_token.type == TokenType.SPACE:
                self._register_token()
                tokens.append(self.current_token)
                self.current_token = self.lexer.get_next_token()

        if self.current_token.type == TokenType.COMMENT:
            self._register_token()
            tokens.append(self.current_token)
            self.current_token = self.lexer.get_next_token()
        return tokens

    def skip_crlf(self):
        """
        set `skip_invisible_characters` to False \n
        跳过连续的换行 `\\n` or `\\r\\n`
        """
        while self.current_token.type in (TokenType.LF, TokenType.CR):
            self.eat(self.current_token.type)

    def skip_end(self):
        """
        跳过最后的空白和换行
        """
        while self.current_token.type != TokenType.EOF:
            self._skip()

    def eat_lf(self):
        """
        跳过一个换行
        """
        if self.current_token.type == TokenType.CR:
            self.eat(self.current_token.type)
        if self.current_token.type == TokenType.EOF:
            return
        else:
            self.eat(TokenType.LF)

    def _register_token(self):
        """
        将一个 token 注册到 token_list 当中

        每一个 token 都需要间接的执行此过程, 以便最终恢复高亮文本信息
        """
        token = self.current_token
        # print(token)
        self._token_list.append(token)

    def to_html(self):
        """
        将一个解析完成的 AST node 输出其 token 流的 HTML 格式
        """
        html_str = ""
        # 对于 ([{<>}]) 计算括号深度
        brace_depth = 0
        brace_stack: List[TokenType] = []
        for token in self._token_list:
            # print(self.brace_list)
            if token.type in self.brace_list:
                if len(brace_stack) == 0:
                    brace_stack.append(token.type)
                    token.class_list.append(f"brace-depth-{brace_depth%self.brace_max_depth}")
                    brace_depth += 1
                else:
                    # 括号匹配
                    if self.brace_list.index(brace_stack[-1]) + 1 == self.brace_list.index(
                        token.type
                    ):
                        brace_stack.pop()
                        brace_depth -= 1
                        token.class_list.append(f"brace-depth-{brace_depth%self.brace_max_depth}")
                    else:
                        brace_stack.append(token.type)
                        token.class_list.append(f"brace-depth-{brace_depth%self.brace_max_depth}")
                        brace_depth += 1

            html_str += f'<span class="{token.get_css_class()}">{html.escape(token.value)}</span>'
        return html_str

    def parse(self):
        raise NotImplementedError(self.__class__.__name__ + " must override the parse function")
