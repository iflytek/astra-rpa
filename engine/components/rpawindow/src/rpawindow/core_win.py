import time
from typing import Any

import win32com.client
import win32con
import win32gui
from rpaatomic.types import WinPick
from rpawindow import ControlInfo, WalkControlInfo, WindowSizeType
from rpawindow.core import IUITreeCore, IWindowsCore
from rpawindow.error import *


class WindowsCore(IWindowsCore):
    @staticmethod
    def toControl(handler: Any) -> Any:
        import uiautomation

        return uiautomation.ControlFromHandle(handler)

    @staticmethod
    def find(pick: WinPick) -> Any:
        """
        _find 查找 handle
        """
        wnd_name = pick.get("elementData", {}).get("path", [])[0].get("name", "")
        wnd_class_name = pick.get("elementData", {}).get("path", [])[0].get("cls", "")

        window_handle = win32gui.FindWindow(wnd_class_name, wnd_name)
        if not window_handle:
            window_handle = win32gui.FindWindowEx(None, None, None, wnd_name)
            if not window_handle:
                raise BaseException(WINDOW_NO_FIND, "未找到目标窗口{}".format(pick))
        return window_handle

    @staticmethod
    def info(handler: Any) -> ControlInfo:
        """
        info 查询信息
        """
        return ControlInfo(
            name=win32gui.GetWindowText(handler),
            classname=win32gui.GetWindowText(handler),
            position=win32gui.GetWindowRect(handler),
            handler=handler,
        )

    @staticmethod
    def top(handler: Any):
        """
        top 置顶
        """
        if win32gui.IsIconic(handler):
            win32gui.ShowWindow(handler, win32con.SW_NORMAL)
        else:
            # 结合键盘事件
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys("%")
            win32gui.SetForegroundWindow(handler)

    @staticmethod
    def close(handler: Any):
        """
        close 关闭
        """
        win32gui.SendMessage(handler, win32con.WM_CLOSE, None, None)

    @staticmethod
    def size(
        handler: Any,
        size_type: WindowSizeType = WindowSizeType.MAX,
        width: int = 0,
        height: int = 0,
    ):
        """
        size 设置尺寸
        """
        if size_type == WindowSizeType.CUSTOM:
            win32gui.ShowWindow(handler, win32con.SW_RESTORE)

            rect = win32gui.GetWindowRect(handler)
            win32gui.SetWindowPos(
                handler,
                win32con.HWND_NOTOPMOST,
                rect[0],
                rect[1],
                width,
                height,
                win32con.SWP_SHOWWINDOW,
            )
        elif size_type == WindowSizeType.MAX:
            win32gui.ShowWindow(handler, win32con.SW_MAXIMIZE)
            # 兜底
            rect = win32gui.GetWindowRect(handler)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            win32gui.SetWindowPos(
                handler,
                win32con.HWND_NOTOPMOST,
                x,
                y,
                w,
                h,
                win32con.SWP_SHOWWINDOW,
            )
        elif size_type == WindowSizeType.MIN:
            win32gui.ShowWindow(handler, win32con.SW_MINIMIZE)


class UITreeCore(IUITreeCore):
    @staticmethod
    def GetRootControl() -> Any:
        import uiautomation

        return uiautomation.GetRootControl()

    @staticmethod
    def WalkControl(control: Any, includeTop: bool = False, maxDepth: int = 0xFFFFFFFF):
        """
        WalkControl Control遍历
        """
        import uiautomation

        for control, depth in uiautomation.WalkControl(control, includeTop=includeTop, maxDepth=maxDepth):
            yield WalkControlInfo(
                name=control.Name,
                classname=control.ClassName,
                position=control.BoundingRectangle,
                control_type=control.ControlType,
                control_type_name=control.LocalizedControlType,
                control=control,
                depth=depth,
            )

    @staticmethod
    def toHandler(control) -> Any:
        return control.NativeWindowHandle

    @staticmethod
    def setAction(control) -> bool:
        return control.SetActive()
