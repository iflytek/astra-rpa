import re
from typing import Any, List, Union

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel, field_validator, model_validator


def params_filter(req, model, **kwargs) -> Any:
    """从req中选择模型所需要的参数"""
    required_attrs = list(model.__annotations__.keys())
    req.update(kwargs)
    req = {key: values for key, values in req.items() if key in required_attrs}
    return model(**req)


class FrequencyRegularTime(BaseModel):
    time_expression: str

    def __str__(self):
        return f"FrequencyRegularTime: (time_expression={self.time_expression})"

    def to_crontab(self):
        pattern = r"(\d{4})-(\d{1,2})-(\d{1,2}) (\d{2}):(\d{2}):(\d{2})"
        match = re.match(pattern, self.time_expression)

        year = int(match.group(1))  # 2025
        month = int(match.group(2))  # 3
        day = int(match.group(3))  # 11
        hour = int(match.group(4))  # 21
        minute = int(match.group(5))  # 33
        second = int(match.group(6))  # 24

        return f"{year} {month} {day} {hour} {minute} {second}"


class FrequencyMinutes(BaseModel):
    minutes: int

    def __str__(self):
        return f"FrequencyMinutes: (minute={self.minutes})"

    @field_validator("minutes")
    def check_valid_m(cls, m):
        valid_minutes = range(0, 60)
        if int(m) not in valid_minutes:
            raise ValueError(f"{m} is not a valid minute of the time")
        return int(m)

    def to_crontab(self):
        return f"{int(self.minutes)} * * * *"


class FrequencyHours(BaseModel):
    hours: int
    minutes: int

    def __str__(self):
        return f"FrequencyHours: (minute={self.minutes}, Hours={self.hours})"

    @model_validator(mode="before")
    def check_valid_combination(cls, values):
        m = int(values.get("minutes"))
        h = int(values.get("hours"))

        if m is None or h is None:
            raise ValueError("'Minutes' and 'Hours' must be set.")

        # validate minute
        if m not in range(0, 60):
            raise ValueError(f"{m} is not a valid minute, must be between 0 and 59.")

        # validate hours
        if h not in range(0, 25):
            raise ValueError(f"{h} is not a valid hours, must be between 0 and 23.")

        return values

    def to_crontab(self):
        return f"{int(self.minutes)} {int(self.hours)} * * *"


class FrequencyDays(BaseModel):
    minutes: int
    hours: int

    def __str__(self):
        return f"FrequencyDays: (minute={self.minutes}, Hours={self.hours})"

    @model_validator(mode="before")
    def check_valid_combination(cls, values):
        m = int(values.get("minutes"))
        h = int(values.get("hours"))

        if m is None or h is None:
            raise ValueError("'Minutes' and 'Hours' must be set.")

        # validate minute
        if m not in range(0, 60):
            raise ValueError(f"{m} is not a valid minute, must be between 0 and 59.")

        # validate hours
        if h not in range(0, 25):
            raise ValueError(f"{h} is not a valid hours, must be between 0 and 23.")

        return values

    def to_crontab(self):
        return f"{int(self.minutes)} {int(self.hours)} * * *"


class FrequencyWeeks(BaseModel):
    weeks: List[int]
    hours: int
    minutes: int

    def __str__(self):
        return f"FrequencyWeeks: (minute={self.minutes}, Hours={self.hours}, Weeks={self.Weeks})"

    @model_validator(mode="before")
    def check_valid_combination(cls, values):
        m = int(values.get("minutes"))
        h = int(values.get("hours"))
        ws = values.get("weeks")

        if m is None or h is None or ws is None:
            raise ValueError("'Minutes' and 'Hours' and 'Weeks' must be set.")

        # validate minute
        if m not in range(0, 60):
            raise ValueError(f"{m} is not a valid minute, must be between 0 and 59.")

        # validate hours
        if h not in range(0, 25):
            raise ValueError(f"{h} is not a valid hours, must be between 0 and 23.")

        # validate weeks
        if not all(int(w) in range(0, 7) for w in ws):
            raise ValueError(f"{ws} is not a valid weeks. Must be between 0 and 6.")

        return values

    def to_crontab(self):
        week_expression = ",".join(map(str, self.weeks))
        return f"{int(self.minutes)} {int(self.hours)} * * {week_expression}"


