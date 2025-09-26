import base64
import json
import os
import socket
import subprocess
import sys
import time
from enum import Enum

import psutil

from ..logger import logger


class EmitType(Enum):
    """
    定义向前端传递消息类型
    """

    SYNC = "sync"  # 阻塞消息，用于组件更新
    SYNC_CANCEL = "sync_cancel"  # 取消阻塞，用于组件更新
    TIP = "tip"  # 后台提示信息，非阻塞
    ALERT = "alert"  # 后台警告信息，非阻塞
    LOG_REPORT = "log_report"  # 日志框，非阻塞
    EDIT_SHOW_HIDE = "edit_show_hide"  # 唤起问题
    EXECUTOR_END = "executor_end"  # 执行器结束, 唤起+执行状态，非阻塞


def string_to_base64(input_string):
    """
    支付串转base64
    """
    string_bytes = input_string.encode("utf-8")
    encoded_bytes = base64.b64encode(string_bytes)
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def emit_to_front(emit_type: EmitType, msg=None):
    """
    向控制台输出信息，传递到 tauri main.rs标准输出中，触发给前端
    使用print暂时行不通，原因未知
    """
    data = {"type": emit_type.value, "msg": msg}
    logger.info("emit msg to front: {}".format(data))
    data = json.dumps(data)
    if sys.platform == "win32":
        subprocess.run(
            ["echo", "||emit|| {}".format(string_to_base64(data))],
            shell=True,
            check=True,
        )
    else:
        subprocess.run(
            ["echo", "||emit|| {}".format(string_to_base64(data))],
            shell=False,
            check=True,
        )


def check_port(port, host="127.0.0.1"):
    """
    检测端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 设置超时时间
            sock.settimeout(0.2)
            result = sock.connect_ex((host, port))
            if result == 0:
                return False
    except Exception as e:
        pass
    return True


def kill_proc_tree(
    proc: psutil.Process = None,
    including_parent: bool = True,
    exclude_pids: list = None,
):
    """
    递归地杀死指定PID的进程及其所有子进程。
    """
    work_dir = os.getcwd()

    try:
        children = proc.children(recursive=True)
        for child in children:
            # 递归调用以杀死子进程的子进程
            kill_proc_tree(child, including_parent=True)
    except Exception as e:
        pass

    if including_parent:
        try:
            if exclude_pids:
                if proc.pid in exclude_pids:
                    return

            # 只会杀掉启动当期运行目录下的进程
            proc_cwd = proc.exe()
            if work_dir not in proc_cwd:
                return

            # 尝试杀死父进程
            proc.kill()
            proc.wait(5)  # 等待进程结束，防止僵尸进程
        except psutil.NoSuchProcess:
            pass


def read_last_n_lines(file_path, n):
    """
    返回文件最后n行信心
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, "rb") as f:
        # 移动到文件末尾
        f.seek(0, 2)
        pointer_location = f.tell()
        buffer = bytearray()
        lines_found = 0

        for i in range(pointer_location - 1, -1, -1):
            f.seek(i)
            byte = f.read(1)
            buffer.append(byte[0])

            if byte == b"\n":
                lines_found += 1
                if lines_found == n:
                    break

        # 反转并解码字节数组为字符串
        line_strs = buffer[::-1].decode("utf-8").strip()
        return line_strs.splitlines(True)


def get_settings(file_path=".setting.json", times: int = 5):
    setting = {}
    for i in range(times):
        try:
            if os.path.exists(file_path):
                with open(file_path, encoding="utf-8") as file:
                    setting = json.load(file)
                    break
        except Exception as e:
            time.sleep(0.1)
    return setting
