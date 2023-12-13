
from .ast import AST, NodeVisitor, String, Identifier
from typing import List
from enum import Enum

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
