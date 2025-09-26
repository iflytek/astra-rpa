import ast
import random
from typing import Any

from rpaatomic import DynamicsItem
from rpaatomic.atomic import atomicMg

from rpadataprocess import DeleteMethodType, InsertMethodType, ListType, SortMethodType
from rpadataprocess.error import *


def list_legal_check(list_data: list, index: str = "", allow_empty: bool = True):
    """
    用于内部检查列表是否合法
    """
    if not allow_empty and len(list_data) == 0:
        raise ValueError("列表不能为空!")

    if index:
        try:
            if isinstance(index, str):
                # 将字符串按逗号分割并转换为整数列表
                index_list = [int(idx.strip()) for idx in index.split(",")]
                # 检查每个索引是否在有效范围内
                for idx in index_list:
                    if idx < -len(list_data) or idx >= len(list_data):
                        raise ValueError("数组索引值超出范围!")
                # 如果只有一个索引，返回第一个值
                if len(index_list) == 1:
                    index = index_list[0]
                else:
                    index = index_list
            else:
                # 如果不是字符串，直接转换为整数
                index = int(index)
                if index < -len(list_data) or index >= len(list_data):
                    raise ValueError("数组索引值超出范围!")
        except ValueError as e:
            raise ValueError("请提供有效的整数类型索引!")
        except Exception:
            raise ValueError("请提供整数类型的索引!")
    return list_data, index


