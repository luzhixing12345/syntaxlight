import os
from .lexers import *
from .error import Error
from .parsers import *
from .ast import display_ast
import sys


def parse(text: str, language: str = "guess", file_path=None, show_error_context=True, save_ast_tree = False) -> str:
    assert type(text) == str
    assert type(language) == str

    if len(text) == 0:
        return ""

    language = language.lower()
    lexer = get_lexer(text, language)
    if file_path is not None:
        lexer.file_path = file_path
    parser = get_parser(lexer)

    try:
        parser.parse()
    except Error as e:
        sys.stderr.write(e.message)
        if show_error_context:
            sys.stderr.write(e.context)
    else:
        display_ast(parser.node, save_ast_tree = save_ast_tree)
        # print(parser.node)
        return parser.to_html()


def parse_file(
    file_path: str, language: str = "guess", show_error_context=True, save_ast_tree=False
) -> str:
    if not os.path.exists(file_path):
        print(f"{file_path} file not exsist")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if language == "guess":
        language = guess_language(file_path)
        if language is None:
            print(f"unknown syntax {file_path}")
            exit(1)

    return parse(
        text,
        language,
        file_path=file_path,
        show_error_context=show_error_context,
        save_ast_tree=save_ast_tree,
    )


def guess_language(file_path: str) -> str:
    '''
    通过文件名猜测文法类型
    '''
    file_name = file_path.split(os.sep)[-1]

    languages = {
        "json": ["json"],
        "c": ["c", "h"],
        "lua": ["lua"],
        "bnf": ["bnf"],
        "Makefile": ["Makefile", "mk", "mak"],
        "java": ["java"],
        "rust": ["rs"],
        "javascript": ["js"],
        "typescript": ["ts", "tsx", "tsc"],
        "pascal": ["pas"],
        "toml": ["toml"],
        "xml": ["xml"],
        "shell": ["sh"],
        "bnf": ["bnf"]
    }

    if "." in file_name:
        suffix = file_name.split(".")[-1]
        for language, suffix_names in languages.items():
            if suffix in suffix_names:
                return language
        file_name = file_name.split(".")[:-1]

    for language, suffix_names in languages.items():
        if file_name in suffix_names:
            return language

    return None


def get_tokens(lexer: Lexer):
    token = lexer.get_next_token()
    tokens = [token]
    while token.type.value != "EOF":
        # if token.type.value == 'ID':
        # print(token)
        # print(token)
        try:
            token = lexer.get_next_token()
            tokens.append(token)
        except Error as e:
            print(e.message)
            print(e.context)
    return tokens


def get_lexer(code: str, language: str) -> Lexer:
    language = language.lower()

    lexers = {
        "c": CLexer,
        "lua": LuaLexer,
        "json": JsonLexer,
        "ebnf": EBNFLexer,
        "toml": TomlLexer,
        "xml": XmlLexer,
        "shell": ShellLexer,
        "bnf": BNFLexer
    }

    lexer_class = lexers.get(language, None)
    if lexer_class is None:
        print("unknown language type: ", language)
        exit(1)

    return lexers[language](code)


def get_parser(lexer: Lexer) -> Parser:
    parsers = {
        "json": JsonParser,
        "toml": TomlParser,
        "c": CParser,
        "xml": XmlParser,
        "shell": ShellParser,
        "bnf": BNFParser
    }

    syntax_type = lexer.__class__.__name__.replace("Lexer", "").lower()
    parser_class = parsers.get(syntax_type, None)

    if parser_class is None:
        print("unknown lexer type: ", lexer.__class__.__name__)
        exit(1)

    return parsers[syntax_type](lexer)
