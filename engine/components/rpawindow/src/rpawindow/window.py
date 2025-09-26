import platform
import sys
import time

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import WinPick

from rpawindow.core import IWindowsCore, WindowExistType, WindowSizeType
from rpawindow.error import *

if sys.platform == "win32":
    from rpawindow.core_win import WindowsCore
elif platform.system() == "Linux":
    from rpawindow.core_unix import WindowsCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

WindowsCore: IWindowsCore = WindowsCore()


class Window:
    @staticmethod
    @atomicMg.atomic(
        "Window",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "WINDOW"}),
            ),
            atomicMg.param(
                "check_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
        ],
    )
    def exist(
        pick: WinPick,
        check_type: WindowExistType = WindowExistType.EXIST,
        wait_time: float = 0,
    ) -> bool:
        """
        exist 窗口是否存在/不存在
        """
        wait_time = max(0, wait_time)
        while wait_time >= 0:
            try:
                window_found = WindowsCore.find(pick) is not None
                if window_found and check_type == WindowExistType.EXIST:
                    return True
            except Exception:
                if check_type == WindowExistType.NOT_EXIST:
                    return True
            wait_time -= 0.5
            time.sleep(0.5)
        return False

    @staticmethod
    @atomicMg.atomic(
        "Window",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "WINDOW"}),
            ),
        ],
    )
    def top(pick: WinPick):
        """
        top 置顶
        """
        handler = WindowsCore.find(pick)
        return WindowsCore.top(handler)

    @staticmethod
    @atomicMg.atomic(
        "Window",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "WINDOW"}),
            ),
        ],
    )
    def close(pick: WinPick):
        """
        close 关闭窗口
        """
        handler = WindowsCore.find(pick)
        return WindowsCore.close(handler)

    @staticmethod
    @atomicMg.atomic(
        "Window",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "WINDOW"}),
            ),
            atomicMg.param(
                "width",
                dynamics=[
                    DynamicsItem(
                        key="$this.width.show",
                        expression="return $this.size_type.value == '{}'".format(WindowSizeType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "height",
                dynamics=[
                    DynamicsItem(
                        key="$this.height.show",
                        expression="return $this.size_type.value == '{}'".format(WindowSizeType.CUSTOM.value),
                    )
                ],
            ),
        ],
    )
    def set_size(
        pick: WinPick,
        size_type: WindowSizeType = WindowSizeType.MAX,
        width: int = 0,
        height: int = 0,
    ):
        """
        set_size 设置尺寸
        """
        if size_type == WindowSizeType.CUSTOM:
            if width <= 0 or height <= 0:
                raise BaseException(
                    PARAMETER_INVALID_FORMAT.format((width, height)),
                    "参数异常 {}".format((width, height)),
                )
        handler = WindowsCore.find(pick)
        return WindowsCore.size(handler, size_type, width, height)
