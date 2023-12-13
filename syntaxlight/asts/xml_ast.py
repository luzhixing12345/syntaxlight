
from .ast import AST, NodeVisitor

class XML(AST):
    def __init__(self) -> None:
        super().__init__()
        self.prolog = None
        self.element = None

    def visit(self, node_visitor: NodeVisitor = None):
        if self.prolog:
            node_visitor.link(self, self.prolog)

        node_visitor.link(self, self.element)
        return super().visit(node_visitor)


class Prolog(AST):
    def __init__(self) -> None:
        super().__init__()
        self.attributes = None

    def visit(self, node_visitor: NodeVisitor = None):
        for attribute in self.attributes:
            node_visitor.link(self, attribute)
        return super().visit(node_visitor)


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.value = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        node_visitor.link(self, self.value)
        return super().visit(node_visitor)


class Name(AST):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class Tag(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.attributes = None
        self.elements = None
        self.end_name = None

    def visit(self, node_visitor: NodeVisitor = None):
        node_visitor.link(self, self.name)
        for attribute in self.attributes:
            node_visitor.link(self, attribute)
        if self.elements:
            for element in self.elements:
                node_visitor.link(self, element)
        if self.end_name:
            node_visitor.link(self, self.end_name)
        return super().visit(node_visitor)


class Content(AST):
    def __init__(self, content) -> None:
        super().__init__()
        self.content = content