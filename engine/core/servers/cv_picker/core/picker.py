import json
import os
import platform
import socket
import sys
import threading
import time
from collections import deque

import cv2
import pyautogui
from cv_picker.core import PickType, Status
from cv_picker.core.core import IPickCore, IRectHandler
from cv_picker.core.cv_match import AnchorMatch
from cv_picker.core.cv_picker import ImageDetector
from pynput import keyboard
from rpaframe.logger.logger import base_logger

base_logger.init("cv_picker")
logger = base_logger.get_log()

current_directory = os.getcwd()
desktop_filepath = os.path.join(current_directory, "imgs", "desktop.png")
partial_filepath = os.path.join(current_directory, "imgs", "partial.png")
alt_filepath = os.path.join(current_directory, "imgs", "alt_picker.png")
target_filepath = os.path.join(current_directory, "imgs", "target.png")
anchor_filepath = os.path.join(current_directory, "imgs", "anchor.png")

os.makedirs(os.path.join(current_directory, "imgs"), exist_ok=True)

if sys.platform == "win32":
    from cv_picker.core.core_win import PickCore, RectHandler
elif platform.system() == "Linux":
    from cv_picker.core.core_unix import PickCore, RectHandler
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

PickCore: IPickCore = PickCore()
RectHandler: IRectHandler = RectHandler()


