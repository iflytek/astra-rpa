from abc import ABC, abstractmethod

from .constants import BrowserType, PluginData, PluginStatus


class PluginManagerCore(ABC):
    @abstractmethod
    def check_browser(self) -> bool:
        """
        检查浏览器是否安装
        :return:
        """
        pass

    @abstractmethod
    def check_plugin(self) -> PluginStatus:
        """
        检查插件的安装状态
        """
        pass

    @abstractmethod
    def install_plugin(self):
        """
        安装插件
        """
        pass

    @abstractmethod
    def close_browser(self):
        """
        关闭浏览器
        """
        pass


class PluginManager(ABC):
    @staticmethod
    @abstractmethod
    def get_support_browser() -> list[BrowserType]:
        """
        获取支持的浏览器类型
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        """
        获取插件管理器
        :param plugin_data: 插件信息
        :param browser_type: 浏览器类型
        :return:
        """
        pass
