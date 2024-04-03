from .ast import AST, NodeVisitor


class XML(AST):
    def __init__(self) -> None:
        super().__init__()
        self.prolog = None
        self.element = None


class Prolog(AST):
    def __init__(self) -> None:
        super().__init__()
        self.attributes = None


class Attribute(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.value = None


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


class Content(AST):
    def __init__(self, content) -> None:
        super().__init__()
        self.content = content
