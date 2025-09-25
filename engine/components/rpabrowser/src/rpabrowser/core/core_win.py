import os
import time
from typing import Any

import pyautogui
import pyperclip
import win32con
import win32gui
from rpaframe.logger.logger import logger
from rpasoftware.software import Software
from rpawindow import WalkControlInfo
from rpawindow.uitree import UITreeCore

from rpabrowser import (
    BROWSER_REGISTER_NAME,
    BROWSER_UIA_POINT_CLASS,
    BROWSER_UIA_WINDOW_CLASS,
    CHROME_LIKE_BROWSERS,
)
from rpabrowser import CommonForBrowserType as BrowserType
from rpabrowser.core.core import IBrowserCore
from rpabrowser.error import *


class BrowserCore(IBrowserCore):
    @staticmethod
    def get_browser_path(browser_type: BrowserType) -> str:
        """获取浏览器绝对地址"""

        if browser_type.value == "chromium":
            return os.path.join(os.getcwd(), "rpachrome", "chromium.exe")
        app_name = BROWSER_REGISTER_NAME.get(browser_type.value, "")
        if not app_name:
            return ""
        return Software.get_app_path(app_name)

    @staticmethod
    def check_microsoft_edge_in_last_part(text, target="edge"):
        """
        用'-'分割字符串，判断目标字符串是否在最后一个分割部分中

        参数:
            text (str): 要处理的原始字符串
            target (str): 要查找的目标字符串，默认为"microsoft edge"

        返回:
            bool: 如果目标字符串在最后一个分割部分中返回True，否则返回False
        """
        # 用'-'分割字符串
        parts = text.split("-")

        # 获取最后一个分割部分并去除首尾空格
        last_part = parts[-1].strip()
        logger.info(f"check_microsoft_edge_in_last_part   {last_part.lower()}")

        # 判断目标字符串是否在最后一个部分中（不区分大小写）
        return target.lower() in last_part.lower()

    @staticmethod
    def get_browser_control(browser_type: BrowserType) -> Any:
        """获取浏览器的控制器"""

        class_name = BROWSER_UIA_WINDOW_CLASS.get(browser_type.value, "")
        if not class_name:
            return None

        # 遍历uitree
        root_control = UITreeCore.GetRootControl()
        control = None
        for walkControlInfo in UITreeCore.WalkControl(root_control, True, 1):
            assert isinstance(walkControlInfo, WalkControlInfo)
            if walkControlInfo.classname == class_name:
                if browser_type == browser_type.BTChrome:
                    if (
                        (walkControlInfo.name == "Chrome Legacy Window")
                        or ("- Google Chrome" in walkControlInfo.name)
                        or (" - Chrome" in walkControlInfo.name)
                    ):
                        control = walkControlInfo.control
                        break
                elif browser_type == browser_type.BT360X:
                    if "- 360极速浏览器X" in walkControlInfo.name:
                        control = walkControlInfo.control
                        break
                elif browser_type == browser_type.BT360SE:
                    if "- 360安全浏览器" in walkControlInfo.name:
                        control = walkControlInfo.control
                        break
                elif browser_type == browser_type.BTFirefox:
                    if "Firefox" in walkControlInfo.name:
                        control = walkControlInfo.control
                        break
                elif browser_type == browser_type.BTEdge:
                    if BrowserCore.check_microsoft_edge_in_last_part(walkControlInfo.name):
                        control = walkControlInfo.control
                        break
                elif walkControlInfo.name.lower().endswith(browser_type.value.lower()):
                    control = walkControlInfo.control
                    break

        # 激活
        if control:
            UITreeCore.setAction(control)

        return control

    @staticmethod
    def get_browser_handler(browser_type: BrowserType) -> Any:
        control = BrowserCore.get_browser_control(browser_type)
        if not control:
            return None
        return UITreeCore.toHandler(control)

    @staticmethod
    def get_browser_point(browser_type: BrowserType) -> Any:
        """获取浏览器坐标"""

        class_name = BROWSER_UIA_POINT_CLASS.get(browser_type.value, "")
        if not class_name:
            return None

        base_ctrl = BrowserCore.get_browser_control(browser_type)
        if not base_ctrl:
            return None

        for walkControlInfo in UITreeCore.WalkControl(base_ctrl, True, 12):
            assert isinstance(walkControlInfo, WalkControlInfo)
            if walkControlInfo.classname == class_name:
                bounding_rect = walkControlInfo.position
                top = bounding_rect.top
                left = bounding_rect.left
                return top, left

    @staticmethod
    def download_window_operate(*args, **kwargs) -> Any:
        """获取浏览器下载文件另存为窗口"""

        file_name = kwargs.get("file_name")
        browser_type = kwargs.get("browser_type")
        is_wait = kwargs.get("is_wait")
        time_out = kwargs.get("time_out")

        def get_text_from_edit(hwnd):
            # 获取edit控件的文本长度
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) * 2 + 2
            # 创建缓冲区并发送WM_GETTEXT消息获取文本
            buffer = win32gui.PyMakeBuffer(length)
            win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length, buffer)
            address, result_length = win32gui.PyGetBufferAddressAndLen(buffer)
            text = win32gui.PyGetString(address, result_length // 2 - 1)
            return text

        # 判断是否弹出下载窗口
        dialog = win32gui.FindWindow("#32770", "另存为")  # 一级窗口
        start_time = time.time()
        while time.time() - start_time < 10:
            dialog = win32gui.FindWindow("#32770", "另存为")  # 一级窗口
            if dialog == 0:
                time.sleep(0.1)
            else:
                time.sleep(3)
                break
        if dialog == 0:
            raise BaseException(DOWNLOAD_WINDOW_NO_FIND, "未弹出下载窗口")

        # 查找到edit， button
        button = win32gui.FindWindowEx(dialog, 0, "Button", "保存(S)")

        a1 = win32gui.FindWindowEx(dialog, None, "DUIViewWndClassName", None)
        a2 = win32gui.FindWindowEx(a1, None, "DirectUIHWND", None)
        a3 = win32gui.FindWindowEx(a2, None, "FloatNotifySink", None)
        a4 = win32gui.FindWindowEx(a3, None, "ComboBox", None)
        edit = win32gui.FindWindowEx(a4, None, "Edit", None)
        origin_name = get_text_from_edit(edit)
        if origin_name.find(".") != -1:
            name = origin_name.split(".")[0]
            suffix = origin_name.rsplit(".", 1)[-1]
            if not suffix.isalpha():
                name = origin_name
                suffix = ""
        else:
            name = origin_name
            suffix = ""

        # 往编辑当中，输入文件路径
        if kwargs.get("custom_flag"):
            name = file_name

        if suffix:
            dest_path = os.path.join(kwargs.get("save_path"), name + "." + suffix)
        else:
            dest_path = os.path.join(kwargs.get("save_path"), name)
        pyperclip.copy(dest_path)

        # 等待一段时间，以确保字符串已复制到剪贴板
        time.sleep(0.5)

        # 模拟 Ctrl+V 粘贴操作
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击打开按钮

        if is_wait:
            if not (time_out == 0 or time_out == ""):
                try:
                    wait_time_download = int(time_out)
                except Exception:
                    wait_time_download = 60
                while wait_time_download > 0:
                    wait_time_download = wait_time_download - 3
                    if os.path.exists(dest_path):
                        break
                    time.sleep(3)
                if wait_time_download <= 0 and not os.path.exists(dest_path):
                    raise Exception("等待下载完成超时")
        return dest_path

    @staticmethod
    def upload_window_operate(*args, **kwargs) -> Any:
        """获取浏览器上传文件窗口操作"""

        upload_path = kwargs.get("upload_path")
        browser_type = kwargs.get("browser_type")
        if browser_type in CHROME_LIKE_BROWSERS:
            # 判断是否弹出上传窗口
            dialog = win32gui.FindWindow("#32770", "打开")
            start_time = time.time()
            while time.time() - start_time < 10:
                dialog = win32gui.FindWindow("#32770", "打开")  # 一级窗口
                if dialog == 0:
                    time.sleep(0.1)
                else:
                    time.sleep(3)
                    break
            if dialog == 0:
                raise BaseException(UPLOAD_WINDOW_NO_FIND, "未弹出上传窗口")
        else:
            raise NotImplementedError()

        button = win32gui.FindWindowEx(dialog, 0, "Button", "打开(O)")  # 四级

        a1 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)  # 二级
        a2 = win32gui.FindWindowEx(a1, 0, "ComboBox", None)  # 三级
        edit = win32gui.FindWindowEx(a2, 0, "Edit", None)  # 四级

        # 往编辑当中，输入文件路径。
        dest_path = ""
        if upload_path.find("|") != -1:
            upload_path = upload_path.split("|")
        if type(upload_path) == list:
            for file in upload_path:
                dest_path += f'"{file.strip()}" '
        else:
            dest_path = upload_path

        win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, dest_path)  # 发送文件路径
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击打开按钮
