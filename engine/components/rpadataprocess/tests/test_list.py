import unittest

from rpadataprocess import DeleteMethodType, InsertMethodType, ListType, SortMethodType
from rpadataprocess.list import ListProcess


class TestListProcess(unittest.TestCase):
    """ListProcess类的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_list = [1, 2, 3, 4, 5]
        self.test_list_str = ["apple", "banana", "cherry"]
        self.test_list_mixed = [1, "hello", 3.14, True]

    def test_create_new_list_empty(self):
        """测试创建空列表"""
        result = ListProcess.create_new_list(list_type=ListType.EMPTY)
        self.assertEqual(result, [])

    def test_create_new_list_same_data(self):
        """测试创建相同数据的列表"""
        result = ListProcess.create_new_list(list_type=ListType.SAME_DATA, size=5, value="test")
        self.assertEqual(result, ["test", "test", "test", "test", "test"])

    def test_create_new_list_user_defined(self):
        """测试创建用户自定义列表"""
        custom_list = [1, 2, 3, 4, 5]
        result = ListProcess.create_new_list(list_type=ListType.USER_DEFINED, value=custom_list)
        self.assertEqual(result, custom_list)

    def test_create_new_list_with_string_format(self):
        """测试使用字符串格式创建列表"""
        result = ListProcess.create_new_list(list_type=ListType.USER_DEFINED, value="[1, 2, 3, 4, 5]")
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_clear_list(self):
        """测试清空列表"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.clear_list(list_data=test_list)
        self.assertEqual(result, [])
        self.assertEqual(len(test_list), 0)

    def test_insert_value_to_list_append(self):
        """测试在列表末尾追加元素"""
        test_list = [1, 2, 3]
        result = ListProcess.insert_value_to_list(list_data=test_list, value=4, insert_method=InsertMethodType.APPEND)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_insert_value_to_list_index(self):
        """测试在指定位置插入元素"""
        test_list = [1, 2, 3]
        result = ListProcess.insert_value_to_list(
            list_data=test_list,
            value=4,
            insert_method=InsertMethodType.INDEX,
            index="1",
        )
        self.assertEqual(result, [1, 4, 2, 3])

    def test_change_value_in_list(self):
        """测试修改列表中的元素"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.change_value_in_list(list_data=test_list, index="2", new_value=10)
        self.assertEqual(result[2], 10)

    def test_get_list_position(self):
        """测试获取元素在列表中的位置"""
        test_list = ["apple", "banana", "cherry"]
        result = ListProcess.get_list_position(list_data=test_list, value="banana")
        self.assertEqual(result, 1)

    def test_get_list_position_not_found(self):
        """测试获取不存在的元素位置"""
        test_list = ["apple", "banana", "cherry"]
        with self.assertRaises(ValueError):
            ListProcess.get_list_position(list_data=test_list, value="orange")

    def test_remove_value_from_list_by_index(self):
        """测试通过索引删除元素"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.remove_value_from_list(list_data=test_list, del_mode=DeleteMethodType.INDEX, del_pos="2")
        self.assertEqual(result, [1, 2, 4, 5])

    def test_remove_value_from_list_by_index_multiple(self):
        """测试通过多个索引删除元素"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.remove_value_from_list(
            list_data=test_list, del_mode=DeleteMethodType.INDEX, del_pos="0,2,4"
        )
        self.assertEqual(result, [2, 4])

    def test_remove_value_from_list_by_value(self):
        """测试通过值删除元素"""
        test_list = ["apple", "banana", "cherry"]
        result = ListProcess.remove_value_from_list(
            list_data=test_list, del_mode=DeleteMethodType.VALUE, del_value="banana"
        )
        self.assertEqual(result, ["apple", "cherry"])

    def test_remove_value_from_list_by_value_not_found(self):
        """测试删除不存在的值"""
        test_list = ["apple", "banana", "cherry"]
        with self.assertRaises(ValueError):
            ListProcess.remove_value_from_list(list_data=test_list, del_mode=DeleteMethodType.VALUE, del_value="orange")

    def test_sort_list_asc(self):
        """测试列表升序排序"""
        test_list = [3, 1, 4, 1, 5, 9, 2, 6]
        result = ListProcess.sort_list(list_data=test_list, sort_method=SortMethodType.ASC)
        self.assertEqual(result, [1, 1, 2, 3, 4, 5, 6, 9])

    def test_sort_list_desc(self):
        """测试列表降序排序"""
        test_list = [3, 1, 4, 1, 5, 9, 2, 6]
        result = ListProcess.sort_list(list_data=test_list, sort_method=SortMethodType.DESC)
        self.assertEqual(result, [9, 6, 5, 4, 3, 2, 1, 1])

    def test_sort_list_mixed_types_error(self):
        """测试混合类型列表排序错误"""
        test_list = [1, "hello", 3.14, True]
        with self.assertRaises(ValueError):
            ListProcess.sort_list(list_data=test_list, sort_method=SortMethodType.ASC)

    def test_random_shuffle_list(self):
        """测试列表随机排序"""
        test_list = [1, 2, 3, 4, 5]
        original_list = test_list.copy()
        result = ListProcess.random_shuffle_list(list_data=test_list)
        # 检查元素是否相同（顺序可能不同）
        self.assertEqual(sorted(result), sorted(original_list))
        # 检查是否真的发生了随机排序（虽然理论上可能相同，但概率很小）
        self.assertIs(result, test_list)  # 应该返回同一个列表对象

    def test_filter_elements_from_list(self):
        """测试列表过滤"""
        list1 = [1, 2, 3, 4, 5]
        list2 = [2, 4]
        result = ListProcess.filter_elements_from_list(list_data_1=list1, list_data_2=list2)
        self.assertEqual(result, [1, 3, 5])

    def test_reverse_list(self):
        """测试列表反转"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.reverse_list(list_data=test_list)
        self.assertEqual(result, [5, 4, 3, 2, 1])
        self.assertIs(result, test_list)  # 应该返回同一个列表对象

    def test_merge_list(self):
        """测试列表合并"""
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        result = ListProcess.merge_list(list_data_1=list1, list_data_2=list2)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6])

    def test_get_unique_list(self):
        """测试列表去重"""
        test_list = [1, 2, 2, 3, 3, 3, 4, 5, 5]
        result = ListProcess.get_unique_list(list_data=test_list)
        # 注意：set去重后顺序可能不同，所以需要排序比较
        self.assertEqual(sorted(result), [1, 2, 3, 4, 5])

    def test_get_common_elements_from_list(self):
        """测试获取两个列表的共同元素"""
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5, 6, 7]
        result = ListProcess.get_common_elements_from_list(list_data_1=list1, list_data_2=list2)
        # 注意：set操作后顺序可能不同，所以需要排序比较
        self.assertEqual(sorted(result), [3, 4, 5])

    def test_get_value_from_list(self):
        """测试获取列表中的元素"""
        test_list = ["apple", "banana", "cherry", "date"]
        result = ListProcess.get_value_from_list(list_data=test_list, index="2")
        self.assertEqual(result, "cherry")

    def test_get_value_from_list_negative_index(self):
        """测试使用负数索引获取元素"""
        test_list = ["apple", "banana", "cherry", "date"]
        result = ListProcess.get_value_from_list(list_data=test_list, index="-1")
        self.assertEqual(result, "date")

    def test_get_length_of_list(self):
        """测试获取列表长度"""
        test_list = [1, 2, 3, 4, 5]
        result = ListProcess.get_length_of_list(list_data=test_list)
        self.assertEqual(result, 5)

    def test_get_length_of_empty_list(self):
        """测试获取空列表长度"""
        test_list = []
        result = ListProcess.get_length_of_list(list_data=test_list)
        self.assertEqual(result, 0)

    def test_list_legal_check_empty_list_error(self):
        """测试空列表检查错误"""
        test_list = []
        with self.assertRaises(ValueError):
            ListProcess.change_value_in_list(list_data=test_list, index="0", new_value=10)

    def test_list_legal_check_index_out_of_range(self):
        """测试索引超出范围错误"""
        test_list = [1, 2, 3]
        with self.assertRaises(ValueError):
            ListProcess.change_value_in_list(list_data=test_list, index="10", new_value=10)

    def test_list_legal_check_invalid_index_format(self):
        """测试无效索引格式错误"""
        test_list = [1, 2, 3]
        with self.assertRaises(ValueError):
            ListProcess.change_value_in_list(list_data=test_list, index="abc", new_value=10)


if __name__ == "__main__":
    unittest.main()
