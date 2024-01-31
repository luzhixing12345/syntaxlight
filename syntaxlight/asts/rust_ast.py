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
        
class ExternCrateItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.as_id = None
        
class UseItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.use = None
        self.path_glob = None
        
        
class PathGlob(AST):
    def __init__(self) -> None:
        super().__init__()
        self.path_items = None
        
        
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
        self.id = None
        self.ty = None
        self.expr = None
        
class TypeItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type = None
        self.id = None
        self.ty = None
        
class FnItem(AST):
    def __init__(self) -> None:
        super().__init__()
        self.fn = None
        self.id = None
        self.generic_params = None
        self.fn_params = None
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
        self.id = None
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
        self.id = None
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
        self.fn_params = None
        
class FnParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        self.ty_sum = None
        
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
        self.id = None
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
        self.id = None
        self.ty_sum = None
        self.expr = None
        
class MemberFnParams(AST):
    def __init__(self) -> None:
        super().__init__()
        self.member_fn_params = None
        
class SelfParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.self = None
        
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
        self.path = None
        self.path_ids = None
        
class Pat(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        
class PatField(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pat = None
        self.ty_sum = None
        
class TySum(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty = None
        self.ty_param_bounds = None
        
class Ty(AST):
    def __init__(self) -> None:
        super().__init__()
        self.ty = None

class TyParam(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.ty_param_bounds = None
        
class TypePathSegment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
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