import ctypes
from typing import List, Tuple

import pyautogui
import pygetwindow
import uiautomation as auto
import win32com
import win32com.client
import win32con
import win32gui
import win32process
from locator import PickerType, Rect
from locator.utils.process import get_process_name
from pygetwindow._pygetwindow_win import Win32Window, isWindowVisible
from rpaframe.logger.logger import logger
from uiautomation import Control, ControlFromHandle


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

    import win32con

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
        return get_screen_scale_rate_new()


def get_system_display_size() -> Tuple[int, int]:
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)  # noqa
    height = user32.GetSystemMetrics(1)  # noqa
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
    max_width = pyautogui.size().width
    max_height = pyautogui.size().height
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


def is_desktop_by_cls_and_name(cls_name: str, name: str) -> bool:
    """
    判断是否是桌面窗口
    注意桌面窗口随时都会变动，cls和name都会变动
    """
    # 常见的桌面窗口类型
    desktop_types = [
        # Windows 10/11 桌面窗口
        ("WorkerW", ""),  # 桌面背景窗口
        ("Progman", "Program Manager"),  # 主桌面窗口
        # Windows 7 桌面窗口
        ("Shell_TrayWnd", "开始"),  # 开始菜单
        ("Shell_TrayWnd", "任务栏"),  # 任务栏
        # 其他可能的桌面窗口
        ("Shell_TrayWnd", ""),  # 空名称的任务栏
        ("WorkerW", "Program Manager"),  # 某些版本的桌面窗口
    ]

    return (cls_name, name) in desktop_types


def is_desktop_by_handle(handle, ctrl: Control) -> bool:
    """
    判断是否是桌面窗口
    """
    if not ctrl or win32gui.GetParent(handle) != 0:
        return False
    return is_desktop_by_cls_and_name(ctrl.ClassName, ctrl.Name)


RPA_HIGHLIGHT_PROCESSES = list()
RPA_HIGHLIGHT_CHECKED = False


def is_rpa_highlight(ctrl: Control) -> bool:
    """判断control是否是高亮窗口"""
    global RPA_HIGHLIGHT_CHECKED
    global RPA_HIGHLIGHT_PROCESSES
    if not RPA_HIGHLIGHT_CHECKED:
        RPA_HIGHLIGHT_CHECKED = True
        all_windows = pygetwindow.getWindowsWithTitle("")
        for window in all_windows:
            win_control = ControlFromHandle(window._hWnd)  # noqa
            if getattr(win_control, "AutomationId", None) == "HighlightForm":
                RPA_HIGHLIGHT_PROCESSES.append(win_control.ProcessId)
    if ctrl.ProcessId in RPA_HIGHLIGHT_PROCESSES:
        return True
    return False


def get_pid_by_handle(handle: int):
    """
    从窗口对象中获取程序pid
    """
    _, proc_pid = win32process.GetWindowThreadProcessId(handle)
    return proc_pid


def find_app_handles(app: str) -> list:
    """
    获取指定app所有可视窗口，过滤掉cmd命令
    """
    handles = []
    # 获取所有的窗口并遍历
    # logger.info(f"获取窗口列表: {app}")
    if app == "iexplore":
        ie_win = auto.WindowControl(searchDepth=1, ClassName="IEFrame")
        return [ie_win.NativeWindowHandle]
    for window in pygetwindow.getWindowsWithTitle(""):
        try:
            # logger.info(f"窗口标题: {window.title}")
            hwnd = window._hWnd  # noqa
            pid = get_pid_by_handle(handle=hwnd)
            if not pid:
                continue

            app_name = get_process_name(pid)
            if app_name == "cmd":
                # 处理命令行窗口
                if app not in ["cmd", "conhost", "powershell", "bash"]:
                    continue
            elif app_name != app:
                # 普通窗口名称匹配
                continue

            if not isWindowVisible(hwnd):
                continue

            handles.append(hwnd)
        except Exception as e:
            logger.error("获取窗口失败: {}".format(e))
            continue
    return handles


DESKTOP_WINDOW_HANDLES = list()


def show_desktop_rect(rect: Rect, desktop_handle=None):
    all_windows = pygetwindow.getWindowsWithTitle("")
    for window in all_windows:
        win_control = ControlFromHandle(window._hWnd)  # noqa

        # rpa高亮窗口，忽略
        if is_rpa_highlight(win_control):
            continue

        # 已经最小化了，忽略
        if window.isMinimized:
            continue

        # 桌面窗口不能最小化，最小化导致桌面被隐藏
        if (desktop_handle and window._hWnd == desktop_handle) or window._hWnd in DESKTOP_WINDOW_HANDLES:  # noqa
            continue

        # 窗口挡住桌面元素，最小化窗口
        win_rect = Rect(window.left, window.top, window.right, window.bottom)
        if win_rect.overlaps(rect):
            window.minimize()


