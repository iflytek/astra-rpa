import threading
import time
from ctypes import wintypes
from ctypes.wintypes import BOOL, WCHAR
from pathlib import Path
from typing import Any, Optional

import win32con
import win32gui
import win32print
import win32process
from locator import ILocator, PickerType, Rect
from locator.core.jab_locator_dll import *
from locator.core.uia_locator import uia_factory
from locator.utils.window import (
    find_window,
    get_screen_scale_rate_runtime,
    get_system_display_size,
    top_window,
    validate_ui_element_rect,
)
from rpaframe.logger.logger import logger
from uiautomation import ControlFromHandle
from win32api import GetSystemMetrics

# 一些常量
MAX_STRING_SIZE = 1024
SHORT_STRING_SIZE = 256
MAX_KEY_BINDINGS = 50
MAX_RELATION_TARGETS = 25
MAX_RELATIONS = 5
MAX_ACTION_INFO = 256
MAX_ACTIONS_TO_DO = 32
MAX_VISIBLE_CHILDREN = 256
TIMEOUT = 30


class JOBJECT64(c_int64):
    pass


class AccessibleValueInfo(Structure):
    _fields_ = [("name", WCHAR * MAX_STRING_SIZE)]


class AccessibleTextRectInfo(Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int),
        ("width", c_int),
        ("height", c_int),
    ]


class JABContext(object):
    """直接与java应用交互，类似于uia框架的抽象"""

    def __init__(self, hwnd=None, vm_id=None, acc_context=None):
        if bridge_dll is None:
            raise Exception("尚未加载jab所需dll")

        if hwnd and not vm_id:
            vm_id = c_long()  # vm_id的作用是跟指定dilog窗口通信
            acc_context = JOBJECT64()
            res = bridge_dll.getAccessibleContextFromHWND(hwnd, byref(vm_id), byref(acc_context))
            logger.info(f"本次的可访问上下文结果   {res}, {vm_id}")
            vm_id = vm_id.value  # 0x607A8
        elif vm_id and not hwnd:
            hwnd = bridge_dll.getWindowHandleFromAccContext(vm_id, acc_context)

        self.hwnd = hwnd
        self.vm_id = vm_id
        self.acc_context = acc_context

    @property
    def Name(self):
        # 这里目的是支持桌面端原子能力，统一调用方式，context可以类比为uia中的control
        info = AccessibleValueInfo()
        accessible_context = self.acc_context
        result = bridge_dll.getAccessibleValueInfo(self.vm_id, accessible_context, byref(info))
        if result == 0:
            raise Exception("Java Access Bridge func '{}' error".format("GetAccessibleContextInfo"))
        logger.info(f"获取name{info.name}")
        return info.name

    def get_element_from_path(self, path, timeout=15000):
        info = JOBJECT64()
        path_bytes = path.encode("utf-8")
        path = ctypes.c_char_p(path_bytes)
        res = bridge_dll.getElementFromPath(self.hwnd, self.vm_id, path, timeout, byref(info))
        logger.info("get_element_from_path, BOOL:{}".format(res))
        self.acc_context = info
        if info.value == 0:
            raise Exception("校验失败，请检查可编辑属性")
        return JABLocator(jab_context=self)

    def get_element_rect(self, ratio=1):
        rect = AccessibleTextRectInfo(x=0, y=0, width=0, height=0)
        res = bridge_dll.getElementRectangle(self.hwnd, self.vm_id, self.acc_context, byref(rect), c_float(ratio))
        logger.info("get_element_rect, BOOL:{}".format(res))
        return rect

    def scroll_into_view(self):
        res = bridge_dll.scrollIntoView(self.vm_id, self.acc_context)
        logger.info("scroll_into_view, BOOL:{}".format(res))


class JABLocator(ILocator):
    def __init__(
        self,
        jab_context: JABContext = None,
    ):
        self.jab_context = jab_context
        self.__rect = None  # 缓存 rect

    def rect(self) -> Optional[Rect]:
        return self.__rect

    def update_rect(self, new_rect):
        self.__rect = new_rect  # 正确更新内部值

    def control(self) -> Any:
        return self.jab_context


