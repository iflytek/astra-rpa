import datetime
import json
import os
import sys
import threading
import time
import traceback
import uuid
from enum import Enum
from typing import Union

import requests
import websocket

from ...core.environment.venv import create_project_venv
from ...core.executor.virtual_desk import (
    WindowVirtualDeskSubprocessAdapter,
    virtual_desk,
)
from ...core.terminal.terminal import Terminal
from ...logger import logger
from ...utils.notify_utils import NotifyUtils
from ...utils.platform_utils import platform_python_venv_path
from ...utils.subprocess import SubPopen
from ...utils.utils import (
    EmitType,
    check_port,
    emit_to_front,
    read_last_n_lines,
)


class ExecuteStatus(Enum):
    """
    机器人执行状态
    """

    # 执行中
    EXECUTE = "robotExecute"
    # 成功
    SUCCESS = "robotSuccess"
    # 执行失败
    FAIL = "robotFail"
    # 取消
    CANCEL = "robotCancel"


class TaskExecuteStatus(Enum):
    # 成功
    SUCCESS = "success"
    # 启动失败
    START_ERROR = "start_error"  # 无效
    # 执行失败
    EXEC_ERROR = "exe_error"
    # 取消
    CANCEL = "cancel"
    # 执行中
    EXECUTING = "executing"


class ProjectExecPosition(Enum):
    """
    指定工程在哪个阶段运行
    """

    # 工程列表页
    PROJECT_LIST = "PROJECT_LIST"
    # 工程编辑页
    EDIT_PAGE = "EDIT_PAGE"
    # 计划任务启动
    CRONTAB = "CRONTAB"
    # 执行器运行列表页
    EXECUTOR = "EXECUTOR"
    # 调度模式
    DISPATCH = "DISPATCH"


def read_status(file) -> (ExecuteStatus, str):
    """
    从日志文件中读取执行结果
    """
    try:
        if os.path.exists(file):
            log_lines = read_last_n_lines(file, 5)
            for line in reversed(log_lines):
                line = line.strip()
                if line == "":
                    continue
                try:
                    result_json = json.loads(line)
                except Exception as e:
                    continue

                # 处理数据
                result_json_data = result_json.get("data", {})
                if result_json_data.get("result", None) is None:
                    continue
                execute_status = ExecuteStatus(result_json_data.get("result"))

                execute_reason = result_json.get("data", {}).get("msg_str", "")
                execute_data = result_json.get("data", {}).get("data", "")
                if execute_status.SUCCESS:
                    execute_reason = ""

                # 直接结束
                return execute_status, execute_reason, execute_data
    except Exception as e:
        logger.exception("read_exec_status error: {}".format(e))
    return ExecuteStatus.FAIL, "运行日志为空", {}


