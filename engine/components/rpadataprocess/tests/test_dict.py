import unittest

from rpadataprocess import NoKeyOptionType
from rpadataprocess.dict import DictProcess


class TestDictProcess(unittest.TestCase):
    """DictProcess类的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_dict = {"name": "张三", "age": 25, "city": "北京"}
        self.test_dict_empty = {}
        self.test_dict_nested = {
            "user": {"name": "李四", "age": 30},
            "settings": {"theme": "dark", "language": "zh"},
        }

    def test_create_new_dict_empty(self):
        """测试创建空字典"""
        result = DictProcess.create_new_dict(dict_data={})
        self.assertEqual(result, {})

    def test_create_new_dict_with_data(self):
        """测试创建包含数据的字典"""
        test_data = {"key1": "value1", "key2": "value2"}
        result = DictProcess.create_new_dict(dict_data=test_data)
        self.assertEqual(result, test_data)

    def test_set_value_to_dict_new_key(self):
        """测试向字典插入新键值对"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="city", value="上海")
        expected = {"name": "张三", "age": 25, "city": "上海"}
        self.assertEqual(result, expected)

    def test_set_value_to_dict_existing_key(self):
        """测试更新字典中已存在的键"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="age", value=30)
        expected = {"name": "张三", "age": 30}
        self.assertEqual(result, expected)

    def test_set_value_to_dict_empty_dict(self):
        """测试向空字典插入键值对"""
        test_dict = {}
        result = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="first_key", value="first_value")
        expected = {"first_key": "first_value"}
        self.assertEqual(result, expected)

    def test_set_value_to_dict_complex_value(self):
        """测试插入复杂类型的值"""
        test_dict = {"simple": "value"}
        complex_value = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        result = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="complex", value=complex_value)
        expected = {"simple": "value", "complex": complex_value}
        self.assertEqual(result, expected)

    def test_delete_value_from_dict_existing_key(self):
        """测试删除字典中存在的键"""
        test_dict = {"name": "张三", "age": 25, "city": "北京"}
        result = DictProcess.delete_value_from_dict(dict_data=test_dict, dict_key="age")
        expected = {"name": "张三", "city": "北京"}
        self.assertEqual(result, expected)

    def test_delete_value_from_dict_nonexistent_key(self):
        """测试删除字典中不存在的键"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.delete_value_from_dict(dict_data=test_dict, dict_key="nonexistent")
        # 删除不存在的键应该不报错，返回原字典
        self.assertEqual(result, test_dict)

    def test_delete_value_from_dict_empty_dict(self):
        """测试从空字典删除键"""
        test_dict = {}
        result = DictProcess.delete_value_from_dict(dict_data=test_dict, dict_key="any_key")
        self.assertEqual(result, {})

    def test_get_value_from_dict_existing_key(self):
        """测试获取字典中存在的键的值"""
        test_dict = {"name": "张三", "age": 25, "city": "北京"}
        result = DictProcess.get_value_from_dict(dict_data=test_dict, dict_key="name")
        self.assertEqual(result, "张三")

    def test_get_value_from_dict_nonexistent_key_raise_error(self):
        """测试获取不存在的键时抛出异常"""
        test_dict = {"name": "张三", "age": 25}
        with self.assertRaises(ValueError):
            DictProcess.get_value_from_dict(
                dict_data=test_dict,
                dict_key="nonexistent",
                fail_option=NoKeyOptionType.RAISE_ERROR,
            )

    def test_get_value_from_dict_nonexistent_key_return_default(self):
        """测试获取不存在的键时返回默认值"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.get_value_from_dict(
            dict_data=test_dict,
            dict_key="nonexistent",
            fail_option=NoKeyOptionType.RETURN_DEFAULT,
            default_value="默认值",
        )
        self.assertEqual(result, "默认值")

    def test_get_value_from_dict_nonexistent_key_return_default_empty_string(self):
        """测试获取不存在的键时返回空字符串默认值"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.get_value_from_dict(
            dict_data=test_dict,
            dict_key="nonexistent",
            fail_option=NoKeyOptionType.RETURN_DEFAULT,
            default_value="",
        )
        self.assertEqual(result, "")

    def test_get_value_from_dict_nonexistent_key_return_default_none(self):
        """测试获取不存在的键时返回None默认值"""
        test_dict = {"name": "张三", "age": 25}
        result = DictProcess.get_value_from_dict(
            dict_data=test_dict,
            dict_key="nonexistent",
            fail_option=NoKeyOptionType.RETURN_DEFAULT,
            default_value=None,
        )
        self.assertEqual(result, "")

    def test_get_value_from_dict_complex_value(self):
        """测试获取复杂类型的值"""
        complex_value = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        test_dict = {"simple": "value", "complex": complex_value}
        result = DictProcess.get_value_from_dict(dict_data=test_dict, dict_key="complex")
        self.assertEqual(result, complex_value)

    def test_get_keys_from_dict(self):
        """测试获取字典的所有键"""
        test_dict = {"name": "张三", "age": 25, "city": "北京"}
        result = DictProcess.get_keys_from_dict(dict_data=test_dict)
        expected = ["name", "age", "city"]
        # 由于字典键的顺序可能不确定，我们检查键的集合是否相同
        self.assertEqual(set(result), set(expected))

    def test_get_keys_from_dict_empty(self):
        """测试获取空字典的键"""
        test_dict = {}
        result = DictProcess.get_keys_from_dict(dict_data=test_dict)
        self.assertEqual(result, [])

    def test_get_keys_from_dict_nested(self):
        """测试获取嵌套字典的键"""
        test_dict = {
            "user": {"name": "李四", "age": 30},
            "settings": {"theme": "dark", "language": "zh"},
        }
        result = DictProcess.get_keys_from_dict(dict_data=test_dict)
        expected = ["user", "settings"]
        self.assertEqual(set(result), set(expected))

    def test_get_values_from_dict(self):
        """测试获取字典的所有值"""
        test_dict = {"name": "张三", "age": 25, "city": "北京"}
        result = DictProcess.get_values_from_dict(dict_data=test_dict)
        expected = ["张三", 25, "北京"]
        # 由于字典值的顺序可能不确定，我们检查值的集合是否相同
        self.assertEqual(set(result), set(expected))

    def test_get_values_from_dict_empty(self):
        """测试获取空字典的值"""
        test_dict = {}
        result = DictProcess.get_values_from_dict(dict_data=test_dict)
        self.assertEqual(result, [])

    def test_get_values_from_dict_nested(self):
        """测试获取嵌套字典的值"""
        nested_dict1 = {"name": "李四", "age": 30}
        nested_dict2 = {"theme": "dark", "language": "zh"}
        test_dict = {"user": nested_dict1, "settings": nested_dict2}
        result = DictProcess.get_values_from_dict(dict_data=test_dict)
        expected = [nested_dict1, nested_dict2]
        # 由于字典值的顺序可能不确定，我们检查值的集合是否相同
        self.assertEqual(set(str(v) for v in result), set(str(v) for v in expected))

    def test_get_values_from_dict_mixed_types(self):
        """测试获取包含不同类型值的字典"""
        test_dict = {
            "string": "hello",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
        }
        result = DictProcess.get_values_from_dict(dict_data=test_dict)
        expected = ["hello", 42, True, [1, 2, 3]]
        # 由于字典值的顺序可能不确定，我们检查值的集合是否相同
        self.assertEqual(set(str(v) for v in result), set(str(v) for v in expected))

    def test_dict_operations_chain(self):
        """测试字典操作的链式调用"""
        # 创建字典
        test_dict = {}

        # 插入多个键值对
        test_dict = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="name", value="王五")
        test_dict = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="age", value=28)
        test_dict = DictProcess.set_value_to_dict(dict_data=test_dict, dict_key="city", value="深圳")

        # 验证插入结果
        self.assertEqual(test_dict, {"name": "王五", "age": 28, "city": "深圳"})

        # 获取值
        name = DictProcess.get_value_from_dict(dict_data=test_dict, dict_key="name")
        self.assertEqual(name, "王五")

        # 删除一个键
        test_dict = DictProcess.delete_value_from_dict(dict_data=test_dict, dict_key="age")
        self.assertEqual(test_dict, {"name": "王五", "city": "深圳"})

        # 获取所有键
        keys = DictProcess.get_keys_from_dict(dict_data=test_dict)
        self.assertEqual(set(keys), {"name", "city"})

        # 获取所有值
        values = DictProcess.get_values_from_dict(dict_data=test_dict)
        self.assertEqual(set(values), {"王五", "深圳"})


if __name__ == "__main__":
    unittest.main()