class Socket:
    def __init__(self):
        # 设置 socket 端口号
        self.__socket_port = 11001
        # 创建 socket 对象，负责与高亮部分通信
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_data = None

    def __enter__(self):
        # 进入上下文管理器
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 退出前先隐藏高亮
        try:
            self.hide_wnd()
        except Exception as e:
            pass

    def send_msg(self, message):
        # 发送消息到指定端口
        self.__socket.sendto(message, ("localhost", self.__socket_port))

    def hide_wnd(self):
        self.send_msg('{"operation":"hide","data":""}')

    def receive_rect(self):
        # 接收消息并解析出坐标值
        operation = None
        rect = None
        try:
            data, _ = self.__socket.recvfrom(1024)
            if data:
                self.receive_data = data.decode("utf-8")
                logger.info(f"receive_data:{self.receive_data}")
                operation, rect = self.parse_response(self.receive_data)
            return operation, rect
        except OSError as e:
            pass

    def parse_response(self, data):
        try:
            # 解析 JSON 数据
            response = json.loads(data)
            # 提取坐标值
            operation = response.get("Operation")
            box = response.get("Boxes")[0] if response.get("Boxes") else None

            left = box.get("Left") if box else None
            top = box.get("Top") if box else None
            right = box.get("Right") if box else None
            bottom = box.get("Bottom") if box else None

            print(f"Received coordinates:operation={operation} left={left}, top={top}, right={right}, bottom={bottom}")
            return operation, (left, top, right, bottom)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def send_rect(self, operation="picking", status="", rect=(0, 0, 0, 0), msg=""):
        try:
            # 发送坐标信息
            message = {
                "Operation": operation,
                "Type": status,
                "Boxes": [
                    {
                        "Left": rect[0],
                        "Top": rect[1],
                        "Right": rect[0] + rect[2],
                        "Bottom": rect[1] + rect[3],
                        "Msg": msg,
                    }
                ],
            }
            # 将消息转换为 JSON 格式
            json_message = json.dumps(message)
            print(json_message)
            # 发送消息
            self.send_msg(json_message.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message: {e}")

    def send_signal(self, operation, status):
        try:
            # 发送信号消息
            message = {"Operation": operation, "Type": status}
            json_message = json.dumps(message)
            self.send_msg(json_message.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message: {e}")


class CVPicker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        status: Status = Status.START,
        picktype: PickType = PickType.TARGET,
        anchor_pick_img=None,
    ):
        # 拾取功能初始化
        self.bboxes = None
        self.x = None
        self.y = None
        self.screen_width = 0
        self.screen_height = 0

        # 开启键盘监听
        self.keyboard_listener = None
        self.mouse_listener = None
        self.receiver = None
        self.stop_event = threading.Event()
        self.operation = None

        # 保存应用的截图和Rect
        self.win_rect = None  # 保存窗口Rect
        self.partial_screenshot = None  # 选择窗口截图
        self.partial_rect = None  # 处理过后的窗口Rect
        self.activate_win = None
        self.selected_boxes = None

        self.desktop_image = None  # 用于存储全屏原图的cv2图像
        self.target_rect = None  # 用于存储目标元素的位置
        self.anchor_rect = None  # 用于存储锚点元素的位置
        self.draw_rect = None  # 用于绘制元素高亮框的位置

        self.match_box = None
        self.match_rect = None

        # 初始化拾取状态
        self.__status = status
        self.pick_type = picktype
        self.pick_res = None

        self.start_time = None
        self.event = threading.Event()
        self.run_signal = True
        self.anchor_pick_img = anchor_pick_img

        self.current_keys = set()

    def set(
        self,
        status: Status = Status.START,
        picktype: PickType = PickType.TARGET,
        anchor_pick_img=None,
    ):
        self.__status = status
        self.pick_type = picktype
        self.anchor_pick_img = anchor_pick_img
        self.run_signal = True

    def start_keyboard_listener(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_listener.start()

    # 停止键盘监听
    def stop_keyboard_listener(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def get_minbox(self, x_pos, y_pos, bboxes):
        min_bbox = None
        min_area = float("inf")
        if not x_pos or not y_pos:
            return min_bbox
        for bbox in bboxes:
            bx, by, bw, bh = bbox
            if bx <= x_pos < bx + bw and by <= y_pos < by + bh:
                # 计算当前框的面积
                area = bw * bh
                if area < min_area:
                    min_area = area
                    min_bbox = bbox
                    break
        return min_bbox

    # 记录接收到的socket信号
    def receive_message(self, socket):
        while not self.stop_event.is_set():
            try:
                self.operation, self.target_rect = socket.receive_rect()
            except Exception as e:
                pass

    def get_rect(self):
        if self.bboxes is not None:
            min_bbox = self.get_minbox(self.x, self.y, self.bboxes)

            if min_bbox != self.draw_rect:
                if min_bbox is not None:
                    bx, by, bw, bh = min_bbox
                else:
                    bx, by, bw, bh = 0, 0, 0, 0
                    # bx, by, bw, bh = self.partial_rect[0], self.partial_rect[1], self.partial_rect[2], \
                    # self.partial_rect[3]

                bx = max(0, min(bx, self.screen_width))
                by = max(0, min(by, self.screen_height))
                bw = max(0, min(bw, self.screen_width - bx))
                bh = max(0, min(bh, self.screen_height - by))

                self.draw_rect = (bx, by, bw, bh)
        else:
            pass
        return self.draw_rect

    def on_press(self, key):
        """
        监听全局键盘事件
        :param key:
        :return:
        """

        self.current_keys.add(key)
        print("press key num: {}".format(len(self.current_keys)))
        print("key:{}".format(key))

        if key == keyboard.Key.esc:
            # 按下ESC 进入退出状态
            self.__status = Status.CANCEL
            logger.info("按下ESC：{}".format(self.__status))

        if (
            ({keyboard.Key.ctrl_l} == self.current_keys or {keyboard.Key.ctrl_r} == self.current_keys)
            and len(self.current_keys) == 1
            and self.__status == Status.WAIT_SIGNAL
        ):
            # 按下CTRL 进入普通拾取状态
            self.__status = Status.CV_CTRL
            logger.info("按下CTRL：{}".format(self.__status))
            self.desktop_image = pyautogui.screenshot()

        if (
            ({keyboard.Key.alt_l} == self.current_keys or {keyboard.Key.alt_gr} == self.current_keys)
            and len(self.current_keys) == 1
            and self.__status == Status.WAIT_SIGNAL
        ):
            # 按下ALT 进入智能拾取状态
            self.__status = Status.CV_ALT
            logger.info("按下ALT：{}".format(self.__status))

        if (
            ({keyboard.Key.shift_l} == self.current_keys or {keyboard.Key.shift_r} == self.current_keys)
            and len(self.current_keys) == 1
            and self.pick_type == PickType.TARGET
        ):
            # 按下SHIFT 返回初始状态
            self.__status = Status.CV_SHIFT
            logger.info("按下SHIFT：{}".format(self.__status))

    def on_release(self, key):
        try:
            self.current_keys.remove(key)
            print("release key num: {}".format(len(self.current_keys)))
            print(len(self.current_keys))

        except KeyError:
            pass

    def take_screenshot(self, desktop_image=None):
        # 拾取界面处理，获取界面截图
        time.sleep(0.1)  # 等待0.1s,防止截图时高亮提示框未隐藏
        if self.pick_type == PickType.TARGET:
            self.desktop_image = pyautogui.screenshot()
            self.desktop_image.save(desktop_filepath)
        elif self.pick_type == PickType.ANCHOR:
            if not desktop_image:
                raise NotImplementedError("桌面截图不存在")
            self.desktop_image = desktop_image
            print(f"锚点拾取桌面截图尺寸：{self.desktop_image.width, self.desktop_image.height}")

        self.screen_width, self.screen_height = self.desktop_image.size

        if self.__status == Status.CV_ALT:
            if self.pick_type == PickType.TARGET:
                self.activate_win, title, self.win_rect = RectHandler.get_foreground_window_rect()
                logger.info("智能拾取模式激活窗口截图：{}".format(self.win_rect))
                logger.info("智能拾取模式激活窗口名称：{}".format(title))
                x = max(self.win_rect[0], 0)
                y = max(self.win_rect[1], 0)
                w = min(self.win_rect[2] - self.win_rect[0], self.screen_width)
                h = min(self.win_rect[3] - self.win_rect[1], self.screen_height)

                self.partial_screenshot = self.desktop_image.crop((x, y, x + w, y + h))
                self.partial_rect = (x, y, w, h)

                # self.partial_screenshot = self.desktop_image
                # self.partial_rect = (0, 0, self.screen_width, self.screen_height)
                self.partial_screenshot.save(partial_filepath)
            elif self.pick_type == PickType.ANCHOR:
                self.partial_rect = (
                    0,
                    0,
                    self.desktop_image.width,
                    self.desktop_image.height,
                )
                self.partial_screenshot = self.desktop_image

            # 智能拾取模式，对界面元素进行分割
            picker_cv = ImageDetector(self.partial_screenshot)
            output_img, self.selected_boxes = picker_cv.detect_objects("#00FF00", 1)
            cv2.imwrite(alt_filepath, output_img)

            for box in range(len(self.selected_boxes)):
                self.selected_boxes[box] = (
                    self.selected_boxes[box][0] + self.partial_rect[0],
                    self.selected_boxes[box][1] + self.partial_rect[1],
                    self.selected_boxes[box][2],
                    self.selected_boxes[box][3],
                )
            self.bboxes = sorted(self.selected_boxes, key=lambda bbox: bbox[2] * bbox[3])

        elif self.__status == Status.CV_CTRL:
            # 普通模式，仅保存界面截图
            self.partial_screenshot = self.desktop_image
            self.partial_screenshot.save(partial_filepath)

        else:
            pass

    def check_timeout(self, start_time):
        # 判断拾取是否超时，时间设置3min
        return time.time() - start_time > 60 * 3

    def stop_receiver(self):
        if self.receiver is not None:
            print("event Stopping receiver...")
            self.stop_event.set()
            # self.receiver.join()
            self.receiver = None
            print("Receiver stopped.")

    def run(self):
        # 使用 Socket 类进行通信
        with Socket() as hl:
            self.start_time = time.time()

            # 定义状态处理器字典
            status_handler = {
                Status.INIT: self.handle_init,  # 初始化状态
                Status.START: self.handle_start,  # 开始状态
                Status.WAIT_SIGNAL: self.handle_wait_signal,  # 等待模式切换状态
                Status.CV_CTRL: self.handle_cv_ctrl,  # 普通拾取模式
                Status.CV_ALT: self.handle_cv_alt,  # 智能拾取模式
                Status.SEND_WINDOW: self.handle_send_window,  # 发送激活窗口坐标
                Status.SEND_TARGET: self.handle_send_target,  # 发送目标信号
                Status.CONFIRM: self.handle_confirm,  # 完善确认信号
                Status.CV_WAIT_TARGET: self.handle_cv_wait_target,  # 等待选取确认信号
                Status.CV_SHIFT: self.handle_cv_shift,  # 返回状态
                Status.CANCEL: self.handle_cancel,  # 取消拾取
                Status.OVER: self.handle_over,  # 拾取完成
            }

            # 主循环，根据状态执行相应的处理方法
            while self.run_signal:
                # 检查是否超时
                if self.check_timeout(self.start_time):
                    self.__status = Status.TIMEOUT
                    self.stop_receiver()
                    self.stop_keyboard_listener()
                    hl.send_signal(operation="initialize", status="ESC")
                    break
                # 获取当前状态对应的处理方法
                handler_cv = status_handler.get(self.__status)
                if handler_cv:
                    handler_cv(hl)
                else:
                    raise NotImplementedError("执行状态有误")
            self.stop_keyboard_listener()
            # self.stop_mouse_listener()
            return self.__status, self.pick_res

    def handle_init(self, hl):
        self.initialize()
        self.stop_receiver()
        # 启动新线程
        self.stop_event.clear()

        self.receiver = threading.Thread(target=self.receive_message, args=(hl,))
        self.receiver.daemon = True  # 设置为守护线程
        self.receiver.start()
        print("Receive start")
        self.start_keyboard_listener()
        if self.pick_type == PickType.TARGET:
            self.__status = Status.START
        elif self.pick_type == PickType.ANCHOR:
            self.__status = Status.CV_ALT

    def handle_start(self, hl):
        hl.send_signal(operation="start", status="CV")
        print("发送状态{}".format(self.__status))
        self.__status = Status.WAIT_SIGNAL

    def handle_wait_signal(self, hl):
        pass

    def handle_cv_ctrl(self, hl):
        hl.send_signal(operation="start", status="hide")
        self.take_screenshot()
        hl.send_signal(operation="start", status="CV_CTRL")
        print("状态{}已发送".format(self.__status))
        self.__status = Status.CV_WAIT_TARGET

    def handle_cv_alt(self, hl):
        if self.pick_type == PickType.TARGET:
            hl.send_signal(operation="start", status="hide")
            self.take_screenshot()
            hl.send_signal(operation="start", status="CV_ALT")
        elif self.pick_type == PickType.ANCHOR:
            self.take_screenshot(self.anchor_pick_img)
        print("状态{}已发送".format(self.__status))
        self.__status = Status.SEND_WINDOW

    def handle_send_window(self, hl):
        hl.send_rect(operation="active_window", rect=self.partial_rect, msg="")
        self.__status = Status.SEND_TARGET

    def handle_send_target(self, hl):
        last_rect = None
        last_position = None
        # self.send_rect = queue.Queue(maxsize=2)
        self.send_rect = deque(maxlen=1)
        send_time = time.time()
        while self.__status == Status.SEND_TARGET and not self.check_timeout(self.start_time):
            if self.operation in ["confirm", "stop"]:
                self.__status = Status.CONFIRM
            time.sleep(0.1)
            current_position = PickCore.get_mouse_position()
            if current_position == last_position:
                continue

            last_position = current_position
            self.x, self.y = current_position

            self.draw_rect = self.get_rect()
            if self.draw_rect and self.draw_rect != last_rect:
                self.send_rect.append(self.draw_rect)

            if self.send_rect and time.time() - send_time > 0.1:
                send_time = time.time()
                last_rect = self.send_rect.pop()
                operation = "picking"
                msg = "锚点图像" if self.pick_type == PickType.ANCHOR else None
                hl.send_rect(operation=operation, rect=last_rect, msg=msg)

    def handle_confirm(self, hl):
        if self.operation == "confirm" and self.target_rect:
            if self.pick_type == PickType.TARGET:
                print("目标元素坐标：{}".format(self.target_rect))
                self.pick_res = self.check_target(self.target_rect)
                print("获取到的目标数据:{}".format(self.pick_res))
                if self.pick_res:
                    self.__status = Status.OVER
                else:
                    raise NotImplementedError("目标获取失败")
            elif self.pick_type == PickType.ANCHOR:
                self.pick_res = self.check_anchor(self.target_rect)
                if self.pick_res:
                    hl.send_rect(operation="picking", status="valid", msg="锚点图像")
                    self.__status = Status.OVER
                else:
                    hl.send_rect(operation="picking", status="invalid", msg="锚点图像")
                    self.target_rect = None
                    while self.operation != "continue":
                        self.event.wait(0.1)
                    self.__status = Status.SEND_TARGET
        elif self.operation == "continue":
            self.__status = Status.SEND_TARGET
        else:
            pass

    def handle_cv_wait_target(self, hl):
        while self.__status == Status.CV_WAIT_TARGET and not self.check_timeout(self.start_time):
            if self.operation == "confirm" and self.target_rect is not None:
                self.pick_res = self.check_target(self.target_rect)
                if self.pick_res:
                    self.__status = Status.OVER
                else:
                    raise NotImplementedError()
            else:
                pass

    def handle_cv_shift(self, hl):
        hl.send_signal(operation="initialize", status="SHIFT")
        print(f"已发送状态，当前状态为{self.__status}")
        self.__status = Status.START
        self.initialize()
        self.clear_selected_boxes()

    def handle_cancel(self, hl):
        hl.send_signal(operation="initialize", status="ESC")
        print(f"已发送取消操作，当前状态为{self.__status}")
        self.current_keys.clear()
        self.run_signal = False

    def handle_over(self, hl):
        hl.send_signal(operation="initialize", status="ESC")
        print(f"已发送取消操作，当前状态为{self.__status}")
        self.current_keys.clear()
        self.run_signal = False

    def check_target(self, target_rect):
        if target_rect:
            print("进入元素唯一校验阶段")
            target_img = self.desktop_image.crop(target_rect)
            print("target_rect:{}".format(target_rect))
            print("desktop_image:{}".format(self.desktop_image.size))
            target_img.save(target_filepath)
            res = None

            if not AnchorMatch.check_if_multiple_elements(self.desktop_image, target_img, match_similarity=0.80):
                print("元素不唯一，自动选取锚点")
                if not self.bboxes:
                    picker_cv = ImageDetector(self.partial_screenshot)
                    output_img, self.selected_boxes = picker_cv.detect_objects("#00FF00", 1)
                    self.bboxes = sorted(self.selected_boxes, key=lambda bbox: bbox[2] * bbox[3])

                for box in self.bboxes[::-1]:
                    anchor_img = self.desktop_image.crop((box[0], box[1], box[0] + box[2], box[1] + box[3]))
                    if AnchorMatch.check_if_multiple_elements(self.desktop_image, anchor_img, match_similarity=0.95):
                        self.anchor_rect = box
                        anchor_img.save(anchor_filepath)
                        res = PickCore.json_res(target_img, target_rect, anchor_img, box, self.desktop_image)
                        break
            else:
                res = PickCore.json_res(target_img, target_rect, None, None, self.desktop_image)
        else:
            raise NotImplementedError("目标元素坐标为空")
        return res

    def check_anchor(self, anchor_rect):
        if anchor_rect:
            start_time = time.time()
            print("进入锚点唯一校验阶段:{}".format(start_time))
            anchor_img = self.desktop_image.crop(anchor_rect)
            anchor_img.save(anchor_filepath)
            res = None
            if not AnchorMatch.check_if_multiple_elements(self.desktop_image, anchor_img, match_similarity=0.95):
                print("锚点必须为唯一元素，请重新选取")
            else:
                res = PickCore.json_res(None, None, anchor_img, anchor_rect, self.desktop_image)

            print("锚点唯一校验结束:{}".format(time.time() - start_time))
            return res

    def initialize(self):
        self.desktop_image = None
        self.win_rect = None
        self.partial_screenshot = None
        self.partial_rect = None
        self.pick_res = None
        self.target_rect = None
        self.anchor_rect = None
        self.match_box = None
        self.match_rect = None
        self.bboxes = None
        self.draw_rect = None
        self.operation = None
        self.current_keys.clear()

    def clear_selected_boxes(self):
        self.target_rect = None
        self.anchor_rect = None
        self.match_box = None
        self.match_rect = None


if __name__ == "__main__":
    picker = CVPicker()
    picker.run()
    sys.exit(-1)
