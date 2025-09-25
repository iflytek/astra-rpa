#!/usr/bin/env python3.6.5
# -*- coding: UTF-8 -*-
"""
Author: chaowang46
Date: 2024/10/8 14:59
docs:
"""

import argparse

from .browser import ExtensionManager
from .constants import OP, BrowserType

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", type=str, choices=["chrome", "edge", "firefox"], default="chrome")  # 指定浏览器
    parser.add_argument(
        "--op",
        type=str,
        choices=["install", "uninstall", "upgrade", "check"],
        default="install",
        help="指定操作",
    )
    args = parser.parse_args()
    browser = BrowserType.init(args.browser)
    op = OP.init(args.op)
    ex_manager = ExtensionManager(browser_type=browser)
    if op == OP.INSTALL:
        ex_manager.install()
    elif op == OP.UNINSTALL:
        ex_manager.uninstall()
    elif op == OP.CHECK:
        ex_manager.check()
