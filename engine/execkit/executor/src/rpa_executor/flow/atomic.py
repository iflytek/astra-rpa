import os
import sys
from typing import Any
from urllib.parse import urlparse

from importlib_metadata import version as check_version
from rpaatomic import ReportTip

from rpa_executor.error import DOWNLOAD_ATOMIC_FORMAT, DOWNLOAD_ATOMIC_SUCCESS_FORMAT
from rpa_executor.flow.report import SimpleReport
from rpa_executor.flow.storage import Storage
from rpa_executor.flow.syntax import Job
from rpa_executor.flow.syntax.environment import Environment
from rpa_executor.flow.syntax.token import Token
from rpa_executor.logger import logger
from rpa_executor.utils import exec_run

python_executable = sys.executable


def compare_versions(v1, v2):
    for i in range(max(len(v1), len(v2))):
        num1 = v1[i] if i < len(v1) else 0
        num2 = v2[i] if i < len(v2) else 0
        if num1 > num2:
            return 1
        elif num1 < num2:
            return -1
    return 0


def find_version(lib, ver, ver_strict) -> bool:
    try:
        v0 = [int(x) for x in check_version(lib).split(".")]
        if ver:
            if not ver_strict:
                # 宽松模式
                v1 = [[int(x) for x in ver.split(".")][0]]
                if compare_versions(v0, v1) >= 0 and compare_versions([v1[0] + 1], v0) > 0:
                    return True
            else:
                # 严格模式
                if compare_versions(v0, [int(x) for x in ver.split(".")]) == 0:
                    return True
        else:
            # 没有版本号，直接返回
            return True
    except Exception as e:
        # 没有library
        pass
    return False


class Atomic(Job):
    def __init__(self, report: SimpleReport, storage):
        self.library_cache = {}
        self.report: SimpleReport = report
        self.storage: Storage = storage

    def init(self, token: Token, cache_dir: str):
        """原子能力初始化下载阶段"""

        src = token.value.get("src", "")
        keys = src.split("(")[0].split(".")

        library = keys[0]
        version = token.value.get("version", "1")

        # 不在安装没有的原子能力。已经交给rpa_schedule来管理
        # self.download(library, version, cache_dir)

    def download(
        self,
        library: str,
        version: str,
        cache_dir: str,
        mirror: str = "",
        version_strict: bool = False,
        error_try=True,
    ):
        # 1. 快速结束
        if not library:
            return

        # 2. cache
        if library in self.library_cache:
            return
        self.library_cache[library] = True

        # 3. 版本检查
        if find_version(library, version, version_strict):
            return

        # 4. 初始化
        self.report.info(ReportTip(msg_str=DOWNLOAD_ATOMIC_FORMAT.format(library)))

        pip_cache_dir = os.path.join(cache_dir, "pip_cache")
        if not os.path.exists(pip_cache_dir):
            os.makedirs(pip_cache_dir)

        # 5. 特殊library, 强制服务端版本
        remote_version_dict = self.storage.atomic_version_list()
        if library in remote_version_dict:
            # 如果是服务器的服务，就需要强制一个版本了

            remote_lib_version_arrr = remote_version_dict[library].split(",")
            for remote_version in remote_lib_version_arrr:
                if version:
                    # 大版本符合要求
                    if int(version.split(".")[0]) == int(remote_version.split(".")[0]):
                        version = remote_version
                        version_strict = True
                        break
                    else:
                        # 取最后一个
                        version = remote_version
                        version_strict = True
                else:
                    # 取最后一个
                    version = remote_version
                    version_strict = True

        # 6. 下载

        # 6.1 下载的名称
        if version:
            if version_strict:
                cmd_name = "{}=={}".format(library, version)
            else:
                v1 = [[int(x) for x in version.split(".")][0]]
                v2 = [v1[0] + 1]
                cmd_name = (
                    "{}>={},<{}".format(
                        library,
                        ".".join(str(x) for x in v1),
                        ".".join(str(x) for x in v2),
                    ),
                )
        else:
            cmd_name = library

        # 6.2 下载的mirror
        if mirror:
            mirror = [
                "--index-url",
                mirror,
                "--trusted-host",
                urlparse(mirror).hostname,
            ]
        else:
            mirror = [
                "--index-url",
                "http://localhost:31808/simple/",
                "--trusted-host",
                "localhost",
            ]

        # 6.3 下载的命令
        pip_download = [
            python_executable,
            "-m",
            "pip",
            "download",
            cmd_name,
            "-d",
            pip_cache_dir,
            *mirror,
            "--disable-pip-version-check",
            "--no-cache",
        ]
        pip_install_1 = [
            python_executable,
            "-m",
            "pip",
            "install",
            cmd_name,
            "--no-index",
            "--find-links={}".format(pip_cache_dir),
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]
        pip_install_2 = [
            python_executable,
            "-m",
            "pip",
            "install",
            cmd_name,
            "--find-links={}".format(pip_cache_dir),
            *mirror,
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]

        try:
            exec_run(pip_download, False, 600)
        except Exception as e:
            logger.warning("pip_download error: {}".format(e))
            pass

        def __install_pip(cmd):
            try:
                exec_run(cmd, False, 600)
            except Exception as e:
                # 3. 再检查一遍版本检查
                if find_version(library, version, version_strict):
                    return
                logger.error("__install_pip error:{}".format(e))
                raise e

        try:
            __install_pip(pip_install_1)
        except Exception as e:
            if error_try:
                __install_pip(pip_install_2)
            else:
                raise e

        self.report.info(ReportTip(msg_str=DOWNLOAD_ATOMIC_SUCCESS_FORMAT.format(library)))

    def run(self, token: Token, svc, env: Environment, params: dict = None) -> Any:
        """原子能力执行阶段"""
        if not params:
            params = {}

        src = token.value.get("src", "")
        project_id = token.value.get("__project_id__")

        if src in ["rpascript.script.Script().run", "rpascript.script.Script().module"]:
            # 有些原子能力需要当前的环境变量，打开这个提供整个环境变量处理
            params["__env__"] = env
            params["__project_id__"] = project_id
        if len(svc.line_debug) > 0 and svc.line_debug == "{}-{}".format(
            token.value.get("__process_id__"), token.value.get("__line__")
        ):
            # debug_line 单行调试
            params["__debug_line__"] = True
            svc.line_debug = ""

        keys = src.split("(")[0].split(".")

        imp = ".".join(keys[0:-1])
        imp_as = "__{}__".format("_".join(keys[0:-1]))
        func_name = src.replace(imp, imp_as, 1)  # 只替换第一个

        globals = env.to_dict(project_id)
        local = params

        if imp_as not in globals:
            # 这个会比较慢
            import_code = f"""{imp_as} = __importlib__.import_module('{imp}')""".strip()
            exec(import_code, globals, None)
            env.sync_with_dict(project_id, globals)  # 这个垮不了子流程

        func_params = ", ".join(f"{p}={p}" for p in params.keys())
        func_code = f"""{func_name}({func_params})""".strip()
        logger.info("atomic run: {}: local: {}".format(func_code, local))
        value = eval(func_code, globals, local)
        env.sync_with_dict(project_id, globals)
        return value
