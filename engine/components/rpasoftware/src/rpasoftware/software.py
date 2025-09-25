import os
import platform
import subprocess
import sys
import time
import warnings
from typing import Any

import psutil
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel
from rpaatomic.atomic import atomicMg
from rpaatomic.logger import logger
from rpasoftware.core import ISoftwareCore
from rpasoftware.error import *

if sys.platform == "win32":
    from rpasoftware.core_win import SoftwareCore
elif platform.system() == "Linux":
    from rpasoftware.core_unix import SoftwareCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

SoftwareCore: ISoftwareCore = SoftwareCore()


class Software:
    @staticmethod
    @atomicMg.atomic(
        "Software",
        inputList=[
            atomicMg.param(
                "app_abs_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": []},
                ),
            ),
            atomicMg.param("app_args", required=False, level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("software_open", types="Str")],
    )
    def open(app_abs_path: str = "", app_args: str = "") -> str:
        """
        打开软件
        :param app_abs_path: 地址
        :param app_args: 参数
        :return:
        """

        if not os.path.exists(app_abs_path):
            raise BaseException(
                APP_PATH_ERROR_FORMAT.format(app_abs_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )

        warnings.filterwarnings("ignore", category=ResourceWarning)
        process = subprocess.Popen([app_abs_path] + app_args.split(), start_new_session=True)
        while not process.pid:
            time.sleep(0.3)
        return app_abs_path

    @staticmethod
    @atomicMg.atomic(
        "Software",
        inputList=[
            atomicMg.param(
                "app_abs_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": []},
                ),
            )
        ],
    )
    def close(app_abs_path: str):
        """
        关闭软件
        :param app_abs_path: 地址
        :return:
        """

        if not os.path.exists(app_abs_path):
            raise BaseException(
                APP_PATH_ERROR_FORMAT.format(app_abs_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )

        exe_name = os.path.split(app_abs_path)[1]
        try:
            if sys.platform == "win32":
                # 特殊处理
                if exe_name == "ThunderStart.exe":
                    subprocess.run(["taskkill", "/F", "/IM", "Thunder.exe"])
                    return
                subprocess.run(["taskkill", "/F", "/IM", exe_name])
            else:
                subprocess.run(["pkill", exe_name])
        except Exception as e:
            logger.error("error: Software close {}".format(e))
            return

    @staticmethod
    def exists(app_name: str = "", parent_name: str = "") -> bool:
        """
        exists 软件是否存在
        :param app_name: 软件名称
        :param parent_name: 软件的父级名称
        :return:
        """

        return Software.pid(app_name, parent_name) >= 0

    @staticmethod
    def pid(app_name: str = "", parent_name: str = "") -> int:
        """
        pid 获取正在执行的软件pid
        :param app_name: 软件名称
        :param parent_name: 软件的父级名称
        :return:
        """

        for process in psutil.process_iter():
            try:
                if process.name() == app_name:
                    if parent_name:
                        for parent in process.parents():
                            if parent.name() == parent_name:
                                return process.pid
                    else:
                        return process.pid
            except Exception as e:
                pass
        return -1

    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        """
        获取软件地址
        """
        return SoftwareCore.get_app_path(app_name)

    @staticmethod
    @atomicMg.atomic("Software", outputList=[atomicMg.param("exec_cmd", types="Dict")])
    def cmd(cmd: str) -> dict:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.terminate()
        return {
            "status": 0 if stdout else 1,
            "stdout": stdout.decode("gbk"),
            "stderr": stderr.decode("gbk"),
        }
