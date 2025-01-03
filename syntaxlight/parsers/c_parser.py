"""
*Copyright (c) 2023 All rights reserved
*@description: enbf/c17_enhance.bnf 在 C17 文法上扩展
*@author: Zhixing Lu
*@date: 2023-07-16
*@email: luzhixing12345@163.com
*@Github: luzhixing12345
"""

import re

from .parser import Parser
from ..lexers import TokenType, CTokenType, CTokenSet, Token
from ..error import ErrorCode
from ..asts.ast import (
    AST,
    String,
    Keyword,
    UnaryOp,
    BinaryOp,
    Identifier,
    Constant,
    Expression,
    AssignOp,
    Char,
    add_ast_type,
    delete_ast_type,
)
from ..asts.c_ast import *
from typing import List
from enum import Enum
from ..gdt import *

GDT = GlobalDescriptorTable()


class C_CSS(Enum):
    BASE_TYPE = "BaseType"
    STORAGE_TYPE = "StorageType"
    TYPE_SPECIFIER = "TypeSpecifier"
    FUNCTION_TYPE = "FunctionType"
    STRUCTURE_TYPE = "StructureType"
    QUALIFY_TYPE = "QualifyType"
    HEADER_NAME = "HeaderName"
    ALIGN_SPECIFIER = "AlignSpecifier"
    ATOMAIC_TYPE_SPECIFIER = "AtomicTypeSpecifier"
    STRUCTURE_CLASS = "StructureClass"
    GOTO_LABEL = "GotoLabel"


class CParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.cfirst_set = CTokenSet()
        self.in_preprocessing = False  # 进入预处理阶段, 影响 after_eat
        self.preprocessing_keywords = [
            "ifdef",
            "ifndef",
            "elif",
            "endif",
            "include",
            "define",
            "undef",
            "line",
            "error",
            "pragma",
        ]
        self.after_eat()

    def parse(self):
        self.root = self.translation_unit()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        GDT.reset()
        return self.root

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
                                 | <group>
                                 | <statement>

        在这里没有办法区分, 需要查看 <declarator> 后面是否有<declaration>* 和 <compound-statement> 才可以确定是 <function-definition>

        @EXTEND-GRAMMAR
        添加 <group> <statement> 以适配宏定义与开头的陈述语句. C 默认不支持 if for 作为陈述语句, 这里添加对于代码段的扩展支持
        """
        # function-definition 在 declaration 中被检验和修正
        self._unknown_typedef_id_guess()
        if self.current_token.type in self.cfirst_set.declaration:
            return self.declaration()
        elif self.current_token.type in self.cfirst_set.statement:
            return self.statement()
        else:  # pragma: no cover
            self.error(
                ErrorCode.UNEXPECTED_TOKEN,
                "token type should inside function definition and declaration",
            )

    def declaration_sepcifier(self) -> AST:
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
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be StorageType or BaseType or QualifyType")

        self._unknown_typedef_id_guess()
        return node

    def storage_class_specifier(self):
        """
        <storage-class-specifier> ::= 'auto'
                                    | 'register'
                                    | 'static'
                                    | 'extern'
                                    | 'typedef'
        """
        return self.get_keyword(css_type=C_CSS.STORAGE_TYPE)

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

                           | bool
        @EXTEND-GRAMMAR
        bool 为 C23 中引入, 但实在是太常见了, 一般都会 typedef int bool
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
            node = self.get_keyword(css_type=C_CSS.BASE_TYPE)
        else:  # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type specifier")
        add_ast_type(node, C_CSS.TYPE_SPECIFIER)
        return node

    def function_specifier(self):
        """
        <function-specifier> ::= inline
                               | _Noreturn
        """
        return self.get_keyword(css_type=C_CSS.FUNCTION_TYPE)

    def alignment_specifier(self):
        """
        <alignment-specifier> ::= _Alignas "(" <type-name> ")"
                                | _Alignas "(" <constant-expression> ")"
        """
        node = TypeSpecifier()
        node.update(keyword=self.get_keyword(CTokenType._ALIGNAS))
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.cfirst_set.type_name:
            node.update(sub_node=self.type_name())
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.cfirst_set.constant_expression:
            node.update(sub_node=self.constant_expression())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type-name or constant-expression")
        add_ast_type(node, C_CSS.ALIGN_SPECIFIER)
        return node

    def atomic_type_specifier(self):
        """
        <atomic-type-specifier> ::= _Atomic "(" <type-name> ")"
        """
        node = TypeSpecifier()
        node.update(keyword=self.get_keyword(CTokenType._ATOMIC))
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(sub_node=self.type_name())
        node.register_token(self.eat(TokenType.RPAREN))
        add_ast_type(node, C_CSS.ATOMAIC_TYPE_SPECIFIER)
        return node

    def struct_or_union_specifier(self):
        """
        <struct-or-union-specifier> ::= <struct-or-union> <identifier> ("{" {<struct-declaration>}* "}")?
                                      | <struct-or-union>              "{" {<struct-declaration>}* "}" <GNU-attribute>?
        """
        if self.current_token.type not in self.cfirst_set.struct_or_union_specifier:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be struct or union")

        node = Structure()

        node.update(structure_type=self.struct_or_union())

        # 对于如下情况
        # typedef struct State State;
        # struct State {
        #     int c;
        #     State *out;
        #     State *out1;
        #     int lastlist;
        # };
        # 将当前 struct 中当前 token: "State" 从 CTokenType.TYPEDEF_ID 恢复为TokenType.ID
        if self.current_token.type == CTokenType.TYPEDEF_ID:
            self.current_token.type = TokenType.ID
        if self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
            add_ast_type(node.id, C_CSS.STRUCTURE_CLASS)
        # else:
        #     # 匿名 struct
        #     if self.current_token.type != TokenType.LCURLY_BRACE:
        #         self.error(
        #             ErrorCode.UNEXPECTED_TOKEN,
        #             "Declaration of anonymous struct must be a definition",
        #         )
        # struct or union 有定义 {}
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            struct_declarations = []
            # struct/union 内部可以确定一定是函数指针而非函数调用
            self._unknown_typedef_id_guess(always_match=True)
            while self.current_token.type in self.cfirst_set.struct_declaration:
                struct_declarations.append(self.struct_declaration())
                self._unknown_typedef_id_guess(always_match=True)
            node.update(declarations=struct_declarations)
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

            # 匿名 struct 且未定义成员
            if len(struct_declarations) == 0 and node.id is None:
                self.warning("unnamed struct/union that defines no instances", node)

        if self.current_token.type == CTokenType._ATTRIBUTE:
            node.update(gnu_attribute=self.gnu_c_attribute())
        return node

    def struct_or_union(self):
        """
        <struct-or-union> ::= "struct"
                            | "union"
        """
        return self.get_keyword(css_type=C_CSS.STRUCTURE_TYPE)

    def struct_declaration(self):
        """
        <struct-declaration> ::= <specifier-qualifier-list> <struct-declarator-list>? ";"
                               | <static_assert-declaration>
                               | "..."

        @EXTEND-GRAMMAR
        支持 ... 省略
        """
        node = StructDeclaration()
        if self.current_token.type in self.cfirst_set.static_assert_declaration:
            node.update(static_assert=self.static_assert_declaration())
        elif self.current_token.type == TokenType.VARARGS:
            node.register_token(self.eat(TokenType.VARARGS))
        else:
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
            if self._is_macro_def():
                result.append(self.get_macro_def())
            elif self._is_macro_func():
                result.append(self.get_macro_func())
            elif self.current_token.type in self.cfirst_set.type_specifier:
                result.append(self.type_specifier())
            else:
                result.append(self.type_qualifier())
        return result

    def after_eat(self):
        if self.current_token.type == TokenType.ID:
            # 对于已经在 GDT 中的元素直接标记为 TYPEDEF
            if self.current_token.value in GDT:
                if GDT[self.current_token.value] == CSS.TYPEDEF:
                    self.current_token.type = CTokenType.TYPEDEF_ID
                elif GDT[self.current_token.value] == CSS.MACRO_DEFINE:
                    self.current_token.add_css(CSS.MACRO_DEFINE)
                elif GDT[self.current_token.value] == CSS.MACRO_FUNCTION:
                    self.current_token.add_css(CSS.MACRO_FUNCTION)
            if self.current_token.value.startswith("__"):
                next_token_types = [TokenType.ID, TokenType.MUL]
                next_token_type = self.peek_next_token().type
                if next_token_type in self.cfirst_set.declaration_specifier or next_token_type in next_token_types:
                    # 双下划线开头的变量特殊处理, 可能是宏. 见 44.c
                    # __init __always_inline
                    self.current_token.type = CTokenType.TYPEDEF_ID
                    self.current_token.add_css(CSS.MACRO_DEFINE)
                    GDT.register_id(self.current_token.value, CSS.MACRO_DEFINE)

        if self.in_preprocessing:
            if self.current_token.type == CTokenType.IF:
                self.current_token.type = CTokenType.IF_P
            elif self.current_token.type == CTokenType.ELSE:
                self.current_token.type = CTokenType.ELSE_P
            elif self.current_token.value in self.preprocessing_keywords:
                self.current_token.type = CTokenType(self.current_token.value)

        elif self.current_token.type == TokenType.HASH:
            # 多根节点树
            # TODO: 考虑如何格式化
            self.group()

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
        <declarator> ::= <pointer>? <direct-declarator>
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
        # @EXTEND-GRAMMAR 匹配宏定义
        # 44.c
        while (
            self.current_token.type == TokenType.MUL
            or self.current_token.type == CTokenType.TYPEDEF_ID
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
        return self.get_keyword(css_type=C_CSS.QUALIFY_TYPE)

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

        <direct-declarator> <GNU-attribute>?
        """
        node = DirectDeclaractor()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.get_identifier())
            # 对于初始化的变量去掉其 DefineName 的 tag
            if node.id.id in GDT and GDT[node.id.id] == CSS.MACRO_DEFINE:
                delete_ast_type(node.id, CSS.MACRO_DEFINE)
                GDT.delete_id(node.id.id)
        elif self.current_token.type == TokenType.LPAREN and self.peek_next_token().type in self.cfirst_set.declarator:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(declarator=self.declarator())
            node.register_token(self.eat(TokenType.RPAREN))
        # parameter_declaration 中无法区分, 在 <declarator> 内部区分
        elif self.current_token.type in self.cfirst_set.direct_abstract_declarator:
            return self.direct_abstract_declarator()
        # elif self.current_token.type == TokenType.RPAREN:
        #     return None
        # else:
        #     node = DirectAbstractDeclaractor()
        #     return node
        else:
            return None

        # 先在这里统一保存, 后续根据 token [] () 来分析具体的 [3](int,int)[4]
        sub_nodes = []
        while self.current_token.type in (TokenType.LPAREN, TokenType.LSQUAR_PAREN):
            sub_node = DirectDeclaractorPostfix()
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                sub_node.register_token(self.eat(TokenType.LSQUAR_PAREN))

                if self.current_token.type == CTokenType.STATIC:
                    sub_node.update(static_head=self.get_keyword(CTokenType.STATIC, C_CSS.STORAGE_TYPE))

                if self.current_token.type in self.cfirst_set.type_qualifier:
                    sub_node.update(type_qualifiers=self.type_qualifier_list())

                if self.current_token.type == CTokenType.STATIC:
                    if sub_node.static_head is not None:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, "multi static")
                    sub_node.update(static_foot=self.get_keyword(CTokenType.STATIC, C_CSS.STORAGE_TYPE))

                if self.current_token.type == TokenType.MUL:
                    self.current_token.type = CTokenType.STAR
                    sub_node.register_token(self.eat(CTokenType.STAR))
                elif self.current_token.type in self.cfirst_set.assignment_expression:
                    sub_node.update(assignment_expr=self.assignment_expression())

                sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))

            if self.current_token.type == TokenType.LPAREN:
                # 可以确定是一个函数名
                if node.id is not None:
                    node.is_function = True
                    add_ast_type(node, CSS.FUNCTION_NAME)
                    # TODO: 注册函数到 GDT
                    GDT.register_id(node.id.id, CSS.FUNCTION_NAME)
                if node.declarator is not None:
                    # 函数指针 "(" <declarator> ")"
                    add_ast_type(node, CSS.FUNCTION_POINTER)
                    # 找到最底层的函数指针的名字, 标记为 FUNCTION_POINTER
                    declarator_id = self._find_declaractor_id(node)
                    if declarator_id is not None:
                        GDT.register_id(declarator_id.id, CSS.FUNCTION_POINTER)

                node.register_token(self.eat(TokenType.LPAREN))
                self._unknown_typedef_id_guess()
                if self.current_token.type in self.cfirst_set.parameter_list:
                    sub_node.update(parameter_list=self.parameter_list())
                # elif self.current_token.type == TokenType.ID:
                #     # @EXTEND-GRAMMAR
                #     # 对于未定义过的 Person 类 void updatePersonInfo(Person* person);
                #     sub_node.update(parameter_list=self.parameter_list())
                elif self.current_token.type in self.cfirst_set.identifier:
                    sub_node.update(identifier_list=self.identifier_list())
                node.register_token(self.eat(TokenType.RPAREN))

            sub_nodes.append(sub_node)

        node.update(sub_nodes=sub_nodes)

        if self.current_token.type == CTokenType._ATTRIBUTE:
            node.update(gnu_attribute=self.gnu_c_attribute())
        elif self.current_token.type == TokenType.ID and self.current_token.value.startswith("__"):
            # 可能尾随的 __attribute__ 属性被宏封装起来了, 判断一下之后将其恢复
            # struct files_struct {
            #         spinlock_t file_lock ____cacheline_aligned_in_smp;
            # };
            # https://github.com/luzhixing12345/syntaxlight/issues/14
            self.current_token.add_css(CSS.MACRO_DEFINE)
            self.current_token.type = CTokenType.TYPEDEF_ID
            self.eat()
        return node

    def _find_declaractor_id(self, node: DirectDeclaractor) -> Identifier:
        """
        找到变量的 id node
        """
        # int (*(*fp));
        if node.declarator is not None:
            # 函数指针 "(" <declarator> ")"
            # 找到最底层的函数指针的名字, 标记为 FUNCTION_POINTER
            fp_node = node
            while fp_node is not None and fp_node.declarator is not None:
                fp_node = fp_node.declarator.direct_declarator
            if fp_node is not None:
                return fp_node.id
        # int x;
        elif node.id is not None:
            # node.id 应该有值
            return node.id
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be declarator or id")

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

        @EXTEND-GRAMMAR
        考虑未定义过的参数类型: void updatePersonInfo(Person*, int, char*, Student*);
        对于 TokenType.ID 修改为CTokenType.TYPEDEF_ID
        """
        if self.current_token.type == TokenType.ID:
            self.current_token.type = CTokenType.TYPEDEF_ID
        result = [self.parameter_declaration()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            if self.current_token.type in self.cfirst_set.parameter_declaration:
                result.append(self.parameter_declaration())
            elif self.current_token.type == TokenType.ID:
                self.current_token.type = CTokenType.TYPEDEF_ID
                result.append(self.parameter_declaration())
            elif self.current_token.type == TokenType.VARARGS:
                self.eat(TokenType.VARARGS)
                break
        return result

    def identifier_list(self) -> List[AST]:
        """
        <identifier-list> ::= <identifier> ("," <identifier>)*
        """
        result = [self.get_identifier()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.get_identifier())
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
        if self.current_token.type == TokenType.QUESTION:
            node.register_token(self.eat(TokenType.QUESTION))
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
        return self._binary_expression([TokenType.PLUS, TokenType.MINUS], self.multiplicative_expression)

    def multiplicative_expression(self):
        """
        <multiplicative-expression> ::= <cast-expression> (("*"|"/"|"%") <cast-expression>)*
        """
        return self._binary_expression([TokenType.MUL, TokenType.DIV, TokenType.MOD], self.cast_expression)

    def cast_expression(self):
        """
        <cast-expression> ::= ("(" <type-name> ")")* <unary-expression>
        """
        node = CastExpression()
        type_names = []

        # @特殊处理 检查强制类型转换: is_type_cast
        # test/c/40.c

        while self.current_token.type == TokenType.LPAREN and (
            self.peek_next_token().type in self.cfirst_set.type_name or self.is_type_cast()
        ):
            if self.peek_next_token().type in self.cfirst_set.type_name:
                node.register_token(self.eat(TokenType.LPAREN))
                type_names.append(self.type_name())
                node.register_token(self.eat(TokenType.RPAREN))
            else:
                node.register_token(self.eat(TokenType.LPAREN))
                # 对于未知符号强制类型的情况将其修改为 TYPEDEF_ID
                self.current_token.type = CTokenType.TYPEDEF_ID
                GDT.register_id(self.current_token.value, CSS.TYPEDEF)
                type_names.append(self.type_name())
                node.register_token(self.eat(TokenType.RPAREN))
        node.update(type_names=type_names)
        if self.current_token.type in self.cfirst_set.unary_expression:
            node.update(expr=self.unary_expression())

        elif self.current_token.type == TokenType.LCURLY_BRACE:
            # @修改文法
            # 个人感觉这里存在问题, 对于 Person* ptr = &(Person) { "Bob", 30, { 50, 60 } }; 这里的 <type-name> 会被优先匹配到, 而不是匹配后面 <primary-expression> => "(" <type-name> ")" "{" <initializer-list> (",")? "}"

            # 所以这里做了一个对于 <initializer-list> 的补充

            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            node.update(initializer_list=self.initializer_list())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
            node.register_token(self.eat(TokenType.RCURLY_BRACE))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be unary expression or (")
        return node

    def is_type_cast(self):
        """
        强制类型转换的情况

        (uint8) <unary-expression>
        (uint8 *) <unary-expression>
        (uint8 ****) <unary-expression>
        """
        if self.peek_next_token().type == TokenType.ID:
            if (
                self.peek_next_token(2).type == TokenType.RPAREN
                and self.peek_next_token(3).type in self.cfirst_set.unary_expression
            ):
                return True
            elif self.peek_next_token(2).type == TokenType.MUL:
                n = 3
                while self.peek_next_token(n).type == TokenType.MUL:
                    n += 1
                if (
                    self.peek_next_token(n).type == TokenType.RPAREN
                    and self.peek_next_token(n + 1).type in self.cfirst_set.unary_expression
                ):
                    return True

        return False

    def unary_expression(self) -> Union[PostfixExpression, UnaryExpression]:
        """
        <unary-expression> ::= <postfix-expression>
                             | "++" <unary-expression>
                             | "--" <unary-expression>
                             | <unary-operator> <cast-expression>
                             | sizeof <unary-expression>
                             | sizeof   "(" <type-name> ")"
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
            if self.current_token.type == TokenType.MUL:
                self.current_token.type = CTokenType.POINTER
            unary_expr = UnaryOp(op=self.current_token.value)
            unary_expr.register_token(self.eat(self.current_token.type))

            # @EXTEND-GRAMMAR: 可能没有 cast_expression
            # time_t (*)(time_t *)
            if self.current_token.type != TokenType.RPAREN:
                unary_expr.update(expr=self.cast_expression())
            node.update(expr=unary_expr)
        elif self.current_token.type == CTokenType.SIZEOF:
            node.update(keyword=self.get_keyword(CTokenType.SIZEOF))

            # 这里的判断有点复杂, 因为 可以
            # A: sizeof "(" <type-name> ")"
            #
            # B: sizeof <unary-expression> => sizeof <postfix-expression> => sizeof <primary-expression>
            # => sizeof "(" <expression> ")"
            # 需要区分 type-name 和 expression
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
                elif self.current_token.type in self.cfirst_set.expression:
                    node.update(expr=self.expression())
                    node.register_token(self.eat(TokenType.RPAREN))
                else:
                    self.error(ErrorCode.UNEXPECTED_TOKEN, "should be type name or expression")

            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "sizeof should follow with unary expr or typename")
        elif self.current_token.type == CTokenType._ALIGNOF:
            node.update(keyword=self.get_keyword(CTokenType._ALIGNOF))
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
                               | "(" <type-name> ")" "{" <initializer-list> (",")? "}"
        """
        node = PostfixExpression()
        if self.current_token.type not in self.cfirst_set.postfix_expression:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be ID or constant or string or (")

        # <primary-expression> 中也有 "(" <expression> ")"
        # 需要和 "(" <type-name> ")" 区分一下
        if (
            self.current_token.type != TokenType.LPAREN
            and self.current_token.type in self.cfirst_set.primary_expression
        ) or (
            self.current_token.type == TokenType.LPAREN
            and self.peek_next_token().type in [self.cfirst_set.expression, TokenType.LCURLY_BRACE]
        ):
            # TokenType.LCURLY_BRACE => GNU C Extension
            # https://github.com/luzhixing12345/syntaxlight/issues/13
            node.update(primary_expr=self.primary_expression())
        else:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(type_name=self.type_name())
            node.register_token(self.eat(TokenType.RPAREN))
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            node.update(initializer_list=self.initializer_list())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

        # 检查是不是宏定义
        if node.primary_expr is not None:
            if isinstance(node.primary_expr.sub_node, Identifier):
                if node.primary_expr.sub_node.id in GDT or bool(
                    re.match(r"^[A-Z_][0-9A-Z_]+$", node.primary_expr.sub_node.id)
                ):
                    if self.current_token.type == TokenType.LPAREN:
                        # 宏函数匹配
                        self._match_macro_function()

        sub_nodes: List[Union[AssignmentExpression, Identifier]] = []
        while self.current_token.type in self.cfirst_set.postfix_expression_inside:
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                sub_nodes.append(self.expression())
                node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            elif self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                if len(sub_nodes) > 0:
                    func_node = sub_nodes[-1]
                    # @EXTEND-GRAMMAR
                    # 对于多个 () 的情况, 有两种可能

                    # time_t (*f)(); 函数指针
                    # func (*f)(); func 的返回值是一个函数指针, 是一个函数调用
                    # 在不知道 func 类型的情况下无法判断, 默认视为函数指针形式.

                    # 如果第一个元素是 *fp
                    if (
                        type(sub_nodes[0]) == AssignmentExpression
                        and type(sub_nodes[0].expr.condition_expr) == CastExpression
                    ):
                        cast_expr = sub_nodes[0].expr.condition_expr
                        if type(cast_expr.expr.expr) == UnaryOp:
                            unary_op = cast_expr.expr.expr
                            if unary_op.op == "*":
                                # 修正为函数指针
                                add_ast_type(unary_op, CSS.FUNCTION_POINTER)
                                # 修正函数指针返回值类型为 typedef
                                delete_ast_type(node.primary_expr, CSS.FUNCTION_CALL)
                                node.primary_expr.sub_node._tokens[0].type = CTokenType.TYPEDEF_ID
                                add_ast_type(node.primary_expr, CSS.TYPEDEF)
                                GDT.register_id(node.primary_expr.sub_node.id, CSS.TYPEDEF)

                                self._unknown_typedef_id_guess()
                                sub_nodes.append(self.parameter_list())
                                node.register_token(self.eat(TokenType.RPAREN))
                                continue
                else:
                    # len(sub_nodes) == 0
                    func_node = node.primary_expr.sub_node
                
                if type(func_node) == Identifier and GDT[func_node.id] == CSS.FUNCTION_POINTER:
                    # 对于函数指针, 不视为 FunctionCall
                    pass
                else:
                    # 暂且视为 function call
                    # 也可能是一个函数指针 time_t (*f)() = NULL; 后续再处理
                    add_ast_type(func_node, CSS.FUNCTION_CALL)

                if self.current_token.type in self.cfirst_set.assignment_expression:
                    sub_nodes.append(self.assignment_expression())
                    while self.current_token.type == TokenType.COMMA:
                        node.register_token(self.eat(TokenType.COMMA))
                        sub_nodes.append(self.assignment_expression())

                node.register_token(self.eat(TokenType.RPAREN))
            elif self.current_token.type == TokenType.DOT:
                node.register_token(self.eat(TokenType.DOT))
                sub_nodes.append(self.get_identifier())
            elif self.current_token.type == TokenType.POINT:
                node.register_token(self.eat(TokenType.POINT))
                sub_nodes.append(self.get_identifier())
            else:
                # ++ --
                node.register_token(self.eat(self.current_token.type))

        # some c project like to define for/while
        # see https://github.com/luzhixing12345/syntaxlight/issues/18
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.update(iter_loop = self.compound_statement())

        node.update(sub_nodes=sub_nodes)
        return node

    def primary_expression(self):
        """
        <primary-expression> ::= <identifier>
                               | <constant>
                               | <string>
                               | <char>
                               | "(" <expression> ")"
                               | <generic-selection>

        # @EXTEND-GRAMMAR: braced-group in expression
        # see more in https://github.com/luzhixing12345/syntaxlight/issues/13

        <primary-expression>   | "(" <compound-statement> ")"

        """
        node = PrimaryExpression()
        if self.current_token.type == TokenType.ID:
            sub_node = self.get_identifier()
            # 多个 STRING 可以拼接在一起
            # printk(KERN_INFO "%s\n")
            sticky_strings = []
            while self.current_token.type == TokenType.STRING:
                sticky_strings.append(self.get_string())
            node.update(sticky_strings=sticky_strings)
        elif self.current_token.type in self.cfirst_set.constant:
            # @EXTEND-GRAMMAR
            # Constant 包含了 true, false
            # 该关键字由 C23 引入, 但非常常用, 一般会 define 为 1 和 0, 所以这里引入为 Constant
            sub_node = Constant(self.current_token.value)
            sub_node.register_token(self.eat(self.current_token.type))
        elif self.current_token.type == TokenType.STRING:
            sub_node = self.get_string()
            # 多个 STRING 可以拼接在一起
            # printk(KERN_INFO "%s\n")
            sticky_strings = []
            while self.current_token.type == TokenType.STRING:
                sticky_strings.append(self.get_string())
            node.update(sticky_strings=sticky_strings)
        elif self.current_token.type == TokenType.CHARACTER:
            sub_node = Char(self.current_token.value)
            sub_node.register_token(self.eat(self.current_token.type))
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.cfirst_set.compound_statement:
                sub_node = self.compound_statement()
            else:
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
        node = GenericSelection()
        node.update(keyword=self.get_keyword(CTokenType._GENERIC))
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
            node.update(keyword=self.get_keyword(CTokenType.DEFAULT))
        elif self.current_token.type in self.cfirst_set.type_name:
            node.update(type_name=self.type_name())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be default or type-name")
        node.register_token(self.eat(TokenType.COLON))
        node.update(assignment_expr=self.assignment_expression())
        return node

    def _match_macro_function(self):
        """
        匹配不符合 C 文法的宏定义函数

        1. 对于全大写 ID 的会被认为是宏函数

           XBOX_ARG_BOOLEAN(NULL, [-h][--help][help = "show help information"])

        2. 对于前面定义过的宏函数会被匹配

           #define container_of()

           struct ipc_namespace *ns = container_of(table->data, struct ipc_namespace, shm_rmid_forced);
        """

        assert self.current_token.type == TokenType.LPAREN
        self.eat(TokenType.LPAREN)
        brace_number = 1

        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.RPAREN:
                brace_number -= 1
                if brace_number == 0:
                    self.eat()
                    return
            elif self.current_token.type == TokenType.LPAREN:
                brace_number += 1
            self.pp_token()

        self.error(ErrorCode.BRACE_MISS_MATCH)

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
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be unary expression or conditional expression")

        node = AssignmentExpression()
        expr = self.conditional_expression()
        if isinstance(expr.condition_expr, BinaryOp):
            # 含双目运算符, 必为 conditional expression
            node.update(expr=expr)
        elif isinstance(expr.condition_expr, CastExpression):
            # CastExpression 含 type_names 必为 conditional expression
            if len(expr.condition_expr.type_names) != 0:
                node.update(expr=expr)
            else:
                # 纯 unary expression
                node.update(expr=expr)
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
        node.register_token(self.eat(self.current_token.type))
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
        <parameter-declaration> ::= <declaration-specifier>+ <declarator>
                                  | <declaration-specifier>+ <abstract-declarator>?
        """
        node = ParameterDeclaration()
        self._unknown_typedef_id_guess()
        declaration_sepcifiers = [self.declaration_sepcifier()]
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_sepcifiers.append(self.declaration_sepcifier())
        node.update(declaration_sepcifiers=declaration_sepcifiers)

        # 这里也没有办法 LL1 的判断, 先统统考虑为 <declarator>
        # 在 <declarator> 内部做 <abstract-declarator> 的处理
        if self.current_token.type in self.cfirst_set.declarator:
            node.update(declarator=self.declarator())
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
                elif self.current_token.type == TokenType.MUL:
                    # void (*binary_func)() = (void (*)())mem;
                    #                                |
                    self.current_token.type = CTokenType.POINTER
                    sub_node.register_token(self.eat(CTokenType.POINTER))
                elif self.current_token.type == TokenType.RPAREN:
                    # void (*binary_func)() = (void (*)())mem;
                    #                                   |
                    pass
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
                    sub_node.update(static_head=self.get_keyword(CTokenType.STATIC, C_CSS.STORAGE_TYPE))
                if self.current_token.type in self.cfirst_set.type_qualifier:
                    sub_node.update(type_qualifiers=self.type_qualifier_list())

                if self.current_token.type == CTokenType.STATIC:
                    if sub_node.static_head is not None:
                        self.error(ErrorCode.UNEXPECTED_TOKEN, "multi static")
                    sub_node.update(static_foot=self.get_keyword(CTokenType.STATIC, C_CSS.STORAGE_TYPE))

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
        
        @EXTEND-GRAMMAR: https://github.com/luzhixing12345/syntaxlight/issues/24
        支持 ... 省略
        """
        node = EnumSpecifier()
        node.update(keyword=self.get_keyword(CTokenType.ENUM))
        if self.current_token.type in self.cfirst_set.identifier:
            node.update(id=self.get_identifier())
            delete_ast_type(node.id, CSS.MACRO_DEFINE)
            add_ast_type(node.id, CSS.ENUM_ID)
            GDT.register_id(node.id.id, CSS.ENUM_ID)
        if self.current_token.type == TokenType.LCURLY_BRACE:
            node.register_token(self.eat(TokenType.LCURLY_BRACE))
            enumerators = [self.enumerator()]
            while self.current_token.type in [TokenType.COMMA, TokenType.VARARGS]:
                node.register_token(self.eat())
                
                if self.current_token.type == TokenType.RCURLY_BRACE:
                    # 如果下一个就是 } 则直接返回即可
                    break
                
                if self.current_token.type == TokenType.VARARGS:
                    node.register_token(self.eat(TokenType.VARARGS))
                    # 如果写法不标准, ... 后没有逗号, 也算在里面
                    # enum x {
                    #    abc,
                    #    ...
                    #    def
                    # }
                    if self.current_token.type != TokenType.ID:
                        continue
                enumerators.append(self.enumerator())
            node.update(enumerators=enumerators)
            node.register_token(self.eat(TokenType.RCURLY_BRACE))

        return node

    def enumerator(self):
        """
        <enumerator> ::= <identifier> ("=" <constant-expression>)?
        """
        node = Enumerator()
        node.update(id=self.get_identifier())
        add_ast_type(node.id, CSS.ENUMERATOR)
        GDT.register_id(node.id.id, CSS.ENUMERATOR)
        if self.current_token.type == TokenType.ASSIGN:
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(const_expr=self.constant_expression())
        return node

    def typedef_name(self):
        """
        <typedef-name> ::= <identifier>
        """
        node = self.get_keyword(CTokenType.TYPEDEF_ID, css_type=CSS.TYPEDEF)
        return node

    def declaration(self):
        """
        <declaration> ::= <declaration-specifier>+ (<init-declarator-list>)? ";"
                        | <static-assert-declaration>
                        | extern "C" <compound-statement>

        也有可能是 <function-definition>, 如果 <init-declarator-list> 的只有一个元素且没有 <initializer> 且后面跟着的是 <declaration>* <compound-statement>

        <function-definition> ::= <declaration-specifier>* <declarator>  <GNU-attribute>? <declaration>* <compound-statement>
        """
        node = Declaration()
        if self.current_token.type in self.cfirst_set.static_assert_declaration:
            node.update(static_assert=self.static_assert_declaration())
            return node

        if self.current_token.type == CTokenType.EXTERN:
            next_token = self.peek_next_token()
            if next_token is not None and next_token.type == TokenType.STRING and next_token.value == '"C"':
                self.eat(CTokenType.EXTERN)
                self.eat(TokenType.STRING)
                node.update(extern_c=self.compound_statement())
                return node

        if self.current_token.type == CTokenType._ATTRIBUTE:
            node.update(gnu_attribute=self.gnu_c_attribute())

        self._unknown_typedef_id_guess()
        declaration_specifiers: List[AST] = [self.declaration_sepcifier()]
        while self.current_token.type in self.cfirst_set.declaration_specifier:
            declaration_specifiers.append(self.declaration_sepcifier())

        if self.current_token.type in self.cfirst_set.init_declarator_list:
            init_declarator_list = self.init_declarator_list()
            if self.current_token.type == TokenType.SEMI:
                node.update(declaration_specifiers=declaration_specifiers)
                node.update(init_declarator_list=init_declarator_list)
                node.register_token(self.eat(TokenType.SEMI))
                if self._is_C_function(init_declarator_list):
                    add_ast_type(declaration_specifiers, CSS.FUNCTION_RETURN_TYPE)
                # @EXTEND-GRAMMAR
                # 对于 typedef 重命名的符号, 加入 GDT 中
                if type(node.declaration_specifiers[0]) == Keyword and node.declaration_specifiers[0].name == "typedef":
                    for init_declarator in node.init_declarator_list:
                        declarator_id = self._find_declaractor_id(init_declarator.declarator.direct_declarator)
                        declarator_id._tokens[0].type = CTokenType.TYPEDEF_ID
                        add_ast_type(declarator_id, CSS.TYPEDEF)
                        GDT.register_id(declarator_id.id, CSS.TYPEDEF)

                return node
            elif self._is_C_function(init_declarator_list) and (
                self.current_token.type in self.cfirst_set.compound_statement
                or self.current_token.type in self.cfirst_set.declaration
            ):
                return self._build_C_function_definition(declaration_specifiers, init_declarator_list[0])
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "miss not declaration or function definition")
        if self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == CTokenType._ATTRIBUTE:
            node.update(gnu_attribute=self.gnu_c_attribute())
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
        node = init_declarator_list[0].declarator.direct_declarator
        if node.is_function:
            return True
        while node.declarator is not None:
            node = node.declarator.direct_declarator
            if node.is_function:
                return True
        return False

    def _build_C_function_definition(self, declaration_specifiers, declarator: InitDeclarator):
        """
        <function-definition> ::= <declaration-specifier>* <declarator> <declaration>* <compound-statement>

        <declaration> 中判断为 <function-definition>
        """
        node = Function()
        node.update(declaration_specifiers=declaration_specifiers)
        node.update(declarator=declarator)

        # 古早的 K&R C 写法
        # int f(a,b) int a,b; {
        #     return 1;
        # }
        declarations = []
        while self.current_token.type in self.cfirst_set.declaration:
            declarations.append(self.declaration())
        node.update(declarations=declarations)
        node.update(compound_statement=self.compound_statement())

        add_ast_type(node.declaration_specifiers, CSS.FUNCTION_RETURN_TYPE)
        add_ast_type(node.declarator.declarator.direct_declarator.id, CSS.FUNCTION_NAME)
        # 对于含 <declaration> 的情况取消其参数的 Typedefine
        if len(node.declarations) != 0:
            delete_ast_type(node.declarator, CSS.TYPEDEF)
        return node

    def init_declarator_list(self) -> List[InitDeclarator]:
        """
        <init-declarator-list> ::= <init-declarator> ("," <init-declarator>)*
        """
        result = [self.init_declarator()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.init_declarator())
        return result

    def init_declarator(self) -> InitDeclarator:
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
            if self.current_token.type in self.cfirst_set.initializer_list:
                node.update(initializer_list=self.initializer_list())

            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))

            node.register_token(self.eat(TokenType.RCURLY_BRACE))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be initializer list or assignment expression")
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
            next_token_type = self.peek_next_token().type
            if (
                next_token_type not in self.cfirst_set.designation
                and next_token_type not in self.cfirst_set.initializer
            ):
                break
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
        designators = [self.designator()]
        while self.current_token.type in self.cfirst_set.designator:
            designators.append(self.designator())
        node.update(designators=designators)

        # @EXTEND-GRAMMAR
        # 此处为 GNU C 扩展, 正常来说赋值应该为
        # struct x[] = {
        #    [0] = 1
        # }
        # GNU C 扩展了此处可以不使用等号直接赋值
        # static uint64 (*syscalls[])(void) = {
        #     [SYS_fork] sys_fork,   [SYS_exit] sys_exit,     [SYS_wait] sys_wait,     [SYS_pipe] sys_pipe,
        #     [SYS_read] sys_read,   [SYS_kill] sys_kill,     [SYS_exec] sys_exec,     [SYS_fstat] sys_fstat,
        #     [SYS_chdir] sys_chdir, [SYS_dup] sys_dup,       [SYS_getpid] sys_getpid, [SYS_sbrk] sys_sbrk,
        #     [SYS_sleep] sys_sleep, [SYS_uptime] sys_uptime, [SYS_open] sys_open,     [SYS_write] sys_write,
        #     [SYS_mknod] sys_mknod, [SYS_unlink] sys_unlink, [SYS_link] sys_link,     [SYS_mkdir] sys_mkdir,
        #     [SYS_close] sys_close,
        # };
        if self.current_token.type == TokenType.ASSIGN:
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
            node.update(const_expr=self.constant_expression())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
        elif self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            node.update(id=self.get_identifier())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be constant expression or id")
        return node

    def compound_statement(self):
        """
        <compound-statement> ::= "{" (<block-item>)* "}"

        <block-item> ::= <declaration>
                       | <statement>
                       | "..."

        @EXTEND-GRAMMAR
        支持 ... 省略
        """
        node = CompoundStatement()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        sub_nodes = []
        self._unknown_typedef_id_guess()
        while self.current_token.type in self.cfirst_set.block_item:
            if self.current_token.type in self.cfirst_set.declaration:
                sub_nodes.append(self.declaration())
            elif self.current_token.type in self.cfirst_set.statement:
                sub_nodes.append(self.statement())
            else:
                # ...
                self.eat(token_type=TokenType.VARARGS)
            self._unknown_typedef_id_guess()
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
                      | <gnu-c-statement-extension>
        """
        if self.current_token.type == TokenType.ID and self.peek_next_token().type == TokenType.COLON:
            # goto id;
            # id: ...
            return self.labeled_statement()
        elif self.current_token.type != TokenType.ID and self.current_token.type in self.cfirst_set.labeled_statement:
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
        elif self.current_token.type in self.cfirst_set.gnu_c_statement_extension:
            return self.gnu_c_statement_extension()
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
            node.update(id=self.get_identifier())
            # goto 的标签
            add_ast_type(node.id, C_CSS.GOTO_LABEL)
            GDT.register_id(node.id.id, C_CSS.GOTO_LABEL)
        elif self.current_token.type == CTokenType.CASE:
            node.update(keyword=self.get_keyword(CTokenType.CASE))
            node.update(const_expr=self.constant_expression())
        elif self.current_token.type == CTokenType.DEFAULT:
            node.update(keyword=self.get_keyword(CTokenType.DEFAULT))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be id or case or default")
        node.register_token(self.eat(TokenType.COLON))
        node.update(stmt=self.statement())
        return node

    def expression_statement(self):
        """
        <expression-statement> ::= <expression>? ";"
        """
        node = ExpressionStatement()
        
        is_macro = self._is_macro()
        if self.current_token.type in self.cfirst_set.expression:
            node.update(expr=self.expression())
        
        # for macro, semicolon is not required in expression because it maybe defined in macro
        # see https://github.com/luzhixing12345/syntaxlight/issues/18
        if not is_macro or (is_macro and self.current_token.type == TokenType.SEMI):
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
            node.update(if_keyword=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be if or switch")
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(expr=self.expression())
        node.register_token(self.eat(TokenType.RPAREN))
        node.update(if_stmt=self.statement())
        if self.current_token.type == CTokenType.ELSE:
            node.update(else_keyword=self.get_keyword())
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
            node.update(keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(stmt=self.statement())
        elif self.current_token.type == CTokenType.DO:
            node.update(keyword=self.get_keyword())
            node.update(stmt=self.statement())
            node.update(while_keyword=self.get_keyword())
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(expr=self.expression())
            node.register_token(self.eat(TokenType.RPAREN))
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == CTokenType.FOR:
            node.update(keyword=self.get_keyword())

            exprs = []
            node.register_token(self.eat(TokenType.LPAREN))
            self._unknown_typedef_id_guess()
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
                node.update(keyword=self.get_keyword())
                node.update(expr=self.get_identifier())
                add_ast_type(node.expr, C_CSS.GOTO_LABEL)
            elif self.current_token.type == CTokenType.RETURN:
                node.update(keyword=self.get_keyword())
                if self.current_token.type in self.cfirst_set.expression:
                    node.update(expr=self.expression())
            else:
                node.update(keyword=self.get_keyword())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be goto continue break return")
        node.register_token(self.eat(TokenType.SEMI))
        return node

    def gnu_c_statement_extension(self):
        """
        https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html

        <gnu-c-statement-extension> ::= (__asm__ | asm ) <asm-qualifiers> "(" <STRING>+ <OutputOperands >* ")"

        <asm-qualifiers> ::= volatile
                           | inline
                           | goto

        <OutputOperands> ::= ":" <STRING>? ( "(" <constant_expression> ")" )? ("," <STRING>? ( "(" <constant_expression> ")" )?)*
        """
        node = GNU_C_Assembly()
        assert self.current_token.type in self.cfirst_set.gnu_c_statement_extension
        node.update(keyword=self.get_keyword())
        if self.current_token.type in (CTokenType.VOLATILE, CTokenType.INLINE, CTokenType.GOTO):
            node.update(asm_qualifier=self.get_keyword())
        node.register_token(self.eat(TokenType.LPAREN))

        sticky_strings = []
        self._skip_macro_def()
        while self.current_token.type == TokenType.STRING:
            sticky_strings.append(self.get_string())
            self._skip_macro_def()
        node.update(sticky_strings=sticky_strings)

        while self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            if self.current_token.type == TokenType.STRING:
                node.register_token(self.eat(TokenType.STRING))
            if self.current_token.type == TokenType.LPAREN:
                node.register_token(self.eat(TokenType.LPAREN))
                self.constant_expression()
                node.register_token(self.eat(TokenType.RPAREN))
            while self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat())
                if self.current_token.type == TokenType.STRING:
                    node.register_token(self.eat(TokenType.STRING))
                if self.current_token.type == TokenType.LPAREN:
                    node.register_token(self.eat(TokenType.LPAREN))
                    self.constant_expression()
                    node.register_token(self.eat(TokenType.RPAREN))

        node.register_token(self.eat(TokenType.RPAREN))

    def get_identifier(self):
        """
        <ID>
        """
        node = Identifier(self.current_token.value)
        token_value = self.current_token.value
        node.register_token(self.eat(TokenType.ID))

        # 判断一下 ID 的 class_name
        if token_value in GDT:
            add_ast_type(node, GDT[token_value])
        elif bool(re.match(r"^[A-Z0-9_]+$", token_value)):
            # ID 全部为 大写/数字/下划线, 很可能为宏
            add_ast_type(node, CSS.MACRO_DEFINE)
            GDT.register_id(node.id, CSS.MACRO_DEFINE)

        return node

    def static_assert_declaration(self):
        """
        <static_assert-declaration> ::= _Static_assert "(" <constant-expression> "," <string> ")"
        """
        node = StaticAssertDeclaration()
        node.update(keyword=self.get_keyword(CTokenType._STATIC_ASSERT))
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(const_expr=self.constant_expression())
        node.register_token(self.eat(TokenType.COMMA))
        node.update(string=self.get_string())
        return node

    def group(self):
        """
        <group> ::= <group-part>*
        """
        node = Group()
        group_parts = []
        while self.current_token.type == TokenType.HASH:
            self._begin_preprocessing()
            group_parts.append(self.group_part())
        node.update(group_parts=group_parts)
        self._end_preprocessing()

        # 添加至 sub_roots
        self.sub_roots.append(node)
        return node

    def _begin_preprocessing(self):
        """
        开始预处理
        """
        # 考虑换行
        if TokenType.LF.value in self.lexer.invisible_characters:
            self.lexer.invisible_characters.remove(TokenType.LF.value)
        self.in_preprocessing = True

    def _end_preprocessing(self):
        """
        终止预处理
        """
        if TokenType.LF.value not in self.lexer.invisible_characters:
            self.lexer.invisible_characters.append(TokenType.LF.value)
        self.in_preprocessing = False
        if self.current_token.type == CTokenType.IF_P:
            self.current_token.type = CTokenType.IF
        elif self.current_token.type == CTokenType.ELSE_P:
            self.current_token.type = CTokenType.ELSE
        elif self.current_token.value in self.preprocessing_keywords:
            self.current_token.type = TokenType.ID

    def group_part(self):
        """
        <group-part> ::= <if-section>
                       | <control-line>
        """
        token_type = self.peek_next_token().type
        if token_type in self.cfirst_set.if_section:
            return self.if_section()
        elif token_type in self.cfirst_set.control_line:
            return self.control_line()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, " unknown preprocess keyword")

    def if_section(self):
        """
        <if-section> ::= <if-group>
                       | <elif-group>
                       | <else-group>
                       | <endif-line>

        @EXTEND-GRAMMAR
        考虑到宏与定义穿插, 这里直接将原始的文法(如下)打散

        <if-section> ::= <if-group> <elif-group>* <else-group>? <endif-line>

        """
        node = IfSection()
        token_type = self.peek_next_token().type
        group = None
        if token_type in self.cfirst_set.if_group:
            group = self.if_group()
        elif token_type in self.cfirst_set.elif_group:
            group = self.elif_group()
        elif token_type in self.cfirst_set.else_group:
            group = self.else_group()
        elif token_type in self.cfirst_set.endif_group:
            group = self.endif_line()
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "preprocess keyword error")
        node.update(group=group)
        return node

    def if_group(self):
        """
        <if-group> ::= "#" if <constant-expression> <CRLF>
                     | "#" ifdef <identifier> <CRLF
                     | "#" ifndef <identifier> <CRLF>
        """
        self.eat(TokenType.HASH)
        node = IfGroup()
        if self.current_token.type == CTokenType.IF_P:
            node.update(keyword=self.get_keyword(CTokenType.IF_P, CSS.PREPROCESS))
            node.update(const_expr=self.constant_expression())
        elif self.current_token.type in (CTokenType.IFDEF, CTokenType.IFNDEF):
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            node.update(id=self.get_identifier())
            add_ast_type(node.id, CSS.MACRO_DEFINE)
            GDT.register_id(node.id.id, CSS.MACRO_DEFINE)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "should be if ifdef ifndef")
        self.eat_lf()
        self._end_preprocessing()
        return node

    def elif_group(self):
        """
        <elif-group> ::= "#" elif <constant-expression> <CRLF>
        """
        self.eat(TokenType.HASH)
        node = ElifGroup()
        node.update(keyword=self.get_keyword(CTokenType.ELIF, css_type=CSS.PREPROCESS))
        node.update(const_expr=self.constant_expression())
        self.eat_lf()
        self._end_preprocessing()
        return node

    def else_group(self):
        """
        <else-group> ::= "#" else <CRLF>
        """
        self.eat(TokenType.HASH)
        node = ElseGroup()
        node.update(keyword=self.get_keyword(CTokenType.ELSE_P, css_type=CSS.PREPROCESS))

        self.eat_lf()
        self._end_preprocessing()
        return node

    def endif_line(self):
        """
        <endif-line> ::= "#" endif <CRLF>
        """
        self.eat(TokenType.HASH)
        node = EndifLine()
        node.update(keyword=self.get_keyword(CTokenType.ENDIF, css_type=CSS.PREPROCESS))
        self.eat_lf()
        self._end_preprocessing()
        # if self.current_token.type in self.cfirst_set.external_declaration:
        #     node.update(group=self.external_declaration())
        return node

    def control_line(self):
        """
        <control-line> ::= "#" include <header-name> <CRLF>
                         | "#" define <identfier> <pp-token>* <CRLF>
                         | "#" define <identifier> "(" <identifier-list>? ")" <pp-token>* <CRLF>
                         | "#" define <identifier> "(" "..." ")" <pp-token>* <CRLF>
                         | "#" define <identifier> "(" <identifier-list> "," "..." ")" <pp-token>* <CRLF>
                         | "#" undef <identifier> <CRLF>
                         | "#" line <pp-token>+ <CRLF>
                         | "#" error <pp-token>* <CRLF>
                         | "#" pragma <pp-token>* <CRLF>
                         | "#" <CRLF>

        <pp-token> ::= any
        """
        self.eat(TokenType.HASH)
        node = ControlLine()
        if self.current_token.type == CTokenType.INCLUDE:
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            node.update(header_name=self.header_name())
        elif self.current_token.type == CTokenType.DEFINE:
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            # define 这里需要考虑空格的影响, 作为函数括号要求前面无空格
            # define A(a,b) 1
            # define A (a,b)
            #
            # 这里禁用skip_space和skip_invisible_characters以单步匹配下一个 token
            self.skip_space = False
            self.skip_invis_chars = False

            # token 第一个 token 可能在 after_eat 中被标记为 TYPEDEF_ID, define 匹配时需要恢复
            # #define ____cacheline_aligned_in_smp ____cacheline_aligned
            # https://github.com/luzhixing12345/syntaxlight/issues/14
            if self.current_token.type == CTokenType.TYPEDEF_ID:
                self.current_token.type = TokenType.ID

            node.update(id=self.get_identifier())
            self.skip_invis_chars = True
            self.skip_space = True
            if self.current_token.type == TokenType.LPAREN:
                # 有 () 说明是宏函数定义
                node.register_token(self.eat(TokenType.LPAREN))
                if self.current_token.type in self.cfirst_set.identifier_list:
                    node.update(parameters=self.identifier_list())
                else:
                    # 对于空参数的也当作宏函数
                    node.parameters = []
                if self.current_token.type == TokenType.VARARGS:
                    node.update(parameterization=self.get_keyword(TokenType.VARARGS))
                node.register_token(self.eat(TokenType.RPAREN))

            # define 后面可能有若干个
            pp_tokens = []
            while self.current_token.type not in (TokenType.EOF, TokenType.LF):
                if self.current_token.type == TokenType.BACK_SLASH:
                    pp_tokens.append(self.pp_token())
                pp_tokens.append(self.pp_token())
            node.update(pp_tokens=pp_tokens)

        elif self.current_token.type == CTokenType.UNDEF:
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            node.update(id=self.get_identifier())
        elif self.current_token.type in (CTokenType.LINE, CTokenType.ERROR):
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            node.update(id=self.get_identifier())

        elif self.current_token.type == CTokenType.PRAGMA:
            node.update(keyword=self.get_keyword(css_type=CSS.PREPROCESS))
            if self.current_token.type in self.cfirst_set.expression:
                self.expression()

        if node.id is not None:
            if node.parameters is not None:
                # parameters 被定义了说明是函数
                # TODO: parameterization
                add_ast_type(node.id, CSS.MACRO_FUNCTION)
                arguments = []
                for i_node in node.parameters:
                    arguments.append(FuncArgument(name=i_node.id, type=None))
                GDT.register_function(node.id.id, arguments, (), CSS.MACRO_FUNCTION)
            else:
                # 常规宏定义变量
                add_ast_type(node.id, CSS.MACRO_DEFINE)
                GDT.register_id(node.id.id, CSS.MACRO_DEFINE)

        self.eat_lf()
        self._end_preprocessing()
        return node

    def pp_token(self):
        """
        any
        """
        if self.current_token.type == TokenType.LANGLE_BRACE:
            self.current_token.type = TokenType.LT
        elif self.current_token.type == TokenType.RANGLE_BRACE:
            self.current_token.type = TokenType.GT

        if self.current_token.type == TokenType.ID:
            # 对于宏套宏的情况, 考虑将后面 ID 也作为宏定义
            if self.current_token.value.startswith("__"):
                self.current_token.add_css(CSS.MACRO_DEFINE)
            return self.get_identifier()
        elif self.current_token.type == TokenType.STRING:
            return self.get_string()
        elif self.current_token.value in self.lexer.reserved_keywords:
            return self.get_keyword()
        elif self.current_token.type in self.cfirst_set.struct_or_union:
            return self.struct_or_union()
        else:
            node = PPtoken(self.current_token.value)
            node.register_token(self.eat())
            return node

    def header_name(self):
        """
        < h-char-sequence >

        any member of the source character set except the new-line character and >

        <string>
        """
        node = HeaderName()
        if self.current_token.type == TokenType.STRING:
            node.update(file_path=self.get_string())
            add_ast_type(node.file_path, C_CSS.HEADER_NAME)
        elif self.current_token.type == TokenType.LANGLE_BRACE:
            node.register_token(self.eat(TokenType.LANGLE_BRACE))
            result = ""
            line = -1
            column = -1
            while self.current_token.type != TokenType.RANGLE_BRACE:
                if self.current_token.type in (TokenType.EOF, TokenType.LF):
                    break
                result += self.current_token.value
                line = self.current_token.line
                column = self.current_token.column
                self.manual_get_next_token()
            if self.current_token.type == TokenType.EOF:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "miss >")
            if self.current_token.type == TokenType.LF:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "\\n inside include <>")

            new_token = Token(TokenType.STRING, result, line, column)
            file_path = String(new_token.value)
            file_path.register_token([new_token])
            self.manual_register_token(new_token)
            node.update(file_path=file_path)
            node.register_token(self.eat(TokenType.RANGLE_BRACE))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, '<> or ""')
        return node

    def gnu_c_attribute(self):
        """
        GNU C Extension

        __attribute__ "(" <expression> ")"
        """
        # if self.current_token.type == CTokenType._ATTRIBUTE:
        node = GNU_C_Assembly()
        node.register_token(self.eat(CTokenType._ATTRIBUTE))
        node.register_token(self.eat(TokenType.LPAREN))
        node.update(expression=self.expression())
        node.register_token(self.eat(TokenType.RPAREN))
        return node

    def _unknown_typedef_id_guess(self, always_match=False):
        """
        @EXTEND-GRAMMAR

        对于未知符号, 判断下一个 token 类型, 更正为 TYPEDEF_ID

        - static clock_t ticks = 10;                  ID
        - static clock_t *ticks = 10;                 *

        下面这种情况没有办法匹配, 唯一的解决措施是在前面手动声明 uint64 的 typedef 或 define
        - static uint64 (*syscalls[])(void)

        如果可以确定一定是函数指针类型的, 可以使用 always_match = True, 例如

        struct file_operations {
            loff_t (*llseek) (struct file *, loff_t, int);
        }

        https://github.com/luzhixing12345/syntaxlight/issues/12
        test/c/45.c
        """
        next_token_types = [TokenType.ID, TokenType.MUL]

        if self.current_token.type == TokenType.ID:
            next_token_type = self.peek_next_token().type
            if always_match or next_token_type in next_token_types:
                self.current_token.type = CTokenType.TYPEDEF_ID
                GDT.register_id(self.current_token.value, CSS.TYPEDEF)

    def _is_macro(self):
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.current_token.value) or self._is_macro_def() or self._is_macro_func()

    def _is_macro_def(self):
        return self.current_token.type in [TokenType.ID, CTokenType.TYPEDEF_ID] and CSS.MACRO_DEFINE.value in self.current_token.class_list
        
    def _is_macro_func(self):
        return self.current_token.type in [TokenType.ID, CTokenType.TYPEDEF_ID] and CSS.MACRO_FUNCTION.value in self.current_token.class_list

    def _skip_macro_def(self):
        """
        @EXTEND-GRAMMAR
        """
        while self._is_macro_def():
            self.eat()
            
    def _skip_macro_func(self):
        if self._is_macro_func():
            self.eat()
            self._match_macro_function()
            
    def get_macro_def(self):
        node = MacroInvocation()
        self.current_token.type = TokenType.ID
        node.update(id = self.get_identifier())
        return node
    
    def get_macro_func(self):
        node = MacroInvocation()
        self.current_token.type = TokenType.ID
        node.update(id = self.get_identifier())
        self._match_macro_function()
        return node