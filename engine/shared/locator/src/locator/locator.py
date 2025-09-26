"""
定位器管理模块

提供统一的元素定位管理功能，支持多种定位器类型。
"""

import json
import re
import traceback
from typing import Union

from rpaframe.logger.logger import logger

from locator import ILocator, PickerDomain


def uia_factory_callback():
    """获取UIA定位器工厂的回调函数"""
    from locator.core.uia_locator import (
        uia_factory,
    )

    return uia_factory.find


def web_factory_callback():
    """获取Web定位器工厂的回调函数"""
    from locator.core.web_locator import (
        web_factory,
    )

    return web_factory.find


def msaa_factory_callback():
    """获取MSAA定位器工厂的回调函数"""
    from locator.core.msaa_locator import (
        msaa_factory,
    )

    return msaa_factory.find


class LocatorManager:
    """管理器"""

    def __init__(self):
        self.locator_handler = {
            PickerDomain.UIA.value: [
                uia_factory_callback,
            ],
            PickerDomain.WEB.value: [web_factory_callback],
            PickerDomain.MSAA.value: [msaa_factory_callback],
        }

    @staticmethod
    def parse_element_json(element_string):
        """
        使用正则匹配出里面的img图片过滤掉

        Args:
            element_string: 元素字符串

        Returns:
            解析后的元素字典
        """
        try:
            img_match = re.search(r'(,"img".*})}$', element_string)
            if img_match:
                dictionary_string = element_string[0 : img_match.regs[1][0]] + "}"
                image_dictionary_string = img_match.group(1)[7:]
                dictionary_json = json.loads(dictionary_string)
                image_dictionary = json.loads(image_dictionary_string)
                dictionary_json["img"] = image_dictionary
                return dictionary_json
        except Exception:
            pass
        return json.loads(element_string)

    def locator(self, element: Union[str, dict], **kwargs) -> Union[list[ILocator], ILocator, None]:
        """
        定位元素

        Args:
            element: 元素信息，可以是字符串或字典
            **kwargs: 额外参数

        Returns:
            定位器对象或定位器列表
        """
        # 读取element
        if isinstance(element, str):
            element = self.parse_element_json(element)

        # 外部配置
        # timeout = kwargs.get('timeout', 10)  超时时间(秒)
        # use_cache = kwargs.get('use_cache', 10) 是否使用缓存
        # search_depth = kwargs.get('search_depth', 10) 搜索深度
        # scroll_into_view = kwargs.get('scroll_into_view', 10) 是否滚动到可视区域

        # 元素公共配置
        locator_type = element.get("type", PickerDomain.UIA.value)
        picker_type = element.get("picker_type", "")
        last_error = None
        for callback in self.locator_handler[locator_type]:
            try:
                callback_func = callback()
                if callback_func is None:
                    continue
                result = callback_func(ele=element, picker_type=picker_type, **kwargs)
                if result is not None:
                    return result
            except Exception as exception:
                last_error = exception
                logger.error(f"Strategy run error: {exception} {traceback.format_exc()}")
        if last_error:
            raise last_error
        return None


locator = LocatorManager()
