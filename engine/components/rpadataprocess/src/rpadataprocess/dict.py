from typing import Any

from rpaatomic import DynamicsItem
from rpaatomic.atomic import atomicMg

from rpadataprocess import NoKeyOptionType


class DictProcess:
    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any", required=False),
        ],
        outputList=[atomicMg.param("created_new_dict_data", types="Dict")],
    )
    def create_new_dict(dict_data: dict):
        return dict_data

    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any"),
            atomicMg.param("dict_key", types="Any", required=False),
            atomicMg.param("value", types="Any", required=False),
        ],
        outputList=[atomicMg.param("inserted_dict_data", types="Dict")],
    )
    def set_value_to_dict(dict_data: dict, dict_key: Any, value: Any):
        """
        字典插入一项
        """
        # dict_key 为None时, 转换为空字符串
        if dict_key is None:
            dict_key = ""
        dict_data[dict_key] = value
        return dict_data

    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any"),
        ],
        outputList=[atomicMg.param("deleted_dict_data", types="Dict")],
    )
    def delete_value_from_dict(dict_data: dict, dict_key: str):
        """
        字典删除一项
        """
        if dict_key in dict_data:
            del dict_data[dict_key]
        return dict_data

    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any"),
            atomicMg.param(
                "default_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.default_value.show",
                        expression="return $this.fail_option.value == '{}'".format(
                            NoKeyOptionType.RETURN_DEFAULT.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("get_dict_value", types="Any")],
    )
    def get_value_from_dict(
        dict_data: dict,
        dict_key: str,
        fail_option: NoKeyOptionType = NoKeyOptionType.RAISE_ERROR,
        default_value: Any = "",
    ):
        """
        字典获取一项
        """
        if dict_data.get(dict_key) is not None:
            return dict_data[dict_key]
        else:
            if fail_option == NoKeyOptionType.RAISE_ERROR:
                raise ValueError("字典中不存在该键!")
            elif fail_option == NoKeyOptionType.RETURN_DEFAULT:
                return default_value

    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any"),
        ],
        outputList=[atomicMg.param("get_dict_keys", types="Dict")],
    )
    def get_keys_from_dict(dict_data: dict):
        """
        字典获取所有键
        """
        return list(dict_data.keys())

    @staticmethod
    @atomicMg.atomic(
        "DictProcess",
        inputList=[
            atomicMg.param("dict_data", types="Any"),
        ],
        outputList=[atomicMg.param("get_dict_values", types="Dict")],
    )
    def get_values_from_dict(dict_data: dict):
        """
        字典获取所有值
        """
        return list(dict_data.values())
