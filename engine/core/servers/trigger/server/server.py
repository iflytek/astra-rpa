import asyncio
import copy
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rpawebsocketclient.ws import BaseMsg
from rpawebsocketclient.ws_client import WsApp

from .. import (
    ConfigInput,
    MailDetectInput,
    NotifyReq,
    QueueConfigInput,
    RemoveQueueTaskInput,
    TaskFutureExecInput,
    TaskFutureExecWithoutIdInput,
    TaskIdInput,
)
from ..core.app_context import app_context
from ..core.config import config
from ..core.logger import logger
from ..server.gateway_client import (
    execute_single_project,
    get_executor_status,
)
from ..tasks.base_task import AsyncImmediateTask, AsyncSchedulerTask
from ..tasks.mail_task import MailTask
from ..tasks.scheduled_task import ScheduledTask


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.ws_app = None
        self._thread = None
        self._stop_event = threading.Event()

    @staticmethod
    def default_log(msg, *args, **kwargs):
        """默认日志记录函数"""
        logger.info("ws: {} {} {}".format(msg, args, kwargs))

    @staticmethod
    def remote_run(msg: BaseMsg):
        """处理远程运行消息"""
        logger.info(msg)
        data = msg.data
        for i in range(3):
            if not get_executor_status():
                return execute_single_project(data)
            else:
                time.sleep(5)
        return None

    def start(self):
        """启动 WebSocket 连接"""
        try:
            self.ws_app = WsApp(
                url=f"ws://127.0.0.1:{config.GATEWAY_PORT}/api/rpa-openapi/ws",
                log=self.default_log,
                reconnect_max_time=-1,
            )
            self.ws_app.event("remote", "run", self.remote_run)

            self._thread = threading.Thread(target=self._ws_worker, daemon=True)
            self._thread.start()

            logger.info("WebSocket 管理器启动成功")
        except Exception as e:
            logger.error(f"WebSocket 管理器启动失败: {e}")

    def _ws_worker(self):
        """WebSocket 工作线程"""
        try:
            self.ws_app.start()
        except Exception as e:
            logger.error(f"WebSocket 工作线程异常: {e}")

    def stop(self):
        """停止 WebSocket 连接"""
        self._stop_event.set()
        if self.ws_app:
            self.ws_app.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("WebSocket 管理器已停止")

    def close_connection(self):
        """关闭当前连接"""
        if self.ws_app:
            self.ws_app.close()


# 创建 WebSocket 管理器实例
ws_manager = WebSocketManager()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/task/health")
async def health():
    return "ok"


@app.on_event("startup")
async def init_trigger():
    await app_context.initialize()

    # 启动 WebSocket 管理器
    ws_manager.start()

    async def periodic_to_native():
        """每300秒调用一次trigger.to_native()"""
        while True:
            logger.info("执行定期同步任务")
            if not app_context.trigger:
                await asyncio.sleep(1)
                continue
            await asyncio.sleep(10)  # 初次10s后同步，兜底前端没发送
            app_context.trigger.to_native()
            await asyncio.sleep(5 * 60)  # 每5分钟同步一次服务端数据，主要是为了兜底

    sync_task = asyncio.create_task(periodic_to_native())


@app.post("/task/run")
async def run_tasks(task_info: TaskIdInput):
    """
    手动触发任务

    :return:
    """
    logger.info("【/task/run】 开始调用")

    # 判断任务是否存在
    _t_info = task_info.model_dump()
    task_id = _t_info["task_id"]
    task = app_context.trigger.tasks.get(task_id)

    # 判断任务是否存在
    if not task:
        return {
            "code": 201,
            "message": "指定任务不存在，请等待一段时间后重试",
            "data": {},
        }
    if not isinstance(task, AsyncImmediateTask):
        return {"code": 201, "message": "指定任务不存在该调度方式", "data": {}}

    flag = await task.callback()
    if flag:
        return {"code": 200, "message": "任务调度成功", "data": {}}
    else:
        return {
            "code": 201,
            "message": "任务调度失败，请检查是否已存在实例正在运行",
            "data": {},
        }


