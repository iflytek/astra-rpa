import argparse
import json
import os
import threading
import time

from rpa_executor.apis.ws import Ws
from rpa_executor.executor import Executor
from rpa_executor.flow.svc import Svc
from rpa_executor.flow.syntax import Environment
from rpa_executor.logger import logger  # 必须排第一
from rpa_executor.tools import log_tool, recording_tool
from rpa_executor.utils import kill_proc_tree


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))

    parser.add_argument("--cache_dir", default=".", help="[系统配置]缓存目录", required=False)
    parser.add_argument("--port", default="8077", help="[系统配置]本地端口号", required=False)
    parser.add_argument("--gateway_port", default="8003", help="[系统配置]网关端口", required=False)

    parser.add_argument(
        "--mode",
        default="EDIT_PAGE",
        help="[启动配置]运行场景[PROJECT_LIST, EDIT_PAGE, CRONTAB, EXECUTOR]",
        required=False,
    )
    parser.add_argument("--version", default="", help="[启动配置]运行版本", required=False)
    parser.add_argument("--project_id", default="", help="[启动配置]启动的工程id", required=True)
    parser.add_argument("--process_id", default="", help="[启动配置]启动的流程id", required=False)
    parser.add_argument("--line", default="0", help="[启动配置]启动的行号", required=False)
    parser.add_argument("--end_line", default="0", help="[启动配置]结束的行号", required=False)
    parser.add_argument("--debug", default="n", help="[启动配置]是否是debug模式 y/n", required=False)
    parser.add_argument("--exec_id", default="", help="[启动配置]启动的执行id", required=False)

    parser.add_argument("--log_ws", default="y", help="[ws功能配置]ws通信，ws总开关 y/n", required=False)
    parser.add_argument(
        "--wait_web_ws",
        default="y",
        help="[ws功能配置]等待前端ws连接 y/n",
        required=False,
    )
    parser.add_argument(
        "--wait_tip_ws",
        default="n",
        help="[ws功能配置]开启并等待右下角ws连接 y/n",
        required=False,
    )

    parser.add_argument(
        "--recording_config",
        default="{}",
        help="[录制功能配置]录制功能配置json",
        required=False,
    )

    parser.add_argument("--run_param", default="", help="运行参数", required=False)

    parser.add_argument("--project_name", default="RPA机器人", help="工程名称", required=False)
    args = parser.parse_args()

    logger.debug("start {}".format(args))

    recording_config = {}  # 初始化录制配置
    if args.recording_config:
        try:
            recording_config = json.loads(args.recording_config)
        except Exception as e:
            pass
    run_param = {}
    if args.run_param:
        try:
            run_param = json.loads(args.run_param)
        except Exception as e:
            pass

    # 初始化Svc服务
    svc = Svc(
        cache_dir=args.cache_dir,
        gateway_port=args.gateway_port,
        project_id=args.project_id,
        project_name=args.project_name,
        port=args.port,
        debug=(args.debug == "y"),
        log_ws=(args.log_ws == "y"),
        exec_id=args.exec_id,
        recording_config=recording_config,
        mode=args.mode,
        run_param=run_param,
        version=args.version,
    )

    # Ws服务基于配置启动
    ws = Ws(svc=svc, port=args.port)
    if args.log_ws == "y":
        ws.is_open_web_link = args.wait_web_ws == "y"
        ws.is_open_top_link = args.wait_tip_ws == "y"
        thread_ws = threading.Thread(target=ws.server, args=(), daemon=True)
        thread_ws.start()
        logger.debug("Wait for the websocket connection")

    # 录制服务基于配置启动
    if recording_config.get("enable", False):
        file_clear_time = recording_config.get("fileClearTime", 0)
        if not recording_config.get("saveType", False):
            file_clear_time = 0
        config = {
            "open": recording_config.get("enable", False),
            "cut_time": recording_config.get("cutTime", 0),
            "scene": recording_config.get("scene", "always"),
            "file_path": recording_config.get("filePath", "./logs/report"),
            "file_clear_time": file_clear_time,  # 清理录制视频7天
        }
        recording_tool.init(args.project_id, args.exec_id, config).start()

    # 右下角日志窗口基于配置启动
    if args.wait_tip_ws == "y":
        log_tool.init(svc).start()

    # 执行器开启执行__process_init__
    executor = Executor(svc=svc)
    env = Environment()
    program = executor.project_init(
        args.project_id,
        args.process_id,
        args.mode,
        args.version,
        int(args.line),
        int(args.end_line),
        env,
    )
    thread_init = threading.Thread(target=executor.__process_init__, args=(program,), daemon=True)
    thread_init.start()

    # 开启执行前，等待ws(n)s内没有连接
    if args.log_ws == "y":
        wait_time = 0
        while not ws.check_ws_link():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 10:
                # 等待1s, 如果正常逻辑没有退出，就强制结束
                logger.error("The websocket connection timed out")
                svc.event_stop(False)
                time.sleep(1)
                svc.sys_exit(True)
                kill_proc_tree(os.getpid(), True)

    # 执行器开启执行__process_run__
    thread_run = threading.Thread(
        target=executor.__process_run__,
        args=(
            program,
            env,
        ),
        daemon=True,
    )
    thread_run.start()
    while thread_run.is_alive():  # 用is_alive替代join，使主线程不会被阻塞，用户监听kill命令
        time.sleep(0.1)
    thread_run.join()

    # 执行器完成后，等待ws消费完成
    if args.log_ws == "y" and args.wait_web_ws == "y":  # ws.is_open_top_link 不用考虑是否发送完成
        wait_time = 0
        size = svc.report.code.queue.qsize()
        while not svc.report.code.queue.empty():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 3:
                wait_time = 0
                if size == svc.report.code.queue.qsize():  # 等待日志(n)s内没有任何发送，就不发送了，直接退出
                    logger.error("The websocket connection send timed out")
                    break
                else:
                    size = svc.report.code.queue.qsize()

    # 等待1s, 如果正常逻辑没有退出，就强制结束
    logger.debug("end ok")
    time.sleep(1)
    svc.sys_exit(False)
    kill_proc_tree(os.getpid(), True)
