import asyncio
import threading
from queue import Queue
from typing import Optional

from rpaatomic import ReportFlow, ReportFlowStatus, ReportType

from rpa_executor import ExecuteStatus, ProcessInfo, ProjectInfo
from rpa_executor.error import *
from rpa_executor.flow.atomic import Atomic
from rpa_executor.flow.params import Params
from rpa_executor.flow.report import report
from rpa_executor.flow.storage import HttpStorage, Storage
from rpa_executor.flow.syntax import Job
from rpa_executor.flow.syntax.event import EventKey, EventStopReason


class SyncMap:
    def __init__(self):
        self.lock = threading.Lock()
        self.map = {}

    def __setitem__(self, key, value):
        with self.lock:
            self.map[key] = value

    def __getitem__(self, key):
        with self.lock:
            return self.map.get(key)

    def __delitem__(self, key):
        with self.lock:
            if key in self.map:
                del self.map[key]

    def __contains__(self, key):
        with self.lock:
            return key in self.map


class Svc:
    def __init__(
        self,
        cache_dir,
        gateway_port,
        project_id,
        port,
        debug: bool = False,
        log_ws: bool = True,
        exec_id: str = "",
        mode: str = "",
        recording_config: dict = None,
        run_param: list = None,
        project_name: str = "",
        version: str = "",
    ):
        """程序上下文管理类"""

        # 运行配置
        self.port: str = port
        self.log_ws: bool = log_ws
        self.debug: bool = debug
        self.line_debug: str = ""  # 单行debug
        self.cache_dir: str = cache_dir
        self.gateway_port: str = gateway_port
        self.exec_id = exec_id
        self.recording_config: dict = recording_config
        self.run_param: list = run_param

        self.global_id2name: dict = {}
        self.process_dict: dict[str, ProcessInfo] = {}
        self.project_dict: dict[str, ProjectInfo] = {}
        self.start_process_id = ""  # 启动的流程id
        self.start_project_id = project_id  # 启动的project_id
        self.start_project_name = project_name  # 启动的project_name

        # 运行事件
        self.events: SyncMap = SyncMap()

        # 日志
        self.report_queue = Queue(maxsize=1000)
        self.report = report
        self.report.code.set_config(self.log_ws, self.report_queue, project_id, self.exec_id)

        # 运行工具
        self.ws = None
        self.storage: Storage = HttpStorage(self.gateway_port, self)
        self.atomic: Job = Atomic(self.report, self.storage)
        self.params: Optional[Params] = Params(self)

        # 退出锁
        self.sys_exit_lock = threading.Lock()
        self.sys_exit_lock_end = False

    def event_stop(self, is_kill: bool = False):
        if is_kill:
            self.events[EventKey.Stop.value] = EventStopReason.Kill.value
        else:
            self.events[EventKey.Stop.value] = EventStopReason.Close.value

    async def event_pause(self, is_pause: bool = True):
        if is_pause:
            self.events[EventKey.ResPause.value] = False
            self.events[EventKey.Pause.value] = True
            while not (self.events.get(EventKey.ResPause.value)):
                await asyncio.sleep(0.1)
        else:
            self.events[EventKey.ResPause.value] = True
            self.events[EventKey.Pause.value] = False
            while self.events.get(EventKey.ResPause.value):
                await asyncio.sleep(0.1)

    async def event_continue(self):
        self.events[EventKey.ResContinue.value] = False
        self.events[EventKey.Continue.value] = True
        while not (self.events.get(EventKey.ResContinue.value)):
            await asyncio.sleep(0.1)

    async def event_next(self):
        self.events[EventKey.ResNext.value] = False
        self.events[EventKey.Next.value] = True
        while not (self.events.get(EventKey.ResNext.value)):
            await asyncio.sleep(0.1)

    def event_break(self) -> dict:
        if EventKey.Break.value not in self.events:
            self.events[EventKey.Break.value] = {}
        return self.events[EventKey.Break.value]

    def sys_exit(self, is_abort):
        # 有锁且，标志位是fase的时候触发，其他情况下等待锁完成后结束
        with self.sys_exit_lock:
            if not self.sys_exit_lock_end:
                svc = self
                # 如果中止了，需要补充日志
                if is_abort:
                    svc.report.info(
                        ReportFlow(
                            log_type=ReportType.Flow,
                            status=ReportFlowStatus.TASK_END,
                            result=ExecuteStatus.CANCEL.value,
                            msg_str=ReportFlowTaskEndUserClose,
                        )
                    )
                    svc.storage.report_status_upload("cancel", ReportFlowTaskEndUserClose)
                # 补充日志结束
                svc.report.code.close()
                self.sys_exit_lock_end = True
