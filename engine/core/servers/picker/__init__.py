import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class Point:
    """点"""

    def __init__(self, x, y):
        self.x = x
        self.y = y


ZERO_POINT = Point(0, 0)


class Rect:
    """位置信息"""

    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)
        self.__area = 0

    def width(self) -> int:
        return self.right - self.left

    def height(self) -> int:
        return self.bottom - self.top

    def area(self) -> int:
        if not self.__area:
            self.__area = self.width() * self.height()
        self.__area = max(self.__area, 0)
        return self.__area

    @staticmethod
    def calculate_area(left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        area = (right - left) * (bottom - top)
        if area < 0:
            return 0
        return area

    def contains(self, point: Point) -> bool:
        """
        是否包含point
        """
        return self.left <= point.x < self.right and self.top <= point.y < self.bottom

    @staticmethod
    def check_point_containment(left, top, right, bottom, point: Point):
        return left <= point.x < right and top <= point.y < bottom

    def contains_rect(self, rect: Any) -> bool:
        """
        是否包含rect
        """
        return self.left < rect.left and self.top < rect.top and self.right >= rect.right and self.bottom >= rect.bottom

    def to_json(self):
        return json.dumps(
            {
                "left": self.left,
                "top": self.top,
                "right": self.right,
                "bottom": self.bottom,
            }
        )

    def __eq__(self, rect):
        return (
            self.left == rect.left and self.top == rect.top and self.right == rect.right and self.bottom == rect.bottom
        )


@dataclass
class DrawResult:
    """统一的拾取绘制结果"""

    success: bool
    rect: Optional[Rect] = None
    app: Optional[str] = None
    error_message: Optional[str] = None
    domain: Optional[str] = None

    def to_dict(self):
        """转换为字典格式"""
        result = {"success": self.success}
        if self.rect:
            result["rect"] = self.rect
        if self.app:
            result["app"] = self.app
        if self.error_message:
            result["error_message"] = self.error_message
        if self.domain:
            result["domain"] = self.domain
        return result


class OperationResultStatus(Enum):
    """业务操作结果状态"""

    SUCCESS = "success"
    ERROR = "error"
    CANCEL = "cancel"


class OperationResult(BaseModel):
    """统一的操作结果模型"""

    status: OperationResultStatus
    data: Optional[Any] = None
    message: Optional[str] = None

    @classmethod
    def success(cls, data: Any = None, message: str = None):
        """创建成功响应"""
        return cls(status=OperationResultStatus.SUCCESS, data=data, message=message)

    @classmethod
    def error(cls, message: str, data: Any = None):
        """创建错误响应"""
        return cls(status=OperationResultStatus.ERROR, message=message, data=data)

    @classmethod
    def cancel(cls, message: str = "操作已取消"):
        """创建取消响应"""
        return cls(status=OperationResultStatus.CANCEL, message=message)

    def to_dict(self):
        """转换为字典格式，兼容现有的_send_response函数"""
        result = {}

        if self.status == OperationResultStatus.SUCCESS:
            result["success"] = True
            if self.data is not None:
                result["data"] = self.data
        elif self.status == OperationResultStatus.CANCEL:
            result["success"] = False
            result["cancel"] = True
        else:  # ERROR
            result["success"] = False
            result["error"] = self.message or "未知错误"

        return result


class PickerType(Enum):
    """拾取类型"""

    ELEMENT = "ELEMENT"  # 元素拾取
    WINDOW = "WINDOW"  # 窗口拾取
    POINT = "POINT"  # 鼠标位置拾取
    SIMILAR = "SIMILAR"  # 相识元素
    BATCH = "BATCH"  # 抓取


PICKER_TYPE_DICT = {p.value: True for p in PickerType}


class MKSign(Enum):
    """定义键鼠监听启动方"""

    PICKER = "PICKER"
    RECORD = "RECORD"  # 录制器专用


class PickerSign(Enum):
    """定义用户拾取传入的消息类型"""

    START = "START"
    STOP = "STOP"  # EXIT
    VALIDATE = "VALIDATE"
    DESIGNATE = "DESIGNATE"  # CV的作用
    GAIN = "GAIN"  # 获取拾取结果
    HIGHLIGHT = "HIGHLIGHT"  # 高亮,区别与校验

    RECORD = "RECORD"  # 录制器专用


class RecordAction(Enum):
    """录制动作 - 专门处理录制相关的子操作"""

    LISTENING = "RECORD_LISTENING"  # 开始监听
    START = "RECORD_START"  # 开始录制
    PAUSE = "RECORD_PAUSE"  # 暂停录制
    HOVER_START = "RECORD_AUTOMIC_HOVER_START"  # 开始选择原子能力
    HOVER_END = "RECORD_AUTOMIC_HOVER_END"  # 原子能力放弃选择
    AUTOMIC_END = "RECORD_AUTOMIC_END"  # 原子能力选择操作结束
    END = "RECORD_END"  # 结束录制


class PickerDomain(Enum):
    """拾取器类型"""

    UIA = "uia"
    WEB = "web"
    WEB_IE = "web_ie"  # 拾取的时候 web的type是web, 而不是web_ie
    JAB = "jab"
    SAP = "SAP"
    MSAA = "msaa"

    AUTO = "auto"  # 拾取的时候 无他


class IEventCore(ABC):
    """用户键盘鼠标事件"""

    @abstractmethod
    def is_cancel(self):
        """是否是退出"""

    @abstractmethod
    def is_focus(self):
        """是否是focus"""

    @abstractmethod
    def start(self) -> bool:
        """开启监听"""

    @abstractmethod
    def close(self):
        """关闭监听"""

    @abstractmethod
    def is_f4_pressed(self):
        """检查F4键是否按下"""

    @abstractmethod
    def reset_f4_flag(self):
        """重置F4键标志位"""

    @abstractmethod
    def reset_cancel_flag(self):
        """重置ESC键标志位"""


class IPickerCore(ABC):
    """拾取核心"""

    @abstractmethod
    def draw(self, svc, highlight_client, data: dict) -> DrawResult:
        """绘图"""

    @abstractmethod
    def element(self, svc, data: dict) -> dict:
        """获取元素"""


class IElement(ABC):
    @abstractmethod
    def rect(self) -> Rect:
        """尺寸"""

    @abstractmethod
    def tag(self) -> str:
        """显示的标签"""

    @abstractmethod
    def path(self, svc=None, strategy_svc=None) -> dict:
        """转换为path"""


class APP(Enum):
    """
    枚举常用的app
    """

    Chrome = "chrome"
    Edge = "edge"
    IE = "iexplore"
    Firefox = "firefox"
    Chrome360X = "360ChromeX"
    Chrome360se = "360se"
    Chrome360 = "360Chrome"
    SAP = "saplogon"
    Thunder = "Thunder"
    Unknown = "Unknown"
    Chromium = "chromium"

    @classmethod
    def init(cls, name: str):
        try:
            if name == "msedge":
                return APP.Edge
            return cls(name)
        except ValueError:
            return APP.Unknown


WEB_CLASS_NAMES = {
    APP.Chrome: ["Chrome_RenderWidgetHostHWND"],
    APP.Edge: ["Chrome_RenderWidgetHostHWND"],
    APP.Chrome360se: ["Chrome_RenderWidgetHostHWND"],
    APP.Chrome360X: ["Chrome_RenderWidgetHostHWND"],
    APP.Firefox: ["MozillaWindowClass"],
    APP.IE: ["Internet Explorer_Server"],
    APP.Chromium: ["Chrome_RenderWidgetHostHWND"],
}

CHROME_LIKE_BROWSER_TYPES = [
    APP.Chrome.value,
    APP.Edge.value,
    APP.Chrome360se.value,
    APP.Chrome360X.value,
    APP.Firefox.value,
    APP.Chromium.value,
]

MSAA_APPLICATIONS = [APP.Thunder.value]

RECORDING_BLACKLIST = ["iflyrpa"]  # 录制绘框黑名单
