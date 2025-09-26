import copy
import json

from rpa_param_utils.param_utils import (
    ParamType,
    param_to_eval,
    pre_param_handler,
    special_eval_element,
    special_eval_parse,
)

from rpa_executor.error import *
from rpa_executor.flow.syntax import Environment, InputParam, OutputParam
from rpa_executor.flow.syntax.token import Token, token_type_key_dict


def callback_special_eval_element(svc, param: InputParam, env: Environment, project_id):
    """特殊处理-元素"""
    res = copy.deepcopy(param)
    env = env.to_dict(project_id)
    try:
        res.value["elementData"] = special_eval_element(
            json.loads(param.value.get("elementData")), env, svc.global_id2name
        )
        return res
    except Exception as e:
        raise BaseException(SPECIAL_PARSE_FORMAL, "特殊元素处理异常 {}".format(e)) from e


def callback_special_eval_parse(svc, param: InputParam, env: Environment, project_id):
    """特殊处理-复杂dict"""
    res = copy.deepcopy(param)
    env = env.to_dict(project_id)
    try:
        res.value = special_eval_parse(param.value, env, svc.global_id2name)
        return res
    except Exception as e:
        raise BaseException(SPECIAL_PARSE_FORMAL, "特殊元素处理异常 {}".format(e)) from e


