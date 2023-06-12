import os
from .lexers import *
from .error import *

def parse(text: str, language: str = 'guess') -> str:
    
    assert type(text) == str
    assert type(language) == str

    language = language.lower()
    lexer = get_lexer(text, language)
    tokens = get_tokens(lexer)
    # print(tokens)

def parse_file(file_path: str, language: str = 'guess') -> str:
    
    if not os.path.exists(file_path):
        print(f"{file_path} 文件不存在")

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    if language == 'guess':
        language = guess_language(file_path)
        if language is None:
            print(f"未知文法类型 {file_path}")
            exit(1)

    parse(text, language)


def guess_language(file_path:str) -> str:

    file_name = file_path.split(os.sep)[-1]
    
    languages = {
        'c': ['c','h'],
        'lua': ['lua'],
        'bnf': ['bnf'],
        'Makefile': ['Makefile', 'mk','mak'],
        'java': ['java'],
        'rust': ['rs'],
        'javascript': ['js'],
        'typescript': ['ts','tsx','tsc']
    }

    if '.' in file_name:
        suffix = file_name.split('.')[-1]
        for language, suffix_names in languages.items():
            if suffix in suffix_names:
                return language
        file_name = file_name.split('.')[:-1]

    for language, suffix_names in languages.items():
        if file_name in suffix_names:
            return language
        
    return None

        

def get_tokens(lexer: Lexer):

    tokens = []

    token = lexer.get_next_token()
    while token.type.value != 'EOF':
        # if token.type.value == 'NUMBER':
        #     print(token)
        try:
            token = lexer.get_next_token()
            tokens.append(token)
        except Exception as e:
            e:Error
            print(e.message)

    return tokens


def get_lexer(code:str, language:str) -> Lexer:

    language = language.lower()

    lexers = {
        'c': CLexer,
        'lua': LuaLexer,
        'json': JsonLexer
    }

    lexer_class = lexers.get(language, None)
    if lexer_class is None:
        print("未知文法")
        exit(1)

    return lexers[language](code)
