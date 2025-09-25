import os
import time

from loguru import logger as log


class Logger:
    """日志"""

    def __init__(self):
        self.logger = log

    def init(self, name: str = ""):
        if not name:
            return
        self.logger.remove()
        log_path = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        # 按时间轮转的日志文件
        log_path = os.path.abspath(os.path.join(log_path, "{}-{}.log".format(name, time.strftime("%Y-%m-%d"))))
        self.logger.add(
            log_path,
            rotation="50MB",
            retention="7 days",
            encoding="utf-8",
            enqueue=True,
            compression="zip",
        )

    def get_log(self):
        return self.logger


base_logger = Logger()
base_logger.init()
logger = base_logger.get_log()
