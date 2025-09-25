import os
import platform
import sys

from ... import ComponentType
from ...utils.subprocess import SubPopen


class Picker:
    def __init__(self, svc):
        self.svc = svc
        self.highlighter = None  # 画框
        self.cv_picker = None  # cv 识别
        self.app_picker = None  # 拾取
        # self.app_picker_core = None  # 拾取
        self.start = False

    def set_start(self, start):
        self.start = start

    def init(self):
        python_executable = self.svc.config.app_server.python_core

        # 1. 服务声明
        if sys.platform == "win32" and platform.release() != "7":
            highlighter_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "win",
                "RPAHighlighter",
                "ConsoleApp1.exe",
            )
            self.highlighter = SubPopen(name="highlighter", cmd=[highlighter_path])
            self.cv_picker = SubPopen(
                name="cv_picker",
                cmd=[python_executable, "-m", "engine.core.servers.cv_picker"],
            )
            self.app_picker = SubPopen(
                name="picker",
                cmd=[python_executable, "-m", "engine.core.servers.picker"],
            )
        elif sys.platform == "win32" and platform.release() == "7":
            highlighter_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "win",
                "RPAHighlighter",
                "cv_match_application_4.0.py",
            )
            self.highlighter = SubPopen(
                name="highlighter",
                cmd=[
                    python_executable,
                    highlighter_path,
                    "{}".format(self.svc.hl_port),
                ],
            )
            self.cv_picker = SubPopen(name="cv_picker", cmd=[python_executable, "-m", "cv_picker"])
            self.app_picker = SubPopen(name="picker", cmd=[python_executable, "-m", "picker"])
        else:
            highlighter_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "linux",
                "RPAHighlighter",
                "cv_match_application_4.0.py",
            )
            self.highlighter = SubPopen(
                name="highlighter",
                cmd=[
                    python_executable,
                    highlighter_path,
                    "{}".format(self.svc.hl_port),
                ],
            )
            self.cv_picker = SubPopen(name="cv_picker", cmd=[python_executable, "-m", "cv_picker"])
            self.app_picker = SubPopen(name="picker", cmd=[python_executable, "-m", "picker_linux"])

        # 2. 服务配置
        self.app_picker.set_param("port", self.svc.get_validate_port(ComponentType.PICKER))
        self.app_picker.set_param("route_port", self.svc.route_port)
        self.app_picker.set_param("highlight_socket_port", self.svc.hl_port)

        self.cv_picker.set_param("schema", "cv_picker")
        self.cv_picker.set_param("cv_picker_port", self.svc.get_validate_port(ComponentType.CV_PICKER))
        self.cv_picker.set_param("remote_addr", self.svc.config.app_server.remote_addr)
        self.cv_picker.set_param("highlight_socket_port", self.svc.hl_port)
