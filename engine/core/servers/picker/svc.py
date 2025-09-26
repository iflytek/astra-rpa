"""服务上下文管理模块"""

import asyncio
import platform
import sys
import threading
import time
from typing import Any

from . import IEventCore, IPickerCore, PickerSign
from .error import TIMEOUT, TIMEOUT_LAG
from .error import BaseException as RpaBaseException
from .logger import logger


class SyncMap:
    """线程安全的映射类"""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.map = {}

    def __setitem__(self, key, value) -> None:
        with self.lock:
            self.map[key] = value

    def __getitem__(self, key) -> Any:
        with self.lock:
            return self.map.get(key)

    def __delitem__(self, key) -> None:
        with self.lock:
            if key in self.map:
                del self.map[key]

    def __contains__(self, key) -> bool:
        with self.lock:
            return key in self.map


class ServiceContext:
    """程序上下文管理类"""

    def __init__(self, port: int, highlight_socket_port: int, route_port: int) -> None:
        # 运行配置
        self.port: str = port
        self.highlight_socket_port: str = highlight_socket_port
        self.route_port: str = route_port

        # 全局运行事件
        self.__sign__: SyncMap = SyncMap()  # PickerSign

        # 策略
        self.strategy = None

        # 组件
        self.highlight_client = None
        self.locator = None
        self.event_core = None
        self.picker_core = None

        self.pick_server = None

        # sap预初始化用
        self.sapguiauto = None
        self.application = None

    def load_modules(self):
        """加载系统模块组件"""

        # 高亮
        from .core.highlight_client import highlight_client

        self.highlight_client = highlight_client

        # 策略
        from .strategy.manager import Strategy

        self.strategy: Strategy = Strategy(self)

        # 拾取 - 平台相关导入
        if sys.platform == "win32":
            from .core.event_core_win import EventCore
            from .core.picker_core_win import PickerCore

            self.event_core: IEventCore = EventCore()
            self.picker_core: IPickerCore = PickerCore()
        elif platform.system() == "Linux":
            pass

        # 定住 - 可选模块
        try:
            from locator.locator import LocatorManager

            self.locator = LocatorManager
        except ImportError:
            logger.info("无法导入locator模块，如非必要请忽略")
            self.locator = None

    def sign(self) -> SyncMap:
        """获取信号映射对象"""
        return self.__sign__

    async def send_sign(self, sign: PickerSign, data: Any, interval: int = 180) -> Any:
        """发送信号并等待响应"""
        # 清空返回值并发送sign
        result_sign = f"{sign.value}_RES"
        if result_sign in self.__sign__:
            del self.__sign__[result_sign]
        self.__sign__[sign.value] = data

        # 超时等待sign的返回结果
        start_time = interval
        self.pick_server.start_time = time.time()
        while result_sign not in self.__sign__ and start_time > 0:
            await asyncio.sleep(0.1)
            start_time -= 0.1
            if self.pick_server and self.pick_server.start_time and time.time() - self.pick_server.start_time > 15:
                self.event_core.close()  # 关闭监听
                raise RpaBaseException(TIMEOUT_LAG, "拾取卡顿超过15s，请退出编辑器后重新进入")
        if start_time <= 0:
            raise RpaBaseException(TIMEOUT, "拾取超时")

        # 返回值
        return self.__sign__[result_sign]
