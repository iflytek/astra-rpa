#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rpasystem.core.process_core import ProcessCoreWin


def test_basic_commands():
    """测试基本命令执行"""
    print("=== 测试基本命令执行 ===")

    # 测试简单命令
    try:
        result = ProcessCoreWin.run_cmd_safe("echo Hello World")
        print(f"echo命令结果: {result}")
    except Exception as e:
        print(f"echo命令失败: {e}")

    # 测试dir命令
    try:
        result = ProcessCoreWin.run_cmd_safe("dir")
        print(f"dir命令成功: {result['success']}")
        print(f"输出长度: {len(result['stdout'])}")
    except Exception as e:
        print(f"dir命令失败: {e}")

    # 测试带工作目录的命令
    try:
        current_dir = os.getcwd()
        result = ProcessCoreWin.run_cmd_safe("pwd", cwd=current_dir)
        print(f"pwd命令结果: {result}")
    except Exception as e:
        print(f"pwd命令失败: {e}")


def test_process_creation():
    """测试进程创建"""
    print("\n=== 测试进程创建 ===")

    try:
        process = ProcessCoreWin.run_cmd("echo Test Process")
        print(f"进程创建成功，PID: {process.pid}")

        # 等待进程完成
        stdout, stderr = process.communicate()
        print(f"进程输出: {stdout.decode('utf-8', errors='ignore')}")
        print(f"进程错误: {stderr.decode('utf-8', errors='ignore')}")
        print(f"返回码: {process.returncode}")
    except Exception as e:
        print(f"进程创建失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")

    # 测试空命令
    try:
        ProcessCoreWin.run_cmd_safe("")
    except ValueError as e:
        print(f"空命令错误处理正确: {e}")

    # 测试不存在的目录
    try:
        ProcessCoreWin.run_cmd_safe("dir", cwd="C:/不存在的目录")
    except ValueError as e:
        print(f"不存在目录错误处理正确: {e}")

    # 测试无效命令
    try:
        result = ProcessCoreWin.run_cmd_safe("invalid_command_12345")
        print(f"无效命令返回码: {result['returncode']}")
        print(f"无效命令错误输出: {result['stderr']}")
    except Exception as e:
        print(f"无效命令异常: {e}")


if __name__ == "__main__":
    print("开始测试 ProcessCoreWin...")
    test_basic_commands()
    test_process_creation()
    test_error_handling()
    print("\n测试完成！")
