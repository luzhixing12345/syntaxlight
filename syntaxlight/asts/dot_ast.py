
from .ast import AST

class Graph(AST):
    def __init__(self) -> None:
        super().__init__()


class Stmt(AST):
    def __init__(self) -> None:
        super().__init__()
        self.key = None
        self.value = None


class AttrStmt(AST):
    def __init__(self) -> None:
        super().__init__()


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keys = None
        self.values = None


class EdgeStmt(AST):
    def __init__(self) -> None:
        super().__init__()


class NodeId(AST):
    def __init__(self) -> None:
        super().__init__()


class SubGraph(AST):
    def __init__(self) -> None:
        super().__init__()


class EdgeRHS(AST):
    def __init__(self) -> None:
        super().__init__()


class NodeStmt(AST):
    def __init__(self) -> None:
        super().__init__()


class Port(AST):
    def __init__(self) -> None:
        super().__init__()
