from syntaxlight.ast import NodeVisitor

from .parser import Parser
from ..lexers import TokenType, LuaTokenType, LuaTokenSet, Token
from ..error import ErrorCode
from ..ast import (
    AST,
    NodeVisitor,
    Number,
    String,
    Punctuator,
    Identifier,
    add_ast_type,
    delete_ast_type,
)
from typing import List, Union, Optional
from enum import Enum
from ..gdt import *


class Block(AST):
    def __init__(self) -> None:
        super().__init__()
        self.stats = None
        self.retstat = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.stats)
        node_visitor.link(self, self.retstat)
        return super().visit(node_visitor)


class Statement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.varlist = None
        self.attnamelist = None
        self.explist = None


class ElseIfStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class ElseStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class AttributeName(AST):
    def __init__(self) -> None:
        super().__init__()


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()


class ReturnStatment(AST):
    def __init__(self) -> None:
        super().__init__()


class Label(AST):
    def __init__(self) -> None:
        super().__init__()


class FuncName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.sub_ids = None


class Var(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.varsuffix: Optional[VarSuffix] = None


class VarSuffix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.prefix_exp_suffix = None


class Expression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.functiondef = None


class PrefixExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.var = None
        self.prefix_exp_suffix = None


class PrefixExpressionSuffix(AST):
    def __init__(self) -> None:
        super().__init__()


class FunctionCall(AST):
    def __init__(self) -> None:
        super().__init__()


class Argument(AST):
    def __init__(self) -> None:
        super().__init__()


class FunctionDefinition(AST):
    def __init__(self) -> None:
        super().__init__()


class FunctionBody(AST):
    def __init__(self) -> None:
        super().__init__()


class ParameterList(AST):
    def __init__(self) -> None:
        super().__init__()


class TableConstructor(AST):
    def __init__(self) -> None:
        super().__init__()


class FieldList(AST):
    def __init__(self) -> None:
        super().__init__()


class Field(AST):
    def __init__(self) -> None:
        super().__init__()


class LuaParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.luafirst_set = LuaTokenSet()

    def parse(self):
        self.root = self.chunk()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        return self.root

    def chunk(self):
        """
        <chunk> ::= <block>
        """
        return self.block()

    def block(self):
        """
        <block> ::= (<stat>)* <retstat>?
        """
        node = Block()
        stats = []
        while self.current_token.type in self.luafirst_set.stat:
            stats.append(self.stat())

        node.update(stats=stats)
        if self.current_token.type in self.luafirst_set.retstat:
            node.update(retstat=self.retstat())

        return node

    def stat(self):
        """
        <stat> ::= ';'
                 | <varlist> '=' <explist>
                 | <functioncall>
                 | <label>
                 | break
                 | goto <ID>
                 | do <block> end
                 | while <exp> do <block> end
                 | repeat <block> until <exp>
                 | if <exp> then <block> (elseif <exp> then <block>)* (else <block>)? end
                 | for <ID> '=' <exp> ',' <exp> (',' <exp>)? do <block> end
                 | for <namelist> in <explist> do <block> end
                 | function <funcname> <funcbody>
                 | local function <ID> <funcbody>
                 | local <attnamelist> ('=' <explist>)?
        """
        node = Statement()
        if self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        elif self.current_token.type == TokenType.LPAREN:
            node.update(varlist=self.varlist())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(explist=self.explist())
            self._match_functiondef(node.varlist, node.explist)
        elif self.current_token.type == TokenType.ID:
            # <varlist> '=' <explist>
            # <functioncall>
            # 区分查看下一个 token
            # BUG 无法区分
            if self.peek_next_token().type in (
                TokenType.COMMA,
                TokenType.ASSIGN,
                TokenType.DOT,
                TokenType.LSQUAR_PAREN,
            ):
                node.update(varlist=self.varlist())
                node.register_token(self.eat(TokenType.ASSIGN))
                node.update(explist=self.explist())
                self._match_functiondef(node.varlist, node.explist)
            else:
                node.update(functioncall=self.functioncall())
        elif self.current_token.type in self.luafirst_set.label:
            node.update(label=self.label())
        elif self.current_token.type == LuaTokenType.BREAK:
            node.update(keyword=self.get_keyword(LuaTokenType.BREAK))
        elif self.current_token.type == LuaTokenType.GOTO:
            node.update(keyword=self.get_keyword(LuaTokenType.GOTO))
            node.update(gotoid=self.identifier())
        elif self.current_token.type == LuaTokenType.DO:
            node.update(keyword=self.get_keyword(LuaTokenType.DO))
            node.update(block=self.block())
            node.update(end=self.get_keyword(LuaTokenType.END))
        elif self.current_token.type == LuaTokenType.WHILE:
            node.update(keyword=self.get_keyword(LuaTokenType.WHILE))
            node.update(exp=self.exp())
            node.update(sub_keyword=self.get_keyword(LuaTokenType.DO))
            node.update(block=self.block())
            node.update(end=self.get_keyword(LuaTokenType.END))
        elif self.current_token.type == LuaTokenType.REPEAT:
            node.update(keyword=self.get_keyword(LuaTokenType.REPEAT))
            node.update(block=self.block())
            node.update(sub_keyword=self.get_keyword(LuaTokenType.UNTIL))
            node.update(exp=self.exp())
        elif self.current_token.type == LuaTokenType.IF:
            node.update(keyword=self.get_keyword(LuaTokenType.IF))
            node.update(exp=self.exp())
            node.update(sub_keyword=self.get_keyword(LuaTokenType.THEN))
            node.update(block=self.block())
            elseif_exprs = []
            while self.current_token.type == LuaTokenType.ELSEIF:
                sub_node = ElseIfStatement()
                sub_node.update(keyword=self.get_keyword(LuaTokenType.ELSEIF))
                sub_node.update(exp=self.exp())
                sub_node.update(sub_keyword=self.get_keyword(LuaTokenType.THEN))
                sub_node.update(block=self.block())
                elseif_exprs.append(sub_node)
            node.update(elseif_exprs=elseif_exprs)
            if self.current_token.type == LuaTokenType.ELSE:
                sub_node = ElseStatement()
                sub_node.update(keyword=self.get_keyword(LuaTokenType.ELSE))
                sub_node.update(block=self.block())
                node.update(else_expr=sub_node)
            node.update(end=self.get_keyword(LuaTokenType.END))
        elif self.current_token.type == LuaTokenType.FOR:
            node.update(keyword=self.get_keyword(LuaTokenType.FOR))
            if self.peek_next_token().type == TokenType.ASSIGN:
                node.update(id=self.identifier())
                node.register_token(self.eat(TokenType.ASSIGN))
                exprs = [self.exp()]
                node.register_token(self.eat(TokenType.COMMA))
                exprs.append(self.exp())
                if self.current_token.type == TokenType.COMMA:
                    node.register_token(self.eat(TokenType.COMMA))
                    exprs.append(self.exp())
                node.update(exp=exprs)
                node.update(sub_keyword=self.get_keyword(LuaTokenType.DO))
                node.update(block=self.block())
                node.update(end=self.get_keyword(LuaTokenType.END))
            else:
                node.update(namelist=self.namelist())
                node.update(sub_keyword=self.get_keyword(LuaTokenType.IN))
                node.update(explist=self.explist())
                node.update(third_keyword=self.get_keyword(LuaTokenType.DO))
                node.update(block=self.block())
                node.update(end=self.get_keyword(LuaTokenType.END))
        elif self.current_token.type == LuaTokenType.FUNCTION:
            node.update(keyword=self.get_keyword(LuaTokenType.FUNCTION))
            node.update(funcname=self.funcname())
            node.update(funcbody=self.funcbody())
        elif self.current_token.type == LuaTokenType.LOCAL:
            node.update(keyword=self.get_keyword(LuaTokenType.LOCAL))
            if self.current_token.type == LuaTokenType.FUNCTION:
                node.update(sub_keyword=self.get_keyword(LuaTokenType.FUNCTION))
                node.update(id=self.identifier())
                node.update(funcbody=self.funcbody())
            elif self.current_token.type in self.luafirst_set.attnamelist:
                node.update(attnamelist=self.attnamelist())
                if self.current_token.type == TokenType.ASSIGN:
                    node.register_token(self.eat(TokenType.ASSIGN))
                    node.update(explist=self.explist())
                    self._match_functiondef(node.attnamelist, node.explist)

        return node

    def attnamelist(self):
        """
        <attnamelist> ::= <ID> <attrib> ("," <ID> <attrib>)*
        """
        result = []
        node = AttributeName()
        node.update(id=self.identifier())
        node.update(attribute=self.attrib())
        result.append(node)

        while self.current_token.type == TokenType.COMMA:
            node = AttributeName()
            node.update(id=self.identifier())
            node.update(attribute=self.attrib())
            result.append(node)
        return result

    def attrib(self):
        """
        <attrib> ::= ("<" <ID> ">")?
        """
        if self.current_token.type == TokenType.LANGLE_BRACE:
            node = Attribute()
            node.register_token(self.eat(TokenType.LANGLE_BRACE))
            node.update(id=self.identifier())
            node.register_token(self.eat(TokenType.RANGLE_BRACE))
            return node
        else:
            return None

    def retstat(self):
        """
        <retstat> ::= return (<explist>)? ';'?
        """
        node = ReturnStatment()
        node.update(keyword=self.get_keyword(LuaTokenType.RETURN))
        if self.current_token.type in self.luafirst_set.explist:
            node.update(explist=self.explist())
        if self.current_token.type == TokenType.SEMI:
            node.register_token(self.eat(TokenType.SEMI))
        return node

    def label(self):
        """
        <label> ::= '::' <ID> "::"
        """
        node = Label()
        node.register_token(self.eat(TokenType.DOUBLE_COLON))
        node.update(id=self.identifier())
        node.register_token(self.eat(TokenType.DOUBLE_COLON))
        return node

    def funcname(self):
        """
        <funcname> ::= <ID> ('.' <ID>)* (':' <ID>)?
        """
        node = FuncName()
        node.update(id=self.identifier())
        sub_ids = []
        while self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            sub_ids.append(self.identifier())
        node.update_subnode = True
        node.update(sub_ids=sub_ids)
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(return_value=self.identifier())

        if len(node.sub_ids) == 0:
            add_ast_type(node.id, CSS.FUNCTION_NAME)
        else:
            add_ast_type(node.sub_ids[-1], CSS.FUNCTION_NAME)
        return node

    def varlist(self) -> List[Var]:
        """
        <varlist> ::= <var> (',' <var>)*
        """
        result = [self.var()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.var())
        return result

    def var(self):
        """
        <var> ::= <ID>
                | <prefixexp> '[' <exp> ']'
                | <prefixexp> '.' <ID>

        <prefixexp> ::= <var>
                      | <functioncall>
                      | '(' <exp> ')'

        <functioncall> ::= <prefixexp> (':' <ID>)? <args>

        <var> 同下面的 <prefixexp> <functioncall> 有比较复杂的循环推导, 处理之后的推导式如下

        <var> ::= <ID> <varsuffix>
                | "(" <exp> ")" <prefix_exp_suffix> "[" <exp> "]" <varsuffix>
                | "(" <exp> ")" <prefix_exp_suffix> "." <ID>      <varsuffix>

        <varsuffix> ::= <prefix_exp_suffix> "[" <exp> "]" <varsuffix>
                      | <prefix_exp_suffix> "." <ID>      <varsuffix>
                      | ε
        """
        node = Var()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exp=self.exp())
            node.register_token(self.eat(TokenType.RPAREN))
            node.update(prefix_exp_suffix=self.prefix_exp_suffix())
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                node.update(next_exp=self.exp())
            elif self.current_token.type == TokenType.DOT:
                node.register_token(self.eat(TokenType.DOT))
                node.update(next_id=self.identifier())
            else:
                self.error(ErrorCode.UNEXPECTED_TOKEN, "error in inside var")
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "error in var")

        node.update(varsuffix=self.varsuffix())
        # 对于函数调用的判断
        if node.id is not None and node.varsuffix is not None:
            if node.varsuffix.prefix_exp_suffix is not None:
                add_ast_type(node.id, CSS.FUNCTION_CALL)
        return node

    def varsuffix(self) -> Optional[VarSuffix]:
        """
        <varsuffix> ::= <prefix_exp_suffix> "[" <exp> "]" <varsuffix>
                      | <prefix_exp_suffix> "." <ID>      <varsuffix>
                      | ε
        """

        if self.current_token.type in self.luafirst_set.prefix_exp_suffix:
            node = VarSuffix()
            node.update(prefix_exp_suffix=self.prefix_exp_suffix())
            if self.current_token.type in (TokenType.LSQUAR_PAREN, TokenType.DOT):
                if self.current_token.type == TokenType.LSQUAR_PAREN:
                    node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                    node.update(exp=self.exp())
                    node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                elif self.current_token.type == TokenType.DOT:
                    node.register_token(self.eat(TokenType.DOT))
                    node.update(id=self.identifier())

                node.update(next_exp=self.varsuffix())
            return node
        elif self.current_token.type in (TokenType.LSQUAR_PAREN, TokenType.DOT):
            node = VarSuffix()
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                node.update(exp=self.exp())
                node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            elif self.current_token.type == TokenType.DOT:
                node.register_token(self.eat(TokenType.DOT))
                node.update(id=self.identifier())

            node.update(next_exp=self.varsuffix())
            return node
        else:
            return None

    def namelist(self):
        """
        <namelist> ::= <ID> (',' <ID>)*
        """
        result = [self.identifier()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.identifier())
        return result

    def explist(self) -> List[Expression]:
        """
        <explist> ::= <exp> (',' <exp>)*
        """
        result = [self.exp()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.exp())
        return result

    def exp(self):
        """
        <exp> ::= nil
                | false
                | true
                | <NUMBER>
                | <STR>
                | '...'
                | <functiondef>
                | <prefixexp>
                | <tableconstructor>
                | <exp> <binop> <exp>
                | <unop> <exp>
        """
        if self.current_token.type in (LuaTokenType.NIL, LuaTokenType.FALSE, LuaTokenType.TRUE):
            node = self.get_keyword()
        elif self.current_token.type == TokenType.NUMBER:
            node = Number(self.current_token.value)
            node.register_token(self.eat(TokenType.NUMBER))
        elif self.current_token.type == TokenType.STR:
            node = String(self.current_token.value)
            node.register_token(self.eat(TokenType.STR))
        elif self.current_token.type == TokenType.VARARGS:
            node = Expression()
            varargs = Punctuator(self.current_token.value)
            varargs.register_token(self.eat(TokenType.VARARGS))
            node.update(varargs=varargs)
        elif self.current_token.type in self.luafirst_set.functiondef:
            node = Expression()
            node.update(functiondef=self.functiondef())
        elif self.current_token.type in self.luafirst_set.prefixexp:
            node = Expression()
            node.update(prefixexp=self.prefixexp())
        elif self.current_token.type in self.luafirst_set.tableconstructor:
            node = Expression()
            node.update(tableconstructor=self.tableconstructor())
        elif self.current_token.type in self.luafirst_set.unop:
            node = Expression()
            node.update(unop=self.unop())
            node.update(exp=self.exp())
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "error in exp")

        if self.current_token.type in self.luafirst_set.binop:
            node.update(binop=self.binop())
            node.update(next_exp=self.exp())

        return node

    def prefixexp(self):
        """
        <prefixexp> ::= <var>
                      | <functioncall>
                      | '(' <exp> ')'

        处理之后的推导式如下

        <prefixexp> ::= <var> <prefix_exp_suffix>
                      | "(" <exp> ")" <prefix_exp_suffix>

        <prefix_exp_suffix> ::= (':' <ID>)? <args> <prefix_exp_suffix>
                            | ε
        """
        node = PrefixExpression()
        if self.current_token.type == TokenType.ID:
            node.update(var=self.var())
            node.update(prefix_exp_suffix=self.prefix_exp_suffix())
        elif self.current_token.type == TokenType.LPAREN:
            # <var> 的推导式中与 "(" <exp> ")" <prefix_exp_suffix> 无法直接区分
            self.eat(TokenType.LPAREN)
            exp = self.exp()
            self.eat(TokenType.RPAREN)
            prefix_exp_suffix = self.prefix_exp_suffix()
            if self.current_token.type in (TokenType.LSQUAR_PAREN, TokenType.DOT):
                var = Var()
                var.update(exp=exp)
                var.update(prefix_exp_suffix=prefix_exp_suffix)
                if self.current_token.type == TokenType.LSQUAR_PAREN:
                    var.register_token(self.eat(TokenType.LSQUAR_PAREN))
                    var.update(next_exp=self.exp())
                    var.register_token(self.eat(TokenType.RSQUAR_PAREN))
                else:
                    var.register_token(self.eat(TokenType.DOT))
                    var.update(next_id=self.identifier())
                var.update(varsuffix=self.varsuffix())
                node.update(var=var)
            else:
                node.update(exp=exp)
                node.update(prefix_exp_suffix=prefix_exp_suffix)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "error in prefixexp")

        return node

    def prefix_exp_suffix(self):
        """
        <prefix_exp_suffix> ::= (':' <ID>)? <args> <prefix_exp_suffix>
                            | ε
        """
        if self.current_token.type in self.luafirst_set.prefix_exp_suffix:
            node = PrefixExpressionSuffix()
            if self.current_token.type == TokenType.COLON:
                node.register_token(self.eat(TokenType.COLON))
                node.update(id=self.identifier())
            node.update(args=self.args())
            node.update(next_exp=self.prefix_exp_suffix())
            return node
        else:
            return None

    def functioncall(self):
        """
        <functioncall> ::= <prefixexp> (':' <ID>)? <args>
        """
        node = FunctionCall()
        node.update(prefixexp=self.prefixexp())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(id=self.identifier())
        # node.update(args = self.args())
        return node

    def args(self):
        """
        <args> ::= '(' <explist>? ')'
                 | <tableconstructor>
                 | <STR>
        """
        node = Argument()
        if self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            if self.current_token.type in self.luafirst_set.explist:
                node.update(explist=self.explist())
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.luafirst_set.tableconstructor:
            node.update(table=self.tableconstructor())
        elif self.current_token.type == TokenType.STR:
            sub_node = String(self.current_token.value)
            sub_node.register_token(self.eat(TokenType.STR))
            node.update(string=sub_node)
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "args error")

        return node

    def functiondef(self):
        """
        <functiondef>::= function <funcbody>
        """
        node = FunctionDefinition()
        node.update(keyword=self.get_keyword(LuaTokenType.FUNCTION))
        node.update(funcbody=self.funcbody())
        return node

    def funcbody(self):
        """
        <funcbody> ::= '(' <parlist>? ')' <block> end
        """
        node = FunctionBody()
        node.register_token(self.eat(TokenType.LPAREN))
        if self.current_token.type in self.luafirst_set.parlist:
            node.update(parlist=self.parlist())
        node.register_token(self.eat(TokenType.RPAREN))
        node.update(block=self.block())
        node.update(end=self.get_keyword(LuaTokenType.END))
        return node

    def parlist(self):
        """
        <parlist> ::= <namelist> (',' '...')?
                    | '...'
        """

        if self.current_token.type == TokenType.VARARGS:
            return self.punctuator()
        elif self.current_token.type in self.luafirst_set.namelist:
            node = ParameterList()
            node.update(namelist=self.namelist())
            if self.current_token.type == TokenType.COMMA:
                node.register_token(self.eat(TokenType.COMMA))
                node.update(varargs=self.punctuator(TokenType.VARARGS))
            return node
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "parlist error")

    def tableconstructor(self):
        """
        <tableconstructor> ::= '{' <fieldlist>? '}'
        """
        node = TableConstructor()
        node.register_token(self.eat(TokenType.LCURLY_BRACE))
        if self.current_token.type in self.luafirst_set.fieldlist:
            node.update(fieldlist=self.fieldlist())
        node.register_token(self.eat(TokenType.RCURLY_BRACE))
        return node

    def fieldlist(self):
        """
        <fieldlist> ::= <field> (<fieldsep> <field>)* <fieldsep>?
        """
        node = FieldList()
        node.update(field=self.field())
        punctuators = []
        sub_fields = []
        while (
            self.current_token.type in self.luafirst_set.fieldsep
            and self.peek_next_token().type in self.luafirst_set.field
        ):
            punctuators.append(self.fieldsep())
            sub_fields.append(self.field())
        node.update(punctuators=punctuators)
        node.update(sub_fields=sub_fields)
        if self.current_token.type in self.luafirst_set.fieldsep:
            node.update(fieldsep=self.fieldsep())
        return node

    def field(self):
        """
        <field> ::= '[' <exp> ']' '=' <exp>
                  | <ID> '=' <exp>
                  | <exp>
        """
        node = Field()
        if self.current_token.type == TokenType.LSQUAR_PAREN:
            node.register_token(self.eat(TokenType.LSQUAR_PAREN))
            node.update(exp=self.exp())
            node.register_token(self.eat(TokenType.RSQUAR_PAREN))
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(end_exp=self.exp())
        elif (
            self.current_token.type == TokenType.ID
            and self.peek_next_token().type == TokenType.ASSIGN
        ):
            node.update(id=self.identifier())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(exp=self.exp())
        else:
            node.update(exp=self.exp())
        return node

    def fieldsep(self):
        """
        <fieldsep> ::= ','
                     | ';'
        """
        return self.punctuator()

    def binop(self):
        """
        <binop> ::= '+'
                  | '-'
                  | '*'
                  | '/'
                  | '//'
                  | '^'
                  | '%'
                  | '&'
                  | '~'
                  | '|'
                  | '>>'
                  | '<<'
                  | '..'
                  | '<'
                  | '<='
                  | '>'
                  | '>='
                  | '=='
                  | '~='
                  | and
                  | or
        """
        if self.current_token.type in (LuaTokenType.AND, LuaTokenType.OR):
            return self.get_keyword()
        else:
            return self.punctuator()

    def unop(self):
        """
        <unop> ::= '-'
                 | not
                 | '#'
                 | '~'
        """
        if self.current_token.type == LuaTokenType.NOT:
            return self.get_keyword()
        else:
            return self.punctuator()

    def _match_functiondef(
        self, varlist: Union[AST, List[AST]], explist: Union[List[Expression], Expression]
    ):
        """
        匹配 varlist 和 explist 的函数定义
        """
        if type(varlist) == list and type(explist) == list:
            var_number = len(varlist)
            exp_number = len(explist)
            if var_number > exp_number:
                self.warning("var will be set to nil because of not enough value")
            elif var_number < exp_number:
                self.warning("value will be ignore")
            number = min(var_number, exp_number)
            for i in range(number):
                self._match_single_functiondef(varlist[i], explist[i])

    def _match_single_functiondef(self, var: AST, exp: Expression):
        if isinstance(exp, Expression) and exp.functiondef is not None:
            add_ast_type(var, CSS.FUNCTION_NAME)