def find_window(cls_name: str, name: str, app_name: str = None) -> int:
    global DESKTOP_WINDOW_HANDLES
    is_desktop_win = is_desktop_by_cls_and_name(cls_name, name)

    # 通过app_name(进程名称)获取所有的顶层窗口, 并过滤cls_name和name
    match_list = list()
    for handle in find_app_handles(app_name):
        handler_ctrl = ControlFromHandle(handle)
        handler_name = handler_ctrl.Name
        handler_class_name = handler_ctrl.ClassName

        # 使用是否是桌面元素过滤(桌面窗口的特殊性,不能直接通过cls过滤)
        match_desktop_win = is_desktop_by_cls_and_name(handler_class_name, handler_name)
        if match_desktop_win and handle not in DESKTOP_WINDOW_HANDLES:
            # 记录所有的桌面的handle
            DESKTOP_WINDOW_HANDLES.append(handle)
        if is_desktop_win and match_desktop_win:
            match_list.append(
                (
                    handle,
                    handler_name,
                    handler_class_name,
                    win32gui.GetParent(handle) == 0,
                    cls_name == handler_class_name,
                )
            )
            continue

        # 使用cls过滤
        if handler_class_name != cls_name:
            continue

        # 使用name过滤
        if handler_name != name:
            continue
        match_list.append(
            (
                handle,
                handler_name,
                handler_class_name,
                win32gui.GetParent(handle) == 0,
                True,
            )
        )

    # 优先检查win32gui.GetParent(handle) == 0，如果都为空就剔除这个优先选项
    match_list_lv2 = [item for item in match_list if item[3]]
    logger.info(f"优先检查win32gui.GetParent(handle) == 0，如果都为空就剔除这个优先选项: {match_list_lv2}")
    if not match_list_lv2:
        match_list_lv2 = match_list

    # 优先选择窗口cls一致的handle，如果有多个桌面窗口的情况
    if is_desktop_win and len(match_list_lv2) > 1:
        match_list_lv2 = [item for item in match_list_lv2 if item[4]]
        logger.info(f"优先选择窗口cls一致的handle: {match_list_lv2}")
        if match_list_lv2:
            return match_list_lv2[0][0]

    # 优先选择窗口name最长的handle
    if match_list_lv2:
        match_list_lv2.sort(key=lambda item: len(item[1]))
        logger.info(f"优先选择窗口name最长的handle: {match_list_lv2}")
        return match_list_lv2[0][0]

    # 如果都没有，则返回0
    return 0


