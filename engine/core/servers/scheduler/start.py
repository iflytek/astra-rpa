import argparse
import json
import time
import traceback

import uvicorn
from fastapi import FastAPI

from .apis import route
from .config import Config as conf
from .core.environment.init import linux_env_check, repair_pywin32_dependence
from .core.server import ServerManager
from .core.servers.async_server import (
    AtomicUploadAsyncServer,
    CheckPickProcessAliveServer,
    RpaSchedulerAsyncServer,
    TerminalAsyncServer,
)
from .core.servers.core_server import (
    RpaBrowserConnectorServer,
    RpaRouteServer,
)
from .core.svc import get_svc
from .utils.utils import check_port

from .logger import logger  # isort: skip # 必须排第一

# 0. app实例化，并做初始化
app = FastAPI()
route.handler(app)


def start():
    try:
        # 1. 初始化配置
        parser = argparse.ArgumentParser(description="{} service".format("scheduler"))
        parser.add_argument("--conf", type=str, default="", help="配置文件")
        args = parser.parse_args()

        logger.info("args: {} service[:{}] start".format(args, "scheduler"))

        # 2. 读取配置，并解析到上下文
        conf_path = args.conf.strip('"')
        conf_path = conf_path.replace("\\\\", "\\")
        with open(conf_path, "r") as f:
            conf_json = json.loads(f.readline().strip())

        conf.app_server.remote_addr = conf_json.get("remote_addr")
        conf.app_server.conf_file = conf_path
        conf.base_pipy_server.pypi_remote = conf_json.get("pypi_remote")

        svc = get_svc()
        svc.set_config(conf)

        # 3. 环境检测
        repair_pywin32_dependence(svc)
        linux_env_check()

        # 4. 服务注册与启动
        server_mg = ServerManager(svc)
        server_mg.register(RpaRouteServer(svc))
        server_mg.register(RpaBrowserConnectorServer(svc))
        server_mg.register(RpaSchedulerAsyncServer(svc))
        server_mg.register(TerminalAsyncServer(svc))
        server_mg.register(AtomicUploadAsyncServer(svc))
        server_mg.register(CheckPickProcessAliveServer(svc))

        server_mg.register(svc.trigger_server)
        if svc.vnc_server:
            server_mg.register(svc.vnc_server)
        server_mg.run()

        # 5. 等待本地网关加载完成，并注册服务
        while check_port(port=svc.route_port):  # 等待本地路由加载完成
            time.sleep(0.1)
        svc.route_server_is_start = True
        svc.register_server()

        # 6. 向前端发送完成初始化完成消息, 写到了 startup 方法里面

        # 7. 启动服务
        uvicorn.run(
            app="engine.core.servers.scheduler.start:app",
            host="0.0.0.0",
            port=svc.scheduler_port,
            workers=1,
        )
    except Exception as e:
        logger.error("scheduler error: {} traceback: {}".format(e, traceback.format_exc()))


if __name__ == "__main__":
    start()
