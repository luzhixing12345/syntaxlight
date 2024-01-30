from .ast import AST, NodeVisitor, String, Identifier
from typing import List
from enum import Enum

class Rust(AST):
    
    def __init__(self) -> None:
        super().__init__()
        
        
class InnerAttr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.meta_item = None
        
class OuterAttr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.meta_item = None
        
class MetaItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ident = None
        self.lit = None
        
class ItemWithAttrs(AST):
    def __init__(self) -> None:
        super().__init__()
        self.attrs_and_vis = None
        self.item = None
        
class AttrsAndVis(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.item_with_attrs = None