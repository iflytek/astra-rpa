import asyncio
import os

from rpawebsocket.ws import BaseMsg

from rpa_executor.apis.ws import wsmg
from rpa_executor.flow.svc import Svc
from rpa_executor.logger import logger
from rpa_executor.utils import kill_proc_tree


def init():
    pass


@wsmg.event("flow", "close")
async def close(msg: BaseMsg, svc: Svc):
    if svc:
        # 正常逻辑退出，等待1.5s, 如果正常逻辑没有退出，就强制结束
        logger.debug("end signal")
        svc.event_stop(False)
        await asyncio.sleep(1)
        svc.sys_exit(True)
        kill_proc_tree(os.getpid(), True)
    return {"status": "ok"}


@wsmg.event("flow", "pause")
async def pause(msg: BaseMsg, svc: Svc):
    if svc:
        await svc.event_pause(True)
    return {"status": "ok"}


@wsmg.event("flow", "unpause")
async def unpause(msg: BaseMsg, svc: Svc):
    if svc:
        await svc.event_pause(False)
    return {"status": "ok"}


@wsmg.event("flow", "add_break")
async def add_break_list(msg: BaseMsg, svc: Svc):
    break_list = msg.data.get("break_list")
    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            svc.event_break()["{}-{}".format(v.get("process_id"), v.get("line"))] = True
    return {"status": "ok"}


@wsmg.event("flow", "clear_break")
async def clear_bradk(msg: BaseMsg, svc: Svc):
    break_list = msg.data.get("break_list")
    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            del svc.event_break()["{}-{}".format(v.get("process_id"), v.get("line"))]
    return {"status": "ok"}


@wsmg.event("flow", "continue")
async def debug_continue(msg: BaseMsg, svc: Svc):
    if svc:
        await svc.event_continue()
    return {"status": "ok"}


@wsmg.event("flow", "next")
async def debug_next(msg: BaseMsg, svc: Svc):
    if svc:
        await svc.event_next()
    return {"status": "ok"}
