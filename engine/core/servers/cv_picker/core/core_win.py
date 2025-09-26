import ctypes

import pyautogui
import win32gui
from cv_picker.core.core import IPickCore, IRectHandler


class RectHandler(IRectHandler):
    @staticmethod
    def get_foreground_window_rect():
        # 获取当前置顶窗口的句柄
        hwnd = win32gui.GetForegroundWindow()
        # 获取窗口标题
        title = win32gui.GetWindowText(hwnd)
        # 获取窗口的矩形区域
        rect = win32gui.GetWindowRect(hwnd)
        # if rect.x < 0: rect.x = 0
        # if rect.y < 0: rect.y = 0
        return hwnd, title, rect

    # @staticmethod
    # def find_window_by_title(window_title):
    #     hwnds = []
    #
    #     def callback(hwnd, _):
    #         try:
    #             title = win32gui.GetWindowText(hwnd)
    #             if window_title in title:
    #                 hwnds.append(hwnd)
    #                 return False  # Stop enumeration
    #             return True
    #         except Exception as e:
    #             print(f"Error processing window {hwnd}: {e}")
    #             return True  # Continue with enumeration
    #
    #     try:
    #         win32gui.EnumWindows(callback, 0)
    #     except Exception as e:
    #         return hwnds[0] if hwnds else None
    #
    #     return hwnds[0] if hwnds else None
    #
    # @staticmethod
    # def set_window_on_top(hwnd):
    #     win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


class PickCore(IPickCore):
    @staticmethod
    def get_mouse_position():
        current_position = pyautogui.position()
        return current_position.x, current_position.y

    @staticmethod
    def get_current_dpi():
        # 获取当前显示设备的 DPI
        hdc = ctypes.windll.user32.GetDC(0)
        dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # 88 是 LOGPIXELSX
        dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)  # 90 是 LOGPIXELSY
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return dpi_x, dpi_y