@app.post("/task/notify")
async def notify(req: NotifyReq):
    """
    通知更新任务

    :return:
    """
    logger.info("notify: {}".format(req))

    if req.event == "login":
        tag = app_context.trigger.to_native()
    elif req.event == "exit":
        ws_manager.close_connection()
        tag = app_context.trigger.to_native(clear=True)
    elif req.event == "switch":
        ws_manager.close_connection()
        app_context.trigger.to_native(clear=True)
        tag = app_context.trigger.to_native()
    else:
        tag = app_context.trigger.to_native()
    if tag:
        return {"code": 200, "message": "任务更新成功", "data": {}}
    else:
        return {"code": 201, "message": "任务更新失败"}


@app.post("/mail/detect")
def mail_detect(task_info: MailDetectInput):
    """
    邮箱检测

    :param task_info:
    :return:
    """
    logger.info("【/mail/detect】 开始调用")
    _t_info = task_info.model_dump()
    amail = MailTask(task_id="book", **_t_info)

    flag = amail.connect()
    if flag:
        return {"code": 200, "message": "邮箱连接成功", "data": {}}
    else:
        return {"code": 201, "message": "邮箱连接失败", "data": {}}


@app.post("/task/future")
def future(task_info: TaskFutureExecInput):
    """
    获取任务未来N次执行的时间
    :param task_info:
    :return:
    """
    try:
        _t_info = task_info.model_dump()
        task_id = _t_info["task_id"]
        times = _t_info["times"]

        # 判断任务是否存在
        task = app_context.trigger.tasks.get(task_id)
        if not task:
            return {"code": 201, "message": "指定任务不存在", "data": {}}
        if not isinstance(task, AsyncSchedulerTask):
            return {
                "code": 201,
                "message": "指定任务不存在获取未来执行时间的方式",
                "data": {},
            }

        l = task.get_future_time(times=times)

        return {"code": 200, "message": "获取成功", "data": {"next_exec_times": l}}

    except Exception as e:
        return {"code": 201, "message": "获取失败", "data": {"next_exec_times": []}}


@app.post("/task/future_with_no_create")
def future_with_create(task_info: TaskFutureExecWithoutIdInput):
    """
    获取任务未来N次执行的时间（在没有创建任务的情况下）
    :param task_info:
    :return:
    """

    try:
        _t_info = task_info.model_dump()
        times = _t_info["times"]

        task = ScheduledTask(**_t_info)
        l = AsyncSchedulerTask.get_future_time_without_create(task.to_trigger(), times)
        return {"code": 200, "message": "获取成功", "data": {"next_exec_times": l}}
    except Exception:
        return {"code": 201, "message": "获取失败", "data": {"next_exec_times": []}}


@app.get("/task/queue/status")
async def get_queue_status(pageNo: int = 1, pageSize: int = 10, name: str = None, taskType: str = None):
    """
    获取当前任务队列状态

    :param pageNo: 页码，从1开始
    :param pageSize: 每页大小
    :param name: 任务名称，用于搜索过滤
    :param taskType: 任务类型，用于搜索过滤
    :return: 分页后的任务队列状态
    """
    try:
        filtered_tasks = []
        total = 0
        start_idx = (pageNo - 1) * pageSize
        end_idx = start_idx + pageSize

        # 一次遍历完成过滤和分页
        for task in app_context.task_queue_monitor:
            # 检查是否超时
            if app_context.task_queue_mgr.is_task_timeout(task):
                app_context.task_queue_monitor.remove(task)
                logger.info(
                    f"任务等待时间超过{app_context.queue_config['max_wait_minutes']}分钟，已移除: {task.get('trigger_id')}"
                )
                continue

            # 应用搜索过滤
            if name and name.lower() not in str(task.get("trigger_name", "")).lower():
                continue
            if taskType and taskType.lower() != str(task.get("task_type", "")).lower():
                continue

            # 计数
            total += 1

            # 只收集当前页的数据
            if start_idx <= total - 1 < end_idx:
                # 使用深拷贝避免修改原始任务对象
                task_copy = copy.deepcopy(task)
                task_copy["status_index"] = total
                filtered_tasks.append(task_copy)

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "max_size": app_context.queue_config["max_length"],
                "monitor_queue_size": total,
                "current_tasks": filtered_tasks,
                "pagination": {
                    "pageNo": pageNo,
                    "pageSize": pageSize,
                    "total": total,
                    "totalPages": (total + pageSize - 1) // pageSize,
                },
            },
        }
    except Exception as e:
        logger.error(f"获取队列状态失败: {e}")
        return {"code": 500, "message": f"获取队列状态失败: {str(e)}", "data": None}


