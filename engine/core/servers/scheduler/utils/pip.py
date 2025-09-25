import os
import sys
import time
from urllib.parse import urlparse

from importlib_metadata import version

from ..logger import logger
from ..utils.subprocess import SubPopen


class PipManager:
    """pip管理类"""

    DOWNLOADED_PACKAGES = {}

    @staticmethod
    def get_installed_packages(exec_python=None):
        if not exec_python:
            exec_python = sys.executable

        packages = dict()

        def default_output_callback(msg):
            try:
                if "==" not in msg:
                    return
                pck, var = msg.split("==")
                packages[pck] = var
            except Exception as e:
                pass

        current_dir = os.path.dirname(os.path.dirname(__file__))
        cmd = [exec_python, os.path.join(current_dir, "pip_all_version_script.py")]
        _, err = SubPopen(cmd=cmd).run(log=True).logger_handler(output_callback=default_output_callback)
        if err:
            logger.error("get_installed_packages error:{}".format(err))
        return packages

    @staticmethod
    def package_version(package_name: str, exec_python=None) -> str:
        """
        校验本地包版本，如果没有这个包，版本为空
        """
        if not exec_python:
            exec_python = sys.executable
        cmd = [
            exec_python,
            "-c",
            "from importlib_metadata import version; print(version('{}'))".format(package_name),
        ]
        stdout, stderr = SubPopen(cmd=cmd).run(log=True).proc.communicate()
        if stderr:
            return ""
        if stdout:
            return stdout.strip()

    @staticmethod
    def local_packages_version(package_name):
        """获取本地版本"""
        try:
            return version(package_name)
        except Exception:
            return None

    @staticmethod
    def download_pip_cmd(package, ver, mirror, exec_python=None, pip_cache_dir="pip_cache"):
        pck = package
        if ver:
            pck = "{}=={}".format(package, ver)
        if not exec_python:
            exec_python = sys.executable

        return [
            exec_python,
            "-m",
            "pip",
            "download",
            pck,
            "-d",
            pip_cache_dir,
            "--index-url={}".format(mirror),
            "--trusted-host",
            urlparse(mirror).hostname,
            "--disable-pip-version-check",
            "--no-cache",
        ]

    @staticmethod
    def download_pip(package, ver, mirror, exec_python=None, pip_cache_dir="pip_cache", time_out=30):
        # 下载缓存
        pck = package
        if ver:
            pck = "{}=={}".format(package, ver)
        if not exec_python:
            exec_python = sys.executable

        if pck in PipManager.DOWNLOADED_PACKAGES:
            # 如果下载完成就直接结束
            last = PipManager.DOWNLOADED_PACKAGES.get(pck)
            if last < 0:
                return
            # 如果下载没有完成，比较抢占的时间, 没有超过就直接返回
            if time.time() - last < time_out:
                return
        PipManager.DOWNLOADED_PACKAGES[package] = time.time()  # 抢占标志
        # 真下载

        cmd = [
            exec_python,
            "-m",
            "pip",
            "download",
            pck,
            "-d",
            pip_cache_dir,
            "--index-url={}".format(mirror),
            "--trusted-host",
            urlparse(mirror).hostname,
            "--disable-pip-version-check",
            "--no-cache",
        ]
        _, error_data = SubPopen(cmd=cmd).run(log=True).logger_handler()
        if error_data:
            logger.error("download_pip error:{}".format(error_data))
            raise Exception("download_pip error:{}".format(error_data))

        # 缓存
        PipManager.DOWNLOADED_PACKAGES[package] = -1  # 结束

    @staticmethod
    def install_pip_cmd(package, ver, exec_python=None, pip_cache_dir="pip_cache"):
        pck = package
        if ver:
            pck += "=={}".format(ver)
        if not exec_python:
            exec_python = sys.executable

        return [
            exec_python,
            "-m",
            "pip",
            "install",
            pck,
            "--no-index",
            "--find-links={}".format(pip_cache_dir),
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]

    @staticmethod
    def install_pip(
        package,
        ver,
        exec_python=None,
        pip_cache_dir="pip_cache",
        error_try=False,
        mirror="",
    ):
        pck = package
        if ver:
            pck += "=={}".format(ver)
        if not exec_python:
            exec_python = sys.executable

        cmd1 = [
            exec_python,
            "-m",
            "pip",
            "install",
            pck,
            "--no-index",
            "--find-links={}".format(pip_cache_dir),
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]
        cmd2 = [
            exec_python,
            "-m",
            "pip",
            "install",
            pck,
            "--find-links={}".format(pip_cache_dir),
            "--index-url={}".format(mirror),
            "--trusted-host",
            urlparse(mirror).hostname,
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]

        def __install_pip(cmd):
            try:
                _, error_data = SubPopen(cmd=cmd).run(log=True).logger_handler()
                if error_data:
                    logger.error("install_pip error:{}".format(error_data))
                    raise Exception("install_pip error:{}".format(error_data))
            except Exception as e:
                new_version = PipManager.local_packages_version(package)
                if not ver and new_version:
                    return
                if ver and ver == new_version:
                    return
                logger.error("install_pip error:{}".format(e))
                raise e

        try:
            __install_pip(cmd1)
        except Exception as e:
            if error_try:
                __install_pip(cmd2)
            else:
                raise e
