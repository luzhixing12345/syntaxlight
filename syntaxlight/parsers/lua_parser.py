from syntaxlight.ast import NodeVisitor

from .parser import Parser
from ..lexers import TokenType, LuaTokenType, LuaTokenSet, Token
from ..error import ErrorCode
from ..ast import AST, NodeVisitor, Number, String, Punctuator, Identifier, add_ast_type
from typing import List, Union, Optional
from enum import Enum
from ..gdt import *


class LuaCSS(Enum):
    TABLE_KEY = "TableKey"
    ATTRIBUTE_TYPE = "AttributeType"


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
        self.label = None
        self.keyword = None
        self.gotoid = None
        self.block = None
        self.exp = None
        self.sub_keyword = None
        self.elseif_exprs = None
        self.else_expr = None
        self.funcname = None
        self.funcbody = None
        self.id = None
        self.end = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.varlist)
        node_visitor.link(self, self.attnamelist)
        node_visitor.link(self, self.explist)
        node_visitor.link(self, self.label)
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.gotoid)
        node_visitor.link(self, self.block)
        node_visitor.link(self, self.exp)
        node_visitor.link(self, self.sub_keyword)
        node_visitor.link(self, self.elseif_exprs)
        node_visitor.link(self, self.else_expr)
        node_visitor.link(self, self.funcname)
        node_visitor.link(self, self.funcbody)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.end)
        return super().visit(node_visitor)


class ElseIfStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class ElseStatement(AST):
    def __init__(self) -> None:
        super().__init__()


class AttributeName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.attribute = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.attribute)
        return super().visit(node_visitor)


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        return super().visit(node_visitor)


class ReturnStatment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.explist = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.explist)
        return super().visit(node_visitor)


class Label(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        return super().visit(node_visitor)


class FuncName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.sub_ids = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.sub_ids)
        return super().visit(node_visitor)


class Variable(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.exp: AST = None
        self.sub_nodes: List[VarSuffix] = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.exp)
        node_visitor.link(self, self.sub_nodes)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0): # pragma: no cover
        result = ""
        if self.id:
            result += self.id.formatter(depth + 1)
        else:
            result += f"({self.exp.formatter(depth+1)})"
        for sub_node in self.sub_nodes:
            result += sub_node.formatter(depth=depth + 1)
        return result


class VarSuffixType(Enum):
    INDEX_ID = 0  # [ID]
    DOT_ID = 1  # .ID
    FUNCTION = 2  # ()
    DOT_ID_FUNCTION = 3  # .F()
    COLON_ID_FUNCTION = 4  # :F()


class VarSuffix(AST):
    def __init__(self) -> None:
        super().__init__()
        self.suffix_type: VarSuffixType = None
        self.id: Identifier = None
        self.exp: AST = None
        self.args: Argument = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.exp)
        node_visitor.link(self, self.args)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0): # pragma: no cover
        result = ""
        assert self.suffix_type is not None
        if self.suffix_type == VarSuffixType.INDEX_ID:
            result += f"[{self.exp.formatter(depth=depth+1)}]"
        elif self.suffix_type == VarSuffixType.DOT_ID:
            result += f".{self.id.formatter(depth=depth+1)}"
        elif self.suffix_type == VarSuffixType.FUNCTION:
            result += f"{self.args.formatter(depth=depth+1)}"
        elif self.suffix_type == VarSuffixType.DOT_ID_FUNCTION:
            result += f".{self.id.formatter(depth=depth+1)}({self.args.formatter(depth=depth+1)})"
        else:
            result += f":{self.id.formatter(depth=depth+1)}({self.args.formatter(depth=depth+1)})"

        return result


class Expression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.functiondef = None
        self.string: List[String] = None
        self.varargs = None
        self.prefixexp = None
        self.unop = None
        self.exp = None
        self.binop = None
        self.next_exp = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.functiondef)
        node_visitor.link(self, self.string)
        node_visitor.link(self, self.varargs)
        node_visitor.link(self, self.prefixexp)
        node_visitor.link(self, self.unop)
        node_visitor.link(self, self.exp)
        node_visitor.link(self, self.binop)
        node_visitor.link(self, self.next_exp)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0): # pragma: no cover
        result = ""
        if self.string:
            for st in self.string:
                result += st.formatter(depth=depth + 1)

        return result


