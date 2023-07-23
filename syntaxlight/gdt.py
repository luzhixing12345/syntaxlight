
from typing import List, Union, Dict, Tuple,TypedDict
from enum import Enum


class CSS(Enum):

    FUNCTION_NAME = 'FunctionName' # 函数名
    FUNCTION_POINTER = 'FunctionP' # 函数指针
    FUNCTION_ARG_NAME = 'FunctionArgName' # 函数参数名
    FUNCTION_ARG_TYPE = 'FunctionArgType' # 函数参数类型
    FUNCTION_RETURN_TYPE = 'FunctionReturnType' # 函数返回值
    FUNCTION_CALL = "FunctionCall"
    TYPEDEF = "Typedefine" # 自定义类型 / 未知类型
    PREPROCESS = "Preprocess" # 预处理命令
    MACRO_DEFINE = "MacroDefine" # 宏定义变量
    MACRO_FUNCTION = 'MarcroFunction' # 宏定义函数
    ENUMERATOR = 'Enumerator' # 枚举类
    ENUM_ID = 'EnumID' # 枚举类型
    GOTO_LABEL = 'GotoLabel'

    BASE_TYPE = "BaseType"
    STORAGE_TYPE = "StorageType"
    TYPE_SPECIFIER = "TypeSpecifier"
    FUNCTION_TYPE = "FunctionType"
    STRUCTURE_TYPE = "StructureType"
    QUALIFY_TYPE = "QualifyType"
    HEADER_NAME = "HeaderName"
    ALIGN_SPECIFIER = "AlignSpecifier"
    ATOMAIC_TYPE_SPECIFIER = "AtomicTypeSpecifier"
    STRUCTURE_CLASS = "StructureClass"


class GDTType(Enum):
    FUNCTION = 'Function'
    FUNCTION_POINTER = 'FunctionP'
    DEFINE = 'DefineType'
    

class Descriptor(TypedDict):
    type: Enum
    scope: str

class GlobalDescriptorTable:
    def __init__(self) -> None:
        self._descriptors:Dict[str, Descriptor] = {} # 内部维护的全局描述符表
        self._classname_map = {}
        self._loginfo = []

    def _log(self, info:str):
        '''
        记录日志
        '''
        self._loginfo.append(info)

    def register_id(self, id_name: str, id_type: CSS, scope: str = 'global'):
        """ """
        # 允许后面覆盖前面
        if id_name in self._descriptors:
            self._log(f'[register_id]: cover {id_name}')

        self._descriptors[id_name] = {
            'type': id_type,
            'scope': scope
        }

    def register_function(
        self,
        function_name: str,
        arguments: List[Dict[str, str]] = [],
        return_value: Tuple[str] = (),
        scope: str = "global",
    ):
        """
        注册函数

        返回值如果存在多个可能的类型, 保存在 Tuple 后传入
        """
        if function_name in self._descriptors:
            self._log(f'[register_function]: cover {function_name}')
        self._descriptors[function_name] = {
            'type': GDTType.FUNCTION,
            'arguments': arguments,
            'return_value': return_value,
            'scope': scope
        }


    def delete_id(self, name):
        if name in self._descriptors:
            del self._descriptors[name]
            self._log(f"delete id [{name}]")
        else:
            raise ValueError(f"unknown id: {name}")

    def reset(self):
        self._descriptors = {}
        self._log(f"reset GDT")

    def __getitem__(self, name) -> Enum:
        return self._descriptors[name]['type']

    def __contains__(self, item):
        return item in self._descriptors

