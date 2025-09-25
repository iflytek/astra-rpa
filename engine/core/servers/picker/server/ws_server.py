import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional

import websockets
from pydantic import BaseModel
from websockets.server import WebSocketServerProtocol

from .. import OperationResult, PickerSign, PickerType, RecordAction
from ..logger import logger


class PickerRequire(BaseModel):
    """拾取器请求参数模型"""

    pick_sign: PickerSign = PickerSign.START
    pick_type: PickerType = PickerType.ELEMENT
    record_action: Optional[RecordAction] = None  # 仅在RECORD时使用
    data: str = None
    ext_data: dict = {}


class PushAcknowledgment(BaseModel):
    """推送消息确认模型 - 专门用于确认推送消息"""

    message_type: str = "ack"  # 标识这是确认消息
    reply_to: str  # 回复的推送消息ID
    status: str = "success"
    data: str = ""
    err_msg: str = ""


class MessageType(Enum):
    """消息类型：区分响应和推送"""

    RESPONSE = "response"  # 对请求的响应
    PUSH = "push"  # 主动推送


class ResponseKey(Enum):
    """引擎响应消息的key值"""

    SUCCESS = "success"
    ERROR = "error"
    CANCEL = "cancel"
    PING = "ping"


class PushKey(Enum):
    """引擎推送消息的key值"""

    RECORD_START = "record_start"
    RECORD_PAUSE = "record_pause"
    RECORD_AUTOMIC_CHOICE = "record_automic_start"
    RECORD_AUTOMIC_DRAW_END = "record_automic_draw_end"


class PickerMessage(BaseModel):
    err_msg: str = ""
    data: str = ""
    key: str
    message_type: Optional[str] = None
    message_id: Optional[str] = None  # 消息唯一ID
    reply_to: Optional[str] = None  # 回复哪个消息的ID

    @classmethod
    def create_response(cls, key: ResponseKey, data: str = "", err_msg: str = ""):
        """创建响应消息"""
        return cls(key=key.value, data=data, err_msg=err_msg)

    @classmethod
    def create_push(cls, key: PushKey, data: str = "", err_msg: str = ""):
        """创建推送消息（带ID）"""
        return cls(
            key=key.value,
            data=data,
            err_msg=err_msg,
            message_type="push",
            message_id=str(uuid.uuid4()),  # 生成唯一ID
        )


