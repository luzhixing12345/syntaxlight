from .ast import AST
from typing import List
from ..lexers import Token

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
        self.key = None
        self.value = None


class Declaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.range = None
        self.list_of_variables = None

class NetDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.charge_strength = None
        self.expandrange = None
        self.delay = None
        self.list_of_variables = None

class EventDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.event_names = None


class GateDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.drive_strength = None
        self.delay = None
        self.gate_instances = None
        
class GateInstance(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.range = None
        self.terminals = None

class ContinuousAssign(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.drive_strength = None
        self.expandrange = None
        self.delay = None
        self.list_of_assignments = None

class DriveStrength(AST):
    def __init__(self) -> None:
        super().__init__()
        self.pos1 = None
        self.pos2 = None


class ExpandRange(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.range = None


class Delay(AST):
    def __init__(self) -> None:
        super().__init__()
        self.number = None
        self.id = None
        self.exp1 = None
        self.exp2 = None
        self.exp3 = None


class Assignment(AST):
    def __init__(self) -> None:
        super().__init__()
        self.lvalue = None
        self.exp = None


class Expression(AST):
    def __init__(self) -> None:
        super().__init__()


class Concatenation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expressions = None


class Lvalue(AST):
    def __init__(self) -> None:
        super().__init__()

class ParameterOverride(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.param_assignments = None
        
        
class RegVar(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.index_begin = None
        self.index_end = None
        
        
class UDPInstantiation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.drive_strength = None
        self.delay = None
        self.udp_instances = None
        
class UDPInstance(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.range = None
        self.terminals = None
        

class ModuleInstantiation(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.parms = None
        self.module_instances = None
        
class ModuleInstance(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.range = None
        self.connections = None
        
        
class NamePortConnection(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.expr = None
        

class InitialStmt(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.stmt = None
        
class AlwaysStmt(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.stmt = None
        
class BlockingAssign(AST):
    def __init__(self) -> None:
        super().__init__()
        

class Control(AST):
    def __init__(self) -> None:
        super().__init__()
        self.number = None
        self.id = None
        self.expr = None
        
class EventExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr = None
        self.edge = None
        self.event_expr = None

class Statement(AST):
    def __init__(self) -> None:
        super().__init__()
        

class CaseItem(AST):
    def __init__(self) -> None:
        super().__init__()
        
        
class SeqBlock(AST):
    def __init__(self) -> None:
        super().__init__()
        
class ParBlock(AST):
    def __init__(self) -> None:
        super().__init__()
        
class TaskEnable(AST):
    def __init__(self) -> None:
        super().__init__()
        
class SystemTaskEnable(AST):
    def __init__(self) -> None:
        super().__init__()
        
class SpecifyBlock(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.specify_items = None
        self.end_keyword = None
        
        
class SpecparamDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.assignments = None
        
class PathDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.path_description:PathDeclaration = None
        self.path_delay_value = None
        
class PathDescription(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specify_input_terminal_descriptors = None
        self.specify_output_terminal_descriptors = None
        
class ListOfPathIOnputs(AST):
    def __init__(self) -> None:
        super().__init__()
        self.multiple: bool = False
        self.path_inputs = None        

class SpecifyTerminalDescriptor(AST):
    def __init__(self) -> None:
        super().__init__()
        self.identifier = None
        self.index_begin = None
        self.index_end = None
        
class PathDelayValue(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expressions = None
        
class MintypmaxExpression(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr1 = None
        self.expr2 = None
        self.expr3 = None
        
class Range(AST):
    def __init__(self) -> None:
        super().__init__()
        self.expr1 = None
        self.expr2 = None
        
class Primary(AST):
    def __init__(self) -> None:
        super().__init__()
        self.number = None
        self.id = None
        self.expr1 = None
        self.expr2 = None

class FunctionCall(AST):
    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.arguments = None

class BinaryOp(AST):
    def __init__(self) -> None:
        super().__init__()
        self.op = None
        self.expr1 = None
        self.expr2 = None
        
class UnaryOp(AST):
    def __init__(self) -> None:
        super().__init__()
        self.op = None
        self.expr = None
        
class LevelSensitivePathDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.conditional_port_expression = None
        self.specify_input_terminal_descriptors = None
        self.specify_output_terminal_descriptors = None
        self.path_delay_value = None
        self.polarity_operator = None
        
class EdgeSensitivePathDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.specify_input_terminal_descriptors = None
        self.specify_output_terminal_descriptors = None
        self.path_delay_value = None
        self.polarity_operator = None
        self.data_source_expression = None
        
class SystemTimingCheck(AST):
    def __init__(self) -> None:
        super().__init__()
        self.sysid:Token = None
        self.timing_check_event = None
        self.timing_check_limit = None
        self.notify_register = None
        
class EdgeControlSpecifier(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.edge_descriptors = None
        
class TimeCheckEvent(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.expr = None
        
class ScalarTimingCheckCondition(AST):
    def __init__(self) -> None:
        super().__init__()
        self.op = None
        self.expr = None
        self.constant = None
        
class SDPD(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.conditional_port_expression = None
        self.specify_input_terminal_descriptors = None
        self.specify_output_terminal_descriptors = None
        self.path_delay_value = None
        
        
class GenerateStmt(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.stmt = None
        self.end_keyword = None
        
class GenvarDeclaration(AST):
    def __init__(self) -> None:
        super().__init__()
        self.keyword = None
        self.vars = None
        
class ModuleParameters(AST):
    def __init__(self) -> None:
        super().__init__()
        self.parameter_declarations = None