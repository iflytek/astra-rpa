from enum import Enum

from pydantic import BaseModel


class PickerSign(Enum):
    """
    定义用户拾取传入的消息类型
    """

    START = "START"
    # WIN_PICKER_START = "WIN_PICKER_START"   # 启动窗口拾取
    STOP = "STOP"
    VALIDATE = "VALIDATE"
    DESIGNATE = "DESIGNATE"


class PickerType(Enum):
    ELEMENT = "ELEMENT"  # 元素拾取
    WINDOW = "WINDOW"  # 窗口拾取
    POINT = "POINT"  # 鼠标位置拾取
    SIMILAR = "SIMILAR"
    OTHERS = "OTHERS"
    CV = "CV"


class PickerInputData(BaseModel):
    """
    定义用户拾取输入的参数结构
    """

    pick_sign: PickerSign = PickerSign.START
    pick_type: PickerType = PickerType.ELEMENT
    data: str = None
    ext_data: dict = {}


class PickerResponseItem(Enum):
    """
    定义拾取返回的结果类型
    """

    PING = "ping"
    SUCCESS = "success"
    ERROR = "error"
    CANCEL = "cancel"


class PickerResponse(BaseModel):
    """
    定义拾取响应
    """

    err_msg: str
    data: str
    key: PickerResponseItem = PickerResponseItem.SUCCESS
