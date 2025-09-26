from typing import Any, Optional, Union

import requests
import uiautomation as auto
from rpaframe.logger.logger import logger

from locator import LIKE_CHROME_BROWSER_TYPES, BrowserType, ILocator, Rect
from locator.utils.window import top_browser


class WEBLocator(ILocator):
    def __init__(self, rect=None, rects=None):
        self.__rect = rect
        self.__rects = rects

    def rect(self) -> Optional[Rect]:
        if self.__rects is not None and len(self.__rects) > 0:
            return self.__rects
        return self.__rect

    def control(self) -> Any:
        return None


class WebFactory:
    """Web工厂"""

    @classmethod
    def find(cls, element: dict, **kwargs) -> Union[WEBLocator, None]:
        if element.get("app", "") not in LIKE_CHROME_BROWSER_TYPES:
            # 直接结束
            return None

        # 获取外部配置
        scroll_into_view = kwargs.get("scroll_into_view", True)

        menu_height, menu_left = cls.__get_web_top__(element)

        # 通过插件获取元素位置信息
        rect_result = cls.__get_rect_from_browser_plugin__(element, scroll_into_view=scroll_into_view)
        if not rect_result:
            return None

        rect = Rect(
            int(rect_result[0]["x"] + menu_left),
            int(rect_result[0]["y"] + menu_height),
            int(rect_result[0]["right"] + menu_left),
            int(rect_result[0]["bottom"] + menu_height),
        )
        rects = []
        if len(rect_result) > 1:
            for single_rect in rect_result:
                rects.append(
                    Rect(
                        int(single_rect["x"] + menu_left),
                        int(single_rect["y"] + menu_height),
                        int(single_rect["right"] + menu_left),
                        int(single_rect["bottom"] + menu_height),
                    )
                )
        return WEBLocator(rect=rect, rects=rects)

    @classmethod
    def __get_rect_from_browser_plugin__(cls, element: dict, scroll_into_view=True):
        """通过浏览器插件获取rect"""
        url = "http://127.0.0.1:9082/browser/transition"
        if scroll_into_view:
            data = {
                "browser_type": element.get("app", ""),
                "data": element.get("path", {}),
                "key": "scrollIntoView",
            }
            _ = requests.post(url, json=data)

        data = {
            "browser_type": element.get("app", ""),
            "data": element.get("path", {}),
            "key": "checkElement",
        }
        response = requests.post(url, json=data)
        if response.json().get("data", {}).get("code", "") == "0000":
            web_info = response.json()["data"]["data"]
            return web_info["rect"]
        else:
            raise Exception(response.json()["data"]["msg"])

    @classmethod
    def __get_web_top__(cls, element: dict) -> tuple[int, int]:
        """浏览器右上角位置"""
        root_control = auto.GetRootControl()
        app_name = element.get("app", "")
        uia_path_list = element.get("uiapath", "")
        target_control = None if uia_path_list == "" else uia_path_list[0]
        logger.info(f"weblocator-__get_web_top__ 携带的uia头信息 {target_control}")

        control_target = None
        for control, _ in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if app_name == BrowserType.CHROME.value:
                if (control.Name == "Chrome Legacy Window") or (
                    ("- Google Chrome" in control.Name) or ("- Chrome" in control.Name)
                ):
                    control_target = control
                    break
            if app_name == BrowserType.EDGE.value:
                if "- Microsoft​ Edge" in control.Name:
                    control_target = control
                    break
            if app_name == BrowserType.CHROME_360_SE.value:
                if "360安全浏览器" in control.Name:
                    control_target = control
                    break
            if app_name == BrowserType.CHROME_360_X.value:
                if "360极速浏览器X" in control.Name:
                    control_target = control
                    break
            if app_name == BrowserType.FIREFOX.value:
                if "Mozilla Firefox" in control.Name:
                    control_target = control
                    break
            if app_name == BrowserType.CHROMIUM.value:
                if (control.Name == "Chrome Legacy Window") or ("- Chromium" in control.Name):
                    control_target = control
                    break
        if control_target is None:
            return 0, 0

        # 置顶
        # control_target.SetActive()
        handle = control_target.NativeWindowHandle
        top_browser(handle, control_target)
        if app_name == BrowserType.FIREFOX.value:
            for child, _ in auto.WalkControl(control_target, includeTop=True, maxDepth=100):
                if child.AutomationId == "tabbrowser-tabpanels":
                    bounding_rect = child.BoundingRectangle
                    top = bounding_rect.top
                    left = bounding_rect.left
                    return top, left
        else:
            for child, _ in auto.WalkControl(control_target, includeTop=True, maxDepth=100):
                if child.ClassName == "Chrome_RenderWidgetHostHWND":
                    bounding_rect = child.BoundingRectangle
                    top = bounding_rect.top
                    left = bounding_rect.left
                    return top, left
        return 0, 0


web_factory = WebFactory()
