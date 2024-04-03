from .ast import AST, NodeVisitor, Identifier, Constant, Expression, Char, BinaryOp, UnaryOp
from typing import List, Union


class TranslationUnit(AST):
    def __init__(self, declarations) -> None:
        super().__init__()
        self.declarations = declarations


class Function(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers = None
        self.declarator: Union[InitDeclarator, Declarator, None] = None
        self.declarations = None
        self.compound_statement = None


class Structure(AST):
    def __init__(self) -> None:
        super().__init__()
        self.structure_type = None
        self.id = None
        self.declarations = None


class StructDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specifier_qualifiers = None
        self.declarators = None
        self.static_assert = None


class StructDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declarator = None
        self.expression = None


class Declarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pointer = None
        self.direct_declarator: DirectDeclaractor = None


class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers: List[AST] = None
        self.init_declarator_list: List[InitDeclarator] = None
        self.static_assert = None
        self.extern_C: CompoundStatement = None
        self.gnu_attribute = None


class Pointer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type_qualifiers = None


class DirectDeclaractor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.declarator: Declarator = None
        self.sub_nodes: List[DirectDeclaractorPostfix] = []
        self.is_function = False


class DirectDeclaractorPostfix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.static_head = None
        self.static_foot = None
        self.type_qualifiers = None
        self.assignment_expr = None
        self.parameter_list = None
        self.identifier_list = None


class DirectAbstractDeclaractor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_nodes = []


class DirectAbstractDeclaractorPostfix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.static_head = None
        self.static_foot = None
        self.type_qualifiers = []
        self.assignment_expr = None


class CastExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type_names = None
        self.expr: UnaryExpression = None
        self.initializer_list = None


class ConditionalExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.condition_expr: Union[BinaryOp, CastExpression] = None
        self.value_true = None
        self.value_false = None


class UnaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr: Union[PostfixExpression, CastExpression, UnaryOp] = None
        self.keyword = None
        self.initializer_list = None


class PostfixExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.primary_expr: PrimaryExpression = None
        self.type_name = None
        self.initializer_list = None
        self.sub_nodes = None


class PrimaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_node: Union[Identifier, Constant, Expression, Char, GenericSelection] = None
        self.sticky_strings = None


class TypeSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.sub_node = None


class EnumSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.id: Identifier = None
        self.enumerators = []


class Enumerator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.const_expr = None


class GenericSelection(AST):
    def __init__(self) -> None:
        super().__init__()
        self.assignment_expr = None
        self.generic_assoc_list = None


class GenericAssociation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.type_name = None
        self.assignment_expr = None


class StaticAssertDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.string = None


class TypeName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specifier_qualifiers = None
        self.abstract_declarator = None


class ParameterDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_sepcifiers = None
        self.declarator = None
        self.abstract_declarator = None


class AbstractDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pointer = None
        self.direct_abstract_declarator = None


class AssignmentExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr: ConditionalExpression = None
        self.assign_op = None
        self.assignment_expr = None


class InitDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declarator: Declarator = None
        self.initializer = None


class Initializer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.assignment_expr = None
        self.initializer_list = None


class DesignationInitializer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.designation = None
        self.initializer = None


class Designation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.designators = None


class Designator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.const_expr = None
        self.id = None


class CompoundStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_nodes = None


class LabeledStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.keyword = None
        self.const_expr = None
        self.stmt = None


class ExpressionStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None


class SelectionStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.if_keyword = None
        self.expr = None
        self.if_stmt = None
        self.else_stmt = None
        self.else_keyword = None


class IterationStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.while_keyword = None
        self.expr = None
        self.stmt = None


class JumpStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.expr = None


class Group(AST):
    def __init__(self) -> None:
        super().__init__()
        self.group_parts = None


class IfSection(AST):
    def __init__(self) -> None:
        super().__init__()
        self.group = None


class IfGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.id: Identifier = None
        self.group = None


class ElifGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.group = None


class ElseGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.group = None


class EndifLine(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None


class ControlLine(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.id: Identifier = None
        self.header_name = None
        self.parameters: List[Identifier] = None
        self.parameterization = None
        self.pp_tokens = None
        self.group = None


class HeaderName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.file_path = None


class PPtoken(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value: str = value
        self.is_leaf_ast = True
        value = self.value.replace("\\", "\\\\").replace('"', '\\"')
        self.node_info += f"\\n{value}"


class GNU_C_Assembly(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.asm_qualifier = None
        self.sticky_strings = None
