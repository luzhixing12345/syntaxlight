import os
from .lexers import *
from .error import Error
from .parsers import *
from .ast import display_ast
import sys


SUPPORTED_SYNTAX = {
    "json": {"lexer": JsonLexer, "parser": JsonParser, "suffix": ["json"]},
    "c": {"lexer": CLexer, "parser": CParser, "suffix": ["c", "h"]},
    "lua": {"lexer": LuaLexer, "parser": LuaParser, "suffix": ["lua"]},
    "bnf": {"lexer": BNFLexer, "parser": BNFParser, "suffix": ["bnf"]},
    "makefile": {"lexer": None, "parser": None, "suffix": ["Makefile", "mk", "mak", "makefile"]},
    "java": {"lexer": None, "parser": None, "suffix": ["java"]},
    "rust": {"lexer": None, "parser": None, "suffix": ["rs"]},
    "javascript": {"lexer": None, "parser": None, "suffix": ["js"]},
    "typescript": {"lexer": None, "parser": None, "suffix": ["ts", "tsx", "tsc"]},
    "pascal": {"lexer": None, "parser": None, "suffix": ["pas"]},
    "toml": {"lexer": TomlLexer, "parser": TomlParser, "suffix": ["toml"]},
    "xml": {"lexer": XmlLexer, "parser": XmlParser, "suffix": ["xml"]},
    "shell": {"lexer": ShellLexer, "parser": ShellParser, "suffix": ["sh"]},
}


def parse(
    text: str, language=None, file_path=None, show_error_context=True, save_ast_tree=False
) -> str:
    if len(text) == 0:
        return ""

    parser = get_parser(text, language)
    parser.lexer.file_path = file_path

    try:
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

    return parse(
        text,
        language=language,
        file_path=file_path,
        show_error_context=show_error_context,
        save_ast_tree=save_ast_tree,
    )


def guess_language(file_path: str) -> str:
    """
    通过文件名猜测文法类型
    """
    suffix_name = file_path.split(os.sep)[-1].split(".")[-1]
    for language in SUPPORTED_SYNTAX:
        if suffix_name in SUPPORTED_SYNTAX[language]["suffix"]:
            return language

    if suffix_name in SUPPORTED_SYNTAX:
        return suffix_name

    print("fail to guess language")
    show_help_info()
    exit(1)


def show_help_info():
    print(f"supported language:")
    for language in SUPPORTED_SYNTAX:
        print(f"{language:>10}:", SUPPORTED_SYNTAX[language]["suffix"])
    exit(1)


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

    return code, language
