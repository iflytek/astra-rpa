"""
RPA定位器模块 - 提供各种UI元素定位功能

本模块包含了用于RPA自动化的各种定位器类和工具函数，
支持UIA、Web、MSAA等多种技术栈的元素定位。
"""

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from locator.utils.move import smooth_move


class Point:
    """表示二维坐标点的类"""

    def __init__(self, x_coordinate, y_coordinate):
        """初始化点坐标

        Args:
            x_coordinate: X坐标值
            y_coordinate: Y坐标值
        """
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    @property
    def x(self):
        """X坐标属性"""
        return self.x_coordinate

    @property
    def y(self):
        """Y坐标属性"""
        return self.y_coordinate


ZERO_POINT = Point(0, 0)


class Rect:
    """表示矩形区域的类"""

    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)
        self.__area = 0

    def width(self) -> int:
        """计算矩形宽度"""
        return self.right - self.left

    def height(self) -> int:
        """计算矩形高度"""
        return self.bottom - self.top

    def area(self) -> int:
        """计算矩形面积"""
        if not self.__area:
            self.__area = self.width() * self.height()
        self.__area = max(self.__area, 0)
        return self.__area

    @staticmethod
    def calculate_area(left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        """计算指定坐标的矩形面积"""
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
    def check_point_contains(left, top, right, bottom, point: Point):
        """检查点是否在指定矩形区域内"""
        return left <= point.x < right and top <= point.y < bottom

    def contains_rect(self, rect: Any) -> bool:
        """
        是否包含rect
        """
        return self.left < rect.left and self.top < rect.top and self.right >= rect.right and self.bottom >= rect.bottom

    def overlaps(self, other: Any) -> bool:
        """
        是否与other重叠
        """
        return not (
            self.right <= other.left or self.left >= other.right or self.bottom <= other.top or self.top >= other.bottom
        )

    def to_json(self):
        """将矩形信息转换为JSON字符串"""
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


EMPTY_RECT = Rect(0, 0, 0, 0)


class PickerDomain(Enum):
    """拾取器类型"""

    UIA = "uia"
    WEB = "web"
    WEB_IE = "web_ie"  # 拾取的时候 web的type是web, 而不是web_ie
    JAB = "jab"
    SAP = "SAP"
    MSAA = "msaa"
    AUTO = "auto"  # 拾取的时候 无他


class PickerType(Enum):
    """拾取类型"""

    ELEMENT = "ELEMENT"  # 元素拾取
    WINDOW = "WINDOW"  # 窗口拾取
    POINT = "POINT"  # 鼠标位置拾取
    SIMILAR = "SIMILAR"  # 相识元素
    BATCH = "BATCH"  # 抓取


PICKER_TYPE_DICT = {p.value: True for p in PickerType}


class ILocator(ABC):
    """定位器接口类"""

    @abstractmethod
    def rect(self) -> Optional[Rect]:
        """获取位置"""

    @abstractmethod
    def control(self) -> Any:
        """获取句柄封装类"""

    def point(self) -> Point:
        """公共方法"""
        rect = self.rect()
        center_x = rect.left + rect.width() // 2
        center_y = rect.top + rect.height() // 2
        return Point(center_x, center_y)

    def move(self, point: Point = None, duration=0.4):
        """公共方法"""
        if point is None:
            point = self.point()
        center_x = point.x
        center_y = point.y
        smooth_move(center_x, center_y, duration=duration)

    def hover(self, point: Point = None):
        """公共方法"""
        return self.move(point)


class BrowserType(Enum):
    """浏览器类型枚举"""

    CHROME = "chrome"
    EDGE = "edge"
    INTERNET_EXPLORER = "iexplore"
    CHROME_360_SE = "360se"
    CHROME_360_X = "360ChromeX"
    FIREFOX = "firefox"
    CHROMIUM = "chromium"


LIKE_CHROME_BROWSER_TYPES = [
    BrowserType.CHROME.value,
    BrowserType.EDGE.value,
    BrowserType.CHROME_360_SE.value,
    BrowserType.CHROME_360_X.value,
    BrowserType.FIREFOX.value,
    BrowserType.CHROMIUM.value,
]

WEB_CLASS_NAMES = {
    BrowserType.CHROME.value: ["Chrome_RenderWidgetHostHWND"],
    BrowserType.EDGE.value: ["Chrome_RenderWidgetHostHWND"],
    BrowserType.CHROME_360_SE.value: ["Chrome_RenderWidgetHostHWND"],
    BrowserType.CHROME_360_X.value: ["Chrome_RenderWidgetHostHWND"],
    BrowserType.FIREFOX.value: ["Chrome_RenderWidgetHostHWND"],
    BrowserType.INTERNET_EXPLORER.value: ["Internet Explorer_Server"],
    BrowserType.CHROMIUM.value: ["Chrome_RenderWidgetHostHWND"],
}
