import win32con

from rpasoftware.core import ISoftwareCore
from rpasoftware.regedit_win import Regedit


class SoftwareCore(ISoftwareCore):
    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        return SoftwareCore.get_app_path_by_regedit(app_name)

    @staticmethod
    def get_app_path_by_regedit(app_name: str = "") -> str:
        """通过注册表查找软件地址"""

        try:
            key = Regedit(
                r"Software\Microsoft\Windows\CurrentVersion\App Paths",
                win32con.HKEY_LOCAL_MACHINE,
                "r",
            )
            path = getattr(key, app_name)[None]
        except Exception as e:
            try:
                key = Regedit(
                    r"Software\Microsoft\Windows\CurrentVersion\App Paths",
                    win32con.HKEY_CURRENT_USER,
                    "r",
                )
                path = getattr(key, app_name)[None]
            except Exception as e:
                return ""
        return path