class JABFactory:
    """JAB工厂"""

    black_list: list = ["eclipse"]  # 不支持的Java应用黑名单

    @classmethod
    def __judge_java_window__(cls, hwnd):
        """
        检查是否有注入的java窗口
        这个函数实际上会对建立了窗口通信的所有窗口进行广播发送，只要有一个窗口返回true则返回true
        """
        is_inject = bridge_dll.isJavaWindow(hwnd)
        if not is_inject:
            raise Exception("target application is not JAVA windows or dialog start failed")
        return is_inject

    @classmethod
    def __inject_dll__(cls, pid):
        try:
            cur_inject_bridge = WinDLL(inject_dll_path)
        except Exception as e:
            logger.error(f"{inject_dll_path} 注入失败: : {str(e)}")
            raise e

        # 设置函数原型
        cur_inject_bridge.inject.argtypes = [c_ulong, c_char_p]
        cur_inject_bridge.inject.restype = c_bool

        # 调用函数
        dll_path = jar_inject_dll_path

        try:
            result = cur_inject_bridge.inject_with_timeout(pid, dll_path.encode("utf-8"), 30000)
            logger.info(f"注入结果: {'成功' if result else '失败'}")
        except Exception as e:
            logger.error(f"{jar_inject_dll_path} 注入失败: {str(e)}")
            raise Exception

    @classmethod
    def __create_rpa_directories__(cls):
        try:
            home_dir = Path.home()
            target_path = (
                home_dir / "AppData" / "Roaming" / "iflyrpa" / "logs" / "jab"
            )  # 这里的处理不同操作系统的路径分隔符
            if not target_path.exists():
                target_path.mkdir(parents=True)
                logger.info(f"JAB日志目录创建成功：{target_path}")
            else:
                logger.info(f"JAB日志目录已存在：{target_path}")
            return True
        except Exception as e:
            logger.error(f"创建JAB日志目录失败: {str(e)}")
            return False

    @classmethod
    def __flatten_path__(cls, path):
        """写成一个以/作为分隔符的字符串"""

        def serialize(datadict):
            # 获取tag_name对应的值，如果不存在则默认为空字符串
            tag_name = datadict.get("tag_name", "")
            # 如果存在tag_name键，则从字典中移除
            if tag_name is not None:
                del datadict["tag_name"]

            disable_list = datadict.get("disable_keys", []) + [
                "checked",
                "disable_keys",
            ]

            # 使用列表推导式将字典键值对转换为指定格式
            serialized_items = [
                '@{}"{}"'.format(key, value)
                for key, value in datadict.items()
                if key not in disable_list
                and (not isinstance(value, str) or (isinstance(value, str) and len(value) > 0))
            ]

            # 使用'&&'连接列表中的所有元素，得到最终的字符串
            serialized_string = "&&".join(serialized_items)

            # 如果存在tag_name，将其作为序列化内容的开始
            if tag_name:
                serialized_string = "{}[{}]".format(tag_name, serialized_string)
            else:
                serialized_string = "[{}]".format(serialized_string)

            return serialized_string

        path_str_all = []
        for p in path:
            if not p.get("checked", ""):
                continue
            path_str_all.append(serialize(p))
        return "/" + "/".join(path_str_all)

    @classmethod
    def __get_screen_scale__(cls):
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
        ratio = max(screen_scale_rate, screen_scale_rate2)
        return ratio

    @classmethod
    def init(cls, **kwargs):
        # 用户目录下创建一个logs目录

        cls.__create_rpa_directories__()

        # 注入等
        def initialize():
            global bridge_dll
            bridge_dll = cdll.LoadLibrary(lib_windows_access_bridge_path)
            bridge_dll.Windows_run()

        class MyThread(threading.Thread):
            def __init__(self):
                super().__init__()  # daemon=True
                self._stop_event = threading.Event()

            def stop(self):
                self._stop_event.set()

            def run(self):
                msg = wintypes.MSG()
                initialize()
                while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) and not self._stop_event.is_set():
                    logger.info(
                        "Time: {}, hWnd: {}, Message: {}, Point (x: {}, y: {}), wParam: {}, lParam: {}".format(
                            msg.time,
                            msg.hWnd,
                            msg.message,
                            msg.pt.x,
                            msg.pt.y,
                            msg.wParam,
                            msg.lParam,
                        )
                    )
                    user32.TranslateMessage(msg)
                    user32.DispatchMessageW(msg)
                logger.info("End of GetMessageW")

        t = MyThread()
        t.daemon = True
        t.start()

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Any:
        if picker_type == PickerType.SIMILAR.value:
            raise NotImplementedError("还未实现")

        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return Exception("请勾选校验信息")

        # 1. 如果path_list只有一个就都是uia的功能
        if len(path_list) == 1:
            return uia_factory.find(ele, picker_type, **kwargs)

        # 2. 先找到窗口, 并置顶
        root_handle = find_window(path_list[0].get("cls"), path_list[0].get("name"), app_name=app_name)
        if not root_handle:
            raise Exception("元素无法找到")
        root_ctrl = ControlFromHandle(handle=root_handle)
        top_window(
            handle=root_handle, ctrl=root_ctrl
        )  # 置顶窗口 巨坑！！！！！！注意使用同一个handle实例化多个Control会导致uia调用报错

        # 3. 使用jab去找
        path_list_str = cls.__flatten_path__(path_list[1:])
        _, pid = win32process.GetWindowThreadProcessId(root_handle)

        # 3.1 尝试注入
        is_inject = False
        for i in range(3):  # 尝试3次
            try:
                is_inject = cls.__judge_java_window__(root_handle)
            except Exception as e:
                logger.error(f"第{i + 1}次判断Java窗口异常: {e}")
                pass

            if is_inject:
                logger.info(f"第{i + 1}次检测已注入")
                break

            logger.info(f"第{i + 1}次注入中...")
            try:
                cls.__inject_dll__(pid)
            except Exception as e:
                logger.error(f"第{i + 1}次注入DLL异常: {e}")

            time.sleep(0.1)

        if not is_inject:
            logger.error("JAB三次尝试均失败")
            return None

        jab_context = JABContext(hwnd=root_handle, vm_id=None, acc_context=None)

        # 3.2 通过path去找
        locator = jab_context.get_element_from_path(path_list_str)
        jab_context.scroll_into_view()

        # 3.3 分别率
        ratio = cls.__get_screen_scale__()

        rect_wywh = jab_context.get_element_rect(ratio=ratio)
        left = rect_wywh.x if rect_wywh.x >= 0 else 0
        top = rect_wywh.y if rect_wywh.y >= 0 else 0
        right = rect_wywh.x + rect_wywh.width if rect_wywh.x + rect_wywh.width >= 0 else 0
        bottom = rect_wywh.y + rect_wywh.height if rect_wywh.y + rect_wywh.height >= 0 else 0
        right = right if right >= left else left
        bottom = bottom if bottom >= top else top

        display = get_system_display_size()
        max_value_screen = [int(ratio * display[0]), int(ratio * display[1])]
        if not validate_ui_element_rect(left, top, right, bottom, max_value_screen[0], max_value_screen[1]):
            left = 0
            top = 0
            right = 1
            bottom = 1

        locator.update_rect(Rect(left, top, right, bottom))
        return locator


jab_factory = JABFactory()
jab_factory.init()
