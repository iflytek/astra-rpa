import ctypes

import pyautogui
import win32con
import win32gui
import win32print
from win32api import GetSystemMetrics

from ..logger import logger


def window_size():
    return pyautogui.size()


def get_screen_scale_rate_new():
    """
    根据dpi，获取屏幕的缩放比例
    :return:
    """
    import ctypes

    user32 = ctypes.windll.user32
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    sys_dpi = user32.GetDpiForSystem()
    return round(sys_dpi / 96, 2)


def get_screen_scale_rate_runtime():
    """
    实时根据主屏dpi获取到主屏的缩放比
    :return:
    """
    from ctypes import Structure, c_long, c_uint, pointer, windll

    try:

        class RECT(Structure):
            _fields_ = [
                ("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long),
            ]

        rect = RECT()
        user32 = windll.user32
        rectp = pointer(rect)
        hmonitor = user32.MonitorFromRect(rectp, win32con.MONITOR_DEFAULTTOPRIMARY)
        dpix = c_uint()
        dpiy = c_uint()
        p_dpix = pointer(dpix)
        p_dpiy = pointer(dpiy)
        res = windll.shcore.GetDpiForMonitor(hmonitor, 0, p_dpix, p_dpiy)
        if res != 0:
            return get_screen_scale_rate_new()
        return round(p_dpix.contents.value / 96, 2)
    except Exception as e:
        logger.info(f"获取缩放比出现了异常{e}")
        return get_screen_scale_rate_new()


def get_system_display_size() -> tuple[int, int]:
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def validate_ui_element_rect(left, top, right, bottom, max_width=2000, max_height=1200):
    """
    校验界面元素矩形框的合理性（坐标系原点在左上角）
    新增校验规则：
    1. 坐标不允许为负数[6,7](@ref)
    2. 宽度不超过max_width（默认2000px，基于4K屏的1/2宽度）
    3. 高度不超过max_height（默认1200px，基于4K屏的1/2高度）
    """
    try:
        # 类型校验（支持int/float类型）
        if not all(isinstance(v, (int, float)) for v in [left, top, right, bottom]):
            return False

        # 坐标有效性校验
        if any(v < 0 for v in [left, top, right, bottom]):
            return False

        # 逻辑位置校验
        if left >= right or top >= bottom:
            return False

        # 计算实际尺寸
        width = right - left
        height = bottom - top

        # 非退化校验（避免零尺寸元素）
        if width <= 0 or height <= 0:
            return False

        # 最大尺寸校验（基于常见界面元素尺寸规范[6,8](@ref)）
        if width > max_width or height > max_height:
            return False

        return True
    except TypeError:
        # 处理非数值类型输入（如字符串）
        return False


def validate_window_rect(left, top, right, bottom):
    max_width = window_size().width
    max_height = window_size().height
    try:
        # 类型校验（支持int/float类型）
        if not all(isinstance(v, (int, float)) for v in [left, top, right, bottom]):
            return False

        # 坐标有效性校验
        if any(v < 0 for v in [left, top, right, bottom]):
            return False

        # 逻辑位置校验
        if left >= right or top >= bottom:
            return False

        # 计算实际尺寸
        width = right - left
        height = bottom - top

        # 非退化校验（避免零尺寸元素）
        if width <= 0 or height <= 0:
            return False

        # 最大尺寸校验（基于常见界面元素尺寸规范[6,8](@ref)）
        if width > max_width or height > max_height:
            return False

        return True
    except TypeError:
        # 处理非数值类型输入（如字符串）
        return False


def get_screen_scale():
    def get_real_resolution():
        """获取真实的分辨率"""
        hDC = win32gui.GetDC(0)
        # 横向分辨率
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        # 纵向分辨率
        h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
        return w, h

    def get_screen_size():
        """获取缩放后的分辨率"""
        w = GetSystemMetrics(0)
        h = GetSystemMetrics(1)
        return w, h

    real_resolution = get_real_resolution()
    screen_size = get_screen_size()

    screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
    screen_scale_rate2 = get_screen_scale_rate_runtime()
    return max(screen_scale_rate, screen_scale_rate2)
