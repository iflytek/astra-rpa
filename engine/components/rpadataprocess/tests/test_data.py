import json
import unittest
from unittest.mock import Mock, patch

from rpadataprocess import *
from rpadataprocess.data import DataProcess


class TestDataProcess(unittest.TestCase):
    """数据处理器测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_int_value = 123
        self.test_float_value = 123.45
        self.test_str_value = "test string"
        self.test_bool_value = True
        self.test_list_value = [1, 2, 3]
        self.test_dict_value = {"key": "value"}
        self.test_tuple_value = (1, 2, 3)
        self.test_json_value = '{"name": "test", "age": 25}'

    def test_set_variable_value_int(self):
        """测试设置整数类型变量"""
        result = DataProcess.set_variable_value(value=self.test_int_value, variable_type=VariableType.INT)
        self.assertEqual(result, 123)
        self.assertIsInstance(result, int)

    def test_set_variable_value_float(self):
        """测试设置浮点数类型变量"""
        result = DataProcess.set_variable_value(value=self.test_float_value, variable_type=VariableType.FLOAT)
        self.assertEqual(result, 123.45)
        self.assertIsInstance(result, float)

    def test_set_variable_value_str(self):
        """测试设置字符串类型变量"""
        result = DataProcess.set_variable_value(value=self.test_str_value, variable_type=VariableType.STR)
        self.assertEqual(result, "test string")
        self.assertIsInstance(result, str)

    def test_set_variable_value_bool_true(self):
        """测试设置布尔类型变量 - True"""
        result = DataProcess.set_variable_value(value="True", variable_type=VariableType.BOOL)
        self.assertEqual(result, True)
        self.assertIsInstance(result, bool)

    def test_set_variable_value_bool_false(self):
        """测试设置布尔类型变量 - False"""
        result = DataProcess.set_variable_value(value="False", variable_type=VariableType.BOOL)
        self.assertEqual(result, False)
        self.assertIsInstance(result, bool)

    def test_set_variable_value_bool_numeric_true(self):
        """测试设置布尔类型变量 - 数字1"""
        result = DataProcess.set_variable_value(value="1", variable_type=VariableType.BOOL)
        self.assertEqual(result, True)
        self.assertIsInstance(result, bool)

    def test_set_variable_value_bool_numeric_false(self):
        """测试设置布尔类型变量 - 数字0"""
        result = DataProcess.set_variable_value(value="0", variable_type=VariableType.BOOL)
        self.assertEqual(result, False)
        self.assertIsInstance(result, bool)

    def test_set_variable_value_list(self):
        """测试设置列表类型变量"""
        list_str = str(self.test_list_value)
        result = DataProcess.set_variable_value(value=list_str, variable_type=VariableType.LIST)
        self.assertEqual(result, [1, 2, 3])
        self.assertIsInstance(result, list)

    def test_set_variable_value_dict(self):
        """测试设置字典类型变量"""
        dict_str = str(self.test_dict_value)
        result = DataProcess.set_variable_value(value=dict_str, variable_type=VariableType.DICT)
        self.assertEqual(result, {"key": "value"})
        self.assertIsInstance(result, dict)

    def test_set_variable_value_tuple(self):
        """测试设置元组类型变量"""
        tuple_str = str(self.test_tuple_value)
        result = DataProcess.set_variable_value(value=tuple_str, variable_type=VariableType.TUPLE)
        self.assertEqual(result, (1, 2, 3))
        self.assertIsInstance(result, tuple)

    def test_set_variable_value_json(self):
        """测试设置JSON类型变量"""
        result = DataProcess.set_variable_value(value=self.test_json_value, variable_type=VariableType.JSON)
        expected = json.loads(self.test_json_value)
        self.assertEqual(result, expected)
        self.assertIsInstance(result, dict)

    def test_set_variable_value_other(self):
        """测试设置其他类型变量"""
        result = DataProcess.set_variable_value(value=self.test_str_value, variable_type=VariableType.OTHER)
        self.assertEqual(result, self.test_str_value)

    def test_set_variable_value_invalid_int(self):
        """测试无效的整数转换"""
        with self.assertRaises(Exception):
            DataProcess.set_variable_value(value="invalid_int", variable_type=VariableType.INT)

    def test_set_variable_value_invalid_float(self):
        """测试无效的浮点数转换"""
        with self.assertRaises(Exception):
            DataProcess.set_variable_value(value="invalid_float", variable_type=VariableType.FLOAT)

    def test_set_variable_value_invalid_list(self):
        """测试无效的列表转换"""
        with self.assertRaises(Exception):
            DataProcess.set_variable_value(value="invalid_list", variable_type=VariableType.LIST)

    def test_set_variable_value_invalid_json(self):
        """测试无效的JSON转换"""
        with self.assertRaises(Exception):
            DataProcess.set_variable_value(value="invalid_json", variable_type=VariableType.JSON)

    def test_get_shared_variable_empty_list(self):
        """测试获取共享变量 - 空列表"""
        shared_variable = {"subVarList": []}
        result = DataProcess.get_shared_variable(shared_variable=shared_variable)
        self.assertIsNone(result)

    def test_get_shared_variable_no_sub_var_list(self):
        """测试获取共享变量 - 无subVarList"""
        shared_variable = {}
        result = DataProcess.get_shared_variable(shared_variable=shared_variable)
        self.assertIsNone(result)

    def test_get_shared_variable_normal_variables(self):
        """测试获取共享变量 - 普通变量"""
        shared_variable = {
            "subVarList": [
                {
                    "varName": "test_var1",
                    "varValue": "test_value1",
                    "encrypt": False,
                    "key": None,
                },
                {
                    "varName": "test_var2",
                    "varValue": 123,
                    "encrypt": False,
                    "key": None,
                },
            ]
        }
        result = DataProcess.get_shared_variable(shared_variable=shared_variable)
        expected = {"test_var1": "test_value1", "test_var2": 123}
        self.assertEqual(result, expected)

    @patch("rpadataprocess.data.Ciphertext")
    def test_get_shared_variable_encrypted_variables(self, mock_ciphertext):
        """测试获取共享变量 - 加密变量"""
        # 模拟Ciphertext类
        mock_cipher = Mock()
        mock_ciphertext.return_value = mock_cipher

        shared_variable = {
            "subVarList": [
                {
                    "varName": "encrypted_var",
                    "varValue": "encrypted_value",
                    "encrypt": True,
                    "key": "test_key",
                }
            ]
        }
        result = DataProcess.get_shared_variable(shared_variable=shared_variable)

        # 验证Ciphertext被正确创建和配置
        mock_ciphertext.assert_called_once_with("encrypted_value")
        mock_cipher.set_key.assert_called_once_with("test_key")

        # 验证结果包含Ciphertext对象
        self.assertIn("encrypted_var", result)
        self.assertEqual(result["encrypted_var"], mock_cipher)

    def test_get_shared_variable_mixed_variables(self):
        """测试获取共享变量 - 混合变量（普通+加密）"""
        with patch("rpadataprocess.data.Ciphertext") as mock_ciphertext:
            mock_cipher = Mock()
            mock_ciphertext.return_value = mock_cipher

            shared_variable = {
                "subVarList": [
                    {
                        "varName": "normal_var",
                        "varValue": "normal_value",
                        "encrypt": False,
                        "key": None,
                    },
                    {
                        "varName": "encrypted_var",
                        "varValue": "encrypted_value",
                        "encrypt": True,
                        "key": "test_key",
                    },
                ]
            }
            result = DataProcess.get_shared_variable(shared_variable=shared_variable)

            # 验证普通变量
            self.assertEqual(result["normal_var"], "normal_value")

            # 验证加密变量
            self.assertEqual(result["encrypted_var"], mock_cipher)
            mock_cipher.set_key.assert_called_once_with("test_key")

    def test_set_variable_value_edge_cases(self):
        """测试边界情况"""
        # 测试空字符串
        result = DataProcess.set_variable_value(value="", variable_type=VariableType.STR)
        self.assertEqual(result, "")

        # 测试零值
        result = DataProcess.set_variable_value(value=0, variable_type=VariableType.INT)
        self.assertEqual(result, 0)

        # 测试负数
        result = DataProcess.set_variable_value(value=-123, variable_type=VariableType.INT)
        self.assertEqual(result, -123)

    def test_set_variable_value_boolean_edge_cases(self):
        """测试布尔类型的边界情况"""
        # 测试各种True值
        true_values = ["True", "true", "1", True, 1]
        for value in true_values:
            result = DataProcess.set_variable_value(value=value, variable_type=VariableType.BOOL)
            self.assertEqual(result, True)

        # 测试各种False值
        false_values = ["False", "false", "0", False, 0]
        for value in false_values:
            result = DataProcess.set_variable_value(value=value, variable_type=VariableType.BOOL)
            self.assertEqual(result, False)

        # 测试其他值转换为布尔
        result = DataProcess.set_variable_value(value="hello", variable_type=VariableType.BOOL)
        self.assertEqual(result, True)  # 非空字符串转换为True


if __name__ == "__main__":
    unittest.main()
