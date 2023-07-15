from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, CTokenType, CTokenSet
from ..error import ErrorCode
from ..ast import (
    AST,
    String,
    Keyword,
    UnaryOp,
    BinaryOp,
    ConditionalExpression,
    Identifier,
    Constant,
    Expression,
    AssignOp,
)
from typing import List
from enum import Enum


class TranslationUnit(AST):
    def __init__(self, declarations) -> None:
        super().__init__()
        self.declarations = declarations

    def visit(self, node_visitor: NodeVisitor = None):
        for declaration in self.declarations:
            node_visitor.link(self, declaration)
        return super().visit(node_visitor)


class Function(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers = None
        self.declarator = None
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
        if self.id:
            node_visitor.link(self.id)
        if self.declarations:
            for declaration in self.declarations:
                node_visitor.link(self, declaration)
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
        if self.declarator:
            node_visitor.link(self, self.declarator)
        if self.expression:
            node_visitor.link(self, self.expression)
        return super().visit(node_visitor)


class Declarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pointer = None
        self.direct_declarator = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.pointer)
        node_visitor.link(self, self.direct_declarator)
        return super().visit(node_visitor)


class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declaration_specifiers = None
        self.init_declarator_list = None
        self.static_assert = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.declaration_specifiers)
        node_visitor.link(self, self.init_declarator_list)
        node_visitor.link(self, self.static_assert)
        return super().visit(node_visitor)


class Pointer(AST):
    def __init__(self) -> None:
        super().__init__()
        self.type_qualifiers = None

    def visit(self, node_visitor: NodeVisitor = None):
        for type_qualifier in self.type_qualifiers:
            node_visitor.link(self, type_qualifier)
        return super().visit(node_visitor)


class DirectDeclaractor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.sub_nodes = []

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
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

    def visit(self, node_visitor: NodeVisitor = None):
        if self.type_names:
            for type_name in self.type_names:
                node_visitor.link(self, type_name)
        if self.expr:
            node_visitor.link(self, self.expr)
        return super().visit(node_visitor)


class UnaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.keyword = None
        self.initializer_list = None


class PostfixExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.primary_expr = None
        self.sub_nodes = None

    def visit(self, node_visitor: NodeVisitor = None):
        for sub_node in self.sub_nodes:
            node_visitor.link(self, sub_node)
        return super().visit(node_visitor)


class PrimaryExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sub_node = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.sub_node)
        return super().visit(node_visitor)


class TypeSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.sub_node = None

    def visit(self, node_visitor: NodeVisitor = None):
        if self.keyword:
            node_visitor.link(self, self.keyword)
        if self.sub_node:
            node_visitor.link(self, self.sub_node)
        return super().visit(node_visitor)


class EnumSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.id = None
        self.enumerators = []

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        if self.id:
            node_visitor.link(self, self.id)
        for enumerator in self.enumerators:
            node_visitor.link(self, enumerator)
        return super().visit(node_visitor)


class Enumerator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.constant_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        if self.constant_expr:
            node_visitor.link(self, self.constant_expr)
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
        self.constant_expr = None
        self.string = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.constant_expr)
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
        self.declarator = None
        self.abstract_declarator = None

    def visit(self, node_visitor: NodeVisitor = None):
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
        self.unary_expr = None
        self.assign_op = None
        self.assignment_expr = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.unary_expr)
        node_visitor.link(self, self.assign_op)
        node_visitor.link(self, self.assignment_expr)
        return super().visit(node_visitor)


class InitDeclarator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.declarator = None
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
        self.designator = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.designator)
        return super().visit(node_visitor)


class Designator(AST):
    def __init__(self) -> None:
        super().__init__()
        self.constant_expr = None
        self.id = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.constant_expr)
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
        self.id = None
        self.keyword = None
        self.statement = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.statement)
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
        self.if_stmt = None
        self.else_stmt = None
        self.else_keyword = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.if_keyword)
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


class CParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)
        self.cfirst_set = CTokenSet()

    def parse(self):
        self.node = self.translation_unit()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.node

    def translation_unit(self):
        """
        <translation-unit> ::= {<external-declaration>}*
        """
        declarations = []
        while self.current_token.type in self.cfirst_set.external_declaration:
            declarations.append(self.external_declaration())
        return TranslationUnit(declarations)

    def external_declaration(self):
        """
        <external-declaration> ::= <function-definition>
                                 | <declaration>

        在这里没有办法区分, 需要查看 <declarator> 后面是否有<declaration>* 和 <compound-statement> 才可以确定是 <function-definition>
        """
        # 没有类型, 即 main() 可以确定是 function_definition
        if self.current_token.type in self.cfirst_set.declarator:
            return self.function_definition()
        elif self.current_token.type in self.cfirst_set.declaration:
            return self.declaration()
        else:  # pragma: no cover
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                "token type should inside function definition and declaration",
            )

    def function_definition(self):
        """
        <function-definition> ::= <declaration-specifier>* <declarator> <declaration>* <compound-statement>
        """
        node = Function()
        declaration_specifiers = []
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_specifiers.append(self.declaration_sepcifier())
        node.update(declaration_specifiers=declaration_specifiers)
        node.update(declarator=self.declarator())
        declarations = []
        while self.current_token.type in self.cfirst_set.declaration:
            declarations.append(self.declaration())
        node.update(declarations=declarations)
        node.update(compound_statement=self.compound_statement())
        return node

    def declaration_sepcifier(self):
        """
        <declaration-specifier> ::= <storage-class-specifier>
                                  | <type-specifier>
                                  | <type-qualifier>
                                  | <function-specifier>
                                  | <alignment-specifier>
        """
        if self.current_token.type in self.cfirst_set.storage_class_specifier:
            node = self.storage_class_specifier()
        elif self.current_token.type in self.cfirst_set.type_specifier:
            node = self.type_specifier()
        elif self.current_token.type in self.cfirst_set.type_qualifier:
            node = self.type_qualifier()
        elif self.current_token.type in self.cfirst_set.function_speficier:
            node = self.function_specifier()
        elif self.current_token.type in self.cfirst_set.alignment_specifier:
            node = self.alignment_specifier()
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN, "should be StorageType or BaseType or QualifyType"
            )

        return node

    def storage_class_specifier(self):
        """
        <storage-class-specifier> ::= 'auto'
                                    | 'register'
                                    | 'static'
                                    | 'extern'
                                    | 'typedef'
        """
        node = Keyword(self.current_token.value)
        node.class_name = "StorageType"
        node.register_token(self.eat(self.current_token.type))
        return node

    def type_specifier(self):
        """
        <type-specifier> ::= void
                           | char
                           | short
                           | int
                           | long
                           | float
                           | double
                           | signed
                           | unsigned
                           | _Bool
                           | _Complex
                           | <atomic-type-specifier>
                           | <struct-or-union-specifier>
                           | <enum-specifier>
                           | <typedef-name>
        """
        if self.current_token.type in self.cfirst_set.atomic_type_specifier:
            node = self.atomic_type_specifier()
        elif self.current_token.type in self.cfirst_set.struct_or_union_specifier:
            node = self.struct_or_union_specifier()
        elif self.current_token.type in self.cfirst_set.enum_specifier:
            node = self.enum_specifier()
        elif self.current_token.type in self.cfirst_set.typedef_name:
            node = self.typedef_name()
        elif self.current_token.type in self.cfirst_set.type_specifier:
            node = Keyword(self.current_token.value)
            node.class_name = "BaseType"
            node.register_token(self.eat(self.current_token.type))

        else:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier")

        return node

    def function_specifier(self):
        """
        <function-specifier> ::= inline
                               | _Noreturn
        """
        node = Keyword(self.current_token.value)
        node.class_name = "FunctionType"
        node.register_token(self.eat(self.current_token.type))

        return node

    def alignment_specifier(self):
        """
        <alignment-specifier> ::= _Alignas "(" <type-name> ")"
                                | _Alignas "(" <constant-expression> ")"
        """
        node = TypeSpecifier()
        node.class_name = "alignment-specifier"
        keyword = Keyword(self.current_token.value)
        keyword.register_token(self.eat(CTokenType._ALIGNAS))
        node.update(keyword=keyword)
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.cfirst_set.type_name:
            node.update(sub_node=self.type_name())
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.cfirst_set.constant_expression:
            node.update(sub_node=self.constant_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type-name or constant-expression")
        return node

    def atomic_type_specifier(self):
        """
        <atomic-type-specifier> ::= _Atomic "(" <type-name> ")"
        """
        node = TypeSpecifier()
        node.class_name = "atomic-type-specifier"
        keyword = Keyword(self.current_token.value)
        keyword.register_token(self.eat(CTokenType._ATOMIC))
        node.update(keyword=keyword)
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(sub_node=self.type_name())
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def struct_or_union_specifier(self):
        """
        <struct-or-union-specifier> ::= <struct-or-union> <identifier> ("{" {<struct-declaration>}* "}")?
                                      | <struct-or-union>              "{" {<struct-declaration>}* "}"
        """
        if self.current_token.type not in self.cfirst_set.struct_or_union_specifier:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be struct or union")

        node = Structure()
        node.update(structure_type=self.struct_or_union())
        if self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
        else:
            # 匿名 struct
            if self.current_token.type != TokenType.LPAREN:
                self.error(
                    ErrorCode.UNEXPECTED_TOKEN,
                    "Declaration of anonymous struct must be a definition",
                )
        # struct or union 有定义 {}
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            struct_declarations = []
            while self.current_token.type in self.cfirst_set.struct_declaration:
                struct_declarations.append(self.struct_declaration())
            node.update(declarations=struct_declarations)
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

            # 匿名 struct 且未定义成员
            if len(struct_declarations) == 0 and node.id is None:
                self.warning("unnamed struct/union that defines no instances", node)

        return node

    def struct_or_union(self):
        """
        <struct-or-union> ::= "struct"
                            | "union"
        """
        node = Keyword(self.current_token.value)
        node.class_name = "StructureType"
        node.register_token(self.eat(self.current_token.type))

        return node

    def struct_declaration(self):
        """
        <struct-declaration> ::= <specifier-qualifier-list> <struct-declarator-list>? ";"
                               | <static_assert-declaration>
        """
        node = StructDeclaration()
        if self.current_token.type in self.cfirst_set.static_assert_declaration:
            node.update(static_assert=self.static_assert_declaration())
            return node

        node.update(specifier_qualifiers=self.specifier_qualifier_list())
        if self.current_token.type in self.cfirst_set.struct_declarator_list:
            node.update(declarators=self.struct_declarator_list())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def specifier_qualifier_list(self) -> List[AST]:
        """
        <specifier-qualifier> ::= <type-specifier> <specifier-qualifier>?
                                | <type-qualifier> <specifier-qualifier>?
        """
        result = []
        while self.current_token.type in self.cfirst_set.specifier_qualifier_list:
            if self.current_token.type in self.cfirst_set.type_specifier:
                result.append(self.type_specifier())
            else:
                result.append(self.type_qualifier())
        return result

    def struct_declarator_list(self) -> List[AST]:
        """
        <struct-declarator-list> ::= <struct-declarator> ("," <struct-declarator>)*
        """
        result = [self.struct_declarator()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.struct_declarator())
        return result

    def struct_declarator(self):
        """
        <struct-declarator> ::= <declarator> (":" <constant-expression>)?
                              | ":" <constant-expression>
        """
        node = StructDeclarator()
        if self.current_token.type in self.cfirst_set.declarator:
            node.update(declarator=self.declarator())
            # 位宽
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
                node.update(expression=self.constant_expression())
        elif self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(expression=self.constant_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "struct declarator should match declarator or :")
        return node

    def declarator(self):
        """
        <declarator> ::= {<pointer>}? <direct-declarator>
        """
        node = Declarator()
        if self.current_token.type == TokenType.MUL:
            node.update(pointer=self.pointer())
        node.update(direct_declarator=self.direct_declaractor())
        return node

    def pointer(self):
        """
        <pointer> ::= "*" ({<type-qualifier>}? "*"?)*
        """
        node = Pointer()
        # 对于二义性的 * 将其属性从 TokenType.MUL 改为 CTokenType.POINTER
        if self.current_token.type == TokenType.MUL:
            self.current_token.type = CTokenType.POINTER
            node.register_token(self.eat(CTokenType.POINTER))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be * as pointer")

        type_qualifiers = []
        while (
            self.current_token.type == TokenType.MUL
            or self.current_token.type in self.cfirst_set.type_qualifier
        ):
            if self.current_token.type == TokenType.MUL:
                self.current_token.type = CTokenType.POINTER
                node.register_token(self.eat(CTokenType.POINTER))
            else:
                type_qualifiers.append(self.type_qualifier())
        node.update(type_qualifiers=type_qualifiers)
        return node

    def type_qualifier(self):
        """
        <type-qualifier> ::= const
                           | volatile
                           | restrict
                           | _Atomic
        """
        node = Keyword(self.current_token.value)
        node.class_name = "QualifyType"
        node.register_token(self.eat(self.current_token.type))

        return node

    def direct_declaractor(self):
        """
        <direct-declarator> ::= <identifier>
                              | "(" <declarator> ")"
                              | <direct-declarator> "[" <type-qualifier-list>? <assignment-expression>? "]"
                              | <direct-declarator> "[" static <type-qualifier-list>? <assignment-expression> "]"
                              | <direct-declarator> "[" <type-qualifier-list> static <assignment-expression> "]"
                              | <direct-declarator> "[" <type-qualifier-list>? "*" "]"
                              | <direct-declarator> "(" <parameter-list> ")"
                              | <direct-declarator> "(" (<identifier-list>)? ")"
        """
        node = DirectDeclaractor()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(id=self.declarator())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id or (")

        # 先在这里统一保存, 后续根据 token [] () 来分析具体的 [3](int,int)[4]
        sub_nodes = []
        while self.current_token.type in (TokenType.LPAREN, TokenType.LSQUAR_PAREN):
            sub_node = DirectDeclaractorPostfix()
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                sub_node.register_token(self.eat(TokenType.LSQUAR_PAREN))

                if self.current_token.type == CTokenType.STATIC:
                    keyword = Keyword(self.current_token.value)
                    keyword.class_name = "StorageType"
                    keyword.register_token(self.eat(CTokenType.STATIC))
                    sub_node.update(static_head=keyword)

                if self.current_token.type in self.cfirst_set.type_qualifier:
                    sub_node.update(type_qualifiers=self.type_qualifier_list())

                if self.current_token.type == CTokenType.STATIC:
                    if sub_node.static_head is not None:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, "multi static")
                    keyword = Keyword(self.current_token.value)
                    keyword.class_name = "StorageType"
                    keyword.register_token(self.eat(CTokenType.STATIC))
                    sub_node.update(static_foot=keyword)

                if self.current_token.type == TokenType.MUL:
                    self.current_token.type = CTokenType.STAR
                    sub_node.register_token(self.eat(CTokenType.STAR))
                elif self.current_token.type in self.cfirst_set.assignment_expression:
                    sub_node.update(assignment_expr=self.assignment_expression())

                sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))

            if self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.parameter_list:
                    sub_node.update(parameter_list=self.parameter_list())
                elif self.current_token.type in self.cfirst_set.identifier:
                    sub_node.update(identifier_list=self.identifier_list())
                node.register_token(self.eat(TokenType.RPAREN))

            sub_nodes.append(sub_node)

        node.update(sub_nodes=sub_nodes)
        return node

    def type_qualifier_list(self) -> List[AST]:
        """
        <type-qualifier-list> ::= <type-qualifier>+
        """
        result = []
        while self.current_token.type in self.cfirst_set.type_qualifier:
            result.append(self.type_qualifier())
        return result

    def parameter_list(self) -> List[AST]:
        """
        <parameter-list> ::= <parameter-declaration> ("," <parameter-declaration>)* ("," "...")?
        """
        result = [self.parameter_declaration()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            if self.current_token.type in self.cfirst_set.parameter_declaration:
                result.append(self.parameter_declaration())
            elif self.current_token.type == TokenType.VARARGS:
                self.eat(TokenType.VARARGS)
                break
        return result

    def identifier_list(self) -> List[AST]:
        """
        <identifier-list> ::= <identifier> ("," <identifier>)*
        """
        result = [self.identifier()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.identifier())
        return result

    def constant_expression(self):
        """
        <constant-expression> ::= <conditional-expression>
        """
        return self.conditional_expression()

    def conditional_expression(self) -> ConditionalExpression:
        """
        <conditional-expression> ::= <logical-or-expression> ("?" <expression> ":" <conditional-expression>)?
        """
        node = ConditionalExpression()
        node.update(condition_expr=self.logical_or_expression())
        if self.current_token.type == TokenType.QUSTION:
            node.register_token(self.eat(TokenType.QUSTION))
            node.update(value_true=self.expression())
            node.register_token(self.eat(TokenType.COLON))
            node.update(value_false=self.conditional_expression())
        return node

    def _binary_expression(self, token_types: List[Enum], func):
        """
        方便后面优先级运算符调用

        为了避免大量的AST嵌套, 简化过程, 如果没有 expr_rights 则直接返回 expr_left
        """
        expr_left = func()
        if self.current_token.type not in token_types:
            return expr_left

        node = BinaryOp()
        node.update(expr_left=expr_left)
        expr_rights = []
        while self.current_token.type in token_types:
            if self.current_token.type == TokenType.LANGLE_BRACE:
                self.current_token.type = TokenType.LT
            elif self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = TokenType.GT
            node.register_token(self.eat(self.current_token.type))
            expr_rights.append(func())
        node.update(expr_rights=expr_rights)
        return node

    def logical_or_expression(self):
        """
        <logical-or-expression> ::= <logical-and-expression> ("||" <logical-and-expression>)*
        """
        return self._binary_expression([TokenType.OR], self.logical_and_expression)

    def logical_and_expression(self):
        """
        <logical-and-expression> ::= <inclusive-or-expression> ("&&" <inclusive-or-expression>)*
        """
        return self._binary_expression([TokenType.AND], self.inclusive_or_expression)

    def inclusive_or_expression(self):
        """
        <inclusive-or-expression> ::= <exclusive-or-expression> ("|" <exclusive-or-expression>)*
        """
        return self._binary_expression([TokenType.PIPE], self.exclusive_or_expression)

    def exclusive_or_expression(self):
        """
        <exclusive-or-expression> ::= <and-expression> ("^" <and-expression>)*
        """
        return self._binary_expression([TokenType.CARET], self.and_expression)

    def and_expression(self):
        """
        <and-expression> ::= <equality-expression> ("&" <equality-expression>)*
        """
        return self._binary_expression([TokenType.AMPERSAND], self.equality_expression)

    def equality_expression(self):
        """
        <equality-expression> ::= <relational-expression> (("=="|"!=") <relational-expression>)*
        """
        return self._binary_expression([TokenType.EQ, TokenType.NE], self.relational_expression)

    def relational_expression(self):
        """
        <relational-expression> ::= <shift-expression> (("<"|">"|"<="|">=") <shift-expression>)*
        """

        return self._binary_expression(
            [TokenType.LANGLE_BRACE, TokenType.RANGLE_BRACE, TokenType.LE, TokenType.GE],
            self.shift_expression,
        )

    def shift_expression(self):
        """
        <shift-expression> ::= <additive-expression> (("<<" | ">>") <additive-expression>)*
        """
        return self._binary_expression([TokenType.SHL, TokenType.SHR], self.additive_expression)

    def additive_expression(self):
        """
        <additive-expression> ::= <multiplicative-expression> (("+"|"-") <multiplicative-expression>)*
        """
        return self._binary_expression(
            [TokenType.PLUS, TokenType.MINUS], self.multiplicative_expression
        )

    def multiplicative_expression(self):
        """
        <multiplicative-expression> ::= <cast-expression> (("*"|"/"|"%") <cast-expression>)*
        """
        return self._binary_expression(
            [TokenType.MUL, TokenType.DIV, TokenType.MOD], self.cast_expression
        )

    def cast_expression(self):
        """
        <cast-expression> ::= ("(" <type-name> ")")* <unary-expression>
        """
        node = CastExpression()
        type_names = []
        while self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            type_names.append(self.type_name())
            node.register_token(self.eat(TokenType.RPAREN))
        node.update(type_names=type_names)
        if self.current_token.type in self.cfirst_set.unary_expression:
            node.update(expr=self.unary_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be unary expression or (")
        return node

    def unary_expression(self):
        """
        <unary-expression> ::= <postfix-expression>
                             | "++" <unary-expression>
                             | "--" <unary-expression>
                             | <unary-operator> <cast-expression>
                             | sizeof <unary-expression>
                             | sizeof   "(" <type-name> ")" ( "{" <initializer-list> (",")? "}")?
                             | _Alignof "(" <type-name> ")"

        <unary-operator> ::= "&"
                           | "*"
                           | "+"
                           | "-"
                           | "~"
                           | "!"
        """
        node = UnaryExpression()
        if self.current_token.type in self.cfirst_set.postfix_expression:
            node.update(expr=self.postfix_expression())
        elif self.current_token.type in (TokenType.INC, TokenType.DEC):
            unary_expr = UnaryOp(op=self.current_token.value)
            unary_expr.register_token(self.eat(self.current_token.type))
            unary_expr.update(expr=self.unary_expression())
            node.update(expr=unary_expr)
        elif self.current_token.type in self.cfirst_set.unary_operator:
            unary_expr = UnaryOp(op=self.current_token.value)
            unary_expr.register_token(self.eat(self.current_token.type))
            unary_expr.update(expr=self.cast_expression())
            node.update(expr=unary_expr)
        elif self.current_token.type == CTokenType.SIZEOF:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(CTokenType.SIZEOF))
            node.update(keyword=keyword)

            # 这里的判断有点复杂, 因为 可以
            # A: sizeof "(" <type-name> ")"
            #
            # B: sizeof <unary-expression> => sizeof <postfix-expression> => sizeof <primary-expression>
            # => sizeof "(" <expression> ")"
            #
            # <expression>            ::= <assignment-expression> ...
            # <assignment-expression> ::= (<unary-expression> <assignment-operator>)* <conditional-expression>
            if (
                self.current_token.type in self.cfirst_set.unary_expression
                and self.current_token.type != TokenType.LPAREN
            ):
                node.update(expr=self.unary_expression())
            elif self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.type_name:
                    node.update(expr=self.type_name())
                    node.register_token(self.eat(TokenType.RPAREN))
                    # C23 移除了此写法
                    if self.current_token.type == TokenType.LCURLY_BRACE:
                        node.register_token(self.eat(TokenType.LCURLY_BRACE))
                        node.update(initializer_list=self.initializer_list())
                        if self.current_token.type == TokenType.COMMA:
                            node.register_token(self.eat(TokenType.COMMA))
                        node.register_token(self.eat(TokenType.RCURLY_BRACE))

                elif self.current_token.type in self.cfirst_set.expression:
                    node.update(expr=self.expression())
                    node.register_token(self.eat(TokenType.RPAREN))
                else:
                    self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type name or expression")

            else:
                self.error(
                    ErrorCode.UNEXPECTED_TOKEN, "sizeof should follow with unary expr or typename"
                )
        elif self.current_token.type == CTokenType._ALIGNOF:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(CTokenType._ALIGNOF))
            node.update(keyword=keyword)
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.type_name())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                "unary expression should follow with postfix or ++ or -- or unary operator or sizeof",
            )

        return node

    def postfix_expression(self):
        """
        <postfix-expression> ::= <primary-expression>
                               | <postfix-expression> "[" <expression> "]"
                               | <postfix-expression> "(" (<assignment-expression> ("," <assignment-expression>)*)? ")"
                               | <postfix-expression> "." <identifier>
                               | <postfix-expression> "->" <identifier>
                               | <postfix-expression> "++"
                               | <postfix-expression> "--"
        """
        node = PostfixExpression()
        if self.current_token.type not in self.cfirst_set.postfix_expression:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be ID or constant or string or (")
        node.update(primary_expr=self.primary_expression())
        sub_nodes = []
        while self.current_token.type in self.cfirst_set.postfix_expression_inside:
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                sub_nodes.append(self.expression())
                node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            elif self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.assignment_expression:
                    sub_nodes.append(self.assignment_expression())
                    while self.current_token.type == TokenType.COMMA:
                        node.register_token(self.eat(TokenType.COMMA))
                        sub_nodes.append(self.assignment_expression())
                node.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type == TokenType.DOT:
                node.register_token(self.eat(TokenType.DOT))
                sub_nodes.append(self.identifier())
            elif self.current_token.type == TokenType.POINT:
                node.register_token(self.eat(TokenType.POINT))
                sub_nodes.append(self.identifier())
            else:
                # ++ --
                node.register_token(self.eat(self.current_token.type))

        node.update(sub_nodes=sub_nodes)
        return node

    def primary_expression(self):
        """
        <primary-expression> ::= <identifier>
                               | <constant>
                               | <string>
                               | "(" <expression> ")"
                               | <generic-selection>
        """
        node = PrimaryExpression()
        if self.current_token.type == TokenType.ID:
            sub_node = self.identifier()
        elif self.current_token.type == TokenType.NUMBER:
            sub_node = Constant(self.current_token.value)
            sub_node.register_token(self.eat(self.current_token.type))
        elif self.current_token.type == TokenType.STRING:
            sub_node = String(self.current_token.value)
            sub_node.register_token(self.eat(self.current_token.type))
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            sub_node = self.expression()
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.cfirst_set.generic_selection:
            sub_node = self.generic_selection()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be ID or constant or string or (")

        node.update(sub_node=sub_node)
        return node

    def generic_selection(self):
        """
        <generic-selection> ::= _Generic "(" <assignment-expression> "," <generic-assoc-list> ")"
        """
        keyword = Keyword(self.current_token.value)
        keyword.register_token(self.eat(CTokenType._GENERIC))
        node = GenericSelection()
        node.update(keyword=keyword)
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(assignment_expr=self.assignment_expression())
        node.register_token(self.eat(TokenType.COMMA))
        node.update(generic_assoc_list=self.generic_assoc_list())
        return node

    def generic_assoc_list(self) -> List[AST]:
        """
        <generic-assoc-list> ::= <generic-association> ("," <generic-association>)*
        """
        result = [self.generic_association()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.generic_association())
        return result

    def generic_association(self):
        """
        <generic-association> ::= <type-name> ":" <assignment-expression>
                                | default ":" <assignment-expression>
        """
        node = GenericAssociation()
        if self.current_token.type == CTokenType.DEFAULT:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(CTokenType.DEFAULT))
            node.update(keyword=keyword)
        elif self.current_token.type in self.cfirst_set.type_name:
            node.update(type_name=self.type_name())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be default or type-name")
        node.register_token(self.eat(TokenType.COLON))
        node.update(assignment_expr=self.assignment_expression())
        return node

    def expression(self):
        """
        <expression> ::= <assignment-expression> ("," <assignment-expression>)*
        """
        node = Expression()
        exprs = [self.assignment_expression()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))
            exprs.append(self.assignment_expression())
        node.update(exprs=exprs)
        return node

    def assignment_expression(self):
        """
        <assignment-expression> ::= <unary-expression> <assignment-operator> <assignment-expression>
                                  | <conditional-expression>
        """
        # <conditional-expression> => <cast-expression> => ("(" <type-name> ")")* <unary-expression>
        # 无法 LL1 判断, 需要额外处理
        if self.current_token.type not in self.cfirst_set.assignment_expression:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN, "should be unary expression or conditional expression"
            )

        node = AssignmentExpression()
        expr = self.conditional_expression()
        if isinstance(expr.condition_expr, BinaryOp):
            # 含双目运算符, 必为 conditional expression
            node.update(expr=expr)
        elif isinstance(expr.condition_expr, CastExpression):
            # CastExpression 含 type_names 必为 conditional expression
            if expr.condition_expr.type_names is not None:
                node.update(expr=expr)
            else:
                # 纯 unary expression
                if self.current_token.type in self.cfirst_set.assignment_operator:
                    # 有赋值运算符, 是产生式A
                    node.update(assign_op=self.assignment_operator())
                    node.update(assignment_expr=self.assignment_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be conditional expr or unary expr")

        return node

    def assignment_operator(self):
        """
        <assignment-operator> ::= "="
                                | "*="
                                | "/="
                                | "%="
                                | "+="
                                | "-="
                                | "<<="
                                | ">>="
                                | "&="
                                | "^="
                                | "|="
        """
        node = AssignOp(self.current_token.value)
        node.register_token(self.current_token.type)
        return node

    def type_name(self):
        """
        <type-name> ::= {<specifier-qualifier>}+ {<abstract-declarator>}?
        """
        node = TypeName()
        specifier_qualifiers = []
        while self.current_token.type in self.cfirst_set.specifier_qualifier_list:
            specifier_qualifiers.append(self.specifier_qualifier_list())
        node.update(specifier_qualifiers=specifier_qualifiers)
        if self.current_token.type in self.cfirst_set.abstract_declarator:
            node.update(abstract_declarator=self.abstract_declarator())
        return node

    def parameter_declaration(self):
        """
        <parameter-declaration> ::= {<declaration-specifier>}+ <declarator>
                                  | {<declaration-specifier>}+ (<abstract-declarator>)?
        """
        node = ParameterDeclaration()
        declaration_sepcifiers = [self.declaration_sepcifier()]
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_sepcifiers.append(self.declaration_sepcifier())
        if self.current_token.type in self.cfirst_set.declarator:
            node.update(declarator=self.declarator())
        elif self.current_token.type in self.cfirst_set.abstract_declarator:
            node.update(abstract_declarator=self.abstract_declarator())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be declarator or abstract declarator")
        return node

    def abstract_declarator(self):
        """
        <abstract-declarator> ::= <pointer>
                                | <pointer> <direct-abstract-declarator>
                                | <direct-abstract-declarator>
        """
        node = AbstractDeclarator()
        if self.current_token.type == TokenType.MUL:
            pointer = self.pointer()
            node.update(pointer=pointer)
        if self.current_token.type in self.cfirst_set.direct_abstract_declarator:
            node.update(direct_abstract_declarator=self.direct_abstract_declarator())
        return node

    def direct_abstract_declarator(self):
        """
        <direct-abstract-declarator> ::=
                | "(" <abstract-declarator> ")"
                | <direct-abstract-declarator>? "(" <parameter-list>? ")"
                | <direct-abstract-declarator>? "[" <type-qualifier-list>? <assignment-expression>? "]"
                | <direct-abstract-declarator>? "[" static <type-qualifier-list>? <assignment-expression> "]"
                | <direct-abstract-declarator>? "[" <type-qualifier-list> static <assignment-expression> ]
                | <direct-abstract-declarator>? "[" "*" "]"
        """
        node = DirectAbstractDeclaractor()
        sub_nodes = []
        while self.current_token.type in (TokenType.LPAREN, TokenType.LSQUAR_PAREN):
            sub_node = DirectAbstractDeclaractorPostfix()
            if self.current_token.type == TokenType.LPAREN:
                sub_node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.abstract_declarator:
                    sub_node.update(expr=self.abstract_declarator())
                elif self.current_token.type in self.cfirst_set.parameter_list:
                    sub_node.update(expr=self.parameter_list())
                else:
                    self.error(
                        ErrorCode.UNEXPECTED_TOKEN,
                        "should be abstract declarator or parameter list",
                    )
                sub_node.register_token(self.eat(TokenType.RPAREN))
            else:
                sub_node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                if self.current_token.type == TokenType.MUL:
                    self.current_token.type = CTokenType.STAR
                    sub_node.register_token(self.eat(CTokenType.STAR))
                    sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                    sub_nodes.append(sub_node)
                    continue

                if self.current_token.type == CTokenType.STATIC:
                    keyword = Keyword(self.current_token.value)
                    keyword.class_name = "StorageType"
                    keyword.register_token(self.eat(CTokenType.STATIC))
                    sub_node.update(static_head=keyword)
                if self.current_token.type in self.cfirst_set.type_qualifier:
                    sub_node.update(type_qualifiers=self.type_qualifier_list())

                if self.current_token.type == CTokenType.STATIC:
                    if sub_node.static_head is not None:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, "multi static")
                    keyword = Keyword(self.current_token.value)
                    keyword.class_name = "StorageType"
                    keyword.register_token(self.eat(CTokenType.STATIC))
                    sub_node.update(static_foot=keyword)

                if self.current_token.type in self.cfirst_set.assignment_expression:
                    sub_node.update(assignment_expr=self.assignment_expression())

                sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                sub_nodes.append(sub_node)

        node.update(sub_nodes=sub_nodes)
        return node

    def enum_specifier(self):
        """
        <enum-specifier> ::= enum (<identifier>)? "{" <enumerator> ("," <enumerator>)* ","? "}"
                           | enum <identifier>
        """
        node = EnumSpecifier()
        keyword = Keyword(self.current_token.value)
        keyword.register_token(self.eat(CTokenType.ENUM))
        node.update(keyword=keyword)
        if self.current_token.type in self.cfirst_set.identifier:
            node.update(id=self.identifier())
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            enumerators = [self.enumerator()]
            while self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                if self.current_token.type == TokenType.RCURLY_BRACE:
                    break
                enumerators.append(self.enumerator())
            node.update(enumerators=enumerators)
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

        return node

    def enumerator(self):
        """
        <enumerator> ::= <identifier> ("=" <constant-expression>)?
        """
        node = Enumerator()
        node.update(id=self.identifier())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(constant_expr=self.constant_expression())
        return node

    def typedef_name(self):
        """
        <typedef-name> ::= <identifier>
        """
        node = Identifier(self.current_token.value)
        node.register_token(self.eat(CTokenType.TYPEDEF_ID))
        return node

    def declaration(self):
        """
        <declaration> ::= <declaration-specifier>+ (<init-declarator-list>)? ";"
                        | <static-assert-declaration>

        也有可能是 <function-definition>, 如果 <init-declarator-list> 的只有一个元素且没有 <initializer> 且后面跟着的是 <declaration>* <compound-statement>

        <function-definition> ::= <declaration-specifier>* <declarator> <declaration>* <compound-statement>
        """
        node = Declaration()
        if self.current_token.type in self.cfirst_set.static_assert_declaration:
            node.update(static_assert=self.static_assert_declaration())
            return node

        declaration_specifiers = []
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_specifiers.append(self.declaration_sepcifier())

        if self.current_token.type in self.cfirst_set.init_declarator_list:
            init_declarator_list = self.init_declarator_list()
            if self.current_token.type == TokenType.SEMI:
                node.update(init_declarator_list=init_declarator_list)
                node.register_token(self.eat(TokenType.SEMI))
                return node
            elif self._is_C_function(init_declarator_list):
                return self._build_C_function_definition(
                    declaration_specifiers, init_declarator_list[0]
                )
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "miss not declaration or function definition")
        if self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "miss ;")
        return node

    def _is_C_function(self, init_declarator_list: List[InitDeclarator]):
        """
        在 <declaration> 判断是否是 <function-definition>
        """
        if len(init_declarator_list) != 1:
            return False
        if init_declarator_list[0].initializer is not None:
            return False
        if (
            self.current_token.type in self.cfirst_set.compound_statement
            or self.current_token.type in self.cfirst_set.declaration
        ):
            return True
        return False

    def _build_C_function_definition(self, declaration_specifiers, declarator):
        """
        <function-definition> ::= <declaration-specifier>* <declarator> <declaration>* <compound-statement>

        <declaration> 中判断为 <function-definition>
        """
        node = Function()
        node.update(declaration_specifiers=declaration_specifiers)
        node.update(declarator=declarator)
        # TODO: 参数和 declaration 匹配
        declarations = []
        while self.current_token.type in self.cfirst_set.declaration:
            declarations.append(self.declaration())
        node.update(declarations=declarations)
        node.update(compound_statement=self.compound_statement())
        return node

    def init_declarator_list(self) -> List[AST]:
        """
        <init-declarator-list> ::= <init-declarator> ("," <init-declarator>)*
        """
        result = [self.init_declarator()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.init_declarator())
        return result

    def init_declarator(self):
        """
        <init-declarator> ::= <declarator> ("=" <initializer>)?
        """
        node = InitDeclarator()
        node.update(declarator=self.declarator())
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(initializer=self.initializer())
        return node

    def initializer(self):
        """
        <initializer> ::= <assignment-expression>
                        | "{" <initializer-list> "}"
                        | "{" <initializer-list> "," "}"
        """
        node = Initializer()
        if self.current_token.type in self.cfirst_set.assignment_expression:
            node.update(assignment_expr=self.assignment_expression())
        elif self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            node.update(initializer_list=self.initializer_list())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
            node.register_token(self.eat(TokenType.RCURLY_BRACE))
        else:
            self.error(
                ErrorCode.UNEXPECTED_TOKEN, "should be initializer list or assignment expression"
            )
        return node

    def initializer_list(self) -> List[AST]:
        """
        <initializer-list> ::= <designation>? <initializer> ("," <designation>? <initializer>)*
        """
        node = DesignationInitializer()
        if self.current_token.type in self.cfirst_set.designation:
            node.update(designation=self.designation())
        node.update(initializer=self.initializer())

        result = [node]

        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            node = DesignationInitializer()
            if self.current_token.type in self.cfirst_set.designation:
                node.update(designation=self.designation())
            node.update(initializer=self.initializer())
            result.append(node)
        return result

    def designation(self):
        """
        <designation> ::= <designator>+ "="
        """
        node = Designation()
        node.update(designator=self.designator())
        node.register_token(self.eat(TokenType.ASSIGN))
        return node

    def designator(self):
        """
        <designator> ::= "[" <constant-expression> "]"
                       | "." <identifier>
        """
        node = Designator()
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(constant_expr=self.constant_expression())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        elif self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            node.update(id=self.identifier())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be constant expression or id")
        return node

    def compound_statement(self):
        """
        <compound-statement> ::= "{" (<block-item>)* "}"

        <block-item> ::= <declaration>
                       | <statement>
        """
        node = CompoundStatement()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        sub_nodes = []
        while self.current_token.type in self.cfirst_set.block_item:
            if self.current_token.type in self.cfirst_set.declaration:
                sub_nodes.append(self.declaration())
            else:
                sub_nodes.append(self.statement())
        node.update(sub_nodes=sub_nodes)
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def statement(self):
        """
        <statement> ::= <labeled-statement>
                      | <expression-statement>
                      | <compound-statement>
                      | <selection-statement>
                      | <iteration-statement>
                      | <jump-statement>
        """
        # goto id
        if (
            self.current_token.type == TokenType.ID
            and self.peek_next_token().type == TokenType.COLON
        ):
            return self.labeled_statement()
        elif (
            self.current_token.type != TokenType.ID
            and self.current_token.type in self.cfirst_set.labeled_statement
        ):
            return self.labeled_statement()
        elif self.current_token.type in self.cfirst_set.expression_statement:
            return self.expression_statement()
        elif self.current_token.type in self.cfirst_set.compound_statement:
            return self.compound_statement()
        elif self.current_token.type in self.cfirst_set.selection_statement:
            return self.selection_statement()
        elif self.current_token.type in self.cfirst_set.iteration_statement:
            return self.iteration_statement()
        elif self.current_token.type in self.cfirst_set.jump_statement:
            return self.jump_statement()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be a statement")

    def labeled_statement(self):
        """
        <labeled-statement> ::= <identifier> ":" <statement>
                              | case <constant-expression> ":" <statement>
                              | default ":" <statement>
        """
        node = LabeledStatement()
        if self.current_token.type in self.cfirst_set.identifier:
            node.update(id=self.identifier())
        elif self.current_token.type in (CTokenType.CASE, CTokenType.DEFAULT):
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(keyword=keyword)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id or case or default")
        node.register_token(self.eat(TokenType.COLON))
        node.update(statement=self.statement())
        return node

    def expression_statement(self):
        """
        <expression-statement> ::= {<expression>}? ";"
        """
        node = ExpressionStatement()
        if self.current_token.type in self.cfirst_set.expression:
            node.update(expr=self.expression())
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def selection_statement(self):
        """
        <selection-statement> ::= if "(" <expression> ")" <statement>
                                | if "(" <expression> ")" <statement> else <statement>
                                | switch "(" <expression> ")" <statement>
        """
        node = SelectionStatement()
        if self.current_token.type in (CTokenType.IF, CTokenType.SWITCH):
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(if_keyword=keyword)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be if or switch")
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(expr=self.expression())
        node.register_token(self.eat(TokenType.RPAREN))
        node.update(if_stmt=self.statement())
        if self.current_token.type == CTokenType.ELSE:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(else_keyword=keyword)
            node.update(else_stmt=self.statement())
        return node

    def iteration_statement(self):
        """
        <iteration-statement> ::= while "(" <expression> ")" <statement>
                                | do <statement> while "(" <expression> ")" ";"
                                | for "(" {<expression>}? ";" {<expression>}? ";" {<expression>}? ")" <statement>
                                | for "(" <declaration> <expression>? ";" <expression>? ")" <statement>
        """
        node = IterationStatement()
        if self.current_token.type == CTokenType.WHILE:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(keyword=keyword)
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement())
        elif self.current_token.type == CTokenType.DO:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(keyword=keyword)
            node.update(stmt=self.statement())
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(while_keyword=keyword)
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == CTokenType.FOR:
            keyword = Keyword(self.current_token.value)
            keyword.register_token(self.eat(self.current_token.type))
            node.update(keyword=keyword)

            exprs = []
            node.register_token(self.eat(TokenType.LPAREN))
            # for "(" <declaration> <expression>? ";" <expression>? ")" <statement>
            if self.current_token.type in self.cfirst_set.declaration:
                node.update(declaration=self.declaration())
                if self.current_token.type in self.cfirst_set.expression:
                    exprs.append(self.expression())
                node.register_token(self.eat(TokenType.SEMI))
                if self.current_token.type in self.cfirst_set.expression:
                    exprs.append(self.expression())
                node.register_token(self.eat(TokenType.RPAREN))
                node.update(expr=exprs)
                node.update(stmt=self.statement())
            else:
                # for "(" {<expression>}? ";" {<expression>}? ";" {<expression>}? ")" <statement>
                if self.current_token.type in self.cfirst_set.expression:
                    exprs.append(self.expression())
                node.register_token(self.eat(TokenType.SEMI))
                if self.current_token.type in self.cfirst_set.expression:
                    exprs.append(self.expression())
                node.register_token(self.eat(TokenType.SEMI))
                if self.current_token.type in self.cfirst_set.expression:
                    exprs.append(self.expression())
                node.register_token(self.eat(TokenType.RPAREN))
                node.update(stmt=self.statement())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be while or do or for")
        return node

    def jump_statement(self):
        """
        <jump-statement> ::= goto <identifier> ";"
                           | continue ";"
                           | break ";"
                           | return {<expression>}? ";"
        """
        node = JumpStatement()
        if self.current_token.type in self.cfirst_set.jump_statement:
            if self.current_token.type == CTokenType.GOTO:
                keyword = Keyword(self.current_token.value)
                keyword.register_token(self.eat(self.current_token.type))
                node.update(keyword=keyword)
                node.update(expr=self.identifier())
            elif self.current_token.type == CTokenType.RETURN:
                keyword = Keyword(self.current_token.value)
                keyword.register_token(self.eat(self.current_token.type))
                node.update(keyword=keyword)
                if self.current_token.type in self.cfirst_set.expression:
                    node.update(expr=self.expression())
            else:
                keyword = Keyword(self.current_token.value)
                keyword.register_token(self.eat(self.current_token.type))
                node.update(keyword=keyword)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be goto continue break return")
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def identifier(self):
        """
        id
        """
        node = Identifier(self.current_token.value)
        node.register_token(self.eat(TokenType.ID))
        return node

    def static_assert_declaration(self):
        """
        <static_assert-declaration> ::= _Static_assert "(" <constant-expression> "," <string> ")"
        """
        node = StaticAssertDeclaration()
        keyword = Keyword(self.current_token.value)
        keyword.register_token(self.eat(CTokenType._STATIC_ASSERT))
        node.update(keyword=keyword)
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(constant_expr=self.constant_expression())
        node.register_token(self.eat(TokenType.COMMA))
        string = String(self.current_token.value)
        string.register_token(self.eat(TokenType.STRING))
        node.update(string=string)
        return node
