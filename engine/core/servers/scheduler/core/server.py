import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from .. import ServerLevel
from ..logger import logger


class IServer(ABC):
    def __init__(
        self,
        svc=None,
        name: str = "",
        level: ServerLevel = ServerLevel.NORMAL,
        run_is_async: bool = False,
    ):
        # 名称
        self.name = name
        # 等级
        self.level = level
        # 业务上下文
        self.svc = svc
        # run是否需要异步执行
        self.run_is_async = run_is_async
        # recover
        self.recover_ing = False

    @abstractmethod
    def run(self):
        """启动服务，不能包含阻塞"""
        pass

    def health(self) -> bool:
        """健康检擦 10s 触发一次 健康就返回True"""
        return True

    def recover(self):
        """监控检查恢复"""
        pass


class ServerManager:
    """服务管理"""

    def __init__(self, svc):
        self.server_list = []
        self.svc = svc

    def register(self, server: IServer):
        """注册"""
        self.server_list.append(server)
        return self

    def check(self):
        """检测"""
        while True:
            time.sleep(10)
            try:
                for server in self.server_list:
                    if not server.health() and server.recover_ing is False:
                        logger.info(f"{server.name} is not health, start recover")
                        server.recover_ing = True
                        server.recover()
                        server.recover_ing = False
            except Exception as e:
                pass

    def run(self):
        # 1. 先启动code核心的非异步
        for c_server in self.server_list:
            if not c_server.run_is_async and c_server.level == ServerLevel.CORE:
                c_server.run()

        def async_run():
            while not self.svc.route_server_is_start:
                time.sleep(1)

            # 2. 启动普通的的非异步
            for n_server in self.server_list:
                if not n_server.run_is_async and n_server.level == ServerLevel.NORMAL:
                    n_server.run()

            # 3. 启动异步
            with ThreadPoolExecutor() as pool:
                for a_server in self.server_list:
                    if a_server.run_is_async:
                        pool.submit(a_server.run)

        threading.Thread(target=async_run, daemon=True).start()
        threading.Thread(target=self.check, daemon=True).start()
        return self
