from typing import Any

from rpaatomic.error import PARAM_VERIFY_ERROR_FORMAT

from rpadocx.error import *


class DocxObj:
    def __init__(self, obj: Any):
        self.obj = obj

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, DocxObj):
            return value
        raise BaseException(
            PARAM_VERIFY_ERROR_FORMAT.format(name, value),
            "{}参数验证失败{}".format(name, value),
        )
