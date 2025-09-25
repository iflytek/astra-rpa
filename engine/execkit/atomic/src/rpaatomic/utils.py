import ast
import inspect
import os
from enum import Enum

from rpaatomic.error import *
from rpaatomic.logger import logger
from rpaatomic.types import Ciphertext


class InspectType(Enum):
    EMPTY = "empty"
    PYTHONBASE = "python_base"
    QUOTE = "quote"
    TYPING = "typing"
    ENUM = "enum"
    RPABASE = "rpa_base"
    OTHER = "other"


class FileExistenceType(Enum):
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CANCEL = "cancel"


def gen_type(__annotation__):
    if __annotation__ == inspect.Parameter.empty:
        # 类型空
        types = "Any"
        kind = InspectType.EMPTY
    elif __annotation__ in [str, list, tuple, int, float, dict, bool]:
        # 基础变量
        types = (
            getattr(__annotation__, "__name__").capitalize()
            if getattr(__annotation__, "__name__", "_empty") != "_empty"
            else None
        )
        kind = InspectType.PYTHONBASE
    elif isinstance(__annotation__, str):
        # 引号类型
        types = __annotation__
        kind = InspectType.QUOTE
    elif str(__annotation__).startswith("typing."):
        # typing.Optional|Union|Any
        types = "Any"
        kind = InspectType.TYPING
        logger.warning("type not support: {}".format(__annotation__))
    elif issubclass(__annotation__, Enum):
        # Enum类型
        types = (
            getattr(__annotation__, "__name__") if getattr(__annotation__, "__name__", "_empty") != "_empty" else None
        )
        kind = InspectType.ENUM
    elif hasattr(__annotation__, "__validate__"):
        # pydantic基础类型扩展
        types = (
            getattr(__annotation__, "__name__") if getattr(__annotation__, "__name__", "_empty") != "_empty" else None
        )
        kind = InspectType.RPABASE
    else:
        # 其他类型
        types = "Any"
        kind = InspectType.OTHER
        logger.warning("type not support: {}".format(__annotation__))
    return types, kind


def handle_existence(file_path, exist_type):
    # 文件存在时的处理方式
    if exist_type == FileExistenceType.OVERWRITE:
        # 覆盖已存在文件，直接返回文件路径
        return file_path
    elif exist_type == FileExistenceType.RENAME:
        if os.path.exists(file_path):
            full_file_name = os.path.basename(file_path)
            file_name, file_ext = os.path.splitext(full_file_name)
            count = 1
            while True:
                new_full_file_name = f"{file_name}_{count}{file_ext}"
                new_file_path = os.path.join(os.path.dirname(file_path), new_full_file_name)
                if os.path.exists(new_file_path):
                    count += 1
                else:
                    return new_file_path
        return file_path
    elif exist_type == FileExistenceType.CANCEL:
        if os.path.exists(file_path):
            return ""
        else:
            return file_path


class ParamModel:
    def __init__(self, inputList: list, params_name_dict: dict, key: str = ""):
        self.inputList = inputList
        self.key = key
        self.params_name_dict = params_name_dict

    @staticmethod
    def parse_conditional(conditional, kwargs) -> bool:
        """解析conditional"""
        res = []
        for i in conditional.operands:
            left = None
            if i.left in kwargs:
                left = kwargs[i.left]

            # > < == != >= <= in
            if i.operator == ">":
                res.append(bool(float(left) > float(i.right)))
            elif i.operator == "<":
                res.append(bool(float(left) < float(i.right)))
            elif i.operator == "==":
                res.append(bool(left == i.right))
            elif i.operator == "!=":
                res.append(bool(left != i.right))
            elif i.operator == ">=":
                res.append(bool(float(left) >= float(i.right)))
            elif i.operator == "<=":
                res.append(bool(float(left) <= float(i.right)))
            elif i.operator == "in":
                res.append(bool(left in i.right))
            else:
                raise BaseException(
                    TYPE_KIND_ERROR_FORMAT.format(i.operator),
                    "类型错误{}".format(i.operator),
                )

        # and or
        if conditional.operators == "and":
            return all(res)
        elif conditional.operators == "or":
            return any(res)
        else:
            raise BaseException(
                TYPE_KIND_ERROR_FORMAT.format(conditional.operators),
                "类型错误{}".format(conditional.operators),
            )

    def __call__(self, **kwargs) -> dict:
        res_list = {}
        for i in self.inputList:
            show_name = self.params_name_dict.get(i.name, i.name)

            # 目前的显影都交给前端来控制
            # # 显隐判断
            # conditional = False
            # if i.conditional is not None:
            #     conditional = self.parse_conditional(i.conditional, kwargs)
            #
            # # 必填判断
            # if i.name not in kwargs and conditional and i.required:
            #     raise BaseException(PARAM_REQUIRED_FORMAT.format(show_name), "参数必填{}".format(show_name))

            if i.name in kwargs:
                value = kwargs[i.name]
            else:
                continue

            # 运行解密
            if isinstance(value, Ciphertext):
                if self.key != "Report.print":
                    value = value.decrypt()

            # 选项判断
            if i.options:
                is_in = False
                for o in i.options:
                    if o.value == value:
                        is_in = True
                        break
                if not is_in:
                    raise BaseException(
                        PARAM_VALUE_ERROR_FORMAT.format(show_name, value),
                        "{}参数的值错误{}".format(show_name, value),
                    )

            # 类型处理
            if i.__annotation__ == inspect.Parameter.empty:
                # 忽略
                pass
            elif i.__annotation__ in [str, list, tuple, int, float, dict, bool]:
                try:
                    if i.__annotation__ in [bool] and isinstance(value, str):
                        if value.lower() in ["false", "none", "undefined", ""]:
                            value = False
                        else:
                            value = i.__annotation__(value)
                    elif i.__annotation__ in [int, float] and isinstance(value, str):
                        if value.lower() in [""]:
                            value = 0
                        else:
                            value = i.__annotation__(value)
                    elif (
                        i.__annotation__ in [list]
                        and isinstance(value, str)
                        and value.startswith("[")
                        and value.endswith("]")
                    ):
                        value = ast.literal_eval(value)
                    elif (
                        i.__annotation__ in [dict]
                        and isinstance(value, str)
                        and value.startswith("{")
                        and value.endswith("}")
                    ):
                        value = ast.literal_eval(value)
                    else:
                        value = i.__annotation__(value)
                except Exception as e:
                    raise BaseException(
                        PARAM_CONVERT_ERROR_FORMAT.format(show_name, i.types, value),
                        "{}的值转换成{}失败{}, error:{}".format(show_name, i.types, value, e),
                    ) from e
            elif isinstance(i.__annotation__, str):
                # 忽略
                pass
            elif str(i.__annotation__).startswith("typing."):
                # 忽略
                pass
            elif issubclass(i.__annotation__, Enum):
                # 转换
                for a in i.__annotation__:
                    if a.value == value:
                        value = a
            elif hasattr(i.__annotation__, "__validate__"):
                # 转换
                try:
                    value = i.__annotation__.__validate__(show_name, value)
                except Exception as e:
                    raise BaseException(
                        PARAM_CONVERT_ERROR_FORMAT.format(show_name, i.types, value),
                        "{}的值装换成{}失败{}, error:{}".format(show_name, i.types, value, e),
                    ) from e
            else:
                # 忽略
                pass
            res_list[i.name] = value
        return res_list
