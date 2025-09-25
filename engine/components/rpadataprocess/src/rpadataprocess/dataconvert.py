import ast
import json
from typing import Any

from rpaatomic.atomic import atomicMg
from rpadataprocess import JSONConvertType, StringConvertType


class DataConvertProcess:
    @staticmethod
    @atomicMg.atomic(
        "DataConvertProcess",
        outputList=[atomicMg.param("json_convert_data", types="Any")],
    )
    def json_convertor(input_data: Any, convert_type: JSONConvertType = JSONConvertType.JSON_TO_STR):
        """
        JSON数据类型转换
        """
        if convert_type == JSONConvertType.JSON_TO_STR:
            return json.dumps(input_data, ensure_ascii=False)
        elif convert_type == JSONConvertType.STR_TO_JSON:
            return json.loads(input_data)

    @staticmethod
    @atomicMg.atomic(
        "DataConvertProcess",
        outputList=[atomicMg.param("other_convert_str", types="Any")],
    )
    def other_to_str(input_data: Any):
        """
        其他数据类型强转为字符串
        """
        try:
            return str(input_data)
        except Exception as e:
            raise ValueError("数据类型不支持强转str!")

    @staticmethod
    @atomicMg.atomic(
        "DataConvertProcess",
        outputList=[atomicMg.param("str_convert_other", types="Any")],
    )
    def str_to_other(input_data: Any, convert_type: StringConvertType = StringConvertType.STR_TO_INT):
        """
        字符串转其他数据类型
        """
        try:
            if convert_type == StringConvertType.STR_TO_INT:
                return int(str(input_data).split(".")[0])
            elif convert_type == StringConvertType.STR_TO_FLOAT:
                return float(input_data)
            elif convert_type == StringConvertType.STR_TO_BOOL:
                if input_data in ["1", "True", "true"]:
                    return True
                elif input_data in ["0", "False", "false"]:
                    return False
                else:
                    return bool(input_data)
            elif convert_type in [
                StringConvertType.STR_TO_LIST,
                StringConvertType.STR_TO_TUPLE,
                StringConvertType.STR_TO_DICT,
            ]:
                return ast.literal_eval(input_data)
        except Exception:
            raise Exception("请输入正确的待转换目标字符串")
