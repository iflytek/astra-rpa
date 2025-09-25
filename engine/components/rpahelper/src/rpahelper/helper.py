import copy
import json
import os

from rpa_param_utils import param_utils
from rpaatomic.report import IReport, report
from rpahelper.error import *
from rpahelper.utils import HttpStorage, Storage

try:
    logger: IReport = GLOBAL_RPA_REPORT
except Exception as e:
    logger: IReport = report


def print(*args, sep=" ", end="\n"):
    output = sep.join(str(arg) for arg in args)
    output += end
    logger.info(output)


class Helper:
    """脚本帮助类"""

    def __init__(self, **kwargs):
        self.__map__ = kwargs
        self.__GATEWAY_PORT__ = os.environ.get("GATEWAY_PORT", "8003")
        self.__PROJECT_ID__ = os.environ.get("PROJECT_ID", "")
        self.__storage__: Storage = HttpStorage(self.__GATEWAY_PORT__)
        self.__env__ = None
        self.__id2name__ = None
        if kwargs.get("project_id"):
            self.__PROJECT_ID__ = kwargs["project_id"]

    def params(self) -> dict:
        """参数获取"""
        return {k: v for k, v in self.__map__.items() if not k.startswith("__")}

    def logger(self) -> IReport:
        """日志打印"""
        return logger

    def element(self, element_id: str) -> dict:
        """获取元素，并解析"""

        if self.__env__ is None:
            global_ls = self.__storage__.global_list(self.__PROJECT_ID__)
            self.__env__, self.__id2name__ = param_utils.global_to_dict(global_ls)
        if self.__env__:
            for k, v in self.__env__.items():
                if k in self.__map__:
                    v = self.__map__[k]
        res = copy.deepcopy(self.__storage__.element_detail(self.__PROJECT_ID__, element_id))
        try:
            element_data = json.loads(res.get("elementData"))
            res["elementData"] = param_utils.special_eval_element(element_data, self.__env__, self.__id2name__)
            return res
        except Exception as e:
            raise BaseException(SPECIAL_PARSE_FORMAL, "特殊元素处理异常 {}".format(e)) from e