class Params:
    def __init__(self, svc):
        self.svc = svc

    def parse_param(self, project_id: str, i: dict, svc=None, token=None) -> InputParam:
        if i.get("need_parse") is not None:
            # 复杂数据前置处理
            if isinstance(i.get("value"), list) and i.get("need_parse", "") == "str":
                dict_value = i.get("value")
            elif isinstance(i.get("value"), str) and i.get("need_parse", "") == "json_str":
                value = i.get("value")
                if value:
                    try:
                        dict_value = json.loads(value)
                    except Exception as e:
                        raise BaseException(VALUE_NOT_PARSE, "参数解析失败")
                else:
                    dict_value = ""
            else:
                dict_value = i.get("value")

            # 复杂数据解析
            return InputParam(
                types=i.get("types", "Any"),
                key=i.get("name"),
                value=dict_value,
                need_eval=False,
                special="callback_special_eval_parse",
            )
        else:
            if (
                isinstance(i.get("value"), list)
                and len(i.get("value")) == 1
                and i.get("value")[0]["type"] == ParamType.ELEMENT.value
            ):
                # 普通流程的特殊数据1：元素数据(原子能力不可枚举使用特殊类型)
                element_id = i.get("value")[0]["data"]
                try:
                    project_info = svc.project_dict[project_id]
                    value = svc.storage.element_detail(
                        project_id,
                        element_id,
                        project_info.project_mode,
                        project_info.project_version,
                    )
                except Exception as e:
                    raise BaseException(
                        ELEMENT_FAIL_GET_FORMAL.format(element_id),
                        "元素获取异常 {}".format(e),
                    ) from e
                return InputParam(
                    types=i.get("types", "Any"),
                    key=i.get("name"),
                    value=value,
                    need_eval=False,
                    special="callback_special_eval_element",
                )
            elif token and token.value.get("key") == "Script.module" and i.get("key") == "content":
                # 普通流程的特殊数据2：子模块数据(原子能力可以枚举)
                code_id = i.get("value")
                try:
                    project_info = svc.project_dict[project_id]
                    value = svc.storage.module_detail(
                        project_id,
                        code_id,
                        project_info.project_mode,
                        project_info.project_version,
                    )
                except Exception as e:
                    raise BaseException(
                        MODULE_FAIL_GET_FORMAL.format(code_id),
                        "模块获取异常 {}".format(e),
                    ) from e
                return InputParam(
                    types=i.get("types", "Any"),
                    key=i.get("name"),
                    value=value,
                    need_eval=False,
                )
            elif (
                token
                and token.value.get("key") == "Enterprise.get_shared_variable"
                and i.get("key") == "shared_variable"
            ):
                # 远程参数
                code_id = i.get("value", "")
                try:
                    key = svc.storage.get_remote_var_key()
                    value = svc.storage.get_remote_var_value(code_id)
                    if value:
                        value["key"] = key
                except Exception as e:
                    raise BaseException(
                        REMOTE_VARIABLE_FAIL_FORMAT.format(code_id),
                        "远程参数获取异常 {}".format(e),
                    ) from e
                return InputParam(
                    types=i.get("types", "Any"),
                    key=i.get("name"),
                    value=value,
                    need_eval=False,
                )
            else:
                # 普通流程的普通数据
                # 1. 预处理
                ls = pre_param_handler(
                    i.get("value"),
                    i.get("types", "Any").lower(),
                    i.get("title", i.get("name", "")),
                    self.svc.global_id2name,
                )
                # 2. 解析
                value, need_eval = param_to_eval(ls)
                return InputParam(
                    types=i.get("types", "Any"),
                    key=i.get("name"),
                    value=value,
                    need_eval=need_eval,
                )

    def parse_condition_input(self, token: Token) -> dict[str, InputParam]:
        """参数解析比较输入 例如if while"""

        res = {}
        project_id = token.value.get("__project_id__")
        input_list = token.value.get("inputList", [])
        if len(input_list) > 0:
            for i in input_list:
                # 0. 显隐关系
                if not i.get("show", True):
                    continue

                # 1. 解析
                if i.get("name") == "condition":
                    res[i.get("name")] = InputParam(
                        types="Str",
                        key=i.get("name"),
                        value=i.get("value"),
                        need_eval=False,
                    )
                else:
                    res[i.get("name")] = self.parse_param(project_id, i, self.svc)
        return res

    @staticmethod
    def parse_output(token: Token) -> list[OutputParam]:
        """参数解析 输出"""
        res = []
        output_list = token.value.get("outputList", [])
        if len(output_list) > 0:
            for i in output_list:
                # 0. 显隐关系
                if not i.get("show", True):
                    continue
                # 1. 预处理
                ls = pre_param_handler(i.get("value", []))
                # 2. 解析
                res.append(OutputParam(types=i.get("types", "Any"), value=ls[0].get("value", "")))
        return res

    def parse_input(self, token: Token) -> dict[str, InputParam]:
        """参数解析 输入"""

        res = {}
        params_name = {}
        input_list = token.value.get("inputList", [])
        for i in input_list:
            # 优化:过滤高级选项中的默认值，减少参数传递[可以剔除这段优化代码]
            if (
                i.get("key")
                in [
                    "__delay_before__",
                    "__delay_after____",
                    "__retry_time__",
                    "__retry_interval__",
                ]
                and i.get("value") == [{"type": "other", "value": 0}]
                or i.get("key") == "__res_print__"
                and i.get("value") is False
                or i.get("key") == "__skip_err__"
                and i.get("value") == "exit"
            ):
                continue

            # 0. 显隐关系
            if not i.get("show", True):
                continue

            # 1. 收集key对应的名称
            if not i.get("key").startswith("__"):
                params_name[i.get("name")] = i.get("title", "")

            # 2. 解析
            project_id = token.value.get("__project_id__")
            res[i.get("name")] = self.parse_param(project_id, i, self.svc, token)

        # 添加一些高级选项
        if token.type not in token_type_key_dict:
            res["__process_id__"] = InputParam(
                types="Str",
                key="__process_id__",
                value=token.value.get("__process_id__", ""),
                need_eval=False,
            )
            res["__process_name__"] = InputParam(
                types="Str",
                key="__process_name__",
                value=token.value.get("__process_name__", ""),
                need_eval=False,
            )
            res["__atomic_name__"] = InputParam(
                types="Str",
                key="__atomic_name__",
                value=token.value.get("alias", token.value.get("title", "")),
                need_eval=False,
            )
            res["__line__"] = InputParam(
                types="Int",
                key="__line__",
                value=token.value.get("__line__", 0),
                need_eval=False,
            )
            res["__line_id__"] = InputParam(
                types="Str",
                key="__line_id__",
                value=token.value.get("id", ""),
                need_eval=False,
            )
        res["__params_name__"] = InputParam(types="Str", key="__params_name__", value=params_name, need_eval=False)
        return res
