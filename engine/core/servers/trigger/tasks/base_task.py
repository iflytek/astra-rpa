import asyncio
from datetime import datetime
from queue import Queue
from typing import List, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from tzlocal import get_localzone

from .. import CONVERT_COLUMN
from ..server.gateway_client import get_executor_status, send_msg
from ..tasks.file_task import FileTask
from ..tasks.hotkey_task import HotKeyTask
from ..tasks.mail_task import MailTask
from ..tasks.scheduled_task import ScheduledTask


class Task:
    def __init__(
        self,
        trigger_id: str,
        trigger_name: str,
        task_type: str,
        enable: bool,
        queue_enable: bool,
        q: Queue,
        callback_project_ids: List,
        exceptional: str,
        timeout: int,
        mode: str,
        screen_record_enable: bool = False,
        open_virtual_desk: bool = False,
        **kwargs,
    ):
        """
        任务模型

        Args:
            trigger_id: `str`, 任务id
            trigger_name: `str`, 任务名称
            task_type: `str`, 任务类型，仅支持`scheduled`、`mail`、`hotkey`、`file`
            enable: `bool`, 启动状态
            queue_enable: `bool`, 是否启用队列
            queue: `asyncio.Queue`, 队列（全局）
            callback_project_ids: `List`, 回调使用的工程id列表
            exceptional: str, 异常处理方式， 支持`skip`或者`stop`
            timeout: int, 工程超时时间， 默认9999
            task_params: 构建task的相关参数, 具体查阅实现类

        """
        self.trigger_id: str = trigger_id
        self.trigger_name: str = trigger_name
        self.task_type: str = task_type
        self.enable: bool = enable
        self.queue_enable: bool = queue_enable
        self.queue: Queue = q
        self.exceptional: str = exceptional
        self.timeout: int = timeout
        self.callback_project_ids: List = callback_project_ids
        self.trigger_json: dict = kwargs
        self.time = datetime.now(tz=get_localzone())
        self.screen_record_enable = screen_record_enable if screen_record_enable else False
        self.open_virtual_desk = open_virtual_desk if open_virtual_desk else False

        # 新增mode字段，用于区分远程下发（DISPATCH）
        self.mode: str = mode
        self.kwargs: dict = {}

        for col_value in CONVERT_COLUMN.values():
            try:
                value = getattr(self, col_value)
            except AttributeError:
                continue
            if isinstance(value, dict):
                # 这里有拆包
                self.kwargs.update(value)
            else:
                self.kwargs[col_value] = value

        self.kwargs.update(kwargs)

        self.minor_task: Union[ScheduledTask, MailTask, FileTask, HotKeyTask] = self._init_task_model(
            self.task_type, **kwargs
        )

    def _init_task_model(self, task_type: str, **kwargs) -> Union[ScheduledTask, MailTask, FileTask, HotKeyTask]:
        """
        初始化任务模型

        Args:
            - task_type: `str`, 判断任务类型，支持`scheduled`、`mail`、`hotkey`、`files`

        :param task_type:
        :param kwargs:
        :return:
        """
        if task_type == "schedule":
            m = ScheduledTask(**kwargs)
        elif task_type == "mail":
            m = MailTask(self.trigger_id, **kwargs)
        elif task_type == "file":
            m = FileTask(**kwargs)
        elif task_type == "hotKey":
            m = HotKeyTask(**kwargs)
        elif task_type == "manual":
            m = None
        else:
            raise NotImplemented
        return m

    def __dict__(self):
        return self.kwargs