class Executor:
    """执行器进程 句柄"""

    def __init__(
        self,
        project_id: str = "",  # 工程id
        project_name: str = "",  # 工程名称
        exec_id: str = "",  # 执行id
        exec_port: int = 0,  # 执行端口
        ins: Union[SubPopen, WindowVirtualDeskSubprocessAdapter] = None,  # 执行器实例
        recording_path: str = "",  # 录制日志路径
        exec_position: ProjectExecPosition = ProjectExecPosition.EDIT_PAGE,  # 执行位置
        task_id: str = "",  # 计划任务id
        task_exec_id: str = "",  # 计划任务执行id
        open_virtual_desk: bool = False,
        version: str = "",  # 版本号
        run_param: str = "",  # 执行参数
    ):
        # 配置数据
        self.project_id = project_id
        self.project_name = project_name
        self.exec_id = exec_id
        self.exec_port = exec_port
        self.__ins__ = ins
        self.recording_path = recording_path
        self.exec_position = exec_position
        self.task_id = task_id
        self.task_exec_id = task_exec_id
        self.open_virtual_desk = open_virtual_desk
        self.version = version
        self.run_param = run_param
        # 是否需要发送日志事件
        self.is_send_log_event = True

        # -流程状态
        self.open_async = False  # 是否开启回收逻辑
        self.kill_time = 0  # 强杀时间 0 不强杀 >0 强杀 <0 已经强杀
        self.report_log_time = 0  # 上报 0 没上报 > 0 上报中 <0 上报结束

        # -运行结果
        self.execute_status = ExecuteStatus.EXECUTE  # 执行状态
        self.execute_reason = None  # 执行原因
        self.execute_data = None  # 执行返回数据

    @property
    def ins(self):
        return self.__ins__

    @ins.setter
    def ins(self, value):
        self.__ins__ = value

    def run(self):
        """启动进程"""
        if self.open_virtual_desk and sys.platform != "win32":
            self.__ins__.run(env=virtual_desk.env)
        else:
            self.__ins__.run()

    def wait_start(self, time_out=5, interval=0.1) -> bool:
        """等待进程真正启动"""
        if isinstance(self.__ins__, SubPopen):
            if not self.__ins__:
                return False

            for i in range(int(time_out / interval)):
                if not check_port(port=self.exec_port):
                    return True
                time.sleep(interval)
            return False
        elif isinstance(self.__ins__, WindowVirtualDeskSubprocessAdapter):
            return True
        else:
            raise NotImplementedError()

    def kill(self):
        """强行关闭进程"""
        if self.__ins__:
            if self.__ins__.is_alive():
                self.__ins__.kill()
        self.kill_time = -1  # [强制关闭结束]

    def close(self):
        """关闭进程"""
        # 进程已经结束
        if not self.__ins__.is_alive():
            return

        # 如果进程没有关闭,先温和关闭，再强制关闭
        self.kill_time = time.time() + 3  # [强制关闭]
        # 温和关闭
        if not check_port(port=self.exec_port):
            ws = websocket.create_connection(f"ws://127.0.0.1:{self.exec_port}/?tag=scheduler")
            closed_event = {
                "event_id": self.exec_id,
                "event_time": int(time.time()),
                "channel": "flow",
                "key": "close",
                "data": {},
            }
            ws.send(json.dumps(closed_event))
            time.sleep(0.1)
            ws.close()


