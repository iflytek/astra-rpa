import subprocess
import winreg

from ..constants import PluginData, PluginStatus
from ..core import PluginManagerCore
from ..utils import FirefoxUtils
from ..utils.win import Registry, kill_process

# 自动安装 firefox 插件的方式
# 1. 使用配置文件的方式（在 Firefox 中，输入 about:profiles 查看配置文件）
# 2. 使用命令行的方式（firefox xxxx.xpi）


class FirefoxPluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data
        self.browser_path = r"Software\Google\Chrome"

    @staticmethod
    def get_browser_path():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Mozilla\\Mozilla Firefox") as key:
                # 获取当前安装的版本
                version, _ = winreg.QueryValueEx(key, "CurrentVersion")
                # 使用版本信息获取安装路径
                with winreg.OpenKey(key, f"{version}\\Main") as main_key:
                    path, _ = winreg.QueryValueEx(main_key, "PathToExe")
                    return path
        except FileNotFoundError:
            raise FileNotFoundError("安装此插件前，请确保本地已安装Firefox浏览器。")

    def check_browser(self):
        # 通过检查注册表来判断浏览器是否存在
        return Registry.exist(self.browser_path)

    def check_plugin(self):
        installed, installed_version = FirefoxUtils.check()

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
        )

    def close_browser(self):
        kill_process("firefox")

    def install_plugin(self):
        # 1. 使用配置文件安装插件的方式
        # default_profile_path = FirefoxRegistry.get_default_profile_path()
        # extensions_path = os.path.join(default_profile_path, "extensions")
        #
        # # 创建 extensions 文件夹（如果不存在）
        # os.makedirs(extensions_path, exist_ok=True)
        #
        # # 复制扩展文件到 extensions 文件夹
        # shutil.copy(extension_xpi, extensions_path)
        #
        # print(f"已将扩展复制到 {extensions_path}")

        # 2. 使用命令行安装
        firefox_path = self.get_browser_path()
        command = [firefox_path, self.plugin_data.plugin_path]
        # 启动进程
        process = subprocess.Popen(command)

        print("Firefox 已启动：{0}".format(process.pid))
