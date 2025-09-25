import json
import os
import time

# 这里写入PyQT里面使用的QT_QPA_PLATFORM_PLUGIN_PATH路径，根据自己的环境进行修改
os.environ.update(
    {
        "QT_QPA_PLATFORM_PLUGIN_PATH": "/home/horizon/RPA/组合/python_base_linux/lib/python3.7/site-packages/PyQt5/Qt5/plugins/platforms/"
    }
)

import sys

from PyQt5.QtCore import QEvent, QPointF, QRect, QRectF, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QGuiApplication,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt5.QtNetwork import QHostAddress, QUdpSocket
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class DrawStatus:
    waitDraw = 0
    drawing = 1
    clicked = 2


class HighlightForm(QWidget):
    message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HighlightForm")
        self.screenshot_widget = None
        self.mode = "normal"
        self.validate_rects = None

        # 设置几个标识符
        self.draw_status = DrawStatus.waitDraw

        self.setWindowFlags(
            Qt.WindowTransparentForInput
            | Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Dialog
            | Qt.Tool
            | Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.draw_rect = QRect(0, 0, 1, 1)

        self.init_toolbar()
        self.full_screen()
        self.update()

    def init_toolbar(self):
        # 工具条初始化
        self.toolbar = QWidget(self)

        # 主工具栏
        mainToolLayout = QHBoxLayout()

        # 创建按钮
        self.btn_cancel = QPushButton("退出")
        self.btn_saveFile = QPushButton("保存")

        # 设置按钮样式
        button_style = """
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #c0c0c0;
                        border-radius: 5px;
                        padding: 5px 15px;
                        color: #333;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        border: 1px solid #b0b0b0;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                        border: 1px solid #a0a0a0;
                    }
                """
        self.btn_cancel.setStyleSheet(button_style)
        self.btn_saveFile.setStyleSheet(button_style)

        # 添加按钮到布局
        mainToolLayout.addWidget(self.btn_saveFile)
        mainToolLayout.addWidget(self.btn_cancel)
        mainToolLayout.setContentsMargins(0, 0, 0, 0)  # 去除边框间隙
        mainToolLayout.setSpacing(5)

        # # 设置工具栏布局
        toolLayout = QVBoxLayout(self.toolbar)
        toolLayout.addLayout(mainToolLayout)
        toolLayout.setContentsMargins(0, 0, 0, 0)  # 去除边框间隙
        toolLayout.setSpacing(0)

        # 初始化工具栏的可见性
        self.toolbar.setVisible(True)

        # 连接按钮信号
        self.btn_cancel.clicked.connect(self.slt_cancel)
        self.btn_saveFile.clicked.connect(self.slt_saveFile)

        # 计算工具栏尺寸
        self.toolbar.adjustSize()
        self.toolBarWidth = self.toolbar.width()
        self.toolBarHeight = self.toolbar.height()

        # 隐藏工具栏
        self.hideToolBar()

    def full_screen(self):
        self.screen = QGuiApplication.primaryScreen()
        self.screenshot = self.screen.grabWindow(0)
        self.size = self.screenshot.size()
        self.setGeometry(0, 0, self.size.width(), self.size.height())
        self.show()

    def slt_cancel(self):
        send_json = {"Operation": "continue"}
        self.send_message(json.dumps(send_json))
        self.draw_status = DrawStatus.drawing
        self.hideToolBar()

    def slt_saveFile(self):
        send_json = {
            "Operation": "confirm",
            "Boxes": [
                {
                    "Left": self.draw_rect.left(),
                    "Top": self.draw_rect.top(),
                    "Right": self.draw_rect.right(),
                    "Bottom": self.draw_rect.bottom(),
                    "Msg": "",
                }
            ],
        }
        self.send_message(json.dumps(send_json))
        self.draw_status = DrawStatus.waitDraw
        self.hideToolBar()

    def hideToolBar(self):
        # 隐藏工具栏的逻辑
        self.toolbar.setVisible(False)

    def handle_invalid(self):
        self.hideToolBar()
        self.draw_status = DrawStatus.drawing

    def paintEvent(self, event):
        self.raise_()
        painter = QPainter(self)
        print("paintEvent", self.mode, self.draw_rect)
        if self.mode != "validate":
            pen = QPen(QColor(255, 255, 224))
            pen.setWidth(3)
            brush = QBrush(QColor(255, 192, 203, 155))
            painter.setPen(pen)
            painter.setBrush(brush)
            print("drawing rect: ", self.draw_rect)
            painter.drawRect(self.draw_rect)
        else:
            pen = QPen(QColor(255, 0, 0))
            painter.setPen(pen)
            pen.setWidth(5)
            for rect in self.validate_rects:
                painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if the click is within the rectangle
            if self.draw_rect.contains(event.pos()):
                self.draw_status = DrawStatus.clicked
                toolbar_position = self.draw_rect.bottomLeft()
                toolbar_position.setY(toolbar_position.y() + 3)
                self.toolbar.move(toolbar_position)
                send_json = {"Operation": "stop"}
                self.send_message(json.dumps(send_json))
                self.toolbar.show()

            else:
                self.hideToolBar()
                send_json = {"Operation": "continue"}
                self.send_message(json.dumps(send_json))
                self.draw_status = DrawStatus.drawing

    def update_rect(self, rect):
        self.draw_rect = rect

        if self.draw_status != DrawStatus.clicked:
            print("update_rect:", self.draw_rect, self.draw_status)
            self.repaint()

    def update_validate_rects(self, rects):
        self.validate_rects = rects
        self.mode = "validate"
        self.repaint()

    def update_mode(self, mode):
        self.mode = mode
        if self.mode.find("CV") != -1:
            # self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Dialog | Qt.Tool | Qt.X11BypassWindowManagerHint
            )

    def activate_screenshot_form(self):
        if not self.screenshot_widget:
            self.screenshot_widget = ScreenshotWidget()
            self.screenshot_widget.show()
            self.raise_()  # 将高亮窗口提到最前面

    def close_activate_screenshot_form(self):
        if self.screenshot_widget:
            self.screenshot_widget.close()
            self.screenshot_widget = None

    def send_message(self, send_string):
        # 在某个方法中触发信号，发送消息
        self.message_signal.emit(send_string)

    def initialize(self):
        self.hideToolBar()
        if self.screenshot_widget:
            self.screenshot_widget.hide()
        self.draw_status = DrawStatus.waitDraw
        self.draw_rect = QRect(0, 0, 1, 1)
        self.validate_rects = None
        self.mode = "normal"
        self.update()


class ScreenshotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScreenshotForm")

        # Get the screen and take a screenshot
        screen = app.primaryScreen()
        screenshot = screen.grabWindow(0)

        # Set the window to be frameless and stay behind
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)

        # Set the initial size and position to cover the entire screen
        self.setGeometry(screenshot.rect())

        # Use a QLabel to display the screenshot
        self.label = QLabel(self)
        self.label.setPixmap(screenshot)


class CtrlWidget(QWidget):
    message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CtrlForm")
        self.showFullScreen()
        print(self.rect())
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.selection_rect = None

        # Set the window to be frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Capture the desktop as a background
        screen = QApplication.primaryScreen()
        self.background = screen.grabWindow(0)
        self.setGeometry(self.background.rect())

        # self.toolbar = None
        print("Initial self.rect():", self.rect())
        self.toolbar = None
        self.toolbar_show = False
        self.init_toolbar()
        self.update()
        print("After init_toolbar self.rect():", self.rect())
        # self.raise_()

    def init_toolbar(self):
        # 工具条初始化
        self.toolbar = QWidget(self)

        # 设置工具栏的固定尺寸
        self.toolbar.setFixedSize(200, 50)  # 假设宽度200，高度50

        # 创建按钮并设定为工具栏的子控件
        self.btn_cancel = QPushButton("退出", self.toolbar)
        self.btn_saveFile = QPushButton("保存", self.toolbar)

        # 设置按钮样式
        button_style = """
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #c0c0c0;
                        border-radius: 5px;
                        padding: 5px 15px;
                        color: #333;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                        border: 1px solid #b0b0b0;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                        border: 1px solid #a0a0a0;
                    }
                """
        self.btn_cancel.setStyleSheet(button_style)
        self.btn_saveFile.setStyleSheet(button_style)

        # 设置每个按钮的位置和大小
        self.btn_saveFile.setGeometry(10, 10, 80, 30)  # 参数是x, y, width, height
        self.btn_cancel.setGeometry(100, 10, 80, 30)

        # 初始化工具栏的可见性
        self.toolbar.setVisible(False)

        # 连接按钮信号
        self.btn_cancel.clicked.connect(self.slt_cancel)
        self.btn_saveFile.clicked.connect(self.slt_saveFile)

    def hideToolBar(self):
        # 隐藏工具栏的逻辑
        self.toolbar.setVisible(False)

    def slt_cancel(self):
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.selection_rect = None
        self.hideToolBar()
        self.toolbar_show = False
        self.update()

    def slt_saveFile(self):
        send_json = {
            "Operation": "confirm",
            "Boxes": [
                {
                    "Left": self.selection_rect.left(),
                    "Top": self.selection_rect.top(),
                    "Right": self.selection_rect.right(),
                    "Bottom": self.selection_rect.bottom(),
                    "Msg": "",
                }
            ],
        }
        print(send_json)
        self.send_message(json.dumps(send_json))
        self.selecting = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.selecting:
                self.start_point = event.pos()
                self.selecting = True

    def mouseMoveEvent(self, event):
        if self.selecting and (not self.toolbar_show):
            self.end_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()  # Trigger a repaint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting and (not self.toolbar_show):
            toolbar_position = self.selection_rect.bottomLeft()
            toolbar_position.setY(toolbar_position.y() + 3)
            self.toolbar.move(toolbar_position)
            self.toolbar.setVisible(True)
            self.toolbar_show = True

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        # print(rect)
        painter.drawPixmap(rect, self.background)

        semi_transparent_red = QColor(255, 0, 0, 80)  # 红色，alpha为100（半透明）
        painter.fillRect(rect, semi_transparent_red)

        # If the user is selecting a region, draw the rectangle
        if self.selection_rect:
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
            # 保存当前painter的状态
            painter.save()

            # 设置裁剪区域为选择矩形
            painter.setClipRect(self.selection_rect)

            # 再次绘制选择区域的背景 pixmap，以去除红色蒙层的效果
            painter.drawPixmap(self.selection_rect, self.background, self.selection_rect)

            # 恢复painter的状态
            painter.restore()

            # 最后绘制选择矩形的边框
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
            painter.drawRect(self.selection_rect)

    def send_message(self, send_string):
        # 在某个方法中触发信号，发送消息
        self.message_signal.emit(send_string)


