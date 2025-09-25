#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RPA Setup 启动脚本
最外层启动脚本，用于启动 scheduler 模块
"""

import os
import pathlib
import sys

print("cwd :", os.getcwd())
print("__file__:", pathlib.Path(__file__).resolve())

import argparse
import os
import subprocess
import sys


def main():
    # 获取项目根目录
    project_root = os.getcwd()
    print("project_root :", project_root)
    # scheduler_path = os.path.join(project_root, "engine", "core", "servers", "scheduler", "start.py")

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="RPA Scheduler 启动脚本")
    parser.add_argument(
        "--conf",
        type=str,
        default=os.path.join(project_root, "resources", "conf.json"),
        help="配置文件路径",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default="START",
        choices=["START", "STOP"],
        help="启动模式",
    )
    args = parser.parse_args()

    # 构建配置文件路径
    conf_path = os.path.abspath(args.conf)

    # 设置PYTHONPATH环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    # 使用 -m 调用scheduler模块
    cmd = [
        sys.executable,
        "-m",
        "engine.core.servers.scheduler.start",
        "--conf",
        conf_path,
    ]

    # cmd = [sys.executable, scheduler_path, "--conf", conf_path]

    try:
        subprocess.run(cmd, check=True, env=env, cwd=project_root)
    except subprocess.CalledProcessError as e:
        print(f"启动scheduler失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
