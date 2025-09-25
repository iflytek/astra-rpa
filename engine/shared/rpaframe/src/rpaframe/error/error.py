from dataclasses import dataclass
from enum import Enum


class BizCode(Enum):
    OK = "0000"
    ServerErr = "5001"
    LocalErr = "1001"


@dataclass
class ErrorCode:
    code: BizCode  # 业务code
    message: str
    httpcode: int = 200

    def format(self, *args, **kwargs):
        self.message = self.message.format(*args, **kwargs)
        return self


class BaseException(Exception):
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(self.code.message)
