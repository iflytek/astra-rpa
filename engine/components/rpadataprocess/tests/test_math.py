import unittest

from rpadataprocess import *
from rpadataprocess.error import *
from rpadataprocess.math import MathProcess


class TestMathProcess(unittest.TestCase):
    """数学处理模块测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.test_number = 10
        self.test_float = 10.567
        self.test_negative = -15
        self.test_string_number = "25"
        self.test_string_float = "25.5"

    def test_generate_random_number_integer_single(self):
        """测试生成单个整数随机数"""
        result = MathProcess.generate_random_number(number_type=NumberType.INTEGER, size=1, start=1, end=101)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLess(result, 101)

    def test_generate_random_number_integer_multiple(self):
        """测试生成多个整数随机数"""
        result = MathProcess.generate_random_number(number_type=NumberType.INTEGER, size=5, start=1, end=101)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        for num in result:
            self.assertIsInstance(num, int)
            self.assertGreaterEqual(num, 1)
            self.assertLess(num, 101)

    def test_generate_random_number_float_single(self):
        """测试生成单个浮点数随机数"""
        result = MathProcess.generate_random_number(number_type=NumberType.FLOAT, size=1, start=1.0, end=10.0)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 1.0)
        self.assertLess(result, 10.0)

    def test_generate_random_number_float_multiple(self):
        """测试生成多个浮点数随机数"""
        result = MathProcess.generate_random_number(number_type=NumberType.FLOAT, size=3, start=1.0, end=10.0)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        for num in result:
            self.assertIsInstance(num, float)
            self.assertGreaterEqual(num, 1.0)
            self.assertLess(num, 10.0)

    def test_generate_random_number_invalid_range(self):
        """测试无效范围参数"""
        with self.assertRaises(BaseException):
            MathProcess.generate_random_number(number_type=NumberType.INTEGER, size=1, start=100, end=50)

    def test_get_rounding_number_integer(self):
        """测试整数四舍五入"""
        result = MathProcess.get_rounding_number(number=10, precision=0)
        self.assertEqual(result, 10)

    def test_get_rounding_number_float_round_up(self):
        """测试浮点数四舍五入向上"""
        result = MathProcess.get_rounding_number(number=10.567, precision=2)
        self.assertEqual(result, 10.57)

    def test_get_rounding_number_float_round_down(self):
        """测试浮点数四舍五入向下"""
        result = MathProcess.get_rounding_number(number=10.564, precision=2)
        self.assertEqual(result, 10.56)

    def test_get_rounding_number_negative_precision(self):
        """测试负数精度四舍五入"""
        result = MathProcess.get_rounding_number(number=1234.567, precision=-2)
        self.assertEqual(result, 1200)

    def test_get_rounding_number_zero_precision(self):
        """测试零精度四舍五入"""
        result = MathProcess.get_rounding_number(number=10.567, precision=0)
        self.assertEqual(result, 11)

    def test_self_calculation_number_add(self):
        """测试自增操作"""
        result = MathProcess.self_calculation_number(number=self.test_number, add_sub=AddSubType.ADD, add_sub_number=5)
        self.assertEqual(result, 15)

    def test_self_calculation_number_sub(self):
        """测试自减操作"""
        result = MathProcess.self_calculation_number(number=self.test_number, add_sub=AddSubType.SUB, add_sub_number=3)
        self.assertEqual(result, 7)

    def test_self_calculation_number_add_default(self):
        """测试自增操作默认参数"""
        result = MathProcess.self_calculation_number(number=self.test_number, add_sub=AddSubType.ADD)
        self.assertEqual(result, 11)

    def test_self_calculation_number_sub_default(self):
        """测试自减操作默认参数"""
        result = MathProcess.self_calculation_number(number=self.test_number, add_sub=AddSubType.SUB)
        self.assertEqual(result, 9)

    def test_get_absolute_number_positive_int(self):
        """测试正整数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=25)
        self.assertEqual(result, 25)

    def test_get_absolute_number_negative_int(self):
        """测试负整数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=self.test_negative)
        self.assertEqual(result, 15)

    def test_get_absolute_number_positive_float(self):
        """测试正浮点数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=25.5)
        self.assertEqual(result, 25.5)

    def test_get_absolute_number_negative_float(self):
        """测试负浮点数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=-25.5)
        self.assertEqual(result, 25.5)

    def test_get_absolute_number_string_int(self):
        """测试字符串整数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=self.test_string_number)
        self.assertEqual(result, 25)

    def test_get_absolute_number_string_float(self):
        """测试字符串浮点数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number=self.test_string_float)
        self.assertEqual(result, 25.5)

    def test_get_absolute_number_string_negative(self):
        """测试字符串负数的绝对值"""
        result = MathProcess.get_absolute_number(raw_number="-25")
        self.assertEqual(result, 25)

    def test_get_absolute_number_invalid_string(self):
        """测试无效字符串格式"""
        with self.assertRaises(BaseException):
            MathProcess.get_absolute_number(raw_number="invalid")

    def test_calculate_expression_add(self):
        """测试加法表达式计算"""
        result = MathProcess.calculate_expression(left="10", operator=MathOperatorType.ADD, right="5")
        self.assertEqual(result, 15)

    def test_calculate_expression_subtract(self):
        """测试减法表达式计算"""
        result = MathProcess.calculate_expression(left="20", operator=MathOperatorType.SUB, right="8")
        self.assertEqual(result, 12)

    def test_calculate_expression_multiply(self):
        """测试乘法表达式计算"""
        result = MathProcess.calculate_expression(left="6", operator=MathOperatorType.MUL, right="7")
        self.assertEqual(result, 42)

    def test_calculate_expression_divide(self):
        """测试除法表达式计算"""
        result = MathProcess.calculate_expression(left="15", operator=MathOperatorType.DIV, right="3")
        self.assertEqual(result, 5.0)

    def test_calculate_expression_with_round(self):
        """测试带四舍五入的表达式计算"""
        result = MathProcess.calculate_expression(
            left="10",
            operator=MathOperatorType.DIV,
            right="3",
            handle_method=MathRoundType.ROUND,
            precision=2,
        )
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 3.33, places=2)

    def test_calculate_expression_with_floor(self):
        """测试带向下取整的表达式计算"""
        result = MathProcess.calculate_expression(
            left="10",
            operator=MathOperatorType.DIV,
            right="3",
            handle_method=MathRoundType.FLOOR,
        )
        self.assertEqual(result, 3)

    def test_calculate_expression_with_ceil(self):
        """测试带向上取整的表达式计算"""
        result = MathProcess.calculate_expression(
            left="10",
            operator=MathOperatorType.DIV,
            right="3",
            handle_method=MathRoundType.CEIL,
        )
        self.assertEqual(result, 4)

    def test_calculate_expression_with_none(self):
        """测试不带处理的表达式计算"""
        result = MathProcess.calculate_expression(
            left="10",
            operator=MathOperatorType.DIV,
            right="3",
            handle_method=MathRoundType.NONE,
        )
        self.assertEqual(result, 10 / 3)

    def test_calculate_expression_invalid_expression(self):
        """测试无效表达式"""
        with self.assertRaises(BaseException):
            MathProcess.calculate_expression(left="10", operator=MathOperatorType.DIV, right="0")

    def test_calculate_expression_invalid_syntax(self):
        """测试语法错误的表达式"""
        with self.assertRaises(BaseException):
            MathProcess.calculate_expression(left="invalid", operator=MathOperatorType.ADD, right="5")

    def test_calculate_expression_float_numbers(self):
        """测试浮点数表达式计算"""
        result = MathProcess.calculate_expression(left="10.5", operator=MathOperatorType.ADD, right="5.3")
        self.assertEqual(result, 15.8)

    def test_calculate_expression_mixed_types(self):
        """测试混合类型表达式计算"""
        result = MathProcess.calculate_expression(left="10", operator=MathOperatorType.MUL, right="2.5")
        self.assertEqual(result, 25.0)

    def test_calculate_expression_default_parameters(self):
        """测试默认参数表达式计算"""
        result = MathProcess.calculate_expression()
        self.assertEqual(result, 0)  # 空字符串相加结果为0

    def test_calculate_expression_complex_expression(self):
        """测试复杂表达式计算"""
        result = MathProcess.calculate_expression(
            left="100",
            operator=MathOperatorType.DIV,
            right="7",
            handle_method=MathRoundType.ROUND,
            precision=3,
        )
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 14.286, places=3)


if __name__ == "__main__":
    unittest.main()
