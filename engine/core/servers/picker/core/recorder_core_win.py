import asyncio
import json
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from .. import (
    RECORDING_BLACKLIST,
    DrawResult,
    MKSign,
    OperationResult,
    PickerType,
    Point,
    RecordAction,
    Rect,
)
from ..engines.uia_picker import UIAOperate
from ..logger import logger
from ..utils.process import find_real_application_process
from .picker_core_win import PickerCore


class RecordingState(Enum):
    """录制状态枚举"""

    IDLE = "idle"
    LISTENING = "listening"
    RECORDING = "recording"
    PAUSED = "paused"


class RecordPickerAdapter:
    """录制功能的拾取适配器"""

    def __init__(self, picker_core: PickerCore):
        self.picker_core = picker_core
        self.enable_blacklist = True

    def set_blacklist_enabled(self, enabled: bool):
        """设置是否启用黑名单功能"""
        self.enable_blacklist = enabled

    def draw_for_record(self, svc, highlight_client, data: dict) -> DrawResult:
        """为录制模式定制的拾取绘制"""
        try:
            # 检查是否需要黑名单处理
            if self.enable_blacklist and self._should_use_blacklist(data):
                blacklist_result = self._handle_blacklist(highlight_client)
                if blacklist_result:
                    return blacklist_result

            # 调用核心拾取功能
            return self.picker_core.draw(svc, highlight_client, data)

        except Exception as e:
            logger.error(f"录制模式拾取失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def _should_use_blacklist(self, data: dict) -> bool:
        """判断是否应该使用黑名单逻辑"""
        pick_type = data.get("pick_type")
        # 只有元素拾取类型才需要黑名单处理
        return pick_type in [PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]

    def _handle_blacklist(self, highlight_client) -> Optional[DrawResult]:
        """处理黑名单逻辑"""
        try:
            # 获取当前鼠标位置的控件信息
            current_x, current_y = UIAOperate.get_cursor_pos()
            current_point = Point(current_x, current_y)
            start_control = UIAOperate.get_windows_by_point(current_point)
            if not start_control:
                logger.info(f"获取点位所在uia-control出错{self.picker_core.last_point}")
                raise Exception("拾取转换器出错，请退出项目重新开始")

            process_id = UIAOperate.get_process_id(start_control)
            process_info = find_real_application_process(process_id)
            process_name = process_info["name"]

            # 检查是否在黑名单中
            if process_name in RECORDING_BLACKLIST:
                logger.debug("当前应用在录制黑名单中，使用上一次的拾取结果")
                return self._use_cached_result(highlight_client, process_name)
            return None  # 不在黑名单中，继续正常拾取

        except Exception as e:
            logger.error(f"黑名单处理失败: {e}")
            return None

    def _use_cached_result(self, highlight_client, process_name: str) -> DrawResult:
        """使用缓存的拾取结果"""
        if self.picker_core.last_valid_rect:
            # 有缓存结果，重新绘制
            logger.info(f"当前落点是{process_name} 缓存结果是 {self.picker_core.last_valid_rect.to_json()}")
            highlight_client.draw_wnd(self.picker_core.last_valid_rect, msgs=self.picker_core.last_valid_tag)
            return DrawResult(
                success=True,
                rect=self.picker_core.last_valid_rect,
                app=process_name,
                domain=self.picker_core.last_valid_domain,
            )
        else:
            logger.info(f"缓存结果是{process_name} {-1, -1, -1, -1}")
            # 没有缓存结果，返回占位符
            placeholder_rect = Rect(-1, -1, -1, -1)
            return DrawResult(
                success=True,  # 虽然是占位符，但对录制来说这是正常情况
                rect=placeholder_rect,
                app=process_name,
                domain=None,  # 占位符结果没有 domain 信息
            )


class RecordManager:
    """录制管理器 - 统一管理录制状态、事件监控和回调"""

    def __init__(self):
        self.svc = None
        self.highlight_client = None
        self.state = RecordingState.IDLE
        self.ws_connection = None

        # 录制专用的拾取适配器
        self.record_adapter: Optional[RecordPickerAdapter] = None

        # 绘框相关
        self.drawing_thread: Optional[threading.Thread] = None
        self.stop_drawing = False

        # 事件监控相关
        self.event_monitor_task = None

        # 右击后的预拾取元素
        self.last_element = None

        # 当前显示的rect
        self.cur_rect = None
        self.cur_app = None
        self.cur_domain = None

        # 回调函数
        self.push_callbacks = {
            "on_f4": None,
            "on_esc": None,
            "on_hover": None,
            "on_mouse_out": None,
        }

        # 悬停触发选项
        self.hover_triggered = False  # 防止重复触发
        self.hover_threshold = 0.2  # 悬停时间阈值(秒)
        self.hover_start_time = None
        self.is_hover_paused = False  # 后端拾取是否因为前端hover而暂停
        self.last_hover_rect = None  # 上次悬停检测时的矩形区域，用于检测元素变化

        # 绘框黑名单开关
        self.enable_record_blacklist = True

    def initialize(self, svc):
        """初始化管理器（在svc创建后调用）"""
        self.svc = svc
        from .highlight_client import highlight_client

        self.highlight_client = highlight_client
        while True:
            if not self.svc.event_core:
                logger.info("svc.event_core初始化中....")
                time.sleep(0.1)
                continue
            if not self.svc.picker_core:
                logger.info("svc.picker_core初始化中....")
                time.sleep(0.1)
                continue
            # 两个组件都已初始化完成，跳出循环
            break

        # 创建录制专用适配器
        if svc.picker_core and not self.record_adapter:
            self.record_adapter = RecordPickerAdapter(svc.picker_core)
            self.record_adapter.set_blacklist_enabled(self.enable_record_blacklist)

    def set_push_callbacks(
        self,
        on_f4: Callable = None,
        on_esc: Callable = None,
        on_hover: Callable = None,
        on_mouse_out: Callable = None,
    ):
        """设置推送回调函数"""
        self.push_callbacks["on_f4"] = on_f4
        self.push_callbacks["on_esc"] = on_esc
        self.push_callbacks["on_hover"] = on_hover
        self.push_callbacks["on_mouse_out"] = on_mouse_out
        logger.info("录制管理器：设置推送回调函数，f4...esc...on_hover")

    async def handle_record_action(self, action: RecordAction, ws, svc, input_data) -> Dict[str, Any]:
        """处理录制动作"""
        self.initialize(svc)  # 确保svc是最新的
        try:
            if action == RecordAction.LISTENING:
                return await self._handle_listening(ws)
            elif action == RecordAction.START:
                return await self._handle_start()
            elif action == RecordAction.PAUSE:
                return await self._handle_pause()
            elif action == RecordAction.HOVER_START:  # 关闭绘框操作
                return await self._handle_hover_start()
            elif action == RecordAction.HOVER_END:  # 开启绘框操作
                return await self._handle_hover_end()
            elif action == RecordAction.AUTOMIC_END:
                return await self._handle_atomic_end(input_data)
            elif action == RecordAction.END:
                return await self._handle_end()
            else:
                return OperationResult.error(f"未知的录制动作: {action}").to_dict()
        except Exception as e:
            import traceback

            error_traceback = traceback.format_exc()
            # 记录堆栈信息到日志
            logger.error(f"处理录制动作失败: {e}\n完整堆栈信息:\n{error_traceback}")
            return OperationResult.error(str(e)).to_dict()

    async def _handle_listening(self, ws) -> Dict[str, Any]:
        """处理监听动作"""
        if self.state != RecordingState.IDLE:
            return OperationResult.error(f"无法开始监听，当前状态: {self.state.value}").to_dict()

        is_start = self.svc.event_core.start(domain=MKSign.RECORD)
        if is_start:
            logger.info("录制键鼠监听开启成功")

        self.state = RecordingState.LISTENING
        self.ws_connection = ws
        self.highlight_client.start_wnd("record")

        # 启动事件监控
        self.event_monitor_task = asyncio.create_task(self._monitor_events())

        logger.info("录制管理器：开始监听模式")
        return OperationResult.success().to_dict()

    async def _handle_start(self) -> Dict[str, Any]:
        """处理开始录制动作"""
        if self.state not in [RecordingState.LISTENING, RecordingState.PAUSED]:
            return OperationResult.error(f"无法开始录制，当前状态: {self.state.value}").to_dict()

        try:
            self.state = RecordingState.RECORDING
            self._start_continuous_drawing()
            logger.info("录制管理器：开始录制")
            return OperationResult.success().to_dict()
        except Exception as e:
            logger.info(f' "error": f"无法开始录制，当前状态: {self.state.value} {e}"')
            return OperationResult.error("无法开始录制，出现异常").to_dict()

    async def _handle_pause(self) -> Dict[str, Any]:
        """处理暂停录制动作"""
        if self.state != RecordingState.RECORDING:
            return OperationResult.error(f"无法暂停录制，当前状态: {self.state.value}").to_dict()

        self.state = RecordingState.PAUSED
        self._stop_continuous_drawing()

        logger.info("录制管理器：暂停录制")
        return OperationResult.success().to_dict()

    async def _handle_hover_start(self) -> Dict[str, Any]:
        """处理暂停录制动作"""
        if self.state != RecordingState.RECORDING:
            return OperationResult.error(f"无法暂停录制过程的拾取，当前状态: {self.state.value}").to_dict()

        self.is_hover_paused = True
        self.state = RecordingState.PAUSED
        self._stop_continuous_drawing()  # 关闭draw更新，但是不hide最后一次的rect

        logger.info("录制管理器：前端hover暂停录制")
        return OperationResult.success().to_dict()

    async def _handle_hover_end(self) -> Dict[str, Any]:
        """处理暂停录制动作"""
        if self.state not in [RecordingState.PAUSED] and not self.is_hover_paused:
            return OperationResult.error(f"无法开始录制，当前状态: {self.state.value}").to_dict()

        self.state = RecordingState.RECORDING
        self._start_continuous_drawing()
        self.is_hover_paused = False

        logger.info("录制管理器：继续录制")
        return OperationResult.success().to_dict()

    async def _handle_atomic_end(self, input_data) -> Dict[str, Any]:
        """处理原子操作结束"""
        logger.info("走入_handle_atomic_end了")
        was_recording = self.state == RecordingState.RECORDING

        # 临时暂停绘框
        if was_recording:
            self._stop_continuous_drawing()
            # time.sleep(3)

        try:
            # 返回预拾取结果
            res = (
                self.last_element
            )  # self.svc.picker_core.element(self.svc, {"pick_type": PickerType.ELEMENT})#self.last_element#

            if isinstance(res, dict):
                res["picker_type"] = input_data.pick_type.name
                result = OperationResult.success(data=res).to_dict()
            else:
                result = OperationResult.error(res).to_dict()

            return result

        finally:
            # 恢复录制状态
            if was_recording:
                self.state = RecordingState.RECORDING
                self._start_continuous_drawing()

    async def _handle_end(self) -> Dict[str, Any]:
        """处理结束录制动作"""
        # 停止键鼠事件监控的callback
        if self.event_monitor_task:
            self.event_monitor_task.cancel()
            self.event_monitor_task = None

        # 停止绘框
        self._stop_continuous_drawing()

        # 隐藏画框
        self.highlight_client.hide_wnd()

        # 停止监听
        self.svc.event_core.close()

        # 重置状态
        self.state = RecordingState.IDLE
        self.ws_connection = None

        logger.info("录制管理器：结束录制")
        return OperationResult.success().to_dict()

    def _start_continuous_drawing(self):
        """启动持续绘框线程"""
        if self.drawing_thread and self.drawing_thread.is_alive():
            return

        self.stop_drawing = False
        self.hover_start_time = None  # 关闭绘框后也要更新键鼠监听hover的数据

        # 清理缓存的绘框结果，确保从当前鼠标位置重新开始
        if self.record_adapter and self.record_adapter.picker_core:
            self.record_adapter.picker_core.last_valid_rect = None
            self.record_adapter.picker_core.last_valid_tag = ""
            logger.debug("已清理绘框缓存，将从当前鼠标位置重新开始")

        self.drawing_thread = threading.Thread(target=self._continuous_drawing_loop, daemon=True)
        self.drawing_thread.start()
        logger.info("启动持续绘框线程")

    def _stop_continuous_drawing(self):
        """停止持续绘框"""
        self.stop_drawing = True
        if self.drawing_thread and self.drawing_thread.is_alive():
            self.drawing_thread.join(timeout=0.5)

    def _continuous_drawing_loop(self):
        """持续绘框循环"""
        import pythoncom

        pythoncom.CoInitialize()
        self.highlight_client.start_wnd("record")
        while not self.stop_drawing and self.state == RecordingState.RECORDING:
            try:
                # 使用录制专用适配器进行拾取
                draw_data = {
                    "pick_type": PickerType.ELEMENT,
                }

                if self.record_adapter:
                    result: DrawResult = self.record_adapter.draw_for_record(self.svc, self.highlight_client, draw_data)
                else:
                    raise Exception("缺少拾取转换器。。。")

                # 更新当前状态
                if result.success and result.rect:
                    self.cur_rect = result.rect
                    self.cur_app = result.app
                    self.cur_domain = result.domain
                # logger.info(f'draw返回的result: success={result.success}, rect={result.rect.to_json() if result.rect else None}')
            except Exception as e:
                import traceback

                error_traceback = traceback.format_exc()
                # 记录堆栈信息到日志
                logger.error(f"持续绘框出错: {e}\n完整堆栈信息:\n{error_traceback}")
                # self.highlight_client.hide_wnd()
                # return
        if not self.is_hover_paused:
            self.highlight_client.hide_wnd()

    async def _monitor_events(self):
        """监控快捷键和鼠标事件"""
        logger.info("开始事件监控")

        try:
            # time.sleep(1)
            await asyncio.sleep(1)
            while self.state != RecordingState.IDLE and self.ws_connection:
                # 检查F4键（开始录制）
                if self.svc.event_core.is_f4_pressed():
                    logger.info("检测到F4按键")
                    self.svc.event_core.reset_f4_flag()

                    # 触发回调
                    if self.push_callbacks["on_f4"] and self.state in [
                        RecordingState.LISTENING,
                        RecordingState.PAUSED,
                    ]:
                        self.state = RecordingState.RECORDING
                        self._start_continuous_drawing()
                        await self.push_callbacks["on_f4"](self.ws_connection)

                # 检查ESC键（暂停录制）
                if self.svc.event_core.is_cancel():
                    logger.info("检测到ESC按键")
                    if hasattr(self.svc.event_core, "reset_cancel_flag"):
                        self.svc.event_core.reset_cancel_flag()

                    # 触发回调
                    if self.push_callbacks["on_esc"] and self.state in [
                        RecordingState.RECORDING,
                        RecordingState.PAUSED,
                    ]:
                        self.state = RecordingState.PAUSED
                        # 对于RecordingState.RECORDING只需要直接调用_stop_continuous_drawing即可，但是增加了hover_start，可能按下esc的时候draw线程已经关闭了，那只需要关一下highlight_client即可
                        if self.is_hover_paused:
                            self.highlight_client.hide_wnd()
                        if not self.stop_drawing:
                            self._stop_continuous_drawing()
                        await self.push_callbacks["on_esc"](self.ws_connection)

                # 鼠标悬停检测
                if self.state == RecordingState.RECORDING:
                    await self._check_mouse_hover()

                await asyncio.sleep(0.05)  # 50ms检查一次

        except asyncio.CancelledError:
            logger.info("事件监控被取消")
        except Exception as e:
            logger.error(f"事件监控出错: {e}")
        finally:
            logger.info("事件监控结束")

    def _get_current_element_rect(self) -> str:
        """获取当前鼠标位置的元素矩形信息"""
        try:
            import win32api

            x, y = win32api.GetCursorPos()
            if not hasattr(self, "cur_rect") or self.cur_rect is None:
                raise ValueError("cur_rect 未初始化")
            # 判断鼠标是否在矩形范围内
            if not (self.cur_rect.left <= x <= self.cur_rect.right and self.cur_rect.top <= y <= self.cur_rect.bottom):
                raise ValueError("鼠标点位不在当前元素范围内")
            final_record_rect = {
                "left": self.cur_rect.left,
                "top": self.cur_rect.top,
                "right": self.cur_rect.right,
                "bottom": self.cur_rect.bottom,
                "mouse_x": x,
                "mouse_y": y,
                "domain": self.cur_domain,
            }

            return json.dumps(final_record_rect, ensure_ascii=False)

        except Exception as e:
            logger.error(f"获取元素矩形信息失败: {e}")
            return "{}"

    def _is_rect_changed(self, current_rect, last_rect):
        """安全地比较两个矩形是否不同，处理None的情况"""
        # 如果其中一个为None，另一个不为None，则认为发生了变化
        if (current_rect is None) != (last_rect is None):
            return True
        # 如果都为None，则没有变化
        if current_rect is None and last_rect is None:
            return False
        # 如果都不为None，则使用正常的比较
        return current_rect != last_rect

    async def _check_mouse_hover(self):
        """检测鼠标悬停 - 只要在rect中就持续计时"""
        try:
            import win32api

            current_pos = win32api.GetCursorPos()
            current_time = time.time()

            # 检查当前矩形区域是否发生变化
            current_rect = self.cur_rect
            if self._is_rect_changed(current_rect, self.last_hover_rect):
                # 矩形变化时重置悬停状态
                if self.hover_start_time is not None:
                    logger.debug(
                        f"检测到元素矩形变化，重置悬停状态。旧矩形: {self.last_hover_rect}, 新矩形: {current_rect}"
                    )
                self.last_hover_rect = current_rect
                self.hover_start_time = None
                self.hover_triggered = False

            # 检查鼠标是否在draw区域内
            is_in_draw_area = (
                current_rect
                and current_rect.left <= current_pos[0] <= current_rect.right
                and current_rect.top <= current_pos[1] <= current_rect.bottom
            )
            rect_data = None
            if is_in_draw_area:
                # 鼠标在区域内
                if self.hover_start_time is None:
                    # 首次进入区域，开始计时
                    self.hover_start_time = current_time
                    self.hover_triggered = False
                    logger.debug("鼠标进入draw区域，开始悬停计时")
                elif not self.hover_triggered:
                    # 持续在区域内，检查悬停时间
                    hover_duration = current_time - self.hover_start_time
                    if hover_duration >= self.hover_threshold:
                        logger.info(f"检测到鼠标悬停{hover_duration:.1f}秒，触发automic_start信号")
                        self.hover_triggered = True
                        rect_data = self._get_current_element_rect()

                        # 触发回调  注意黑名单悬停多少秒都不该发送数据
                        if self.push_callbacks["on_hover"] and (
                            not self.enable_record_blacklist or self.cur_app not in RECORDING_BLACKLIST
                        ):
                            await self.push_callbacks["on_hover"](self.ws_connection, rect_data)
                        self.last_element = self.svc.picker_core.element(self.svc, {"pick_type": PickerType.ELEMENT})
            else:
                # 鼠标离开区域，重置所有状态
                if self.hover_start_time is not None:
                    logger.debug("鼠标离开draw区域，重置悬停状态")
                if self.hover_triggered and (
                    not self.enable_record_blacklist or self.cur_app not in RECORDING_BLACKLIST
                ):  # 还要判断当前的应用是不是iflyrpa是的话就不要通知
                    await self.push_callbacks["on_mouse_out"](self.ws_connection)
                    logger.debug(f"鼠标悬停后离开draw区域，通知前端收敛红框 当前红框是{self.cur_app}")
                self.hover_start_time = None
                self.hover_triggered = False

        except Exception as e:
            import traceback

            logger.error("堆栈信息:\n{}".format(traceback.format_exc()))
            logger.error(f"悬停检测出错: {e} {traceback.extract_stack()}")

    def get_state(self) -> RecordingState:
        """获取当前状态"""
        return self.state

    def is_recording(self) -> bool:
        """是否正在录制"""
        return self.state == RecordingState.RECORDING

    def is_listening(self) -> bool:
        """是否在监听状态"""
        return self.state == RecordingState.LISTENING


# 全局单例
record_manager = RecordManager()
