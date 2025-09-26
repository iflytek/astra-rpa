import os
import re
import sys

from ...logger import logger
from ...utils.subprocess import SubPopen


class VenvManager:
    @staticmethod
    def list_temp_venvs(svc):
        """
        枚举素有的虚拟环境
        """
        res = list()
        if not os.path.exists(svc.config.app_server.venv_base_dir):
            return res
        for temp_venv in os.listdir(svc.config.app_server.venv_base_dir):
            if re.search(r"^temp_venv\d+$", temp_venv):
                res.append(temp_venv)
        res.sort()
        return res

    @staticmethod
    def list_project_venvs(self):
        """
        获取所有的工程虚拟环境
        """
        project_venv_list = list()
        if not os.path.exists(self.svc.config.app_server.venv_base_dir):
            return project_venv_list
        for venv in os.listdir(self.svc.config.app_server.venv_base_dir):
            if re.search(r"^\d+$", venv):
                project_venv_list.append(os.path.join(self.svc.config.app_server.venv_base_dir, venv))
        return project_venv_list

    @staticmethod
    def remove_temp_venv(svc):
        venvs_path = svc.config.app_server.venv_base_dir
        if not os.path.exists(venvs_path):
            os.makedirs(venvs_path)

        files = os.listdir(venvs_path)
        for file_name in files:
            if file_name.startswith("."):
                try:
                    # os.remove 无法删除.文件
                    if sys.platform == "win32":
                        os.system("rd /s/q {}".format(os.path.join(venvs_path, file_name)))
                    else:
                        os.system("rm -rf {}".format(os.path.join(venvs_path, file_name)))
                except Exception as e:
                    pass
            if not os.path.exists(os.path.join(venvs_path, file_name, "venv")):
                try:
                    # os.remove 无法删除.文件
                    if sys.platform == "win32":
                        os.system("rd /s/q {}".format(os.path.join(venvs_path, file_name)))
                    else:
                        os.system("rm -rf {}".format(os.path.join(venvs_path, file_name)))
                except Exception as e:
                    pass

    @staticmethod
    def create_new(svc, temp_venv_maxsize=1):
        """
        穿件一个新的工程运行的venv
        """

        # 1. 清空temp_venv保证是最新的
        VenvManager.remove_temp_venv(svc)
        temp_venv_list = VenvManager.list_temp_venvs(svc)
        if len(temp_venv_list) >= temp_venv_maxsize:
            return

        # 2. 虚拟环创建
        logger.info("create new venv...")

        # 2.1 名称获取
        temp_venv_num_start = 1
        if temp_venv_list:
            temp_venv_num_start = int(temp_venv_list[-1].split("temp_venv")[-1]) + 1
        env_dir_parent = os.path.join(
            svc.config.app_server.venv_base_dir,
            ".temp_venv{}".format(temp_venv_num_start),
        )
        env_dir_temp = os.path.join(env_dir_parent, "venv")

        # 2.2 创建虚拟环境
        cmd = [
            svc.config.app_server.python_base,
            "-m",
            "venv",
            env_dir_temp,
            "--system-site-packages",
        ]
        _, err = SubPopen(name="create_venv", cmd=cmd).run(log=True, encoding=None).logger_handler()
        if err:
            logger.error("create venv failed: {}".format(err))

        # 2.3 修改pyvenv.cfg
        pyvenv_cfg = os.path.join(env_dir_temp, "pyvenv.cfg")
        if not os.path.exists(pyvenv_cfg):
            if sys.platform == "win32":
                os.system("rd /s/q {}".format(env_dir_parent))
            else:
                os.system("rm -rf {}".format(env_dir_parent))
            return
        with open(pyvenv_cfg) as file:
            pyvenv_cfg_content = file.read()
        pyvenv_cfg_content = pyvenv_cfg_content.replace(
            "include-system-site-packages = false",
            "include-system-site-packages = true",
        )
        with open(pyvenv_cfg, "w") as file:
            file.write(pyvenv_cfg_content)

        # 2.4 .temp_venv重命名成temp_venv
        os.rename(
            env_dir_parent,
            os.path.join(
                svc.config.app_server.venv_base_dir,
                "temp_venv{}".format(temp_venv_num_start),
            ),
        )


def create_project_venv(svc, project_id: str):
    """
    创建一个工程的虚拟环境
    """
    temp_envs = VenvManager.list_temp_venvs(svc)
    v_path = os.path.join(svc.config.app_server.venv_base_dir, project_id)
    if not os.path.exists(v_path):
        if not temp_envs:
            raise Exception("empty venv runtime...")
        temp_v = temp_envs[0]
        os.rename(os.path.join(svc.config.app_server.venv_base_dir, temp_v), v_path)
