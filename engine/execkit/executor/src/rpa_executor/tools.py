import sys
import threading

from rpa_executor.utils import exec_run
from rpa_recording.recording import RecordingTool
from rpatools.tools import RpaTools


class LogTool:
    def __init__(self):
        self.thread = None
        self.svc = None

    def init(self, svc):
        self.svc = svc
        return self

    def __tool__(self):
        if sys.platform == "win32":
            url = RpaTools.get_window_dir()
        else:
            url = RpaTools.get_window_dir()
        exec_run(
            [
                url,
                "--url=tauri://localhost/logwin.html?title={}&ws=ws://127.0.0.1:{}/?tag=tip".format(
                    self.svc.start_project_name, self.svc.port
                ),
                "--pos=right_bottom",
                "--width=288",
                "--height=102",
                "--top=true",
            ],
            True,
        )

    def start(self):
        self.thread = threading.Thread(target=self.__tool__, daemon=True)
        self.thread.start()


log_tool = LogTool()
recording_tool = RecordingTool()