def find_window_handles_list(cls_name: str, name: str, app_name: str = None, picker_type=None) -> List[int]:
    """
    获取指定窗口的handle列表，包含cls完全一致的handle和窗口name最长并且一致的handle

    :param cls_name: 窗口类名
    :param name: 窗口名称
    :param app_name: 应用程序名称
    :return: handle列表，包含cls完全一致的handle和窗口name最长并且一致的handle
    """
    if picker_type == PickerType.WINDOW.value:
        return [find_window(cls_name, name, app_name)]
    global DESKTOP_WINDOW_HANDLES
    is_desktop_win = is_desktop_by_cls_and_name(cls_name, name)

    # 通过app_name(进程名称)获取所有的顶层窗口, 并过滤cls_name和name
    match_list = list()
    for handle in find_app_handles(app_name):
        handler_ctrl = ControlFromHandle(handle)
        handler_name = handler_ctrl.Name
        handler_class_name = handler_ctrl.ClassName

        # 使用是否是桌面元素过滤(桌面窗口的特殊性,不能直接通过cls过滤)
        match_desktop_win = is_desktop_by_cls_and_name(handler_class_name, handler_name)
        if match_desktop_win and handle not in DESKTOP_WINDOW_HANDLES:
            # 记录所有的桌面的handle
            DESKTOP_WINDOW_HANDLES.append(handle)
        if is_desktop_win and match_desktop_win:
            match_list.append(
                (
                    handle,
                    handler_name,
                    handler_class_name,
                    win32gui.GetParent(handle) == 0,
                    cls_name == handler_class_name,
                )
            )
            continue

        # 使用cls过滤
        if handler_class_name != cls_name:
            continue

        # 使用name过滤
        if handler_name != name:
            continue
        match_list.append(
            (
                handle,
                handler_name,
                handler_class_name,
                win32gui.GetParent(handle) == 0,
                True,
            )
        )

    # 优先检查win32gui.GetParent(handle) == 0，如果都为空就剔除这个优先选项
    match_list_lv2 = [item for item in match_list if item[3]]
    logger.info(f"优先检查win32gui.GetParent(handle) == 0，如果都为空就剔除这个优先选项: {match_list_lv2}")
    if not match_list_lv2:
        match_list_lv2 = match_list

    result_handles = []

    # 获取cls完全一致的handle
    if is_desktop_win and len(match_list_lv2) > 1:
        cls_match_list = [item for item in match_list_lv2 if item[4]]
        logger.info(f"cls完全一致的handle: {cls_match_list}")
        if cls_match_list:
            result_handles.append(cls_match_list[0][0])

    # 获取窗口name最长并且一致的handle
    if match_list_lv2:
        # 按name长度排序，取最长的
        match_list_lv2.sort(key=lambda item: len(item[1]), reverse=True)
        logger.info(f"窗口name最长并且一致的handle: {match_list_lv2}")

        # 获取第一个匹配项的name作为基准
        target_name = match_list_lv2[0][1]
        logger.info(f"目标窗口名称: {target_name}")

        # 遍历match_list_lv2，获取跟match_list_lv2[0][1]同名的所有handle
        for item in match_list_lv2:
            handle = item[0]
            handler_name = item[1]

            # 如果窗口名称与目标名称相同，且handle不重复，则添加到结果中
            if handler_name == target_name and handle not in result_handles:
                result_handles.append(handle)
                logger.info(f"添加同名handle: {handle}, 窗口名称: {handler_name}")

    # 这里筛选桌面窗口

    return result_handles


def find_window_by_enum(cls: str, name: str, app_name: str = None) -> int:
    """
    通过枚举窗口 classname 和 name属性获得窗口，返回如果是0则窗口不存在
    与find_window的区别是使用EnumWindows枚举所有窗口，能找到更多窗口
    :param cls: 控件className
    :param name: 控件name
    :param app_name: 程序名字
    :return:
    """

    def get_all_windows_by_enum():
        """通过枚举获取所有窗口句柄"""
        handles = []

        def enum_win(hwnd, result):
            # 通过这种方式获取当前窗口是否是顶层窗口
            if not isWindowVisible(hwnd):
                return
            handles.append(hwnd)

        win32gui.EnumWindows(enum_win, handles)
        return handles

    # 获取枚举的窗口句柄列表
    enum_handles = get_all_windows_by_enum()
    logger.info(f"枚举的窗口句柄列表: {enum_handles}")
    # 如果指定了app_name，也加上find_app_handles的结果，确保不遗漏
    if app_name:
        try:
            app_handles = find_app_handles(app_name)
            # 合并句柄列表，去重
            all_handles = list(set(enum_handles + app_handles))
            logger.info(f"合并后的窗口句柄列表: {all_handles}")
        except Exception:
            all_handles = enum_handles
    else:
        all_handles = enum_handles

    # 复用find_window的匹配逻辑
    global DESKTOP_WINDOW_HANDLES
    is_desktop_win = is_desktop_by_cls_and_name(cls, name)

    match_list = []
    for handle in all_handles:
        handler_ctrl = ControlFromHandle(handle)
        if not handler_ctrl:
            continue

        handler_name = handler_ctrl.Name or ""
        handler_class_name = handler_ctrl.ClassName or ""

        # 使用是否是桌面元素过滤(桌面窗口的特殊性,不能直接通过cls过滤)
        match_desktop_win = is_desktop_by_cls_and_name(handler_class_name, handler_name)
        if match_desktop_win and handle not in DESKTOP_WINDOW_HANDLES:
            DESKTOP_WINDOW_HANDLES.append(handle)
        if is_desktop_win and match_desktop_win:
            match_list.append(
                (
                    handle,
                    handler_name,
                    handler_class_name,
                    win32gui.GetParent(handle) == 0,
                    cls == handler_class_name,
                )
            )
            continue

        # 使用cls过滤
        if handler_class_name != cls:
            continue

        # 使用name过滤 (支持双向模糊匹配)
        if handler_name != name:
            continue
        match_list.append(
            (
                handle,
                handler_name,
                handler_class_name,
                win32gui.GetParent(handle) == 0,
                True,
            )
        )

    # 复用find_window的优先级选择逻辑
    match_list_lv2 = [item for item in match_list if item[3]]
    logger.info(f"测试一开始的: {match_list_lv2}")
    if not match_list_lv2:
        match_list_lv2 = match_list

    if is_desktop_win and len(match_list_lv2) > 1:
        match_list_lv2 = [item for item in match_list_lv2 if item[4]]
        if match_list_lv2:
            return match_list_lv2[0][0]

    if match_list_lv2:
        match_list_lv2.sort(key=lambda item: len(item[1]), reverse=True)
        logger.info(f"优先选择窗口cls一致的handle: {match_list_lv2}")
        return match_list_lv2[0][0]

    return 0


