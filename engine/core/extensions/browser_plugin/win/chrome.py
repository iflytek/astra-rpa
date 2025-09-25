import getpass

from rpaframe.logger import logger

from ..constants import PluginData, PluginStatus
from ..core import PluginManagerCore
from ..utils.win import (
    Registry,
    check_chrome_plugin,
    kill_process,
    remove_browser_setting,
)
from ..win.reg import run_reg_file


class ChromePluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\Google\Chrome"
        self.extension_path = f"{self.browser_path}\\Extensions\\{plugin_data.plugin_id}"
        self.preferences_path_list = [
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Profile 1\Preferences".format(getpass.getuser()),
        ]
        self.secure_preferences = (
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences".format(getpass.getuser())
        )

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
        kill_process("chrome")

    def install_plugin(self):
        self.close_browser()
        remove_browser_setting(
            preferences_path_list=self.preferences_path_list,
            secure_preferences=self.secure_preferences,
            extension_id=self.plugin_data.plugin_id,
        )

        Registry.create(self.extension_path)
        Registry.add_string_value(self.extension_path, "path", self.plugin_data.plugin_path)
        Registry.add_string_value(self.extension_path, "version", self.plugin_data.plugin_version)

        # https://chromeenterprise.google/policies/?policy=ExtensionInstallAllowlist
        try:
            # 插件未发布，这个去掉这个警告
            if not Registry.exist(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist"):
                Registry.create(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist")
            Registry.add_string_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist",
                "2",
                self.plugin_data.plugin_id,
            )

            # if not Registry.exist(r"SOFTWARE\Policies\Google\Chrome\ExtensionManifestV2Availability"):
            #     Registry.create(r"SOFTWARE\Policies\Google\Chrome\ExtensionManifestV2Availability")
            # # 设置 value 为dword:00000002
            # Registry.add_dword_value(r"SOFTWARE\Policies\Google\Chrome\ExtensionManifestV2Availability", "1", 2)
            logger.info("设置插件白名单成功")
        except Exception as e:
            logger.error(f"设置插件白名单失败: {e}")
            self.register_policy()
            pass

    def register_policy(self):
        logger.info("手动添加注册表")
        return run_reg_file(self.plugin_data.plugin_id)
