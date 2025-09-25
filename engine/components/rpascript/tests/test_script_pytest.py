#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用pytest的测试文件
展示如何使用fixture来减少mock的使用
"""

import pytest
from rpascript.script import Script


class TestScriptModulePytest:
    """使用pytest测试Script.module原子能力"""

    def test_module_with_main_function(self, basic_env, sample_script_content):
        """测试包含main函数的脚本执行"""
        result = Script.module(content=sample_script_content, __env__=basic_env)

        expected = {"result": "value1_value2", "status": "success"}
        assert result == expected

    def test_module_without_main_function(self, basic_env, no_main_script_content):
        """测试不包含main函数的脚本执行"""
        result = Script.module(content=no_main_script_content, __env__=basic_env)

        assert result is None

    def test_module_with_mathematical_operations(self, math_env, math_script_content):
        """测试数学运算脚本"""
        result = Script.module(content=math_script_content, __env__=math_env)

        expected = {"sum": 13, "product": 30, "difference": 7, "quotient": 10 / 3}
        assert result == expected

    def test_module_with_list_operations(self, list_env, list_script_content):
        """测试列表操作脚本"""
        result = Script.module(content=list_script_content, __env__=list_env)

        expected = {"result": [1, 1, 3, 4, 5]}
        assert result == expected

    def test_module_with_string_operations(self, string_env, string_script_content):
        """测试字符串操作脚本"""
        result = Script.module(content=string_script_content, __env__=string_env)

        expected = {"result": "HELLO WORLD"}
        assert result == expected

    def test_module_with_conditional_logic(self, grade_env, grade_script_content):
        """测试条件逻辑脚本"""
        result = Script.module(content=grade_script_content, __env__=grade_env)

        expected = {"score": 85, "grade": "B"}
        assert result == expected

    def test_module_with_real_world_scenario(self, data_processing_env, data_processing_script_content):
        """测试真实世界场景"""
        result = Script.module(content=data_processing_script_content, __env__=data_processing_env)

        expected = {
            "original_count": 7,
            "filtered_count": 4,
            "average": 27.5,
            "max": 40,
            "min": 15,
        }
        assert result == expected


class TestScriptModuleParameterFormat:
    """测试原子能力参数格式的兼容性"""

    def test_atomic_parameter_format(self):
        """测试原子能力参数格式（a=a,b=b）的兼容性"""
        test_content = """
def main(a, b):
    return {"sum": a + b, "product": a * b}
"""

        env = type("MockEnv", (), {"to_dict": lambda: {"a": 5, "b": 3}})()

        result = Script.module(content=test_content, __env__=env)

        expected = {"sum": 8, "product": 15}
        assert result == expected


class TestScriptModuleEdgeCases:
    """测试边界情况"""

    def test_module_with_none_values(self):
        """测试包含None值的情况"""
        test_content = """
def main(value1, value2):
    return {
        "value1_is_none": value1 is None,
        "value2_is_none": value2 is None,
        "combined": f"{value1}_{value2}" if value1 and value2 else "empty"
    }
"""

        env = type("MockEnv", (), {"to_dict": lambda: {"value1": None, "value2": "test"}})()

        result = Script.module(content=test_content, __env__=env)

        expected = {
            "value1_is_none": True,
            "value2_is_none": False,
            "combined": "empty",
        }
        assert result == expected
