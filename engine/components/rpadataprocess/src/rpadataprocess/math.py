import math
import re
from typing import Any

from rpaatomic import DynamicsItem
from rpaatomic.atomic import atomicMg
from rpadataprocess import AddSubType, MathOperatorType, MathRoundType, NumberType
from rpadataprocess.error import *


def random_number(start, end, number_type: NumberType = NumberType.INTEGER, size: int = 1) -> list:
    """随机数生成"""
    import numpy

    if number_type == NumberType.INTEGER:
        return numpy.random.randint(start, end, size).tolist()
    elif number_type == NumberType.FLOAT:
        return numpy.random.uniform(start, end, size).tolist()


class MathProcess:
    @staticmethod
    @atomicMg.atomic(
        "MathProcess",
        inputList=[atomicMg.param("size", types="Int", required=False)],
        outputList=[atomicMg.param("generated_random_numbers", types="Any")],
    )
    def generate_random_number(
        number_type: NumberType = NumberType.INTEGER,
        size: int = 1,
        start: float = 0,
        end: float = 101,
    ):
        """
        生成随机数，可以指定整数，小数
        """
        if start > end:
            raise BaseException(INVALID_NUMBER_RANGE_ERROR_FORMAT, "开始值必须小于结束值")
        res = random_number(number_type=number_type, start=start, end=end, size=size)
        if len(res) == 1:
            return res[0]
        else:
            return res

    @staticmethod
    @atomicMg.atomic("MathProcess", outputList=[atomicMg.param("rounding_number", types="Any")])
    def get_rounding_number(number: float, precision: int = 2):
        """
        四舍五入
        """
        if precision <= 0:
            return int(round(float(number), int(precision)))
        else:
            if float(number).is_integer():
                return int(round(float(number), int(precision)))
            else:
                return round(float(number), int(precision))

    @staticmethod
    @atomicMg.atomic(
        "MathProcess",
        outputList=[atomicMg.param("self_calculation_number", types="Int")],
    )
    def self_calculation_number(number: int, add_sub: AddSubType = AddSubType.ADD, add_sub_number: int = 1):
        """
        自增自减
        """
        if add_sub == AddSubType.ADD:
            return number + add_sub_number
        elif add_sub == AddSubType.SUB:
            return number - add_sub_number

    @staticmethod
    @atomicMg.atomic(
        "MathProcess",
        inputList=[atomicMg.param("raw_number", types="Any")],
        outputList=[atomicMg.param("absolute_number", types="Any")],
    )
    def get_absolute_number(raw_number: Any):
        """
        获取绝对值
        """
        if isinstance(raw_number, str):
            if re.match(r"^-?\d+$", raw_number):
                raw_number = int(raw_number)
            # 正则表达式匹配浮点数
            elif re.match(r"^-?\d+\.\d+$", raw_number):
                raw_number = float(raw_number)
            else:
                raise BaseException(INVALID_NUMBER_FORMAT_ERROR_FORMAT, "请输入整数或浮点数")
        return abs(raw_number)

    @staticmethod
    @atomicMg.atomic(
        "MathProcess",
        inputList=[
            atomicMg.param(
                "precision",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.precision.show",
                        expression="return $this.handle_method.value == '{}'".format(MathRoundType.ROUND.value),
                    )
                ],
            )
        ],
        outputList=[atomicMg.param("calculation_number", types="Any")],
    )
    def calculate_expression(
        left: str = "",
        operator: MathOperatorType = MathOperatorType.ADD,
        right: str = "",
        handle_method: MathRoundType = MathRoundType.NONE,
        precision: int = 0,
    ):
        """
        表达式计算
        """
        if not left:
            left = "0"
        if not right:
            right = "0"
        try:
            calc_res = eval(str(left) + operator.value + str(right))
        except Exception as e:
            raise BaseException(
                INVALID_MATH_EXPRESSION_ERROR_FORMAT.format(e),
                str(left) + operator.value + str(right),
            )
        if handle_method == MathRoundType.ROUND:
            if precision <= 0:
                return int(round(float(calc_res), int(precision)))
            else:
                if float(calc_res).is_integer():
                    return int(round(float(calc_res), int(precision)))
                else:
                    return round(float(calc_res), int(precision))
        elif handle_method == MathRoundType.FLOOR:
            calc_res = math.floor(calc_res)
        elif handle_method == MathRoundType.CEIL:
            calc_res = math.ceil(calc_res)
        return calc_res
