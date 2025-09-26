import heapq
import json
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from websocket import WebSocketApp

from rpawebsocketclient.ws import (
    AckMsg,
    BaseMsg,
    ExitMsg,
    PingMsg,
    PongMsg,
    Route,
    Watch,
    WatchRetry,
    WatchTimeout,
    WsException,
    default_log,
)


class WsApp:
    def __init__(
        self,
        url: str,
        ping_interval=30,
        reconnect_interval=10,
        reconnect_max_time=20,
        log: Callable[..., Any] = default_log,
    ):
        # url配置
        self.url = url
        self.log = log

        # 状态
        self.ws_app = None
        self.running = False

        # ping机制
        self.ping_event = None
        self.ping_interval = ping_interval

        # 路由管理
        self.routes: dict[str, Route] = {}

        # 重启机制
        self.reconnect_time = 0
        self.reconnect_interval = reconnect_interval
        self.reconnect_max_time = reconnect_max_time

        # 消息监听
        self.watch_msg_event = None
        self.watch_interval = 1
        self.watch_msg: dict[str, Watch] = {}
        self.watch_msg_queue: list = []

        # 任务
        self.start_ping_task = None
        self.clear_watch_task = None
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

    def _send_text(self, msg: BaseMsg):
        """
        _send_text 发送text文本
        """
        if self.ws_app:
            self.log(">>>{}".format(msg.tojson()))
            self.ws_app.send(msg.tojson())

    def _call_route(self, channel: str, key: str, *args, **kwargs):
        """
        _call_route 路由调用
        """
        temp_channel = "{}$${}".format(channel, key)
        no_key_temp_channel = "{}$${}".format(channel, "")
        if temp_channel in self.routes or no_key_temp_channel in self.routes:
            func = self.routes[temp_channel].func
            return func(*args, **kwargs)
        else:
            raise WsException("func is not exist: {}".format((channel, key)))

    @staticmethod
    def _call_wait(watch: Watch, *args, **kwargs):
        if watch.callback:
            watch.callback(*args, **kwargs)

    def event(self, channel: str, key: str = "", func: Callable[[BaseMsg, Any], Any] = None):
        """
        _add_route 路由添加
        """
        temp_channel = "{}$${}".format(channel, key)
        self.routes[temp_channel] = Route(channel=channel, key=key, func=func)

    def _add_watch(self, watch: Watch):
        """
        _add_watch 添加监听
        """
        name = "{}$${}".format(watch.watch_type, watch.watch_key)
        self.watch_msg[name] = watch
        heapq.heappush(self.watch_msg_queue, (watch.timeout, name))

    def _clear_watch(self):
        """
        clear_watch 清理过期watch
        """

        def inner_clear_watch():
            while not self.watch_msg_event.wait(self.watch_interval) and self.running:
                while self.watch_msg_queue:
                    now = datetime.now()
                    if self.watch_msg_queue[0][0] > now:
                        break

                    try:
                        _, name = heapq.heappop(self.watch_msg_queue)

                        if name in self.watch_msg:
                            watch = self.watch_msg[name]
                            watch.retry()
                            if watch.time > watch.retry_time:
                                self._call_wait(watch, None, WatchTimeout("watch timeout"))
                                del self.watch_msg[name]
                            else:
                                self._call_wait(watch, None, WatchRetry("retry"))
                                heapq.heappush(self.watch_msg_queue, (watch.timeout, name))
                    except Exception as e:
                        self.log("error clear_watch: {}".format(e))

        self.watch_msg_event = threading.Event()
        self.clear_watch_task = threading.Thread(target=inner_clear_watch, daemon=True)
        self.clear_watch_task.start()

    def _close_watch(self):
        if self.watch_msg_event:
            self.watch_msg_event.set()
        if self.clear_watch_task and self.clear_watch_task.is_alive():
            self.clear_watch_task.join(3)
        self.clear_watch_task = None
        self.watch_msg_event = None
        self.watch_msg_queue = []
        self.watch_msg = {}

    def _start_ping(self):
        """
        _start_ping 开启ping服务
        """

        def _send_ping():
            while not self.ping_event.wait(self.ping_interval) and self.running:
                try:
                    self._send_text(PingMsg)
                except Exception as e:
                    self.log("error send_ping: {}".format(e))

        self.ping_event = threading.Event()
        self.start_ping_task = threading.Thread(target=_send_ping, daemon=True)
        self.start_ping_task.start()

    def _close_ping(self):
        if self.ping_event:
            self.ping_event.set()
        if self.start_ping_task and self.start_ping_task.is_alive():
            self.start_ping_task.join(3)
        self.start_ping_task = None
        self.ping_event = None

    def send(self, msg: BaseMsg):
        """
        send 发送消息，支持ack确认机制
        """

        def _send():
            self._send_text(msg)

        _send()

    def send_reply(self, msg: BaseMsg, timeout, callback_func=None):
        msg.need_reply = True

        def callback(watch_msg: BaseMsg = None, e: Exception = None):
            nonlocal callback_func
            if isinstance(e, WatchTimeout):
                # 已经退出
                return callback_func(None, e)
            elif isinstance(e, WatchRetry):
                # 重试
                return
            elif watch_msg:
                # 已经触发成功
                return callback_func(watch_msg, None)

        self._add_watch(
            Watch(
                watch_type="reply",
                watch_key=msg.event_id,
                callback=callback,
            ).init(timeout)
        )

        self.send(msg)

    def _on_message(self, ws, message):
        self.log("<<<{}".format(message))

        def inner_on_message():
            # 拦截特殊消息
            if msg.channel == PongMsg.channel:
                return
            elif msg.channel == AckMsg.channel:
                name = "{}$${}".format("ack", msg.event_id)
                if name in self.watch_msg:
                    watch = self.watch_msg[name]
                    self._call_wait(watch, msg, None)
                    del self.watch_msg[name]
                return
            elif msg.channel == ExitMsg.channel:
                return

            # 拦截reply消息
            if msg.reply_event_id:
                name = "{}$${}".format("reply", msg.reply_event_id)
                if name in self.watch_msg:
                    watch = self.watch_msg[name]
                    self._call_wait(watch, msg, None)
                    del self.watch_msg[name]
                return

            # 分发消息
            res_msg = msg.to_reply()
            try:
                res = self._call_route(msg.channel, msg.key, msg)
                try:
                    res = json.loads(res.body.decode("utf-8"))
                except Exception:
                    pass
                res_msg.data = res
            except Exception as e:
                res_msg.data = str(e)

            # 消息返回
            try:
                if res_msg.data is not None:
                    self.send(res_msg)
            except Exception as e:
                self.log("error _call_route: {}".format(e))

        # 处理消息
        try:
            data = json.loads(message)
            msg = BaseMsg(**data)
        except Exception as e:
            self.log("error json.loads: {}".format(e))

        # 处理
        self.thread_pool.submit(inner_on_message)

    def _on_open(self, ws):
        self.running = True
        self._start_ping()
        self._clear_watch()
        try:
            self._call_route("open", "", None)
        except Exception as e:
            self.log("error: _on_open _call_route {}".format(e))

    def _on_close(self, ws, arg1, arg2):
        self.running = False
        self._close_ping()
        self._close_watch()
        self.ws_app = None
        try:
            self._call_route("close", "", None)
        except Exception as e:
            self.log("error: _on_close _call_route {}".format(e))
        self._reconnect()

    def _on_error(self, ws, error):
        try:
            self._call_route("error", "", None)
        except Exception as e:
            self.log("error: _on_error _call_route {}".format(e))
        self.log("error _on_error: {}".format(error))

    def _reconnect(self):
        """
        _reconnect 重新连接
        """
        time.sleep(self.reconnect_interval)
        if self.reconnect_max_time < 0:
            self.log("_reconnect star: {}".format(self.reconnect_time))
            self.start()
            self.log("_reconnect end: {}".format(self.reconnect_time))
        elif self.reconnect_time < self.reconnect_max_time:
            self.reconnect_time += 1
            self.log("_reconnect star: {}".format(self.reconnect_time))
            self.start()
            self.log("_reconnect end: {}".format(self.reconnect_time))

    def start(self):
        """
        start 开启websocket连接
        """
        self.ws_app = WebSocketApp(
            self.url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )
        self.ws_app.run_forever(reconnect=None)
