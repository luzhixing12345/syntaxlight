from .ast import AST, Identifier, Keyword, Punctuator
from typing import List, Union, Optional
from ..gdt import GlobalDescriptorTable, CSS


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
        self.id:Identifier = None
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


class ExternCrateItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.as_id = None


class UseItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.use = None
        self.path_glob: PathGlob = None


class PathGlob(AST):
    def __init__(self) -> None:
        super().__init__()
        self.path_item: Union[Identifier, Keyword, None] = None
        self.sub_path_glob: Optional[PathGlob] = None
        self.path_globs: Optional[List[PathGlob]] = None

        self.father: PathGlob = None  # sub_path_glob 的父节点

    def register_gdt(self, GDT: GlobalDescriptorTable):
        """
        将最后一个导入的路径注册到 GDT 中
        """
        if self.path_item is not None:
            if self.sub_path_glob is None:
                if type(self.path_item) == Identifier:
                    if GDT[self.path_item.id] != CSS.ENUM_ID:
                        GDT.register_id(self.path_item.id, CSS.IMPORT_LIBNAME)
                elif type(self.path_item) == Keyword:
                    father_node = self.father
                    while father_node.path_item is None and father_node.father is not None:
                        father_node = father_node.father
                    if father_node.father is not None:
                        GDT.register_id(father_node.path_item.id, CSS.IMPORT_LIBNAME)
            else:
                self.sub_path_glob.register_gdt(GDT)
        else:
            if self.path_globs is not None:
                for path_glob in self.path_globs:
                    path_glob.register_gdt(GDT)


class StaticItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.static = None
        self.mut = None
        self.id = None
        self.ty = None
        self.expr = None


class ConstItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.const = None
        self.id:Identifier = None
        self.ty = None
        self.expr = None


class TypeItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type = None
        self.id:Identifier = None
        self.ty = None


class FnItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.fn = None
        self.id:Identifier = None
        self.generic_params = None
        self.fn_params:FnParams = None
        self.ret_ty = None
        self.where_clause = None
        self.block_expr = None


class GenericParams(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty_params = None


class ModItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.mod = None
        self.id = None
        self.rust = None


class StructItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.struct = None
        self.id:Identifier = None
        self.generic_params = None
        self.where_clause = None
        self.tuple_struct_body = None
        self.record_struct_body = None


class TupleStructBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.exprs = None


class EnumItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.enum = None
        self.id:Identifier = None
        self.generic_params = None
        self.enum_body = None


class TupleStructMember(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.visibility = None
        self.ty = None


class RecordStructBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.record_struct_members = None


class RecordStructMember(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.visibility = None
        self.id = None
        self.ty_sum = None


class FnParams(AST):
    def __init__(self) -> None:
        super().__init__()
        self.fn_params:List[FnParam] = None


class FnParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat:Pat = None
        self.ty_sum :TySum= None


class RetTy(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty = None


class EnumBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.enum_members = None


class EnumMember(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.visibility = None
        self.id:Identifier = None
        self.tuple_struct_body = None
        self.record_struct_body = None


class ImplItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.impl = None
        self.unsafe = None
        self.generic_params = None
        self.ty_sum = None
        self.for_kw = None
        self.ty_sum = None
        self.where_clause = None
        self.impl_members = None


class ImplMember(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type = None
        self.id:Identifier = None
        self.ty_sum = None
        self.expr = None
        self.member_fn_params: MemberFnParams = None

class MemberFnParams(AST):
    def __init__(self) -> None:
        super().__init__()
        self.self_param:SelfParam = None
        self.fn_params = None

class SelfParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.self = None
        self.mut: Keyword = None
        self.kw_self: Keyword = None

class TraitItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.trait = None
        self.id = None
        self.generic_params = None
        self.ty_param_bounds = None
        self.where_clause = None
        self.trait_body = None


class TraitBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.trait_members = None


class TraitMember(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type = None
        self.ty_param = None
        self.id = None
        self.generic_params = None
        self.member_fn_params = None
        self.ret_ty = None
        self.where_clause = None
        self.block_expr = None


class ForeignModItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.extern = None
        self.abi = None
        self.foreign_items = None


class ForeignItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.outer_attrs = None
        self.visibility = None
        self.fn = None
        self.id = None
        self.generic_params = None
        self.fn_params = None
        self.ret_ty = None
        self.where_clause = None
        self.block_expr = None


class WhereClause(AST):
    def __init__(self) -> None:
        super().__init__()
        self.where = None
        self.ty = None
        self.ty_param_bounds = None


class Path(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.path_ids = None


class Pat(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        self.id: Identifier = None
        self.path: Path = None
        self.mut = None

class PatField(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        self.ty_sum = None


class TySum(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty:Ty = None
        self.ty_param_bounds = None


class Ty(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty = None
        self.mut = None

class TyParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id:Identifier = None
        self.ty_param_bounds = None


class TypePathSegment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.generic_values = None
        self.ty_sums = None
        self.ret_ty = None


class GenericValues(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ids = None
        self.tys = None
        self.ty_sums = None
        self.ret_ty = None


class ExprPathSegment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.generic_values = None


class MacroExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ident = None
        self.exprs = None


class Expr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr: Union[UnaryGroup, PrimaryGroup, MacroExpr] = None
        self.ref_exprs: List[RefGroup] = []
        self.op:Punctuator = None

class UnaryGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None


class PrimaryGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr_path: List[ExprPathSegment] = None


class StructField(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.expr = None


class LambdaExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.lambda_params = None
        self.ret_ty = None
        self.expr = None


class LambdaParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        self.ty_sum = None


class BlockExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.stmts = None
        self.expr = None


class UnsafeBlockExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.unsafe = None
        self.block_expr = None


class IfExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.if_kw = None
        self.expr = None
        self.block_expr = None
        self.else_expr = None


class WhileExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.while_kw = None
        self.expr = None
        self.block_expr = None


class LoopExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.loop_kw = None
        self.block_expr = None


class MatchExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.match_kw = None
        self.expr = None
        self.pats = None
        self.block_expr = None


class MatchItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pats = None
        self.expr = None


class ForExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.for_kw = None
        self.pat = None
        self.expr = None
        self.block_expr = None


class LetExpr(AST):
    def __init__(self) -> None:
        super().__init__()
        self.let_kw = None
        self.pat: Pat = None
        self.ty_sum = None
        self.expr = None


class RefGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.id = None
        self.index_expr = None
        self.generic_values = None


class Visibility(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pub = None
        self.crate = None

class LabelItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.label:Identifier = None
        self.expr = None
        
class Lit(AST):
    def __init__(self) -> None:
        super().__init__()
        self.lit = None