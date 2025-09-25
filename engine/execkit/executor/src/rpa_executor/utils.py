import base64
import os
import subprocess
import sys

import psutil
from rpa_executor.logger import logger

system_encoding = sys.getdefaultencoding()


def kill_proc_tree(pid, including_parent=True, exclude_pids=None):
    """
    递归地杀死指定PID的进程及其所有子进程。
    :param pid: 要杀死的进程的PID。
    :param including_parent: 是否包括父进程本身。
    :param exclude_pids: 排出进程
    """
    if exclude_pids is None:
        exclude_pids = []

    work_dir = os.getcwd()
    try:
        # 获取指定PID的进程
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return  # 如果进程不存在，则退出函数

    try:
        # 获取所有子进程
        children = proc.children(recursive=True)
        for child in children:
            kill_proc_tree(child.pid, including_parent=True)  # 递归调用以杀死子进程的子进程
    except Exception as e:
        pass

    if including_parent:
        try:
            if pid in exclude_pids:
                return
            # 这里对进程名字做判断，避免关闭执行器启动的客户端程序
            # name = proc.name()
            # if name not in ["python.exe", "iflyrpa-log.exe"]:
            #     return
            # 只会杀掉当前运行目录下的进程
            proc_cwd = proc.exe()
            if work_dir not in proc_cwd:
                return
            # 尝试杀死父进程
            proc.kill()
            proc.wait(5)  # 等待进程结束，防止僵尸进程
        except psutil.NoSuchProcess:
            pass


def exec_run(exec_args: list, ignore_error: bool = False, timeout=-1):
    """启动子进程，忽略日志"""
    try:
        logger.debug("exec_run res: {}".format(exec_args))

        # 注意部分命令执行不能加env，对于拾取组件，加上env导致拾取进程启动异常
        current_env = os.environ.copy()
        current_env["no_proxy"] = "True"

        proc = subprocess.Popen(exec_args, shell=False, env=current_env)

        if timeout > 0:
            _, stderr_data = proc.communicate(timeout=timeout)
        else:
            _, stderr_data = proc.communicate()
        if stderr_data and not ignore_error:
            raise Exception(stderr_data)
    except Exception as e:
        raise e
