import json
import os
import subprocess
import threading
import time
import urllib.parse

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import DialogResult
from rpatools.tools import RpaTools

from rpadialog import (
    ButtonType,
    DefaultButtonC,
    DefaultButtonCN,
    DefaultButtonY,
    DefaultButtonYN,
    FileType,
    InputType,
    MessageType,
    OpenType,
    SelectType,
    TimeFormat,
    TimeType,
)
from rpadialog.core import DialogCore
from rpadialog.error import *


class Dialog:
    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param(
                "message_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            atomicMg.param(
                "message_content",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                limitLength=[-1, 120],
            ),
            atomicMg.param("button_type"),
            atomicMg.param(
                "auto_check",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.wait_time.show",
                        expression="return $this.auto_check.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "default_button_c",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_c.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.CONFIRM.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_cn",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_cn.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.CONFIRM_CANCEL.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_y",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_y.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.YES_NO.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "default_button_yn",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button_yn.show",
                        expression="return $this.auto_check.value == true && $this.button_type.value == '{}'".format(
                            ButtonType.YES_NO_CANCEL.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "preview_button",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("result_button", types="Str")],
    )
    def message_box(
        box_title: str = "消息提示框",
        message_type: MessageType = MessageType.MESSAGE,
        message_content: str = "",
        button_type: ButtonType = ButtonType.CONFIRM,
        auto_check: bool = False,
        wait_time: int = None,
        default_button_c: DefaultButtonC = DefaultButtonC.CONFIRM,
        default_button_cn: DefaultButtonCN = DefaultButtonCN.CONFIRM,
        default_button_y: DefaultButtonY = DefaultButtonY.YES,
        default_button_yn: DefaultButtonYN = DefaultButtonYN.YES,
        preview_button=None,
    ) -> str:
        exe_path = RpaTools.get_window_dir()
        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")

        if auto_check and not wait_time:
            wait_time = 60
        encoded_data = urllib.parse.quote(
            json.dumps(
                {
                    "key": "Dialog.message_box",
                    "box_title": box_title,
                    "message_type": message_type.value,
                    "message_content": message_content,
                    "button_type": button_type.value,
                    "auto_check": auto_check,
                    "wait_time": wait_time,
                    "outputkey": "result_button",
                }
            )
        )
        args = [
            exe_path,
            f"--url=tauri://localhost/userform.html?option={encoded_data}",
        ]
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        output_list = []
        thread = threading.Thread(target=DialogCore.read_output, args=(process, output_list), daemon=True)
        thread.start()

        last_position = None
        start_time = time.time()
        save_dict = {}

        from pynput import keyboard, mouse

        def on_move(x, y):
            nonlocal auto_check
            if auto_check:
                print("用户干预：鼠标移动，停止自动检查")
                auto_check = False

        def on_click(x, y, button, pressed):
            nonlocal auto_check
            if auto_check:
                print("用户干预：鼠标点击，停止自动检查")
                auto_check = False

        def on_press(key):
            nonlocal auto_check
            if auto_check:
                print("用户干预：键盘按下，停止自动检查")
                auto_check = False

        def on_release(key):
            # 监听esc按键，按下之后结束监听
            nonlocal auto_check
            if auto_check:
                if key == keyboard.Key.esc:
                    print("用户手动结束监听")
                    auto_check = False

        if auto_check:  # Only start the listener if autocheck is enabled
            mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
            keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

            mouse_listener.start()
            keyboard_listener.start()

        while True:
            if auto_check:
                cur_position = DialogCore.get_mouse_position()
                if cur_position != last_position:
                    last_position = cur_position
                    start_time = time.time()
            if auto_check and time.time() - start_time > wait_time:
                print("kill")
                break
            if output_list:
                output = output_list.pop(0)
                save_str = output.strip()

            if process.poll() is not None:
                break

            try:
                save_dict = json.loads(save_str)
            except Exception as error:
                pass
        try:
            process.kill()
        except Exception:
            pass

        if not save_dict.get("result_button") and auto_check:
            if button_type == ButtonType.CONFIRM:
                result_button = default_button_c.value
            elif button_type == ButtonType.CONFIRM_CANCEL:
                result_button = default_button_cn.value
            elif button_type == ButtonType.YES_NO:
                result_button = default_button_y.value
            elif button_type == ButtonType.YES_NO_CANCEL:
                result_button = default_button_yn.value
            else:
                raise NotImplementedError()
        else:
            result_button = save_dict.get("result_button")

        return result_button

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("input_type"),
            atomicMg.param("input_title", types="Str", required=False, limitLength=[-1, 60]),
            atomicMg.param(
                "default_input_text",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.default_input_text.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param(
                "default_input_pwd",
                formType=AtomicFormTypeMeta(type=AtomicFormType.DEFAULTPASSWORD.value),
                required=False,
                limitLength=[4, 16],
                dynamics=[
                    DynamicsItem(
                        key="$this.default_input_pwd.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.PASSWORD.value),
                    )
                ],
            ),
            atomicMg.param(
                "preview_button",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("input_content", types="Str")],
    )
    def input_box(
        box_title: str = "输入对话框",
        input_type: InputType = InputType.TEXT,
        input_title: str = "输入框标题",
        default_input_text: str = "",
        default_input_pwd: str = "",
        preview_button=None,
    ):
        exe_path = RpaTools.get_window_dir()

        if input_type == InputType.TEXT:
            default_input = default_input_text
        elif input_type == InputType.PASSWORD:
            default_input = default_input_pwd
        else:
            raise NotImplementedError()

        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")
        data = {
            "key": "Dialog.input_box",
            "box_title": box_title,
            "input_type": input_type.value,
            "input_title": input_title,
            "default_input": default_input,
            "outputkey": "input_content",
        }
        data = json.dumps(data)
        encoded_data = urllib.parse.quote(data)
        args = [
            exe_path,
            f"--url=tauri://localhost/userform.html?option={encoded_data}",
        ]

        save_dict = DialogCore.exe_run(args)

        input_content = save_dict.get("input_content")
        return input_content or None

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("select_type"),
            atomicMg.param(
                "options",
                formType=AtomicFormTypeMeta(AtomicFormType.OPTIONSLIST.value),
                need_parse="str",
            ),
            atomicMg.param(
                "options_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
            ),
            atomicMg.param(
                "preview_button",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("select_result", types="Any")],
    )
    def select_box(
        box_title: str = "选择对话框",
        select_type: SelectType = SelectType.SINGLE,
        options: list = [],
        options_title: str = "",
        preview_button=None,
    ):
        exe_path = RpaTools.get_window_dir()
        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")

        data = {
            "key": "Dialog.select_box",
            "box_title": box_title,
            "select_type": select_type.value,
            "options": options,
            "options_title": options_title,
            "outputkey": "select_result",
        }
        data = json.dumps(data)
        encoded_data = urllib.parse.quote(data)
        args = [
            exe_path,
            f"--url=tauri://localhost/userform.html?option={encoded_data}",
        ]

        save_dict = DialogCore.exe_run(args)

        return save_dict.get("select_result") if save_dict.get("select_result") else None

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                limitLength=[-1, 50],
            ),
            atomicMg.param("time_type", required=False),
            atomicMg.param("time_format", required=False),
            atomicMg.param(
                "default_time",
                required=False,
                formType=AtomicFormTypeMeta(
                    AtomicFormType.DEFAULTDATEPICKER.value,
                    params={"format": "YYYY-MM-DD"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_time.show",
                        expression="return $this.time_type.value == '{}'".format(TimeType.TIME.value),
                    ),
                    DynamicsItem(
                        key="$this.default_time.formType.params.format",
                        expression="return $this.time_format.value",
                    ),
                ],
            ),
            atomicMg.param(
                "default_time_range",
                required=False,
                formType=AtomicFormTypeMeta(
                    AtomicFormType.RANGEDATEPICKER.value,
                    params={"format": "YYYY-MM-DD"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_time_range.show",
                        expression="return $this.time_type.value == '{}'".format(TimeType.TIME_RANGE.value),
                    ),
                    DynamicsItem(
                        key="$this.default_time.formType.params.format",
                        expression="return $this.time_format.value",
                    ),
                ],
            ),
            atomicMg.param(
                "input_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                types="Str",
            ),
            atomicMg.param(
                "preview_button",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("select_time", types="Any")],
    )
    def select_time_box(
        box_title: str = "日期时间选择框",
        time_type: TimeType = TimeType.TIME,
        time_format: TimeFormat = TimeFormat.YEAR_MONTH_DAY,
        default_time: str = "",
        default_time_range: list = ["", ""],
        input_title: str = "输入框标题",
        preview_button: bool = None,
    ):
        exe_path = RpaTools.get_window_dir()

        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")

        data = {
            "key": "Dialog.select_time_box",
            "box_title": box_title,
            "time_type": time_type.value,
            "time_format": time_format.value,
            "default_time": default_time,
            "default_time_range": default_time_range,
            "input_title": input_title,
            "outputkey": "select_time",
        }
        data = json.dumps(data)
        print(f"data:{data}")
        encoded_data = urllib.parse.quote(data)
        args = [
            exe_path,
            f"--url=tauri://localhost/userform.html?option={encoded_data}",
        ]

        save_dict = DialogCore.exe_run(args)

        return (
            save_dict.get("select_time")
            if (save_dict.get("select_time") and save_dict.get("select_time") != ["", ""])
            else None
        )

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title_file",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.box_title_file.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
                limitLength=[-1, 50],
            ),
            atomicMg.param(
                "box_title_folder",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.box_title_folder.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FOLDER.value),
                    )
                ],
                limitLength=[-1, 50],
            ),
            atomicMg.param("open_type", required=False),
            atomicMg.param(
                "file_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_type.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "multiple_choice",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.multiple_choice.show",
                        expression="return $this.open_type.value == '{}'".format(OpenType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "select_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                required=False,
                limitLength=[-1, 60],
            ),
            atomicMg.param(
                "default_path",
                required=False,
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "preview_button",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("select_file", types="Any")],
    )
    def select_file_box(
        box_title_file: str = "文件选择框",
        box_title_folder="文件夹选择框",
        open_type: OpenType = OpenType.FILE,
        file_type: FileType = FileType.ALL,
        multiple_choice: bool = True,
        select_title: str = "",
        default_path: str = "",
        preview_button=None,
    ):
        exe_path = RpaTools.get_window_dir()

        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")
        if open_type == OpenType.FILE:
            box_title = box_title_file
        elif open_type == OpenType.FOLDER:
            box_title = box_title_folder
        else:
            raise NotImplementedError()
        data = {
            "key": "Dialog.select_file_box",
            "box_title": box_title,
            "open_type": open_type.value,
            "file_type": file_type.value,
            "multiple_choice": multiple_choice,
            "select_title": select_title,
            "default_path": default_path,
            "outputkey": "select_file",
        }
        data = json.dumps(data)
        encoded_data = urllib.parse.quote(data)
        args = [
            exe_path,
            f"--url=tauri://localhost/userform.html?option={encoded_data}",
        ]

        save_dict = DialogCore.exe_run(args)

        return save_dict.get("select_file") if save_dict.get("select_file") else None

    @staticmethod
    @atomicMg.atomic(
        "Dialog",
        inputList=[
            atomicMg.param(
                "box_title",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
                types="Str",
                limitLength=[-1, 50],
            ),
            atomicMg.param(
                "design_interface",
                types="Str",
                formType=AtomicFormTypeMeta(AtomicFormType.MODALBUTTON.value),
                required=False,
                need_parse="json_str",
            ),
            atomicMg.param(
                "auto_check",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.wait_time.show",
                        expression="return $this.auto_check.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "default_button",
                level=AtomicLevel.ADVANCED,
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.default_button.show",
                        expression="return $this.auto_check.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("dialog_result", types="DialogResult")],
    )
    def custom_box(
        box_title: str = "自定义对话框",
        design_interface: dict = None,
        auto_check: bool = False,
        wait_time: int = None,
        default_button: DefaultButtonCN = DefaultButtonCN.CONFIRM,
    ) -> DialogResult:
        exe_path = RpaTools.get_window_dir()
        if not os.path.exists(exe_path):
            raise BaseException(EXE_EMPTY_FORMAT.format(exe_path), "可执行窗口路径不存在,请检查路径信息")

        if auto_check and not wait_time:
            if wait_time == 0:
                auto_check = False
            else:
                wait_time = 60

        data = {
            "key": "Dialog.custom_box",
            "box_title": box_title,
            "design_interface": json.dumps(design_interface.get("value"), ensure_ascii=False),
            "result_button": default_button.value,
            "outputkey": "dialog_result",
        }
        encoded_data = json.dumps(data)
        chunk_size = 4096

        args = [exe_path, "--url=tauri://localhost/userform.html"]  # 不传递数据

        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,  # 开启管道
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        begin_signal = "BIG_DATA_SEND"
        while True:
            line = process.stdout.readline().strip()
            if line:
                if begin_signal in line:
                    break  # 退出循环，开始发送数据
            time.sleep(0.1)  # 避免忙等待

        # 分块传输数据
        process.stdin.write("option_start\n")
        process.stdin.flush()
        time.sleep(0.1)
        for i in range(0, len(encoded_data), chunk_size):
            chunk = encoded_data[i : i + chunk_size]
            process.stdin.write(chunk)  # 需要decode变成string给text=True的管道
            process.stdin.flush()  # 强制刷新缓冲区，确保数据被发送
        time.sleep(0.1)
        process.stdin.write("\n")
        process.stdin.write("option_end\n")
        process.stdin.flush()

        process.stdin.close()  # 关闭输入流，通知子进程数据传输完成

        output_list = []
        thread = threading.Thread(target=DialogCore.read_output, args=(process, output_list))
        thread.start()

        last_position = DialogCore.get_mouse_position()
        start_time = time.time()
        dialog_result = {}

        from pynput import keyboard, mouse

        def on_move(x, y):
            nonlocal auto_check
            if auto_check:
                print("用户干预：鼠标移动，停止自动检查")
                auto_check = False

        def on_click(x, y, button, pressed):
            nonlocal auto_check
            if auto_check:
                print("用户干预：鼠标点击，停止自动检查")
                auto_check = False

        def on_press(key):
            nonlocal auto_check
            if auto_check:
                print("用户干预：键盘按下，停止自动检查")
                auto_check = False

        def on_release(key):
            # 监听esc按键，按下之后结束监听
            nonlocal auto_check
            if auto_check:
                if key == keyboard.Key.esc:
                    print("用户手动结束监听")
                    auto_check = False

        if auto_check:  # Only start the listener if autocheck is enabled
            mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move)
            keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

            mouse_listener.start()
            keyboard_listener.start()

        while True:
            if auto_check:
                cur_position = DialogCore.get_mouse_position()
                if cur_position != last_position:
                    auto_check = False
            if auto_check and time.time() - start_time > wait_time:
                print("kill")
                break

            if output_list:
                output = output_list.pop(0)
                save_str = output.strip()

            if process.poll() is not None:
                break

            try:
                dialog_result = json.loads(save_str)
            except Exception as error:
                pass
        try:
            process.kill()
        except Exception:
            pass

        if not dialog_result and auto_check:
            if design_interface.get("value").get("table_required"):
                dialog_result["result_button"] = DefaultButtonCN.CANCEL.value
            else:
                dialog_result["result_button"] = DefaultButtonCN.CONFIRM.value

        return dialog_result
