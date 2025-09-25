#!/usr/bin/env python3.6.5
# -*- coding: UTF-8 -*-
"""
Author: chaowang46
Date: 2024/10/8 14:58
docs:
"""

import configparser
import json
import os
import platform
import re
import subprocess


def parse_filename_regex(filename):
    # 正则表达式匹配模式
    pattern = (
        r"^(?P<browser>[a-zA-Z0-9-]+)-(?P<version>\d+(\.\d+)*)-(?P<hashid>[a-zA-Z0-9]+)\.(?P<extension>[a-zA-Z]+)$"
    )
    match = re.match(pattern, filename)
    if match:
        # 使用命名捕获组来提取各部分
        browser = match.group("browser")
        version = match.group("version")
        hashid = match.group("hashid")
        extension = match.group("extension")
        return browser, version, hashid, extension
    else:
        raise ValueError("Filename does not match expected pattern")


class FirefoxUtils:
    firefox_plugin_id = "iflyrpa@iflytek.com"

    @staticmethod
    def get_firefox_command():
        try:
            """
            检查系统上是否安装了Firefox或Firefox ESR。

            返回:
                bool: 如果安装了Firefox或Firefox ESR则返回True，否则返回False。
            """
            # 可能的Firefox二进制文件名列表
            firefox_versions = ["firefox", "firefox-esr"]

            # 遍历每个版本并检查是否安装
            for version in firefox_versions:
                result = subprocess.run(["which", version], capture_output=True, text=True)
                # 检查'which'命令是否找到了二进制文件
                if result.returncode == 0:
                    return version

        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def get_default_profile_path(firefox_command="firefox"):
        """
        获取 Firefox 配置文件路径
        :return:
        """
        if platform.system() == "Windows":
            profile_path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox")
        elif platform.system() == "Darwin":  # macOS
            profile_path = os.path.expanduser("~/Library/Application Support/Firefox")
        else:  # Linux
            profile_path = os.path.expanduser("~/.mozilla/{0}".format(firefox_command))

        # 找到默认配置文件夹
        config = configparser.ConfigParser()
        config.read(os.path.join(profile_path, "installs.ini"))
        sections = config.sections()
        # 检查是否有任何 section 存在
        if sections:
            default_profile = config[sections[0]]["Default"]
            return os.path.join(profile_path, default_profile)
        else:
            raise FileNotFoundError("没有找到默认配置文件。请确保已创建 Firefox 配置文件。")

    @staticmethod
    def check(firefox_command="firefox"):
        """
        检查插件是否安装, 并返回插件的版本号
        :return:
        """
        try:
            default_profile_path = FirefoxUtils.get_default_profile_path(firefox_command)
            # extensions.json 文件中保存了插件的相关信息
            extensions_path = os.path.join(default_profile_path, "extensions.json")
            if os.path.exists(extensions_path):
                with open(extensions_path, "r", encoding="utf8") as f:
                    dict_msg = json.loads(f.read())
                    for addon in dict_msg["addons"]:
                        if addon["id"] == FirefoxUtils.firefox_plugin_id:
                            return True, addon["version"]
                    return False, None
            else:
                return False, None
        except FileNotFoundError:
            return False, None
