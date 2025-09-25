import time
from enum import Enum
from functools import wraps


class EventKey(Enum):
    Stop = "__Stop__"  # close kill

    Pause = "__Pause__"  # bool
    ResPause = "__ResPause__"  # bool

    Next = "__Next__"  # bool
    ResNext = "__ResNext__"  # bool

    Continue = "__Continue__"  # bool
    ResContinue = "__ResContinue__"  # bool

    PreNext = "__PreNext__"  # bool
    Break = "__Break__"  # 断点 静态 dict
    STACK = "__STACK__"  # 堆栈 静态 list
    LINE = "__LINE__"  # 执行行号 int


class EventStopReason(Enum):
    Close = "close"
    Kill = "kill"


class CloseError(Exception):
    pass


default_close_error = CloseError("close")
default_kill_error = CloseError("kill")


def default_event_handler(svc, func=None, *args, **war_kwargs):
    events = svc.events
    if events:
        # 关闭 事件
        if EventKey.Stop.value in events and events[EventKey.Stop.value]:
            reason = events[EventKey.Stop.value]
            if reason == EventStopReason.Close.value:
                raise default_close_error
            else:
                raise default_kill_error

        # 暂停\取消暂停 事件
        if EventKey.Pause.value in events and events[EventKey.Pause.value]:
            while events[EventKey.Pause.value]:
                events[EventKey.ResPause.value] = True
                time.sleep(0.3)

                # 关闭 事件
                if EventKey.Stop.value in events and events[EventKey.Stop.value]:
                    reason = events[EventKey.Stop.value]
                    if reason == EventStopReason.Close.value:
                        raise default_close_error
                    else:
                        raise default_kill_error
            events[EventKey.ResPause.value] = False
    if func:
        return func(*args, **war_kwargs)


def default_error_logger_handler(svc, env, token, func, *args, **war_kwargs):
    return func(*args, **war_kwargs)


def default_debug_handler(svc, env, token):
    pass


class Event:
    def __init__(
        self,
        raw_error_logger_handler=default_error_logger_handler,
        raw_event_handler=default_event_handler,
        raw_debug_handler=default_debug_handler,
    ):
        self.raw_event_handler = raw_event_handler
        self.raw_error_logger_handler = raw_error_logger_handler
        self.raw_debug_handler = raw_debug_handler

    def event_handler(self, svc):
        """处理事件，暂停，继续 关闭等外来事件"""

        def raw_event_handler(func):
            @wraps(func)
            def wrapper(*args, **war_kwargs):
                return self.raw_event_handler(svc, func, *args, **war_kwargs)

            return wrapper

        return raw_event_handler

    def error_logger_handler(self, svc, env, token):
        """处理错误日志，核心是eval的错误"""

        def raw_error_logger_handler(func):
            @wraps(func)
            def wrapper(*args, **war_kwargs):
                return self.raw_error_logger_handler(svc, env, token, func, *args, **war_kwargs)

            return wrapper

        return raw_error_logger_handler

    def debug_handler(self, svc, env, token):
        """处理debug模式执行埋点，包含atomic"""

        return self.raw_debug_handler(svc, env, token)


event = Event()
