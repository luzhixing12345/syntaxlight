import re
from .parser import Parser
from ..lexers import TokenType, RustTokenSet, RustTokenType
from ..error import ErrorCode
from ..asts.rust_ast import *
from ..asts.ast import add_ast_type, Token, String
from ..gdt import CSS, GlobalDescriptorTable
from enum import Enum

# 默认预导入的 rust 的标准库
DEFAULT_RUST_LIB = [
    ("std", CSS.IMPORT_LIBNAME),
    ("core", CSS.IMPORT_LIBNAME),
    ("String", CSS.IMPORT_LIBNAME),
    ("Vec", CSS.IMPORT_LIBNAME),
    ("HashMap", CSS.IMPORT_LIBNAME),
    ("HashSet", CSS.IMPORT_LIBNAME),
    ("bool", CSS.IMPORT_LIBNAME),
    ("char", CSS.IMPORT_LIBNAME),
    ("u8", CSS.IMPORT_LIBNAME),
    ("u16", CSS.IMPORT_LIBNAME),
    ("u32", CSS.IMPORT_LIBNAME),
    ("u64", CSS.IMPORT_LIBNAME),
    ("u128", CSS.IMPORT_LIBNAME),
    ("i8", CSS.IMPORT_LIBNAME),
    ("i16", CSS.IMPORT_LIBNAME),
    ("i32", CSS.IMPORT_LIBNAME),
    ("i64", CSS.IMPORT_LIBNAME),
    ("i128", CSS.IMPORT_LIBNAME),
    ("f32", CSS.IMPORT_LIBNAME),
    ("f64", CSS.IMPORT_LIBNAME),
    ("isize", CSS.IMPORT_LIBNAME),
    ("usize", CSS.IMPORT_LIBNAME),
    ("str", CSS.IMPORT_LIBNAME),
    ("tuple", CSS.IMPORT_LIBNAME),
    ("Some", CSS.IMPORT_LIBNAME),
    ("None", CSS.IMPORT_LIBNAME),
    ("NAN", CSS.ENUM_ID),
    ("Ok", CSS.ENUM_ID),
    ("Err", CSS.ENUM_ID),
]

GDT = GlobalDescriptorTable(DEFAULT_RUST_LIB)


class RustCSS(Enum):
    MUTABLE_VAR = "MutableVar"  # 可变变量
    MUTABLE_SELF = "MutableSelf"  # 可变 self
    MUTABLE_FUNCTION = "MutableFunction"  # 可变函数
    MUTABLE_ARG = "MutableArg"  # 可变参数名
    MUTABLE_OP = "MutableOp"  # 可变操作符
    GENERIC_TYPE = "GenericType"  # 泛型
    TYPE_BOUND = "TypeBound"  # 类型约束
    ATTRIBUTE = "Attribute"  # meta 属性
    TRAIT_NAME = "TraitName"  # trait 名称
    LABEL = "Label"  # 标签


class RustParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.rust_first_set = RustTokenSet()

        self.binary_op_set = [
            # 基础
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.DIV,
            TokenType.MOD,
            TokenType.SHL,
            TokenType.SHR,
            TokenType.PIPE,
            TokenType.AMPERSAND,
            TokenType.ASSIGN,
            # assign
            TokenType.ADD_ASSIGN,
            TokenType.SUB_ASSIGN,
            TokenType.MUL_ASSIGN,
            TokenType.DIV_ASSIGN,
            TokenType.MOD_ASSIGN,
            TokenType.SHL_ASSIGN,
            TokenType.SHR_ASSIGN,
            TokenType.AND_ASSIGN,
            TokenType.OR_ASSIGN,
            # binop
            TokenType.EQ,
            TokenType.NE,
            TokenType.LANGLE_BRACE,
            TokenType.LE,
            TokenType.RANGLE_BRACE,
            TokenType.GE,
            TokenType.CARET,
            TokenType.OR,
            TokenType.AND,
            TokenType.CONCAT,
        ]

    def parse(self):
        self.root = self.rustFiles()
        GDT.reset()
        return self.root

    def rustFiles(self):
        """
        rustFile ::= inner_attr* item_with_attrs*
        """
        node = Rust()
        inner_attrs = []
        while self.current_token.type in self.rust_first_set.inner_attr:
            inner_attrs.append(self.inner_attr())
        node.update(inner_attrs=inner_attrs)

        item_with_attrs = []
        while self.current_token.type in self.rust_first_set.item_with_attrs:
            item_with_attrs.append(self.item_with_attrs())
        node.update(item=item_with_attrs)

        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return node

    def inner_attr(self):
        """
        inner_attr ::= '#!' '[' meta_item ']'
        """
        node = InnerAttr()
        node.register_token(self.eat(RustTokenType.HASH_BANG))
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(meta_item=self.meta_item())
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def outer_attrs(self):
        """
        outer_attrs ::= outer_attr *
        """
        outer_attrs = []
        while self.current_token.type in self.rust_first_set.outer_attr:
            outer_attrs.append(self.outer_attr())
        return outer_attrs

    def outer_attr(self):
        """
        outer_attr ::= '#' '[' meta_item ']
        """
        node = OuterAttr()
        node.register_token(self.eat(TokenType.HASH))
        node.register_token(self.eat(TokenType.LSQUAR_PAREN))
        node.update(meta_item=self.meta_item())
        node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        return node

    def meta_item(self):
        """
        meta_item ::= ident '=' lit
                    | ident '(' <<comma_separated_list meta_item>> ')'
                    | ident
        """
        node = MetaItem()
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(lit=self.lit())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(meta_items=self.list_items(self.meta_item, trailing_set=[TokenType.ID]))
            node.register_token(self.eat(TokenType.RPAREN))
            add_ast_type(node.id, RustCSS.ATTRIBUTE)
        else:
            # 递归到根节点
            add_ast_type(node.id, RustCSS.TRAIT_NAME)
        return node

    def item_with_attrs(self):
        """
        item_with_attrs ::= attrs_and_vis item
        """
        node = ItemWithAttrs()
        node.update(attrs_and_vis=self.attrs_and_vis())
        node.update(item=self.item())
        return node

    def attrs_and_vis(self):
        """
        attrs_and_vis ::= outer_attrs [visibility]
        """
        node = AttrsAndVis()
        node.update(outer_attrs=self.outer_attrs())
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        return node

    def visibility(self):
        """
        visibility ::= 'pub' ("(" crate ")")?
        """
        node = Visibility()
        node.update(pub=self.get_keyword(token_type=RustTokenType.PUB))
        if self.current_token.type == TokenType.LPAREN and self.peek_next_token().type == RustTokenType.CRATE:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(crate=self.get_keyword(token_type=RustTokenType.CRATE))
            node.register_token(self.eat(TokenType.RPAREN))
        return node

    def item(self):
        """
        private_item ::= stmt_item
                       | use_item
                       | extern_crate_item
        """
        if self.current_token.type == RustTokenType.EXTERN and self.peek_next_token().type == RustTokenType.CRATE:
            return self.extern_crate_item()
        elif self.current_token.type in self.rust_first_set.stmt_item:
            return self.stmt_item()
        elif self.current_token.type == RustTokenType.USE:
            return self.use_item()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be stmt_item or use_item or extern_crate_item")

    def stmt_item(self):
        """
        stmt_item ::= static_item
                    | const_item
                    | type_item
                    | block_item
                    | use_item
                    | let_item
        """
        if self.current_token.type == RustTokenType.STATIC:
            return self.static_item()
        elif self.current_token.type == RustTokenType.CONST:
            return self.const_item()
        elif self.current_token.type == RustTokenType.TYPE:
            return self.type_item()
        elif self.current_token.type in self.rust_first_set.block_item:
            return self.block_item()
        elif self.current_token.type == RustTokenType.USE:
            return self.use_item()
        elif self.current_token.type == RustTokenType.LET:
            return self.let_item()
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN, message="should be static_item or const_item or type_item or block_item"
            )

    def use_item(self):
        """
        use_item ::= use path_glob ';'
        """
        node = UseItem()
        node.update(use=self.get_keyword(token_type=RustTokenType.USE))
        node.update(path_glob=self.path_glob())
        # 将 path_glob 的最后一个 id 注册到 GDT 中
        node.path_glob.register_gdt(GDT)
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def path_glob(self):
        """
        path_glob ::= path_item ["::" path_glob]
                    | '{' [<<comma_separated_list path_glob>>] '}'
                    | "*"
        """
        node = PathGlob()
        if self.current_token.type in self.rust_first_set.path_item:
            node.update(path_item=self.path_item())
            if self.current_token.type == TokenType.DOUBLE_COLON:
                node.register_token(self.eat(TokenType.DOUBLE_COLON))
                node.update(sub_path_glob=self.path_glob())
                node.sub_path_glob.father = node
        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            if self.current_token.type in self.rust_first_set.path_glob:
                node.update(path_globs=self.list_items(self.path_glob, trailing_set=self.rust_first_set.path_glob))
                for path_glob in node.path_globs:
                    path_glob.father = node
            node.register_token(self.eat(TokenType.RCURLY_BRACE))
        elif self.current_token.type == TokenType.MUL:
            self.current_token.type = RustTokenType.STAR
            node.register_token(self.eat(RustTokenType.STAR))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be path_item or { or *")
        return node

    def path_item(self):
        """
        path_item ::= ident | self | crate
        """
        if self.current_token.type == TokenType.ID:
            node = self.get_identifier()
            add_ast_type(node, CSS.IMPORT_LIBNAME)
            return node
        elif self.current_token.type in (RustTokenType.SELF, RustTokenType.CRATE):
            return self.get_keyword()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be id or self")

    def extern_crate_item(self):
        """
        extern_crate_item ::= extern crate ident [as ident] ';'
        """
        node = ExternCrateItem()
        node.update(extern=self.get_keyword(token_type=RustTokenType.EXTERN))
        node.update(crate=self.get_keyword(token_type=RustTokenType.CRATE))
        node.update(id=self.get_identifier())
        if self.current_token.type == RustTokenType.AS:
            node.register_token(self.eat(RustTokenType.AS))
            node.update(as_id=self.get_identifier())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def static_item(self):
        """
        static_item ::= static [mut] ident ':' ty '=' expr ';'
        """
        node = StaticItem()
        node.update(static=self.get_keyword(token_type=RustTokenType.STATIC))
        if self.current_token.type == RustTokenType.MUT:
            node.register_token(self.eat(RustTokenType.MUT))
        node.update(id=self.get_identifier())
        node.register_token(self.eat(TokenType.COLON))
        node.update(ty=self.ty())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(expr=self.expr())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def const_item(self):
        """
        const_item ::= const ident ':' ty '=' expr ';'
        """
        node = ConstItem()
        node.update(const=self.get_keyword(token_type=RustTokenType.CONST))
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.CONSTANT)
        GDT.register_id(node.id.id, CSS.CONSTANT)
        node.register_token(self.eat(TokenType.COLON))
        node.update(ty=self.ty())
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(expr=self.expr())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def type_item(self):
        """
        type_item ::= type ident '=' ty ';'
        """
        node = TypeItem()
        node.update(type=self.get_keyword(token_type=RustTokenType.TYPE))
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.TYPEDEF)
        GDT.register_id(node.id.id, CSS.TYPEDEF)
        node.register_token(self.eat(TokenType.ASSIGN))
        node.update(ty=self.ty())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def block_item(self):
        """
        block_item ::= (outer_attrs | inner_attr)?
                     (fn_item
                     | mod_item
                     | struct_item
                     | enum_item
                     | impl_item
                     | trait_item
                     | foreign_mod_item
                     )
        """
        if self.current_token.type in self.rust_first_set.outer_attr:
            self.outer_attrs()
        elif self.current_token.type in self.rust_first_set.inner_attr:
            self.inner_attr()

        if self.current_token.type == RustTokenType.FN:
            return self.fn_item()
        elif self.current_token.type == RustTokenType.MOD:
            return self.mod_item()
        elif self.current_token.type == RustTokenType.STRUCT:
            return self.struct_item()
        elif self.current_token.type == RustTokenType.ENUM:
            return self.enum_item()
        elif self.current_token.type == RustTokenType.IMPL:
            return self.impl_item()
        elif self.current_token.type == RustTokenType.TRAIT:
            return self.trait_item()
        elif self.current_token.type == RustTokenType.EXTERN:
            return self.foreign_mod_item()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN)

    def fn_item(self):
        """
        fn_item ::= fn ident [generic_params] fn_params [ret_ty] [where_clause] block_expr
        """
        node = FnItem()
        node.update(fn=self.get_keyword(token_type=RustTokenType.FN))
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.FUNCTION_NAME)
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())
        node.update(fn_params=self.fn_params())
        if self.current_token.type in self.rust_first_set.ret_ty:
            node.update(ret_ty=self.ret_ty())
        if self.current_token.type in self.rust_first_set.where_clause:
            node.update(where_clause=self.where_clause())

        # 将 parameter 中 mut 的注册到 GDT 中, 用于在 block 中判断匹配
        self._register_fn_param(node.fn_params.fn_params, node.id.id)

        node.update(block_expr=self.block_expr())

        # 脱离作用域, 删除 GDT 中的 parameter
        self._unregister_fn_param(node.id.id)
        return node

    def fn_params(self):
        """
        fn_params ::= '(' [ <<comma_separated_list fn_param>> ] ')'
        """
        node = FnParams()
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.rust_first_set.fn_param:
            node.update(fn_params=self.list_items(self.fn_param, trailing_set=self.rust_first_set.pat))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def fn_param(self):
        """
        fn_param ::= pat ':' ty_sum
        """
        node = FnParam()
        node.update(pat=self.pat())
        node.register_token(self.eat(TokenType.COLON))
        node.update(ty_sum=self.ty_sum())
        return node

    def _register_fn_param(self, fn_params: List[FnParam], scope: str):
        """
        将参数中的 mut 注册到 GDT 中
        """
        if fn_params is None:
            return
        for fn_param in fn_params:
            if fn_param.ty_sum is not None:
                if fn_param.ty_sum.ty.mut is not None:
                    if fn_param.pat.path is not None:
                        GDT.register_id(fn_param.pat.path.id.id, RustCSS.MUTABLE_ARG, scope)
                        fn_param.pat.path.id._tokens[0].add_css(RustCSS.MUTABLE_ARG)

    def _unregister_fn_param(self, scope: str):
        """
        离开作用域时, 从 GDT 中删除参数中的 mut
        """
        GDT.delete_scope(scope)

    def ret_ty(self):
        """
        ret_ty ::= '->' ('!' | ty)
        """
        node = RetTy()
        node.register_token(self.eat(TokenType.POINT))
        if self.current_token.type == TokenType.BANG:
            node.register_token(self.eat(TokenType.BANG))
        elif self.current_token.type in self.rust_first_set.ty:
            node.update(ty=self.ty())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be BANG or ty")
        return node

    def mod_item(self):
        """
        mod_item ::= mod ident ('{' inner_attr* item_with_attrs* '}' | ';')
        """
        node = ModItem()
        node.update(mod=self.get_keyword(token_type=RustTokenType.MOD))
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            node.update(rust=self.rustFiles())
            node.register_token(self.eat(TokenType.RCURLY_BRACE))
        elif self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be LCURLY_BRACE or SEMI")
        return node

    def struct_item(self):
        """
        struct_item ::= struct ident [generic_params]
                        ( [where_clause] ';'
                          | tuple_struct_body [where_clause] ';'
                          | [where_clause] record_struct_body)
        """
        node = StructItem()
        node.update(struct=self.get_keyword(token_type=RustTokenType.STRUCT))
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.CLASS_NAME)
        GDT.register_id(node.id.id, CSS.CLASS_NAME)
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())

        if self.current_token.type == RustTokenType.WHERE:
            node.update(where_clause=self.where_clause())

        if self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type in self.rust_first_set.record_struct_body:
            node.update(record_struct_body=self.record_struct_body())
        elif self.current_token.type in self.rust_first_set.tuple_struct_body:
            node.update(tuple_struct_body=self.tuple_struct_body())
            if self.current_token.type in self.rust_first_set.where_clause:
                node.update(where_clause=self.where_clause())
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be tuple_struct_body or record_struct_body")
        return node

    def tuple_struct_body(self):
        """
        tuple_struct_body ::= '(' <<comma_separated_list tuple_struct_member>> ')'
        """
        node = TupleStructBody()
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(
            tuple_struct_members=self.list_items(
                self.tuple_struct_member, trailing_set=[TokenType.HASH, RustTokenType.PUB, self.rust_first_set.ty]
            )
        )
        node.register_token(self.eat(TokenType.RPAREN))

    def tuple_struct_member(self):
        """
        tuple_struct_member ::= outer_attrs [visibility] ty
        """
        node = TupleStructMember()
        node.update(outer_attrs=self.outer_attrs())
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        node.update(ty=self.ty())
        return node

    def record_struct_body(self):
        """
        record_struct_body ::= '{' <<comma_separated_list record_struct_member>> '}'
        """
        node = RecordStructBody()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        node.update(
            record_struct_members=self.list_items(
                self.record_struct_member, trailing_set=[TokenType.ID, RustTokenType.PUB]
            )
        )
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def record_struct_member(self):
        """
        record_struct_member ::= [visibility] ident ':' ty_sum
        """
        node = RecordStructMember()
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        node.update(id=self.get_identifier())
        node.register_token(self.eat(TokenType.COLON))
        node.update(ty_sum=self.ty_sum())
        return node

    def enum_item(self):
        """
        enum_item ::= enum ident [generic_params] enum_body
        """
        node = EnumItem()
        node.update(enum=self.get_keyword(token_type=RustTokenType.ENUM))
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.ENUMERATOR)
        GDT.register_id(node.id.id, CSS.ENUMERATOR)
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())
        node.update(enum_body=self.enum_body())
        return node

    def enum_body(self):
        """
        enum_body ::= '{' <<comma_separated_list enum_member>> '}'
        """
        node = EnumBody()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        node.update(
            enum_members=self.list_items(
                self.enum_member, trailing_set=[TokenType.ID, RustTokenType.PUB, TokenType.HASH]
            )
        )
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def enum_member(self):
        """
        enum_member ::= outer_attrs [visibility] ident [record_struct_body | tuple_struct_body] ["=" expr]
        """
        node = EnumMember()
        node.update(outer_attrs=self.outer_attrs())
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.ENUM_ID)
        GDT.register_id(node.id.id, CSS.ENUM_ID)
        if self.current_token.type in self.rust_first_set.record_struct_body:
            node.update(record_struct_body=self.record_struct_body())
        elif self.current_token.type in self.rust_first_set.tuple_struct_body:
            node.update(tuple_struct_body=self.tuple_struct_body())

        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(expr=self.expr())
        return node

    def impl_item(self):
        """
        impl_item ::= [unsafe] impl [generic_params] ty_sum [for ty_sum] [where_clause]
              '{' inner_attr* ([visibility] impl_member)* '}'
        """
        node = ImplItem()
        if self.current_token.type == RustTokenType.UNSAFE:
            node.update(unsafe=self.get_keyword(token_type=RustTokenType.UNSAFE))
        node.update(impl=self.get_keyword(token_type=RustTokenType.IMPL))
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())
        node.update(ty_sum=self.ty_sum())
        if self.current_token.type == RustTokenType.FOR:
            node.update(for_kw=self.get_keyword(token_type=RustTokenType.FOR))
            node.update(ty_sum=self.ty_sum())
        if self.current_token.type in self.rust_first_set.where_clause:
            node.update(where_clause=self.where_clause())
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        inner_attrs = []
        while self.current_token.type in self.rust_first_set.inner_attr:
            inner_attrs.append(self.inner_attr())
        node.update(inner_attrs=inner_attrs)

        impl_members = []
        while self.current_token.type in (self.rust_first_set.impl_member, self.rust_first_set.visibility):
            if self.current_token.type in self.rust_first_set.visibility:
                self.visibility()
            impl_members.append(self.impl_member())
        node.update(impl_members=impl_members)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def impl_member(self):
        """
        impl_member ::= type ident '=' ty_sum ';'
                      | const ident ':' ty_sum '=' expr ';'
                      | member_fn_item

        member_fn_item ::= fn ident [generic_params] member_fn_params [ret_ty] [where_clause] block_expr
        """
        node = ImplMember()
        if self.current_token.type == RustTokenType.TYPE:
            node.update(type=self.get_keyword(token_type=RustTokenType.TYPE))
            node.update(id=self.get_identifier())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(ty_sum=self.ty_sum())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == RustTokenType.CONST:
            node.update(const=self.get_keyword(token_type=RustTokenType.CONST))
            node.update(id=self.get_identifier())
            node.register_token(self.eat(TokenType.COLON))
            node.update(ty_sum=self.ty_sum())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(expr=self.expr())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == RustTokenType.FN:
            node.update(fn=self.get_keyword(token_type=RustTokenType.FN))
            node.update(id=self.get_identifier())
            add_ast_type(node.id, CSS.FUNCTION_NAME)
            if self.current_token.type in self.rust_first_set.generic_params:
                node.update(generic_params=self.generic_params())
            node.update(member_fn_params=self.member_fn_params())

            if node.member_fn_params.self_param is not None:
                if node.member_fn_params.self_param.mut is not None:
                    add_ast_type(node.id, RustCSS.MUTABLE_FUNCTION)
                    GDT.register_id("self", RustCSS.MUTABLE_SELF, node.id.id)

            if self.current_token.type in self.rust_first_set.ret_ty:
                node.update(ret_ty=self.ret_ty())
            if self.current_token.type in self.rust_first_set.where_clause:
                node.update(where_clause=self.where_clause())

            self._register_fn_param(node.member_fn_params.fn_params, node.id.id)
            node.update(block_expr=self.block_expr())
            self._unregister_fn_param(node.id.id)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be type, const or fn")
        return node

    def member_fn_params(self):
        """
        member_fn_params ::= '(' ')'
                           | '(' self_param [','] ')'
                           | '(' self_param ',' <<comma_separated_list fn_param>> ')'
                           | '(' <<comma_separated_list fn_param>> ')'
        """
        node = MemberFnParams()
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.rust_first_set.self_param:
            node.update(self_param=self.self_param())
        if self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))

        if self.current_token.type in self.rust_first_set.fn_param:
            node.update(fn_params=self.list_items(self.fn_param, trailing_set=self.rust_first_set.fn_param))
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def self_param(self):
        """
        self_param ::= ['&' [lifetime]] [mut] self
        """
        node = SelfParam()
        if self.current_token.type == TokenType.AMPERSAND:
            node.register_token(self.eat(TokenType.AMPERSAND))
            if self.current_token.type == RustTokenType.LIFETIME:
                node.register_token(self.eat(RustTokenType.LIFETIME))
        if self.current_token.type == RustTokenType.MUT:
            node.update(mut=self.get_keyword(token_type=RustTokenType.MUT))
        node.update(kw_self=self.get_keyword(token_type=RustTokenType.SELF))
        if node.mut is not None:
            node.kw_self._tokens[0].add_css(RustCSS.MUTABLE_SELF)
        return node

    def trait_item(self):
        """
        trait_item ::= trait ident [generic_params] [':' ty_param_bounds] [where_clause] trait_body
        """
        node = TraitItem()
        node.update(trait=self.get_keyword(token_type=RustTokenType.TRAIT))
        node.update(id=self.get_identifier())
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(ty_param_bounds=self.ty_param_bounds())
        if self.current_token.type in self.rust_first_set.where_clause:
            node.update(where_clause=self.where_clause())
        node.update(trait_body=self.trait_body())
        return node

    def trait_body(self):
        """
        trait_body ::= '{' (outer_attrs trait_member) * '}'
        """
        node = TraitBody()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        outer_attrs = []
        trait_members = []
        while self.current_token.type in self.rust_first_set.outer_attr:
            outer_attrs.append(self.outer_attr())
            trait_members.append(self.trait_member())

        node.update(outer_attrs=outer_attrs)
        node.update(trait_members=trait_members)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def trait_member(self):
        """
        trait_member ::= type ty_param ';'
                       | fn ident [generic_params] member_fn_params [ret_ty] [where_clause] (';' | block_expr )
        """
        node = TraitMember()
        if self.current_token.type == RustTokenType.TYPE:
            node.update(type=self.get_keyword(token_type=RustTokenType.TYPE))
            node.update(ty_param=self.ty_param())
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == RustTokenType.FN:
            node.update(fn=self.get_keyword(token_type=RustTokenType.FN))
            node.update(id=self.get_identifier())
            if self.current_token.type in self.rust_first_set.generic_params:
                node.update(generic_params=self.generic_params())
            node.update(member_fn_params=self.member_fn_params())
            if self.current_token.type in self.rust_first_set.ret_ty:
                node.update(ret_ty=self.ret_ty())
            if self.current_token.type in self.rust_first_set.where_clause:
                node.update(where_clause=self.where_clause())

            if self.current_token.type == TokenType.SEMI:
                node.register_token(self.eat(TokenType.SEMI))
            elif self.current_token.type == TokenType.LCURLY_BRACE:
                node.update(block_expr=self.block_expr())
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be SEMI or LCURLY_BRACE")
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be type or fn")
        return node

    def foreign_mod_item(self):
        """
        foreign_mod_item ::= extern [abi] '{' inner_attr*  foreign_item* '}'
        """
        node = ForeignModItem()
        node.update(extern=self.get_keyword(token_type=RustTokenType.EXTERN))
        if self.current_token.type == TokenType.STRING:
            node.update(abi=self.get_string())
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        node.update(inner_attrs=self.list_items(self.inner_attr, trailing_set=self.rust_first_set.inner_attr))
        node.update(foreign_items=self.list_items(self.foreign_item, trailing_set=self.rust_first_set.outer_attr))
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def foreign_item(self):
        """
        foreign_item ::= outer_attrs [visibility] fn ident [generic_params] fn_params [ret_ty] [where_clause] ';'
        """
        node = ForeignItem()
        node.update(outer_attrs=self.outer_attrs())
        if self.current_token.type in self.rust_first_set.visibility:
            node.update(visibility=self.visibility())
        node.update(fn=self.get_keyword(token_type=RustTokenType.FN))
        node.update(id=self.get_identifier())
        if self.current_token.type in self.rust_first_set.generic_params:
            node.update(generic_params=self.generic_params())
        node.update(fn_params=self.fn_params())
        if self.current_token.type in self.rust_first_set.ret_ty:
            node.update(ret_ty=self.ret_ty())
        if self.current_token.type in self.rust_first_set.where_clause:
            node.update(where_clause=self.where_clause())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def generic_params(self):
        """
        generic_params ::= '<' [lifetime] [<<comma_separated_list ty_param>>] '>'
        """
        node = GenericParams()
        node.register_token(self.eat(TokenType.LANGLE_BRACE))
        if self.current_token.type == RustTokenType.LIFETIME:
            node.register_token(self.eat(RustTokenType.LIFETIME))
        if self.current_token.type == TokenType.ID:
            node.update(ty_params=self.list_items(self.ty_param, trailing_set=[TokenType.ID, RustTokenType.LIFETIME]))
        node.register_token(self.eat(TokenType.RANGLE_BRACE))
        return node

    def where_clause(self):
        """
        where_clause ::= where <<comma_separated_list (ty ':' ty_param_bounds)>>
        """
        node = WhereClause()
        node.register_token(self.eat(RustTokenType.WHERE))

        tys = []
        ty_param_bounds = []
        while self.current_token.type in self.rust_first_set.ty:
            tys.append(self.ty())
            node.register_token(self.eat(TokenType.COLON))
            ty_param_bounds.append(self.ty_param_bounds())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
        node.update(tys=tys)
        node.update(ty_param_bounds=ty_param_bounds)
        return node

    def pat(self):
        """
        pat ::= '_'
              | '&' pat
              | mut ident
              | ref [mut] ident
              | '(' <<comma_separated_list pat>> ')'
              | '[' <<comma_separated_list pat>> ']'
              | path '(' <<comma_separated_list pat>> ')'
              | path '{' <<comma_separated_list pat_field>> ['..']'}'
              | path ['@' lit]
              | '-'? lit
        """
        node = Pat()
        if self.current_token.type == TokenType.AMPERSAND:
            node.register_token(self.eat(TokenType.AMPERSAND))
            node.update(pat=self.pat())
        elif self.current_token.type == RustTokenType.MUT:
            node.update(mut=self.get_keyword(token_type=RustTokenType.MUT))
            node.update(id=self.get_identifier())
            GDT.register_id(node.id.id, RustCSS.MUTABLE_VAR)
            node.id._tokens[0].add_css(RustCSS.MUTABLE_VAR)

        elif self.current_token.type == RustTokenType.REF:
            node.update(ref=self.get_keyword(token_type=RustTokenType.REF))
            if self.current_token.type == RustTokenType.MUT:
                node.update(mut=self.get_keyword(token_type=RustTokenType.MUT))
            node.update(id=self.get_identifier())
            
            if node.mut is not None:
                GDT.register_id(node.id.id, RustCSS.MUTABLE_VAR)
                node.id._tokens[0].add_css(RustCSS.MUTABLE_VAR)
        elif self.current_token.type == TokenType.LPAREN:
            if self.peek_next_token().type == TokenType.RPAREN:
                node.update(lit=self.lit())
            elif self.peek_next_token().type in self.rust_first_set.pat:
                node.register_token(self.eat(TokenType.LPAREN))
                node.update(pats=self.list_items(self.pat, trailing_set=self.rust_first_set.pat))
                node.register_token(self.eat(TokenType.RPAREN))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be pat or (\{pats\})")
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(pats=self.list_items(self.pat, trailing_set=self.rust_first_set.pat))
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        elif self.current_token.type in self.rust_first_set.path:
            node.update(path=self.path())
            if self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                node.update(pats=self.list_items(self.pat, trailing_set=self.rust_first_set.pat))
                node.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type == TokenType.LCURLY_BRACE:
                node.register_token(self.eat(TokenType.LCURLY_BRACE))
                node.update(pats=self.list_items(self.pat_field, trailing_set=self.rust_first_set.pat_field))
                if self.current_token.type == TokenType.CONCAT:
                    node.register_token(self.eat(TokenType.CONCAT))
                node.register_token(self.eat(TokenType.RCURLY_BRACE))
            elif self.current_token.type == TokenType.AT_SIGN:
                node.register_token(self.eat(TokenType.AT_SIGN))
                node.update(lit=self.lit())
        elif self.current_token.type in (self.rust_first_set.lit, TokenType.MINUS):
            if self.current_token.type == TokenType.MINUS:
                node.register_token(self.eat(TokenType.MINUS))
            node.update(lit=self.lit())

        elif self.current_token.type == TokenType.CONCAT:
            node.register_token(self.eat(TokenType.CONCAT))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be pat or lit or &/mut/ref")
        return node

    def pat_field(self):
        """
        pat_field ::= ident ':' pat | [ref] [mut] ident
        """
        node = PatField()
        if self.current_token.type == RustTokenType.REF:
            node.update(ref=self.get_keyword(token_type=RustTokenType.REF))
            if self.current_token.type == RustTokenType.MUT:
                node.update(mut=self.get_keyword(token_type=RustTokenType.MUT))
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(pat=self.pat())
        return node

    def pats(self):
        """
        pats ::= pat ('|' pat)*
        """
        return self.list_items(self.pat, trailing_set=self.rust_first_set.pat, delimiter=TokenType.PIPE)

    def ty_sum(self):
        """
        ty_sum ::= ty ['+' ty_param_bounds]
        """
        node = TySum()
        node.update(ty=self.ty())
        if self.current_token.type == TokenType.PLUS:
            node.register_token(self.eat(TokenType.PLUS))
            node.update(ty_param_bounds=self.ty_param_bounds())
        return node

    def ty(self):
        """
        ty ::= '(' ty_sum ')'
             | '()'
             | '(' <<comma_separated_list ty>> ')'
             | '*' ptr
             | '[' ty_sum ']'
             | '[' ty_sum ';' expr ']'
             | '&' [lifetime] [mut] ty
             | bare_fn
             | type_path

        bare_fn 是什么?
        ptr 是什么?
        """
        node = Ty()
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.rust_first_set.ty_sum:
                node.update(ty_sums=self.list_items(self.ty_sum, trailing_set=self.rust_first_set.ty_sum))
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type == TokenType.MUL:
            self.current_token.type = RustTokenType.DEREF
            node.register_token(self.eat(RustTokenType.DEREF))
            node.update(ptr=self.get_identifier())
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(ty_sum=self.ty_sum())
            if self.current_token.type == TokenType.SEMI:
                node.register_token(self.eat(TokenType.SEMI))
                node.update(expr=self.expr())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        elif self.current_token.type == TokenType.AMPERSAND:
            node.register_token(self.eat(TokenType.AMPERSAND))
            if self.current_token.type == RustTokenType.LIFETIME:
                node.register_token(self.eat(RustTokenType.LIFETIME))
            if self.current_token.type == RustTokenType.MUT:
                node.update(mut=self.get_keyword(token_type=RustTokenType.MUT))
            node.update(ty=self.ty())
        elif self.current_token.type in self.rust_first_set.type_path:
            node.update(type_path=self.type_path())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be ty_sum or *ptr or type_path")

        return node

    def ty_param(self):
        """
        ty_param ::= ident [':' ty_param_bounds]
        """
        node = TyParam()
        node.update(id=self.get_identifier())
        node.id._tokens[0].add_css(RustCSS.GENERIC_TYPE)
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(ty_param_bounds=self.ty_param_bounds())
        return node

    def ty_param_bounds(self):
        """
        ty_param_bounds ::= ty_param_bound ('+' ty_param_bound)*
        """
        return self.list_items(
            self.ty_param_bound, trailing_set=[RustTokenType.LIFETIME, TokenType.ID], delimiter=TokenType.PLUS
        )

    def ty_param_bound(self):
        """
        ty_param_bound ::= lifetime | ["?"] type_path
        """
        if self.current_token.type == RustTokenType.LIFETIME:
            self.eat()
            return None
        elif self.current_token.type in self.rust_first_set.type_path or self.current_token.type == TokenType.QUESTION:
            if self.current_token.type == TokenType.QUESTION:
                self.eat()
            return self.type_path()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be lifetime or type_path or ?")

    def type_path(self):
        """
        type_path ::= type_path_segment ("::" type_path_segment)*
        """
        return self.list_items(self.type_path_segment, trailing_set=[TokenType.ID], delimiter=TokenType.DOUBLE_COLON)

    def type_path_segment(self):
        """
        type_path_segment ::= (ident|Self) [generic_values | '(' [<<comma_separated_list ty_sum>>] ')' [ret_ty]]
        """
        node = TypePathSegment()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
            GDT.register_id(node.id.id, RustCSS.TYPE_BOUND)
            node.id._tokens[0].add_css(RustCSS.TYPE_BOUND)
        elif self.current_token.type == RustTokenType.SSELF:
            node.update(sself=self.get_keyword(token_type=RustTokenType.SSELF))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be ident or Self")

        if self.current_token.type in self.rust_first_set.generic_values:
            node.update(generic_values=self.generic_values())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.rust_first_set.ty_sum:
                node.update(ty_sums=self.list_items(self.ty_sum, trailing_set=self.rust_first_set.ty_sum))
            node.register_token(self.eat(TokenType.RPAREN))
            if self.current_token.type in self.rust_first_set.ret_ty:
                node.update(ret_ty=self.ret_ty())
        return node

    def generic_values(self):
        """
        generic_values ::= '<' <<comma_separated_list (ident '=' ty | ty_sum | lifetime)>> '>'
        """
        node = GenericValues()
        node.register_token(self.eat(TokenType.LANGLE_BRACE))

        ids = []
        tys = []
        ty_sums = []
        while self.current_token.type in (self.rust_first_set.ty_sum, RustTokenType.LIFETIME):
            if self.current_token.type == TokenType.ID and self.peek_next_token().type == TokenType.ASSIGN:
                ids.append(self.get_identifier())
                node.register_token(self.eat(TokenType.ASSIGN))
                tys.append(self.ty())
            elif self.current_token.type == RustTokenType.LIFETIME:
                node.register_token(self.eat(RustTokenType.LIFETIME))
            else:
                ty_sums.append(self.ty_sum())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))

        node.update(ids=ids)
        node.update(tys=tys)
        node.update(ty_sums=ty_sums)
        node.register_token(self.eat(TokenType.RANGLE_BRACE))
        return node

    def path(self):
        """
        path ::= (ident|Self) ("::" ident)*
        """
        node = Path()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
        elif self.current_token.type == RustTokenType.SSELF:
            node.update(kw_self=self.get_keyword(token_type=RustTokenType.SSELF))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be ident or Self")

        path_ids = []
        while self.current_token.type == TokenType.DOUBLE_COLON:
            node.register_token(self.eat(TokenType.DOUBLE_COLON))
            path_ids.append(self.get_identifier())
        node.update(path_ids=path_ids)
        return node

    def expr_path(self):
        """
        expr_path ::= expr_path_segment ("::" expr_path_segment)*
        """
        return self.list_items(self.expr_path_segment, trailing_set=[TokenType.ID], delimiter=TokenType.DOUBLE_COLON)

    def expr_path_segment(self):
        """
        expr_path_segment ::= ident ["::" generic_values]
        """
        node = ExprPathSegment()
        node.update(id=self.get_identifier())
        if (
            self.current_token.type == TokenType.DOUBLE_COLON
            and self.peek_next_token().type in self.rust_first_set.generic_values
        ):
            node.register_token(self.eat(TokenType.DOUBLE_COLON))
            node.update(generic_values=self.generic_values())
        return node

    def expr(self, is_match_expr=False):
        """
        expr ::= assign_expr
               | range_expr
               | lor_expr
               | land_expr
               | comp_group
               | bor_expr
               | bxor_expr
               | band_expr
               | shift_group
               | add_group
               | mul_group
               | cast_expr

               --- expr op expr ---

               | unary_group
               | macro_expr
               | primary_group

               --- expr match ---

               | ref_group -- expr suffix
        """
        node = Expr()
        # unary_group.borrow_expr 和 primary_group.paren_expr 有重叠, 但是不影响匹配, 可以直接在这里过 unary_group, 交由下一组匹配 expr
        if self.current_token.type in self.rust_first_set.unary_group:
            node.update(expr=self.unary_group(is_match_expr))
        elif self.current_token.type == TokenType.ID and self.peek_next_token().type == TokenType.BANG:
            node.update(expr=self.macro_expr(is_match_expr))
        elif self.current_token.type in self.rust_first_set.primary_group:
            node.update(expr=self.primary_group(is_match_expr))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be unary group or primary group or macro expr")

        while self.current_token.type in self.rust_first_set.ref_group:
            self.ref_group(node)

        if self.current_token.type in self.binary_op_set or self.current_token.type == RustTokenType.AS:
            if self.current_token.type == RustTokenType.AS:
                node.update(kw_as=self.get_keyword(token_type=RustTokenType.AS))
            else:
                node.update(op=self.get_punctuator())
                if len(node.op.op) > 1 and node.op.op[-1] == '=' and node.op.op not in ['<=','>=']:
                    node.op._tokens[0].add_css(RustCSS.MUTABLE_OP)

            node.update(next_expr=self.expr())
        return node

    def unary_group(self, is_match_expr=False):
        """
        unary_group ::= box_expr
                      | unary_min_expr
                      | deref_expr
                      | not_expr
                      | borrow_expr
        """
        node = UnaryGroup()
        if self.current_token.type == RustTokenType.BOX:
            node.update(kw=self.get_keyword(token_type=RustTokenType.BOX))
        elif self.current_token.type == TokenType.MUL:
            self.current_token.type = RustTokenType.DEREF
            node.register_token(self.eat(RustTokenType.DEREF))
        elif self.current_token.type == TokenType.BANG:
            node.register_token(self.eat(TokenType.BANG))
        elif self.current_token.type == TokenType.MINUS:
            node.register_token(self.eat(TokenType.MINUS))
        elif self.current_token.type == TokenType.AMPERSAND:
            node.register_token(self.eat(TokenType.AMPERSAND))
            if self.current_token.type == RustTokenType.MUT:
                node.update(kw=self.get_keyword(token_type=RustTokenType.MUT))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be box, *, & or -")
        node.update(expr=self.expr(is_match_expr))
        return node

    def macro_expr(self, is_match_expr=False):
        """
        macro_expr ::= ident '!' '(' [<<comma_separated_list expr>>] ')'
        """
        node = MacroExpr()
        node.update(ident=self.get_identifier())
        node.register_token(self.eat(TokenType.BANG))
        add_ast_type(node.ident, CSS.MACRO_DEFINE)

        if self.current_token.type in (TokenType.LPAREN, TokenType.LSQUAR_PAREN):
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be '(' or '['")
        if self.current_token.type in self.rust_first_set.expr:
            node.update(
                exprs=self.list_items(self.expr, trailing_set=self.rust_first_set.expr, func_args=(is_match_expr,))
            )
        if self.current_token.type in (TokenType.RPAREN, TokenType.RSQUAR_PAREN):
            node.register_token(self.eat())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be ')' or ']'")
        return node

    def ref_group(self, expr: Expr):
        """
        ref_group ::= ref_expr | array_ref_expr | call_expr

        ref_expr ::= expr '.' (ident | lit_integer)
        array_ref_expr ::= expr '[' index_expr ']'
        private index_expr ::= expr || ..
        call_expr ::= expr ["::" generic_values] '(' [<<comma_separated_list expr>>] ')'
        """
        node = RefGroup()
        if self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            if self.current_token.type == TokenType.ID:
                node.update(id=self.get_identifier())
            elif self.current_token.type == TokenType.NUMBER:
                node.register_token(self.eat(TokenType.NUMBER))
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be identifier or integer")
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            if self.current_token.type == TokenType.CONCAT:
                node.register_token(self.eat(TokenType.CONCAT))
            else:
                node.update(index_expr=self.expr())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        elif self.current_token.type in (TokenType.DOUBLE_COLON, TokenType.LPAREN):
            # call_expr
            if self.current_token.type == TokenType.DOUBLE_COLON:
                node.register_token(self.eat(TokenType.DOUBLE_COLON))
                node.update(generic_values=self.generic_values())
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.rust_first_set.expr:
                node.update(exprs=self.list_items(self.expr, trailing_set=self.rust_first_set.expr))
            node.register_token(self.eat(TokenType.RPAREN))

            if type(expr.expr) == PrimaryGroup:
                if len(expr.ref_exprs) != 0 and expr.ref_exprs[-1].id is not None:
                    add_ast_type(expr.ref_exprs[-1].id, CSS.FUNCTION_CALL)
                elif expr.expr.expr_path is not None:
                    add_ast_type(expr.expr.expr_path[-1], CSS.FUNCTION_CALL)

        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be . or [")

        expr.ref_exprs.append(node)

    def primary_group(self, is_match_expr=False):
        """
        primary_group ::= struct_expr
                        | simple_ref_expr
                        | literal_expr
                        | paren_expr
                        | tuple_expr
                        | array_expr
                        | lambda_expr
                        | return_expr
                        | statement_like_expr
                        | continue
                        | break [expr|lifetime ";"?]

        struct_expr ::= expr_path '{' <<comma_separated_list struct_field>> ['..' expr]'}'

        simple_ref_expr ::= expr_path | self
        literal_expr ::= lit
        paren_expr ::= &('(' expr ')') '(' expr ')'
        tuple_expr ::= '(' expr ',' [<<comma_separated_list expr>>] ')'
        array_expr ::= '[' expr ';' expr ']'
                     | '[' [<<comma_separated_list expr>>] ']'
        return_expr ::= return [expr]

        @EXTENDED-GRAMMAR: 添加 continue 和 break 的语法
        """
        node = PrimaryGroup()
        if self.current_token.type == RustTokenType.SELF:
            node.update(kw_self=self.get_keyword(token_type=RustTokenType.SELF))
        elif self.current_token.type == TokenType.ID:
            # struct_expr | simple_ref_expr
            node.update(expr_path=self.expr_path())
            if (
                not is_match_expr
                and self.current_token.type == TokenType.LCURLY_BRACE
                and self.peek_next_token().type == TokenType.ID
            ):
                node.register_token(self.eat(TokenType.LCURLY_BRACE))
                node.update(struct_fields=self.list_items(self.struct_field, trailing_set=[TokenType.ID]))
                if self.current_token.type == TokenType.CONCAT:
                    node.register_token(self.eat(TokenType.CONCAT))
                    node.update(expr=self.expr())
                node.register_token(self.eat(TokenType.RCURLY_BRACE))
        elif self.current_token.type == TokenType.LPAREN:
            if self.peek_next_token().type != TokenType.RPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                node.update(exprs=self.list_items(self.expr, trailing_set=self.rust_first_set.expr))
                node.register_token(self.eat(TokenType.RPAREN))
            else:
                node.update(lit=self.lit())
        elif self.current_token.type in self.rust_first_set.lit:
            node.update(lit=self.lit())
        elif self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            if self.current_token.type in self.rust_first_set.expr:
                node.update(expr=self.expr())
                if self.current_token.type == TokenType.SEMI:
                    node.register_token(self.eat(TokenType.SEMI))
                    node.update(next_expr=self.expr())
                elif self.current_token.type == TokenType.COMMA:
                    node.register_token(self.eat(TokenType.COMMA))
                    exprs = []
                    while self.current_token.type in self.rust_first_set.expr:
                        exprs.append(self.expr())
                        if self.current_token.type == TokenType.COMMA:
                            node.register_token(self.eat(TokenType.COMMA))
                        else:
                            break
                    node.update(exprs=exprs)

            node.register_token(self.eat(TokenType.RSQUAR_PAREN))

        elif self.current_token.type in self.rust_first_set.lambda_expr:
            node.update(lambda_expr=self.lambda_expr())
        elif self.current_token.type == RustTokenType.RETURN:
            node.update(kw=self.get_keyword(token_type=RustTokenType.RETURN))
            if self.current_token.type in self.rust_first_set.expr:
                node.update(expr=self.expr())
        elif self.current_token.type in self.rust_first_set.statement_like_expr:
            node.update(statement_like_expr=self.statement_like_expr())
        elif self.current_token.type == RustTokenType.CONTINUE:
            node.update(kw=self.get_keyword(token_type=RustTokenType.CONTINUE))
        elif self.current_token.type == RustTokenType.BREAK:
            node.update(kw=self.get_keyword(token_type=RustTokenType.BREAK))
            if self.current_token.type in self.rust_first_set.expr:
                node.update(expr=self.expr())
            elif self.current_token.type == RustTokenType.LIFETIME:
                self.current_token.type = RustTokenType.LABEL
                node.register_token(self.eat(RustTokenType.LABEL))
                if self.current_token.type == TokenType.SEMI:
                    node.register_token(self.eat(TokenType.SEMI))

        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                message="should be struct_expr | simple_ref_expr | literal_expr | paren_expr | tuple_expr | array_expr | return_expr | statement_like_expr | continue | break",
            )
        return node

    def struct_field(self):
        """
        struct_field ::= ident [':' expr]
        """
        node = StructField()
        node.update(id=self.get_identifier())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(expr=self.expr())
        return node

    def lambda_expr(self):
        """
        lambda_expr ::= ('||' | '|' [<<comma_separated_list lambda_param>>] '|') [ret_ty] expr
        """
        node = LambdaExpr()
        if self.current_token.type == TokenType.OR:
            self.current_token.type = RustTokenType.LAMBDA
            node.register_token(self.eat(RustTokenType.LAMBDA))
        elif self.current_token.type == TokenType.PIPE:
            node.register_token(self.eat(TokenType.PIPE))
            if self.current_token.type in self.rust_first_set.pat:
                node.update(lambda_params=self.list_items(self.lambda_param, trailing_set=self.rust_first_set.pat))
            node.register_token(self.eat(TokenType.PIPE))
            if self.current_token.type in self.rust_first_set.ret_ty:
                node.update(ret_ty=self.ret_ty())
            node.update(expr=self.expr())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be || or |")

        return node

    def lambda_param(self):
        """
        lambda_param ::= pat [":" ty_sum]
        """
        node = LambdaParam()
        node.update(pat=self.pat())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(ty_sum=self.ty_sum())
        return node

    def statement_like_expr(self):
        """
        statement_like_expr ::= block_expr
                              | unsafe_block_expr
                              | if_expr
                              | while_expr
                              | loop_expr
                              | match_expr
                              | for_expr
        """
        if self.current_token.type == TokenType.LCURLY_BRACE:
            return self.block_expr()
        elif self.current_token.type == RustTokenType.UNSAFE:
            return self.unsafe_block_expr()
        elif self.current_token.type == RustTokenType.IF:
            return self.if_expr()
        elif self.current_token.type == RustTokenType.WHILE:
            return self.while_expr()
        elif self.current_token.type == RustTokenType.LOOP:
            return self.loop_expr()
        elif self.current_token.type == RustTokenType.MATCH:
            return self.match_expr()
        elif self.current_token.type == RustTokenType.FOR:
            return self.for_expr()
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                message="should be block_expr | unsafe_block_expr | if_expr | while_expr | loop_expr | match_expr | for_expr",
            )

    def block_expr(self):
        """
        block_expr ::= '{' stmt* [expr] '}'
        """
        node = BlockExpr()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        node.update(stmts=self.list_items(self.stmt, trailing_set=self.rust_first_set.stmt, delimiter=None))
        if self.current_token.type in self.rust_first_set.expr:
            node.update(expr=self.expr())
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def unsafe_block_expr(self):
        """
        unsafe_block_expr ::= unsafe block_expr
        """
        node = UnsafeBlockExpr()
        node.update(unsafe=self.get_keyword(token_type=RustTokenType.UNSAFE))
        node.update(block_expr=self.block_expr())
        return node

    def if_expr(self):
        """
        if_expr ::= if (let pat '=' expr | expr) block_expr [else (if_expr | block_expr)]
        """
        node = IfExpr()
        node.update(if_kw=self.get_keyword(token_type=RustTokenType.IF))
        if self.current_token.type == RustTokenType.LET:
            node.update(let_kw=self.get_keyword(token_type=RustTokenType.LET))
            node.update(pat=self.pat())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(expr=self.expr())
        elif self.current_token.type in self.rust_first_set.expr:
            node.update(expr=self.expr())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be let | expr")
        node.update(block_expr=self.block_expr())
        if self.current_token.type == RustTokenType.ELSE:
            node.register_token(self.eat(RustTokenType.ELSE))
            if self.current_token.type == RustTokenType.IF:
                node.update(if_expr=self.if_expr())
            elif self.current_token.type in self.rust_first_set.block_expr:
                node.update(block_expr=self.block_expr())
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be if | block_expr")
        return node

    def while_expr(self):
        """
        while_expr ::= while (let pat '=' expr | expr) block_expr
        """
        node = WhileExpr()
        node.update(while_kw=self.get_keyword(token_type=RustTokenType.WHILE))
        if self.current_token.type == RustTokenType.LET:
            node.update(let_kw=self.get_keyword(token_type=RustTokenType.LET))
            node.update(pat=self.pat())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(expr=self.expr())
        elif self.current_token.type in self.rust_first_set.expr:
            node.update(expr=self.expr())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be let | expr")
        node.update(block_expr=self.block_expr())
        return node

    def loop_expr(self):
        """
        loop_expr ::= loop block_expr
        """
        node = LoopExpr()
        node.update(loop_kw=self.get_keyword(token_type=RustTokenType.LOOP))
        node.update(block_expr=self.block_expr())
        return node

    def match_expr(self):
        """
        match_expr ::= match expr '{'
            (pats [if expr] '=>' (block_expr [',']| expr ','))*
            [pats [if expr] '=>' expr]
        '}'
        """
        node = MatchExpr()
        node.update(match_kw=self.get_keyword(token_type=RustTokenType.MATCH))
        node.update(expr=self.expr(is_match_expr=True))
        node.register_token(self.eat(TokenType.LCURLY_BRACE))

        match_items = []
        while self.current_token.type in self.rust_first_set.pat:
            match_item = MatchItem()
            match_item.update(pats=self.pats())
            if self.current_token.type == RustTokenType.IF:
                match_item.register_token(self.eat(RustTokenType.IF))
                match_item.update(expr=self.expr())
            match_item.register_token(self.eat(TokenType.LAMBDA_POINT))
            if self.current_token.type in self.rust_first_set.block_expr:
                match_item.update(block_expr=self.block_expr())
            elif self.current_token.type in self.rust_first_set.expr:
                match_item.update(expr=self.expr())
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be block_expr | expr")
            if self.current_token.type == TokenType.COMMA:
                match_item.register_token(self.eat(TokenType.COMMA))
            match_items.append(match_item)
        node.update(match_items=match_items)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def for_expr(self):
        """
        for_expr ::= for pat in expr block_expr
        """
        node = ForExpr()
        node.update(for_kw=self.get_keyword(token_type=RustTokenType.FOR))
        node.update(pat=self.pat())
        node.register_token(self.eat(RustTokenType.IN))
        node.update(expr=self.expr())
        node.update(block_expr=self.block_expr())
        return node

    def stmt(self):
        """
        stmt ::= stmt_item
               | let_item
               | label_item
               | statement_like_expr
               | expr "?"? ';'?
               | ';'
        """
        if self.current_token.type in self.rust_first_set.stmt_item:
            return self.stmt_item()
        elif self.current_token.type == RustTokenType.LET:
            return self.let_item()
        elif self.current_token.type == RustTokenType.LIFETIME:
            return self.label_item()
        elif self.current_token.type in self.rust_first_set.statement_like_expr:
            return self.statement_like_expr()
        elif self.current_token.type in self.rust_first_set.expr:
            node = self.expr()
            if self.current_token.type == TokenType.QUESTION:
                node.register_token(self.eat(TokenType.QUESTION))
            if self.current_token.type == TokenType.SEMI:
                node.register_token(self.eat(TokenType.SEMI))
            return node
        elif self.current_token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            return None
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be stmt_item | let | statement_like_expr | expr | ;")

    def let_item(self):
        """
        let pat [':' ty_sum] ['=' expr] ';'
        """
        node = LetExpr()
        node.update(let_kw=self.get_keyword(token_type=RustTokenType.LET))
        node.update(pat=self.pat())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(ty_sum=self.ty_sum())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(expr=self.expr())
        node.register_token(self.eat(TokenType.SEMI))
        # 对于 pat 为不可变的变量, 修正其匹配类型
        # let mux x = 0;
        # ...
        # let x = x;
        #     |
        if node.pat.path is not None:
            node.pat.path.id._tokens[0].remove_css(RustCSS.MUTABLE_VAR)
        return node

    def label_item(self):
        """
        label_item ::= lifetime ":" stmt
        """
        node = LabelItem()
        if self.current_token.type == RustTokenType.LIFETIME:
            self.current_token.type = RustTokenType.LABEL
            node.update(label=self.get_identifier(RustTokenType.LABEL))
            add_ast_type(node.label, RustCSS.LABEL)
            GDT.register_id(node.label.id, RustCSS.LABEL)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be lifetime")

        node.register_token(self.eat(TokenType.COLON))
        node.update(stmt=self.stmt())
        return node

    def lit(self):
        """
        lit ::= (lit_byte
              | lit_char
              | lit_integer
              | lit_float
              | lit_string
              | lit_byte_string
              | '()'
              | true
              | false
              | str
              | ..)

              ["..=" lit]
        """

        if self.current_token.type not in self.rust_first_set.lit:
            self.error(ErrorCode.UNEXPECTED_TOKEN, message="should be lit")

        node = Lit()
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type == TokenType.STRING:
            # rust 的格式化字符串
            node.update(lit_string=self.get_string())
        elif self.current_token.type == TokenType.NUMBER:
            node.update(lit_integer=self.get_number(r"(.*?)([iuf](?:8|16|32|64|128|size))$"))
        else:
            node.register_token(self.eat())
        if self.current_token.type == RustTokenType.PATTERN_MATCH:
            node.register_token(self.eat(RustTokenType.PATTERN_MATCH))
            node.update(end_lit=self.lit())
        return node

    def after_eat(self):
        if self.current_token.type == TokenType.ID and self.current_token.value in GDT:
            if GDT[self.current_token.value] == RustCSS.MUTABLE_ARG:
                self.current_token.add_css(RustCSS.MUTABLE_VAR)
            else:
                self.current_token.add_css(GDT[self.current_token.value])

        if self.current_token.type == RustTokenType.SELF:
            if "self" in GDT:
                self.current_token.add_css(RustCSS.MUTABLE_SELF)

    def get_string(self):
        invisible_pattern = r"\\\\|\\n|\\t|\\v|\\f"
        sub_strings = re.split(r"(\{\{|\}\}|{|}|(?:" + invisible_pattern + "))", self.current_token.value)
        new_asts = []

        line = self.current_token.line
        column = self.current_token.column - len(self.current_token.value)

        format_inside = False

        for sub_string in sub_strings:
            if len(sub_string) == 0:
                continue

            column += len(sub_string)
            token = Token(TokenType.STRING, sub_string, line, column)

            if sub_string == "{":
                format_inside = True
                token.add_css(CSS.FORMAT)
            elif sub_string == "}":
                format_inside = False
                token.add_css(CSS.FORMAT)
            elif bool(re.match(invisible_pattern, sub_string)):
                token.add_css(CSS.CONTROL)

            if format_inside:
                if bool(re.match(r"^[_a-zA-Z][_a-zA-Z0-9]*", sub_string)):
                    token.type = TokenType.ID
                elif bool(re.match(r"\d+", sub_string)):
                    token.type = TokenType.NUMBER

                match = re.match(r"(:[><\.#]?\??)(.*)", sub_string)
                if match is not None:
                    format_token = Token(TokenType.STRING, match.group(1), line, column - len(match.group(2)))
                    format_token.add_css(CSS.FORMAT)
                    self.manual_register_token(format_token)
                    node = String(format_token.value)
                    node.register_token([format_token])
                    new_asts.append(node)

                    token.type = TokenType.NUMBER
                    token.value = match.group(2)

            self.manual_register_token(token)
            node = String(token.value)
            node.register_token([token])
            new_asts.append(node)

        self.manual_get_next_token()
        return new_asts
