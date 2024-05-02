from enum import Enum
from ..error import ErrorCode, LexerError, ParserError
from typing import Dict, List, Tuple, Union
import re
from ..token import Token, TokenType, BaseTokenType


class Lexer:
    """
    Lexer 基类, 提供了一些基础函数和功能, 比如匹配数字, 匹配字符串

        可能有些编程语言的处理(比如Lua的字符串)不同, 单独覆盖即可

    继承 Lexer 的子类需要重写其 get_next_token 方法以提供给后续的 parser 解析
    """

    def __init__(self, text: str, LanguageTokenType: BaseTokenType):
        self.text: str = text
        self.pos: int = 0  # 当前指针指向的字符
        self.current_char: str = self.text[self.pos]  # 当前指针指向的字符
        self.line: int = 1
        self.column: int = 1  # 指向 token 的 value 中最后出现的字符的位置
        self.LanguageTokenType: Enum = LanguageTokenType
        self.file_path = ""  # 手动修改文件路径, 用于后期错误处理的输出
        self._status_stack = []  # 状态栈

        tt_list: List[Enum] = list(LanguageTokenType)
        try:
            # RESERVED_KEYWORD_START 和 RESERVED_KEYWORD_END 之间为保留关键字
            # 每一个自定义的 TokenType 都应当定义这两个枚举类型
            start_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_START)
            end_index = tt_list.index(LanguageTokenType.RESERVED_KEYWORD_END)
            self.reserved_keywords = {
                token_type.value: token_type for token_type in tt_list[start_index + 1 : end_index]
            }
        except:
            self.reserved_keywords = {}
        # 不可见字符, 一般情况下直接忽略即可, 这里考虑到为了不破坏原本的代码格式所以进行保留
        # \n \t \v \r \f \b
        self.invisible_characters = [
            TokenType.LF.value,
            TokenType.TAB.value,
            TokenType.VERTICAL_TAB.value,
            TokenType.CR.value,
            TokenType.FORM_FEED.value,
            TokenType.BACKSPACE.value,
        ]

        # 匹配长字符串时使用
        # if self.current_char in self.long_op_dict:
        #     return self.get_long_op()
        self.long_op_dict: Dict[str, List] = {}

    def build_long_op_dict(self, supported_long_op: List[str]):
        """
        构造长运算符的匹配模式
        """
        self._long_ops = sorted(supported_long_op, key=len, reverse=True)
        for long_op in self._long_ops:
            assert len(long_op) >= 2, f"{long_op} should be longer"
            if self.long_op_dict.get(long_op[0]) is None:
                self.long_op_dict[long_op[0]] = []
            self.long_op_dict[long_op[0]].append(long_op[1:])

    def _record(self):
        """
        用于 parser 中 peek_next_token

        记录当前 lexer 解析状态, 被 _reset 调用时恢复
        """
        # 采用栈的方式保存数据状态, 避免由于 peek_next_token 中的 eat 导致多次嵌套调用覆盖数据
        self._status_stack.append({"pos": self.pos, "c": self.current_char, "line": self.line, "column": self.column})

    def _reset(self):
        """
        用于 parser 中 peek_next_token

        恢复为 lexer 之前的状态
        """
        status = self._status_stack.pop()
        self.pos = status["pos"]
        self.current_char = status["c"]
        self.line = status["line"]
        self.column = status["column"]

    def error(
        self,
        error_code: ErrorCode = None,
        token: Token = None,
        message: str = "",
        ErrorType=Union[LexerError, ParserError],
    ):
        # 对于 file_path 的处理, 去掉开头的 ./
        # \ 改为 /
        if self.file_path.startswith("./"):
            self.file_path = self.file_path[2:]
        self.file_path = self.file_path.replace("\\", "/")

        raise ErrorType(
            token=token,
            error_code=error_code,
            error_context=self.text,
            error_message=message,
            file_path=self.file_path,
        )

    def advance(self):
        """
        获取下一个字符, 遇到换行则更新 line
        """
        if self.current_char == "\n":
            self.line += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # 结束
            self.column += 1
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def skip_whitespace(self):
        """
        通常来说直接跳过空格即可, 这里保留空格是为了不破坏原本的代码格式
        """
        result = ""
        while self.current_char is not None and self.current_char == " ":
            result += " "
            self.advance()
        return Token(TokenType.SPACE, result, self.line, self.column - 1)

    def skip_invisiable_character(self):
        token = Token(
            TokenType(self.current_char),
            self.current_char,
            self.line,
            self.column,
        )
        self.advance()
        return token

    def peek(self, n: int = 1):
        """
        向后看 n 个字符

        当 n > 1 时,返回 n 个字符的切片
        """
        peek_pos = self.pos + n
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[self.pos + 1 : peek_pos + 1]

    def get_number(self, accept_float=True, accept_bit=False, accept_hex=False, end_chars: str = "p") -> Token:
        """
         <digit> ::= [0-9]
        <digits> ::= <digit>*
        <number> ::= <digits>(.<digits>)?(E|e[+-]?<digits>)?

        @accept_float: 允许小数和科学计数法
        @accept_hex  : 允许16进制表示 0xfff
        @accept_bit  : 允许二进制表示 0b111
        """
        bit_matching_status = False
        hex_matching_status = False

        def is_match_char(char: str) -> bool:
            if hex_matching_status:
                return bool(re.match(r"[0-9a-fA-F]", char))
            elif bit_matching_status:
                return bool(re.match(r"[01]", char))
            else:
                return bool(re.match(r"[0-9_]", char))

        result = ""

        if self.current_char == "0":
            result += self.current_char
            self.advance()
            if accept_bit and self.current_char in ("b", "B"):
                result += self.current_char
                self.advance()
                result += self.current_char
                self.advance()
                bit_matching_status = True
            elif accept_hex and self.current_char in ("x", "X"):
                result += self.current_char
                self.advance()
                result += self.current_char
                self.advance()
                hex_matching_status = True

        # <digits>
        while self.current_char is not None and is_match_char(self.current_char):
            result += self.current_char
            self.advance()

        if accept_float:
            # (.<digits>)?
            if self.current_char == "." and self.peek() != ".":
                result += self.current_char
                self.advance()
                while self.current_char is not None and is_match_char(self.current_char):
                    result += self.current_char
                    self.advance()

            # (E|e[+-]?<digits>)?
            if self.current_char == "e" or self.current_char == "E":
                result += self.current_char
                self.advance()
                if self.current_char in (TokenType.MINUS.value, TokenType.PLUS.value):
                    result += self.current_char
                    self.advance()
                while self.current_char is not None and is_match_char(self.current_char):
                    result += self.current_char
                    self.advance()

        while self.current_char is not None and self.current_char in end_chars:
            result += self.current_char
            self.advance()
        # column - 1, 因为判断结束需要跳出 number
        return Token(TokenType.NUMBER, result, self.line, self.column - 1)

    def get_string(self):
        """
        严格双引号 ""
        """
        result = self.current_char
        if result != TokenType.QUOTO.value:
            token = Token(TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token, 'should be strict "')
        end_character = TokenType.QUOTO.value
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            result += self.current_char
            if self.current_char == "\\":
                self.advance()
                if self.current_char is None:
                    self.error()
                result += self.current_char
            self.advance()

        result += end_character
        token = Token(TokenType.STRING, result, self.line, self.column)
        self.advance()
        return token

    def get_str(self):
        """
        匹配 "" 和 '' 之间的字符
        """
        result = self.current_char
        if result not in ("'", '"'):
            token = Token(TokenType.STRING, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token, "should be ' or \"")
        end_character = self.current_char  # 结束标志一定是和开始标志相同的
        self.advance()

        while self.current_char is not None and self.current_char != end_character:
            if self.current_char == "\\":
                result += self.current_char
                self.advance()
                if self.current_char is None:
                    self.error(
                        ErrorCode.UNEXPECTED_TOKEN,
                        Token(TokenType.STRING, result, self.line, self.column - 1),
                    )
                # 对于 '\' 和 "\" 直接结束
                # print(self.current_char)
                if self.current_char == end_character and self.peek() in (" ", "\n"):
                    break
            result += self.current_char
            self.advance()

        result += end_character
        token = Token(TokenType.STR, result, self.line, self.column)
        self.advance()
        return token

    def get_char(self):
        """
        单字符
        """
        result = self.current_char
        if result != "'":
            token = Token(TokenType.CHARACTER, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token, "should be a single character")

        self.advance()
        result += self.current_char
        self.advance()
        if self.current_char != "'":
            token = Token(TokenType.CHARACTER, result, self.line, self.column)
            self.advance()
            self.error(ErrorCode.UNEXPECTED_TOKEN, token, "should be a single character")

        result += self.current_char
        token = Token(TokenType.CHARACTER, result, self.line, self.column)
        self.advance()
        return token

    def get_extend_str(self, extend_symbol_pair: Tuple[str, str], token_type: Enum = TokenType.STR):
        """
        扩展匹配字符串, 比如 """ """ 和 ''' '''
        """
        start_symbol, end_symbol = extend_symbol_pair
        assert len(start_symbol) > 0 and len(end_symbol) > 0
        assert self.current_char == start_symbol[0]
        if len(start_symbol) > 1:
            assert self.peek(len(start_symbol) - 1) == start_symbol[1:]

        result = start_symbol
        for _ in range(len(start_symbol)):
            self.advance()

        end_symbol_length = len(end_symbol)
        while self.current_char is not None:
            if self.current_char == end_symbol[0] and self.peek(end_symbol_length - 1) == end_symbol[1:]:
                break
            else:
                if self.current_char == "\\":
                    result += self.current_char
                    self.advance()
                result += self.current_char
                self.advance()

        if self.current_char is None:
            token = Token(token_type, result, self.line, self.column - 1)
        else:
            result += end_symbol
            for _ in range(end_symbol_length):
                self.advance()
            token = Token(token_type, result, self.line, self.column - 1)

        return token

    def get_id(self, ignore_case=False, extend_chars: List[str] = ["_"]):
        """
        获取标识符, 留给后续的语法分析处理
        @ignore_case : 是否忽略大小写
        @extend_chars: 扩展字符, 默认扩展 "_", 一般还可修改为 ["_", "-"]

        <letter> ::= [A-Za-z]
         <digit> ::= [0-9]
            <id> ::= (<letter>|_)(<letter>|_|<digit>)*

        此函数应次于 get_number 调用
        """
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in extend_chars):
            result += self.current_char
            self.advance()

        # 忽略关键字的大小写
        if ignore_case:
            token_type = next(
                (self.reserved_keywords[item] for item in self.reserved_keywords if item.lower() == result.lower()),
                None,
            )
            # token_type = self.reserved_keywords.get(result.upper())
        else:
            token_type = self.reserved_keywords.get(result)

        if token_type is None:
            token = Token(type=TokenType.ID, value=result, line=self.line, column=self.column - 1)
        else:
            # 作为保留关键字
            token = Token(type=token_type, value=result, line=self.line, column=self.column - 1)
        return token

    def get_comment(self, start_symbol="#", end_symbol="\n"):
        """
        跳过注释部分, 多个注释的情况需要分多个 get_comment 函数处理

        单行注释不包含结尾的 \n

        python 风格: ("#", "\n")
             C 风格: ("//", "\n"), ("/*", "*/")
        pascal 风格: ("//", "\n"), ("{", "}"), ("(*", "*)")
        """

        assert start_symbol[0] == self.current_char

        result = start_symbol
        for _ in range(len(start_symbol)):
            self.advance()

        end_symbol_length = len(end_symbol)
        while self.current_char is not None:
            if self.current_char == end_symbol[0]:
                if end_symbol_length == 1:
                    # 单行注释不包括最后的换行
                    result += self.current_char
                    break
                elif self.peek(end_symbol_length - 1) == end_symbol[1:]:
                    result += self.current_char
                    for _ in range(end_symbol_length - 1):
                        self.advance()
                        result += self.current_char
                    break
            result += self.current_char
            self.advance()

        # 除单行注释外抛异常
        if self.current_char is None and end_symbol != "\n":
            token = Token(TokenType.COMMENT, result, self.line, self.column - 1)
            self.error(ErrorCode.UNTERMINATED_COMMENT, token)

        # 对于单行注释以 \n 为终止符的, 将最后一个 \n 去掉
        if end_symbol == "\n" and result[-1] == "\n":
            result = result[:-1]
            token = Token(TokenType.COMMENT, result, self.line, self.column - 1)
        else:
            token = Token(TokenType.COMMENT, result, self.line, self.column)
            self.advance()
        return token

    def get_long_op(self):
        """
        匹配一个长运算符

        需要使用 build_long_op_dict 函数设置所有支持的长运算符

        默认的一些常用长运算符见 TokenType, 也可以自定义新的长运算符
        """
        assert self.current_char in self.long_op_dict
        token_type = TokenType(self.current_char)
        result = self.current_char

        for long_op in self.long_op_dict[self.current_char]:
            if self.peek(len(long_op)) == long_op:
                result = self.current_char + long_op
                # 优先尝试用户自定义的长运算符
                try:
                    token_type = self.LanguageTokenType(result)
                except:
                    token_type = TokenType(result)
                for _ in range(len(long_op)):
                    self.advance()
                break

        token = Token(token_type, result, self.line, self.column)
        self.advance()
        return token

    def get_next_token(self) -> Token:
        """
        while self.current_char is not None:
            if self.current_char == TokenType.SPACE.value:
                return self.skip_whitespace()

            if self.current_char in self.invisible_characters:
                return self.skip_invisiable_character()

            # your code

            try:
                token_type = TokenType(self.current_char)
            except ValueError:  # pragma: no cover
                token = Token(TokenType.TEXT, self.current_char, self.line, self.column)
                self.advance()
                return token
            else:
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    line=self.line,
                    column=self.column,
                )
                self.advance()
                return token

        # End of File
        return Token(type=TokenType.EOF, value="EOF", line=self.line, column=self.column)
        """
        raise NotImplementedError

