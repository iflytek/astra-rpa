import os
from typing import List, Tuple

import psutil
from rpaframe.logger.logger import logger


def get_process_name(pid: int):
    p = psutil.Process(pid)
    return p.name().split(".exe")[0] if p.name().endswith(".exe") else p.name()


def get_java_process() -> Tuple[List[int], List[str]]:
    username = os.getenv("USERNAME")
    if not username:
        logger.error("无法获取当前用户名")
        return [], []

    hsperf_dir = os.path.join("C:\\Users", username, "AppData", "Local", "Temp", f"hsperfdata_{username}")
    if not os.path.exists(hsperf_dir):
        logger.error(f"hsperf不存在: {hsperf_dir}")
        return [], []

    # 收集所有数字文件名（潜在PID）
    pids = []
    for filename in os.listdir(hsperf_dir):
        if filename.isdigit():
            try:
                pid = int(filename)
                pids.append(pid)
            except ValueError:
                continue

    # 验证进程是否实际存在
    java_pids = []
    for pid in pids:
        if psutil.pid_exists(pid):
            java_pids.append(pid)

    # 构建数据
    prod_name_list = []
    prod_pid_list = []
    if java_pids:
        for pid in java_pids:
            process_info = psutil.Process(pid)
            prod_name_list.append(process_info.name())
            prod_pid_list.append(pid)
    return prod_pid_list, prod_name_list
