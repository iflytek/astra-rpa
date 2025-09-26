import asyncio
import os
import traceback
from base64 import b64decode
from typing import Any

from fastapi import APIRouter, Depends
from rpawebsocket.ws import BaseMsg, Conn, IWebSocket, WsException
from rpawebsocket.ws_service import WsManager
from starlette.websockets import WebSocket

from ..apis.context import ServiceContext, get_svc
from ..apis.response import CustomResponse
from ..error import CODE_INNER, ERROR_FORMAT, BaseException
from ..logger import logger


def error_to_base_error(e=None) -> BaseException:
    if isinstance(e, BaseException):
        return e
    elif isinstance(e, WsException):
        return BaseException(ERROR_FORMAT.format(e), "ERROR_FORMAT error: {}".format(e))
    else:
        return BaseException(CODE_INNER, "raw error: {}".format(e))


def error_format(e=None) -> dict:
    def gen_error_msg(exc: BaseException):
        logger.error(
            "http_base_exception: code:{} message:{} httpcode:{} error:{}".format(
                exc.code.code, exc.code.message, exc.code.httpcode, exc.message
            )
        )
        logger.error("http_base_exception: traceback:{}".format(traceback.format_exc()))

        return CustomResponse(exc.code.code.value, exc.code.message, {}).__dict__

    return gen_error_msg(error_to_base_error(e))


def ws_log(msg):
    logger.info(msg)


wsmg = WsManager(error_format=error_format, log=ws_log)
router = APIRouter()

inject_path = os.path.abspath(__file__)
for _ in range(2):
    inject_path = os.path.dirname(inject_path)
inject_path = os.path.join(inject_path, "inject")


class WsSocket(IWebSocket):
    def __init__(self, ws: WebSocket):
        self.ws = ws

    async def receive_text(self) -> str:
        return await self.ws.receive_text()

    async def send(self, message: Any) -> None:
        return await self.ws.send({"type": "websocket.send", "text": message})

    async def close(self) -> None:
        return await self.ws.close()


async def browser_init_inject(ws: IWebSocket, uuid: str):
    data_list = [
        {
            "data_path": os.path.join(inject_path, "backgroundInject.js"),
            "key": "backgroundInject",
        },
        {
            "data_path": os.path.join(inject_path, "contentInject.js"),
            "key": "contentInject",
        },
    ]
    for data in data_list:
        with open(data.get("data_path"), encoding="utf-8") as file:
            file_data = file.read()
        await ws.send(
            BaseMsg(
                channel="browser",
                key=data.get("key"),
                uuid="$root$",
                send_uuid=uuid,
                need_ack=False,
                data=file_data,
            )
            .init()
            .tojson()
        )


@router.websocket("")
async def websocket_endpoint(ws: WebSocket, svc: ServiceContext = Depends(get_svc), token: str = None):
    await ws.accept()
    if not token:
        token = ws.headers.get("token", "")
    uuid = ""
    if token:
        try:
            uuid = b64decode(token).decode("utf-8")
        except Exception as e:
            pass
    if not uuid:
        return

    ws = WsSocket(ws)
    await browser_init_inject(ws, uuid)
    await asyncio.gather(wsmg.listen(uuid, Conn(ws=ws), svc), wsmg.start_ping(), wsmg.clear_watch())
