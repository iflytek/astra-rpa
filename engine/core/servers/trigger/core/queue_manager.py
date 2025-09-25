import copy
import time
import uuid
from collections import deque

from ..core.config import config
from ..core.logger import logger
from ..server.gateway_client import execute_multiple_projects


class TaskQueueManager:
    def __init__(self, task_queue_monitor: deque, trigger_queue, app_context):
        self.task_queue_monitor = task_queue_monitor
        self.trigger_queue = trigger_queue
        self.app_context = app_context  # 直接引用 app_context
        self.trigger = None

    def set_trigger(self, trigger):
        """设置trigger实例"""
        self.trigger = trigger

    @property
    def queue_config(self):
        """动态获取队列配置"""
        return self.app_context.queue_config

    @staticmethod
    def is_task_timeout(task):
        """检查任务是否超时"""
        try:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            expire_time = task.get("expire_time", "")
            # 判断是否超时
            return time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")) > time.mktime(
                time.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            logger.error(f"检查任务是否超时失败: {e}")
            return False

    def fetch_tasks(self):
        """获取任务并添加到监控队列"""
        while True:
            if not self.trigger:
                time.sleep(1)
                continue
            task_info = self.trigger.queue.get()  # 会等待直到有为止
            if not task_info:
                time.sleep(1)
                continue
            logger.info(f"接收到触发任务, task_info: {task_info}")

            if len(self.task_queue_monitor) >= self.queue_config["max_length"]:
                logger.warning(f"任务队列已满，任务已丢弃: {task_info.get('trigger_id')}")
                continue

            # 使用深拷贝避免修改原始任务对象
            task_copy = copy.deepcopy(task_info)

            if not config.TERMINAL_MODE:
                # 检查是否需要去重
                if self.queue_config["deduplicate"]:
                    # 检查是否已存在相同trigger_id的任务
                    for task in self.task_queue_monitor:
                        if task.get("trigger_id") == task_copy.get("trigger_id"):
                            logger.info(f"任务已存在，跳过: {task_copy.get('trigger_id')}")
                            continue

            # 将任务信息添加到监控队列，并记录入队时间和过期时间
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            task_copy["enqueue_time"] = current_time
            # 计算过期时间
            expire_time = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(
                    time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S"))
                    + self.queue_config["max_wait_minutes"] * 60
                ),
            )
            task_copy["expire_time"] = expire_time
            # 添加唯一ID
            task_copy["unique_id"] = str(uuid.uuid4())
            self.task_queue_monitor.append(task_copy)

    def process_tasks(self):
        """处理监控队列中的任务"""
        while True:
            if not self.task_queue_monitor:
                time.sleep(1)
                continue

            task_info = self.task_queue_monitor[0]  # 只查看不移除

            # 检查任务是否是当前mode的
            if task_info.get("mode") == "DISPATCH" and not config.TERMINAL_MODE:
                self.task_queue_monitor.popleft()  # 下发前就移除第一个元素
                logger.info(f"任务模式为本地计划任务，已移除远程调度任务: {task_info.get('trigger_id')}")
                continue
            if task_info.get("mode") != "DISPATCH" and config.TERMINAL_MODE:
                self.task_queue_monitor.popleft()  # 下发前就移除第一个元素
                logger.info(f"任务模式为远程调度任务，已移除本地计划任务: {task_info.get('trigger_id')}")
                continue

            # 检查任务是否超时
            if self.is_task_timeout(task_info):
                self.task_queue_monitor.popleft()  # 移除超时任务
                logger.info(
                    f"任务等待时间超过{self.queue_config['max_wait_minutes']}分钟，已移除: {task_info.get('trigger_id')}"
                )
                continue

            self.task_queue_monitor.popleft()  # 下发前就移除第一个元素
            i = 0
            while True:
                success_flag = execute_multiple_projects(task_info)  # 调度调度器
                if not success_flag:
                    if i < 10:
                        i += 1
                    time.sleep(6 * i)  # 等待6*i秒后，重新下发【这里表示下发失败】
                    logger.info(f"重新下发, task_info: {task_info}")
                    continue
                # 任务执行完成后，从监控队列中移除
                break
