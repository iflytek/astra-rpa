import random
import subprocess
import time

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpagui import KeyboardType, KeyModel, Simulate_flag
from rpagui.code.clipboard import Clipboard
from rpagui.code.keyboard import Keyboard
from rpagui.error import *

# 定义输入法的语言代码
ENGLISH = 0x0409  # 英文（美国）
CHINESE = 0x0804  # 中文（简体，中国）


class GuiKeyBoard:
    @staticmethod
    @atomicMg.atomic(
        "Gui",
        inputList=[
            atomicMg.param(
                "message",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.message.show",
                        expression="return ['{}', '{}', '{}'].includes($this.keyboard_type.value)".format(
                            KeyboardType.NORMAL.value,
                            KeyboardType.DRIVER.value,
                            KeyboardType.GBLID.value,
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "simulate_flag",
                dynamics=[
                    DynamicsItem(
                        key="$this.simulate_flag.show",
                        expression="return $this.keyboard_type.value == '{}'".format(KeyboardType.NORMAL.value),
                    )
                ],
            ),
            atomicMg.param(
                "interval",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.interval.show",
                        expression="return ['{}', '{}'].includes($this.keyboard_type.value)".format(
                            KeyboardType.NORMAL.value, KeyboardType.DRIVER.value
                        ),
                    )
                ],
            ),
        ],
    )
    def keyboard(
        keyboard_type: KeyboardType = KeyboardType.NORMAL,
        message: str = "",
        simulate_flag: Simulate_flag = Simulate_flag.NO,
        interval: float = 0.1,
    ):
        """
        键盘输入
        """
        if keyboard_type == KeyboardType.NORMAL:
            message = str(message)
            if simulate_flag == Simulate_flag.YES:
                Keyboard.change_language(ENGLISH)
                for char in message:
                    random_num = random.uniform(0, interval)
                    Keyboard.write_char(char)
                    time.sleep(random_num)
                Keyboard.change_language(CHINESE)
            elif simulate_flag == Simulate_flag.NO:
                Keyboard.change_language(ENGLISH)
                for char in message:
                    Keyboard.write_char(char)
                    time.sleep(interval)
                Keyboard.change_language(CHINESE)
            else:
                raise NotImplementedError()
        elif keyboard_type == KeyboardType.CLIP:
            msg = Clipboard.paste()
            if not msg:
                raise BaseException(CLIP_PASTE_ERROR, "Clip is empty.")
            else:
                Keyboard.hotkey("ctrl", "v")
                Clipboard.clear()
        elif keyboard_type == KeyboardType.DRIVER:
            if message == "":
                raise BaseException(KEYBOARD_MSG_ERROR, "输入内容为空，请检查输入内容")

            file_path = Keyboard.get_drive_path()
            cmd = [file_path, message, f"{interval}"]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                raise BaseException(DRIVE_INPUT_ERROR, "键盘驱动输入没有管理员权限")
        elif keyboard_type == KeyboardType.GBLID:
            from rpagui.code import ghostbox as gb

            device = gb.opendevicebyid(0x5188, 0x1801)
            is_connected = gb.isconnected()
            if not device or not is_connected:
                raise BaseException(GHOST_DRIVE_ERROR, "设备不存在或未连接,请检查设备连接")
            if message == "":
                raise BaseException(KEYBOARD_MSG_ERROR, "输入内容为空，请检查输入内容")
            try:
                Keyboard.change_language(ENGLISH)
                gb.inputstring(message)
                Keyboard.change_language(CHINESE)
            except Exception as e:
                raise BaseException(DRIVE_INPUT_ERROR, "键盘驱动输入错误")
            finally:
                gb.closedevice()

        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "Gui",
        inputList=[
            atomicMg.param(
                "keys_str",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.KEYBOARD.value),
            ),
        ],
    )
    def key_input(keys_str: str = "", key_model: KeyModel = KeyModel.CLICK):
        try:
            keys_str = keys_str.replace("ArrowLeft", "left")
            keys_str = keys_str.replace("ArrowRight", "right")
            keys_str = keys_str.replace("ArrowUp", "up")
            keys_str = keys_str.replace("ArrowDown", "down")
            key_list = []
            for k in keys_str.split("+"):
                key_list.append(k.strip())
            if key_model == KeyModel.CLICK:
                Keyboard.hotkey(*key_list)
            elif key_model == KeyModel.DOWN:
                for key in key_list:
                    Keyboard.key_down(key)
            elif key_model == KeyModel.UP:
                for key in key_list:
                    Keyboard.key_up(key)
            else:
                raise NotImplementedError()
        except Exception as e:
            raise BaseException(KEY_INPUT_ERROR, "模拟键盘按键输入错误")
