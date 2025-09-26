import os
import subprocess
import sys

from ...logger import logger
from ...utils.pip import PipManager
from ...utils.utils import EmitType, emit_to_front


def repair_pywin32_dependence(svc):
    """
    修复部分机器pywin32依赖缺失，无法引入，导致拾取组件无法使用bug，直接使用动态修复方法，如果环境依赖缺失将动态下载, win32_repair包然后执行修复
    """
    if sys.platform != "win32":
        return

    version = PipManager.local_packages_version("pywin32")
    if not version:
        return
    try:
        pass
    except Exception as e:
        emit_to_front(
            EmitType.SYNC,
            msg={
                "msg": "系统依赖缺失，执行修复中...",
                "step": 95,  # 进度条 90-100之间可选
            },
        )
        try:
            PipManager.download_pip(
                "win32_repair",
                ver="",
                mirror=svc.config.base_pipy_server.pypi_remote,
            )
            PipManager.install_pip(
                "win32_repair",
                ver="",
                mirror=svc.config.base_pipy_server.pypi_remote,
            )
            command = [
                sys.executable,
                "-m",
                "win32_repair",
                '--work_dir="{}"'.format(os.getcwd()),
            ]
            result = subprocess.run(command, check=True)
            if result.returncode == 0:
                logger.info("pywin32扩展安装成功")
            else:
                raise Exception("pywin32扩展安装失败!")
        except Exception as e:
            emit_to_front(
                EmitType.TIP,
                {
                    "msg": "系统依赖修复失败",
                    "type": "error",
                },
            )
        else:
            emit_to_front(EmitType.TIP, {"msg": "系统依赖修复成功", "type": "tip"})


def linux_env_check():
    """linux环境检测"""
    if sys.platform == "win32":
        return

    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.interface",
                "toolkit-accessibility",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() != "true":
            emit_to_front(
                EmitType.ALERT,
                msg={"msg": "首次安装，请手动重启电脑后重启打开", "type": "normal"},
            )

            # 环境写入
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.desktop.interface",
                    "toolkit-accessibility",
                    "true",
                ],
                check=True,
            )
            # qt写入
            result = subprocess.run(
                ["grep", "^export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1", "/etc/profile"],
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip() != "export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1":
                subprocess.run(
                    [
                        "sudo",
                        "sh",
                        "-c",
                        'echo "export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1" >> /etc/profile',
                    ],
                    check=True,
                )
    except subprocess.CalledProcessError as e:
        pass