class ExecutorManager:
    """执行器管理"""

    def __init__(self, svc):
        # 执行实列
        self.svc = svc
        self.thread_lock = threading.Lock()
        self.report_log_lock = threading.Lock()
        # 正在执行队列
        self.executor_list = {}

        # 一些统计数据
        self.curr_task_name = ""
        self.curr_project_name = ""
        self.curr_log_name = ""
        self.curr_task_id = ""

        # 异步任务处理
        threading.Thread(target=self.async_call, daemon=True).start()

    def create(
        self,
        project_id: str = "",  # 工程id
        project_name: str = "",  # 工程名称
        process_id: str = "",  # 流程id
        line: int = 1,  # 测试行号
        end_line: int = 0,  # 测试行号
        debug: str = None,  # debug模式
        exec_position: ProjectExecPosition = ProjectExecPosition.EDIT_PAGE,  # 执行位置
        recording_config: dict = None,  # 录制器配置
        hide_log_window: bool = False,  # 是否隐藏日志框
        task_id: str = "",  # 计划任务id
        task_name: str = "",  # 计划任务名称
        task_exec_id: str = "",  # 计划任务执行id
        run_param: str = "",  # 执行参数
        open_virtual_desk: bool = False,  # 虚拟桌面
        version: str = "",  # 版本号
        is_send_log_event: bool = True,  # 是否需要发送日志事件
    ):
        """启动一个实例"""
        executor = Executor()
        executor.project_id = project_id
        executor.project_name = project_name
        executor.exec_position = exec_position
        executor.task_id = task_id
        executor.task_exec_id = task_exec_id
        executor.open_virtual_desk = open_virtual_desk
        executor.version = version
        executor.run_param = run_param
        executor.is_send_log_event = is_send_log_event

        # 1. 日志上报
        if exec_position in [
            ProjectExecPosition.DISPATCH,
            ProjectExecPosition.CRONTAB,
            ProjectExecPosition.EXECUTOR,
        ]:
            executor.exec_id = self.get_execute_id(
                project_id,
                exec_position,
                Terminal.get_terminal_id(),
                task_exec_id,
                executor.version,
                executor.run_param,
            )
            if not executor.exec_id:
                raise Exception(r"服务端接口异常，工程运行失败")
        if not executor.exec_id:
            executor.exec_id = str(uuid.uuid1())

        # 2. 检查是否占用
        if self.status():
            raise Exception("已有实例运行，启动失败...")

        # 2.1 统计数据
        self.curr_task_name = task_name
        self.curr_task_id = task_id
        self.curr_project_name = project_name
        self.curr_log_name = os.path.join(r"logs", "report", executor.project_id, "{}.txt".format(executor.exec_id))

        # 3. 获取端口
        executor.exec_port = self.svc.get_validate_port(None)

        # 4. 创建虚拟环境
        create_project_venv(self.svc, project_id)

        # 5. 配置tasK
        exec_python = platform_python_venv_path(os.path.join(self.svc.config.app_server.venv_base_dir, project_id))

        if open_virtual_desk and sys.platform == "win32":
            ins = WindowVirtualDeskSubprocessAdapter(self.svc, exec_python=exec_python)
        else:
            ins = SubPopen(name="executor", cmd=[exec_python, "-m", "rpa_executor"])

        ins.set_param("port", executor.exec_port)
        ins.set_param("gateway_port", self.svc.route_port)
        ins.set_param("project_id", executor.project_id)
        ins.set_param("mode", exec_position.value)
        ins.set_param("exec_id", executor.exec_id)
        if run_param:
            ins.set_param("run_param", run_param)
        if process_id:
            ins.set_param("process_id", process_id)
        if line:
            ins.set_param("line", line)
        if end_line:
            ins.set_param("end_line", end_line)
        if debug:
            ins.set_param("debug", debug)
        if project_name:
            ins.set_param("project_name", project_name)
        if version:
            ins.set_param("version", version)

        wait_web_ws = "y"
        wait_tip_ws = "y"
        if hide_log_window:
            wait_tip_ws = "n"
        if exec_position in [
            ProjectExecPosition.PROJECT_LIST,
            ProjectExecPosition.DISPATCH,
            ProjectExecPosition.CRONTAB,
            ProjectExecPosition.EXECUTOR,
        ]:
            wait_web_ws = "n"
        ins.set_param("wait_web_ws", wait_web_ws)
        ins.set_param("wait_tip_ws", wait_tip_ws)

        executor.recording_path = ""
        if recording_config and exec_position in [
            ProjectExecPosition.CRONTAB,
            ProjectExecPosition.DISPATCH,
            ProjectExecPosition.EXECUTOR,
        ]:
            try:
                if recording_config.get("enable", False):
                    ins.set_param(
                        "recording_config",
                        json.dumps(recording_config, ensure_ascii=True),
                    )
                    executor.recording_path = recording_config.get("filePath", "./logs/report")
            except Exception as e:
                pass

        executor.ins = ins

        # 6. 启动运行
        if open_virtual_desk:
            # 开启了虚拟桌面
            virtual_desk.start(self.svc)

        try:
            executor.run()
        except Exception as e:
            logger.error("ExecutorManager error: {}".format(e))
            return None
        with self.thread_lock:
            self.executor_list[executor.exec_id] = executor

        # 7. 检查是否真启动完成
        if executor.wait_start(time_out=5):
            return executor
        else:
            executor.execute_status = ExecuteStatus.FAIL
            executor.execute_reason = "启动失败"
            executor.execute_data = {}
            self.close(executor)
            return None

    def async_call(self):
        """异步任务：回收，强杀，上报等异步任务"""
        while True:
            time.sleep(0.1)
            try:
                if len(self.executor_list) == 0:
                    time.sleep(3)  # 执行器至少执行3s，延迟越长给其他任务更多时间
                    continue

                # 每.1秒检查一次是否进程死亡，需要回收
                for key in list(self.executor_list.keys()):
                    executor = self.executor_list[key]

                    # 任务1：检测他的进程是否关闭(可能是主动也可能是异常关闭或用户手动关闭)，并标记需要回收，不重复标记
                    try:
                        if not executor.open_async and not executor.ins.is_alive():
                            # 启动回收逻辑
                            logger.info("step1: {}".format(executor.exec_id))
                            executor.open_async = True
                            continue
                    except Exception as e:
                        logger.errr("step1 error: {}".format(e))
                        continue

                    # 任务2: 强杀逻辑, 如果标记回收，且标记了强杀时间[大于0]，到了强杀时间就回收[强杀结束后kill_time会设置成-1]
                    try:
                        if executor.open_async and 0 < executor.kill_time <= time.time():
                            logger.info("step2: {} {}".format(executor.exec_id, executor.kill_time))
                            executor.kill()
                    except Exception as e:
                        logger.errr("step2 error: {}".format(e))
                        continue

                    # 任务3: 日志上报，如果标记回收，没有标记强杀时间，或已经被强杀了
                    # 所有尘埃落地后，去上报并标记上报状态
                    # 上报 0 没上报 > 0 上报中 <0 上报结束
                    try:
                        if executor.open_async and executor.kill_time <= 0 and executor.report_log_time == 0:
                            logger.info("step3: {}".format(executor.exec_id))
                            self.report_app_log(executor)
                    except Exception as e:
                        logger.errr("step3 error: {} ".format(e))
                        continue

                    # 任务4: 全部完成，上报也结束后，删除执行器
                    try:
                        if executor.open_async and executor.kill_time <= 0 and executor.report_log_time < 0:
                            logger.info("step4: {}".format(executor.exec_id))
                            try:
                                if executor.open_virtual_desk:
                                    virtual_desk.stop()
                            except Exception as e:
                                pass
                            del self.executor_list[executor.exec_id]
                    except Exception as e:
                        logger.info("step4 error: {}".format(e))
                        continue
            except Exception as e:
                logger.error("async_call error: {} {}".format(e, traceback.format_exc()))
                pass

    def close(self, executor: Executor):
        """用户主动结束, 不包括进程自己关闭"""
        if executor.exec_id not in self.executor_list:
            return
        try:
            executor.close()  # 用户主动结束
            executor.open_async = True  # 再设置他关闭状态
        except Exception as e:
            logger.exception("close error: {}".format(e))

    def close_by_project(self, project_id: int):
        """用户主动结束, 不包括进程自己关闭"""
        if len(self.executor_list) > 0:
            for _, v in self.executor_list.items():
                if v.project_id == project_id:
                    self.close(v)
                    return True
        return False

    def close_all(self):
        """用户主动结束, 不包括进程自己关闭"""
        for _, v in self.executor_list.items():
            self.close(v)
        return True

    def status(self) -> bool:
        """判断是否存在正在运行的实例，有返回True"""

        with self.thread_lock:
            if len(self.executor_list) == 0:
                return False
        return True

    def task_trigger_status(self):
        """通知触发"""

        emit_to_front(EmitType.TERMINAL_STATUS, msg={"type": "busy" if self.status() else "idle"})

    def get_execute_id(
        self,
        project_id: str,
        exec_position: ProjectExecPosition,
        terminalId="",
        task_exec_id="",
        version="",
        paramJson="",
    ):
        """服务端获取工程运行ID，用于日志上报"""
        api = "/api/robot/robot-record/save-result"
        try:
            data = {
                "robotId": project_id,
                "taskExecuteId": task_exec_id,
                "terminalId": terminalId,
                "result": ExecuteStatus.EXECUTE.value,
                "isDispatch": self.svc.terminal_mod,
                "paramJson": paramJson,
            }
            if exec_position.value:
                data["mode"] = exec_position.value
            if version:
                data["robotVersion"] = int(version)
            if self.svc.terminal_mod:
                data["dispatchTaskExecuteId"] = task_exec_id
            response = requests.post(
                url="http://127.0.0.1:{}{}".format(self.svc.route_port, api),
                json=data,
                timeout=10,
            )
            status_code = response.status_code
            text = response.text
            if status_code != 200:
                raise Exception("get error status_code: {}".format(status_code))
            logger.info("report data: {}, response: {} {}".format(data, status_code, text))
            return json.loads(text.strip())["data"]
        except Exception as e:
            logger.exception("[APP] request api: {} error: {}".format(api, e))

    def report_app_log(self, executor: Executor):
        """日志上报"""
        if executor.report_log_time != 0:
            return
        executor.report_log_time = time.time()

        try:
            # 1. 提示前端关闭
            if executor.is_send_log_event:
                emit_to_front(EmitType.EXECUTOR_END)

            # 2. 日志收集

            log_file = os.path.join(
                r"logs",
                "report",
                executor.project_id,
                "{}.txt".format(executor.exec_id),
            )
            log_content = ""
            execute_status = executor.execute_status
            execute_reason = executor.execute_reason
            execute_data = executor.execute_data
            if os.path.exists(log_file):
                # 2.1 日志文件存在

                # 2.2 发送给前端显示
                if executor.is_send_log_event:
                    emit_to_front(
                        EmitType.LOG_REPORT,
                        msg={
                            "exec_id": executor.exec_id,
                            "exec_position": executor.exec_position.name,
                            "log_path": log_file,
                        },
                    )

                # 2.3 读取日志
                log_path_size = os.path.getsize(log_file)
                if log_path_size < 10 * 1024 * 1024:
                    # 小于10M的才读取
                    with open(log_file, encoding="utf-8") as f:
                        log_content = f.readlines()
                    log_content = [json.loads(item.strip()) for item in log_content]
                    log_content = json.dumps(log_content)
                else:
                    logger.warning(f"{log_file} size is {log_path_size / (10 * 1024 * 1024)}, will ignore report.")

                # 2.4 状态收集
                execute_status, execute_reason, execute_data = read_status(log_file)

            # 3. 视频路径收集
            video_path = os.path.join(
                executor.recording_path,
                executor.project_id,
                "{}.mp4".format(executor.exec_id),
            )
            if not os.path.exists(video_path):
                video_path = ""

            # 4. 状态汇总
            executor.execute_status = execute_status
            executor.execute_reason = execute_reason
            executor.execute_data = execute_data

            # 5. 日志上报
            if executor.exec_position in [
                ProjectExecPosition.CRONTAB,
                ProjectExecPosition.DISPATCH,
                ProjectExecPosition.EXECUTOR,
            ]:
                # 发送通知
                if executor.execute_status == ExecuteStatus.FAIL:
                    NotifyUtils(self.svc).send(
                        "{} ID: {}".format(executor.project_name, executor.project_id),
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )

                # 日志上报
                data = {
                    "robotId": executor.project_id,
                    "executeId": executor.exec_id or "",
                    "taskExecuteId": executor.task_exec_id,
                    "result": executor.execute_status.value,
                    "errorReason": executor.execute_reason,
                    "executeLog": log_content,
                    "terminalId": Terminal.get_terminal_id(),
                    "videoLocalPath": video_path,
                    "isDispatch": self.svc.terminal_mod,
                    "paramJson": executor.run_param,
                }
                if executor.exec_position.value:
                    data["mode"] = executor.exec_position.value
                if executor.version:
                    data["robotVersion"] = int(executor.version)
                if self.svc.terminal_mod:
                    data["dispatchTaskExecuteId"] = executor.task_exec_id
                response = requests.post(
                    url="http://127.0.0.1:{}/api/robot/robot-record/save-result".format(self.svc.route_port),
                    json=data,
                    timeout=10,
                )
                status_code = response.status_code
                text = response.text
                logger.info("report log data: {}, response: {} {}".format(data, status_code, text))
        except Exception as e:
            logger.exception("report_app_log error: {}".format(e))
        finally:
            executor.report_log_time = -1
