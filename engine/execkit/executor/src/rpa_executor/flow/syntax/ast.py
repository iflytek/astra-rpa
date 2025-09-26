import ast
import collections
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union

from rpaatomic.types import Bool, Int
from rpaatomic.types import Dict as RpaDict
from rpaatomic.types import List as RpaList

from rpa_executor.error import FLOW_PARAM_NAME_FORMAT
from rpa_executor.flow.params import (
    callback_special_eval_element,
    callback_special_eval_parse,
)
from rpa_executor.flow.svc import Svc
from rpa_executor.flow.syntax import InputParam, OutputParam
from rpa_executor.flow.syntax.environment import EnvBizTypes, Environment, EnvItem
from rpa_executor.flow.syntax.event import event
from rpa_executor.flow.syntax.sign import BreakSign, ContinueSign, Sign, SignType
from rpa_executor.flow.syntax.token import Token, TokenType


def expression(code: str, svc: Svc, env: Optional[Environment], token: Token, project_id) -> Any:
    """处理python的表达式， 大概率会出现错误"""

    if not code:
        return code
    globals = None
    if env:
        globals = env.to_dict(project_id=project_id)
    try:
        value = eval(code, None, globals)
    except NameError as e:
        if svc.line_debug:
            return None
        else:
            raise e
    except Exception as e:
        raise e
    # 不用回写值，因为用户填写参数不能影响到变量，eval也不支持a=10的回写
    # if env:
    #     env.sync_with_dict(globals)
    return value


def condition_expression(
    condition: dict[str, InputParam],
    svc: Svc,
    env: Environment,
    token: Token,
    project_id,
):
    """处理condition的表达式，先对于expression会后一些和python执行器差异的地方"""

    cond = condition["condition"].value

    args1 = condition["args1"]
    if args1.need_eval:
        args1_val = expression(args1.value, svc, env, token, project_id)
    else:
        args1_val = args1.value

    def raw_condition(a1, a2, cond):
        if cond == ">":
            res = a1 > a2
        elif cond == "==":
            res = a1 == a2
        elif cond == "<":
            res = a1 < a2
        elif cond == "!=":
            res = a1 != a2
        elif cond == ">=":
            res = a1 >= a2
        elif cond == "<=":
            res = a1 <= a2
        elif cond == "in":
            res = a2 in a1
        elif cond == "notin":
            res = a2 not in a1
        elif cond == "true":
            res = bool(a1)
        elif cond == "false":
            res = not bool(a1)
        elif cond == "empty":
            if a1 is None:
                res = True
            elif isinstance(a1, str):
                res = not a1.strip()
            else:
                res = False
        elif cond == "notempty":
            if a1 is None:
                res = False
            elif isinstance(a1, str):
                res = bool(a1.strip())
            else:
                res = True
        else:
            res = False
        return res

    def str_is_integer(s):
        return bool(re.match(r"^-?\d+$", s))

    def str_is_float(s):
        return bool(re.match(r"^-?\d*\.\d+$", s))

    def str_is_list(s):
        return bool(s.startswith("[") and s.endswith("]"))

    def str_is_dict(s):
        return bool(s.startswith("{") and s.endswith("}"))

    if cond in ["true", "false", "empty", "notempty"]:
        # 1. 这个是没有第二个字段的运算符
        if cond in ["true", "false"]:
            # args1_val是布尔值
            args1_val = bool(Bool.__validate__("arg1", args1_val))
        if cond in ["empty", "notempty"]:
            pass
        return raw_condition(args1_val, Node, cond)
    else:
        # 2. 这个是有第二个参数的运算符
        args2 = condition["args2"]
        if args2.need_eval:
            args2_val = expression(args2.value, svc, env, token, project_id)
        else:
            args2_val = args2.value
        if cond in [">", "<", ">=", "<="]:
            # 优先将args1_val转换成数字做比较
            if isinstance(args1_val, str) and (str_is_integer(args1_val) or str_is_float(args1_val)):
                if str_is_integer(args1_val):
                    args1_val = int(args1_val)
                else:
                    args1_val = float(args1_val)
            elif isinstance(args1_val, float) or isinstance(args1_val, int):
                pass
            else:
                args1_val = str(args1_val)

            # 优先将args2_val转换成数字做比较
            if isinstance(args2_val, str) and (str_is_integer(args2_val) or str_is_float(args2_val)):
                if str_is_integer(args2_val):
                    args2_val = int(args2_val)
                else:
                    args2_val = float(args2_val)
            elif isinstance(args2_val, float) or isinstance(args2_val, int):
                pass
            else:
                args2_val = str(args2_val)
            return raw_condition(args1_val, args2_val, cond)
        elif cond in ["in", "notin"]:
            # 优先将args2_val尝试转换成list和dict
            try:
                if (
                    isinstance(args2_val, str)
                    and str_is_list(args2_val)
                    or isinstance(args2_val, str)
                    and str_is_dict(args2_val)
                ):
                    args2_val = ast.literal_eval(args2_val)
            except Exception:
                pass

            # 如果是列表，值换成str之后对比
            if isinstance(args2_val, list):
                args2_val = [str(x) for x in args2_val]

            # args1都转换成str比较
            return raw_condition(str(args1_val), args2_val, cond)
        elif cond in ["==", "!="]:
            # 如果类型相同就直接比较，否则转换成str比较
            if type(args1_val) == type(args2_val):
                pass
            else:
                args1_val = str(args1_val)
                args2_val = str(args2_val)
            return raw_condition(args1_val, args2_val, cond)


