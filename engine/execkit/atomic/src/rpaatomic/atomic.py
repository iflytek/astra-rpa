import inspect
import json
import os
import re
import time
import traceback
from enum import Enum
from functools import wraps
from typing import Any

from rpaatomic import (
    AtomicFormType,
    AtomicFormTypeMeta,
    AtomicMeta,
    AtomicOption,
    AtomicParamMeta,
    IgnoreException,
    ReportCode,
    ReportCodeStatus,
    ReportType,
    utils,
)
from rpaatomic.config import config
from rpaatomic.error import *
from rpaatomic.report import report
from rpaatomic.types import Bool, Date, Pick
from rpaatomic.utils import InspectType


class AtomicManager:
    """原子能力，运行"""

    def __init__(self):
        self.atomic_dict = {}
        self.model_cache = {}
        self.model_cache_max_size = 1000

    @staticmethod
    def cfg() -> dict:
        return {"GATEWAY_PORT": os.environ.get("GATEWAY_PORT", "")}

    def atomic(self, group_key="", **kwargs):
        def real_atomic(func):
            t = AtomicMeta(**kwargs).init()
            if not t.key:
                t.key = "{}.{}".format(group_key, func.__name__)
            self.atomic_dict[t.key] = t

            @wraps(func)
            def wrapper(*args, **war_kwargs):
                if len(args) > 1:
                    raise BaseException(PARAM_ARGS_NO_SUPPORT_FORMAT.format(args), "参数不支持args")
                return self.atomic_run(func, t.key, *args, **war_kwargs)

            wrapper.__tag_key__ = "atomic"  # 标记
            return wrapper

        return real_atomic

    @staticmethod
    def param(key: str, **kwargs):
        """
        convert 废弃
        """
        return AtomicParamMeta(**kwargs, key=key)

    def atomic_run(self, func: Any, key: str, *args, **kwargs):
        base_kwargs = {k: v for k, v in kwargs.items() if v is not None and not k.startswith("__")}
        advance_kwargs = {k: v for k, v in kwargs.items() if v is not None and k.startswith("__")}

        line = int(kwargs.get("__line__", 0))
        if not line:
            # 不是用原子能力调用，而是直接调用，不做处理
            return func(*args, **base_kwargs, **advance_kwargs)

        line_id = kwargs.get("__line_id__", "")
        res_print = kwargs.get("__res_print__", False)
        delay_before = float(kwargs.get("__delay_before__", 0))
        delay_after = float(kwargs.get("__delay_after__", 0))
        skip_err = kwargs.get("__skip_err__", "exit")
        process_name = kwargs.get("__process_name__", "")
        process_id = kwargs.get("__process_id__", "")
        atomic_name = kwargs.get("__atomic_name__", "")
        params_name_dict = kwargs.get("__params_name__", {})
        retry_time = kwargs.get("__retry_time__", 0)
        retry_interval = float(kwargs.get("__retry_interval__", 0))

        report.info(
            ReportCode(
                log_type=ReportType.Code,
                process=process_name,
                process_id=process_id,
                atomic=atomic_name,
                key=key,
                line=line,
                line_id=line_id,
                status=ReportCodeStatus.START,
                msg_str=ReportStartMsgFormat.format(process_name, line, atomic_name),
            )
        )

        # 基础参数验证+转换
        if not self.atomic_dict[key].__end__:
            self._update_atomic_param(key, func)

        if key not in self.model_cache:
            if len(self.model_cache) > self.model_cache_max_size:
                # gc回收
                self.model_cache = {}
            model = utils.ParamModel(self.atomic_dict[key].inputList, params_name_dict, key)
            self.model_cache[key] = model
        else:
            model = self.model_cache[key]

        # 2. 高级参数处理
        has_result = True
        if self.atomic_dict[key].outputList is None or len(self.atomic_dict[key].outputList) == 0:
            has_result = False

        if delay_before > 0:
            time.sleep(delay_before)

        while True:
            try:
                # 验证只验证 __convert__ 为true的参数，不适用于对象验证
                model_res = model(**base_kwargs)
                for name, value in model_res.items():
                    base_kwargs[name] = value

                # 只有**kwargs的原子能力才接受高级参数
                if not self.atomic_dict[key].__has_kwargs__:
                    advance_kwargs = {}
                res = func(*args, **base_kwargs, **advance_kwargs)
                if res_print and has_result:
                    report.info(
                        ReportCode(
                            log_type=ReportType.Code,
                            process=process_name,
                            process_id=process_id,
                            atomic=atomic_name,
                            line=line,
                            line_id=line_id,
                            status=ReportCodeStatus.RES,
                            msg_str=str(res),
                        )
                    )
                break
            except Exception as e:
                res = None
                if isinstance(e, BaseException):
                    error_str = e.code.message
                else:
                    error_str = str(e)
                if skip_err == "skip":
                    report.warning(
                        ReportCode(
                            log_type=ReportType.Code,
                            process=process_name,
                            process_id=process_id,
                            atomic=atomic_name,
                            line=line,
                            line_id=line_id,
                            status=ReportCodeStatus.SKIP,
                            msg_str="{} {}".format(ReportCodeSkip, error_str),
                            error_traceback=traceback.format_exc(),
                        )
                    )
                    break
                elif skip_err == "retry":
                    retry_time -= 1
                    if retry_time < 0:
                        report.error(
                            ReportCode(
                                log_type=ReportType.Code,
                                process=process_name,
                                process_id=process_id,
                                atomic=atomic_name,
                                line=line,
                                line_id=line_id,
                                status=ReportCodeStatus.ERROR,
                                msg_str="{} {}".format(ReportCodeError, error_str),
                                error_traceback=traceback.format_exc(),
                            )
                        )
                        raise IgnoreException() from e
                    report.warning(
                        ReportCode(
                            log_type=ReportType.Code,
                            process=process_name,
                            process_id=process_id,
                            atomic=atomic_name,
                            line=line,
                            line_id=line_id,
                            status=ReportCodeStatus.SKIP,
                            msg_str="{} {}".format(ReportCodeRetry, error_str),
                            error_traceback=traceback.format_exc(),
                        )
                    )
                    if retry_interval > 0:
                        time.sleep(retry_interval)
                else:
                    report.error(
                        ReportCode(
                            log_type=ReportType.Code,
                            process=process_name,
                            process_id=process_id,
                            atomic=atomic_name,
                            line=line,
                            line_id=line_id,
                            status=ReportCodeStatus.ERROR,
                            msg_str="{} {}".format(ReportCodeError, error_str),
                            error_traceback=traceback.format_exc(),
                        )
                    )
                    raise IgnoreException() from e

        if delay_after > 0:
            time.sleep(delay_after)
        return res

    @staticmethod
    def _inspect_param(inspect_item, user_item):
        options = None
        name = inspect_item.name
        default = inspect_item.default if inspect_item.default != inspect.Parameter.empty else None
        formType = AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value)
        __annotation__ = inspect_item.annotation
        noInput = None

        # 反射
        types, kind = utils.gen_type(__annotation__)
        if kind == InspectType.PYTHONBASE:
            if __annotation__ is bool:
                if options is None:
                    options = []
                options.append(AtomicOption("是", True))
                options.append(AtomicOption("否", False))
                formType = AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={})
        elif kind == InspectType.ENUM:
            default = default.value
            for e in __annotation__:
                if options is None:
                    options = []
                options.append(AtomicOption(e.value, e.value))
            if len(options) <= 3:
                formType = AtomicFormTypeMeta(type=AtomicFormType.RADIO.value)
            else:
                formType = AtomicFormTypeMeta(type=AtomicFormType.SELECT.value)
        elif kind == InspectType.RPABASE:
            if issubclass(__annotation__, Bool):
                formType = AtomicFormTypeMeta(type=AtomicFormType.SWITCH.value, params={})
            if issubclass(__annotation__, Pick):
                formType = AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": types})
                noInput = True
            if issubclass(__annotation__, Date):
                formType = AtomicFormTypeMeta(type=AtomicFormType.DEFAULTDATEPICKER.value, params={})

        # 更新值
        return {
            "name": name,
            "types": types,
            "__annotation__": __annotation__,
            "formType": formType,
            "default": default,
            "options": options,
            "noInput": noInput,
            "required": True,
        }

    def _update_atomic_param(self, key, func):
        if self.atomic_dict[key].__end__:
            return

        sig = inspect.signature(func)

        # 处理输入
        inputList = []
        __has_kwargs__ = None
        for k, v in sig.parameters.items():
            if k in ("self", "cls", "args"):
                continue
            if k == "kwargs":
                __has_kwargs__ = True
                continue
            has = False
            if self.atomic_dict[key].inputList:
                for k1, v1 in enumerate(self.atomic_dict[key].inputList):
                    assert isinstance(v1, AtomicParamMeta)
                    if v1.key == k:
                        v1.update(**self._inspect_param(v, v1))
                        inputList.append(v1)
                        has = True
                        break
            if not has:
                v1 = AtomicParamMeta(key=k)
                v1.update(**self._inspect_param(v, v1))
                inputList.append(v1)
        self.atomic_dict[key].inputList = inputList

        # 处理输出
        outputList = []
        if self.atomic_dict[key].outputList:
            for k2, v2 in enumerate(self.atomic_dict[key].outputList):
                assert isinstance(v2, AtomicParamMeta)
                if not v2.types:
                    raise BaseException(
                        REQUIRED_PARAM_MISSING.format("types"),
                        "缺少必填参数, 返回值的types必须传值",
                    )
                v2.update(
                    formType=AtomicFormTypeMeta(type=AtomicFormType.RESULT.value),
                    required=None,
                )
                outputList.append(v2)
        self.atomic_dict[key].outputList = outputList

        self.atomic_dict[key].__has_kwargs__ = __has_kwargs__
        self.atomic_dict[key].__end__ = True

    def register(self, cls: Any, group_key: str = "", version: str = "1"):
        # group_key
        if not group_key:
            group_key = cls.__name__

        # src
        src = "{}.{}()".format(cls.__module__, cls.__name__)

        # 反射类
        for name, member in inspect.getmembers(cls):
            # 过滤原子能力方法
            if not (inspect.isfunction(member) or inspect.ismethod(member)):
                continue
            try:
                if member.__tag_key__ != "atomic":
                    continue
            except Exception as e:
                continue

            key = "{}.{}".format(group_key, member.__name__)

            # 处理公共
            self.atomic_dict[key].version = version
            self.atomic_dict[key].src = "{}.{}".format(src, member.__name__)

            # 反射并更新方法
            self._update_atomic_param(key, member)

    def json(self):
        temp_atomic_dict = {}
        for k, v in self.atomic_dict.items():
            if not v.src:
                continue
            if not v.title:
                v.title = config.get("atomic", v.key, "title")
            if not v.comment:
                v.comment = config.get("atomic", v.key, "comment")
            if not v.icon:
                v.icon = config.get("atomic", v.key, "icon")
            if not v.helpManual:
                v.helpManual = config.get("atomic", v.key, "helpManual")

            # intputList
            inputList = config.get("atomic", v.key, "inputList")
            if not inputList:
                inputList = []
            inputMap = {}
            for i in inputList:
                inputMap[i.get("key", None)] = i

            for a in v.inputList:
                if not a.title and a.key in inputMap:
                    a.title = inputMap[a.key].get("title", None)
                if not a.tip and a.key in inputMap:
                    a.tip = inputMap[a.key].get("tip", None)

                options = config.get("options", a.types)
                if a.options and options:
                    optionsMap = {}
                    for op in options:
                        optionsMap[op.get("value", None)] = op.get("label", None)
                    for p in a.options:
                        if p.value in optionsMap:
                            p.label = optionsMap[p.value]

            # outputList
            outputList = config.get("atomic", v.key, "outputList")
            if not outputList:
                outputList = []
            outputMap = {}
            for i in outputList:
                outputMap[i.get("key", None)] = i

            if v.outputList:
                for o in v.outputList:
                    if not o.title and o.key in outputMap:
                        o.title = outputMap[o.key].get("title", None)
                    if not o.tip and o.key in outputMap:
                        o.tip = outputMap[o.key].get("tip", None)

            # 6.1 检测comment
            if v.comment:
                matches = re.findall(r"@\{(.*?)\}", v.comment)
                result = []
                if matches:
                    for item in matches:
                        # 分割 '||' 的情况
                        if "||" in item:
                            parts = item.split("||")
                            result.extend(parts)
                        # 分割 ':' 的情况
                        elif ":" in item:
                            parts = item.split(":")
                            result.append(parts[0])
                        # 普通元素
                        else:
                            result.append(item)
                for res in result:
                    if (res in outputMap) or (res in inputMap):
                        continue
                    else:
                        raise BaseException(
                            REQUIRED_PARAM_MISSING.format(res),
                            "comment存在未定义的数据:{}".format(res),
                        )

            # 6.2 回写
            temp_atomic_dict[k] = v

        def _json(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, "tojson"):
                return obj.tojson(True)
            else:
                return obj.__dict__

        return json.dumps(temp_atomic_dict, ensure_ascii=False, default=_json)

    def meta(self):
        data = self.json()
        file = "meta.json"
        with open(file, "w", encoding="utf-8") as file:
            file.write(data)
        return file


atomicMg = AtomicManager()
