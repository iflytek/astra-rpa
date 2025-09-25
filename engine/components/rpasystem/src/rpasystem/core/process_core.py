import os
import subprocess
from abc import ABC, abstractmethod

import psutil


class IProcessCore(ABC):
    @staticmethod
    @abstractmethod
    def run_cmd_admin(cmd: str, cwd: str = ""):
        pass

    @staticmethod
    @abstractmethod
    def run_cmd(cmd=None, cwd=None):
        pass

    @staticmethod
    @abstractmethod
    def get_pid_list():
        """
        获取当前所有pid
        """
        pass

    @staticmethod
    @abstractmethod
    def terminate_pid(pid: int, wait_time: int = 1):
        pass


class ProcessCoreWin(IProcessCore):
    @staticmethod
    def run_cmd_admin(cmd: str, cwd: str = ""):
        """
        以管理员权限运行命令
        """
        if not cmd:
            raise ValueError("命令不能为空")
        if not cwd:
            cwd = None

        try:
            # 使用runas命令以管理员权限运行
            if cwd and os.path.exists(cwd):
                # 如果有工作目录，先切换到该目录
                full_cmd = f'cd /d "{cwd}" && {cmd}'
            else:
                full_cmd = cmd

            # 使用runas命令请求管理员权限
            process = subprocess.Popen(
                ["runas", "/user:Administrator", f'cmd /c "{full_cmd}"'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return process
        except Exception as e:
            raise RuntimeError(f"执行管理员命令失败: {e}")

    @staticmethod
    def run_cmd(cmd=None, cwd=None):
        """
        以普通权限运行命令
        """
        if not cmd:
            raise ValueError("命令不能为空")
        if not cwd:
            cwd = None

        try:
            # 确保cmd是字符串格式
            if isinstance(cmd, list):
                cmd = " ".join(cmd)

            # 在Windows上使用更稳定的配置
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return process
        except Exception as e:
            raise RuntimeError(f"执行命令失败: {e}")

    @staticmethod
    def get_pid_list():
        """
        获取当前所有pid
        """
        return psutil.process_iter(["name"])

    @staticmethod
    def terminate_pid(pid: int, wait_time: int = 1):
        try:
            process = psutil.Process(pid)
            process.terminate()
            try:
                process.wait(timeout=wait_time)
            except psutil.NoSuchProcess:
                pass
        except psutil.AccessDenied:
            raise ValueError(f"无法终止进程 {pid}：访问被拒绝。")
        except psutil.TimeoutExpired:
            raise ValueError(f"进程 {pid} 未在超时时间内终止。")
        except Exception as e:
            raise ValueError(f"进程 {pid} 终止时发生错误：{e}")


class ProcessCoreLinux(IProcessCore):
    @staticmethod
    def run_cmd_admin(cmd: str, cwd: str = ""):
        """
        以管理员权限运行命令
        """
        if not cmd:
            raise ValueError("命令不能为空")

        try:
            full_cmd = f"sudo {cmd}"
            process = subprocess.Popen(
                full_cmd,
                cwd=cwd,
                shell=True,
                start_new_session=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return process
        except Exception as e:
            raise RuntimeError(f"执行管理员命令失败: {e}")

    @staticmethod
    def run_cmd(cmd=None, cwd=None):
        """
        以普通权限运行命令
        """
        if not cmd:
            raise ValueError("命令不能为空")

        try:
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                start_new_session=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return process
        except Exception as e:
            raise RuntimeError(f"执行命令失败: {e}")

    @staticmethod
    def get_pid_list():
        """
        获取当前所有pid
        """
        return psutil.process_iter(["name"])

    @staticmethod
    def terminate_pid(pid: int, wait_time: int = 1):
        try:
            process = psutil.Process(pid)
            process.terminate()
            try:
                process.wait(timeout=wait_time)
            except psutil.NoSuchProcess:
                pass
        except psutil.AccessDenied:
            raise ValueError(f"无法终止进程 {pid}：访问被拒绝。")
        except psutil.TimeoutExpired:
            raise ValueError(f"进程 {pid} 未在超时时间内终止。")
        except Exception as e:
            raise ValueError(f"进程 {pid} 终止时发生错误：{e}")
