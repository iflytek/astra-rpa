import sys
import threading
import time

import requests

from .. import ComponentType
from ..config import Config
from ..core.executor.executor import ExecutorManager
from ..core.picker.picker import Picker
from ..core.servers.normal_server import TriggerServer, VNCServer
from ..logger import logger
from ..utils.utils import check_port


class Svc:
    def __init__(self):
        """程序上下文管理类"""
        # 0. 服务对应端口
        self.port_lock = threading.Lock()
        self.port_dict: dict = {}

        # 1. 配置

        # 运行配置 静态
        self.config: Config = None

        # 端口号:
        self.__local_port__: int = 8002
        # 路由端口[随机分配]
        self.route_port: int = self.get_validate_port(ComponentType.ROUTE)
        # 调度器端口[随机分配]
        self.scheduler_port: int = self.get_validate_port(ComponentType.SCHEDULER)
        # trigger端口[随机分配]
        self.trigger_port: int = self.get_validate_port(ComponentType.TRIGGER)
        # 浏览器通信端口[固定分配]
        self.browser_connector_port: int = 9082
        self.port_dict[ComponentType.BROWSER_CONNECTOR.name.lower()] = self.browser_connector_port
        # 拾取框[固定分配]
        self.hl_port: int = 11001
        # 虚拟桌面
        self.win_virtual_port: int = self.get_validate_port()

        # 2. 核心服务

        # 本地路由是否启动标识
        self.route_server_is_start = False
        # 执行器
        self.executor_mg = ExecutorManager(self)
        # pick
        self.picker = Picker(self)
        # 触发器
        self.trigger_server = TriggerServer(self)
        # nav服务

        if sys.platform == "win32":
            self.vnc_server = VNCServer(self)
        else:
            self.vnc_server = None

        # 3. 核心模式

        # 是否是终端模式
        self.terminal_mod = False

        # 4. 全局状态
        self.pip_download_ing = False

    def set_config(self, config):
        self.config = config
        self.picker.init()

    def get_validate_port(self, component_type: ComponentType = None) -> int:
        """
        获取一个本地可用的端口
        """
        with self.port_lock:
            while True:
                self.__local_port__ += 1
                # 长时间运行的端口资源问题
                if self.__local_port__ >= 65500:
                    self.__local_port__ = 8002
                if check_port(self.__local_port__):
                    if component_type is not None:
                        self.port_dict[component_type.name.lower()] = self.__local_port__
                    return self.__local_port__

    def register_server(self):
        def register_component(component, port: int):
            try:
                url = "http://127.0.0.1:{}/rpa-local-route/registry".format(self.route_port)
                data = {"module_name": component, "port": str(port)}
                response = requests.post(
                    url=url,
                    json=data,
                )
                logger.info("register_component: {} => {}".format(data, response.text))
                if "OK" in response.text:
                    pass
                else:
                    raise Exception("route register error : {} {} => {}".format(component, port, response.text))
            except Exception as e:
                logger.exception("register_component error: {}".format(e))

        if len(self.port_dict) == 0:
            return

        if not self.route_server_is_start:
            return

        # 等待本地路由加载完成
        while check_port(port=self.route_port):
            time.sleep(0.1)
        for k, v in self.port_dict.items():
            register_component(k, v)


_svc = Svc()


def get_svc() -> Svc:
    """
    获取全局svc
    """
    return _svc
