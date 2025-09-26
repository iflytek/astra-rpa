import json
import time
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...apis.connector.terminal import Terminal
from ...apis.response import ResCode, res_msg
from ...core.executor.executor import (
    ExecuteStatus,
    ProjectExecPosition,
    TaskExecuteStatus,
)
from ...core.svc import Svc, get_svc
from ...logger import logger
from ...utils.utils import EmitType, emit_to_front, get_settings

router = APIRouter()


class ExecutorProject(BaseModel):
    project_id: str  # 工程id
    project_name: str = ""  # 工程名称
    process_id: str = ""  # 流程id
    line: int = 0  # 测试行号
    end_line: int = 0  # 测试行号
    jwt: str = ""  # jwt[无效]
    debug: str = "n"  # debug模式
    exec_position: ProjectExecPosition = ProjectExecPosition.EDIT_PAGE  # 执行位置
    recording_config: str = ""  # 录制器配置
    hide_log_window: bool = False  # 是否隐藏日志框
    run_param: str = ""  # 执行器参数
    open_virtual_desk: bool = False  # 虚拟桌面


class StopTask(BaseModel):
    task_id: Optional[str] = None


class RobotInfo(BaseModel):
    robotId: str
    robotName: str
    paramJson: str = ""
    version: str = "1"
    sort: int = 1


class TaskInfo(BaseModel):
    trigger_id: str  # 任务id
    task_type: str = ""  # schedule manual hotKey files mail
    trigger_name: str  # 任务名称
    exceptional: str
    timeout: int = 0
    callback_project_ids: list[RobotInfo] = []
    mode: ProjectExecPosition = ProjectExecPosition.EDIT_PAGE
    retry_num: int = 0
    open_virtual_desk: bool = False  # 虚拟桌面


def report_task_log(svc, status: TaskExecuteStatus, task_id: str = None, task_execute_id: str = None):
    """日志上报：计划任务整体状态上报，区分与普通日志上报"""

    import requests

    if svc.terminal_mod:
        data = {
            "dispatchTaskId": task_id,
            "result": status.value,
            "isDispatch": True,
            "terminalId": Terminal.get_terminal_id(),
        }
        if task_execute_id:
            data["dispatchTaskExecuteId"] = task_execute_id
    else:
        data = {
            "taskId": task_id,
            "result": status.value,
            "isDispatch": False,
        }
        if task_execute_id:
            data["taskExecuteId"] = task_execute_id

    response = requests.post(
        headers={"Content-Type": "application/json"},
        url="http://127.0.0.1:{}/api/robot/task-execute/status".format(svc.route_port),
        data=json.dumps(data),
        timeout=3,
    )
    status_code = response.status_code
    text = response.text
    logger.info("report log request: {}".format(json.dumps(data)))
    logger.info("report log result: {}, response: {} {}".format(task_id, status_code, text))
    json_data = json.loads(text.strip())
    return json_data["data"]


@router.post("/run_list")
def executor_run_list(task_info: TaskInfo, svc: Svc = Depends(get_svc)):
    """
    运行和启动一组工程(计划任务), 同步
    """
    if svc.executor_mg.status():
        return res_msg(code=ResCode.ERR, msg="已有实例在运行，无法启动")
    svc.terminal_task_stop = False
    settings = get_settings()
    task_executor_id = ""
    try:
        emit_to_front(EmitType.EDIT_SHOW_HIDE, msg={"type": "hide"})

        task_executor_id = report_task_log(svc, TaskExecuteStatus.EXECUTING, task_info.trigger_id)
        if not task_executor_id:
            raise Exception("服务日志上报异常")

        end_time = 0
        if task_info.timeout > 0:
            end_time = time.time() + (task_info.timeout * 60)

        temp_terminal_mod = svc.terminal_mod

        # 循环每个机器人
        is_cancel = False
        for r in sorted(task_info.callback_project_ids, key=lambda x: x.sort):
            is_break = False
            for t in range(task_info.retry_num + 1):
                executor = svc.executor_mg.create(
                    task_id=task_info.trigger_id,
                    task_name=task_info.trigger_name,
                    task_exec_id=task_executor_id,
                    project_id=r.robotId,
                    project_name=r.robotName,
                    exec_position=task_info.mode,
                    recording_config=settings.get("videoForm", None),
                    hide_log_window=settings.get("commonSetting", {}).get("hideLogWindow", False),
                    run_param=r.paramJson,
                    open_virtual_desk=settings.get("open_virtual_desk", False) or task_info.open_virtual_desk,
                    version=r.version,
                    is_send_log_event=False,
                )
                if svc.terminal_mod:
                    svc.executor_mg.task_trigger_status()

                # 检查是否运行结束
                while svc.executor_mg.status():
                    time.sleep(1)
                    if 0 < end_time < time.time():
                        svc.executor_mg.close(executor)
                        raise Exception("启动失败: 运行超时")

                # 检查全局状态
                if temp_terminal_mod != svc.terminal_mod:
                    # 状态切换了，直接跳出剩余任务
                    is_cancel = True
                    is_break = True
                    break

                if svc.terminal_task_stop:
                    svc.terminal_task_stop = False
                    is_cancel = True
                    is_break = True
                    break

                # 检测状态
                if executor is not None:
                    execute_status = executor.execute_status
                    execute_reason = executor.execute_reason
                    execute_data = executor.execute_data
                else:
                    execute_status = ExecuteStatus.FAIL
                    execute_reason = "启动失败"
                    execute_data = {}

                if execute_status == ExecuteStatus.SUCCESS:
                    # 成功
                    break
                else:
                    # 失败
                    if task_info.exceptional == "jump":
                        # 跳过
                        break
                    elif task_info.exceptional == "retry_stop":
                        if t == task_info.retry_num - 1:
                            raise Exception("启动失败: {}".format(execute_reason))
                    else:
                        # stop
                        raise Exception("启动失败: {}".format(execute_reason))

            if is_break:
                break
        # 运行成功
        if task_info.task_type in ["manual", "hotKey"]:
            emit_to_front(EmitType.EXECUTOR_END)
        if task_executor_id:
            if is_cancel:
                report_task_log(
                    svc,
                    TaskExecuteStatus.CANCEL,
                    task_info.trigger_id,
                    task_executor_id,
                )
            else:
                report_task_log(
                    svc,
                    TaskExecuteStatus.SUCCESS,
                    task_info.trigger_id,
                    task_executor_id,
                )
        if svc.terminal_mod:
            svc.executor_mg.task_trigger_status()
        return res_msg(code=ResCode.SUCCESS, msg="运行成功", data={})
    except Exception as e:
        # 运行失败
        if task_info.task_type in ["manual", "hotKey"]:
            emit_to_front(EmitType.EXECUTOR_END)
        if task_executor_id:
            report_task_log(
                svc,
                TaskExecuteStatus.EXEC_ERROR,
                task_info.trigger_id,
                task_executor_id,
            )
        if svc.terminal_mod:
            svc.executor_mg.task_trigger_status()
        return res_msg(code=ResCode.SUCCESS, msg=str(e), data={})