class HoverHintWidget(QWidget):
    def __init__(self, mode):
        super().__init__()
        self.setWindowTitle("HoverHintForm")

        self.mode = mode
        # 标志位，跟踪窗口位置状态
        self.is_at_bottom_right = False
        self.init_ui()

    def init_ui(self):
        try:
            # 设置窗口大小和初始位置（左上角）
            self.setGeometry(0, 0, 300, 200)

            # 设置无边框窗口，方便制作透明效果
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        except Exception as e:
            print(f"Error in HoverHintWidget.init_ui: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)

        def paint_text(
            painter,
            text,
            center_x,
            center_y,
            font_size=16,
            font="Arial",
            color=QColor(0, 0, 0),
            box_flag=False,
        ):
            # 设置字体和颜色
            painter.setPen(color)
            painter.setFont(QFont(font, font_size))
            text_height = painter.fontMetrics().height()
            text_width = painter.fontMetrics().width(text)
            x = center_x - text_width // 2
            y = center_y - painter.fontMetrics().ascent() // 2
            painter.drawText(x, y, text)

            if box_flag:
                padding = 5  # 在矩形四周加一些填充，使其不紧贴文本
                rect_x = x - padding
                rect_y = y - text_height + padding
                rect_width = text_width + 2 * padding
                rect_height = text_height
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(rect_x, rect_y, rect_width, rect_height)

        # 设置半透明白色矩形背景
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        if self.mode == "CV":
            # 设置字体和颜色
            paint_text(painter=painter, text="ALT", center_x=100, center_y=80, box_flag=True)
            paint_text(painter=painter, text="CTRL", center_x=100, center_y=150, box_flag=True)
            paint_text(painter=painter, text="智能拾取", center_x=200, center_y=80)
            paint_text(painter=painter, text="截图拾取", center_x=200, center_y=150)
        else:
            # 设置字体和颜色
            paint_text(
                painter=painter,
                text="CTRL + 点击",
                center_x=100,
                center_y=80,
                box_flag=True,
            )
            paint_text(painter=painter, text="ESC", center_x=100, center_y=150, box_flag=True)
            paint_text(painter=painter, text="拾取", center_x=200, center_y=80)
            paint_text(painter=painter, text="退出", center_x=200, center_y=150)

    def enterEvent(self, event):
        # 获取屏幕大小
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        if self.is_at_bottom_right:
            x, y = 0, 0
        else:
            # 移动窗口到右下角
            x = screen_width - self.width()
            y = screen_height - self.height()

        # 移动到目标位置
        self.move(x, y)

        # 切换标志位
        self.is_at_bottom_right = not self.is_at_bottom_right

        event.accept()


class ConsoleApp(QMainWindow):
    def __init__(self, socket_port):
        super().__init__()

        # 创建 QUdpSocket
        self.udp_socket = QUdpSocket(self)
        self.sender_port = None
        self.sender_host = None
        if not self.udp_socket.bind(QHostAddress.Any, int(socket_port)):  # 绑定到端口 11001
            print("Failed to bind UDP socket!")
            return

        # 连接 readyRead 信号到槽函数
        self.udp_socket.readyRead.connect(self.read_datagrams)
        print("UDP Server started on port 11001...")

        self.highlight_form = HighlightForm()
        self.highlight_form.message_signal.connect(self.handle_message)
        self.highlight_form.showFullScreen()
        self.ctrl_form = None
        self.hint_form = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_datagrams)
        self.timer.start(500)  # 每隔 500 毫秒调用一次 read_datagrams

        print(f"Console App started:{self.udp_socket.hasPendingDatagrams()}")

    def read_datagrams(self):
        """处理接收到的 UDP 数据包"""
        if self.udp_socket.hasPendingDatagrams():
            # 获取数据包大小
            datagram_size = self.udp_socket.pendingDatagramSize()
            # 读取数据包
            datagram = self.udp_socket.readDatagram(datagram_size)
            if datagram:
                data, sender_host, sender_port = datagram
                message = data.decode("utf-8")  # 将字节数据解码为字符串
                print(f"Received from {sender_host}:{sender_port}: {message}")
                self.sender_port = sender_port
                self.sender_host = sender_host
                message_dict = json.loads(message)
                if message_dict["Operation"] == "start":
                    self.highlight_form.update_mode(message_dict["Type"])
                    if message_dict["Type"] == "CV":
                        if not self.hint_form:
                            self.hint_form = HoverHintWidget("CV")
                            self.hint_form.show()
                            self.hint_form.raise_()
                            pass
                        else:
                            self.hint_form.show()
                            self.hint_form.raise_()
                    if message_dict["Type"] == "hide":
                        self.hint_form.hide()
                    if message_dict["Type"] == "CV_ALT":
                        self.highlight_form.activate_screenshot_form()
                        pass
                    elif message_dict["Type"] == "CV_CTRL":
                        if not self.ctrl_form:
                            self.ctrl_form = CtrlWidget()
                            self.ctrl_form.showFullScreen()
                            self.ctrl_form.raise_()
                            self.ctrl_form.message_signal.connect(self.handle_message)
                        else:
                            self.ctrl_form.show()
                            self.ctrl_form.raise_()
                elif message_dict["Operation"] == "picking":
                    if message_dict["Type"] == "invalid":
                        self.highlight_form.handle_invalid()
                    if len(message_dict["Boxes"]) == 1:
                        print("updating rect...")
                        # 一定要show一下，否则不显示
                        self.highlight_form.show()
                        self.highlight_form.showFullScreen()
                        self.highlight_form.update_rect(
                            QRect(
                                message_dict["Boxes"][0]["Left"],
                                message_dict["Boxes"][0]["Top"],
                                message_dict["Boxes"][0]["Right"] - message_dict["Boxes"][0]["Left"],
                                message_dict["Boxes"][0]["Bottom"] - message_dict["Boxes"][0]["Top"],
                            )
                        )
                    else:
                        validate_rects = []
                        for box in message_dict["Boxes"]:
                            validate_rects.append(
                                QRect(
                                    box["Left"],
                                    box["Top"],
                                    box["Right"] - box["Left"],
                                    box["Bottom"] - box["Top"],
                                )
                            )
                        for i in range(3):
                            self.highlight_form.show()
                            time.sleep(0.5)
                            self.highlight_form.hide()
                            time.sleep(0.5)
                        self.highlight_form.show()
                elif message_dict["Operation"] == "initialize":
                    if message_dict["Type"] == "SHIFT":
                        self.highlight_form.initialize()
                        if self.ctrl_form:
                            self.ctrl_form.close()
                            self.ctrl_form = None
                        if self.hint_form:
                            self.hint_form.show()
                            self.hint_form.raise_()
                    if message_dict["Type"] == "ESC":
                        self.highlight_form.initialize()
                        # if self.highlight_form.screenshot_widget:
                        #     self.highlight_form.close_activate_screenshot_form()
                        if self.ctrl_form:
                            self.ctrl_form.hide()
                        if self.hint_form:
                            self.hint_form.hide()
                    if message_dict["Type"] == "Exit":
                        if self.highlight_form.screenshot_widget:
                            self.highlight_form.screenshot_widget.close()
                        self.highlight_form.close()
                        if self.ctrl_form:
                            self.ctrl_form.close()
                        if self.hint_form:
                            self.hint_form.close()
                        self.close()
                elif message_dict["Operation"] == "validate":
                    validate_rects = []
                    for box in message_dict["Boxes"]:
                        validate_rects.append(
                            QRect(
                                box["Left"],
                                box["Top"],
                                box["Right"] - box["Left"],
                                box["Bottom"] - box["Top"],
                            )
                        )
                    self.highlight_form.update_validate_rects(validate_rects)
                    for i in range(3):
                        self.highlight_form.show()
                        time.sleep(0.5)
                        self.highlight_form.hide()
                        time.sleep(0.5)
                    # self.highlight_form.show()

    def handle_message(self, message):
        # 处理来自 HighlightForm 的消息
        print(f"Received message from HighlightForm: {message}")
        self.udp_socket.writeDatagram(message.encode("utf-8"), QHostAddress("127.0.0.1"), self.sender_port)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    console = ConsoleApp(sys.argv[1])
    # canvas.showFullScreen()  # 画布全屏显示
    # canvas.hide()  # 隐藏画布
    sys.exit(app.exec_())
