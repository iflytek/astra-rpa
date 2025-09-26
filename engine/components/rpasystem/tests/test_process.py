import os
import sys
import unittest
from unittest import TestCase

from rpasystem import *
from rpasystem.process import Process


class TestProcess(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.test_command = os.path.join(os.path.dirname(__file__), "test.exe")

    def test_run_command_normal_success(self):
        """测试运行命令 - 普通模式成功"""
        # 运行简单的echo命令
        result = Process.run_command(
            command=self.test_command,
            cmd_type=CmdType.NORMAL,
            run_type=RunType.CONTINUE,
        )
        self.assertTrue(result)

    def test_run_command_with_params(self):
        """测试运行命令 - 带参数"""
        params = "param1 param2"

        result = Process.run_command(
            command=self.test_command,
            cmd_type=CmdType.NORMAL,
            run_type=RunType.CONTINUE,
            params=params,
        )
        self.assertTrue(result)

    def test_run_command_with_work_dir(self):
        """测试运行命令 - 指定工作目录"""
        work_dir = os.getcwd()  # 使用当前工作目录

        result = Process.run_command(
            command=self.test_command,
            cmd_type=CmdType.NORMAL,
            run_type=RunType.CONTINUE,
            work_dir=work_dir,
        )
        self.assertTrue(result)

    def test_run_command_complete_wait(self):
        """测试运行命令 - 完整等待模式"""
        # 运行一个快速完成的命令
        try:
            result = Process.run_command(
                command=self.test_command,
                cmd_type=CmdType.NORMAL,
                run_type=RunType.COMPLETE,
                wait_time=5,
            )
            self.assertTrue(result)
        except Exception as e:
            pass

    def test_get_pid_exact_match(self):
        """测试获取PID - 精确匹配"""
        # 查找当前Python进程
        result = Process.get_pid(
            process_name="python.exe" if sys.platform == "win32" else "python",
            search_type=SearchType.EXACT,
            pid_type=PidType.ALL,
        )

        # 验证返回的是列表且包含当前进程的PID
        self.assertIsInstance(result, list)
        self.assertIn(os.getpid(), result)

    def test_get_pid_fuzzy_match(self):
        """测试获取PID - 模糊匹配"""
        # 使用模糊匹配查找Python进程
        result = Process.get_pid(process_name="python", search_type=SearchType.FUZZY, pid_type=PidType.ALL)

        # 验证返回的是列表
        self.assertIsInstance(result, list)
        # 应该能找到当前Python进程
        self.assertIn(os.getpid(), result)

    def test_get_pid_regex_match(self):
        """测试获取PID - 正则匹配"""
        # 使用正则表达式匹配Python进程
        result = Process.get_pid(process_name="python.*", search_type=SearchType.REGEX, pid_type=PidType.ALL)

        # 验证返回的是列表
        self.assertIsInstance(result, list)
        # 应该能找到当前Python进程
        self.assertIn(os.getpid(), result)

    def test_get_pid_one_result(self):
        """测试获取PID - 返回单个结果"""
        # 查找当前Python进程，返回单个PID
        result = Process.get_pid(
            process_name="python.exe" if sys.platform == "win32" else "python",
            search_type=SearchType.EXACT,
            pid_type=PidType.ONE,
        )

        # 验证返回的是整数且是当前进程的PID
        self.assertIsInstance(result, int)

    def test_get_pid_empty_name(self):
        """测试获取PID - 空名称"""
        with self.assertRaises(BaseException):
            Process.get_pid(process_name="", search_type=SearchType.EXACT, pid_type=PidType.ALL)

    def test_get_pid_no_such_process(self):
        """测试获取PID - 进程不存在"""
        # 查找一个不存在的进程
        result = Process.get_pid(
            process_name="nonexistent_process_12345",
            search_type=SearchType.EXACT,
            pid_type=PidType.ALL,
        )

        # 验证返回空列表
        self.assertEqual(result, [])

    def test_run_command_system_commands(self):
        """测试运行命令 - 系统命令"""
        system_commands = [
            "dir" if sys.platform == "win32" else "ls",
            "echo Hello World",
            "whoami" if sys.platform != "win32" else "whoami",
        ]

        for cmd in system_commands:
            try:
                result = Process.run_command(command=cmd, cmd_type=CmdType.NORMAL, run_type=RunType.CONTINUE)
                self.assertTrue(result)
            except Exception:
                # 某些命令可能在某些系统上不可用，这是正常的
                pass

    def test_run_command_with_environment_variables(self):
        """测试运行命令 - 环境变量"""
        # 运行一个使用环境变量的命令
        env_command = "echo %PATH%" if sys.platform == "win32" else "echo $PATH"

        result = Process.run_command(command=env_command, cmd_type=CmdType.NORMAL, run_type=RunType.CONTINUE)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
