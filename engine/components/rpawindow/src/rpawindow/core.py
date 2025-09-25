from abc import ABC, abstractmethod
from typing import Any

from rpaatomic.types import WinPick
from rpawindow import ControlInfo, WindowExistType, WindowSizeType


class IWindowsCore(ABC):
    @staticmethod
    @abstractmethod
    def find(pick: WinPick) -> Any:
        pass

    @staticmethod
    @abstractmethod
    def top(handler: Any):
        pass

    @staticmethod
    @abstractmethod
    def info(handler: Any) -> ControlInfo:
        """窗口信息"""
        pass

    @staticmethod
    @abstractmethod
    def close(handler: Any):
        """关闭窗口"""
        pass

    @staticmethod
    @abstractmethod
    def size(
        handler: Any,
        size_type: WindowSizeType = WindowSizeType.MAX,
        width: int = 0,
        height: int = 0,
    ):
        """设置尺寸"""
        pass

    @staticmethod
    @abstractmethod
    def toControl(handler: Any) -> Any:
        """转换成Control"""
        pass


class IUITreeCore(ABC):
    @staticmethod
    @abstractmethod
    def GetRootControl() -> Any:
        """获取根Control"""
        pass

    @staticmethod
    @abstractmethod
    def WalkControl(control: Any, includeTop: bool = False, maxDepth: int = 0):
        """生成器，Control遍历"""
        pass

    @staticmethod
    @abstractmethod
    def toHandler(control) -> Any:
        """toHandler 转换成HWN"""
        pass

    @staticmethod
    @abstractmethod
    def setAction(control) -> bool:
        pass
