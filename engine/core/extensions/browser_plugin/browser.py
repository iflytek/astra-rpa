#!/usr/bin/env python3.6.5
# -*- coding: UTF-8 -*-
"""
Author: chaowang46
Date: 2024/9/30 15:30
docs:
"""

import os
import sys

from .constants import BrowserType, PluginData
from .utils import parse_filename_regex

if sys.platform == "win32":
    from .win import BrowserPluginFactory
elif sys.platform == "linux":
    from .unix import BrowserPluginFactory


class ExtensionManager(object):
    def __init__(self, browser_type: BrowserType = BrowserType.CHROME):
        self.browser_type = browser_type

        current_directory = os.path.dirname(os.path.abspath(__file__))
        plugin_dir = os.path.join(current_directory, "plugins")
        browser_name = self.browser_type.value.lower()

        public_chrom_plugin = tuple(name.value.lower() for name in (BrowserType.CHROME, BrowserType.MICROSOFT_EDGE))
        pre_name = "chrome" if browser_name in public_chrom_plugin else browser_name
        plugins = [file for file in os.listdir(plugin_dir) if file.startswith(pre_name + "-")]

        if not plugins:
            raise Exception("插件不存在安装失败...")

        # 提取文件名中的参数
        plugin_name, plugin_version, plugin_id, _extension = parse_filename_regex(plugins[-1])

        self.plugin_data = PluginData(
            plugin_path=os.path.join(os.getcwd(), plugin_dir, plugins[-1]),
            plugin_id=plugin_id,
            plugin_version=plugin_version,
            plugin_name=plugin_name,
        )

        self.browser_plugin_manager = BrowserPluginFactory.get_plugin_manager(browser_type, self.plugin_data)

    @staticmethod
    def get_support():
        """
        获取支持的浏览器
        :return:
        """
        return BrowserPluginFactory.get_support_browser()

    def close_browser(self):
        """
        关闭浏览器
        :return:
        """
        self.browser_plugin_manager.close_browser()

    def check_status(self):
        """
        检测插件的状态
        :return: 插件是否安装，是否需要更新，当前版本，最新版本
        """

        return self.browser_plugin_manager.check_plugin()

    def install(self):
        """
        安装插件
        """
        return self.browser_plugin_manager.install_plugin()

    def uninstall(self):
        """
        卸载插件
        """
        pass

    def upgrade(self):
        """
        升级插件
        """
        return self.install()

    def check_browser(self):
        """
        检测浏览器是否安装
        """
        return self.browser_plugin_manager.check_browser()
