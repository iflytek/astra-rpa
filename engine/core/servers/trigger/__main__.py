import argparse

from .core.config import config
from .core.logger import logger
from .server.server import app

if __name__ == "__main__":
    # 读取配置
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="8087", help="[系统配置]本地端口号", required=False)
    parser.add_argument("--gateway_port", default="8003", help="[系统配置]网关端口", required=False)
    parser.add_argument("--terminal_mode", default="n", help="[系统配置]是否为调度模式", required=False)
    parser.add_argument("--terminal_id", help="[系统配置]调度模式终端ID", required=True)
    args = parser.parse_args()

    logger.info("start trigger {}".format(args))

    config.PORT = args.port
    config.GATEWAY_PORT = args.gateway_port
    config.TERMINAL_MODE = True if args.terminal_mode == "y" else False
    config.TERMINAL_ID = args.terminal_id

    # 启动服务
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(args.port))
