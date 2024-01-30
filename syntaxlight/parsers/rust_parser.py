
from .parser import Parser
from ..lexers import TokenType, RustTokenSet, RustTokenType
from ..error import ErrorCode
from ..asts.rust_ast import *

class RustParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.rust_first_set = RustTokenSet()
        
    def parse(self):
        '''
        rustFile ::= inner_attr* item_with_attrs *
        '''
        self.root = self.rustFiles()
        return self.root
    
    def rustFiles(self):
        
        node = Rust()
        inner_attrs = []
        while self.current_token.type in self.rust_first_set.inner_attr:
            inner_attrs.append(self.inner_attr())
        node.update(inner_attrs=inner_attrs)
        
        item_with_attrs = []
        while self.current_token.type in self.rust_first_set.item_with_attrs:
            item_with_attrs.append(self.item_with_attrs())
        node.update(item=item_with_attrs)
        return node
    
    def inner_attr(self):
        '''
        inner_attr ::= '#!' '[' meta_item ']'
        '''
        node = InnerAttr()
        node.register_token(self.eat(RustTokenType.HASH_BANG))
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(meta_item=self.meta_item())
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node
    
    def outer_attrs(self):
        '''
        outer_attrs ::= outer_attr *
        '''
        outer_attrs = []
        while self.current_token.type in self.rust_first_set.outer_attr:
            outer_attrs.append(self.outer_attr())
        return outer_attrs
    
    def outer_attr(self):
        '''
        outer_attr ::= '#' '[' meta_item ']
        '''
        node = OuterAttr()
        node.register_token(self.eat(TokenType.HASH))
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(meta_item=self.meta_item())
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node
    
    def meta_item(self):
        '''
        meta_item ::= ident '=' lit 
                    | ident '(' <<comma_separated_list meta_item>> ')'
                    | ident
        '''
        # TODO
        node = MetaItem()
        node.update(ident=self.get_identifier())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(lit=self.lit())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(meta_items=self.comma_separated_list(self.meta_item))
            node.register_token(self.eat(TokenType.RPAREN))
        return node
    
    def item_with_attrs(self):
        '''
        item_with_attrs ::= attrs_and_vis item
        '''
        node = ItemWithAttrs()
        node.update(attrs_and_vis=self.attrs_and_vis())
        node.update(item=self.item())
        return node
    
    def attrs_and_vis(self):
        '''
        attrs_and_vis ::= outer_attrs [visibility]
        '''
        node = AttrsAndVis()
        node.update(outer_attrs=self.outer_attrs())
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        return node
    
    def private_item(self):
        '''
        private_item ::= stmt_item
                       | use_item 
                       | extern_crate_item
        '''
        if self.current_token.type in self.rust_first_set.stmt_item:
            return self.stmt_item()
        elif self.current_token.type in self.rust_first_set.use_item:
            return self.use_item()
        elif self.current_token.type in self.rust_first_set.extern_crate_item:
            return self.extern_crate_item()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be stmt_item or use_item or extern_crate_item")