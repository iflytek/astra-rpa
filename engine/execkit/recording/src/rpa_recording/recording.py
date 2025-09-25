import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

from rpaframe.logger.logger import logger

system_encoding = sys.getdefaultencoding()


def folder_empty(folder_path) -> bool:
    contents = os.listdir(folder_path)
    if len(contents) == 0:
        return True
    else:
        return False


class RecordingTool:
    def __init__(self):
        self.thread = None

        self.config = {
            "open": True,
            "cut_time": 30,  # 裁剪最后时间：0表示不裁剪
            "scene": "always",  # 运行场景:fail/always
            "file_path": "./logs/report",
            "file_clear_time": 7,  # 清理录制视频7天
        }
        self.start_time = 0
        self.end_time = 0
        self.local_raw_file = None
        self.local_file = None

        # 通信相关
        self.event = threading.Event()
        self.exec_success = False
        self.exec_res = None

    def init(self, project_id, exec_id, config=None):
        if config:
            self.config = config

        local_file_path = os.path.join(os.getcwd(), self.config.get("file_path"), project_id)
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)
        self.local_raw_file = os.path.join(local_file_path, "{}_raw.mp4".format(exec_id))
        self.local_file = os.path.join(local_file_path, "{}.mp4".format(exec_id))

        return self

    def __tool__(self):
        try:
            if not self.config.get("open"):
                return

            # 0. 获取ffmpeg位置
            self.start_time = int(time.time())
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if sys.platform == "win32":
                url = os.path.join(script_dir, "view", "win", "ffmpeg.exe")
                exec_args_1 = [
                    url,
                    "-thread_queue_size",
                    "16",
                    "-f",
                    "gdigrab",
                    "-rtbufsize",
                    "500M",
                    "-framerate",
                    "3",
                    "-i",
                    "desktop",
                    "-crf",
                    "23",
                    "-pix_fmt",
                    "yuv420p",
                    "-vf",
                    "scale=iw*75/100:ih*75/100,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    "{}".format(self.local_raw_file),
                    "-y",
                ]
            else:
                url = os.path.join(script_dir, "view", "linux", "ffmpeg.exe")
                exec_args_1 = [
                    url,
                    "-thread_queue_size",
                    "16",
                    "-f",
                    "x11grab",
                    "-rtbufsize",
                    "500M",
                    "-framerate",
                    "3",
                    "-i",
                    ":0.0",
                    "-crf",
                    "23",
                    "-vf",
                    "scale=iw*75/100:ih*75/100,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    "{}".format(self.local_raw_file),
                    "-y",
                ]

            # 1. 启动录制
            proc_1 = subprocess.Popen(
                exec_args_1,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding=system_encoding,
            )

            # 2. 收到结束信号
            self.event.wait()

            # 3. 关闭录制
            output, error = proc_1.communicate(input="q")
            logger.info("RecordingTool proc_1 output: {}, error: {}".format(output, error))

            self.end_time = int(time.time())

            # 4. 判断是否保存
            if self.exec_success:
                if self.config.get("scene") == "always":
                    is_save = True
                else:
                    is_save = False
            else:
                is_save = True
            if not is_save:
                # 不保持
                __path = "{}".format(self.local_raw_file)
                os.remove(__path)
                # 如果删除后文件的文件夹是空，顺带把文件夹删除
                __path_dir = os.path.dirname(__path)
                if folder_empty(__path_dir):
                    os.rmdir("{}".format(__path_dir))
            elif int(self.config.get("cut_time")) <= 0:
                # 不剪切
                os.rename("{}".format(self.local_raw_file), self.local_file)
            else:
                # 剪切mp4, [改进: 冗余量前后各+5s]
                dt = 5
                ss = self.end_time - self.start_time - int(self.config.get("cut_time")) - dt
                if ss <= 0:
                    os.rename("{}".format(self.local_raw_file), self.local_file)
                else:
                    exec_args_2 = [
                        url,
                        "-ss",
                        "{}".format(ss),
                        "-t",
                        "{}".format(int(self.config.get("cut_time")) + dt + dt),
                        "-i",
                        self.local_raw_file,
                        self.local_file,
                        "-y",
                    ]
                    proc_2 = subprocess.Popen(
                        exec_args_2,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding=system_encoding,
                    )
                    output, error = proc_2.communicate()
                    logger.info("RecordingTool proc_2 output: {}, error: {}".format(output, error))

                    os.remove("{}".format(self.local_raw_file))
        except Exception as e:
            self.exec_res = False
            raise e
        finally:
            self.exec_res = True

    def __clear__(self):
        # 1.判断目录是否存在
        # 2.目录存在就便利目录，包含子目录下的所有已.mp4结尾的文件
        # 3.判断.mp4文件的修改时间是否大于7天，
        # 4.删除大于7天的数据

        logger.info("clear mp4:{}")

        file_clear_time = int(self.config.get("file_clear_time", 0))
        if not file_clear_time:
            return
        seven_days_ago = datetime.now() - timedelta(days=file_clear_time)

        for root, dirs, files in os.walk(self.config.get("file_path")):
            for file in files:
                if file.endswith(".mp4"):
                    file_path = os.path.join(root, file)
                    logger.info("walk mp4:{}".format(file_path))
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    # 如果文件修改时间超过7天，则删除该文件
                    if file_mod_time < seven_days_ago:
                        os.remove(file_path)
                        logger.info("clear mp4:{}".format(file_path))
                        # 如果删除后文件的文件夹是空，顺带把文件夹删除
                        __path_dir = os.path.dirname(file_path)
                        if folder_empty(__path_dir):
                            os.rmdir("{}".format(__path_dir))

    def start(self):
        if self.config.get("open"):
            self.thread = threading.Thread(target=self.__tool__, daemon=True)
            self.thread.start()
        else:
            # 不用close提起结束
            self.exec_res = True
        if int(self.config.get("file_clear_time", 0)):
            # 如果需要清理就启动清理程序
            thread_2 = threading.Thread(target=self.__clear__, daemon=True)
            thread_2.start()

    def close(self, is_success: bool):
        # self.event 没有触发，且exec_res没有返回值[有返回值就表示提前结束了]
        if not self.event.is_set() and self.exec_res is None:
            self.exec_success = is_success
            now = int(time.time())
            if now - self.start_time < 3:
                time.sleep(3 - now + self.start_time)
            self.event.set()
            while self.exec_res is None:
                time.sleep(0.1)
            self.exec_res = None