@router.post("/run_sync")
def executor_run_sync(param: ExecutorProject, svc: Svc = Depends(get_svc)):
    """
    运行和启动一个工程(远程调度), 同步，并获取返回值
    """

    if svc.executor_mg.status():
        return res_msg(code=ResCode.ERR, msg="已有实例在运行，无法启动")

    recording_config = {}
    try:
        if param.recording_config:
            recording_config = json.loads(param.recording_config)
    except Exception as e:
        # 录制功能不影响执行器
        pass

    executor = svc.executor_mg.create(
        project_id=param.project_id,
        project_name=param.project_name,
        process_id=param.process_id,
        line=param.line,
        end_line=param.end_line,
        debug=param.debug,
        exec_position=param.exec_position,
        recording_config=recording_config,
        hide_log_window=param.hide_log_window,
        run_param=param.run_param,
        open_virtual_desk=param.open_virtual_desk,
        is_send_log_event=False,
    )
    # 检查是否运行结束
    while svc.executor_mg.status():
        time.sleep(1)
    # 检测状态
    if executor is not None:
        execute_status = executor.execute_status
        execute_reason = executor.execute_reason
        execute_data = executor.execute_data
    else:
        execute_status = ExecuteStatus.FAIL
        execute_reason = "启动失败"
        execute_data = {}
    if execute_status == ExecuteStatus.SUCCESS:
        return res_msg(code=ResCode.SUCCESS, msg="启动成功", data=execute_data)
    else:
        return res_msg(code=ResCode.ERR, msg=execute_reason)


@router.post("/run")
def executor_run(param: ExecutorProject, svc: Svc = Depends(get_svc)):
    """
    运行和启动一个工程(本地执行), 异步
    """
    # 初始化
    if not param.project_id:
        return res_msg(code=ResCode.ERR, msg="工程id为空", data=None)
    if svc.executor_mg.status():
        return res_msg(code=ResCode.ERR, msg="已有实例在运行，无法启动")

    recording_config = {}
    try:
        if param.recording_config:
            recording_config = json.loads(param.recording_config)
    except Exception as e:
        # 录制功能不影响执行器
        pass

    executor = svc.executor_mg.create(
        project_id=param.project_id,
        project_name=param.project_name,
        process_id=param.process_id,
        line=param.line,
        end_line=param.end_line,
        debug=param.debug,
        exec_position=param.exec_position,
        recording_config=recording_config,
        hide_log_window=param.hide_log_window,
        run_param=param.run_param,
        open_virtual_desk=param.open_virtual_desk,
        is_send_log_event=True,
    )
    if executor is not None:
        return res_msg(
            msg="启动成功",
            data={"addr": "ws://127.0.0.1:{}/".format(executor.exec_port)},
        )
    else:
        return res_msg(code=ResCode.ERR, msg="启动失败")


@router.post("/status")
def executor_status(svc: Svc = Depends(get_svc)):
    """
    获取执行器状态
    """
    status = svc.executor_mg.status()
    return res_msg(msg="ok", data={"running": status})


@router.post("/stop")
def executor_stop(exe_pro: ExecutorProject, svc: Svc = Depends(get_svc)):
    """
    强制关闭一个工程
    """
    project_id = exe_pro.project_id
    if not project_id:
        return res_msg(code=ResCode.ERR, msg="工程id为空", data=None)
    svc.executor_mg.close_by_project(project_id=project_id)
    return res_msg(msg="停止成功", data=None)


@router.post("/stop_list")
def executor_stop_list(stop_info: StopTask, svc: Svc = Depends(get_svc)):
    if svc.executor_mg:
        if (stop_info.task_id and svc.executor_mg.curr_task_id == stop_info.task_id) or (not stop_info.task_id):
            svc.terminal_task_stop = True
            svc.executor_mg.close_all()  # 关闭正在进行的任务
    return res_msg(msg="停止成功", data=None)
