import subprocess
from typing import Any

from rpaatomic.types import WinPick

from rpawindow import ControlInfo, WindowSizeType
from rpawindow.core import IWindowsCore


class WindowsCore(IWindowsCore):
    @staticmethod
    def info(handler: Any) -> ControlInfo:
        assert isinstance(handler, int)
        win_id = handler

        output = subprocess.check_output(["xdotool", "getwindowname", str(win_id)])
        name = output.decode("utf-8")

        geom = {}
        output = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", str(win_id)], shell=True)
        for line in output.splitlines():
            key, value = line.decode("utf-8").split("=")
            geom[key] = int(value)

        return ControlInfo(
            name=name,
            classname="",  # xprop -id xxx | awk -F '"' '/WM_CLASS/ {print $2}'
            position=(geom["X"], geom["Y"], geom["WIDTH"], geom["HEIGHT"]),
            handler=handler,
        )

    @staticmethod
    def find(pick: WinPick) -> Any:
        name = pick.get("name")
        output = subprocess.check_output(["xdotool", "search", "--name", name])
        window_id = ""
        for line in output.splitlines():
            window_id = line.decode("utf-8")
            # 使用最后一个
        if window_id:
            return int(window_id)
        return None

    @staticmethod
    def top(handler: Any):
        assert isinstance(handler, int)
        win_id = handler
        subprocess.check_output(["xdotool", "windowraise", str(win_id)])

    @staticmethod
    def close(handler: Any):
        assert isinstance(handler, int)
        win_id = handler
        subprocess.check_output(["xdotool", "windowclose", str(win_id)])

    @staticmethod
    def size(
        handler: Any,
        size_type: WindowSizeType = WindowSizeType.MAX,
        width: int = 0,
        height: int = 0,
    ):
        assert isinstance(handler, int)
        win_id = handler

        if size_type == WindowSizeType.CUSTOM:
            subprocess.check_output(["xdotool", "windowsize", str(win_id), str(width), str(height)])
        elif size_type == WindowSizeType.MAX:
            subprocess.check_output(["xdotool", "windowsize", str(win_id), "100%", "100%"])
        elif size_type == WindowSizeType.MIN:
            subprocess.check_output(["xdotool", "windowminimize", str(win_id)])

    @staticmethod
    def toControl(handler: Any) -> Any:
        raise NotImplementedError
