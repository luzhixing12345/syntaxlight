from syntaxlight.ast import NodeVisitor
from .parser import Parser
from ..lexers import TokenType, CTokenType, CTokenSet
from ..error import ErrorCode
from ..ast import AST, Object, Array, Pair, String, Number, Keyword, UnaryOp


class TranslationUnit(AST):
    def __init__(self, declarations) -> None:
        super().__init__()
        self.declarations = declarations

    def visit(self, node_visitor: NodeVisitor = None):
        for declaration in self.declarations:
            node_visitor.link(self, declaration)
        return super().visit(node_visitor)

class Function(AST):

    def __init__(self, declaration_specifiers, declarator, declarations) -> None:
        super().__init__()
        self.declaration_specifiers = declaration_specifiers
        self.declarator = declarator
        self.declarations = declarations

    def visit(self, node_visitor: NodeVisitor = None):
        for declaration_specifier in self.declaration_specifiers:
            node_visitor.link(self, declaration_specifier)
        node_visitor.link(self, self.declarator)
        for declaration in self.declarations:
            node_visitor.link(self, declaration)
        return super().visit(node_visitor)

class Structure(AST):
    
    def __init__(self, type:str) -> None:
        super().__init__()
        self.type = type
        self.id = None
        self.declarations = None

    def update_id(self):
        for token in self._tokens:
            if token.type == TokenType.ID:
                self.id = token
                break
        
        assert False, "struct or union should have id by update_id not found!"  # pragma: no cover

    def visit(self, node_visitor: NodeVisitor = None):
        if self.declarations:
            for declaration in self.declarations:
                node_visitor.link(self, declaration)
        return super().visit(node_visitor)

class StructDeclaration(AST):

    def __init__(self) -> None:
        super().__init__()
        self.declarators = None
    
    def visit(self, node_visitor: NodeVisitor = None):
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
        else: # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "token type should inside function definition and declaration")

    def function_definition(self):
        """
        <function-definition> ::= {<declaration-specifier>}* <declarator> {<declaration>}* <compound-statement>
        """
        declaration_specifiers = []
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_specifiers.append(self.declaration_sepcifier())
        declarator = self.declarator()
        declarations = []
        while self.current_token.type in self.cfirst_set.declaration:
            declarations.append(self.declaration())
        return Function(declaration_specifiers, declarator, declarations)

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
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be StorageClass or Type or QualifyType")
        
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
        node.class_name = 'StorageClass'
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
            node.class_name = 'Type'
        else: # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier")

    def struct_or_union_specifier(self):
        """
        <struct-or-union-specifier> ::= ("struct"|"union") <identifier> ("{" {<struct-declaration>}+ "}")?
                                      | ("struct"|"union") "{" {<struct-declaration>}+ "}"
        """
        if self.current_token.type not in self.cfirst_set.struct_or_union_specifier:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be struct or union")
        
        node = Structure(self.current_token.value)
        node.register_token(self.eat(self.current_token.type)) # struct or union
        if self.current_token.type == TokenType.ID:
            node.register_token(self.eat(TokenType.ID))
            node.update_id() # 手动更新一下 Structure 中的 id 信息
        
        # struct or union 有定义 {}
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            struct_declarations = []
            while self.current_token.type in self.cfirst_set.struct_declaration:
                struct_declarations.append(self.struct_declaration())
            node.update(declarations = struct_declarations)
            node.register_token(self.eat(TokenType.RPAREN))
        
        return node


    def struct_declaration(self):
        """
        <struct-declaration> ::= {<specifier-qualifier>}* <struct-declarator> ("," <struct-declarator>)*
        """
        node = StructDeclaration()
        while self.current_token.type in self.cfirst_set.specifier_qualifier:
            node.register_token(self.eat(self.current_token.type))
        
        struct_declarators = [self.struct_declarator()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))
            struct_declarators.append(self.struct_declarator())
        node.update(declarators = struct_declarators)
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
        else: # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier or type qualifier")

    def struct_declarator(self):
        """
        <struct-declarator> ::= <declarator> (":" <constant-expression>)?
                              | ":" <constant-expression>
        """
        node = StructDeclarator()
        if self.current_token.type in self.cfirst_set.declarator:
            node.update(declarator = self.declarator())
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
                node.update(expression = self.constant_expression())
        elif self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(expression = self.constant_expression())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "struct declarator should match declarator or :")
        return node


    def declarator(self):
        """
        <declarator> ::= {<pointer>}? <direct-declarator>
        """
        

    def pointer(self):
        """
        <pointer> ::= "*" {<type-qualifier>}* {<pointer>}?
        """

    def type_qualifier(self):
        """
        <type-qualifier> ::= const
                           | volatile
        """
        node = Keyword(self.current_token.value)
        node.register_token(self.eat(self.current_token.type))
        node.class_name = 'QualifyType'
        return node

    def direct_declaractor(self):
        """
        <direct-declarator> ::= <identifier>
                              | "(" <declarator> ")"
                              | <direct-declarator> "[" {<constant-expression>}? "]"
                              | <direct-declarator> "(" <parameter-type-list>    ")"
                              | <direct-declarator> "(" {<identifier>}*          ")"
        """

    def constant_expression(self):
        """
        <constant-expression> ::= <conditional-expression>
        """

    def conditional_expression(self):
        """
        <conditional-expression> ::= <logical-or-expression> ("?" <expression> ":" <conditional-expression>)?
        """

    def logical_or_expression(self):
        """
        <logical-or-expression> ::= (<logical-or-expression> "||")? <logical-and-expression>
        """

    def logical_and_expression(self):
        """
        <logical-and-expression> ::= (<logical-and-expression> "&&")? <inclusive-or-expression>
        """

    def inclusive_or_expression(self):
        """
        <inclusive-or-expression> ::= (<inclusive-or-expression> "|")? <exclusive-or-expression>
        """

    def exclusive_or_expression(self):
        """
        <exclusive-or-expression> ::= (<exclusive-or-expression> "^")? <and-expression>
        """

    def and_expression(self):
        """
        <and-expression> ::= (<and-expression> "&")? <equality-expression>
        """

    def equality_expression(self):
        """
        <equality-expression> ::= (<equality-expression> ("=="|"!="))? <relational-expression>
        """

    def relational_expression(self):
        """
        <relational-expression> ::= (<relational-expression> ("<"|">"|"<="|">="))? <shift-expression>
        """

    def shift_expression(self):
        """
        <shift-expression> ::= (<shift-expression> ("<<" | ">>"))? <additive-expression>
        """

    def additive_expression(self):
        """
        <additive-expression> ::= (<additive-expression> ("+"|"-"))? <multiplicative-expression>
        """

    def multiplicative_expression(self):
        """
        <multiplicative-expression> ::= (<multiplicative-expression> ("*"|"/"|"%"))? <cast-expression>
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

    def parameter_type_list(self):
        """
        <parameter-type-list> ::= <parameter-list>
                                | <parameter-list> "," "..."
        """

    def parameter_list(self):
        """
        <parameter-list> ::= (<parameter-list> ",")? <parameter-declaration>
        """

    def parameter_declaration(self):
        """
        <parameter-declaration> ::= {<declaration-specifier>}+ <declarator>
                                  | {<declaration-specifier>}+ <abstract-declarator>
                                  | {<declaration-specifier>}+
        """

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
                                       | {<direct-abstract-declarator>}? "(" {<parameter-type-list>}? ")"
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
