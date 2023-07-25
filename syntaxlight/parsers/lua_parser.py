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


class LuaCSS(Enum):
    TABLE_KEY = "TableKey"


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


class Variable(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.exp = None
        self.sub_nodes: List[VarSuffix] = None


class VarSuffixType(Enum):
    INDEX = 0  # [ID]
    DOT = 1  # .ID
    FUNCTION = 2  # F()
    DOT_FUNCTION = 3  # .F()
    COLON_FUNCTION = 4  # :F()


class VarSuffix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.suffix_type: VarSuffixType = None
        self.id = None
        self.args = None


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
        elif self.current_token.type in (TokenType.LPAREN, TokenType.ID):
            # <varlist> 和 <functioncall>
            varlist = self.varlist()
            if len(varlist) == 1 and self._is_functioncall(varlist[0]):
                node = varlist[0]
            else:
                node.update(varlist=varlist)
                node.register_token(self.eat(TokenType.ASSIGN))
                node.update(explist=self.explist())
                self._match_functiondef(node.varlist, node.explist)
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
            node.register_token(self.eat(TokenType.COMMA))
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

    def varlist(self) -> List[Variable]:
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

        <var> 与下面的 prefixexp functioncall 形成了循环推导

        <prefixexp> ::= <var>
                      | <functioncall>
                      | '(' <exp> ')'

        <functioncall> ::= <prefixexp> (':' <ID>)? <args>
        """
        node = Variable()
        if self.current_token.type == TokenType.ID:
            node.update(id=self.identifier())
        elif self.current_token.type == TokenType.LPAREN:
            node.register_token(self.eat(TokenType.LPAREN))
            node.update(exp=self.exp())
            node.register_token(self.eat(TokenType.RPAREN))
        else:
            self.error(ErrorCode.UNEXPECTED_TOKEN, "error in var, should be id or (")

        sub_nodes = []
        while self.current_token.type in (
            TokenType.LSQUAR_PAREN,
            TokenType.DOT,
            TokenType.LPAREN,
            TokenType.COLON,
        ):
            sub_node = VarSuffix()
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                sub_node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                sub_node.update(exp=self.exp())
                sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                sub_node.suffix_type = VarSuffixType.INDEX

            elif self.current_token.type == TokenType.DOT:
                sub_node.register_token(self.eat(TokenType.DOT))
                sub_node.update(id=self.identifier())
                sub_node.suffix_type = VarSuffixType.DOT
                if self.current_token.type == TokenType.LPAREN:
                    sub_node.update(args=self.args())
                    sub_node.suffix_type = VarSuffixType.DOT_FUNCTION

            elif self.current_token.type == TokenType.LPAREN:
                sub_node.update(args=self.args())
                sub_node.suffix_type = VarSuffixType.FUNCTION
            else:
                # COLON
                sub_node.register_token(self.eat(TokenType.COLON))
                sub_node.update(id=self.identifier())
                sub_node.update(args=self.args())
                sub_node.suffix_type = VarSuffixType.COLON_FUNCTION
            sub_nodes.append(sub_node)

        node.update(sub_nodes=sub_nodes)
        return node

    def _is_functioncall(self, node: Variable):
        # TODO: GDT
        functioncall_enum_set = (
            VarSuffixType.DOT_FUNCTION,
            VarSuffixType.COLON_FUNCTION,
        )

        if len(node.sub_nodes) > 0:
            if len(node.sub_nodes) == 1 and node.sub_nodes[0].suffix_type == VarSuffixType.FUNCTION:
                add_ast_type(node.id, CSS.FUNCTION_CALL)
                add_ast_type(node.exp, CSS.FUNCTION_CALL)
                return True

            for sub_node in node.sub_nodes:
                if sub_node.suffix_type in functioncall_enum_set:
                    add_ast_type(sub_node.id, CSS.FUNCTION_CALL)
                elif sub_node.suffix_type == VarSuffixType.DOT:
                    add_ast_type(sub_node, LuaCSS.TABLE_KEY)
                # INDEX 不做处理

            if node.sub_nodes[-1].suffix_type in functioncall_enum_set:
                return True
        return False

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
        """
        node = self.var()
        self._is_functioncall(node)
        return node

    def functioncall(self):
        """
        <functioncall> ::= <prefixexp> (':' <ID>)? <args>
        """
        return self.var()

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
                # TODO 检查返回值个数是否匹配
                self.warning("var will be set to nil because of not enough value")
            elif var_number < exp_number:
                self.warning("value will be ignore")
            number = min(var_number, exp_number)
            for i in range(number):
                self._match_single_functiondef(varlist[i], explist[i])

    def _match_single_functiondef(self, var: AST, exp: Expression):
        if isinstance(exp, Expression) and exp.functiondef is not None:
            add_ast_type(var, CSS.FUNCTION_NAME)