class Argument(AST):
    def __init__(self) -> None:
        super().__init__()
        self.explist: List[Expression] = None
        self.table: TableConstructor = None
        self.string: List[String] = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.explist)
        node_visitor.link(self, self.table)
        node_visitor.link(self, self.string)
        return super().visit(node_visitor)

    def formatter(self, depth: int = 0): # pragma: no cover
        result = ""
        if self.explist is not None:
            result += "("
            for exp in self.explist:
                result += exp.formatter(depth=depth + 1)
            result += ")"
        elif self.table is not None:
            result += "table"
        else:
            print(self.string, "xx")
            # for st in self.string:
            #     result += st.formatter(depth=depth + 1)
        return result


class FunctionDefinition(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.funcbody = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.keyword)
        node_visitor.link(self, self.funcbody)
        return super().visit(node_visitor)


class FunctionBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.parlist = None
        self.block = None
        self.end = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.parlist)
        node_visitor.link(self, self.block)
        node_visitor.link(self, self.end)
        return super().visit(node_visitor)


class ParameterList(AST):
    def __init__(self) -> None:
        super().__init__()
        self.namelist = None
        self.varargs = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.namelist)
        node_visitor.link(self, self.varargs)
        return super().visit(node_visitor)


class TableConstructor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.fieldlist = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.fieldlist)
        return super().visit(node_visitor)


class FieldList(AST):
    def __init__(self) -> None:
        super().__init__()
        self.field = None
        self.punctuators = None
        self.sub_fields = None
        self.fieldsep = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.field)
        node_visitor.link(self, self.punctuators)
        node_visitor.link(self, self.sub_fields)
        node_visitor.link(self, self.fieldsep)
        return super().visit(node_visitor)


class Field(AST):
    def __init__(self) -> None:
        super().__init__()
        self.exp = None
        self.id = None
        self.end_exp = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.exp)
        node_visitor.link(self, self.id)
        node_visitor.link(self, self.end_exp)
        return super().visit(node_visitor)


