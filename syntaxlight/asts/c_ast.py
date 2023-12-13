

from .ast import AST, NodeVisitor, Identifier, Constant, Expression, Char
from typing import List, Union

class TranslationUnit(AST):
    def __init__(self, declarations) -> None:
        super().__init__()
        self.declarations = declarations

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declarations)
        return super().visit(node_visitor)


class Function(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers = None
        self.declarator: Union[InitDeclarator, Declarator, None] = None
        self.declarations = None
        self.compound_statement = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declaration_specifiers)
        node_visitor.link(self, self.declarator)
        node_visitor.link(self, self.declarations)
        node_visitor.link(self, self.compound_statement)
        return super().visit(node_visitor)


class Structure(AST):
    def __init__(self) -> None:
        super().__init__()
        self.structure_type = None
        self.id = None
        self.declarations = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.structure_type)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.declarations)
        return super().visit(node_visitor)


class StructDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specifier_qualifiers = None
        self.declarators = None
        self.static_assert = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.specifier_qualifiers)
        node_visitor.link(self, self.declarators)
        node_visitor.link(self, self.static_assert)
        return super().visit(node_visitor)


class StructDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declarator = None
        self.expression = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declarator)
        node_visitor.link(self, self.expression)
        return super().visit(node_visitor)


class Declarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pointer = None
        self.direct_declarator: DirectDeclaractor = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.pointer)
        node_visitor.link(self, self.direct_declarator)
        return super().visit(node_visitor)


class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers: List[AST] = None
        self.init_declarator_list: List[InitDeclarator] = None
        self.static_assert = None
        self.extern_C: CompoundStatement = None
        self.gnu_attribute = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declaration_specifiers)
        node_visitor.link(self, self.init_declarator_list)
        node_visitor.link(self, self.static_assert)
        node_visitor.link(self, self.extern_C)
        node_visitor.link(self, self.gnu_attribute)
        return super().visit(node_visitor)


class Pointer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type_qualifiers = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.type_qualifiers)
        return super().visit(node_visitor)


class DirectDeclaractor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.declarator: Declarator = None
        self.sub_nodes: List[DirectDeclaractorPostfix] = []
        self.is_function = False

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.declarator)
        node_visitor.link(self, self.sub_nodes)
        return super().visit(node_visitor)


class DirectDeclaractorPostfix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.static_head = None
        self.static_foot = None
        self.type_qualifiers = None
        self.assignment_expr = None
        self.parameter_list = None
        self.identifier_list = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.static_head)
        node_visitor.link(self, self.type_qualifiers)
        node_visitor.link(self, self.static_foot)
        node_visitor.link(self, self.parameter_list)
        node_visitor.link(self, self.identifier_list)
        node_visitor.link(self, self.assignment_expr)
        return super().visit(node_visitor)


class DirectAbstractDeclaractor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_nodes = []

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.sub_nodes)
        return super().visit(node_visitor)


class DirectAbstractDeclaractorPostfix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.static_head = None
        self.static_foot = None
        self.type_qualifiers = []
        self.assignment_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.static_head)
        node_visitor.link(self, self.type_qualifiers)
        node_visitor.link(self, self.static_foot)
        node_visitor.link(self, self.assignment_expr)
        return super().visit(node_visitor)


class CastExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type_names = None
        self.expr = None
        self.initializer_list = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.type_names)
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.initializer_list)
        return super().visit(node_visitor)


class UnaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.keyword = None
        self.initializer_list = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.initializer_list)
        return super().visit(node_visitor)


class PostfixExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.primary_expr: PrimaryExpression = None
        self.type_name = None
        self.initializer_list = None
        self.sub_nodes = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.primary_expr)
        node_visitor.link(self, self.type_name)
        node_visitor.link(self, self.initializer_list)
        node_visitor.link(self, self.sub_nodes)
        return super().visit(node_visitor)


class PrimaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_node: Union[Identifier, Constant, Expression, Char, GenericSelection] = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.sub_node)
        return super().visit(node_visitor)


class TypeSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.sub_node = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.sub_node)
        return super().visit(node_visitor)


class EnumSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.id: Identifier = None
        self.enumerators = []

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.enumerators)
        return super().visit(node_visitor)


