import argparse
import threading

from .logger import logger
from .server.ws_server import WsServer
from .svc import ServiceContext


def start():
    parser = argparse.ArgumentParser(description=f"{'executor'} service")

    parser.add_argument("--port", help="服务http端口", type=int, default=8101)
    parser.add_argument("--route_port", help="浏览器通信中间件端口", type=int, default=8003)
    parser.add_argument("--highlight_socket_port", help="高亮程序端口号", type=int, default=11001)

    args = parser.parse_args()

    # 初始化
    logger.debug(f"ws start {args}")
    service_context = ServiceContext(
        port=args.port,
        highlight_socket_port=args.highlight_socket_port,
        route_port=args.route_port,
    )

    # 启动ws服务
    ws = WsServer(svc=service_context, port=args.port)
    thread_ws = threading.Thread(target=ws.server, args=(), daemon=True)
    thread_ws.start()

    # 启动拾取服务
    from .server.picker_server import PickerServer

    threading.Thread(target=service_context.load_modules, args=(), daemon=True).start()

    service_context.pick_server = PickerServer(service_context)
    service_context.pick_server.server()
