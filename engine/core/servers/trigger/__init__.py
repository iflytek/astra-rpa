from typing import List, Optional

from pydantic import BaseModel


# 任务参数模型
class TaskInput(BaseModel):
    task_type: str
    enable: bool
    callback_project_ids: list
    queue_enable: bool
    exceptional: str
    timeout: int = 9999

    # 定时调度参数
    end_time: Optional[str] = None
    frequency_flag: str = None
    minutes: Optional[int] = None
    hours: Optional[int] = None
    weeks: Optional[list[int]] = None
    months: Optional[list[int]] = None
    time_expression: Optional[str] = None
    cron_expression: Optional[str] = None

    # 邮件参数
    user_mail: str = None
    user_password: str = None
    mail_flag: str = None
    end_time: Optional[str] = None
    interval_time: int = 1
    condition: str = None
    sender_text: Optional[str] = None
    receiver_text: Optional[str] = None
    theme_text: Optional[str] = None
    content_text: Optional[str] = None
    attachment: Optional[bool] = None
    custom_mail_server: Optional[str] = None
    custom_mail_port: Optional[str] = None

    # 文件任务参数
    directory: str = None
    relative_sub_path: bool = False
    events: list[str] = None
    files_or_type: list[str] = None

    # 热键参数
    shortcuts: list = None

    # 手动触发参数
    pass


class TaskIdInput(BaseModel):
    task_id: str


class NotifyReq(BaseModel):
    event: str = "normal"  # "login" "normal" "exit" "switch


class TaskFutureExecWithoutIdInput(BaseModel):
    times: int = None
    end_time: Optional[str] = None
    frequency_flag: str = None
    minutes: Optional[int] = None
    hours: Optional[int] = None
    weeks: Optional[list[int]] = None
    months: Optional[list[int]] = None
    time_expression: Optional[str] = None
    cron_expression: Optional[str] = None


class RemoveQueueTaskInput(BaseModel):
    unique_id: list[str] = []


class QueueConfigInput(BaseModel):
    max_length: int
    max_wait_minutes: int
    deduplicate: bool


class TaskFutureExecInput(BaseModel):
    task_id: str
    times: int


class UserIdInput(BaseModel):
    user_id: str


class MailDetectInput(BaseModel):
    mail_flag: str
    custom_mail_server: str
    custom_mail_port: str
    user_mail: str
    user_authorization: str


class ConfigInput(BaseModel):
    terminal_mode: bool


CONVERT_COLUMN = {
    "taskId": "trigger_id",
    "name": "trigger_name",
    "taskType": "task_type",
    "enable": "enable",
    "taskJson": "trigger_json",
    "exceptional": "exceptional",
    "timeout": "timeout",
    "mode": "mode",
    "queueEnable": "queue_enable",
    "robotInfoList": "callback_project_ids",
    "screenRecordEnable": "screen_record_enable",
    "virtualDesktopEnable": "open_virtual_desk",
}

TERMINAL_CONVERT_COLUMN = {
    "taskId": "trigger_id",
    "taskName": "trigger_name",
    "taskType": "task_type",
    "cronJson": "cron_json",
    "taskStatus": "task_status",
    "exceptional": "exceptional",
    "timeout": "timeout",
    "timeoutEnable": "timeout_enable",
    "retryNum": "retry_num",
    "queueEnable": "queue_enable",
    "screenRecordEnable": "screen_record_enable",
    "virtualDesktopEnable": "open_virtual_desk",
    "dispatchRobotInfos": "callback_project_ids",
}
