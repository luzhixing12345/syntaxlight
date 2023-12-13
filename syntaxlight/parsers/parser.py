from ..lexers.lexer import Lexer, Token, TokenType, TTYColor
from ..error import ParserError, ErrorCode
from enum import Enum
from ..asts.ast import AST, Keyword, add_ast_type, Identifier, Punctuator, WrapString, Number, String
from typing import List
import sys
import html
import traceback
import re
from ..gdt import CSS


DEBUG = False
DEBUG = True


class Parser:
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        self.lexer: Lexer = lexer
        # set current token to the first token taken from the input
        self.skip_invisible_characters = skip_invisible_characters
        self.skip_space = skip_space
        self.display_warning = display_warning
        self._token_list: List[Token] = []  # lexer 解析后经过 parser 确定类型后的 tokens
        self.root: AST = None  # 主根节点
        self.sub_roots: List[AST] = []  # 其他根节点, 例如预处理命令
        self._status_stack = []  # 状态栈
        self.current_token: Token = self.lexer.get_next_token()
        self._skip()

    def error(
        self,
        error_code: ErrorCode,
        message: str = "",
        token: Token = None,
    ):
        error_trace = self.error_func_trace()
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
            error_trace=error_trace,
        )

    def warning(self, message=None, ast: AST = None):
        """
        语法解析过程中的警告信息
        """
        if not self.display_warning:
            return

        warning_color = TTYColor.MAGENTA

        sys.stderr.write(self.lexer.ttyinfo("warning: ", warning_color, underline=False) + message + "\n")
        # sys.stderr.write(self.lexer.ttyinfo(str(ast), warning_color))

    def error_func_trace(self) -> List[str]:
        """
        查看 python 函数调用栈
        """
        error_trace = []
        # 前4后2不重要
        stack_trace = traceback.extract_stack()[4:-2]
        function_length = 0
        line_length = 0
        for stack in stack_trace:
            _, line_number, function_name, _ = stack
            function_length = max(function_length, len(function_name))
            line_length = max(line_length, len(str(line_number)))
        for stack in stack_trace:
            _, line_number, function_name, line_of_code = stack
            error_trace.append(
                f"[{function_name:>{function_length}}][{line_number:<{line_length}}]: {line_of_code.strip()}"
            )
        return error_trace

    def eat(self, token_type: Enum = None) -> List[Token]:
        """
        匹配一个 token_type 类型的 token, 并获取下一个 token 更新 current_token

        token_type 默认值为 None, 表示匹配当前 current_token.type
        """
        # print(token_type, self.current_token)
        # self._log_trace()
        # if DEBUG:
        #     import inspect
        #     frame = inspect.currentframe().f_back
        #     lineno = frame.f_lineno
        #     print(f"The 'eat' method was called from line {lineno}.")
        tokens = [self.current_token]
        if token_type is None or self.current_token.type == token_type:
            self._register_token()
            self.current_token = self.lexer.get_next_token()
            tokens.extend(self._skip())
            self.after_eat()
            return tokens

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

    def manual_get_next_token(self):
        """
        正常情况下调用 eat 获取下一个 token, 如果需要合并多个 token 并生成一个新的 token 时可调用此函数
        """
        self.current_token = self.lexer.get_next_token()
        self._skip()
        self.after_eat()

    def manual_register_token(self, token):
        """
        正常情况下不需要手动将 token 注册到 _token_list 当中, eat 内部会调用此方法

        如果因为合并或分割创建了新的 token 可调用此方法注册
        """
        self._register_token(token)

    def after_eat(self):
        """
        如果希望在 eat 之后对于 current_token 进行一些操作, 比如查 GDT 或处理预处理关键字, 可在继承类中重载此方法
        """
        return

    def _skip(self) -> List[Token]:
        """
        跳过不可见字符和空格

        由 self.skip_invisible_characters 与 self.skip_space 控制
        """
        tokens = []
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
            tokens.extend(self._skip())
            return tokens
        else:
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
        跳过一个换行, 如果是结尾 EOF 则不跳过
        """
        if self.current_token.type == TokenType.CR:
            self.eat(self.current_token.type)
        if self.current_token.type == TokenType.EOF:
            return
        self.eat(TokenType.LF)
        self.skip_crlf()

    def peek_next_token(self, n=1) -> Token:
        """
        查看下一个 token 的类型
        """
        # 保存程序状态
        self.lexer._record()
        token_list_length = len(self._token_list)
        sub_roots_length = len(self.sub_roots)
        current_token = self.current_token

        for _ in range(n):
            self.eat()
        next_token = self.current_token

        self.lexer._reset()
        self._token_list = self._token_list[:token_list_length]
        self.sub_roots = self.sub_roots[:sub_roots_length]
        self.current_token = current_token
        return next_token

    def look_back_token(self, n=1) -> Token:
        """
        查看前面以匹配的 token 类型
        """
        return self._token_list[-n]

    def _register_token(self, token=None):
        """
        将一个 token 注册到 token_list 当中

        每一个 token 都需要间接的执行此过程, 以便最终恢复高亮文本信息
        """
        if token is None:
            token = self.current_token
        # print(token)
        self._token_list.append(token)

    def to_html(self):
        """
        将一个解析完成的 AST node 输出其 token 流的 HTML 格式
        """
        html_str = ""
        self.brace_matching()
        for token in self._token_list:
            html_str += f'<span class="{token.get_css_class()}">{html.escape(token.value)}</span>'
        return html_str

    def brace_matching(self):
        """
        对于 ([{<>}]) 计算括号深度
        """
        brace_max_depth = 3  # 括号深度循环轮次
        left_brace_list: List[TokenType] = [
            TokenType.LPAREN,
            TokenType.LSQUAR_PAREN,
            TokenType.LCURLY_BRACE,
            TokenType.LANGLE_BRACE,
        ]
        right_brace_list: List[TokenType] = [
            TokenType.RPAREN,
            TokenType.RSQUAR_PAREN,
            TokenType.RCURLY_BRACE,
            TokenType.RANGLE_BRACE,
        ]

        brace_depth = 0
        brace_stack: List[TokenType] = []
        for token in self._token_list:
            # print(brace_list)
            if token.type in left_brace_list:
                # 左括号直接加入到 stack 当中
                brace_stack.append(token.type)
                token.class_list.append(f"BraceDepth-{brace_depth%brace_max_depth}")
                brace_depth += 1
            elif token.type in right_brace_list:
                if len(brace_stack) == 0:
                    # 栈为空且当前符号为右括号, 直接置 0
                    token.class_list.append(f"BraceDepth-0")
                else:
                    if left_brace_list.index(brace_stack[-1]) == right_brace_list.index(token.type):
                        # 如果左右括号类型匹配
                        brace_stack.pop()
                        brace_depth -= 1
                        token.class_list.append(f"BraceDepth-{brace_depth%brace_max_depth}")
                    else:
                        # 如果括号类型不匹配, 不断弹出栈内元素直到可以匹配
                        while True:
                            brace_stack.pop()
                            brace_depth -= 1
                            if len(brace_stack) == 0:
                                break
                            if left_brace_list.index(brace_stack[-1]) == right_brace_list.index(token.type):
                                brace_stack.pop()
                                brace_depth -= 1
                                token.class_list.append(f"BraceDepth-{brace_depth%brace_max_depth}")
                                break
                            

    def parse(self):
        raise NotImplementedError(self.__class__.__name__ + " must override the parse function")

    def get_keyword(self, token_type: Enum = None, css_type: Enum = None) -> Keyword:
        """
        keyword

        @token_type: keyword 的类型,默认为 current_token.type
        @class_name: 修改 Keyword 的类名
        """
        keyword = Keyword(self.current_token.value)
        if token_type:
            keyword.register_token(self.eat(token_type))
        else:
            keyword.register_token(self.eat())
        if css_type is not None:
            add_ast_type(keyword, css_type)
        return keyword

    def identifier(self) -> Identifier:
        """
        ID
        """
        node = Identifier(self.current_token.value)
        node.register_token(self.eat(TokenType.ID))
        return node

    def punctuator(self, token_type: Enum = None) -> Punctuator:
        """
        获取运算符
        
        对于 <> 修正为 TokenType.LT 和 TokenType.GT
        """
        node = Punctuator(self.current_token.value)
            
        if token_type is None:
            if self.current_token.type == TokenType.LANGLE_BRACE:
                self.current_token.type = TokenType.LT
            elif self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = TokenType.GT
            node.register_token(self.eat())
        else:
            node.register_token(self.eat(token_type))
        return node

    def string(self):
        node = WrapString()
        node.update(strings=self.string_inside_format())
        return node

    def string_inside_format(self, token: Token = None) -> List[String]:
        """
        取出其中格式化字符(如 %d %x \n) 并新建 token
        """
        if token is None:
            token = self.current_token
        pattern = r"(%[#0-9ldiufFeEgGxXoscpaAnYyMmHhSsLl]+|(?:\\\\|\\n|\\t|\\v|\\f))"
        sub_strings = re.split(pattern, token.value)
        new_asts = []
        line = token.line
        column = token.column - len(token.value)
        token_type = token.type
        for sub_string in sub_strings:
            if len(sub_string) == 0:
                continue
            column += len(sub_string)
            token = Token(token_type, sub_string, line, column)
            if bool(re.match(r"%[#0-9ldiufFeEgGxXoscpaAnYyMmHhSsLl]+", sub_string)):
                token.add_css(CSS.FORMAT)
            elif sub_string in ["\\n", "\\t", "\\f", "\\v", "\\a", "\\b", "\\\\"]:
                token.add_css(CSS.CONTROL)

            self.manual_register_token(token)
            node = String(token.value)
            node.register_token([token])
            new_asts.append(node)

        self.manual_get_next_token()
        return new_asts

    def number(self):
        node = Number(self.current_token.value)
        node.register_token(self.eat())
        return node
