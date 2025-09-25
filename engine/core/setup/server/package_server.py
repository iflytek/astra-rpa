# import json
# import platform
import os
import sys

# import time
# import requests
from setup.config import config

# from setup.logger import logger
from setup.utils.subprocess import SubPopen


# from setup.utils.utils import emit_to_front
# from setup.utils.utils import EmitType
# from setup.utils.pip import PipManager
#
#
class Package:
    # @staticmethod
    # def get_core_packages():
    #     """
    #     获取当前版本核心组件依赖的版本
    #     """
    #     url = "{}/api/update/v2/core/pip_version?platform={}&arch={}".format(config.REMOTE_ADDR, platform.system(), platform.machine())
    #     response = requests.get(url, timeout=5, verify=False)
    #     return response.json()

    @staticmethod
    def core_package_start():
        cmd = [
            sys.executable,
            os.path.join(os.getcwd(), "src", "scheduler", "start.py"),
            "--conf={}".format(config.CONF_FILE),
        ]
        print(cmd)
        SubPopen(name="scheduler", cmd=cmd).run()

    #     """
    #     开始任务
    #     """
    #     logger.info("starting core_start component...")
    #     end_stp = 90
    #     c_stp = 60
    #     try:
    #         # 包检测并下载
    #         packages = Package.get_core_packages()
    #         logger.info("required core component res: {}".format(json.dumps(packages)))
    #
    #         stp = float(float(end_stp - c_stp) / 2 / len(packages))
    #
    #         for pck, ver in packages.items():
    #             logger.info("package update: {} {}".format(pck, ver))
    #
    #             now_ver = PipManager.local_packages_version(pck)
    #             if not now_ver or now_ver != ver:
    #                 c_stp += stp
    #                 emit_to_front(EmitType.SYNC, {
    #                     "msg": "核心热更新加载中",
    #                     "step": int(c_stp),
    #                 })
    #                 try:
    #                     PipManager.download_pip(pck, ver, mirror=config.PYPI_SERVER_REMOTE)
    #                 except Exception as e:
    #                     # 下载错误也不影响，决定作用的还是安装
    #                     logger.info("package download_pip error: ".format(e))
    #
    #                 c_stp += stp
    #                 emit_to_front(EmitType.SYNC, {
    #                     "msg": "核心热更新安装中",
    #                     "step": int(c_stp),
    #                 })
    #                 PipManager.install_pip(pck, ver, pip_cache_dir=config.PIP_CACHE_DIR, error_try=True, mirror=config.PYPI_SERVER_REMOTE)
    #
    #                 # 如果是本身更新，将重新启动rpa-setup [废弃 setup没有任何业务，无影响, 重新打开即可]
    #                 # if pck == "rpa-setup":
    #                 #     # 如果rpa-setup更新，将重新启动rpa-setup
    #             else:
    #                 c_stp += stp
    #                 c_stp += stp
    #     except Exception as e:
    #         logger.error("package error: {}".format(e))
    #         emit_to_front(EmitType.TIP, {
    #             "msg": "组件更新失败",
    #             "type": "error"
    #         })
    #     finally:
    #         emit_to_front(EmitType.SYNC, {
    #             "msg": "核心检测完成",
    #             "step": end_stp,
    #         })
    #         cmd = [sys.executable, "-m", "scheduler", "--conf={}".format(config.CONF_FILE)]
    #         SubPopen(name="scheduler", cmd=cmd).run()


#
#     @staticmethod
#     def core_package_upload():
#         logger.info("starting core_upload component...")
#         while True:
#             time.sleep(60)
#             try:
#                 packages = Package.get_core_packages()
#                 for pck, ver in packages.items():
#                     now_ver = PipManager.local_packages_version(pck)
#                     if not now_ver or now_ver != ver:
#                         logger.info("package upload version mismatch {}!={}".format(pck, ver))
#                         PipManager.download_pip(pck, ver, mirror=config.PYPI_SERVER_REMOTE)
#             except Exception as e:
#                 logger.error("download new core component error: {}".format(str(e)))
