import os
from .lexers import *
from .parsers import *
from .error import Error, ttyinfo
from .language import guess_language, SUPPORTED_SYNTAX, show_help_info, clean_language
from .asts.ast import display_ast
import traceback
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class ParseResult:
    success: bool  # 是否解析成功
    parser: Parser  # 解析器
    error: Error  # 错误信息(如果有)


def parse(text: str, language=None, file_path=None) -> ParseResult:
    """
    解析文本, 高亮代码段

    :param text: 待解析的文本
    :param language: 代码语言, 默认为 None
    :param file_path: 文件路径, 默认为 None
    :param save_ast_tree: 是否保存抽象语法树, 默认为 False
    :param highlight_lines: 要高亮的代码段的行号, 默认为空列表
    :param highlight_tokens: 要高亮的代码段的 token 号, 默认为空列表
    :return: 返回一个 ParseResult 对象, 包含解析结果和错误信息
    """
    if len(text) == 0:
        text = " "
    language = clean_language(language)
    parser = get_parser(text, language)
    parser.lexer.file_path = file_path

    exception: Optional[Error] = None
    try:
        parser.parse()
    except Error as e:
        exception = e
        # 失败后将剩余部分也解析
        while parser.current_token.type != TokenType.EOF:
            parser.eat()
    except Exception as e:
        exception = Error()
        exception.self_error_info = f'  {ttyinfo("Parse running error")}: {e}\n'
        if file_path:
            exception.self_error_info += f'  {ttyinfo("File path")}: {file_path}\n'
        exception.self_error_info += traceback.format_exc()
        # 失败后将剩余部分也解析
        while parser.current_token.type != TokenType.EOF:
            parser.eat()
    finally:
        # if save_ast_tree:
        #     display_ast(parser.root, parser.sub_roots)
        # print(parser.node)
        return ParseResult(success=exception is None, parser=parser, error=exception)


def parse_file(file_path: str, language=None) -> ParseResult:
    if not os.path.exists(file_path):
        print(f"{file_path} file not exsist")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if language is None:
        language = guess_language(file_path)
    else:
        language = clean_language(language)

    return parse(text, language=language, file_path=file_path)


def get_tokens(lexer: Lexer):
    token = lexer.get_next_token()
    tokens = [token]
    while token.type != TokenType.EOF:
        try:
            token = lexer.get_next_token()
            tokens.append(token)
        except Error as e:
            print(e.message)
    return tokens


def get_lexer(text: str, language: str = None) -> Lexer:
    """
    @code_or_path: 代码或者文件的路径
    @lanaguge: 选择的语言, 如果第一个参数为文件路径则不需要传入 language
    """
    if language not in SUPPORTED_SYNTAX:
        print("lexer not support")
        show_help_info()
        exit(1)
    return SUPPORTED_SYNTAX[language]["lexer"](text)


def get_parser(text: str, language: str = None) -> Parser:
    lexer = get_lexer(text, language)
    parser = SUPPORTED_SYNTAX[language]["parser"](lexer)
    return parser
