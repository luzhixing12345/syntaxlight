import os
from .lexers import *
from .parsers import *
import re
from typing import List, TypedDict


class SyntaxDict(TypedDict):
    lexer: Lexer
    parser: Parser
    suffix: List[str]


SUPPORTED_SYNTAX = {
    "json": SyntaxDict(lexer=JsonLexer, parser=JsonParser, suffix=["json"]),
    "c": SyntaxDict(lexer=CLexer, parser=CParser, suffix=["c", "h"]),
    "lua": SyntaxDict(lexer=LuaLexer, parser=LuaParser, suffix=["lua"]),
    "bnf": SyntaxDict(lexer=BNFLexer, parser=BNFParser, suffix=["bnf"]),
    "toml": SyntaxDict(lexer=TomlLexer, parser=TomlParser, suffix=["toml"]),
    "xml": SyntaxDict(lexer=XmlLexer, parser=XmlParser, suffix=["xml"]),
    "shell": SyntaxDict(lexer=ShellLexer, parser=ShellParser, suffix=["sh"]),
    "x86asm": SyntaxDict(lexer=X86AssemblyLexer, parser=X86AssemblyParser, suffix=["asm"]),
    "riscvasm": SyntaxDict(lexer=RISCVAssemblyLexer, parser=RISCVAssmemblyParser, suffix=["S"]),
    "css": SyntaxDict(lexer=CSSLexer, parser=CSSParser, suffix=["css"]),
    "makefile": SyntaxDict(lexer=MakefileLexer, parser=MakefileParser, suffix=["mk", "mak"]),
    "dot": SyntaxDict(lexer=DotLexer, parser=DotParser, suffix=["dot", "gv"]),
    "yaml": SyntaxDict(lexer=YamlLexer, parser=YamlParser, suffix=["yml", "yaml"]),
    "python": SyntaxDict(lexer=PythonLexer, parser=PythonParser, suffix=["py"]),
    "txt": SyntaxDict(lexer=TxtLexer, parser=TxtParser, suffix=["txt"]),
    "verilog": SyntaxDict(lexer=VerilogLexer, parser=VerilogParser, suffix=["v"]),
    "rust": SyntaxDict(lexer=RustLexer, parser=RustParser, suffix=["rs"]),
    "diff": SyntaxDict(lexer=DiffLexer, parser=DiffParser, suffix=["diff"]),
}

supported_languages = list(SUPPORTED_SYNTAX.keys())


def clean_language(language: str):
    language = language.lower()
    rename_languages = {
        r"^bash$": "shell",
        r"^sh$": "shell",
    }
    for r_language in rename_languages:
        if bool(re.match(r_language, language)):
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
