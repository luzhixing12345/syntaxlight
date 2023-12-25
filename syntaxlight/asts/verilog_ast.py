from .ast import AST
from typing import List


class Verilog(AST):
    def __init__(self) -> None:
        super().__init__()
        self.descriptions: List[Description] = None


class Description(AST):
    def __init__(self) -> None:
        super().__init__()
        self.module: Module = None
        self.udp: UDP = None


class Module(AST):
    def __init__(self) -> None:
        super().__init__()
        self.module = None
        self.name = None
        self.list_of_ports = None
        self.module_items = None
        self.end_keyword = None


class UDP(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.name = None
        self.variable_names = None
        self.udp_declarations = None
        self.udp_initial_statement = None
        self.table_definition = None
        self.end_keyword = None


class Port(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.port_expression = None


class PortReference(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.index_begin = None
        self.index_end = None


class UdpInitialStatement(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.name = None
        self.init_val = None


class TableDefinition(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.entries = None
        self.end_keyword = None


class TableEntry(AST):
    def __init__(self) -> None:
        super().__init__()


class Task(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.name = None
        self.tf_declarations = None
        self.stmt = None
        self.end_keyword = None


class Function(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.range = None
        self.type = None
        self.name = None
        self.stmt = None
        self.end_keyword = None
        
class Parameter(AST):
    def __init__(self) -> None:
        super().__init__()


class ParameterAssign(AST):
    def __init__(self) -> None:
        super().__init__()