import os
import subprocess
import sys
import threading
import time

import psutil
from rpaframe import logger
from rpawatch.utils.utils import kill_proc_tree

system_encoding = sys.getdefaultencoding()


def disable_cmd_quick_edit():
    # window特有的
    if sys.platform == "win32":
        import ctypes

        # 定义常量
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_EXTENDED_FLAGS = 0x0080

        # 获取标准输入的句柄
        kernel32 = ctypes.windll.kernel32
        hStdin = kernel32.GetStdHandle(-10)

        # 获取当前输入模式
        mode = ctypes.c_uint32()
        kernel32.GetConsoleMode(hStdin, ctypes.byref(mode))

        # 禁用快速编辑模式
        mode.value &= ~ENABLE_QUICK_EDIT_MODE
        mode.value |= ENABLE_EXTENDED_FLAGS

        # 设置新的输入模式
        kernel32.SetConsoleMode(hStdin, mode)


def default_output_callback(msg):
    logger.info("[RES]{}".format(msg))


def async_default_output_callback(msg, error):
    if error:
        logger.info("[ERR]{}".format(error))
    else:
        logger.info("[RES]{}".format(msg))


class SubPopen:
    def __init__(self, name: str = None, cmd: list = None, params: dict = None):
        if not params:
            params = {}
        if not cmd:
            cmd = []
        self.name = name
        self.cmd = cmd
        self.params = params
        self.proc = None
        self.start_time = 0
        self.__log__ = None

    def logger_handler(self, output_callback=default_output_callback, timeout=None) -> (str, str):
        if self.__log__:

            def read_stdout(pipe, callback):
                """读取标准输出的线程函数"""
                for text in iter(pipe.readline, ""):
                    if callback:
                        callback(text.strip())

            stdout_thread = threading.Thread(
                target=read_stdout,
                args=(self.proc.stdout, output_callback),
                daemon=True,
            )
            stdout_thread.start()

            self.proc.wait(timeout=timeout)
            stdout_thread.join()

            _, stderr_data = self.proc.communicate()
            return "", stderr_data
        else:
            return self.proc.communicate(timeout=timeout)

    def async_logger_handler(self, output_callback=async_default_output_callback):
        if not self.__log__:
            # 不支持没有日志的情况
            return

        def read_stdout(proc, callback):
            """读取标准输出的线程函数"""
            try:
                for text in iter(proc.stdout.readline, ""):
                    if callback:
                        callback(text.strip())
                proc.wait()
            except Exception as e:
                pass
            finally:
                _, stderr_data = proc.communicate()
                if proc.returncode != 0:
                    callback("", stderr_data)
                else:
                    pass

        stdout_thread = threading.Thread(target=read_stdout, args=(self.proc, output_callback), daemon=True)
        stdout_thread.start()
        return

    def run(self, shell: bool = None, log: bool = False, encoding="") -> "SubPopen":
        disable_cmd_quick_edit()

        # shell 默认值
        if shell is None:
            if sys.platform == "win32":
                shell = True
            else:
                shell = False

        # 配置encoding
        if encoding == "":
            encoding = system_encoding

        # 参数
        param_list = list()
        for key, value in self.params.items():
            param_list.append("--{}={}".format(key, value))
        cmd = self.cmd + param_list
        logger.info("cmd: {}".format(cmd))

        # 启动是否包含log
        self.start_time = time.time()

        # 注意部分命令执行不能加env，对于拾取组件，加上env导致拾取进程启动异常
        current_env = os.environ.copy()
        current_env["no_proxy"] = "True"
        env = current_env if "pip" in cmd else None

        self.__log__ = log
        if log:
            self.proc = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                encoding=encoding,
            )
        else:
            self.proc = subprocess.Popen(
                cmd,
                shell=shell,
                env=env,
            )
        return self

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
        """
        判断子进程是否存活
        """
        return self.proc is not None and self.proc.poll() is None

    def kill(self):
        if self.proc:
            try:
                # 如果已经关闭可能报错
                kill_proc_tree(psutil.Process(self.proc.pid), including_parent=True)
            except Exception as e:
                pass
