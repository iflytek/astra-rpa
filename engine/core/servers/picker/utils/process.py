import os
from typing import Dict, List, Optional, Tuple

import psutil

from ..logger import logger


def get_process_name(pid: int):
    p = psutil.Process(pid)
    return p.name().split(".exe")[0] if p.name().endswith(".exe") else p.name()


def get_process_info(pid: int) -> Dict:
    """获取进程详细信息"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        name = process_name.split(".exe")[0] if process_name.endswith(".exe") else process_name

        # 获取父进程信息
        parent_info = None
        try:
            parent_process = process.parent()
            if parent_process:
                parent_process_name = parent_process.name()
                if parent_process_name.endswith(".exe"):
                    parent_name = parent_process_name.split(".exe")[0]
                else:
                    parent_name = parent_process_name
                parent_info = {
                    "pid": parent_process.pid,
                    "name": parent_name,
                    "cmdline": (" ".join(parent_process.cmdline()) if parent_process.cmdline() else ""),
                }
        except:
            pass

        return {
            "pid": pid,
            "name": name,
            "cmdline": " ".join(process.cmdline()) if process.cmdline() else "",
            "parent": parent_info,
        }
    except Exception as e:
        return {"pid": pid, "name": f"未知进程 (PID: {pid})", "error": str(e)}


def find_real_application_process(webview_pid: int) -> Optional[Dict]:
    """
    从WebView2进程追踪到真正的应用程序进程
    """
    try:
        webview_process = psutil.Process(webview_pid)

        # 检查是否是WebView2进程
        if "msedgewebview2" not in webview_process.name().lower():
            return get_process_info(webview_pid)

        # 如果是WebView2，查找父进程
        parent_process = webview_process.parent()
        if parent_process:
            # 检查父进程是否也是系统进程，如果是，继续向上查找
            parent_name = parent_process.name().lower()

            # 跳过一些系统进程
            system_processes = ["svchost", "explorer", "winlogon", "csrss", "lsass"]

            if any(sys_proc in parent_name for sys_proc in system_processes):
                # 尝试通过命令行参数找到真正的应用
                cmdline = webview_process.cmdline()
                for cmd_part in cmdline:
                    if "--app-id=" in cmd_part or ".exe" in cmd_part:
                        # 可能包含应用信息
                        break

                return get_process_info(parent_process.pid)
            else:
                return get_process_info(parent_process.pid)

        # 如果没有找到合适的父进程，返回WebView2的信息
        return get_process_info(webview_pid)

    except Exception as e:
        logger.info(f"从WebView2进程追踪到真正的应用程序进程出现了异常{e}")
        return get_process_info(webview_pid)


def get_java_process() -> Tuple[List[int], List[str]]:
    username = os.getenv("USERNAME")
    if not username:
        logger.error("无法获取当前用户名")
        return [], []

    temp_dir = os.path.join("C:\\Users", username, "AppData", "Local", "Temp")
    hsperf_dir = os.path.join(temp_dir, f"hsperfdata_{username}")
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
