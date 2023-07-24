import re

from syntaxlight.ast import NodeVisitor

from .parser import Parser
from ..lexers import TokenType, LuaTokenType, LuaTokenSet, Token
from ..error import ErrorCode
from ..ast import (
    AST,
    STR,
    Keyword,
    UnaryOp,
    BinaryOp,
    ConditionalExpression,
    Identifier,
    Constant,
    Expression,
    AssignOp,
    NodeVisitor,
    Char,
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
            node.update(keyword = self.get_keyword(LuaTokenType.BREAK))
        elif self.current_token.type == LuaTokenType.GOTO:
            node.update(keyword = self.get_keyword(LuaTokenType.GOTO))
            node.update(gotoid = self.identifier())
        elif self.current_token.type == LuaTokenType.DO:
            node.update(keyword = self.get_keyword(LuaTokenType.DO))
            node.update(block = self.block())
            node.update(end = self.get_keyword(LuaTokenType.END))
        elif self.current_token.type == LuaTokenType.WHILE:
            node.update(keyword = self.get_keyword(LuaTokenType.WHILE))
            

    def attnamelist(self):
        """
        <attnamelist> ::= <ID> <attrib> ("," <ID> <attrib>)*
        """

    def attrib(self):
        """
        <attrib> ::= ("<" <ID> ">")?
        """

    def retstat(self):
        """
        <retstat> ::= return (<explist>)? ';'?
        """

    def label(self):
        """
        <label> ::= '::' <ID> "::"
        """

    def funcname(self):
        """
        <funcname> ::= <ID> ('.' <ID>)* (':' <ID>)?
        """

    def varlist(self):
        """
        <varlist> ::= <var> (',' <var>)*
        """

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

    def explist(self):
        """
        <explist> ::= <exp> (',' <exp>)*
        """

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

    def prefixexp(self):
        """
        <prefixexp> ::= <var>
                      | <functioncall>
                      | '(' <exp> ')'
        """

    def functioncall(self):
        """
        <functioncall> ::= <prefixexp> <args>
                         | <prefixexp> ':' <ID> <args>
        """

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

    def unop(self):
        """
        <unop> ::= '-'
                 | not
                 | '#'
                 | '~'
        """

    def identifier(self):
        """
        <ID>
        """
        node = Identifier(self.current_token.value)
        node.register_token(self.eat(TokenType.ID))
        return node
