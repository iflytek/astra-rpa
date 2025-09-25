#!/usr/bin/env python3.6.5
# -*- coding: UTF-8 -*-
"""
Author: chaowang46
Date: 2024/10/8 15:01
docs:
"""

from dataclasses import dataclass
from enum import Enum


class BrowserType(Enum):
    CHROME = "CHROME"
    MICROSOFT_EDGE = "MICROSOFT_EDGE"
    FIREFOX = "FIREFOX"
    BROWSER_360 = "360"
    BROWSER_360X = "360X"

    @classmethod
    def init(cls, name: str):
        name = name.upper()
        return cls(name)


class OP(Enum):
    INSTALL = "INSTALL"
    UNINSTALL = "UNINSTALL"
    UPGRADE = "UPGRADE"
    CHECK = "CHECK"

    @classmethod
    def init(cls, name: str):
        name = name.upper()
        return cls(name)


@dataclass
class PluginStatus:
    """
    插件的安装状态
    """

    installed: bool = False  # 插件是否安装
    latest: bool = False  # 插件是否是最新版本
    installed_version: str = None  # 插件安装的版本
    latest_version: str = None  # 插件最新版本


@dataclass
class PluginData:
    """
    插件的相关数据
    """

    plugin_path: str = None  # 插件的路径
    plugin_name: str = None  # 插件的名称
    plugin_id: str = None  # 插件的id
    plugin_version: str = None  # 插件的版本


if __name__ == "__main__":
    print(BrowserType.init("chrome"))
