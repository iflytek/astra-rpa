import subprocess

from cv_picker.core.core import IPickCore, IRectHandler
from pynput.mouse import Controller


class RectHandler(IRectHandler):
    @staticmethod
    def get_foreground_window_rect():
        try:
            # 获取当前活动窗口的 ID
            window_id = subprocess.check_output(["xdotool", "getactivewindow"]).strip()

            # 获取窗口的标题
            window_name = subprocess.check_output(["xdotool", "getwindowname", window_id]).strip().decode("utf-8")

            # 获取窗口的几何信息
            window_geometry = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", window_id]).decode(
                "utf-8"
            )
            geometry = {}
            for line in window_geometry.splitlines():
                key, value = line.split("=")
                geometry[key] = int(value)

            rect = (geometry["X"], geometry["Y"], geometry["WIDTH"], geometry["HEIGHT"])

            return window_id.decode("utf-8"), window_name, rect
        except subprocess.CalledProcessError:
            return None, None, None


class PickCore(IPickCore):
    mouse = Controller()

    @staticmethod
    def get_mouse_position():
        position = PickCore.mouse.position
        return position
