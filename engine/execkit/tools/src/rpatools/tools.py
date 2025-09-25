import os.path
import sys


class RpaTools:
    @staticmethod
    def get_window_dir() -> str:
        if sys.platform == "win32":
            return os.path.join(os.path.dirname(__file__), "iflyrpa_window", "iflyrpa-window.exe")
        else:
            return os.path.join(os.path.dirname(__file__), "iflyrpa_linux", "iflyrpa-window.exe")