class ListProcess:
    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param(
                "size",
                dynamics=[
                    DynamicsItem(
                        key="$this.size.show",
                        expression="return $this.list_type.value == '{}'".format(ListType.SAME_DATA.value),
                    )
                ],
            ),
            atomicMg.param(
                "value",
                types="Any",
                dynamics=[
                    DynamicsItem(
                        key="$this.value.show",
                        expression="return ['{}', '{}'].includes($this.list_type.value)".format(
                            ListType.SAME_DATA.value, ListType.USER_DEFINED.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("created_list_data", types="List")],
    )
    def create_new_list(list_type: ListType = ListType.EMPTY, size: int = 0, value: Any = ""):
        """
        创建新列表
        """
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            try:
                value = ast.literal_eval(value)
            except Exception as e:
                raise BaseException(INVALID_LIST_FORMAT_ERROR_FORMAT.format(e), "请输入正确的列表格式")
        new_array = []
        if list_type == ListType.EMPTY:
            pass
        elif list_type == ListType.SAME_DATA:
            new_array = [value] * size
        elif list_type == ListType.USER_DEFINED:
            if not isinstance(value, list):
                raise ValueError("用户自定义列表类型错误!")
            new_array = value
        return new_array

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[atomicMg.param("list_data", types="List")],
        outputList=[atomicMg.param("cleared_list_data", types="List")],
    )
    def clear_list(list_data: list):
        """
        清空列表
        """
        list_data.clear()
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
            atomicMg.param(
                "index",
                dynamics=[
                    DynamicsItem(
                        key="$this.index.show",
                        expression="return $this.insert_method.value == '{}'".format(InsertMethodType.INDEX.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("inserted_list_data", types="List")],
    )
    def insert_value_to_list(
        list_data: list,
        value: Any,
        insert_method: InsertMethodType = InsertMethodType.APPEND,
        index: str = "",
    ):
        """
        列表插入一项
        """
        if insert_method == InsertMethodType.APPEND:
            index = ""
        list_data, _ = list_legal_check(list_data, "", True)
        if insert_method == InsertMethodType.APPEND:  # 插入方式：末尾追加
            list_data.append(value)
        elif insert_method == InsertMethodType.INDEX:  # 插入方式：指定位置
            try:
                index = int(index)
            except:
                raise BaseException(INVALID_INDEX_ERROR_FORMAT.format(index), "需要提供整数类型的索引！")
            list_data.insert(index, value)
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
            atomicMg.param("index", types="Any"),
        ],
        outputList=[atomicMg.param("changed_list_data", types="List")],
    )
    def change_value_in_list(list_data: list, index: str = "", new_value: Any = ""):
        """
        列表修改一项
        """
        list_data, index = list_legal_check(list_data, index, False)
        list_data[index] = new_value
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
            atomicMg.param("value", types="Any"),
        ],
        outputList=[atomicMg.param("get_list_position", types="Int")],
    )
    def get_list_position(list_data: list, value: Any):
        """
        列表获取一项的位置
        """
        try:
            list_pos = list_data.index(value)
            return list_pos
        except ValueError:
            raise ValueError("列表中不存在该对象!")

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
            atomicMg.param(
                "del_value",
                types="Any",
                dynamics=[
                    DynamicsItem(
                        key="$this.del_value.show",
                        expression="return $this.del_mode.value == '{}'".format(DeleteMethodType.VALUE.value),
                    )
                ],
            ),
            atomicMg.param(
                "del_pos",
                types="Any",
                dynamics=[
                    DynamicsItem(
                        key="$this.del_pos.show",
                        expression="return $this.del_mode.value == '{}'".format(DeleteMethodType.INDEX.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("removed_list_data", types="List")],
    )
    def remove_value_from_list(
        list_data: list,
        del_mode: DeleteMethodType = DeleteMethodType.INDEX,
        del_value: Any = "",
        del_pos: str = "",
    ):
        """
        列表删除一项
        """
        list_data, del_pos = list_legal_check(list_data, del_pos, False)
        if del_mode == DeleteMethodType.INDEX:
            if isinstance(del_pos, list):
                # 从大到小排序索引，避免删除时索引变化
                sorted_indices = sorted(del_pos, reverse=True)
                for index in sorted_indices:
                    del list_data[index]
            else:
                del list_data[del_pos]
            return list_data
        elif del_mode == DeleteMethodType.VALUE:
            try:
                index = list_data.index(del_value)
            except ValueError:
                raise ValueError("列表中未找到该元素！")
            del list_data[index]
            return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("sorted_list_data", types="List")],
    )
    def sort_list(list_data: list, sort_method: SortMethodType = SortMethodType.DESC):
        """
        列表排序
        """
        list_instance = []
        if sort_method == SortMethodType.ASC:
            try:
                list_instance = sorted(list_data)  # 升序
            except:
                raise ValueError("请提供元素数据类型一致的列表进行排序!")
        elif sort_method == SortMethodType.DESC:
            try:
                list_instance = sorted(list_data, reverse=True)  # 默认降序
            except:
                raise ValueError("请提供元素数据类型一致的列表进行排序!")
        return list_instance

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("shuffled_list_data", types="List")],
    )
    def random_shuffle_list(list_data: list):
        """
        列表随机排序
        :param list_data:
        :return:
        """
        random.shuffle(list_data)
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data_1", types="Any"),
            atomicMg.param("list_data_2", types="Any"),
        ],
        outputList=[atomicMg.param("filter_list_data", types="List")],
    )
    def filter_elements_from_list(list_data_1: list, list_data_2: list):
        """
        列表过滤
        """
        return [i for i in list_data_1 if i not in list_data_2]

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("reversed_list_data", types="List")],
    )
    def reverse_list(list_data: list):
        list_data.reverse()
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data_1", types="Any"),
            atomicMg.param("list_data_2", types="Any"),
        ],
        outputList=[atomicMg.param("merged_list_data", types="List")],
    )
    def merge_list(list_data_1: list, list_data_2: list):
        """
        列表合并
        """
        result_list = list_data_1.copy()
        result_list.extend(list_data_2)
        return result_list

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("unique_list_data", types="List")],
    )
    def get_unique_list(list_data: list):
        """
        列表去重
        """
        list_data = list(set(list_data))
        return list_data

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data_1", types="Any"),
            atomicMg.param("list_data_2", types="Any"),
        ],
        outputList=[atomicMg.param("common_list_data", types="List")],
    )
    def get_common_elements_from_list(list_data_1: list, list_data_2: list):
        """
        列表获取共同元素
        """
        list_result = list(set(list_data_1) & set(list_data_2))
        return list_result

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
            atomicMg.param("index", types="Any"),
        ],
        outputList=[atomicMg.param("get_list_value", types="Any")],
    )
    def get_value_from_list(list_data: list, index: str = ""):
        """
        列表获取一项
        """
        list_data, index = list_legal_check(list_data, index, False)
        return list_data[index]

    @staticmethod
    @atomicMg.atomic(
        "ListProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("get_list_length", types="Int")],
    )
    def get_length_of_list(list_data: list):
        """
        列表获取长度
        """
        return len(list_data)
