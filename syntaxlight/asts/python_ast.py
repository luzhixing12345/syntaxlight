from .ast import AST, Identifier, Keyword, Punctuator
from typing import List, Union, Optional

class Python(AST):
    def __init__(self) -> None:
        super().__init__()