from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, CTokenType, CTokenSet
from ..error import ErrorCode
from ..ast import (
    AST,
    Object,
    Array,
    Pair,
    String,
    Number,
    Keyword,
    UnaryOp,
    BinaryOp,
    ConditionalExpression,
)
from typing import List


class TranslationUnit(AST):
    def __init__(self, declarations) -> None:
        super().__init__()
        self.declarations = declarations

    def visit(self, node_visitor: NodeVisitor = None):
        for declaration in self.declarations:
            node_visitor.link(self, declaration)
        return super().visit(node_visitor)


class Function(AST):
    def __init__(
        self, declaration_specifiers, declarator_list: List["Declarator"], compound_statement
    ) -> None:
        super().__init__()
        self.declaration_specifiers = declaration_specifiers
        self.declarator_list = declarator_list
        self.compound_statement = compound_statement

    def visit(self, node_visitor: NodeVisitor = None):
        for declaration_specifier in self.declaration_specifiers:
            node_visitor.link(self, declaration_specifier)
        for declarator in self.declarator_list:
            node_visitor.link(self, declarator)
        node_visitor.link(self, self.compound_statement)
        return super().visit(node_visitor)


class Structure(AST):
    def __init__(self) -> None:
        super().__init__()
        self.structure_type = None
        self.id = None
        self.declarations = None

    def update_id(self):
        for token in self._tokens:
            if token.type == TokenType.ID:
                self.id = token
                return

        assert False, "struct or union should have id by update_id not found!"  # pragma: no cover

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.structure_type)
        if self.declarations:
            for declaration in self.declarations:
                node_visitor.link(self, declaration)
        return super().visit(node_visitor)


class StructDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specifier_qualifiers = None
        self.declarators = None

    def visit(self, node_visitor: NodeVisitor = None):
        for specifier_qualifier in self.specifier_qualifiers:
            node_visitor.link(self, specifier_qualifier)
        for declarator in self.declarators:
            node_visitor.link(self, declarator)
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
        self.direct_declarator: DirectDeclaractor = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.pointer)
        node_visitor.link(self, self.direct_declarator)
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
        self.declarator: Declarator = None
        self.constant_expressions = None
        self.parameter_list = None

    def update_id(self):
        for token in self._tokens:
            if token.type == TokenType.ID:
                self.id = token
                return
        # 找到子 declarator 的子 DirectDeclaractor 的 id
        self.id = self.declarator.direct_declarator.id

    def visit(self, node_visitor: NodeVisitor = None):
        if self.declarator:
            node_visitor.link(self, self.declarator)
        for constant_expression in self.constant_expressions:
            node_visitor.link(self, constant_expression)

        for parameter in self.parameter_list:
            node_visitor.link(self, parameter)
        return super().visit(node_visitor)


