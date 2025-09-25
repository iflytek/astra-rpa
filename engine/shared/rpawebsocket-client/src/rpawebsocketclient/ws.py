import copy
import json
import logging
import time
import uuid as uid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Union


class IWebSocket(ABC):
    @abstractmethod
    async def receive_text(self) -> str:
        pass

    @abstractmethod
    async def send(self, message: Any) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


def gen_event_id():
    """
    生成uuid
    """

    return "{}".format(str(uid.uuid4()))


def default_error_format(e: Exception = None) -> Union[None, dict]:
    """
    default_error_format 默认错误格式化
    """
    return None


def default_log(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)


@dataclass
class Conn:
    """
    Conn 连接管理器
    """

    # 核心
    ws: IWebSocket = None
    # 同msg的uuid
    uuid: str = ""
    # 最后一次ping的时间
    last_ping: int = 0

    async def send_text(self, data: str) -> None:
        await self.ws.send(data)


@dataclass
class BaseMsg:
    """
    BaseMsg 基础消息
    """

    # 回复事件id 已http的形式使用 适合一来一回的消息
    reply_event_id: str = None
    # 事件id 唯一值
    event_id: str = None
    # 事件发生的时间戳
    event_time: int = None
    # 业务 大业务
    channel: str = None
    # 事件名称 大业务下面的小事件
    key: str = None
    # 用户名，客户标识，同一个客户多个连接，发送时会广播，主要时解决回收不及时问题
    uuid: str = None
    # 消息发送给
    send_uuid: str = None
    # 是否需要ack[无效]
    need_ack: bool = None
    # 是否需要回复
    need_reply: bool = None
    # 数据
    data: dict = None

    def to_reply(self):
        res_msg = copy.deepcopy(self)
        res_msg.reply_event_id = self.event_id
        res_msg.uuid = self.send_uuid
        res_msg.send_uuid = self.uuid
        res_msg.data = None
        res_msg.init()
        return res_msg

    def init(self):
        self.event_id = gen_event_id()
        self.event_time = int(time.time())
        return self

    def tojson(self, filtered_none: bool = True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data, ensure_ascii=True)


@dataclass
class Route:
    """
    Route 映射的路由
    """

    # 同msg的channel
    channel: str = ""
    # 同msg的key
    key: str = ""
    # 回调
    func: Callable[[BaseMsg, Any], Any] = None


@dataclass
class Watch:
    # 监听类型
    watch_type: str = ""
    # 监听key
    watch_key: str = ""
    # 触发callback
    callback: Callable[[Union[BaseMsg, None], Union[Exception, None]], Any] = None

    # 额外重试次数
    retry_time: int = 0
    # 间隔
    interval: int = 10

    # 过期时间
    timeout: datetime = None
    # 重试次数
    time: int = 0

    def init(self, interval: int = 10):
        self.interval = interval
        self.timeout = datetime.now() + timedelta(seconds=interval)
        return self

    def retry(self):
        self.time += 1
        self.timeout += timedelta(seconds=self.interval)


class WsException(Exception):
    """
    WsException ws基础异常
    """

    pass


class WatchRetry(WsException):
    """
    WatchTimeout watch重试
    """

    pass


class WatchTimeout(WsException):
    """
    WatchTimeout watch超时
    """

    pass


class WsError(WsException):
    """
    WsError ws基础错误, 会关闭连接
    """

    pass


class PingTimeoutError(WsError):
    """
    PingTimeoutException ping超时
    """

    pass


class MsgUnlawfulnessError(WsError):
    """
    MsgUnlawfulnessError 消息不合法
    """

    pass


PingMsg = BaseMsg(channel="ping")
PongMsg = BaseMsg(channel="pong")
ExitMsg = BaseMsg(channel="exit")
AckMsg = BaseMsg(channel="ack")


def gen_ack_msg(event_id: str = ""):
    """
    gen_ack_msg 快速生成ack消息
    """
    return BaseMsg(channel=AckMsg.channel, event_id=event_id)


def gen_exit_msg(data: dict = None):
    """
    gen_exit_msg 快速生成exit退出消息
    """
    return BaseMsg(channel=ExitMsg.channel, data=data)
