import unittest

from rpadataprocess import *
from rpadataprocess.dataconvert import DataConvertProcess


class TestDataConvertProcess(unittest.TestCase):
    """数据转换处理模块测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_dict = {"name": "张三", "age": 25, "city": "北京"}
        self.test_list = [1, 2, 3, "测试"]
        self.test_str_json = '{"name": "李四", "age": 30, "city": "上海"}'
        self.test_str_list = "[1, 2, 3, '测试']"
        self.test_str_dict = "{'name': '王五', 'age': 35, 'city': '广州'}"
        self.test_str_tuple = "(1, 2, 3, '测试')"

    def test_json_convertor_json_to_str(self):
        """测试JSON转字符串"""
        result = DataConvertProcess.json_convertor(input_data=self.test_dict, convert_type=JSONConvertType.JSON_TO_STR)
        expected = '{"name": "张三", "age": 25, "city": "北京"}'
        self.assertEqual(result, expected)

    def test_json_convertor_str_to_json(self):
        """测试字符串转JSON"""
        result = DataConvertProcess.json_convertor(
            input_data=self.test_str_json, convert_type=JSONConvertType.STR_TO_JSON
        )
        expected = {"name": "李四", "age": 30, "city": "上海"}
        self.assertEqual(result, expected)

    def test_json_convertor_default_type(self):
        """测试JSON转换默认类型（JSON_TO_STR）"""
        result = DataConvertProcess.json_convertor(input_data=self.test_list)
        expected = '[1, 2, 3, "测试"]'
        self.assertEqual(result, expected)

    def test_json_convertor_with_list(self):
        """测试列表转JSON字符串"""
        result = DataConvertProcess.json_convertor(input_data=self.test_list, convert_type=JSONConvertType.JSON_TO_STR)
        expected = '[1, 2, 3, "测试"]'
        self.assertEqual(result, expected)

    def test_other_to_str_with_dict(self):
        """测试字典转字符串"""
        result = DataConvertProcess.other_to_str(input_data=self.test_dict)
        expected = "{'name': '张三', 'age': 25, 'city': '北京'}"
        self.assertEqual(result, expected)

    def test_other_to_str_with_list(self):
        """测试列表转字符串"""
        result = DataConvertProcess.other_to_str(input_data=self.test_list)
        expected = "[1, 2, 3, '测试']"
        self.assertEqual(result, expected)

    def test_other_to_str_with_int(self):
        """测试整数转字符串"""
        result = DataConvertProcess.other_to_str(input_data=123)
        self.assertEqual(result, "123")

    def test_other_to_str_with_float(self):
        """测试浮点数转字符串"""
        result = DataConvertProcess.other_to_str(input_data=123.45)
        self.assertEqual(result, "123.45")

    def test_other_to_str_with_bool(self):
        """测试布尔值转字符串"""
        result = DataConvertProcess.other_to_str(input_data=True)
        self.assertEqual(result, "True")

    def test_str_to_other_str_to_int(self):
        """测试字符串转整数"""
        result = DataConvertProcess.str_to_other(input_data="123", convert_type=StringConvertType.STR_TO_INT)
        self.assertEqual(result, 123)

    def test_str_to_other_str_to_int_with_float_string(self):
        """测试带小数点的字符串转整数（取整数部分）"""
        result = DataConvertProcess.str_to_other(input_data="123.45", convert_type=StringConvertType.STR_TO_INT)
        self.assertEqual(result, 123)

    def test_str_to_other_str_to_float(self):
        """测试字符串转浮点数"""
        result = DataConvertProcess.str_to_other(input_data="123.45", convert_type=StringConvertType.STR_TO_FLOAT)
        self.assertEqual(result, 123.45)

    def test_str_to_other_str_to_bool_true_1(self):
        """测试字符串'1'转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="1", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, True)

    def test_str_to_other_str_to_bool_true_string(self):
        """测试字符串'True'转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="True", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, True)

    def test_str_to_other_str_to_bool_false_0(self):
        """测试字符串'0'转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="0", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, False)

    def test_str_to_other_str_to_bool_false_string(self):
        """测试字符串'False'转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="False", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, False)

    def test_str_to_other_str_to_bool_other_string(self):
        """测试其他字符串转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="hello", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, True)  # 非空字符串转为True

    def test_str_to_other_str_to_list(self):
        """测试字符串转列表"""
        result = DataConvertProcess.str_to_other(
            input_data=self.test_str_list, convert_type=StringConvertType.STR_TO_LIST
        )
        expected = [1, 2, 3, "测试"]
        self.assertEqual(result, expected)

    def test_str_to_other_str_to_dict(self):
        """测试字符串转字典"""
        result = DataConvertProcess.str_to_other(
            input_data=self.test_str_dict, convert_type=StringConvertType.STR_TO_DICT
        )
        expected = {"name": "王五", "age": 35, "city": "广州"}
        self.assertEqual(result, expected)

    def test_str_to_other_str_to_tuple(self):
        """测试字符串转元组"""
        result = DataConvertProcess.str_to_other(
            input_data=self.test_str_tuple, convert_type=StringConvertType.STR_TO_TUPLE
        )
        expected = (1, 2, 3, "测试")
        self.assertEqual(result, expected)

    def test_str_to_other_default_type(self):
        """测试字符串转换默认类型（STR_TO_INT）"""
        result = DataConvertProcess.str_to_other(input_data="123")
        self.assertEqual(result, 123)

    def test_str_to_other_invalid_int(self):
        """测试无效的字符串转整数（应该抛出异常）"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="abc", convert_type=StringConvertType.STR_TO_INT)

    def test_str_to_other_invalid_float(self):
        """测试无效的字符串转浮点数（应该抛出异常）"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="abc", convert_type=StringConvertType.STR_TO_FLOAT)

    def test_str_to_other_invalid_list(self):
        """测试无效的字符串转列表（应该抛出异常）"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="invalid_list", convert_type=StringConvertType.STR_TO_LIST)

    def test_str_to_other_invalid_dict(self):
        """测试无效的字符串转字典（应该抛出异常）"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="invalid_dict", convert_type=StringConvertType.STR_TO_DICT)

    def test_str_to_other_invalid_tuple(self):
        """测试无效的字符串转元组（应该抛出异常）"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="invalid_tuple", convert_type=StringConvertType.STR_TO_TUPLE)

    def test_edge_cases_empty_string_to_int(self):
        """测试边界情况：空字符串转整数"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="", convert_type=StringConvertType.STR_TO_INT)

    def test_edge_cases_empty_string_to_float(self):
        """测试边界情况：空字符串转浮点数"""
        with self.assertRaises(Exception):
            DataConvertProcess.str_to_other(input_data="", convert_type=StringConvertType.STR_TO_FLOAT)

    def test_edge_cases_empty_string_to_bool(self):
        """测试边界情况：空字符串转布尔值"""
        result = DataConvertProcess.str_to_other(input_data="", convert_type=StringConvertType.STR_TO_BOOL)
        self.assertEqual(result, False)

    def test_edge_cases_complex_json(self):
        """测试复杂JSON结构转换"""
        complex_data = {
            "users": [
                {"name": "张三", "age": 25, "skills": ["Python", "Java"]},
                {"name": "李四", "age": 30, "skills": ["C++", "Go"]},
            ],
            "metadata": {"total": 2, "active": True, "tags": ["开发", "测试"]},
        }

        # JSON转字符串
        json_str = DataConvertProcess.json_convertor(input_data=complex_data, convert_type=JSONConvertType.JSON_TO_STR)

        # 字符串转JSON
        result = DataConvertProcess.json_convertor(input_data=json_str, convert_type=JSONConvertType.STR_TO_JSON)

        self.assertEqual(result, complex_data)

    def test_edge_cases_nested_structures(self):
        """测试嵌套结构转换"""
        nested_str = "{'outer': {'inner': [1, 2, {'deep': 'value'}]}}"

        result = DataConvertProcess.str_to_other(input_data=nested_str, convert_type=StringConvertType.STR_TO_DICT)

        expected = {"outer": {"inner": [1, 2, {"deep": "value"}]}}
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