def find_window_by_enum_list(cls: str, name: str, app_name: str = None, picker_type=None) -> int:
    """
    通过枚举窗口 classname 和 name属性获得窗口，返回如果是0则窗口不存在
    与find_window的区别是使用EnumWindows枚举所有窗口，能找到更多窗口
    :param cls: 控件className
    :param name: 控件name
    :param app_name: 程序名字
    :return:
    """
    if picker_type == PickerType.WINDOW.value:
        return [find_window_by_enum(cls, name, app_name)]

    def get_all_windows_by_enum():
        """通过枚举获取所有窗口句柄"""
        handles = []

        def enum_win(hwnd, result):
            # 通过这种方式获取当前窗口是否是顶层窗口
            if not isWindowVisible(hwnd):
                return
            handles.append(hwnd)

        win32gui.EnumWindows(enum_win, handles)
        return handles

    # 获取枚举的窗口句柄列表
    enum_handles = get_all_windows_by_enum()
    logger.info(f"枚举的窗口句柄列表: {enum_handles}")
    # 如果指定了app_name，也加上find_app_handles的结果，确保不遗漏
    if app_name:
        try:
            app_handles = find_app_handles(app_name)
            # 合并句柄列表，去重
            all_handles = list(set(enum_handles + app_handles))
            logger.info(f"合并后的窗口句柄列表: {all_handles}")
        except Exception:
            all_handles = enum_handles
    else:
        all_handles = enum_handles

    # 复用find_window的匹配逻辑
    global DESKTOP_WINDOW_HANDLES
    is_desktop_win = is_desktop_by_cls_and_name(cls, name)

    match_list = []
    for handle in all_handles:
        handler_ctrl = ControlFromHandle(handle)
        if not handler_ctrl:
            continue

        handler_name = handler_ctrl.Name or ""
        handler_class_name = handler_ctrl.ClassName or ""

        # 使用是否是桌面元素过滤(桌面窗口的特殊性,不能直接通过cls过滤)
        match_desktop_win = is_desktop_by_cls_and_name(handler_class_name, handler_name)
        if match_desktop_win and handle not in DESKTOP_WINDOW_HANDLES:
            DESKTOP_WINDOW_HANDLES.append(handle)
        if is_desktop_win and match_desktop_win:
            match_list.append(
                (
                    handle,
                    handler_name,
                    handler_class_name,
                    win32gui.GetParent(handle) == 0,
                    cls == handler_class_name,
                )
            )
            continue

        # 使用cls过滤
        if handler_class_name != cls:
            continue

        # 使用name过滤 (支持双向模糊匹配)
        if handler_name != name:
            continue
        match_list.append(
            (
                handle,
                handler_name,
                handler_class_name,
                win32gui.GetParent(handle) == 0,
                True,
            )
        )

    # 复用find_window的优先级选择逻辑
    match_list_lv2 = [item for item in match_list if item[3]]
    if not match_list_lv2:
        match_list_lv2 = match_list
    result_handles = []

    # 获取cls完全一致的handle
    if is_desktop_win and len(match_list_lv2) > 1:
        cls_match_list = [item for item in match_list_lv2 if item[4]]
        logger.info(f"cls完全一致的handle: {cls_match_list}")
        if cls_match_list:
            result_handles.append(cls_match_list[0][0])

    # 获取窗口name最长并且一致的handle
    if match_list_lv2:
        # 按name长度排序，取最长的
        match_list_lv2.sort(key=lambda item: len(item[1]), reverse=True)
        logger.info(f"窗口name最长并且一致的handle: {match_list_lv2}")

        # 获取第一个匹配项的name作为基准
        target_name = match_list_lv2[0][1]
        logger.info(f"目标窗口名称: {target_name}")

        # 遍历match_list_lv2，获取跟match_list_lv2[0][1]同名的所有handle
        for item in match_list_lv2:
            handle = item[0]
            handler_name = item[1]

            # 如果窗口名称与目标名称相同，且handle不重复，则添加到结果中
            if handler_name == target_name and handle not in result_handles:
                result_handles.append(handle)
                logger.info(f"添加同名handle: {handle}, 窗口名称: {handler_name}")

    return result_handles