@app.post("/task/queue/remove")
async def remove_queue_task(task_info: RemoveQueueTaskInput):
    """
    从队列中删除指定任务

    :param task_info: 包含unique_id列表的请求体
    :return:
    """
    try:
        removed_count = 0
        # 遍历要删除的unique_id列表
        for unique_id in task_info.unique_id:
            # 在队列中查找对应的任务
            for task in list(app_context.task_queue_monitor):
                if task.get("unique_id") == unique_id:
                    app_context.task_queue_monitor.remove(task)
                    removed_count += 1
                    logger.info(f"从队列中删除任务: {unique_id}")
                    break

        if removed_count > 0:
            return {
                "code": 200,
                "message": f"成功删除{removed_count}个任务",
                "data": {"removed_count": removed_count},
            }
        else:
            return {
                "code": 404,
                "message": "未找到指定的任务",
                "data": {"removed_count": 0},
            }
    except Exception as e:
        logger.error(f"删除队列任务失败: {e}")
        return {"code": 500, "message": f"删除失败: {str(e)}", "data": None}


@app.post("/task/queue/config")
async def update_queue_config(config: QueueConfigInput):
    """
    更新队列配置

    :param config: 队列配置信息
    :return:
    """
    try:
        # 如果最大等待时间发生变化，更新所有任务的过期时间
        if config.max_wait_minutes != app_context.queue_config["max_wait_minutes"]:
            for task in app_context.task_queue_monitor:
                enqueue_time = task.get("enqueue_time", "")
                if enqueue_time:
                    # 重新计算过期时间
                    expire_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(
                            time.mktime(time.strptime(enqueue_time, "%Y-%m-%d %H:%M:%S")) + config.max_wait_minutes * 60
                        ),
                    )
                    task["expire_time"] = expire_time

        # 如果队列最大长度变小了，删除超出限制的任务
        if config.max_length < app_context.queue_config["max_length"]:
            current_size = len(app_context.task_queue_monitor)
            if current_size > config.max_length:
                # 删除超出限制的任务（从队列末尾删除，保留最早的任务）
                tasks_to_remove = current_size - config.max_length
                for _ in range(tasks_to_remove):
                    if app_context.task_queue_monitor:
                        removed_task = app_context.task_queue_monitor.pop()
                        logger.info(f"队列长度超限，删除任务: {removed_task.get('unique_id')}")

        if config.deduplicate and not app_context.queue_config["deduplicate"]:
            # 开启去重，需要重新检查所有任务是否重复
            trigger_ids = set()
            for task in app_context.task_queue_monitor:
                if task.get("trigger_id") in trigger_ids:
                    app_context.task_queue_monitor.remove(task)
                    logger.info(f"任务已存在，跳过: {task.get('unique_id')}")
                    continue
                trigger_ids.add(task.get("trigger_id"))

        app_context.queue_config.update(config.model_dump())
        logger.info(f"更新队列配置: {app_context.queue_config}")
        return {
            "code": 200,
            "message": "配置更新成功",
            "data": app_context.queue_config,
        }
    except Exception as e:
        logger.error(f"更新队列配置失败: {e}")
        return {"code": 500, "message": f"配置更新失败: {str(e)}", "data": None}


@app.get("/task/queue/config")
async def get_queue_config():
    """
    获取当前队列配置
    """
    return {"code": 200, "message": "获取成功", "data": app_context.queue_config}


@app.post("/config/update")
async def update_config(input_config: ConfigInput):
    """
    更新配置
    """
    logger.info(input_config.terminal_mode)
    app_context.update_config(input_config.terminal_mode)
    return {"code": 200, "message": "配置更新成功", "data": config}