class PickerRequestHandler:
    """拾取请求处理器 - 抽离所有业务处理逻辑"""

    def __init__(self, svc):
        self.svc = svc

    async def handle_request(self, ws, input_data: PickerRequire) -> bool:
        """处理拾取请求，返回是否需要关闭连接"""
        logger.info("[RequestHandler] 处理请求: {}".format(input_data))

        if input_data.pick_sign == PickerSign.RECORD:
            await self._handle_record_request(ws, input_data)
            if input_data.record_action == RecordAction.END:
                return True  # 录制end请求不关闭连接
            else:
                return False  # 录制非end请求不关闭连接
        else:
            await self._handle_picker_request(ws, input_data)
            return True  # 其他请求需要关闭连接

    async def _handle_record_request(self, ws, input_data: PickerRequire):
        """处理录制请求"""
        from ..core.recorder_core_win import record_manager

        # 委托给录制管理器处理
        result = await record_manager.handle_record_action(input_data.record_action, ws, self.svc, input_data)
        # 发送响应
        await self._send_response(ws, result)

    async def _handle_picker_request(self, ws, input_data: PickerRequire):
        """处理普通拾取请求"""
        if input_data.pick_sign == PickerSign.START:
            result = await self._handle_pick_start(input_data)
        elif input_data.pick_sign == PickerSign.STOP:
            result = await self._handle_pick_stop(input_data)
        elif input_data.pick_sign == PickerSign.VALIDATE:
            result = await self._handle_pick_validate(input_data)
        elif input_data.pick_sign == PickerSign.HIGHLIGHT:
            result = await self._handle_pick_highlight(input_data)
        elif input_data.pick_sign == PickerSign.GAIN:
            result = await self._handle_pick_gain(input_data)
        else:
            result = OperationResult.error("pick_sign没有实现").to_dict()

        await self._send_response(ws, result)

    async def _handle_pick_start(self, input_data: PickerRequire) -> Dict[str, Any]:
        """处理拾取开始"""
        try:
            from ..core.highlight_client import highlight_client

            with highlight_client:
                highlight_client.start_wnd("normal")

                # 处理拾取数据
                if input_data.pick_type in [PickerType.SIMILAR, PickerType.BATCH]:
                    input_data.data = self._process_element_data(input_data)

                # 发送拾取开始信号
                res = await self.svc.send_sign(PickerSign.START, input_data.model_dump())
                highlight_client.hide_wnd()

                if res == "cancel":
                    return OperationResult.cancel().to_dict()
                elif isinstance(res, dict):
                    res["picker_type"] = input_data.pick_type.name
                    return OperationResult.success(data=res).to_dict()
                else:
                    return OperationResult.error(res).to_dict()

        except Exception as e:
            logger.error(f"拾取开始处理失败: {e}")
            return OperationResult.error(str(e)).to_dict()

    async def _handle_pick_stop(self, input_data: PickerRequire) -> Dict[str, Any]:
        """处理拾取停止"""
        try:
            await self.svc.send_sign(PickerSign.STOP, input_data.model_dump())
            return OperationResult.success().to_dict()
        except Exception as e:
            return OperationResult.error(str(e)).to_dict()

    async def _handle_pick_validate(self, input_data: PickerRequire) -> Dict[str, Any]:
        """处理拾取校验"""
        try:
            from locator.locator import LocatorManager

            from ..core.highlight_client import highlight_client

            with highlight_client:
                highlight_client.start_wnd("validate")
                input_data.data = self._process_element_data(input_data)

                res = LocatorManager().locator(input_data.data)
                if isinstance(res, list):
                    rects = [item.rect() for item in res]
                else:
                    rects = res.rect()

                highlight_client.draw_wnd(rects, "", "validate")

                time.sleep(3)

                return OperationResult.success(data="校验成功").to_dict()

        except Exception as e:
            return OperationResult.error(str(e)).to_dict()

    async def _handle_pick_highlight(self, input_data: PickerRequire) -> Dict[str, Any]:
        """处理拾取高亮"""
        try:
            from locator.locator import LocatorManager

            input_data.data = self._process_element_data(input_data)
            data = (
                LocatorManager.parse_element_json(input_data.data)
                if isinstance(input_data.data, str)
                else input_data.data
            )

            url = f"http://127.0.0.1:{self.svc.route_port}/browser_connector/browser/transition"
            payload = {
                "browser_type": data.get("app"),
                "data": data.get("path"),
                "key": "highLightColumn",
            }

            import requests

            requests.post(url, json=payload)

            return OperationResult.success(data="高亮成功").to_dict()

        except Exception as e:
            return OperationResult.error(str(e)).to_dict()

    async def _handle_pick_gain(self, input_data: PickerRequire) -> Dict[str, Any]:
        """处理拾取获取数据"""
        try:
            from locator.locator import LocatorManager
            from rpa_table_helper.table_filter import (
                DataFilter,
                table_json_merge_values,
            )

            input_data.data = self._process_element_data(input_data)
            data = (
                LocatorManager.parse_element_json(input_data.data)
                if isinstance(input_data.data, str)
                else input_data.data
            )

            url = f"http://127.0.0.1:{self.svc.route_port}/browser_connector/browser/transition"
            batch_element = data.get("path")
            payload = {
                "browser_type": data.get("app"),
                "data": batch_element,
                "key": "getBatchData",
            }

            import requests

            response = requests.post(url, json=payload)
            web_info = response.json()["data"]["data"]
            values = web_info["values"]
            batch_element = table_json_merge_values(batch_element, values)
            locate_data = DataFilter(data_json=batch_element).get_filtered_data()

            return OperationResult.success(data=locate_data).to_dict()

        except Exception as e:
            return OperationResult.error(str(e)).to_dict()

    def _process_element_data(self, input_data: PickerRequire):
        """处理元素数据"""
        import rpa_param_utils.param_utils
        from locator.locator import LocatorManager

        global_data = input_data.ext_data.get("global", [])
        env, id2name = rpa_param_utils.param_utils.global_to_dict(global_data)
        data = (
            LocatorManager.parse_element_json(input_data.data) if isinstance(input_data.data, str) else input_data.data
        )
        return rpa_param_utils.param_utils.special_eval_element(data, env, id2name)

    async def _send_response(self, ws, result: Dict[str, Any]):
        """发送响应消息"""
        if result.get("success"):
            data = result.get("data", "")
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
            await ws.send(PickerMessage.create_response(ResponseKey.SUCCESS, data=data).model_dump_json())

        else:
            if result.get("cancel"):
                await ws.send(PickerMessage.create_response(ResponseKey.CANCEL).model_dump_json())
            error_msg = result.get("error", "未知错误")
            await ws.send(PickerMessage.create_response(ResponseKey.ERROR, err_msg=error_msg).model_dump_json())


