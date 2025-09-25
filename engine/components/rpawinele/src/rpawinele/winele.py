import os

import pyautogui
from locator import PickerDomain, Point
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import WinPick
from rpaatomic.utils import FileExistenceType, handle_existence
from rpawinele import (
    ElementInputType,
    MouseClickButton,
    MouseClickKeyboard,
    MouseClickType,
)
from rpawinele.core import IWinEleCore
from rpawinele.core_win import WinEleCore
from rpawinele.error import *

WinEleCore: IWinEleCore = WinEleCore()


class WinEle:
    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
    )
    def click_element(
        pick: WinPick,
        click_button: MouseClickButton = MouseClickButton.LEFT,
        click_type: MouseClickType = MouseClickType.CLICK,
        wait_time: float = 10.0,
        horizontals_offset=0,
        verticals_offset=0,
        keyboard_input: MouseClickKeyboard = MouseClickKeyboard.NONE,
    ):
        locator = WinEleCore.find(pick, wait_time)
        point = locator.point()

        # 按下辅助按键
        if keyboard_input != MouseClickKeyboard.NONE:
            pyautogui.keyDown(keyboard_input.value)
        try:
            locator.move(Point(point.x + horizontals_offset, point.y + verticals_offset))
            pyautogui.click(
                clicks=1 if click_type == MouseClickType.CLICK else 2,
                button=click_button.value,
            )
        except Exception as e:
            raise e
        finally:
            # 记得释放
            if keyboard_input != MouseClickKeyboard.NONE:
                pyautogui.keyUp(keyboard_input.value)

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
    )
    def screenshot_element(
        pick: WinPick,
        file_path: str,
        file_name: str = "桌面元素截图",
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        if not file_name.endswith(".png"):
            file_name += ".png"

        new_file_path = handle_existence(os.path.join(file_path, file_name), exist_type)
        if not new_file_path:
            raise BaseException(PATH_ERROR, "拾取或保存路径有误")

        locator = WinEleCore.find(pick=pick)
        window_rect = locator.rect()
        rect = (
            window_rect.left,
            window_rect.top,
            window_rect.width(),
            window_rect.height(),
        )
        screenshot = pyautogui.screenshot(region=rect)
        screenshot.save(new_file_path)

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
    )
    def hover_element(pick: WinPick, wait_time: float = 10.0):
        locator = WinEleCore.find(pick, wait_time)
        locator.hover()

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
            atomicMg.param(
                "text",
                dynamics=[
                    DynamicsItem(
                        key="$this.text.show",
                        expression="return $this.input_type.value == '{}'".format(ElementInputType.KEYBOARD.value),
                    )
                ],
            ),
        ],
    )
    def input_text_element(
        pick: WinPick,
        input_type: ElementInputType = ElementInputType.KEYBOARD,
        text: str = "",
        clear_first: bool = True,
        wait_time: float = 10.0,
    ):
        if pick.get("type", None) not in [PickerDomain.UIA.value]:
            raise BaseException(UNPICKABLE, "类型不支持{}".format(pick.get("type", None)))

        locator = WinEleCore.find(pick, wait_time)
        locator.move()
        pyautogui.click()

        import uiautomation

        if clear_first:
            window_control = locator.control()
            if window_control.ControlTypeName == uiautomation.EditControl.ControlTypeName:
                window_control.GetValuePattern().SetValue("")
            else:
                pyautogui.press("home")
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("delete")
        else:
            pyautogui.press("end")

        if input_type == ElementInputType.KEYBOARD:
            uiautomation.SendKeys(text)
        elif input_type == ElementInputType.CLIPBOARD:
            pyautogui.hotkey("ctrl", "v")

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        inputList=[
            atomicMg.param(
                "pick",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "ELEMENT"}),
            ),
        ],
        outputList=[atomicMg.param("ele_text", types="Str")],
    )
    def get_element_text(pick: WinPick, wait_time: float = 10.0):
        locator = WinEleCore.find(pick, wait_time)
        return locator.control().Name

    @staticmethod
    @atomicMg.atomic(
        "WinEle",
        outputList=[
            atomicMg.param("get_similar_ele", types="List"),
        ],
    )
    def similar(pick: WinPick, wait_time: int = 10) -> list:
        if pick.get("type", None) not in [PickerDomain.UIA.value]:
            raise BaseException(UNPICKABLE, "类型不支持{}".format(pick.get("type", None)))

        locator_list = WinEleCore.find(pick, wait_time)
        res_list = []
        if locator_list:
            if not isinstance(locator_list, list):
                locator_list = [locator_list]
            for locator in locator_list:
                win_pick = WinPick()
                win_pick.locator = locator
                res_list.append(win_pick)
        return res_list
