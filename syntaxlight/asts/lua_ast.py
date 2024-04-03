from .ast import AST, NodeVisitor, String, Identifier
from typing import List
from enum import Enum


class Block(AST):
    def __init__(self) -> None:
        super().__init__()
        self.stats = None
        self.retstat = None


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


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None


class ReturnStatment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.explist = None


class Label(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None


class FuncName(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.sub_ids = None


class Variable(AST):
    def __init__(self) -> None:
        super().__init__()
        self.id: Identifier = None
        self.exp: AST = None
        self.sub_nodes: List[VarSuffix] = None

    def formatter(self, depth: int = 0):  # pragma: no cover
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

    def formatter(self, depth: int = 0):  # pragma: no cover
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

    def formatter(self, depth: int = 0):  # pragma: no cover
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

    def formatter(self, depth: int = 0):  # pragma: no cover
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


class FunctionBody(AST):
    def __init__(self) -> None:
        super().__init__()
        self.parlist = None
        self.block = None
        self.end = None


class ParameterList(AST):
    def __init__(self) -> None:
        super().__init__()
        self.namelist = None
        self.varargs = None


class TableConstructor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.fieldlist = None


class FieldList(AST):
    def __init__(self) -> None:
        super().__init__()
        self.field = None
        self.punctuators = None
        self.sub_fields = None
        self.fieldsep = None


class Field(AST):
    def __init__(self) -> None:
        super().__init__()
        self.exp = None
        self.id = None
        self.end_exp = None
