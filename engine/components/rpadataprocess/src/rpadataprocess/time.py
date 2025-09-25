import copy
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem, TimeFormatType
from rpaatomic.atomic import atomicMg
from rpaatomic.types import Date
from rpadataprocess import TimeChangeType, TimestampUnitType, TimeUnitType, TimeZoneType


class TimeProcess:
    @staticmethod
    @atomicMg.atomic("TimeProcess", outputList=[atomicMg.param("current_time", types="Date")])
    def get_current_time(time_format: TimeFormatType = TimeFormatType.YMD_HMS):
        res = Date()
        res.format = time_format
        return res

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
            atomicMg.param(
                "seconds",
                dynamics=[
                    DynamicsItem(
                        key="$this.seconds.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
            atomicMg.param(
                "minutes",
                dynamics=[
                    DynamicsItem(
                        key="$this.minutes.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
            atomicMg.param(
                "hours",
                dynamics=[
                    DynamicsItem(
                        key="$this.hours.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
            atomicMg.param(
                "days",
                dynamics=[
                    DynamicsItem(
                        key="$this.days.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
            atomicMg.param(
                "months",
                dynamics=[
                    DynamicsItem(
                        key="$this.months.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
            atomicMg.param(
                "years",
                dynamics=[
                    DynamicsItem(
                        key="$this.years.show",
                        expression="return $this.change_type.value != '{}'".format(TimeChangeType.MAINTAIN.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("set_time", types="Date")],
    )
    def set_time(
        time: Date,
        change_type: TimeChangeType = TimeChangeType.MAINTAIN,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        months: int = 0,
        years: int = 0,
    ):
        res = copy.deepcopy(time)
        if change_type == TimeChangeType.ADD:
            res.time += relativedelta(
                years=years,
                months=months,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            )
        elif change_type == TimeChangeType.SUB:
            res.time -= relativedelta(
                years=years,
                months=months,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            )
        return res

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            )
        ],
        outputList=[atomicMg.param("converted_timestamp", types="Int")],
    )
    def time_to_timestamp(time: Date, timestamp_unit: TimestampUnitType = TimestampUnitType.SECOND):
        if timestamp_unit == TimestampUnitType.SECOND:
            return int(time.time.timestamp())
        elif timestamp_unit == TimestampUnitType.MILLISECOND:
            return int(time.time.timestamp() * 1000)
        elif timestamp_unit == TimestampUnitType.MICROSECOND:
            return int(time.time.timestamp() * 1000000)

    @staticmethod
    @atomicMg.atomic("TimeProcess", outputList=[atomicMg.param("converted_time", types="Date")])
    def timestamp_to_time(timestamp: int, time_zone: TimeZoneType = TimeZoneType.LOCAL):
        if 10 < len(str(timestamp)) <= 13:  # 毫秒级时间戳
            timestamp = timestamp / 1000
        elif 13 < len(str(timestamp)) <= 16:  # 微秒级时间戳
            timestamp = timestamp / 1000000
        time_obj = Date()
        if time_zone == TimeZoneType.UTC:
            time_obj.time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        elif time_zone == TimeZoneType.LOCAL:
            time_obj.time = datetime.fromtimestamp(timestamp)
        return time_obj

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time_1",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
            atomicMg.param(
                "time_2",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
        ],
        outputList=[atomicMg.param("time_difference", types="Int")],
    )
    def get_time_difference(time_1: Date, time_2: Date, time_unit: TimeUnitType = TimeUnitType.SECOND):
        time_difference = abs((time_2.time - time_1.time).total_seconds())
        # 根据所需的时间单位转换差值
        if time_unit == TimeUnitType.SECOND:
            return int(time_difference)
        elif time_unit == TimeUnitType.MINUTE:
            return int(time_difference / 60)
        elif time_unit == TimeUnitType.HOUR:
            return int(time_difference / 3600)
        elif time_unit == TimeUnitType.DAY:
            return int(time_difference / 86400)
        elif time_unit in {TimeUnitType.MONTH, TimeUnitType.YEAR}:
            delta = relativedelta(time_2.time, time_1.time)
            if time_unit == TimeUnitType.MONTH:
                return delta.years * 12 + delta.months  # 计算总月数
            elif time_unit == TimeUnitType.YEAR:
                return delta.years  # 直接返回年数
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
        ],
        outputList=[atomicMg.param("format_datetime", types="Str")],
    )
    def format_datetime(time: Date, format_type: TimeFormatType = TimeFormatType.YMD_HMS):
        time.format = format_type
        return time.__str__()