class FrequencyMonths(BaseModel):
    months: List[int]
    weeks: List[int]
    hours: int
    minutes: int

    def __str__(self):
        return f"FrequencyDays: (minute={self.minutes}, Hours={self.hours}, Weeks={self.weeks}, Months={self.months})"

    @model_validator(mode="before")
    def check_valid_combination(cls, values):
        m = int(values.get("minutes"))
        h = int(values.get("hours"))
        ws = values.get("weeks")
        ms = values.get("months")

        if m is None or h is None or ws is None or ms is None:
            raise ValueError("'Minutes' and 'Hours' and 'Weeks' and 'Months' must be set.")

        # validate minute
        if m not in range(0, 60):
            raise ValueError(f"{m} is not a valid minute, must be between 0 and 59.")

        # validate hours
        if h not in range(0, 25):
            raise ValueError(f"{h} is not a valid hours, must be between 0 and 23.")

        # validate weeks
        if not all(int(w) in range(0, 7) for w in ws):
            raise ValueError(f"{ws} is not a valid weeks, must be between 0 and 6.")

        # validate months
        if not all(int(m) in range(1, 13) for m in ms):
            raise ValueError(f"{ms} is not a valid months, must be between 1 and 12.")

        return values

    def to_crontab(self):
        week_expression = ",".join(map(str, self.weeks))
        month_expression = ",".join(map(str, self.months))
        return f"{self.minutes} {self.hours} * {month_expression} {week_expression}"


class FrequencyAdvance(BaseModel):
    cron_expression: str

    def __str__(self):
        return f"FrequencyAdvance: (cron_expression={self.cron_expression})"

    def to_crontab(self):
        return self.cron_expression


class ScheduledTask:
    def __init__(self, end_time: str = None, **kwargs):
        """
        构建定时任务的类

        end_time: `str`, 是否启用结束时间
        Kwargs: 该参数用于构建任务的详细参数状态
            - frequency_flag: 对应不同任务频率类型，支持传入`Minutes`、`Hours`、`Days`、`Weeks`、`Months`、`Advance`
            - end_time: 用于判断停止时间，默认为空表示不填写停止时间
            - minutes: `int`, 支持[0, 60)
            - hours: `int`, 支持[0, 24)
            - weeks: `List`, 星期列表, 例如[1 ,3, 5]代表周一、周三、周五
            - months: `List`, 月份列表, 例如[1 ,3, 5]代表一月、三月、五月
            - expression: 高级自定义表达式

        """
        self.f_model = None
        self.f = kwargs.get("frequency_flag")  # 该f用于控制调度的频率
        self._end_time: str = end_time
        if not self.f:
            raise Exception

        self._init_f_model(kwargs)

    def _init_f_model(self, kwargs: dict):
        """
        初始化频率模型
        """
        m = {
            "regular": FrequencyRegularTime,
            "minutes": FrequencyMinutes,
            "hours": FrequencyHours,
            "days": FrequencyDays,
            "weeks": FrequencyWeeks,
            "months": FrequencyMonths,
            "advance": FrequencyAdvance,
        }
        fm = m.get(self.f)
        if not fm:
            raise Exception("该选择正确的频次选项")

        self.f_model = params_filter(kwargs, fm)

    def to_crontab(self):
        return self.f_model.to_crontab()

    async def callback(self) -> bool:
        """
        检查回调

        :return
            `bool`, 标识是否调度成功
        """

        return True

    def to_trigger(self) -> Union[CronTrigger, IntervalTrigger]:
        """获取该类任务的触发器模型"""
        cron_expression = self.to_crontab()
        cron_fields = cron_expression.split()
        cron_fields = [int(x) if x.isdigit() else x for x in cron_fields]

        if self.f == "regular":
            _datetime = {
                "year": cron_fields[0],
                "month": cron_fields[1],
                "day": cron_fields[2],
                "hour": cron_fields[3],
                "minute": cron_fields[4],
                "second": cron_fields[5],
            }
            trigger = CronTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "minutes":
            _datetime = {"minutes": int(cron_fields[0])}
            trigger = IntervalTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "hours":
            _datetime = {"minutes": cron_fields[0], "hours": cron_fields[1]}
            trigger = IntervalTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "days":
            _datetime = {"minute": cron_fields[0], "hour": cron_fields[1]}
            trigger = CronTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "weeks":
            _datetime = {
                "minute": cron_fields[0],
                "hour": cron_fields[1],
                "day_of_week": cron_fields[4],
            }
            trigger = CronTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "months":
            _datetime = {
                "minute": cron_fields[0],
                "hour": cron_fields[1],
                "month": cron_fields[3],
                "day_of_week": cron_fields[4],
            }
            trigger = CronTrigger(end_date=self._end_time, **_datetime)
        elif self.f == "advance":
            _datetime = {
                "minute": cron_fields[0],
                "hour": cron_fields[1],
                "day": cron_fields[2],
                "month": cron_fields[3],
                "day_of_week": cron_fields[4],
            }
            trigger = CronTrigger(end_date=self._end_time, **_datetime)
        else:
            raise NotImplementedError

        return trigger
