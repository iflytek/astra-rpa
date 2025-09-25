import sys
import time
from urllib.parse import urlparse

from importlib_metadata import version
from setup.logger import logger
from setup.utils.subprocess import SubPopen


class PipManager:
    """pip管理类"""

    DOWNLOADED_PACKAGES = {}

    @staticmethod
    def local_packages_version(package_name):
        """获取本地版本"""
        try:
            return version(package_name)
        except Exception:
            return None

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
