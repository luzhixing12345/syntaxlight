import os
from .lexers import *
from .parsers import *
from .error import Error, ttyinfo
from .language import guess_language, SUPPORTED_SYNTAX, show_help_info, clean_language
from .asts.ast import display_ast
import sys
import traceback
from typing import Tuple, Optional


def parse(text: str, language=None, file_path=None, save_ast_tree=False) -> Tuple[str, Optional[Error]]:
    """
    解析文本, 高亮代码段

    return: (html, error)
    html: html 格式的代码段, 无论是否有错误, 都会返回; 错误位置会用红色标记, 其后面的代码段会被默认高亮
    error: 异常信息, 无错误时为 None, 有错误时为异常对象(Error), 可以打印错误信息
    """
    if len(text) == 0:
        return "", None
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
        if save_ast_tree:
            display_ast(parser.root, parser.sub_roots)
        # print(parser.node)
        return parser.to_html(), exception


def parse_file(file_path: str, language=None, save_ast_tree=False) -> Tuple[str, bool]:
    if not os.path.exists(file_path):
        print(f"{file_path} file not exsist")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if language is None:
        language = guess_language(file_path)
    else:
        language = clean_language(language)

    return parse(text, language=language, file_path=file_path, save_ast_tree=save_ast_tree)


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