class AsyncSchedulerTask(Task):
    def __init__(self, scheduler: AsyncIOScheduler, **kwargs):
        self.trigger: Union[CronTrigger, IntervalTrigger] = None
        self.scheduler = scheduler
        super().__init__(**kwargs)

    async def callback(self, *args) -> bool:
        """回调，进行任务触发"""

        # rtask是tasks里类的具体实现
        flag = await self.minor_task.callback()
        if not flag:
            return False

        status = get_executor_status()  # 调度器的执行状态
        # 第一种条件是判断不添加队列的情况
        # 第二种条件是队列可用
        if (not self.queue_enable and not status) or self.queue_enable:
            self.queue.put(self.__dict__())
            return True
        else:
            send_msg(
                {
                    "msg": "任务被占用，当前存在正在执行的任务，且该任务未开启排队逻辑",
                    "type": "tip",
                }
            )
            return False

    def create(self):
        """创建任务"""
        self.trigger = self.minor_task.to_trigger()
        self.job = self.scheduler.add_job(
            self.callback,  # 是本身的callback，用于和tasks的具体实现类的callback进行通信
            trigger=self.trigger,
            id=self.trigger_id,
        )

        if not self.enable:
            self.pause()

    def delete(self):
        """删除任务"""
        task = self.scheduler.get_job(self.trigger_id)
        if task:
            self.scheduler.remove_job(self.trigger_id)

    def pause(self):
        """停止任务"""
        self.job.pause()

    def resume(self):
        """恢复任务"""
        self.job.resume()

    def get_future_time(self, times: int = 3):
        """获取未来N次执行时间"""
        if not self.trigger:
            return []

        executions = []
        next_run = self.time
        # 获取未来N次执行时间
        for _ in range(times):
            next_run = self.trigger.get_next_fire_time(next_run, next_run)
            if next_run is None:
                break
            formatted_time = next_run.strftime("%Y-%m-%d %H:%M:%S")
            executions.append(formatted_time)

        return executions

    @classmethod
    def get_future_time_without_create(cls, trigger=None, times: int = 3):
        """获取未来N次执行时间(未创建任务情况下)"""
        if not trigger:
            return []

        executions = []
        next_run = datetime.now(tz=get_localzone())
        # 获取未来N次执行时间
        for _ in range(times):
            next_run = trigger.get_next_fire_time(next_run, next_run)
            if next_run is None:
                break
            formatted_time = next_run.strftime("%Y-%m-%d %H:%M:%S")
            executions.append(formatted_time)

        return executions


class AsyncOneCallTask(Task):
    def __init__(self, **kwargs):
        self.task: asyncio.Task = None
        self._run_event = asyncio.Event()
        super().__init__(**kwargs)

    async def callback(self, *args):
        """回调，进行任务触发"""
        q = asyncio.Queue()
        # 开始执行回调

        self.task = asyncio.create_task(self.minor_task.callback(q, args[0]))

        while True:
            flag = await q.get()
            if not flag:
                continue

            status = get_executor_status()
            # 没开排队且空闲 和 开了排队
            if (not self.queue_enable and not status) or self.queue_enable:
                self.queue.put(self.__dict__())
            else:
                send_msg(
                    {
                        "msg": "任务被占用，当前存在正在执行的任务，且该任务未开启排队逻辑",
                        "type": "tip",
                    }
                )
            continue

    def create(self):
        """创建任务"""
        asyncio.create_task(self.callback(self._run_event))

        if not self.enable:
            self.pause()

    def delete(self):
        """删除任务"""
        self.task.cancel()
        if hasattr(
            self.minor_task, "force_end_callback"
        ):  # 热键任务无法通过Asyncio.task.cancel直接取消，所以需要添加force_end_callback从内部取消
            self.minor_task.force_end_callback()

    def pause(self):
        """停止任务"""
        self._run_event.set()

    def resume(self):
        """恢复任务"""
        self._run_event.clear()


class AsyncImmediateTask(Task):
    """这是一个即时函数的调度类"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, *args):
        """
        该回调方法是获取立即执行对象的运行处理函数

        :return:
        """
        try:
            from ..core.app_context import app_context

            status = get_executor_status()
            # 检测队列里是否存在待排队工程，若存在则不投放入队列
            # 若处于调度模式，全排队
            if (self.enable and len(app_context.task_queue_monitor) == 0 and not status) or (self.mode == "DISPATCH"):
                self.queue.put(self.__dict__())
                return True
            return False
        except Exception as e:
            return False
