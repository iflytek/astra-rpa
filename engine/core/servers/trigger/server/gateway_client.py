import json
from typing import Dict, List

import requests

from .. import CONVERT_COLUMN, TERMINAL_CONVERT_COLUMN
from ..core.config import config
from ..core.logger import logger


def execute_multiple_projects(project_info: Dict):
    url = "http://127.0.0.1:{}/scheduler/executor/run_list".format(config.GATEWAY_PORT)
    headers = {"Content-Type": "application/json"}
    logger.info(f"当前调度器请求的Json是：{project_info}")
    response = requests.post(url, headers=headers, data=json.dumps(project_info))

    logger.info(f"当前调度器返回的结果的Json是：{response.json()}")
    if int(response.status_code) == 200 and response.json()["code"] == "0000":
        return True
    else:
        return False


def execute_single_project(project_info: Dict):
    url = "http://127.0.0.1:{}/scheduler/executor/run_sync".format(config.GATEWAY_PORT)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(project_info))

    logger.info(f"当前调度器返回的结果的Json是：{response.json()}")
    if int(response.status_code) == 200 and response.json()["code"] == "0000":
        return response.json()
    else:
        return None


def get_executor_status():
    url = "http://127.0.0.1:{}/scheduler/executor/status".format(config.GATEWAY_PORT)
    response = requests.post(url)
    logger.info(f"当前调度器返回的结果的Json是：{response.json()}")
    if int(response.status_code) == 200 and response.json().get("data", {}).get("running", False):
        return True
    else:
        return False


def send_msg(data: dict):
    url = "http://127.0.0.1:{}/scheduler/send/tip".format(config.GATEWAY_PORT)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"当前调度器返回的结果的Json是：{response.json()}")
    if int(response.status_code) == 200 and response.json()["code"] == "0000":
        return response.json()
    else:
        return None


def send_stop_list(task_id: str = None):
    url = "http://127.0.0.1:{}/scheduler/executor/stop_list".format(config.GATEWAY_PORT)
    if task_id:
        data = {"task_id": task_id}
    else:
        data = {}
    logger.info(f"当前调度器请求的Json是：{data}")
    response = requests.post(url, json=data)
    logger.info(f"当前调度器返回的结果的Json是：{response.text}")
    if int(response.status_code) == 200 and response.json()["code"] == "0000":
        return response.json()
    else:
        return None


def list_trigger():
    def convert(recorder: List[Dict]) -> Dict:
        trigger_tasks = {}
        for task in recorder:
            _d = {}
            for k, v in CONVERT_COLUMN.items():
                # 规则转换（进行服务端的规范0和1转换）
                if k == "enable" or k == "queueEnable":
                    _d[v] = True if task.get(k) == 1 else False
                    continue
                # taskJson对Dict进行扩充
                elif k == "taskJson":
                    task[k] = task.get(k).replace("'", '"')
                    _d.update(json.loads(task.get(k)))
                    # taskJson本体也保留
                elif k == "robotInfoList":
                    callback_infos_list = []
                    for i in task.get(k):
                        callback_infos = {}
                        for key, value in i.items():
                            if value is not None:
                                callback_infos[key] = value
                        callback_infos_list.append(callback_infos)
                    _d[v] = callback_infos_list
                    continue

                _d[v] = task.get(k)
            _d["mode"] = "EXECUTOR"
            if _d.get("open_virtual_desk") is None:
                _d["open_virtual_desk"] = False
            if _d.get("screen_record_enable") is None:
                _d["screen_record_enable"] = False
            trigger_tasks[_d["trigger_id"]] = _d

        return trigger_tasks

    url = "http://127.0.0.1:{}/api/robot/triggerTask/page/list4Trigger".format(config.GATEWAY_PORT)
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"pageSize": 100, "pageNo": 1, "name": "", "taskType": ""})
    response = requests.request("POST", url, headers=headers, data=payload, timeout=5)
    if response.json()["code"] == "000000":
        return convert(response.json()["data"]["records"])
    else:
        raise Exception("获取任务列表失败")


def terminal_poll_update():
    """
    从节点轮询更新接口

    Args:
        terminal_id: 终端ID

    Returns:
        True或False
    """
    url = "http://127.0.0.1:{}/api/robot/dispatch-task/poll-task-update".format(config.GATEWAY_PORT)
    params = {"terminalId": config.TERMINAL_ID}
    response = requests.request("GET", url, params=params, timeout=5)
    if int(response.status_code) == 200:
        return response.json()["data"]
    else:
        return False


def terminal_list_task():
    """
    从节点获取任务列表接口
    """

    def convert(recorder: Dict):
        dispatch_tasks = {}
        retry_tasks = {}
        stop_tasks = {}

        def convert_task(task):
            _d = {}
            for k, v in TERMINAL_CONVERT_COLUMN.items():
                # 规则转换（进行服务端的规范0和1转换）
                if k in [
                    "queueEnable",
                    "screenRecordEnable",
                    "virtualDesktopEnable",
                    "timeoutEnable",
                ]:
                    _d[v] = True if task.get(k) == 1 else False
                    continue
                _d[v] = task.get(k)
            _d["enable"] = True
            _d["mode"] = "DISPATCH"

            if _d.get("cron_json"):
                # cron_json拆包
                _d.update(json.loads(_d.get("cron_json")))

            if _d.get("callback_project_ids"):
                for project in _d.get("callback_project_ids"):
                    for key, value in project.items():
                        if value is None:
                            project[key] = ""
                    if project.get("robotVersion"):
                        # 引擎内部用version流转，上下服务端用robotVersion流转
                        project["version"] = project.get("robotVersion")

            if _d.get("retry_num"):
                _d["retry_num"] = int(_d.get("retry_num"))
            else:
                _d["retry_num"] = 0

            if _d.get("task_type") == "trigger":
                _d["task_type"] = "schedule"
            return _d

        for record in recorder.get("dispatchTaskInfos", []):
            _d = convert_task(record)
            dispatch_tasks[_d["trigger_id"]] = _d
        for record in recorder.get("retryTaskInfos", []):
            _d = convert_task(record)
            retry_tasks[_d["trigger_id"]] = _d
        for record in recorder.get("stopTaskInfos", []):
            _d = convert_task(record)
            stop_tasks[_d["trigger_id"]] = _d

        return dispatch_tasks, retry_tasks, stop_tasks

    url = "http://127.0.0.1:{}/api/robot/dispatch-task/terminal-task-detail".format(config.GATEWAY_PORT)
    headers = {"Content-Type": "application/json"}
    params = {"terminalId": config.TERMINAL_ID}
    response = requests.request("GET", url, headers=headers, params=params, timeout=5)
    if int(response.status_code) == 200:
        return convert(response.json()["data"])
    else:
        return None
