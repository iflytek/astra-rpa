from queue import Queue
from typing import Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .core.config import config
from .core.logger import logger
from .server.gateway_client import list_trigger
from .tasks.base_task import (
    AsyncImmediateTask,
    AsyncOneCallTask,
    AsyncSchedulerTask,
)


class Trigger:
    def __init__(self):
        self.tasks: dict[str, Union[AsyncSchedulerTask, AsyncOneCallTask, AsyncImmediateTask]] = {}
        self.queue: Queue = Queue(maxsize=1000)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def to_native(self, clear: bool = False):
        """从云端同步到本地并启动"""

        """
        1. 先聚合有robot_id有交集的部分，在分出没有交集的部分（分别是本地列表里的、云端下拉的）
        2. 本地列表里没有交集的部分，删除
        3. 云端下拉里没有交集的部分，新增
        4. 有交集的部分：
          4.1 判断值是否相等，相等不变
          4.2 不相等则重启并更新
        """

        try:
            if config.TERMINAL_MODE:
                # 如果是调度模式，略过更新
                return True

            # 从云端获取数据信息
            if not clear:
                triggers = list_trigger()
                if triggers is None:
                    # 如果服务端为空就直接结束
                    return True
            else:
                triggers = {}

            trigger_ids = triggers.keys()
            # 和本地任务的交集、本地任务差集、云端任务差集
            intersection = [triggers.get(task_id) for task_id, task in self.tasks.items() if task_id in trigger_ids]
            local_tasks_unique = [task_id for task_id, task in self.tasks.items() if task_id not in trigger_ids]
            cloud_tasks_unique = [task for task_id, task in triggers.items() if task_id not in self.tasks.keys()]
            logger.info(f"【to_native】intersection本地、云端相交部分是：{intersection} ")
            logger.info(f"【to_native】local_tasks_unique本地独有任务：{local_tasks_unique} ")
            logger.info(f"【to_native】cloud_tasks_unique云端独有任务：{cloud_tasks_unique} ")

            # 本地任务差值，直接删除
            for task_id in local_tasks_unique:
                logger.info("【to_native】本地删除任务: {}".format(task_id))
                self.delete_task(task_id)
            # 云端任务差值，直接添加
            for trigger in cloud_tasks_unique:
                logger.info("【to_native】云端添加任务: {}".format(trigger))
                self.add_task(**trigger)
            # 本地计划任务交集，进行更新处理
            for trigger in intersection:
                task = self.tasks[trigger["trigger_id"]]

                if task.kwargs == trigger:
                    logger.info("【to_native】云端、本地任务ID相同，参数相同，不进行更新。 ")
                    continue
                else:
                    logger.info(f"【to_native】云端、本地任务ID相同，参数不同，进行更新：{trigger} ")
                    self.update_task(**trigger)
            return True
        except Exception as e:
            import traceback

            logger.error("触发器同步失败: {} {}".format(e, traceback.extract_stack()))
            return False

    def add_task(
        self,
        trigger_id: str,
        trigger_name: str,
        task_type: str,
        queue_enable: bool,
        callback_project_ids: list,
        exceptional: str,
        timeout: int,
        **kwargs,
    ):
        """
        添加任务

        Args:
            trigger_id: 任务id
            trigger_name: 触发器名称
            task_type: 任务类型，仅支持`scheduled`、`mail`、`hotkey`、`files`
            queue_enable: bool, 是否启用队列
            callback_project_ids: 回调使用的工程id序列
            exceptional: str, 异常处理方式， 支持`skip`或者`stop`
            timeout: int, 工程超时时间， 默认9999
            kwargs: 构建task的相关参数
        """
        # 定时任务和邮件任务都使用这个类创建任务
        task = self.get_task(trigger_id)
        if task:
            return False

        # 触发类型判断原理是：
        # 1. schedule和mail可以使用定时轮询的方式调度
        # 2. file和hotKey只需要启动一次
        # 3. manual手动触发

        if task_type == "schedule" or task_type == "mail":
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
                **kwargs,
            )
            task.create()

        elif task_type == "file" or task_type == "hotKey":
            task = AsyncOneCallTask(
                trigger_id=trigger_id,
                trigger_name=trigger_name,
                task_type=task_type,
                queue_enable=queue_enable,
                q=self.queue,
                callback_project_ids=callback_project_ids,
                exceptional=exceptional,
                timeout=timeout,
                **kwargs,
            )
            task.create()

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
                **kwargs,
            )

        else:
            raise Exception("不支持的任务类型")

        self.tasks[trigger_id] = task
        return True

    def update_task(
        self,
        trigger_id: str,
        task_type: str,
        queue_enable: bool,
        callback_project_ids: list,
        **kwargs,
    ):
        """
        更新任务

        Args:
            trigger_id: 任务id
            task_type: 任务类型，仅支持`scheduled`、`mail`、`hotkey`、`files`
            queue_enable: bool, 是否启用队列
            callback_project_ids: 回调使用的工程id
            kwargs: 更新task的相关参数
        """
        task = self.get_task(trigger_id)
        if not task:
            return False

        # 移除任务调度
        self.delete_task(trigger_id)

        self.add_task(
            trigger_id=trigger_id,
            task_type=task_type,
            queue_enable=queue_enable,
            callback_project_ids=callback_project_ids,
            **kwargs,
        )

        return True

    def delete_task(self, trigger_id: str) -> bool:
        """
        删除对应任务

        :param trigger_id: `str`, 任务id
        :return:
        """
        logger.info(f"【delete_task】开始删除任务: {trigger_id}")

        task = self.get_task(trigger_id)
        if not task:
            logger.warning(f"【delete_task】任务不存在，删除失败: {trigger_id}")
            return False

        try:
            # 记录任务信息
            task_type = getattr(task, "task_type", "unknown")
            task_name = getattr(task, "trigger_name", "unknown")
            logger.info(f"【delete_task】找到任务: ID={trigger_id}, 类型={task_type}, 名称={task_name}")

            # 执行任务删除
            if hasattr(task, "delete"):
                logger.info(f"【delete_task】执行任务删除方法: {trigger_id}")
                task.delete()
            else:
                logger.warning(f"【delete_task】任务没有delete方法: {trigger_id}")

            # 从任务字典中移除
            del self.tasks[trigger_id]
            logger.info(f"【delete_task】任务删除成功: {trigger_id}")
            return True

        except Exception as e:
            logger.error(f"【delete_task】删除任务时发生异常: {trigger_id}, 错误: {str(e)}")
            import traceback

            logger.error(f"【delete_task】详细错误信息: {traceback.format_exc()}")
            return False

    def get_task(self, trigger_id: str) -> Union[AsyncSchedulerTask, AsyncOneCallTask]:
        """
        获取对应任务

        :param trigger_id: `str`, 任务id
        :return:
        """
        return self.tasks.get(trigger_id)

    def resume_task(self, trigger_id: str) -> bool:
        """
        开启任务

        :param trigger_id: `str`, 任务id
        :return:
        """
        task = self.get_task(trigger_id)
        if not task:
            return False

        task.resume()
        task.enable = True
        return True

    def pause_task(self, trigger_id: str) -> bool:
        """
        停止任务

        :param trigger_id: `str`, 任务id
        :return:
        """
        task = self.get_task(trigger_id)
        if not task:
            return False

        task.pause()
        task.enable = False
        return True

    def to_dict(self) -> list:
        """
        序列化任务

        :return:
            `List`, 序列化后的列表
        """

        return [task.__dict__() for task in self.tasks.values()]

    def delete_all_tasks(self):
        """
        删除所有任务
        """
        logger.info("【delete_all_tasks】: {}".format(self.tasks.keys()))
        task_keys = list(self.tasks.keys())
        for task_key in task_keys:
            logger.info("【delete_all_tasks】删除任务: {}".format(task_key))
            try:
                self.delete_task(task_key)
            except Exception as e:
                logger.error("【delete_all_tasks】删除任务失败: {}".format(e))