def if_condition_expression(
    condition: dict[str, InputParam],
    consequence: "Block",
    svc: Svc,
    env: Environment,
    token: Token,
    project_id,
) -> Any:
    """if执行主要是为了处理else if无限叠层"""

    if condition_expression(condition, svc, env, token, project_id):
        if consequence:
            res = consequence.run(svc, env)
            if res is not None:
                # 上抛出异常
                assert isinstance(res, Sign)
                if res.type in [SignType.Return, SignType.Continue, SignType.Break]:
                    return res
        return True
    else:
        return False


@dataclass
class Node(ABC):
    # 标识
    token: Token = None
    # 是否初始化完成
    is_init: bool = False

    @abstractmethod
    def init(self, svc: Svc):
        pass

    @abstractmethod
    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        pass


@dataclass
class Program(Node):
    token: Token = None
    statements: list[Node] = None

    def init(self, svc: Svc):
        self.is_init = True
        if self.statements:
            for statement in self.statements:
                statement.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            # 处理全局变量
            for gk, gv in env.get_global(svc.start_project_id).items():
                if isinstance(gv.value, InputParam):
                    if gv.value.need_eval:
                        gv.value = expression(gv.value.value, svc, None, self.token, svc.start_project_id)
                    else:
                        gv.value = gv.value.value

            process_param_dict: dict = {}
            process_param_list = svc.run_param
            for v in process_param_list:
                process_param_dict[v.get("varName")] = v

            # 处理主流程变量
            process_return_key = []
            if svc.start_process_id in svc.process_dict:
                for p_v in svc.process_dict[svc.start_process_id].param:
                    # 获取返回值
                    if p_v.get("varDirection", 1) and int(p_v.get("varDirection", 1)) == 1:
                        process_return_key.append(p_v.get("varName", ""))

                    # 计算值
                    if p_v.get("varName", "") in process_param_dict:
                        # 获取传参值
                        p_v_value = process_param_dict[p_v.get("varName", "")].get("varValue", None)
                    else:
                        # 计算默认值
                        p_v_value = svc.params.parse_param(
                            svc.start_project_id,
                            {
                                "types": p_v.get("varType", "Any"),
                                "name": p_v.get("varName", ""),
                                "value": p_v.get("varValue", ""),
                                "title": p_v.get(FLOW_PARAM_NAME_FORMAT.format(p_v.get("varName", ""))),
                            },
                            svc,
                        )
                        if isinstance(p_v_value, InputParam):
                            if p_v_value.need_eval:
                                p_v_value = expression(
                                    p_v_value.value,
                                    svc,
                                    None,
                                    self.token,
                                    svc.start_project_id,
                                )
                            else:
                                p_v_value = p_v_value.value

                    # 设置局部变量
                    env.setitem(
                        svc.start_project_id,
                        p_v.get("varName", ""),
                        EnvItem(
                            biz_types=EnvBizTypes.Other,
                            types=p_v.get("varType", "Any"),
                            key=p_v.get("varName", ""),
                            value=p_v_value,
                            ext={
                                "id": p_v.get("id"),
                                "varDirection": p_v.get("varDirection"),
                                "varDescribe": p_v.get("varDescribe"),
                            },
                        ),
                    )

            if self.statements:
                for statement in self.statements:
                    res = statement.run(svc, env)
                    if res is None:
                        continue

                    # 中断后续执行, 并向上抛出
                    assert isinstance(res, Sign)
                    if res.type == SignType.Return:
                        return res

            # 输出参数
            res = {}
            for r in process_return_key:
                r_v = env.getitem(svc.start_project_id, r)
                res[r_v.key] = r_v.value
            return res

        return raw_run()


