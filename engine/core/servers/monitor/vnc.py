import os
import sys

from rpaframe import logger
from rpawatch.utils.subprocess import SubPopen


class VNCServer:
    """VNC服务器管理类，负责启动和停止VNC服务及WebSocket代理"""

    def __init__(self, vnc_port=5900, websocket_port=5901):
        """
        初始化VNCServer

        Args:
            vnc_port (int): VNC服务器端口，默认5900
            websocket_port (int): WebSocket代理端口，默认5901
        """
        self.vnc_process = None
        self.websockify_process = None

        self.vnc_port = vnc_port
        self.websocket_port = websocket_port

        self._vnc_dir = None
        self._log_dir = None
        self._is_running = False

    @property
    def vnc_dir(self):
        """获取VNC目录路径"""
        if self._vnc_dir is None:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            if sys.platform == "win32":
                self._vnc_dir = os.path.join(parent_dir, "vnc", "win")
            else:
                self._vnc_dir = os.path.join(parent_dir, "vnc", "linux")
        return self._vnc_dir

    @property
    def log_dir(self):
        if self._log_dir is None:
            self._log_dir = os.path.join(os.getcwd(), "log")
        return self._log_dir

    def start(self):
        """
        启动VNC服务器和WebSocket代理

        Returns:
            bool: 启动成功返回True，失败返回False
        """
        if self._is_running:
            logger.warning("VNCServer 已在运行中")
            return True

        try:
            logger.info("开始启动 VNCServer...")

            # 启动VNC服务器
            if not self._start_vnc_server():
                return False

            # 启动WebSocket代理
            if not self._start_websocket_proxy():
                self._stop_vnc_server()  # 清理已启动的服务
                return False

            self._is_running = True
            logger.info("VNCServer 启动完成")
            return True

        except Exception as e:
            logger.error("VNCServer 启动失败: {}".format(e))
            self.stop()
            return False

    def stop(self):
        """
        停止VNC服务器和WebSocket代理

        Returns:
            bool: 停止成功返回True，失败返回False
        """
        if not self._is_running:
            logger.info("VNCServer 未在运行")
            return True

        try:
            logger.info("开始停止 VNCServer...")

            success = True

            # 停止WebSocket代理
            if not self._stop_websocket_proxy():
                success = False

            # 停止VNC服务器
            if not self._stop_vnc_server():
                success = False

            self._is_running = False

            if success:
                logger.info("VNCServer 停止完成")
            else:
                logger.warning("VNCServer 停止过程中出现错误")

            return success

        except Exception as e:
            logger.error("VNCServer 停止失败: {}".format(e))
            self._is_running = False
            return False

    def is_running(self):
        """
        检查服务是否正在运行

        Returns:
            bool: 正在运行返回True，否则返回False
        """
        return self._is_running

    def _setup_vnc_config(self):
        """设置VNC配置文件"""
        try:
            ini_tpl_path = os.path.join(self.vnc_dir, "ultravnc.ini.tpl")
            ini_path = os.path.join(self.vnc_dir, "ultravnc.ini")

            # 读取模板文件内容
            with open(ini_tpl_path, encoding="utf-8") as file:
                content = file.read()

            # 替换路径变量
            content = content.replace("{{$PATH}}", self.log_dir)
            content = content.replace("{{$PORT}}", str(self.vnc_port))

            # 写入配置文件
            with open(ini_path, "w", encoding="utf-8") as file:
                file.write(content)

            logger.debug("VNC配置文件设置完成")
            return True

        except Exception as e:
            logger.error("设置VNC配置文件失败: {}".format(e))
            return False

    def _start_vnc_server(self):
        """
        启动VNC服务器

        Returns:
            bool: 启动成功返回True，失败返回False
        """
        try:
            # 设置配置文件
            if not self._setup_vnc_config():
                return False

            # 获取VNC可执行文件路径
            vnc_path = os.path.join(self.vnc_dir, "winvnc.exe")
            if not os.path.exists(vnc_path):
                logger.error("VNC可执行文件不存在: {}".format(vnc_path))
                return False

            # 启动VNC进程
            self.vnc_process = SubPopen(name="winvnc", cmd=[vnc_path])
            self.vnc_process.run()

            # 检查进程是否成功启动
            if not self.vnc_process.is_alive():
                logger.error("VNC进程启动失败")
                return False

            logger.info("VNC服务器启动成功，进程ID: {}".format(self.vnc_process.proc.pid))
            return True

        except Exception as e:
            logger.error("启动VNC服务器失败: {}".format(e))
            return False

    def _stop_vnc_server(self):
        """
        停止VNC服务器

        Returns:
            bool: 停止成功返回True，失败返回False
        """
        try:
            if self.vnc_process and self.vnc_process.is_alive():
                self.vnc_process.kill()
                logger.info("VNC服务器已停止")
                return True
            else:
                logger.info("VNC服务器未运行")
                return True

        except Exception as e:
            logger.error("停止VNC服务器失败: {}".format(e))
            return False

    def _start_websocket_proxy(self):
        """
        启动WebSocket代理

        Returns:
            bool: 启动成功返回True，失败返回False
        """
        try:
            # 启动websockify进程
            self.websockify_process = SubPopen(
                name="websockify",
                cmd=[
                    sys.executable,
                    "-m",
                    "websockify",
                    str(self.websocket_port),
                    "127.0.0.1:{}".format(self.vnc_port),
                ],
            )
            self.websockify_process.run()

            # 检查进程是否成功启动
            if not self.websockify_process.is_alive():
                logger.error("WebSocket代理进程启动失败")
                return False

            logger.info(
                "WebSocket代理启动成功，VNC端口: {}, WebSocket端口: {}".format(self.vnc_port, self.websocket_port)
            )
            return True

        except Exception as e:
            logger.error("启动WebSocket代理失败: {}".format(e))
            return False

    def _stop_websocket_proxy(self):
        """
        停止WebSocket代理

        Returns:
            bool: 停止成功返回True，失败返回False
        """
        try:
            if self.websockify_process and self.websockify_process.is_alive():
                self.websockify_process.kill()
                logger.info("WebSocket代理已停止")
                return True
            else:
                logger.info("WebSocket代理未运行")
                return True

        except Exception as e:
            logger.error("停止WebSocket代理失败: {}".format(e))
            return False

    def __enter__(self):
        """上下文管理器入口"""
        if not self.start():
            raise RuntimeError("VNCServer 启动失败")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
