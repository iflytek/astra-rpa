from ..constants import BrowserType, PluginData
from ..core import PluginManager, PluginManagerCore
from .chromium import ChromiumPluginManager
from .firefox import FirefoxPluginManager


class BrowserPluginFactory(PluginManager):
    @staticmethod
    def get_support_browser():
        return [
            BrowserType.CHROME,
            BrowserType.FIREFOX,
            BrowserType.MICROSOFT_EDGE,
        ]

    @staticmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        if browser_type == BrowserType.CHROME:
            return ChromiumPluginManager(
                plugin_data,
                root_path="/opt/google/chrome",
                browser_name="google-chrome",
                process_name="chrome",
            )
        elif browser_type == BrowserType.MICROSOFT_EDGE:
            return ChromiumPluginManager(
                plugin_data,
                root_path="/usr/share/microsoft-edge",
                browser_name="microsoft-edge",
                process_name="msedge",
            )
        elif browser_type == BrowserType.FIREFOX:
            return FirefoxPluginManager(plugin_data)
        elif browser_type == BrowserType.BROWSER_360:
            return ChromiumPluginManager(
                plugin_data,
                root_path="/opt/browser360",
                browser_name="browser360-cn",
                process_name="browser360",
            )
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
