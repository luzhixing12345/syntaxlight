import os
from .lexers import *
from .parsers import *
from .error import Error
from .language import guess_language, SUPPORTED_SYNTAX, show_help_info, clean_language
from .ast import display_ast
import sys


def parse(
    text: str, language=None, file_path=None, show_error_context=True, save_ast_tree=False
) -> str:
    if len(text) == 0:
        return ""
    language = clean_language(language)
    
    try:
        parser = get_parser(text, language)
        parser.lexer.file_path = file_path
        parser.parse()
    except Error as e:
        sys.stderr.write(e.message)
        if show_error_context:
            sys.stderr.write(e.context)
    else:
        display_ast(parser.root, parser.sub_roots, save_ast_tree=save_ast_tree)
        # print(parser.node)
        return parser.to_html()


def parse_file(file_path: str, language=None, show_error_context=True, save_ast_tree=False) -> str:
    if not os.path.exists(file_path):
        print(f"{file_path} file not exsist")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if language is None:
        language = guess_language(file_path)
    else:
        language = clean_language(language)

    return parse(
        text,
        language=language,
        file_path=file_path,
        show_error_context=show_error_context,
        save_ast_tree=save_ast_tree,
    )


def get_tokens(lexer: Lexer):
    token = lexer.get_next_token()
    tokens = [token]
    while token.type.value != "EOF":
        try:
            token = lexer.get_next_token()
            tokens.append(token)
        except Error as e:
            print(e.message)
            print(e.context)
    return tokens


def get_lexer(code_or_path: str, language: str = None) -> Lexer:
    """
    @code_or_path: 代码或者文件的路径
    @lanaguge: 选择的语言, 如果第一个参数为文件路径则不需要传入 language
    """
    code, language = _preprocess(code_or_path, language)
    if language not in SUPPORTED_SYNTAX:
        print("lexer not support")
        show_help_info()
        exit(1)
    return SUPPORTED_SYNTAX[language]["lexer"](code)


def get_parser(code_or_path: str, language: str = None) -> Parser:
    code, language = _preprocess(code_or_path, language)
    lexer = get_lexer(code, language)
    parser = SUPPORTED_SYNTAX[language]["parser"](lexer)
    return parser


def _preprocess(code_or_path: str, language: str = None):
    if os.path.exists(code_or_path):
        with open(code_or_path, "r", encoding="utf-8") as f:
            code = f.read()

        if language is None:
            language = guess_language(code_or_path)
    else:
        code = code_or_path

    language = clean_language(language)
    return code, language