@dataclass
class Component(Node):
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None
    token: Token = None
    statements: list[Node] = None

    def init(self, svc: Svc):
        self.__arguments__ = {}
        params = svc.params.parse_input(self.token)
        if len(params) > 0:
            for pk, pv in params.items():
                self.__arguments__[pk] = pv
        self.__returned__ = svc.params.parse_output(self.token)

        self.is_init = True
        if self.statements:
            for statement in self.statements:
                statement.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            # 重新生成一个env继承父类的全局数据，剔除局部变量
            new_env = env.new_process_environment()
            project_id = self.token.value.get("__project_id__")
            process_id = self.token.value.get("__process_id__")

            # 处理全局变量
            for gk, gv in env.get_global(project_id).items():
                if isinstance(gv.value, InputParam):
                    if gv.value.need_eval:
                        gv.value = expression(gv.value.value, svc, None, self.token, project_id)
                    else:
                        gv.value = gv.value.value

            # 处理参数
            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)

                    # 特殊处理
                    if v.special:
                        if v.special == "callback_special_eval_element":
                            v = callback_special_eval_element(svc, v, env, project_id)
                        elif v.special == "callback_special_eval_parse":
                            v = callback_special_eval_parse(svc, v, env, project_id)

                    # 去执行
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            process_param_dict: dict = {}
            for i, v in arguments.items():
                process_param_dict[i] = {
                    "varName": i,
                    "varValue": v,
                }

            # 处理子流程变量
            process_return_key = []
            if process_id in svc.process_dict:
                for p_v in svc.process_dict[process_id].param:
                    # 获取返回值
                    if p_v.get("varDirection", 1) and int(p_v.get("varDirection", 1)) == 1:
                        process_return_key.append(p_v.get("varName", ""))

                    # 计算值
                    if p_v.get("varName", "") in process_param_dict:
                        # 获取传参值
                        p_v_value = process_param_dict[p_v.get("varName", "")].get("varValue", None)
                    else:
                        # 计算默认值
                        p_v_value = svc.params.parse_param(
                            project_id,
                            {
                                "types": p_v.get("varType", "Any"),
                                "name": p_v.get("varName", ""),
                                "value": p_v.get("varValue", ""),
                                "title": p_v.get(FLOW_PARAM_NAME_FORMAT.format(p_v.get("varName", ""))),
                            },
                            svc,
                        )
                        if isinstance(p_v_value, InputParam):
                            if p_v_value.need_eval:
                                p_v_value = expression(p_v_value.value, svc, None, self.token, project_id)
                            else:
                                p_v_value = p_v_value.value

                    # 设置局部变量
                    new_env.setitem(
                        project_id,
                        p_v.get("varName", ""),
                        EnvItem(
                            biz_types=EnvBizTypes.Other,
                            types=p_v.get("varType", "Any"),
                            key=p_v.get("varName", ""),
                            value=p_v_value,
                            ext={
                                "id": p_v.get("id"),
                                "varDirection": p_v.get("varDirection"),
                                "varDescribe": p_v.get("varDescribe"),
                            },
                        ),
                    )
            if self.statements:
                for statement in self.statements:
                    res = statement.run(svc, new_env)
                    if res is None:
                        continue

                    # 中断后续执行, 并向上抛出
                    assert isinstance(res, Sign)
                    if res.type == SignType.Return:
                        return res

            returned = []
            if len(self.__returned__) > 0:
                for r in self.__returned__:
                    if r.special:
                        pass
                    if r:
                        returned.append(r)

            for i, r in enumerate(returned):
                pr_k = process_return_key[i]
                pr_v = new_env.getitem(project_id, pr_k)
                # 回收掉(不回收其实也行，因为子流程全部运行结束，后续确实都不会使用了)
                new_env.delitem(pr_k)

                t_biz_types = EnvBizTypes.Flow
                if new_env.in_global(project_id, r.value):
                    t_biz_types = EnvBizTypes.Global
                env.setitem(
                    project_id,
                    r.value,
                    EnvItem(
                        biz_types=t_biz_types,
                        types=returned[0].types,
                        key=r.value,
                        value=pr_v.value,
                    ),
                )
            return

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class ChildProgram(Node):
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None
    token: Token = None
    statements: list[Node] = None

    def init(self, svc: Svc):
        self.__arguments__ = {}
        params = svc.params.parse_input(self.token)
        if len(params) > 0:
            for pk, pv in params.items():
                self.__arguments__[pk] = pv
        self.__returned__ = svc.params.parse_output(self.token)

        self.is_init = True
        if self.statements:
            for statement in self.statements:
                statement.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            # 重新生成一个env继承父类的全局数据，剔除局部变量
            new_env = env.new_process_environment()

            project_id = self.token.value.get("__project_id__")

            # 处理参数
            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)

                    # 特殊处理
                    if v.special:
                        if v.special == "callback_special_eval_element":
                            v = callback_special_eval_element(svc, v, env, project_id)
                        elif v.special == "callback_special_eval_parse":
                            v = callback_special_eval_parse(svc, v, env, project_id)

                    # 去执行
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            # todo 处理组件和子流程的差异
            process_param_dict: dict = {}
            process_param_list = arguments.get("process_param", [])
            for v in process_param_list:
                process_param_dict[v.get("varName")] = v

            # 处理子流程变量
            process_return_key = []
            process_id = arguments.get("process", "")
            if process_id in svc.process_dict:
                for p_v in svc.process_dict[process_id].param:
                    # 获取返回值
                    if p_v.get("varDirection", 1) and int(p_v.get("varDirection", 1)) == 1:
                        process_return_key.append(p_v.get("varName", ""))

                    # 计算值
                    if p_v.get("varName", "") in process_param_dict:
                        # 获取传参值
                        p_v_value = process_param_dict[p_v.get("varName", "")].get("varValue", None)
                    else:
                        # 计算默认值
                        p_v_value = svc.params.parse_param(
                            project_id,
                            {
                                "types": p_v.get("varType", "Any"),
                                "name": p_v.get("varName", ""),
                                "value": p_v.get("varValue", ""),
                                "title": p_v.get(FLOW_PARAM_NAME_FORMAT.format(p_v.get("varName", ""))),
                            },
                            svc,
                        )
                        if isinstance(p_v_value, InputParam):
                            if p_v_value.need_eval:
                                p_v_value = expression(p_v_value.value, svc, None, self.token, project_id)
                            else:
                                p_v_value = p_v_value.value

                    # 设置局部变量
                    new_env.setitem(
                        project_id,
                        p_v.get("varName", ""),
                        EnvItem(
                            biz_types=EnvBizTypes.Other,
                            types=p_v.get("varType", "Any"),
                            key=p_v.get("varName", ""),
                            value=p_v_value,
                            ext={
                                "id": p_v.get("id"),
                                "varDirection": p_v.get("varDirection"),
                                "varDescribe": p_v.get("varDescribe"),
                            },
                        ),
                    )
            if self.statements:
                for statement in self.statements:
                    res = statement.run(svc, new_env)
                    if res is None:
                        continue

                    # 中断后续执行, 并向上抛出
                    assert isinstance(res, Sign)
                    if res.type == SignType.Return:
                        return res

            returned = []
            if len(self.__returned__) > 0:
                for r in self.__returned__:
                    if r.special:
                        pass
                    if r:
                        returned.append(r)

            if len(returned) > 0:
                if len(returned) > 1:
                    # 不会存在多个只
                    pass
                else:
                    t_key = returned[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    # 合并返回值
                    res = {}
                    for r in process_return_key:
                        r_v = new_env.getitem(project_id, r)
                        res[r_v.key] = r_v.value
                        # 回收掉(不回收其实也行，因为子流程全部运行结束，后续确实都不会使用了)
                        new_env.delitem(r)
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=returned[0].types,
                            key=t_key,
                            value=res,
                        ),
                    )
            return

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class Block(Node):
    token: Token = None
    statements: list[Node] = None

    def init(self, svc: Svc):
        self.is_init = True
        if self.statements:
            for statement in self.statements:
                statement.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            # python block 没有作用域的概念
            # 其他语言是否 block 作用域的概念
            # env = env.new_enclose_environment()

            if self.statements:
                for statement in self.statements:
                    res = statement.run(svc, env)
                    if res is None:
                        continue

                    # 中断后续执行, 并向上抛出
                    assert isinstance(res, Sign)
                    if res.type in [SignType.Break, SignType.Continue, SignType.Return]:
                        return res
            return

        return raw_run()


