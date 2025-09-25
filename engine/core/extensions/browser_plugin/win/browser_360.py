import getpass
import subprocess
import winreg

from ..constants import PluginData, PluginStatus
from ..core import PluginManagerCore
from ..utils.win import Registry, check_chrome_plugin, kill_process


class Browser360PluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\360\360se6\Chrome"
        # 360 用户偏好文件地址
        self.preferences_path_list = [
            r"C:\Users\{}\AppData\Local\360Chrome\Chrome\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Local\360Chrome\Chrome\User Data\Profile 1\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Roaming\360se6\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Roaming\360se6\User Data\Default\Profile 1\Preferences".format(getpass.getuser()),
        ]

    @staticmethod
    def get_browser_path():
        """
        获取可执行文件路径
        """
        try:
            # 打开注册表中的路径
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\360se6.exe"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            # 读取默认值，这通常是可执行文件的完整路径
            value, _ = winreg.QueryValueEx(key, "")
            return value
        except FileNotFoundError:
            try:
                # 打开注册表中的路径
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\360se6.exe"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
                # 读取默认值，这通常是可执行文件的完整路径
                value, _ = winreg.QueryValueEx(key, "")
                return value
            except FileNotFoundError:
                raise FileNotFoundError("360 is not installed or the registry key is not found.")

    def check_browser(self):
        # 通过检查注册表来判断浏览器是否存在
        return Registry.exist(self.browser_path)

    def check_plugin(self):
        installed, installed_version = check_chrome_plugin(self.preferences_path_list, self.plugin_data.plugin_id)

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
        )

    def close_browser(self):
        kill_process("360se")

    def install_plugin(self):
        browser_path = self.get_browser_path()
        command = [browser_path, self.plugin_data.plugin_path]
        # 启动进程
        subprocess.Popen(command)