class CParser(Parser):
    def __init__(self, lexer, skip_invisible_characters=True, skip_space=True):
        super().__init__(lexer, skip_invisible_characters, skip_space)
        self.cfirst_set = CTokenSet()

    def parse(self):
        self.node = self.translation_unit()
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
        """
        if self.current_token.type in self.cfirst_set.function_definition:
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
        <function-definition> ::= {<declaration-specifier>}* <declarator_list> (<compound-statement>)?
        """
        declaration_specifiers = []
        compound_statement = None
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_specifiers.append(self.declaration_sepcifier())
        declarator_list = self.declarator_list()
        if self.current_token.type in self.cfirst_set.compound_statement:
            compound_statement = self.compound_statement()
        return Function(declaration_specifiers, declarator_list, compound_statement)

    def declaration_sepcifier(self):
        """
        <declaration-specifier> ::= <storage-class-specifier>
                                  | <type-specifier>
                                  | <type-qualifier>
        """
        if self.current_token.type in self.cfirst_set.storage_class_specifier:
            node = self.storage_class_specifier()
        elif self.current_token.type in self.cfirst_set.type_specifier:
            node = self.type_specifier()
        elif self.current_token.type in self.cfirst_set.type_qualifier:
            node = self.type_qualifier()
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
        node.register_token(self.eat(self.current_token.type))
        node.class_name = "StorageType"
        return node

    def type_specifier(self):
        """
        <type-specifier> ::= 'void'
                           | 'char'
                           | 'short'
                           | 'int'
                           | 'long'
                           | 'float'
                           | 'double'
                           | 'signed'
                           | 'unsigned'
                           | <struct-or-union-specifier>
                           | <enum-specifier>
                           | <typedef-name>
        """
        if self.current_token.type in self.cfirst_set.struct_or_union_specifier:
            node = self.struct_or_union_specifier()
        elif self.current_token.type in self.cfirst_set.enum_specifier:
            node = self.enum_specifier()
        elif self.current_token.type in self.cfirst_set.typedef_name:
            node = self.typedef_name()
        elif self.current_token.type in self.cfirst_set.type_specifier:
            node = Keyword(self.current_token.value)
            node.register_token(self.eat(self.current_token.type))
            node.class_name = "BaseType"
        else:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier")

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
            node.register_token(self.eat(TokenType.ID))
            node.update_id()  # 手动更新一下 Structure 中的 id 信息
        else:
            # 匿名 struct
            if self.current_token.type != TokenType.LPAREN:
                self.error(
                    ErrorCode.UNEXPECTED_TOKEN,
                    "Declaration of anonymous struct must be a definition",
                )
        # struct or union 有定义 {}
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            struct_declarations = []
            while self.current_token.type in self.cfirst_set.struct_declaration:
                struct_declarations.append(self.struct_declaration())
            node.update(declarations=struct_declarations)
            node.register_token(self.eat(TokenType.RPAREN))

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
        node.register_token(self.eat(self.current_token.type))
        node.class_name = "StructureType"
        return node

    def struct_declaration(self):
        """
        <struct-declaration> ::= {<specifier-qualifier>}* <struct-declarator> ("," <struct-declarator>)*
        """
        node = StructDeclaration()
        specifier_qualifiers = []
        while self.current_token.type in self.cfirst_set.specifier_qualifier:
            specifier_qualifiers.append(self.specifier_qualifier())
        node.update(specifier_qualifiers=specifier_qualifiers)

        struct_declarators = [self.struct_declarator()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))
            struct_declarators.append(self.struct_declarator())
        node.update(declarators=struct_declarators)
        return node

    def specifier_qualifier(self):
        """
        <specifier-qualifier> ::= <type-specifier>
                                | <type-qualifier>
        """
        if self.current_token.type in self.cfirst_set.type_specifier:
            return self.type_specifier()
        elif self.current_token.type in self.cfirst_set.type_qualifier:
            return self.type_qualifier()
        else:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier or type qualifier")

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

    def declarator_list(self) -> List[Declarator]:
        """
        <declarator_list> ::= <declarator> ("," <declarator>)*
        """
        declarator_list = [self.declarator()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            declarator_list.append(self.declarator())
        return declarator_list

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
        <type-qualifier> ::= "const"
                           | "volatile"
        """
        node = Keyword(self.current_token.value)
        node.register_token(self.eat(self.current_token.type))
        node.class_name = "QualifyType"
        return node

    def direct_declaractor(self):
        """
        <direct-declarator> ::=     <identifier>     (<direct-declarator-postfix>)?
                              | "(" <declarator> ")" (<direct-declarator-postfix>)?

        <direct-declarator-postfix> ::= "[" {<constant-expression>}? "]" (<direct-declarator-postfix>)?
                                      | "(" (<parameter-list>)?      ")" (<direct-declarator-postfix>)?

        最后的匹配使用("," <declarator>)?, 将逗号后的所有情况放到下一级的 declarator 中去嵌套解决
        """
        node = DirectDeclaractor()
        if self.current_token.type == TokenType.ID:
            node.register_token(self.eat(TokenType.ID))
            node.update_id()

        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(declarator=self.declarator())
            node.register_token(self.eat(TokenType.RPAREN))
            # declarator 与 direct_declaractor 是一个嵌套调用
            node.update_id()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id or (")

        # 先在这里统一保存, 后续根据 token [] () 来分析具体的 [3](int,int)[4]
        constant_expressions = []
        parameter_list = []
        while self.current_token.type in self.cfirst_set.direct_delcartor_postfix:
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                if self.current_token.type in self.cfirst_set.constant_expression:
                    constant_expressions.append(self.constant_expression())
                node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            if self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.parameter_list:
                    parameter_list.append(self.parameter_list())
                node.register_token(self.eat(TokenType.RPAREN))

        node.update(constant_expressions=constant_expressions)
        node.update(parameter_list=parameter_list)

        return node

    def constant_expression(self):
        """
        <constant-expression> ::= <conditional-expression>
        """
        return self.conditional_expression()

    def conditional_expression(self):
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

    def logical_or_expression(self):
        """
        <logical-or-expression> ::= <logical-and-expression> ("||" <logical-and-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.logical_and_expression())
        while self.current_token.type == TokenType.OR:
            node.update(expr_right=self.logical_and_expression())
        return node

    def logical_and_expression(self):
        """
        <logical-and-expression> ::= <inclusive-or-expression> ("&&" <inclusive-or-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.inclusive_or_expression())
        while self.current_token.type == TokenType.AND:
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.inclusive_or_expression())
        return node

    def inclusive_or_expression(self):
        """
        <inclusive-or-expression> ::= <exclusive-or-expression> ("|" <exclusive-or-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.exclusive_or_expression())
        while self.current_token.type == TokenType.PIPE:
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.exclusive_or_expression())
        return node

    def exclusive_or_expression(self):
        """
        <exclusive-or-expression> ::= <and-expression> ("^" <and-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.and_expression())
        while self.current_token.type == TokenType.CARET:
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.and_expression())
        return node

    def and_expression(self):
        """
        <and-expression> ::= <equality-expression> ("&" <equality-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.equality_expression())
        while self.current_token.type == TokenType.AMPERSAND:
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.equality_expression())
        return node

    def equality_expression(self):
        """
        <equality-expression> ::= <relational-expression> (("=="|"!=") <relational-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.relational_expression())
        while self.current_token.type in (TokenType.EQ, TokenType.NE):
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.relational_expression())
        return node

    def relational_expression(self):
        """
        <relational-expression> ::= <shift-expression> (("<"|">"|"<="|">=") <shift-expression>)*
        """
        node = BinaryOp()
        node.update(expr_left=self.shift_expression())
        while self.current_token.type in (TokenType.LANGLE_BRACE, TokenType.RANGLE_BRACE, TokenType.LE, TokenType.GE):
            if self.current_token.type == TokenType.LANGLE_BRACE:
                self.current_token.type = TokenType.LT
            elif self.current_token.type == TokenType.RANGLE_BRACE:
                self.current_token.type = TokenType.GT
            node.register_token(self.eat(self.current_token.type))
            node.update(expr_right=self.shift_expression())
        return node

    def shift_expression(self):
        """
        <shift-expression> ::= <additive-expression> (("<<" | ">>") <additive-expression>)*
        """

    def additive_expression(self):
        """
        <additive-expression> ::= <multiplicative-expression> (("+"|"-") <multiplicative-expression>)*
        """

    def multiplicative_expression(self):
        """
        <multiplicative-expression> ::= <cast-expression> (("*"|"/"|"%") <cast-expression>)*
        """

    def case_expression(self):
        """
        <cast-expression> ::= <unary-expression>
                            | "(" <type-name> ")" <cast-expression>
        """

    def unary_expression(self):
        """
        <unary-expression> ::= <postfix-expression>
                             | "++" <unary-expression>
                             | "--" <unary-expression>
                             | <unary-operator> <cast-expression>
                             | "sizeof" <unary-expression>
                             | "sizeof" <type-name>
        """

    def postfix_expression(self):
        """
        <postfix-expression> ::= <primary-expression>
                               | <postfix-expression> [ <expression> ]
                               | <postfix-expression> ( {<assignment-expression>}* )
                               | <postfix-expression> . <identifier>
                               | <postfix-expression> -> <identifier>
                               | <postfix-expression> ++
                               | <postfix-expression> --
        """

    def primary_expression(self):
        """
        <primary-expression> ::= <identifier>
                               | <constant>
                               | <string>
                               | "(" <expression> ")"
        """

    def constant(self):
        """
        <constant> ::= <integer-constant>
                     | <character-constant>
                     | <floating-constant>
                     | <enumeration-constant>
        """

    def expression(self):
        """
        <expression> ::= <assignment-expression>
                       | <expression> "," <assignment-expression>
        """

    def assignment_expression(self):
        """
        <assignment-expression> ::= <conditional-expression>
                                  | <unary-expression> <assignment-operator> <assignment-expression>
        """

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

    def unary_operator(self):
        """
        <unary-operator> ::= "&"
                           | "*"
                           | "+"
                           | "-"
                           | "~"
                           | "!"
        """

    def type_name(self):
        """
        <type-name> ::= {<specifier-qualifier>}+ {<abstract-declarator>}?
        """

    def parameter_list(self):
        """
        <parameter-list> ::= <parameter-declaration> ("," <parameter-declaration>)* ("," "...")?
        """

    def parameter_declaration(self):
        """
        <parameter-declaration> ::= {<declaration-specifier>}+ <declarator>
                                  | {<declaration-specifier>}+ <abstract-declarator>
                                  | {<declaration-specifier>}+
        """
        self.declaration_sepcifier()

    def abstract_declarator(self):
        """
        <abstract-declarator> ::= <pointer>
                                | <pointer> <direct-abstract-declarator>
                                | <direct-abstract-declarator>
        """

    def direct_abstract_declarator(self):
        """
        <direct-abstract-declarator> ::=  "(" <abstract-declarator> ")"
                                       | {<direct-abstract-declarator>}? "[" {<constant-expression>}? "]"
                                       | {<direct-abstract-declarator>}? "(" {<parameter-list>}? ")"
        """

    def enum_specifier(self):
        """
        <enum-specifier> ::= "enum" <identifier> "{" <enumerator-list> "}"
                           | "enum" "{" <enumerator-list> "}"
                           | "enum" <identifier>
        """

    def enumerator_list(self):
        """
        <enumerator-list> ::= (<enumerator-list> ",")? <enumerator>
        """

    def enumerator(self):
        """
        <enumerator> ::= <identifier> ("=" <constant-expression>)?
        """

    def typedef_name(self):
        """
        <typedef-name> ::= <identifier>
        """

    def declaration(self):
        """
        <declaration> ::=  {<declaration-specifier>}+ {<init-declarator>}* ";"
        """
        self.declaration_sepcifier()

    def init_declarator(self):
        """
        <init-declarator> ::= <declarator> ("=" <initializer>)?
        """

    def initializer(self):
        """
        <initializer> ::= <assignment-expression>
                        | "{" <initializer-list> "}"
                        | "{" <initializer-list> "," "}"
        """

    def initializer_list(self):
        """
        <initializer-list> ::= (<initializer-list> ",")? <initializer>
        """

    def compound_statement(self):
        """
        <compound-statement> ::= "{" {<declaration>}* {<statement>}* "}"
        """

    def statement(self):
        """
        <statement> ::= <labeled-statement>
                      | <expression-statement>
                      | <compound-statement>
                      | <selection-statement>
                      | <iteration-statement>
                      | <jump-statement>
        """

    def labeled_statement(self):
        """
        <labeled-statement> ::= <identifier> ":" <statement>
                              | "case" <constant-expression> ":" <statement>
                              | "default" ":" <statement>
        """

    def expression_statement(self):
        """
        <expression-statement> ::= {<expression>}? ";"
        """

    def selection_statement(self):
        """
        <selection-statement> ::= "if" "(" <expression> ")" <statement>
                                | "if" "(" <expression> ")" <statement> "else" <statement>
                                | "switch" "(" <expression> ")" <statement>
        """

    def iteration_statement(self):
        """
        <iteration-statement> ::= "while" "(" <expression> ")" <statement>
                                | "do" <statement> "while" "(" <expression> ")" ";"
                                | "for" "(" {<expression>}? ";" {<expression>}? ";" {<expression>}? ")" <statement>
        """

    def jump_statement(self):
        """
        <jump-statement> ::= "goto" <identifier> ";"
                           | "continue" ";"
                           | "break" ";"
                           | "return" {<expression>}? ";"
        """