@dataclass
class Atomic(Node):
    token: Token = None
    init_err = None
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None

    def init(self, svc: Svc):
        try:
            self.__arguments__ = {}
            params = svc.params.parse_input(self.token)
            if len(params) > 0:
                for pk, pv in params.items():
                    self.__arguments__[pk] = pv
            self.__returned__ = svc.params.parse_output(self.token)
            svc.atomic.init(self.token, svc.cache_dir)
            self.is_init = True
        except Exception as e:
            self.init_err = e
            self.is_init = True

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, env, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            if self.init_err is not None:
                raise self.init_err

            project_id = self.token.value.get("__project_id__")

            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)

                    # 特殊处理
                    if v.special:
                        if v.special == "callback_special_eval_element":
                            v = callback_special_eval_element(svc, v, env, project_id)
                        elif v.special == "callback_special_eval_parse":
                            v = callback_special_eval_parse(svc, v, env, project_id)

                    # 去执行
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            res = svc.atomic.run(self.token, svc, env, arguments)
            returned = []
            if len(self.__returned__) > 0:
                for r in self.__returned__:
                    if r.special:
                        pass
                    if r:
                        returned.append(r)

            if len(returned) > 0:
                if len(returned) > 1:
                    for i, v in enumerate(returned):
                        t_key = v.value
                        t_biz_types = EnvBizTypes.Flow
                        if env.in_global(project_id, t_key):
                            t_biz_types = EnvBizTypes.Global
                        env.setitem(
                            project_id,
                            t_key,
                            EnvItem(
                                biz_types=t_biz_types,
                                types=v.types,
                                key=t_key,
                                value=res[i],
                            ),
                        )
                else:
                    t_key = returned[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=returned[0].types,
                            key=t_key,
                            value=res,
                        ),
                    )

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class AtomicExist(Node):
    """缝合原子能力和IF"""

    token: Token = None
    init_err = None
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None

    consequence: Block = None
    conditions_and_blocks: list["IF"] = None
    alternative: Block = None

    def init(self, svc: Svc):
        try:
            self.__arguments__ = {}
            params = svc.params.parse_input(self.token)
            if len(params) > 0:
                for pk, pv in params.items():
                    self.__arguments__[pk] = pv
            self.__returned__ = svc.params.parse_output(self.token)

            svc.atomic.init(self.token, svc.cache_dir)
            if self.conditions_and_blocks:
                for i in self.conditions_and_blocks:
                    i.init(svc)
            self.is_init = True
            if self.consequence:
                self.consequence.init(svc)
            if self.alternative:
                self.alternative.init(svc)
        except Exception as e:
            self.init_err = e
            self.is_init = True

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, Node, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            if self.init_err is not None:
                # 提前结束
                return

            project_id = self.token.value.get("__project_id__")

            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)

                    # 特殊处理
                    if v.special:
                        if v.special == "callback_special_eval_element":
                            v = callback_special_eval_element(svc, v, env, project_id)
                        elif v.special == "callback_special_eval_parse":
                            v = callback_special_eval_parse(svc, v, env, project_id)

                    # 去执行
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            atomic_res = svc.atomic.run(self.token, svc, env, arguments)

            # 如果返回值为True 且 self.consequence这个存在的话
            if atomic_res and self.consequence:
                res = self.consequence.run(svc, env)
                if res is not None:
                    # 上抛出异常
                    assert isinstance(res, Sign)
                    if res.type in [SignType.Return, SignType.Continue, SignType.Break]:
                        return res
            if not atomic_res:
                if self.conditions_and_blocks:
                    for i in self.conditions_and_blocks:
                        event.debug_handler(svc, env, i.token)
                        c_res = if_condition_expression(
                            i.__condition__,
                            i.consequence,
                            svc,
                            env,
                            i.token,
                            project_id,
                        )
                        # 中断后续执行, 并向上抛出
                        if not isinstance(c_res, bool):
                            assert isinstance(c_res, Sign)
                            if c_res.type in [
                                SignType.Return,
                                SignType.Continue,
                                SignType.Break,
                            ]:
                                return c_res

                        # 如果执行成功，就结束后续执行
                        if c_res:
                            return
                if self.alternative:
                    event.debug_handler(svc, env, self.alternative.token)
                    a_res = self.alternative.run(svc, env)
                    if a_res is not None:
                        # 上抛出异常
                        assert isinstance(a_res, Sign)
                        if a_res.type in [
                            SignType.Return,
                            SignType.Continue,
                            SignType.Break,
                        ]:
                            return a_res

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class AtomicFor(Node):
    token: Token = None
    init_err = None

    body: Block = None
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None

    def init(self, svc: Svc):
        try:
            self.__arguments__ = {}
            params = svc.params.parse_input(self.token)
            if len(params) > 0:
                for pk, pv in params.items():
                    self.__arguments__[pk] = pv
            self.__returned__ = svc.params.parse_output(self.token)
            svc.atomic.init(self.token, svc.cache_dir)
            self.is_init = True

            if self.body:
                self.body.init(svc)
        except Exception as e:
            self.init_err = e
            self.is_init = True

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, Node, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            if self.init_err is not None:
                # 提前结束
                return

            project_id = self.token.value.get("__project_id__")

            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)

                    # 特殊处理
                    if v.special:
                        if v.special == "callback_special_eval_element":
                            v = callback_special_eval_element(svc, v, env, project_id)
                        elif v.special == "callback_special_eval_parse":
                            v = callback_special_eval_parse(svc, v, env, project_id)

                    # 去执行
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            atomic_res = svc.atomic.run(self.token, svc, env, arguments)
            if isinstance(atomic_res, list):
                lists = atomic_res
                i = 0
                ls = len(lists)
                while True:
                    event.debug_handler(svc, env, self.token)
                    if i >= ls:
                        break
                    v = lists[i]

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=i,
                        ),
                    )

                    t_key = self.__returned__[1].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[1].types,
                            key=t_key,
                            value=v,
                        ),
                    )

                    res = self.body.run(svc, env)
                    if res is None:
                        i += 1
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += 1
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += 1
            elif isinstance(atomic_res, dict):
                dicts = atomic_res
                keys = list(dicts.keys())

                i = 0
                ls = len(keys)
                while True:
                    event.debug_handler(svc, env, self.token)
                    if i >= ls:
                        break
                    k = keys[i]
                    v = dicts[k]

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=k,
                        ),
                    )

                    t_key = self.__returned__[1].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[1].types,
                            key=t_key,
                            value=v,
                        ),
                    )

                    res = self.body.run(svc, env)
                    if res is None:
                        i += 1
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += 1
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += 1
            elif isinstance(atomic_res, collections.abc.Iterable):
                # 处理迭代器
                i = 0
                iterator = iter(atomic_res)
                while True:
                    event.debug_handler(svc, env, self.token)

                    try:
                        iterator_res = next(iterator)
                    except StopIteration:
                        break

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=i,
                        ),
                    )

                    t_key = self.__returned__[1].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[1].types,
                            key=t_key,
                            value=iterator_res,
                        ),
                    )

                    res = self.body.run(svc, env)
                    if res is None:
                        i += 1
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += 1
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += 1
            else:
                raise TypeError(f"不支持的类型: {type(atomic_res)}")

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class Break(Node):
    token: Token = None

    def init(self, svc: Svc):
        self.is_init = True

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            return BreakSign

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class Continue(Node):
    token: Token = None

    def init(self, svc: Svc):
        self.is_init = True

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            return ContinueSign

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class IF(Node):
    token: Token = None
    consequence: Block = None
    conditions_and_blocks: list["IF"] = None
    alternative: Block = None
    __condition__: dict[str, InputParam] = None

    def init(self, svc: Svc):
        self.__condition__ = svc.params.parse_condition_input(self.token)
        if self.conditions_and_blocks:
            for i in self.conditions_and_blocks:
                i.init(svc)
        self.is_init = True
        if self.consequence:
            self.consequence.init(svc)
        if self.alternative:
            self.alternative.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, env, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            project_id = self.token.value.get("__project_id__")

            res = if_condition_expression(self.__condition__, self.consequence, svc, env, self.token, project_id)
            if not isinstance(res, bool):
                assert isinstance(res, Sign)
                if res.type in [SignType.Return, SignType.Continue, SignType.Break]:
                    return res
            if not res:
                if self.conditions_and_blocks:
                    for i in self.conditions_and_blocks:
                        event.debug_handler(svc, env, i.token)
                        c_res = if_condition_expression(
                            i.__condition__,
                            i.consequence,
                            svc,
                            env,
                            i.token,
                            project_id,
                        )
                        # 中断后续执行, 并向上抛出
                        if not isinstance(c_res, bool):
                            assert isinstance(c_res, Sign)
                            if c_res.type in [
                                SignType.Return,
                                SignType.Continue,
                                SignType.Break,
                            ]:
                                return c_res

                        # 如果执行成功，就结束后续执行
                        if c_res:
                            return
                if self.alternative:
                    event.debug_handler(svc, env, self.alternative.token)
                    a_res = self.alternative.run(svc, env)
                    if a_res is not None:
                        # 上抛出异常
                        assert isinstance(a_res, Sign)
                        if a_res.type in [
                            SignType.Return,
                            SignType.Continue,
                            SignType.Break,
                        ]:
                            return a_res

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class While(Node):
    token: Token = None
    body: Block = None
    __condition__: dict[str, InputParam] = None

    def init(self, svc: Svc):
        self.__condition__ = svc.params.parse_condition_input(self.token)
        self.is_init = True
        if self.body:
            self.body.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, env, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            project_id = self.token.value.get("__project_id__")

            while True:
                event.debug_handler(svc, env, self.token)
                if not condition_expression(self.__condition__, svc, env, self.token, project_id):
                    break

                res = self.body.run(svc, env)
                if res is None:
                    continue

                # 中断后续执行
                assert isinstance(res, Sign)
                if res.type == SignType.Break:
                    break
                elif res.type == SignType.Continue:
                    continue
                elif res.type == SignType.Return:
                    return res

        return raw_run()


