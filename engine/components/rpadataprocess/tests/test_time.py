import unittest
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from rpaatomic import *
from rpaatomic.types import Date
from rpadataprocess import TimeChangeType, TimestampUnitType, TimeUnitType, TimeZoneType
from rpadataprocess.time import TimeProcess


class TestTimeProcess(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.test_datetime = datetime(2023, 12, 25, 10, 30, 45)
        self.test_date = Date()
        self.test_date.time = self.test_datetime
        self.test_date.format = TimeFormatType.YMD_HMS

    def test_get_current_time_success(self):
        """测试获取当前时间成功"""
        result = TimeProcess.get_current_time(time_format=TimeFormatType.YMD_HMS)

        self.assertIsInstance(result, Date)
        self.assertEqual(result.format, TimeFormatType.YMD_HMS)

    def test_get_current_time_with_different_format(self):
        """测试不同格式获取当前时间"""
        result = TimeProcess.get_current_time(time_format=TimeFormatType.YMD)

        self.assertIsInstance(result, Date)
        self.assertEqual(result.format, TimeFormatType.YMD)

    def test_set_time_maintain(self):
        """测试设置时间 - 保持模式"""
        original_time = self.test_date.time
        result = TimeProcess.set_time(time=self.test_date, change_type=TimeChangeType.MAINTAIN)

        self.assertEqual(result.time, original_time)

    def test_set_time_add(self):
        """测试设置时间 - 增加模式"""
        original_time = self.test_date.time
        result = TimeProcess.set_time(time=self.test_date, change_type=TimeChangeType.ADD, days=1, hours=2)

        expected_time = original_time + relativedelta(days=1, hours=2)
        self.assertEqual(result.time, expected_time)

    def test_set_time_subtract(self):
        """测试设置时间 - 减少模式"""
        original_time = self.test_date.time
        result = TimeProcess.set_time(time=self.test_date, change_type=TimeChangeType.SUB, days=1, hours=2)

        expected_time = original_time - relativedelta(days=1, hours=2)
        self.assertEqual(result.time, expected_time)

    def test_set_time_with_all_parameters(self):
        """测试设置时间 - 所有参数"""
        original_time = self.test_date.time
        result = TimeProcess.set_time(
            time=self.test_date,
            change_type=TimeChangeType.ADD,
            seconds=30,
            minutes=15,
            hours=3,
            days=5,
            months=2,
            years=1,
        )

        expected_time = original_time + relativedelta(seconds=30, minutes=15, hours=3, days=5, months=2, years=1)
        self.assertEqual(result.time, expected_time)

    def test_time_to_timestamp_second(self):
        """测试时间转时间戳 - 秒级"""
        result = TimeProcess.time_to_timestamp(time=self.test_date, timestamp_unit=TimestampUnitType.SECOND)

        expected_timestamp = int(self.test_datetime.timestamp())
        self.assertEqual(result, expected_timestamp)

    def test_time_to_timestamp_millisecond(self):
        """测试时间转时间戳 - 毫秒级"""
        result = TimeProcess.time_to_timestamp(time=self.test_date, timestamp_unit=TimestampUnitType.MILLISECOND)

        expected_timestamp = int(self.test_datetime.timestamp() * 1000)
        self.assertEqual(result, expected_timestamp)

    def test_time_to_timestamp_microsecond(self):
        """测试时间转时间戳 - 微秒级"""
        result = TimeProcess.time_to_timestamp(time=self.test_date, timestamp_unit=TimestampUnitType.MICROSECOND)

        expected_timestamp = int(self.test_datetime.timestamp() * 1000000)
        self.assertEqual(result, expected_timestamp)

    def test_timestamp_to_time_local(self):
        """测试时间戳转时间 - 本地时区"""
        timestamp = int(self.test_datetime.timestamp())
        result = TimeProcess.timestamp_to_time(timestamp=timestamp, time_zone=TimeZoneType.LOCAL)

        self.assertIsInstance(result, Date)
        self.assertEqual(result.time, self.test_datetime)

    def test_timestamp_to_time_utc(self):
        """测试时间戳转时间 - UTC时区"""
        utc_datetime = datetime(2023, 12, 25, 10, 30, 45, tzinfo=timezone.utc)
        timestamp = int(utc_datetime.timestamp())
        result = TimeProcess.timestamp_to_time(timestamp=timestamp, time_zone=TimeZoneType.UTC)

        self.assertIsInstance(result, Date)
        self.assertEqual(result.time, utc_datetime)

    def test_timestamp_to_time_millisecond(self):
        """测试毫秒级时间戳转时间"""
        timestamp = int(self.test_datetime.timestamp() * 1000)
        result = TimeProcess.timestamp_to_time(timestamp=timestamp, time_zone=TimeZoneType.LOCAL)

        self.assertIsInstance(result, Date)
        # 由于精度问题，比较到秒级
        self.assertEqual(int(result.time.timestamp()), int(self.test_datetime.timestamp()))

    def test_timestamp_to_time_microsecond(self):
        """测试微秒级时间戳转时间"""
        timestamp = int(self.test_datetime.timestamp() * 1000000)
        result = TimeProcess.timestamp_to_time(timestamp=timestamp, time_zone=TimeZoneType.LOCAL)

        self.assertIsInstance(result, Date)
        # 由于精度问题，比较到秒级
        self.assertEqual(int(result.time.timestamp()), int(self.test_datetime.timestamp()))

    def test_get_time_difference_seconds(self):
        """测试计算时间差 - 秒级"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 30, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 10, 30, 30)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.SECOND)
        self.assertEqual(result, 30)

    def test_get_time_difference_minutes(self):
        """测试计算时间差 - 分钟级"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 30, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 10, 32, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.MINUTE)
        self.assertEqual(result, 2)

    def test_get_time_difference_hours(self):
        """测试计算时间差 - 小时级"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 0, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 13, 0, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.HOUR)
        self.assertEqual(result, 3)

    def test_get_time_difference_days(self):
        """测试计算时间差 - 天级"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 0, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 28, 10, 0, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.DAY)
        self.assertEqual(result, 3)

    def test_get_time_difference_months(self):
        """测试计算时间差 - 月级"""
        time_1 = Date()
        time_1.time = datetime(2023, 1, 1, 10, 0, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 3, 1, 10, 0, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.MONTH)
        self.assertEqual(result, 2)

    def test_get_time_difference_years(self):
        """测试计算时间差 - 年级"""
        time_1 = Date()
        time_1.time = datetime(2020, 1, 1, 10, 0, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 1, 1, 10, 0, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.YEAR)
        self.assertEqual(result, 3)

    def test_get_time_difference_reverse_order(self):
        """测试计算时间差 - 时间顺序颠倒"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 30, 30)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 10, 30, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.SECOND)
        self.assertEqual(result, 30)  # 应该返回绝对值

    def test_format_datetime_ymd_hms(self):
        """测试格式化时间 - YMD_HMS格式"""
        result = TimeProcess.format_datetime(time=self.test_date, format_type=TimeFormatType.YMD_HMS)

        expected_format = "2023-12-25 10:30:45"
        self.assertEqual(result, expected_format)

    def test_format_datetime_ymd(self):
        """测试格式化时间 - YMD格式"""
        result = TimeProcess.format_datetime(time=self.test_date, format_type=TimeFormatType.YMD)

        expected_format = "2023-12-25"
        self.assertEqual(result, expected_format)

    def test_format_datetime_ym(self):
        """测试格式化时间 - YM格式"""
        result = TimeProcess.format_datetime(time=self.test_date, format_type=TimeFormatType.YMD)

        expected_format = "2023-12-25"
        self.assertEqual(result, expected_format)

    def test_format_datetime_hms(self):
        """测试格式化时间 - HMS格式"""
        result = TimeProcess.format_datetime(time=self.test_date, format_type=TimeFormatType.HMS)

        expected_format = "10:30:45"
        self.assertEqual(result, expected_format)

    def test_format_datetime_hm(self):
        """测试格式化时间 - HM格式"""
        result = TimeProcess.format_datetime(time=self.test_date, format_type=TimeFormatType.HM)

        expected_format = "10:30"
        self.assertEqual(result, expected_format)

    def test_get_time_difference_invalid_unit(self):
        """测试计算时间差 - 无效时间单位"""
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 30, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 10, 30, 30)

        # 测试无效的时间单位
        with self.assertRaises(NotImplementedError):
            TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit="INVALID_UNIT")

    def test_set_time_edge_cases(self):
        """测试设置时间的边界情况"""
        # 测试零值
        result = TimeProcess.set_time(
            time=self.test_date,
            change_type=TimeChangeType.ADD,
            seconds=0,
            minutes=0,
            hours=0,
            days=0,
            months=0,
            years=0,
        )
        self.assertEqual(result.time, self.test_date.time)

        # 测试负数
        original_time = self.test_date.time
        result = TimeProcess.set_time(time=self.test_date, change_type=TimeChangeType.ADD, days=-1)
        expected_time = original_time + relativedelta(days=-1)
        self.assertEqual(result.time, expected_time)

    def test_timestamp_edge_cases(self):
        """测试时间戳转换的边界情况"""
        # 测试零时间戳
        result = TimeProcess.timestamp_to_time(timestamp=0, time_zone=TimeZoneType.LOCAL)
        self.assertIsInstance(result, Date)

        # 测试1970年1月1日
        epoch_timestamp = 0
        result = TimeProcess.timestamp_to_time(timestamp=epoch_timestamp, time_zone=TimeZoneType.LOCAL)
        expected_time = datetime.fromtimestamp(0)
        self.assertEqual(result.time, expected_time)

    def test_time_difference_edge_cases(self):
        """测试时间差计算的边界情况"""
        # 测试相同时间
        time_1 = Date()
        time_1.time = datetime(2023, 12, 25, 10, 30, 0)

        time_2 = Date()
        time_2.time = datetime(2023, 12, 25, 10, 30, 0)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.SECOND)
        self.assertEqual(result, 0)

        # 测试跨年
        time_1.time = datetime(2022, 12, 31, 23, 59, 59)
        time_2.time = datetime(2023, 1, 1, 0, 0, 1)

        result = TimeProcess.get_time_difference(time_1=time_1, time_2=time_2, time_unit=TimeUnitType.SECOND)
        self.assertEqual(result, 2)

    def test_format_datetime_edge_cases(self):
        """测试格式化时间的边界情况"""
        # 测试午夜时间
        midnight_date = Date()
        midnight_date.time = datetime(2023, 12, 25, 0, 0, 0)
        midnight_date.format = TimeFormatType.YMD_HMS

        result = TimeProcess.format_datetime(time=midnight_date, format_type=TimeFormatType.YMD_HMS)
        self.assertEqual(result, "2023-12-25 00:00:00")

        # 测试年末
        year_end_date = Date()
        year_end_date.time = datetime(2023, 12, 31, 23, 59, 59)
        year_end_date.format = TimeFormatType.YMD_HMS

        result = TimeProcess.format_datetime(time=year_end_date, format_type=TimeFormatType.YMD_HMS)
        self.assertEqual(result, "2023-12-31 23:59:59")


if __name__ == "__main__":
    unittest.main()
