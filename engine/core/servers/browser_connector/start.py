import argparse
import os

import uvicorn
from browser_connector.apis import context, route
from browser_connector.config import Config as conf
from browser_connector.logger import logger  # 必须排第一
from fastapi import FastAPI
from no_config import Config

# 0. app实例化，并做初始化
app = FastAPI()
route.handler(app)


def start():
    # 1. 初始化配置
    parser = argparse.ArgumentParser(description="{} service".format("rpa-browser-connector"))
    parser.add_argument("--f", default="service.yaml", help="配置文件")
    parser.add_argument("--port", default="19082", help="本地端口号")
    parser.add_argument("--gateway_port", default="", help="网关端口", required=False)
    args = parser.parse_args()
    if os.path.exists(args.f):
        Config.init(args.f)  # 初始化作用是conf赋值，通过注解完成
    if args.port:
        conf.http_settings.app_port = int(args.port)
    if args.gateway_port:
        conf.http_settings.gateway_port = int(args.gateway_port)

    # 2. 上下文
    svc = context.get_svc()
    svc.set_config(conf)

    # 3. FastApi启动
    logger.info("{} service[:{}] start".format(conf.app_settings.app_name, conf.http_settings.app_port))
    logger.info("swagger urL:{}".format("/docs"))
    uvicorn.run(
        app="browser_connector.start:app",
        host=conf.http_settings.app_host,
        port=conf.http_settings.app_port,
    )
