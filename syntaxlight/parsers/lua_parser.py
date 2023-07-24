import re

from syntaxlight.ast import NodeVisitor

from .parser import Parser
from ..lexers import TokenType, LuaTokenType, LuaTokenSet, Token
from ..error import ErrorCode
from ..ast import (
    AST,
    UnaryOp,
    BinaryOp,
    ConditionalExpression,
    Identifier,
    Constant,
    AssignOp,
    NodeVisitor,
    Number,
    String,
    Punctuator,
    add_ast_type,
    delete_ast_type,
)
from typing import List, Union
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


class ElseIfStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class ElseStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class AttributeNameList(AST):
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


class FunctionName(AST):
    def __init__(self) -> None:
        super().__init__()


class Var(AST):
    def __init__(self) -> None:
        super().__init__()


class Expression(AST):
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
        elif self.current_token.type in self.luafirst_set.varlist:
            node.update(varlist=self.varlist())
            node.register_token(self.eat(TokenType.ASSIGN))
            node.update(explist=self.explist())
        elif self.current_token.type in self.luafirst_set.functioncall:
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

        return node

    def attnamelist(self):
        """
        <attnamelist> ::= <ID> <attrib> ("," <ID> <attrib>)*
        """
        node = AttributeNameList()

        ids = [self.identifier()]
        attribs = [self.attrib()]
        while self.current_token.type == TokenType.COMMA:
            node.register_token(self.eat(TokenType.COMMA))
            ids.append(self.identifier())
            attribs.append(self.attrib())

        node.update(ids=ids)
        node.update(attribs=attribs)
        return node

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
        node = FunctionName()
        node.update(id=self.identifier())
        sub_ids = []
        while self.current_token.type == TokenType.DOT:
            node.register_token(self.eat(TokenType.DOT))
            sub_ids.append(self.identifier())
        if self.current_token.type == TokenType.COLON:
            node.register_token(self.eat(TokenType.COLON))
            node.update(return_value=self.identifier())
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
        """

    def namelist(self):
        """
        <namelist> ::= <ID> (',' <ID>)*
        """
        result = [self.identifier()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            result.append(self.identifier())
        return result

    def explist(self):
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
            node.update(functiondef = self.functiondef())
        elif self.current_token.type in self.luafirst_set.prefixexp:
            node = Expression()
            node.update(prefixexp = self.prefixexp())
        elif self.current_token.type in self.luafirst_set.tableconstructor:
            node = Expression()
            node.update(tableconstructor = self.tableconstructor())
        elif self.current_token.type in self.luafirst_set.exp:
            ...

    def prefixexp(self):
        """
        <prefixexp> ::= <var>
                      | <functioncall>
                      | '(' <exp> ')'
        """
        node = PrefixExpression()

    def functioncall(self):
        """
        <functioncall> ::= <prefixexp> <args>
                         | <prefixexp> ':' <ID> <args>
        """
        node = FunctionCall()

    def args(self):
        """
        <args> ::= '(' <explist>? ')'
                 | <tableconstructor>
                 | <STR>
        """

    def functiondef(self):
        """
        <functiondef>::= function <funcbody>
        """

    def funcbody(self):
        """
        <funcbody> ::= '(' <parlist>? ')' <block> end
        """

    def parlist(self):
        """
        <parlist> ::= <namelist> (',' '...')?
                    | '...'
        """

    def tableconstructor(self):
        """
        <tableconstructor> ::= '{' <fieldlist>? '}'
        """

    def fieldlist(self):
        """
        <fieldlist> ::= <field> (<fieldsep> <field>)* <fieldsep>?
        """

    def field(self):
        """
        <field> ::= '[' <exp> ']' '=' <exp>
                  | <ID> '=' <exp>
                  | <exp>
        """

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