@dataclass
class Try(Node):
    token: Token = None
    body: Block = None
    catch_block: Block = None
    finally_block: Block = None

    def init(self, svc: Svc):
        self.is_init = True
        if self.body:
            self.body.init(svc)
        if self.catch_block:
            self.catch_block.init(svc)
        if self.finally_block:
            self.finally_block.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, env, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            try:
                if self.body:
                    res = self.body.run(svc, env)
                    if res is not None:
                        assert isinstance(res, Sign)
                        if res.type in [
                            SignType.Return,
                            SignType.Continue,
                            SignType.Break,
                        ]:
                            return res
            except Exception as e:
                if self.catch_block:
                    event.debug_handler(svc, env, self.catch_block.token)
                    c_res = self.catch_block.run(svc, env)
                    if c_res is not None:
                        assert isinstance(c_res, Sign)
                        if c_res.type in [
                            SignType.Return,
                            SignType.Continue,
                            SignType.Break,
                        ]:
                            return c_res
            finally:
                if self.finally_block:
                    event.debug_handler(svc, env, self.finally_block.token)
                    f_res = self.finally_block.run(svc, env)
                    if f_res is not None:
                        assert isinstance(f_res, Sign)
                        if f_res.type in [
                            SignType.Return,
                            SignType.Continue,
                            SignType.Break,
                        ]:
                            return f_res

        event.debug_handler(svc, env, self.token)
        return raw_run()