class LuaParser(Parser):
    def __init__(
        self, lexer, skip_invisible_characters=True, skip_space=True, display_warning=True
    ):
        super().__init__(lexer, skip_invisible_characters, skip_space, display_warning)
        self.luafirst_set = LuaTokenSet()

    def parse(self):
        self.root = self.chunk()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF: # pragma: no cover
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

    def attnamelist(self) -> List[AttributeName]:
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

        https://www.lua.org/manual/5.4/manual.html#3.3.7
        """
        if self.current_token.type == TokenType.LANGLE_BRACE:
            node = Attribute()
            node.register_token(self.eat(TokenType.LANGLE_BRACE))
            node.update(id=self.identifier())
            node.register_token(self.eat(TokenType.RANGLE_BRACE))
            # 对于 close 和 const 特殊标记
            if node.id.id in ("close", "const"):
                add_ast_type(node.id, LuaCSS.ATTRIBUTE_TYPE)
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
        else: # pragma: no cover
            self.error(ErrorCode.UNEXPECTED_TOKEN, "error in var, should be id or (")

        sub_nodes = []
        while self.current_token.type in (
            TokenType.LSQUAR_PAREN,
            TokenType.DOT,
            TokenType.COLON,
            # argument
            TokenType.LPAREN,
            TokenType.STR,
            TokenType.LCURLY_BRACE,
        ):
            sub_node = VarSuffix()
            if self.current_token.type == TokenType.LSQUAR_PAREN:
                sub_node.register_token(self.eat(TokenType.LSQUAR_PAREN))
                sub_node.update(exp=self.exp())
                sub_node.register_token(self.eat(TokenType.RSQUAR_PAREN))
                sub_node.suffix_type = VarSuffixType.INDEX_ID

            elif self.current_token.type == TokenType.DOT:
                sub_node.register_token(self.eat(TokenType.DOT))
                sub_node.update(id=self.identifier())
                sub_node.suffix_type = VarSuffixType.DOT_ID
                if self.current_token.type in self.luafirst_set.args:
                    sub_node.update(args=self.args())
                    sub_node.suffix_type = VarSuffixType.DOT_ID_FUNCTION

            elif self.current_token.type in self.luafirst_set.args:
                sub_node.update(args=self.args())
                sub_node.suffix_type = VarSuffixType.FUNCTION
            else:
                # COLON
                sub_node.register_token(self.eat(TokenType.COLON))
                sub_node.update(id=self.identifier())
                sub_node.update(args=self.args())
                sub_node.suffix_type = VarSuffixType.COLON_ID_FUNCTION
            sub_nodes.append(sub_node)

        node.update(sub_nodes=sub_nodes)
        return node

    def _is_functioncall(self, node: Variable):
        # TODO: GDT
        if len(node.sub_nodes) > 0:
            has_functioncall = False
            # 对 .ID() 和 :ID() 的 sub_node 设置为 functioncall
            #
            # a.b(name)().c():d().e.f()
            #
            # b c d f 应为 functioncall
            # e 应为 key
            for sub_node in node.sub_nodes:
                if sub_node.suffix_type in (
                    VarSuffixType.DOT_ID_FUNCTION,
                    VarSuffixType.COLON_ID_FUNCTION,
                ):
                    add_ast_type(sub_node.id, CSS.FUNCTION_CALL)
                    has_functioncall = True
                elif sub_node.suffix_type == VarSuffixType.DOT_ID:
                    add_ast_type(sub_node, LuaCSS.TABLE_KEY)
                # INDEX 不做处理

            if node.sub_nodes[-1].suffix_type in (
                VarSuffixType.DOT_ID_FUNCTION,
                VarSuffixType.COLON_ID_FUNCTION,
                VarSuffixType.FUNCTION,
            ):
                # 如果最后一个 sub_node 是 () 且之前未设置 functioncall
                # 则将开头 node 的 id/exp 设置为 functioncall
                # myModule(name)
                # io.write(name)
                if not has_functioncall:
                    add_ast_type(node.id, CSS.FUNCTION_CALL)
                    add_ast_type(node.exp, CSS.FUNCTION_CALL)
                return True
        return False

    def namelist(self):
        """
        <namelist> ::= <ID> (',' <ID>)*
        """
        result = [self.identifier()]
        while (
            self.current_token.type == TokenType.COMMA
            and self.peek_next_token().type == TokenType.ID
        ):
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
            node = Expression()
            node.update(string=self.string_inside_format(self.current_token))
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
        else: # pragma: no cover
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

    # def functioncall(self):
    #     """
    #     <functioncall> ::= <prefixexp> (':' <ID>)? <args>
    #     """
    #     return self.var()

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
            else:
                node.update(explist=[])
            node.register_token(self.eat(TokenType.RPAREN))
        elif self.current_token.type in self.luafirst_set.tableconstructor:
            node.update(table=self.tableconstructor())
        elif self.current_token.type == TokenType.STR:
            sub_node = self.string_inside_format(self.current_token)
            node.update(string=sub_node)
        else: # pragma: no cover
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
        else: # pragma: no cover
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
                # self.warning("var will be set to nil because of not enough value")
                pass
            elif var_number < exp_number:
                # self.warning("value will be ignore")
                pass
            number = min(var_number, exp_number)
            for i in range(number):
                self._match_single_functiondef(varlist[i], explist[i])

    def _match_single_functiondef(self, var: Union[Variable, AttributeName], exp: Expression):
        if isinstance(exp, Expression) and exp.functiondef is not None:
            if isinstance(var, Variable):
                if len(var.sub_nodes) == 0:
                    add_ast_type(var, CSS.FUNCTION_NAME)
                else:
                    if var.sub_nodes[-1].suffix_type == VarSuffixType.DOT_ID:
                        add_ast_type(var.sub_nodes[-1], CSS.FUNCTION_NAME)
            else:
                # AttributeName
                add_ast_type(var, CSS.FUNCTION_NAME)
