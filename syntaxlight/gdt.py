from typing import List, Union, Dict, Tuple, TypedDict
from enum import Enum


class CSS(Enum):
    FUNCTION_NAME = "FunctionName"  # 函数名
    FUNCTION_POINTER = "FunctionP"  # 函数指针
    FUNCTION_ARG_NAME = "FunctionArgName"  # 函数参数名
    FUNCTION_ARG_TYPE = "FunctionArgType"  # 函数参数类型
    FUNCTION_RETURN_TYPE = "FunctionReturnType"  # 函数返回值
    FUNCTION_CALL = "FunctionCall"
    TYPEDEF = "Typedefine"  # 自定义类型 / 未知类型
    PREPROCESS = "Preprocess"  # 预处理命令
    MACRO_DEFINE = "MacroDefine"  # 宏定义变量
    MACRO_FUNCTION = "MarcroFunction"  # 宏定义函数
    ENUMERATOR = "Enumerator"  # 枚举类
    ENUM_ID = "EnumID"  # 枚举类型


class Descriptor(TypedDict):
    type: Enum
    scope: str


class FuncArgument(TypedDict):
    name: str
    type: Tuple[str]


class GlobalDescriptorTable:
    def __init__(self) -> None:
        self._descriptors: Dict[str, Descriptor] = {}  # 内部维护的全局描述符表
        self._classname_map = {}
        self._loginfo = []

    def _log(self, info: str):
        """
        记录日志
        """
        self._loginfo.append(info)

    def register_id(self, id_name: str, id_type: Enum, scope: str = "global"):
        """ """
        # 允许后面覆盖前面
        if id_name in self._descriptors:
            self._log(f"[register_id]: cover {id_name}")

        self._descriptors[id_name] = {"type": id_type, "scope": scope}

    def register_function(
        self,
        function_name: str,
        arguments: List[FuncArgument],
        return_value: Tuple[str],
        type: Enum,
        scope: str = "global",
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
            "scope": scope,
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
        if name not in self._descriptors:
            return None
        return self._descriptors[name]["type"]

    def __contains__(self, item):
        return item in self._descriptors
