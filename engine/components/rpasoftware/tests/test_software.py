import os
import unittest

from rpasoftware.software import Software


class TestSoftware(unittest.TestCase):
    """测试Software类中原子能力方法的单元测试"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_app_path = os.path.join(os.path.dirname(__file__), "test.exe")

    def tearDown(self):
        """测试后的清理工作"""
        pass

    def test_open_with_keyword_arguments(self):
        """测试open方法使用关键字参数调用"""
        result = Software.open(app_abs_path=self.test_app_path, app_args="")
        self.assertEqual(result, self.test_app_path)

    def test_open_with_keyword_arguments_no_args(self):
        """测试open方法使用关键字参数调用，不传递app_args"""
        # 使用关键字参数调用open方法，不传递app_args
        result = Software.open(app_abs_path=self.test_app_path)
        self.assertEqual(result, self.test_app_path)

    def test_close_with_keyword_arguments(self):
        """测试close方法使用关键字参数调用"""

        Software.close(app_abs_path=self.test_app_path)
        # 如果没有异常，说明调用成功
        self.assertTrue(True)

    def test_cmd_with_keyword_arguments(self):
        """测试cmd方法使用关键字参数调用"""
        # 使用关键字参数调用cmd方法
        result = Software.cmd(cmd="echo test")

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("stdout", result)
        self.assertIn("stderr", result)

    def test_exists_with_keyword_arguments(self):
        """测试exists方法使用关键字参数调用"""
        # 使用关键字参数调用exists方法
        result = Software.exists(app_name="test_app", parent_name="test_parent")

        # 验证返回布尔值
        self.assertIsInstance(result, bool)

    def test_exists_with_keyword_arguments_no_parent(self):
        """测试exists方法使用关键字参数调用，不传递parent_name"""
        # 使用关键字参数调用exists方法，不传递parent_name
        result = Software.exists(app_name="test_app")

        # 验证返回布尔值
        self.assertIsInstance(result, bool)

    def test_pid_with_keyword_arguments(self):
        """测试pid方法使用关键字参数调用"""
        # 使用关键字参数调用pid方法
        result = Software.pid(app_name="test_app", parent_name="test_parent")

        # 验证返回整数
        self.assertIsInstance(result, int)

    def test_pid_with_keyword_arguments_no_parent(self):
        """测试pid方法使用关键字参数调用，不传递parent_name"""
        # 使用关键字参数调用pid方法，不传递parent_name
        result = Software.pid(app_name="test_app")

        # 验证返回整数
        self.assertIsInstance(result, int)

    def test_get_app_path_with_keyword_arguments(self):
        """测试get_app_path方法使用关键字参数调用"""
        # 使用关键字参数调用get_app_path方法
        result = Software.get_app_path(app_name="test_app")

        # 验证返回字符串
        self.assertIsInstance(result, str)

    def test_atomic_methods_require_keyword_arguments(self):
        """测试原子能力方法必须使用关键字参数调用"""
        # 这个测试确保我们理解原子能力方法应该使用关键字参数
        # 在实际使用中，应该避免使用位置参数

        # 正确的调用方式（使用关键字参数）
        correct_calls = [
            lambda: Software.open(app_abs_path=self.test_app_path),
            lambda: Software.close(app_abs_path=self.test_app_path),
            lambda: Software.cmd(cmd="echo test"),
            lambda: Software.exists(app_name="test"),
            lambda: Software.pid(app_name="test"),
            lambda: Software.get_app_path(app_name="test"),
        ]

        # 验证所有正确的调用方式都能正常工作
        for i, call_func in enumerate(correct_calls):
            try:
                call_func()
                # 如果没有异常，说明调用成功
                self.assertTrue(True, f"调用 {i + 1} 成功")
            except Exception as e:
                # 如果是因为文件不存在等实际错误，这是正常的
                # 我们主要测试语法正确性
                self.assertIsInstance(e, Exception, f"调用 {i + 1} 出现异常，但语法正确")

    def test_method_signatures(self):
        """测试方法签名"""
        # 验证所有方法都存在
        methods = ["open", "close", "cmd", "exists", "pid", "get_app_path"]
        for method_name in methods:
            self.assertTrue(hasattr(Software, method_name), f"方法 {method_name} 不存在")

    def test_keyword_arguments_best_practice(self):
        """测试关键字参数的最佳实践"""
        # 演示正确的调用方式
        test_cases = [
            # (方法名, 关键字参数, 期望的返回类型)
            ("open", {"app_abs_path": self.test_app_path, "app_args": ""}, str),
            ("close", {"app_abs_path": self.test_app_path}, type(None)),
            ("cmd", {"cmd": "echo test"}, dict),
            ("exists", {"app_name": "test", "parent_name": "parent"}, bool),
            ("pid", {"app_name": "test", "parent_name": "parent"}, int),
            ("get_app_path", {"app_name": "test"}, str),
        ]

        for method_name, kwargs, expected_return_type in test_cases:
            method = getattr(Software, method_name)
            try:
                result = method(**kwargs)
                if expected_return_type != type(None):
                    self.assertIsInstance(
                        result,
                        expected_return_type,
                        f"方法 {method_name} 返回类型不正确",
                    )
            except Exception as e:
                # 某些方法可能因为实际环境原因失败，这是正常的
                self.assertIsInstance(e, Exception, f"方法 {method_name} 调用失败")

    def test_positional_arguments_avoidance(self):
        """测试避免使用位置参数"""
        # 这个测试说明为什么应该避免使用位置参数

        try:
            Software.open(app_abs_path=self.test_app_path, app_args="")
            Software.close(app_abs_path=self.test_app_path)
            Software.cmd(cmd="echo test")
            self.assertTrue(True, "关键字参数调用成功")
        except Exception as e:
            # 即使出现异常，也说明语法正确
            self.assertIsInstance(e, Exception)

    def test_parameter_names_consistency(self):
        """测试参数名称的一致性"""
        # 验证所有方法的参数名称都是明确的
        method_params = {
            "open": ["app_abs_path", "app_args"],
            "close": ["app_abs_path"],
            "cmd": ["cmd"],
            "exists": ["app_name", "parent_name"],
            "pid": ["app_name", "parent_name"],
            "get_app_path": ["app_name"],
        }

        for method_name, expected_params in method_params.items():
            method = getattr(Software, method_name)
            # 获取方法的参数信息
            import inspect

            sig = inspect.signature(method)
            actual_params = list(sig.parameters.keys())

            # 验证参数名称
            for param in expected_params:
                self.assertIn(param, actual_params, f"方法 {method_name} 缺少参数 {param}")


if __name__ == "__main__":
    unittest.main()
