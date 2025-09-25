import os
import platform

import requests

from ...logger import logger
from ...utils.pip import PipManager
from ...utils.utils import EmitType, emit_to_front


class Package:
    @staticmethod
    def get_atomic_packages(svc):
        """
        获取目前服务端控制升级的原子能力版本
        """
        url = "http://127.0.0.1:{}/api/update/v2/atom/pip_version?platform={}&arch={}".format(
            svc.route_port, platform.system(), platform.machine()
        )
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code != 200:
            return {}
        return response.json()

    @staticmethod
    def atomic_upload(svc):
        atom_packages = Package.get_atomic_packages(svc)
        logger.info("atom_packages: {}".format(atom_packages))

        # 1. 检查python_base是否存在
        exec_python = svc.config.app_server.python_base
        if not os.path.exists(exec_python):
            return

        installed_pck_info = PipManager.get_installed_packages(exec_python=exec_python)

        svc.pip_download_ing = False
        for atom_pck, atom_major_pub_list in atom_packages.items():
            atom_major_pub_list = atom_major_pub_list.strip().split(",")
            if "" in atom_major_pub_list:
                atom_major_pub_list.remove("")
            max_atom_major = atom_major_pub_list[-1]
            if atom_pck in installed_pck_info and max_atom_major == installed_pck_info[atom_pck]:
                continue
            update_pck_ver = f"{atom_pck}=={max_atom_major}"

            if not svc.pip_download_ing:
                emit_to_front(EmitType.TIP, msg={"msg": "原子能力静默更新中..."})
            svc.pip_download_ing = True

            try:
                try:
                    PipManager.download_pip(
                        package=update_pck_ver,
                        ver="",
                        mirror=svc.config.base_pipy_server.pypi_remote,
                    )
                except Exception as e:
                    # 如果下载不成功也应该不影响安装
                    pass
                if not svc.executor_mg.status():
                    # 没有运行的时候才安装
                    PipManager.install_pip(
                        package=atom_pck,
                        ver=max_atom_major,
                        exec_python=exec_python,
                        error_try=True,
                        mirror=svc.config.base_pipy_server.pypi_remote,
                    )
            except Exception as e:
                logger.error(f"{atom_pck} 安装失败: {e}")
