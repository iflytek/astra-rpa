import subprocess
from typing import Any

from dogtail.tree import *

from rpabrowser import (
    BROWSER_DOGTAIL_POINT_CLASS,
    BROWSER_DOGTAIL_WINDOW_CLASS,
    BROWSER_XDOT_WINDOW_HANDLER_NAME,
)
from rpabrowser import CommonForBrowserType as BrowserType
from rpabrowser.core.core import IBrowserCore
from rpabrowser.error import *


class BrowserCore(IBrowserCore):
    @staticmethod
    def get_browser_path(browser_type: BrowserType) -> str:
        raise BaseException(LINUX_MUST_BROWSER_PATH_ERROR, "Linux必须手动填入浏览器地址")

    @staticmethod
    def get_browser_handler(browser_type: BrowserType) -> Any:
        class_names = BROWSER_XDOT_WINDOW_HANDLER_NAME[browser_type.value]
        try:
            output = subprocess.check_output(["xdotool", "search", "--name", str(class_names)])
        except Exception:
            return None
        # 获取最后一个
        window_id = 0
        for line in output.splitlines():
            window_id = line.decode("utf-8")
        if window_id:
            return int(window_id)

    @staticmethod
    def get_ele_by_name(name_list: list) -> Any:
        for ind, app in enumerate(root.children):
            if app.name in name_list:
                return app, app.name
        return None

    @staticmethod
    def get_browser_point(browser_type: BrowserType) -> Any:
        control, name = BrowserCore.get_ele_by_name(BROWSER_DOGTAIL_WINDOW_CLASS[browser_type.value])
        if not control:
            return 0, 0

        c0 = control.getChildAtIndex(0)
        c0.getRelationSet()
        document = c0.child(roleName=BROWSER_DOGTAIL_POINT_CLASS[browser_type.value])
        return document.extents[0], document.extents[1]

    @staticmethod
    def download_window_operate(*args, **kwargs) -> Any:
        raise NotImplementedError

    @staticmethod
    def upload_window_operate(*args, **kwargs) -> Any:
        raise NotImplementedError