def top_window(handle: int, ctrl: Control):
    if ctrl and ctrl.ClassName == "IEFrame":
        ct = None
        root_control = auto.GetRootControl()
        for control, _ in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if control.ClassName == "IEFrame":
                ct = control
                break
        ct.SetActive()
        return

    # 1. 先尝试恢复和激活窗口
    cur_window = Win32Window(handle)
    try:
        if cur_window.isMinimized:
            cur_window.restore()
            cur_window.activate()
    except Exception as e:
        logger.info(f"恢复和激活窗口失败")

    if is_desktop_by_handle(handle, ctrl):
        # 桌面窗口不需要置顶
        return

    # 2. 避免窗口多次置顶，微信等软件很多交互重复置顶会导致页面元素消失，如表情选择界面
    system_windows = {"Shell_SecondaryTrayWnd", "TaskManagerWindow"}

    need_top = False
    cur_br = ctrl.BoundingRectangle
    cur_rect = Rect(cur_br.left, cur_br.top, cur_br.right, cur_br.bottom)

    pre_win = ctrl.GetPreviousSiblingControl()
    while pre_win:
        try:
            # 避免自己
            if handle == pre_win.NativeWindowHandle:
                continue
            # 避免rpa画框
            if is_rpa_highlight(pre_win):
                continue
            # 系统窗口
            is_c = cur_rect.overlaps(pre_win.BoundingRectangle)
            if pre_win.ClassName in system_windows and is_c:
                # 系统窗口，应用窗口是无法置顶到系统的界面上去的，如任务管理器界面，所以需要先缩小它再置顶
                window = Win32Window(pre_win.NativeWindowHandle)
                window.minimize()
                continue
            # 避免重复置顶
            if is_c:
                need_top = True
        except Exception as e:
            pass
        finally:
            pre_win = pre_win.GetPreviousSiblingControl()

    if not need_top:
        return

    # 3. 置顶
    if win32gui.IsIconic(handle):
        win32gui.ShowWindow(handle, win32con.SW_NORMAL)
    else:
        if ctrl.ClassName == "SAP_FRONTEND_SESSION":
            return
        # 结合键盘事件
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        win32gui.SetForegroundWindow(handle)


def top_browser(handle: int, ctrl: Control):
    if ctrl and ctrl.ClassName == "IEFrame":
        ct = None
        root_control = auto.GetRootControl()
        for control, _ in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if control.ClassName == "IEFrame":
                ct = control
                break
        ct.SetActive()
        return

    # 1. 先尝试恢复和激活窗口
    cur_window = Win32Window(handle)
    try:
        if cur_window.isMinimized:
            cur_window.restore()
            cur_window.activate()
    except Exception as e:
        logger.info(f"恢复和激活窗口失败")

    if is_desktop_by_handle(handle, ctrl):
        # 桌面窗口不需要置顶
        return

    # 2. 避免窗口多次置顶，微信等软件很多交互重复置顶会导致页面元素消失，如表情选择界面
    system_windows = {"Shell_SecondaryTrayWnd", "TaskManagerWindow"}

    need_top = False
    cur_br = ctrl.BoundingRectangle
    cur_rect = Rect(cur_br.left, cur_br.top, cur_br.right, cur_br.bottom)

    pre_win = ctrl.GetPreviousSiblingControl()
    while pre_win:
        try:
            # 避免自己
            if handle == pre_win.NativeWindowHandle:
                continue
            # 避免rpa画框
            if is_rpa_highlight(pre_win):
                continue
            # 系统窗口
            is_c = cur_rect.overlaps(pre_win.BoundingRectangle)
            if pre_win.ClassName in system_windows and is_c:
                # 系统窗口，应用窗口是无法置顶到系统的界面上去的，如任务管理器界面，所以需要先缩小它再置顶
                window = Win32Window(pre_win.NativeWindowHandle)
                window.minimize()
                continue
            # 避免重复置顶
            if is_c:
                need_top = True
        except Exception as e:
            pass
        finally:
            pre_win = pre_win.GetPreviousSiblingControl()

    if not need_top:
        return

    # 3. 置顶
    if win32gui.IsIconic(handle):
        win32gui.ShowWindow(handle, win32con.SW_NORMAL)
    else:
        win32gui.SetWindowPos(
            handle,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        win32gui.SetWindowPos(
            handle,
            win32con.HWND_NOTOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
