import threading
from collections import deque
from typing import Optional

from ..core.config import config
from ..core.logger import logger
from ..core.queue_manager import TaskQueueManager
from ..terminal import Terminal
from ..trigger import Trigger


class AppContext:
    """应用程序上下文管理器，用于管理全局状态和组件实例"""

    def __init__(self):
        # 核心组件
        self.trigger: Optional[Trigger] = None
        self.terminal: Optional[Terminal] = None
        self.task_queue_mgr: Optional[TaskQueueManager] = None

        # 队列配置
        self.queue_config = {
            "max_length": 500,  # 最大队列长度
            "max_wait_minutes": 30,  # 最大等待时间（分钟）
            "deduplicate": False,  # 是否去重
        }

        # 用于监控的队列，存储当前正在排队的任务信息
        self.task_queue_monitor = deque(maxlen=1000)  # 设置最大长度为1000，防止内存溢出

        # 线程管理
        self._threads = []

    async def initialize(self):
        """初始化应用程序上下文"""
        logger.info("开始初始化应用程序上下文")

        # 初始化触发器
        await self._init_trigger()

        # 初始化任务队列管理器
        self._init_task_queue_manager()

        # 初始化终端（如果需要）
        if config.TERMINAL_MODE:
            await self._init_terminal()

        logger.info("应用程序上下文初始化完成")

    async def _init_trigger(self):
        """初始化触发器"""
        self.trigger = Trigger()  # 一定要在异步里面启动Trigger，他会New一个AsyncIOScheduler()
        logger.info("trigger初始化成功")

    def _init_task_queue_manager(self):
        """初始化任务队列管理器"""
        if not self.trigger:
            raise RuntimeError("trigger必须在task_queue_manager之前初始化")

        self.task_queue_mgr = TaskQueueManager(
            self.task_queue_monitor,
            self.trigger.queue,
            self,  # 传入 self (app_context)
        )
        self.task_queue_mgr.set_trigger(self.trigger)

        # 启动任务队列管理线程
        fetch_thread = threading.Thread(target=self.task_queue_mgr.fetch_tasks, daemon=True)
        process_thread = threading.Thread(target=self.task_queue_mgr.process_tasks, daemon=True)

        fetch_thread.start()
        process_thread.start()

        self._threads.extend([fetch_thread, process_thread])
        logger.info("任务队列管理器初始化成功")

    async def _init_terminal(self):
        """初始化终端（仅在TERMINAL_MODE下）"""
        if not self.trigger:
            raise RuntimeError("trigger必须在terminal之前初始化")

        self.trigger.delete_all_tasks()

        if not self.terminal:
            self.terminal = Terminal(self.task_queue_monitor, self.trigger.queue, self.trigger.scheduler)
            logger.info("terminal初始化成功")

        self.terminal.start_poll()  # 启动terminal轮询线程

    def update_config(self, terminal_mode: bool):
        """更新配置"""
        config.TERMINAL_MODE = terminal_mode

        self.trigger.delete_all_tasks()

        if self.terminal:
            self.terminal.stop_poll()  # 停止terminal轮询线程

        if config.TERMINAL_MODE:
            if not self.terminal:
                self.terminal = Terminal(self.task_queue_monitor, self.trigger.queue, self.trigger.scheduler)
                logger.info("terminal重新初始化成功")
            self.terminal.start_poll()
        else:
            self.trigger.to_native()

    def get_active_threads(self):
        """获取活跃线程列表"""
        return [t for t in self._threads if t.is_alive()]


# 全局应用程序上下文实例
app_context = AppContext()
