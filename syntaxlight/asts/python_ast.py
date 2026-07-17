from .ast import AST

class Python(AST):
    def __init__(self) -> None:
        super().__init__()
        self.statements = []


class PythonStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.kind = None


class Decorator(PythonStatement):
    def __init__(self) -> None:
        super().__init__()
        self.name = None


class ImportStmt(PythonStatement):
    def __init__(self) -> None:
        super().__init__()
        self.from_module = None
        self.names = []
        self.aliases = []


class ClassDef(PythonStatement):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.bases = []
        self.type_params = []


class FunctionDef(PythonStatement):
    def __init__(self) -> None:
        super().__init__()
        self.async_kw = None
        self.name = None
        self.params = []
        self.type_params = []
        self.return_annotation = []


class TypeAlias(PythonStatement):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.type_params = []
        self.value = []