import os
import subprocess
import sys
import threading
import time

import requests

from ...logger import logger


class LinuxVirtualDesk:
    """使用xephyr来构建"""

    def __init__(self, display=":10"):
        self.display = display
        self.xephyr = None
        self.env = os.environ.copy()
        self.env["DISPLAY"] = display
        self.resolution = "1280x720"

    def start(self, minimized=False):
        """
        启动Xephyr虚拟桌面

        Args:
            minimized: 是否最小化启动，默认为True
        """
        if not (self.xephyr is not None and self.xephyr.poll() is None):
            # 构建Xephyr命令
            cmd = [
                "Xephyr",
                self.display,
                "-screen",
                self.resolution,
                "-title",
                "IflyRPA",
            ]

            # 使用获取到的分辨率启动Xephyr
            self.xephyr = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)  # 至少等待会话初始化

    def stop(self):
        pass


class WindowVirtualDesk:
    def __init__(self):
        self.svc = None
        self.resolution = "1280x720"
        self.handler = None

    def start(self, svc, minimized=False):
        """
        启动虚拟桌面

        Args:
            svc: 上下文对象
            minimized: 是否最小化启动，默认为True
        """
        if not (self.handler is not None and self.handler.poll() is None):
            self.svc = svc
            vd_path = os.path.join(os.path.dirname(__file__), "virtual_desktop", "iFlyRpaRDP.exe")
            ve_path = os.path.join(os.path.dirname(__file__), "virtual_desktop", "virtual-engine.exe")
            python_path = os.path.abspath(svc.config.app_server.python_base)
            port = svc.win_virtual_port
            params = "{} --python-path={} --port={}".format(ve_path, python_path, port)
            self.handler = subprocess.Popen(
                [vd_path, params],
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)  # 至少等待会话初始化
        else:
            logger.info("虚拟桌面已经开启")

    def stop(self):
        """关闭虚拟桌面: 用户手动关闭"""
        pass


class WindowVirtualDeskSubprocessAdapter:
    """虚拟桌面subprocess适配器"""

    def __init__(self, svc, params: dict = None, exec_python=None):
        if not params:
            params = {}
        self.params = params
        self.svc = svc
        self.json = None
        self.live_cache = None
        self.live_cache_time = None
        self.set_param("exec_python", exec_python)

    def run(self, timeout=10 * 60):
        def is_start():
            is_live = virtual_desk.handler is not None and virtual_desk.handler.poll() is None
            if not is_live:
                logger.info("检查虚拟桌面是否开启 {}".format(False))
                raise Exception("检查虚拟桌面是否开启")

            try:
                url = "http://127.0.0.1:{}/is_alive".format(self.svc.win_virtual_port)
                response = requests.get(url)
                if response.status_code != 200:
                    logger.info("检查虚拟桌面是否开启 {}".format(False))
                    return False
                logger.info("检查虚拟桌面是否开启 {}".format(True))
                return True
            except Exception as e:
                logger.warning("检查虚拟桌面是否开启 {}".format(False))
                return False

        def raw_run():
            url = "http://127.0.0.1:{}/run".format(self.svc.win_virtual_port)
            response = requests.post(url, json=self.params)
            return response.json()

        i = 0
        while not is_start():
            time.sleep(2)
            i += 2
            if i > timeout:
                raise Exception("虚拟桌面启动超时")
        threading.Thread(target=raw_run, daemon=True).start()

    def set_param(self, key, val):
        """
        设置参数
        """
        self.params[key] = val

    def get_param(self, key):
        """
        获取参数
        """
        return self.params[key]

    def is_alive(self):
        if self.live_cache is not None and self.live_cache_time > time.time():
            return self.live_cache

        logger.info("检查虚拟桌面任务")
        self.live_cache_time = time.time() + 2
        try:
            url = "http://127.0.0.1:{}/is_alive".format(self.svc.win_virtual_port)
            response = requests.get(url)
            response_json = response.json()
            self.live_cache = response_json["data"]["current_process"]["has_running_process"]
            logger.info("检查虚拟桌面任务 {}".format(self.live_cache))
        except Exception as e:
            logger.error("检查虚拟桌面任务 {}".format(e))
            self.live_cache = False
        return self.live_cache

    def kill(self):
        try:
            logger.info("检查虚拟桌面任务关闭")
            url = "http://127.0.0.1:{}/kill".format(self.svc.win_virtual_port)
            response = requests.post(url)
            result = response.json()
            logger.info("检查虚拟桌面任务关闭 {}".format(result))
            return result
        except Exception as e:
            logger.error("检查虚拟桌面任务关闭 {}".format(e))


if sys.platform != "win32":
    virtual_desk = LinuxVirtualDesk()
else:
    virtual_desk = WindowVirtualDesk()