@dataclass
class For(Node):
    token: Token = None
    body: Block = None
    __arguments__: dict[str, InputParam] = None
    __returned__: list[OutputParam] = None

    def init(self, svc: Svc):
        self.__arguments__ = {}
        params = svc.params.parse_input(self.token)
        if len(params) > 0:
            for pk, pv in params.items():
                self.__arguments__[pk] = pv
        self.__returned__ = svc.params.parse_output(self.token)
        self.is_init = True
        if self.body:
            self.body.init(svc)

    def run(self, svc: Svc, env: Environment) -> Union[Sign, None]:
        @event.error_logger_handler(svc, env, self.token)
        @event.event_handler(svc)
        def raw_run():
            while not self.is_init:
                time.sleep(0.1)
                event.raw_event_handler(svc)

            project_id = self.token.value.get("__project_id__")

            arguments = {}
            if self.__arguments__:
                for k, v in self.__arguments__.items():
                    assert isinstance(v, InputParam)
                    if v.need_eval:
                        arguments[k] = expression(v.value, svc, env, self.token, project_id)
                    else:
                        arguments[k] = v.value

            if self.token.type == TokenType.ForStep.value:
                params_name = arguments.get("__params_name__", {})
                start = int(Int.__validate__(params_name.get("start", "start"), arguments.get("start", 0)))
                end = int(Int.__validate__(params_name.get("end", "end"), arguments.get("end", 0)))
                step = int(Int.__validate__(params_name.get("step", "step"), arguments.get("step", 0)))
                i = start
                while True:
                    event.debug_handler(svc, env, self.token)
                    if i >= end:
                        break

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=i,
                        ),
                    )
                    res = self.body.run(svc, env)
                    if res is None:
                        i += step
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += step
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += step
            elif self.token.type == TokenType.ForList.value:
                params_name = arguments.get("__params_name__", {})
                lists = list(RpaList.__validate__(params_name.get("list", "list"), arguments.get("list", 0)))
                i = 0
                ls = len(lists)
                while True:
                    event.debug_handler(svc, env, self.token)
                    if i >= ls:
                        break
                    v = lists[i]

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=i,
                        ),
                    )

                    t_key = self.__returned__[1].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[1].types,
                            key=t_key,
                            value=v,
                        ),
                    )
                    res = self.body.run(svc, env)
                    if res is None:
                        i += 1
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += 1
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += 1
            elif self.token.type == TokenType.ForDict.value:
                params_name = arguments.get("__params_name__", {})
                dicts = dict(RpaDict.__validate__(params_name.get("dicts", "dicts"), arguments.get("dicts", 0)))
                keys = list(dicts.keys())

                i = 0
                ls = len(keys)
                while True:
                    event.debug_handler(svc, env, self.token)
                    if i >= ls:
                        break
                    k = keys[i]
                    v = dicts[k]

                    t_key = self.__returned__[0].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[0].types,
                            key=t_key,
                            value=k,
                        ),
                    )

                    t_key = self.__returned__[1].value
                    t_biz_types = EnvBizTypes.Flow
                    if env.in_global(project_id, t_key):
                        t_biz_types = EnvBizTypes.Global
                    env.setitem(
                        project_id,
                        t_key,
                        EnvItem(
                            biz_types=t_biz_types,
                            types=self.__returned__[1].types,
                            key=t_key,
                            value=v,
                        ),
                    )

                    res = self.body.run(svc, env)
                    if res is None:
                        i += 1
                        continue

                    # 中断后续执行
                    assert isinstance(res, Sign)
                    if res.type == SignType.Break:
                        break
                    elif res.type == SignType.Continue:
                        i += 1
                        continue
                    elif res.type == SignType.Return:
                        return res

                    i += 1

        return raw_run()
