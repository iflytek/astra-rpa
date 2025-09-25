import locale
import os
import subprocess
import sys
import time

import psutil
from setup.logger import logger

system_encoding = locale.getpreferredencoding()


class Process:
    """进程管理类"""

    @staticmethod
    def kill_all_zombie():
        """杀死所有的僵尸进程"""
        zombie_processes = Process.get_python_proc_in_current_dir()
        for z_p in zombie_processes:
            logger.info("kill_all_zombie {}".format(z_p.pid))
            Process.kill_proc_tree(z_p)

    @staticmethod
    def get_python_proc_in_current_dir():
        """获取所有在当前目录Python进程"""

        python_tag_window = "python.exe"
        python_tag_linux = "python3.7"

        setup_pid = os.getpid()
        work_dir = os.getcwd()

        all_process = list()
        if sys.platform == "win32":
            # 他们的名称是否包含python
            output_1 = subprocess.check_output(
                [
                    "tasklist",
                    "/FI",
                    "IMAGENAME eq {}".format(python_tag_window),
                    "/FO",
                    "CSV",
                ]
            ).decode(system_encoding)
            output_2 = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq route.exe", "/FO", "CSV"]).decode(
                system_encoding
            )
            output_3 = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq ConsoleApp1.exe", "/FO", "CSV"]
            ).decode(system_encoding)
            output_4 = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq winvnc.exe", "/FO", "CSV"]).decode(
                system_encoding
            )
            pids = []
            for output in [output_1, output_2, output_3, output_4]:
                for line in output.splitlines()[1:]:
                    parts = line.split(",")
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        pids.append(int(pid))
            for pid in pids:
                try:
                    # 忽略自己
                    if pid == setup_pid:
                        continue
                    # 查看他们的cwd
                    proc = psutil.Process(pid)
                    proc_cwd = proc.cwd()
                    if work_dir not in proc_cwd:
                        continue
                    # 都符合条件
                    all_process.append(proc)
                except Exception as e:
                    pass
        else:
            for proc in psutil.process_iter(["pid", "name", "exe", "cwd", "cmdline"]):
                try:
                    # 他们的名称是否包含python
                    proc_name = proc.name()
                    if python_tag_linux in proc_name or "route.exe" in proc_name or "winvnc" in proc_name:
                        # 忽略自己
                        if proc.pid == setup_pid:
                            continue
                        # 查看他们的cwd
                        proc_cwd = proc.cwd()
                        if work_dir not in proc_cwd:
                            continue
                        # 都符合条件
                        all_process.append(proc)
                except Exception as e:
                    pass
        return all_process

    @staticmethod
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
                Process.kill_proc_tree(child, including_parent=True)
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

    @staticmethod
    def get_root_process(proc):
        """
        获取根节点进程号(第一个不是python的进程)
        """
        if "python" in proc.name():
            p_proc = proc.parent()
            return Process.get_root_process(p_proc)
        else:
            return proc

    @staticmethod
    def pid_exist_check():
        # 一开始就启动获取root进程号，往往不是rpa进程号，这里异步3秒获取
        time.sleep(3)
        self = psutil.Process(os.getpid())
        root = Process.get_root_process(self)
        root_id = root.pid
        root_name = root.name()
        while True:
            time.sleep(1)
            try:
                if not psutil.pid_exists(root_id) or psutil.Process(root_id).name() != root_name:
                    logger.info("pid_exist_check kill process...")
                    # 首先递归杀一遍子进程
                    Process.kill_proc_tree(psutil.Process(os.getpid()), exclude_pids=[os.getpid()])
                    # 再找到当前的启动路径的所有python进程杀一遍
                    Process.kill_all_zombie()
                    # 自行杀掉
                    Process.kill_proc_tree(psutil.Process(os.getpid()))
            except Exception as e:
                logger.exception(e)
