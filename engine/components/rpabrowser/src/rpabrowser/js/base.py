"""基础JS构建器模块，提供JS代码构建的抽象接口。"""

import re
from abc import ABC, abstractmethod

from rpabrowser import Element


def multi_replace(func):
    """
    替换字符串中的占位符
    """

    def wrapper(ele: Element, *args, **kwargs):
        element = ele.kwargs
        result = func(*args, **kwargs)
        # 映射属性字典，并替换
        replacements = {replace_key: element.get(replace_key, "") for replace_key in re.findall(r"\$(.*?)\$", result)}
        for replace_key, value in replacements.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
                result = result.replace("$" + replace_key + "$", value)
                continue
            if isinstance(value, int):
                value = str(value)
                result = result.replace("$" + replace_key + "$", value)
                continue
            if isinstance(value, str) and len(value) == 0:
                result = result.replace("$" + replace_key + "$", "''")
                continue
            result = result.replace("$" + replace_key + "$", "`" + value + "`")

        return result

    return wrapper


class BaseBuilder(ABC):
    """基础构建器抽象类。"""

    @staticmethod
    @abstractmethod
    def eval_js_code(is_await: bool):
        """执行代码。"""
