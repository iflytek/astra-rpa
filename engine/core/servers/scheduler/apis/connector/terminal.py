import base64
import io

import pyautogui
from fastapi import APIRouter, Depends

from ...apis.response import ResCode, res_msg
from ...core.svc import Svc, get_svc
from ...core.terminal.terminal import Terminal

router = APIRouter()


@router.post("/start")
def terminal_start(svc: Svc = Depends(get_svc)):
    svc.terminal_mod = True
    Terminal.register(svc)  # 强行注册一下
    Terminal.upload(svc)  # 强行更新一下
    if svc.executor_mg:
        svc.executor_mg.close_all()  # 关闭正在进行的任务
    svc.trigger_server.update_config(svc.terminal_mod)
    return res_msg(msg="启动成功", data=None)


@router.post("/end")
def terminal_end(svc: Svc = Depends(get_svc)):
    svc.terminal_mod = False
    Terminal.upload(svc)  # 强行更新一下
    if svc.vnc_server:
        svc.vnc_server.close()  # 强制关闭不必要的服务
    if svc.executor_mg:
        svc.executor_mg.close_all()  # 关闭正在进行的任务
    svc.trigger_server.update_config(svc.terminal_mod)
    return res_msg(msg="结束成功", data=None)


@router.get("/ping")
def terminal_ping(svc: Svc = Depends(get_svc)):
    """
    使用pyautogui获取当前屏幕的截图并返回base64编码
    """
    try:
        if not svc.terminal_mod:
            return res_msg(
                code=ResCode.SUCCESS,
                msg="pong",
                data={
                    "width": 0,  # 屏幕框
                    "height": 0,  # 屏幕高
                    "terminal_mod": svc.terminal_mod,  # 模式
                    "vnc_port": "",  # 端口
                    "curr_status": False,  # 当前状态
                    "curr_task_name": "",  # 只有curr_status为true才有效
                    "curr_project_name": "",
                    "curr_log_name": "",
                    "base64": "",  # 渲染图片
                },
            )

        # 获取屏幕截图
        screenshot = pyautogui.screenshot()

        # 将图片转换为字节流
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # 转换为base64编码
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        curr_status = svc.executor_mg.status()
        return res_msg(
            code=ResCode.SUCCESS,
            msg="pong",
            data={
                "width": screenshot.width,  # 屏幕框
                "height": screenshot.height,  # 屏幕高
                "terminal_mod": svc.terminal_mod,  # 模式
                "vnc_port": (svc.vnc_server.vnc_ws_port if svc.vnc_server else ""),  # 端口
                "curr_status": svc.executor_mg.status(),  # 当前状态
                "curr_task_name": (
                    svc.executor_mg.curr_task_name if curr_status else ""
                ),  # 只有curr_status为true才有效
                "curr_project_name": (svc.executor_mg.curr_project_name if curr_status else ""),
                "curr_log_name": svc.executor_mg.curr_log_name if curr_status else "",
                "base64": f"data:image/png;base64,{img_base64}",  # 渲染图片
            },
        )
    except Exception as e:
        return res_msg(code=ResCode.ERR, msg=f"获取失败: {str(e)}", data=None)


@router.get("/terminal_id")
def terminal_id():
    return res_msg(msg="获取成功", data={"terminal_id": Terminal.get_terminal_id()})
