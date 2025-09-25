import time

from ... import ServerLevel
from ...logger import logger
from ..environment.package import Package
from ..environment.venv import VenvManager
from ..server import IServer
from ..terminal.terminal import Terminal


class RpaSchedulerAsyncServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="scheduler_async",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        i = 1
        while True:
            try:
                # 创建空的虚拟环境
                try:
                    VenvManager().create_new(self.svc)
                except Exception as e:
                    logger.exception("VenvManager error: {}".format(e))

                # 定时注册服务
                try:
                    if i % 30 == 0:
                        self.svc.register_server()
                except Exception as e:
                    logger.exception("register_server error: {}".format(e))
            except Exception as e:
                pass
            finally:
                i += 1
                if i > 60:
                    i = 0
                time.sleep(1)


class TerminalAsyncServer(IServer):
    def __init__(self, svc):
        super().__init__(svc=svc, name="terminal_async", level=ServerLevel.NORMAL, run_is_async=True)

    def run(self):
        i = 1
        while True:
            try:
                if i % 10 == 0:
                    # 创建空的虚拟环境
                    res = Terminal.upload(self.svc)
                    if res == "TERMINAL_NOT_FOUND":
                        # 未注册，先去注册
                        Terminal.register(self.svc)
            except Exception as e:
                logger.exception("Terminal upload error: {}".format(e))
            finally:
                i += 1
                if i > 60:
                    i = 0
                time.sleep(1)


class AtomicUploadAsyncServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="atomic_upload_async",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        i = 1
        while True:
            try:
                # 原子能力更新
                if i % 60 == 0:
                    Package().atomic_upload(self.svc)
            except Exception as e:
                logger.exception("update_atomic error: {}".format(e))
            finally:
                i += 1
                if i > 60:
                    i = 0
                time.sleep(1)


class CheckPickProcessAliveServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="check_pick_process_alive",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        while True:
            try:
                if self.svc.picker.start:
                    if self.svc.picker.cv_picker:
                        if not self.svc.picker.cv_picker.is_alive():
                            self.svc.picker.cv_picker.run()
                    if self.svc.picker.app_picker:
                        if not self.svc.picker.app_picker.is_alive():
                            self.svc.picker.app_picker.run()
                    if self.svc.picker.highlighter:
                        if not self.svc.picker.highlighter.is_alive():
                            self.svc.picker.highlighter.run()
            except Exception as e:
                logger.exception("check_pick_process error: {}".format(e))
            finally:
                time.sleep(1)
