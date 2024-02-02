from typing import List, Union, Dict, Tuple, TypedDict
from enum import Enum


class CSS(Enum):
    FUNCTION_NAME = "FunctionName"  # 函数名
    FUNCTION_POINTER = "FunctionP"  # 函数指针
    FUNCTION_ARG_NAME = "FunctionArgName"  # 函数参数名
    FUNCTION_ARG_TYPE = "FunctionArgType"  # 函数参数类型
    FUNCTION_RETURN_TYPE = "FunctionReturnType"  # 函数返回值
    FUNCTION_CALL = "FunctionCall"  # 函数调用
    CLASS_NAME = "ClassName"  # 类名
    CLASS_INSTANTIATION = "ClassInstantiation"  # 类实例化
    IMPORT_LIBNAME = "ImportLibName"  # 引用库名
    IMPORT_LIBFUNCTION = "ImportLibFunction"  # 引用库函数名
    TYPEDEF = "Typedefine"  # 自定义类型 / 未知类型
    PREPROCESS = "Preprocess"  # 预处理命令
    MACRO_DEFINE = "MacroDefine"  # 宏定义变量
    MACRO_FUNCTION = "MarcroFunction"  # 宏定义函数
    ENUMERATOR = "Enumerator"  # 枚举类
    ENUM_ID = "EnumID"  # 枚举类型
    FORMAT = "Format"
    CONTROL = "Control"
    NUMBER_TYPE = "NumberType" # 数字类型 i32/i64
    CONSTANT = "Constant" # 常量

class Descriptor(TypedDict):
    type: Enum
    scope: str


class FuncArgument(TypedDict):
    name: str
    type: Tuple[str]


class GlobalDescriptorTable:
    def __init__(self, default_import_descriptors: List[Tuple[str, Enum]] = None) -> None:
        self._default_import_descriptors = default_import_descriptors
        self._descriptors: Dict[str, Descriptor] = {}  # 内部维护的全局描述符表
        self._classname_map = {}
        self._loginfo = []
        if self._default_import_descriptors is not None:
            for name, type in self._default_import_descriptors:
                self.register_id(name, type)

        self._scope_gdt: Dict[str, GlobalDescriptorTable] = {}

    def _log(self, info: str):
        """
        记录日志
        """
        self._loginfo.append(info)

    def register_id(self, id_name: str, id_type: Enum, scope: str = None):
        """
        将一个 id 注册到 GDT 中
        """
        assert type(id_name) == str
        if scope is None:
            # 允许后面覆盖前面
            if id_name in self._descriptors:
                self._log(f"[register_id]: cover {id_name}")

            self._descriptors[id_name] = {"type": id_type}
        else:
            if scope not in self._scope_gdt:
                self._scope_gdt[scope] = GlobalDescriptorTable()
            self._scope_gdt[scope].register_id(id_name, id_type)

    def register_function(
        self,
        function_name: str,
        arguments: List[FuncArgument],
        return_value: Tuple[str],
        type: Enum,
    ):
        """
        注册函数

        返回值如果存在多个可能的类型, 保存在 Tuple 后传入
        """
        if function_name in self._descriptors:
            self._log(f"[register_function]: cover {function_name}")
        self._descriptors[function_name] = {
            "type": type,
            "arguments": arguments,
            "return_value": return_value,
        }

    def delete_id(self, name: str):
        if name in self._descriptors:
            del self._descriptors[name]
            self._log(f"delete id [{name}]")
        else:
            raise ValueError(f"unknown id: {name}")

    def delete_scope(self, scope: str):
        """
        删除作用域 scope 下的所有 id
        """
        if scope in self._scope_gdt:
            del self._scope_gdt[scope]

    def reset(self):
        self._descriptors = {}
        if self._default_import_descriptors is not None:
            for name, type in self._default_import_descriptors:
                self.register_id(name, type)
        self._log(f"reset GDT")

    def __getitem__(self, name) -> Enum:
        '''
        优先从 scope 中检查
        '''
        for scope in self._scope_gdt:
            if name in self._scope_gdt[scope]:
                return self._scope_gdt[scope][name]
            
        if name not in self._descriptors:
            return None
        return self._descriptors[name]["type"]

    def __contains__(self, item):
        '''
        优先检查所有 scope 中的 id
        '''
        for scope in self._scope_gdt:
            if item in self._scope_gdt[scope]:
                return True
        return item in self._descriptors

    def __repr__(self) -> str:
        return str(list(self._descriptors.keys()))
