

from .lexers import *

def parse(text: str, language: str = 'guess') -> str:
    ...

def get_lexer(code:str, language:str) -> Lexer:

    language = language.lower()

    lexers = {
        'c': CLexer,
        'lua': LuaLexer,
        'json': JsonLexer
    }

    return lexers[language](code)