class Enumerator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.const_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.const_expr)
        return super().visit(node_visitor)


class GenericSelection(AST):
    def __init__(self) -> None:
        super().__init__()
        self.assignment_expr = None
        self.generic_assoc_list = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.assignment_expr)
        node_visitor.link(self, self.generic_assoc_list)
        return super().visit(node_visitor)


class GenericAssociation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.type_name = None
        self.assignment_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.type_name)
        node_visitor.link(self, self.assignment_expr)
        return super().visit(node_visitor)


class StaticAssertDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.string = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.const_expr)
        node_visitor.link(self, self.string)
        return super().visit(node_visitor)


class TypeName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specifier_qualifiers = None
        self.abstract_declarator = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.specifier_qualifiers)
        node_visitor.link(self, self.abstract_declarator)
        return super().visit(node_visitor)


class ParameterDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_sepcifiers = None
        self.declarator = None
        self.abstract_declarator = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declaration_sepcifiers)
        node_visitor.link(self, self.declarator)
        node_visitor.link(self, self.abstract_declarator)
        return super().visit(node_visitor)


class AbstractDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pointer = None
        self.direct_abstract_declarator = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.pointer)
        node_visitor.link(self, self.direct_abstract_declarator)
        return super().visit(node_visitor)


class AssignmentExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.assign_op = None
        self.assignment_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.assign_op)
        node_visitor.link(self, self.assignment_expr)
        return super().visit(node_visitor)


class InitDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declarator: Declarator = None
        self.initializer = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declarator)
        node_visitor.link(self, self.initializer)
        return super().visit(node_visitor)


class Initializer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.assignment_expr = None
        self.initializer_list = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.assignment_expr)
        node_visitor.link(self, self.initializer_list)
        return super().visit(node_visitor)


class DesignationInitializer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.designation = None
        self.initializer = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.designation)
        node_visitor.link(self, self.initializer)
        return super().visit(node_visitor)


class Designation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.designators = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.designators)
        return super().visit(node_visitor)


class Designator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.const_expr = None
        self.id = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.const_expr)
        node_visitor.link(self, self.id)
        return super().visit(node_visitor)


class CompoundStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_nodes = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.sub_nodes)
        return super().visit(node_visitor)


class LabeledStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.keyword = None
        self.const_expr = None
        self.stmt = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.const_expr)
        node_visitor.link(self, self.stmt)
        return super().visit(node_visitor)


class ExpressionStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.expr)
        return super().visit(node_visitor)


class SelectionStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.if_keyword = None
        self.expr = None
        self.if_stmt = None
        self.else_stmt = None
        self.else_keyword = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.if_keyword)
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.if_stmt)
        node_visitor.link(self, self.else_keyword)
        node_visitor.link(self, self.else_stmt)
        return super().visit(node_visitor)


class IterationStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.while_keyword = None
        self.expr = None
        self.stmt = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        # while for do ...
        node_visitor.link(self, self.while_keyword)
        node_visitor.link(self, self.expr)
        node_visitor.link(self, self.stmt)
        return super().visit(node_visitor)


class JumpStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.expr)
        return super().visit(node_visitor)


class Group(AST):
    def __init__(self) -> None:
        super().__init__()
        self.group_parts = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.group_parts)
        return super().visit(node_visitor)


class IfSection(AST):
    def __init__(self) -> None:
        super().__init__()
        self.group = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.group)
        return super().visit(node_visitor)


class IfGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.id: Identifier = None
        self.group = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.const_expr)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.group)
        return super().visit(node_visitor)


class ElifGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.const_expr = None
        self.group = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.const_expr)
        node_visitor.link(self, self.group)
        return super().visit(node_visitor)


class ElseGroup(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.group = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.group)
        return super().visit(node_visitor)


class EndifLine(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        return super().visit(node_visitor)


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

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.header_name)
        node_visitor.link(self, self.parameters)
        node_visitor.link(self, self.parameterization)
        node_visitor.link(self, self.pp_tokens)
        node_visitor.link(self, self.group)
        return super().visit(node_visitor)


class HeaderName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.file_path = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.file_path)
        return super().visit(node_visitor)


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