class PushManager:
    """推送管理器 - 处理推送消息的发送和确认"""

    def __init__(self):
        self.pending_pushes = {}  # 存储待确认的推送消息

    async def send_push_message(self, ws, push_key: PushKey, data: str = "") -> str:
        """发送推送消息并记录"""
        push_msg = PickerMessage.create_push(push_key, data=data)

        # 记录待确认的推送
        self.pending_pushes[push_msg.message_id] = {
            "type": push_key.value,
            "timestamp": time.time(),
            "data": push_msg.data,
        }

        await ws.send(push_msg.model_dump_json())
        logger.info(f"推送消息: {push_key.value}, ID: {push_msg.message_id}")

        return push_msg.message_id

    async def handle_acknowledgment(self, ack_data: PushAcknowledgment) -> bool:
        """处理推送确认"""
        reply_to_id = ack_data.reply_to
        status = ack_data.status
        data = ack_data.data

        logger.info(f"[PushManager] 收到推送确认: reply_to={reply_to_id}, status={status}")

        if reply_to_id in self.pending_pushes:
            push_info = self.pending_pushes[reply_to_id]
            logger.info(f"前端确认推送 {push_info['type']}: {data}")
            del self.pending_pushes[reply_to_id]
            return True
        else:
            logger.warning(f"收到未知推送ID的确认: {reply_to_id}")
            return False


class WsServer:
    """WebSocket服务器 - 只负责连接管理和消息路由"""

    def __init__(self, svc, port: int):
        self.svc = svc
        self.port = port

        # 业务处理器
        self.request_handler = PickerRequestHandler(svc)
        self.push_manager = PushManager()

        # 设置录制事件回调
        self._setup_record_callbacks()

    def _setup_record_callbacks(self):
        """设置录制事件回调"""
        from ..core.recorder_core_win import record_manager

        record_manager.set_push_callbacks(
            on_f4=self._on_f4_pressed,
            on_esc=self._on_esc_pressed,
            on_hover=self._on_mouse_hover,
            on_mouse_out=self._on_mouse_out,
        )

    async def _on_f4_pressed(self, ws_connection):
        """录制 F4按键回调"""
        await self.push_manager.send_push_message(ws_connection, PushKey.RECORD_START)

    async def _on_esc_pressed(self, ws_connection):
        """录制 ESC按键回调"""
        await self.push_manager.send_push_message(ws_connection, PushKey.RECORD_PAUSE)

    async def _on_mouse_hover(self, ws_connection, rect_data):
        """录制 鼠标悬停回调"""
        await self.push_manager.send_push_message(
            ws_connection,
            PushKey.RECORD_AUTOMIC_CHOICE,  # 复用现有的信号类型
            data=rect_data,
        )

    async def _on_mouse_out(self, ws_connection):
        """录制 鼠标移出悬停元素区域回调"""
        await self.push_manager.send_push_message(ws_connection, PushKey.RECORD_AUTOMIC_DRAW_END)

    async def websocket_endpoint(self, ws: WebSocketServerProtocol):
        """WebSocket端点 - 只负责消息路由"""
        async for message in ws:
            try:
                data = json.loads(message)

                # 1. 检查是否是推送确认消息
                if data.get("message_type") == "ack":
                    ack_data = PushAcknowledgment(**data)
                    await self.push_manager.handle_acknowledgment(ack_data)
                    continue

                # 2. 检查是否是拾取请求
                if data.get("pick_sign"):
                    input_data = PickerRequire(**data)
                    should_close = await self.request_handler.handle_request(ws, input_data)
                    if should_close:
                        await ws.close()
                    continue

                # 3. 未知消息格式
                logger.warning(f"未知的消息格式: {data}")
                await ws.send(
                    PickerMessage.create_response(ResponseKey.ERROR, err_msg="未知的消息格式").model_dump_json()
                )

            except Exception as e:
                import traceback

                logger.error("WebSocket消息处理错误: {} stack: {}".format(e, traceback.format_exc()))
                try:
                    await ws.send(PickerMessage.create_response(ResponseKey.ERROR, err_msg=str(e)).model_dump_json())
                except:
                    pass  # 连接可能已断开

    def server(self) -> None:
        """启动WebSocket服务器"""
        import pythoncom

        pythoncom.CoInitialize()

        async def start_server():
            """异步启动WebSocket服务器"""
            server = await websockets.serve(
                self.websocket_endpoint,
                "127.0.0.1",
                self.port,
                max_size=10 * 1024 * 1024,
            )
            await server.wait_closed()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(start_server())
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info("picker ws接口被中断")
        finally:
            loop.close()
