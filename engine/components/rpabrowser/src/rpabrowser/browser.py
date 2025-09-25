"""浏览器操作模块，提供浏览器对象的基本操作功能。"""

from typing import Any
from urllib.parse import urljoin

import requests
from rpaatomic.atomic import atomicMg
from rpaatomic.error import PARAM_VERIFY_ERROR_FORMAT
from rpaatomic.types import typesMg

from rpabrowser import CHROME_LIKE_BROWSERS, CommonForBrowserType
from rpabrowser.error import (
    BROWSER_EXTENSION_ERROR_FORMAT,
    BROWSER_EXTENSION_INSTALL_ERROR,
    BaseException,
    WEB_EXEC_ElE_ERROR,
    WEB_GET_ElE_ERROR,
)


class Browser:
    """浏览器操作类，提供浏览器的基本操作方法。"""

    def __init__(self):
        self.browser_type: CommonForBrowserType = CommonForBrowserType.BTChrome
        self.browser_abs_path: str = ""
        self.browser_control = None

    @typesMg.shortcut(group_key="Browser", res_type="Str")
    def get_url(self) -> str:
        """获取当前网页URL。"""
        if self.browser_type in CHROME_LIKE_BROWSERS:
            data = self.send_browser_extension(browser_type=self.browser_type.value, key="getUrl", data={"": ""})
        else:
            raise NotImplementedError()
        return data

    @typesMg.shortcut(group_key="Browser", res_type="Str")
    def get_title(self) -> str:
        """获取当前网页标题。"""
        if self.browser_type in CHROME_LIKE_BROWSERS:
            data = self.send_browser_extension(browser_type=self.browser_type.value, key="getTitle", data={"": ""})
        else:
            raise NotImplementedError()
        return data

    @typesMg.shortcut(group_key="Browser", res_type="Int")
    def get_tabid(self) -> int:
        """获取当前标签ID。"""
        if self.browser_type in CHROME_LIKE_BROWSERS:
            data = self.send_browser_extension(browser_type=self.browser_type.value, key="getTabId", data={"": ""})
        else:
            raise NotImplementedError()
        return data

    @classmethod
    def __validate__(cls, name: str, value):
        """验证浏览器对象。"""
        if isinstance(value, Browser):
            return value
        raise BaseException(PARAM_VERIFY_ERROR_FORMAT.format(name, value), f"{name}参数验证失败{value}")

    @staticmethod
    def send_browser_rpc(req: dict, timeout: float = None) -> Any:
        """发送浏览器RPC请求。"""
        gateway_port = atomicMg.cfg().get("GATEWAY_PORT") or "8003"
        url = f"http://127.0.0.1:{gateway_port}"
        return requests.post(
            urljoin(
                url,
                "browser_connector",
            )
            + "/browser/transition",
            json=req,
            timeout=timeout,
        )

    def send_browser_extension(
        self,
        browser_type: str,
        data: Any,
        key: str,
        data_path: str = "",
        timeout: float = None,
    ):
        """发送浏览器扩展请求。"""
        res = self.send_browser_rpc(
            {
                "browser_type": browser_type,
                "data": data,
                "key": key,
                "data_path": data_path,
            },
            timeout,
        )

        if res.status_code != 200:
            raise BaseException(BROWSER_EXTENSION_INSTALL_ERROR, "浏览器插件通信出错，请重试")
        data = res.json()
        if not data.get("data"):
            return "插件无返回消息"
        if data.get("data").get("code") == "5001":
            raise BaseException(
                BROWSER_EXTENSION_ERROR_FORMAT.format(data.get("data").get("msg")),
                data.get("data").get("msg"),
            )
        if data.get("data").get("code") == "5002":
            raise BaseException(WEB_GET_ElE_ERROR.format(data.get("data").get("msg")), "网页元素未找到")
        if data.get("data").get("code") == "5003":
            raise BaseException(
                WEB_EXEC_ElE_ERROR.format(data.get("data").get("msg")),
                data.get("data").get("msg"),
            )
        if data.get("data").get("code") == "5004":
            raise BaseException(
                BROWSER_EXTENSION_ERROR_FORMAT.format(data.get("data").get("msg")),
                data.get("data").get("msg"),
            )
        return data.get("data").get("data")
