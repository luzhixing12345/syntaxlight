import os
from .lexers import *
from .parsers import *
from typing import List, TypedDict

class SyntaxDict(TypedDict):
    lexer: Lexer
    parser: Parser
    suffix: List[str]

SUPPORTED_SYNTAX = {
    "json": SyntaxDict(lexer=JsonLexer, parser=JsonParser, suffix=['json']),
    "c": SyntaxDict(lexer=CLexer, parser=CParser, suffix=["c", "h"]),
    "lua": SyntaxDict(lexer=LuaLexer, parser=LuaParser, suffix=['lua']),
    "bnf": SyntaxDict(lexer=BNFLexer, parser=BNFParser, suffix=['bnf']),
    "toml": SyntaxDict(lexer=TomlLexer, parser=TomlParser, suffix=['toml']),
    "xml": SyntaxDict(lexer=XmlLexer, parser=XmlParser, suffix=['xml']),
    "shell": SyntaxDict(lexer=ShellLexer, parser=ShellParser, suffix=['sh']),
}

def clean_language(language:str):
    
    language = language.lower()
    rename_languages = {
        'bash': 'shell'
    }
    for r_language in rename_languages:
        if language == r_language:
            return rename_languages[r_language]
        
    return language

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

def is_language_support(language: str):
    """
    检验 syntaxlight 是否支持当前语言
    """
    language = clean_language(language)
    global SUPPORTED_SYNTAX
    return language in SUPPORTED_SYNTAX