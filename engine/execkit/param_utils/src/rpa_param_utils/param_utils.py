from enum import Enum
from typing import Any, Tuple

from rpaatomic.types import Bool
from rpaatomic.types import Dict as RpaDict
from rpaatomic.types import Float, Int
from rpaatomic.types import List as RpaList


class ParamType(Enum):
    PYTHON = "python"  # python模式
    VAR = "var"  # 流变量
    P_VAR = "p_var"  # 流程变量
    G_VAR = "g_var"  # 全局变量
    STR = "str"  # 明确是str
    OTHER = "other"  # int float bool list dict str
    ELEMENT = "element"  # 元素

    @classmethod
    def to_dict(cls):
        return {item.value: item.value for item in cls}


param_type_dict = ParamType.to_dict()


def __dict_deep_traverse__(data, process_func):
    """深度遍历字典"""
    if isinstance(data, dict):
        for key in list(data.keys()):  # 使用list()来避免在遍历过程中修改字典
            value = data[key]
            res = process_func(key, value)
            if res is not None:
                data[key] = res
                continue
            __dict_deep_traverse__(value, process_func)
    elif isinstance(data, list):
        for item in data:
            __dict_deep_traverse__(item, process_func)


def __special_eval__(value: Any, env: dict, id2name: dict = None) -> Any:
    """特殊dict处理"""

    if not isinstance(value, dict):
        return

    if value.get("rpa", "") != "special":
        return

    ls = pre_param_handler(value.get("value", []), None, "", id2name)
    value, need_eval = param_to_eval(ls)
    if not need_eval:
        return value

    code = value
    if not code:
        return code

    try:
        value = eval(code, None, env)
    except Exception as e:
        raise e
    return value


def global_to_dict(ls: list) -> Tuple[dict, dict]:
    """工具类: 全局变量转换为字典"""
    res = {}
    id2name = {}
    for v in ls:
        id2name[v.get("globalId")] = v.get("varName")
        res[v.get("varName")] = v.get("varValue")
    return res, id2name


def special_eval_element(param: dict, env: dict, id2name: dict = None):
    """特殊处理元素"""

    def process_func(key, value):
        # if key not in [""]:
        #     # 为了加速处理
        #     return
        return __special_eval__(value, env, id2name)

    __dict_deep_traverse__(param, process_func)
    return param


def special_eval_parse(param: dict, env: dict, id2name: dict = None):
    """特殊处理解析"""

    def process_func(key, value):
        # if key not in [""]:
        #     # 为了加速处理
        #     return
        return __special_eval__(value, env, id2name)

    __dict_deep_traverse__(param, process_func)
    return param


def pre_param_handler(param_value: Any, param_types: str = None, show_name: str = "", id2name: dict = None):
    """预处理参数"""
    if id2name is None:
        id2name = {}

    ls = []

    # 判断是不是列表, 并且列表的结构符合要求
    if (
        isinstance(param_value, list)
        and len(param_value) > 0
        and "type" in param_value[0]
        and param_value[0]["type"] in param_type_dict
    ):
        # 预处理1: 处理data优先
        # 预处理2: 过略前端无效数据
        for v in param_value:
            if "data" not in v:
                v["data"] = v.get("value", "")
            if v["data"] != "":
                ls.append(v)
        if len(ls) == 0:
            ls.append(param_value[0])
    else:
        ls = [{"type": ParamType.OTHER.value, "data": param_value}]

    # 预处理3: 基于t处理type为other的数据
    # 预处理4: 处理全局变量数据
    for v in ls:
        if v.get("type") == ParamType.OTHER.value and isinstance(v["data"], str):
            try:
                if param_types == "bool":
                    v["data"] = bool(Bool.__validate__(show_name, v["data"]))
                elif param_types == "float":
                    v["data"] = float(Float.__validate__(show_name, v["data"]))
                elif param_types == "int":
                    v["data"] = int(Int.__validate__(show_name, v["data"]))
                elif param_types == "list":
                    v["data"] = list(RpaList.__validate__(show_name, v["data"]))
                elif param_types == "dict":
                    v["data"] = dict(RpaDict.__validate__(show_name, v["data"]))
                elif param_types == "str":
                    v["type"] = ParamType.STR.value
                else:
                    v["type"] = ParamType.STR.value
            except Exception as e:
                raise Exception("{}的值转换成{}失败，原始值:{}。".format(show_name, param_types, v["data"])) from e
        elif v.get("type") == ParamType.G_VAR.value and v["data"] in id2name:
            v["data"] = id2name[v["data"]]
        else:
            # 不用处理
            pass

    # 处理后的数据返回
    return ls


def param_to_eval(ls: list) -> (Any, bool):
    """
    将参数解析成evaL能执行的状态,
    need_eval=False是为了加速, 能够直接算出来就不经过eval处理, 直接输出结果
    """

    # 判断是否需要解析
    need_eval = False
    for v in ls:
        if v.get("type", "str") in [
            ParamType.PYTHON.value,
            ParamType.VAR.value,
            ParamType.G_VAR.value,
            ParamType.P_VAR.value,
        ]:
            need_eval = True
            break

    res = []
    for v in ls:
        types = v.get("type", "str")
        value = v.get("data", "")
        if need_eval:
            # 转换成eval能执行的状态
            if types == ParamType.STR.value:
                res.append('"{}"'.format(value.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")))
            else:
                res.append("{}".format(value))
        else:
            # 直接输出
            res.append(value)

    # 处理最终数据(>1表示拼凑 =1表示正常数据)
    if len(res) > 1:
        if need_eval:
            # 拼接成eval能执行的状态
            return "+".join("str({})".format(r) for r in res), need_eval
        else:
            # 手动拼接
            res_str = ""
            for r in res:
                res_str += str(r)
            return res_str, need_eval
    else:
        return res[0], need_eval
