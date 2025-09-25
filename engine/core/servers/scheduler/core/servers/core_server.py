from urllib.parse import urlparse

import requests

from ... import ComponentType, ServerLevel
from ...utils.subprocess import SubPopen
from ..route.proxy import get_cmd
from ..server import IServer


class RpaRouteServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        super().__init__(svc=svc, name="route", level=ServerLevel.CORE, run_is_async=False)

    def run(self):
        self.port = self.svc.route_port

        self.proc = SubPopen(name="route", cmd=[get_cmd()])
        self.proc.set_param("port", self.port)

        remote_parsed_url = urlparse(self.svc.config.app_server.remote_addr)

        if remote_parsed_url.scheme.lower() == "https":
            self.proc.set_param("httpProtocol", "https")
            self.proc.set_param("wsProtocol", "wss")
        else:
            self.proc.set_param("httpProtocol", "http")
            self.proc.set_param("wsProtocol", "ws")
        # 注意这里不同版本处理结果不一样，同时对于域名端口处理结果也不一样
        self.proc.set_param(
            "remoteHost",
            (
                # f"{remote_parsed_url.hostname}:{remote_parsed_url.port}"
                # if remote_parsed_url.port
                # else f"{remote_parsed_url.hostname}"
                remote_parsed_url.netloc
            ),
        )
        self.proc.run()

    def health(self) -> bool:
        if not self.proc.is_alive():
            return False
        return True

    def recover(self):
        # 先关闭
        self.proc.kill()

        # 再重启
        self.run()


class RpaBrowserConnectorServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        self.err_time = 0
        self.err_max_time = 3
        super().__init__(svc=svc, name="route", level=ServerLevel.CORE, run_is_async=False)

    def run(self):
        self.port = self.svc.browser_connector_port

        self.proc = SubPopen(
            name="browser_connector",
            cmd=[
                self.svc.config.app_server.python_core,
                "-m",
                "engine.core.servers.browser_connector",
            ],
        )
        self.proc.set_param("port", self.port)
        self.proc.run()

    def health(self) -> bool:
        if not self.proc.is_alive():
            return False

        response = requests.get(
            "http://127.0.0.1:{}/{}/browser/health".format(
                self.svc.route_port, ComponentType.BROWSER_CONNECTOR.name.lower()
            )
        )
        status_code = response.status_code
        if status_code != 200:
            self.err_time += 1
        else:
            self.err_time = 0

        if self.err_time >= self.err_max_time:
            return False

        return True

    def recover(self):
        # 先关闭
        self.proc.kill()

        # 再重启
        self.run()
