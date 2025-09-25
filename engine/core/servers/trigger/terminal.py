import asyncio
import threading
import time
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .core.logger import logger
from .server.gateway_client import (
    send_stop_list,
    terminal_list_task,
    terminal_poll_update,
)
from .tasks.base_task import AsyncImmediateTask, AsyncSchedulerTask


class Terminal:
    def __init__(self, global_deque, global_queue, global_scheduler):
        self.task_queue_monitor = global_deque
        self.queue = global_queue
        self.scheduler: AsyncIOScheduler = global_scheduler
        self.tasks = {}

        # terminal轮询线程控制
        self.poll_thread = None
        self.poll_stop_event = threading.Event()

    def terminal_poll_worker(self):
        """
        terminal轮询工作线程
        """
        logger.info("【terminal_poll_worker】terminal轮询线程启动")
        self.update_task_list()
        count = 1
        while not self.poll_stop_event.is_set():
            try:
                if count % 5 == 0:
                    flag = terminal_poll_update()
                    if flag:
                        logger.info("【terminal_poll_worker】terminal轮询结果：{}", flag)
                    if flag or count % 100 == 0:
                        # 处理terminal更新逻辑
                        self.update_task_list()
            except Exception as e:
                logger.error(f"【terminal_poll_worker】terminal轮询异常: {e}")
            finally:
                count += 1
                if count > 100:
                    count = 1
                time.sleep(1)

        logger.info("【terminal_poll_worker】terminal轮询线程停止")

    def start_poll(self):
        """
        启动terminal轮询线程
        """
        if self.poll_thread and self.poll_thread.is_alive():
            logger.warning("【start_poll】terminal轮询线程已在运行")
            return

        self.poll_stop_event.clear()
        self.poll_thread = threading.Thread(target=self.terminal_poll_worker, daemon=True)
        self.poll_thread.start()
        logger.info("【start_poll】terminal轮询线程启动成功")

    def stop_poll(self):
        """
        停止terminal轮询线程
        """
        if not self.poll_thread or not self.poll_thread.is_alive():
            logger.warning("【stop_poll】terminal轮询线程未运行")
            return

        logger.info("【stop_poll】正在停止terminal轮询线程")
        self.poll_stop_event.set()
        self.poll_thread.join(timeout=15)  # 等待最多5秒
        if self.poll_thread.is_alive():
            logger.warning("【stop_poll】terminal轮询线程未能在15秒内停止")
        else:
            logger.info("【stop_poll】terminal轮询线程已停止")

        self.delete_all_tasks()

    def update_task_list(self):
        # 请求全量任务列表
        new_task_list, retry_task_list, stop_task_list = terminal_list_task()
        new_task_ids = new_task_list.keys()
        # 和本地任务的交集、本地任务差集、云端任务差集

        intersection = [new_task_list.get(task_id) for task_id, task in self.tasks.items() if task_id in new_task_ids]
        local_tasks_unique = [task_id for task_id, task in self.tasks.items() if task_id not in new_task_ids]
        cloud_tasks_unique = [task for task_id, task in new_task_list.items() if task_id not in self.tasks.keys()]
        logger.info(f"【update_task_list】intersection本地、云端相交部分是：{intersection} ")
        logger.info(f"【update_task_list】local_tasks_unique本地独有任务：{local_tasks_unique} ")
        logger.info(f"【update_task_list】cloud_tasks_unique云端独有任务：{cloud_tasks_unique} ")

        # 本地任务差值，直接删除
        for task_id in local_tasks_unique:
            logger.info(f"【update_task_list】本地删除任务: {task_id}")
            self.delete_task(task_id)

        # 云端任务差值，直接添加
        for task in cloud_tasks_unique:
            logger.info(f"【update_task_list】云端添加任务: {task}")
            self.add_task(**task)

        # 本地计划任务交集，进行更新处理
        # intersection里拿的是新的
        for new_task in intersection:
            task = self.tasks[new_task["trigger_id"]]

            if task.kwargs == new_task:
                logger.info("【update_task_list】云端、本地任务ID相同，参数相同，不进行更新。 ")
                continue
            else:
                logger.info(f"【update_task_list】云端、本地任务ID相同，参数不同，进行更新：{new_task} ")
                self.update_task(**new_task)

        # 处理retry和stop任务
        for task in retry_task_list.values():
            task["task_type"] = "manual"
            logger.info(f"【retry_task】 重试任务: {task}")
            self.add_task(**task)

        if stop_task_list:
            for task in stop_task_list.values():
                logger.info(f"【stop_task】 停止任务: {task}")
                send_stop_list(task.get("trigger_id", None))

    def add_task(
        self,
        trigger_id: str,
        trigger_name: str,
        task_type: str,
        callback_project_ids: List,
        exceptional: str,
        timeout: int,
        queue_enable: bool,
        screen_record_enable: bool,
        open_virtual_desk: bool,
        **kwargs,
    ):
        """
        添加任务

        Args:
            trigger_id: 任务id
            trigger_name: 任务名称
            task_type: 任务类型
            callback_project_ids: 调度机器人信息
            exceptional: 异常处理方式
            timeout: 超时时间
            queue_enable: 是否启用队列
            screen_record_enable: 是否启用录屏
            open_virtual_desk: 是否启用虚拟桌面
            kwargs: 构建task的相关参数
        """

        task = self.get_task(trigger_id)
        if task and task_type != "manual":
            return False

        if task_type == "schedule":
            task = AsyncSchedulerTask(
                scheduler=self.scheduler,
                trigger_id=trigger_id,
                trigger_name=trigger_name,
                task_type=task_type,
                queue_enable=queue_enable,
                q=self.queue,
                callback_project_ids=callback_project_ids,
                exceptional=exceptional,
                timeout=timeout,
                screen_record_enable=screen_record_enable,
                open_virtual_desk=open_virtual_desk,
                **kwargs,
            )
            task.create()
            self.tasks[trigger_id] = task

        elif task_type == "manual":
            task = AsyncImmediateTask(
                trigger_id=trigger_id,
                trigger_name=trigger_name,
                task_type=task_type,
                queue_enable=queue_enable,
                q=self.queue,
                callback_project_ids=callback_project_ids,
                exceptional=exceptional,
                timeout=timeout,
                screen_record_enable=screen_record_enable,
                open_virtual_desk=open_virtual_desk,
                **kwargs,
            )
            flag = asyncio.run(task.callback())
            if flag:
                logger.info("任务调度成功")
            else:
                logger.info("任务调度失败，请检查是否已存在实例正在运行")

            del task
        else:
            raise Exception("不支持的任务类型: {}".format(task_type))
        return True

    def get_task(self, task_id: str):
        """
        获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务对象或None
        """
        return self.tasks.get(task_id)

    def delete_task(self, task_id: str):
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否删除成功
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"【delete_task】任务不存在: {task_id}")
            return False

        try:
            if hasattr(task, "delete"):
                task.delete()
            del self.tasks[task_id]
            logger.info(f"【delete_task】任务删除成功: {task_id}")
            return True
        except Exception as e:
            logger.error(f"【delete_task】删除任务异常: {task_id}, 错误: {e}")
            return False

    def update_task(self, **kwargs):
        """
        更新任务

        Args:
            **kwargs: 任务参数

        Returns:
            是否更新成功
        """
        task_id = kwargs.get("trigger_id")
        if not task_id:
            logger.error("【update_task】缺少taskId参数")
            return False

        try:
            # 先删除旧任务
            self.delete_task(task_id)
            # 再添加新任务
            return self.add_task(**kwargs)
        except Exception as e:
            logger.error(f"【update_task】更新任务异常: {task_id}, 错误: {e}")
            return False

    def delete_all_tasks(self):
        """
        删除所有任务
        """
        logger.info("【delete_all_tasks】: {}".format((self.tasks.keys())))
        task_keys = list(self.tasks.keys())
        for task_key in task_keys:
            logger.info("【delete_all_tasks】删除任务: {}".format(task_key))
            try:
                self.delete_task(task_key)
            except Exception as e:
                logger.error("【delete_all_tasks】删除任务失败: {}".format(e))
