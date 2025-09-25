"""浏览器元素操作模块，提供网页元素的各种操作功能。"""

import base64
import json
import os
import platform
import sys
import time
from functools import wraps

import pandas as pd
from rpa_table_helper.table_filter import (
    DataFilter,
    page_values_merge,
    table_df_to_out,
    table_json_merge_values,
)
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH, WebPick
from rpaframe.logger.logger import logger
from rpagui.code.screenshot import Screenshot

from rpabrowser import (
    ALL_BROWSER_TYPES,
    CHROME_LIKE_BROWSERS,
    ButtonForAssistiveKeyFlag,
    ButtonForClickTypeFlag,
    ChildElementType,
    ElementAttributeOpTypeFlag,
    ElementCheckedTypeFlag,
    ElementDragDirectionTypeFlag,
    ElementDragTypeFlag,
    ElementGetAttributeHasSelfTypeFlag,
    ElementGetAttributeTypeFlag,
    FillInputForFillTypeFlag,
    FillInputForInputTypeFlag,
    LocateType,
    RelativePosition,
    RelativeType,
    ScrollbarForXScrollTypeFlag,
    ScrollbarForYScrollTypeFlag,
    ScrollbarType,
    ScrollDirection,
    SelectionPartner,
    SiblingElementType,
    TablePickType,
    WaitElementForStatusFlag,
)
from rpabrowser.browser import Browser
from rpabrowser.core.core import IBrowserCore
from rpabrowser.error import (
    CODE_EMPTY,
    FOCUS_TIMEOUT_MUST_BE_POSITIVE,
    KEY_PRESS_INTERVAL_MUST_BE_NON_NEGATIVE,
    PARAMETER_INVALID_FORMAT,
    BaseException,
    WEB_GET_ElE_ERROR,
)
from rpabrowser.js.base import BaseBuilder
from rpabrowser.js.chrome import CodeChromeBuilder

if sys.platform == "win32":
    from locator import smooth_move
    from locator.locator import locator

    from rpabrowser.core.core_win import BrowserCore
elif platform.system() == "Linux":
    from locator_linux import smooth_move
    from locator_linux.locator import locator

    from rpabrowser.core.core_unix import BrowserCore
else:
    raise NotImplementedError(f"Your platform ({platform.system()}) is not supported by clipboard.")

BrowserCore: IBrowserCore = BrowserCore()
CodeChromeBuilder: BaseBuilder = CodeChromeBuilder()
Locator = locator


def get_browser_instance():
    """获取可用的浏览器实例。"""
    browser_instance = Browser()
    browser_found = False
    for browser_type in ALL_BROWSER_TYPES:
        handler = None
        open_timeout = 10
        start_time = time.time()
        while time.time() - start_time < open_timeout:
            handler = BrowserCore.get_browser_handler(browser_type)
            if handler:
                break
            time.sleep(1)
        if not handler:
            continue

        browser_found = True
        browser_instance.browser_type = browser_type
        if browser_type in CHROME_LIKE_BROWSERS:
            from rpawindow import WindowSizeType
            from rpawindow.window import WindowsCore

            WindowsCore.top(handler)
            WindowsCore.size(handler, WindowSizeType.MAX)
        else:
            raise NotImplementedError()
        break
    return browser_instance if browser_found else None


def get_default_browser(func):
    """装饰器：为函数提供默认的浏览器对象。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        new_kwargs = kwargs.copy()
        if not new_kwargs or not new_kwargs["browser_obj"]:
            browser_instance = get_browser_instance()
            if browser_instance:
                new_kwargs["browser_obj"] = browser_instance
            else:
                new_kwargs["browser_obj"] = None
        return func(*args, **new_kwargs)

    return wrapper


def wait_element_appear(func):
    """等待元素加载出来"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        new_kwargs = kwargs.copy()
        timeout = new_kwargs.get("element_timeout", None)
        browser_obj = new_kwargs.get("browser_obj", None)
        element_data = new_kwargs.get("element_data", None)
        if timeout and browser_obj and element_data:
            ret = BrowserElement.wait_element(
                browser_obj=browser_obj,
                element_data=element_data,
                ele_status=WaitElementForStatusFlag.ElementExists,
                element_timeout=int(timeout),
            )
            if not ret:
                if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                    reason = browser_obj.send_browser_extension(
                        browser_type=browser_obj.browser_type.value,
                        key="checkElement",
                        data=element_data["elementData"]["path"],
                    )
                    raise BaseException(WEB_GET_ElE_ERROR.format(reason.msg), "浏览器元素未找到！")
                else:
                    raise BaseException(WEB_GET_ElE_ERROR.format(""), "浏览器元素未找到！")
        return func(*args, **new_kwargs)

    return wrapper


def extract_element_path_data(element_data):
    """提取 element_data['elementData']['path'] 的属性"""
    path_data = element_data["elementData"]["path"]
    return extract_path_attributes(path_data)


def extract_path_attributes(path_data):
    """提取 path_data 的属性"""
    return {
        "xpath": path_data.get("xpath", ""),
        "cssSelector": path_data.get("cssSelector", ""),
        "pathDirs": repr(json.dumps(path_data.get("pathDirs", []), ensure_ascii=False)),
        "checkType": path_data.get("checkType", ""),
        "shadowRoot": path_data.get("shadowRoot", False),
        "matchTypes": json.dumps(path_data.get("matchTypes", []), ensure_ascii=False),
        "url": path_data.get("url", ""),
        "isFrame": path_data.get("isFrame", False),
        "iframeXpath": path_data.get("iframeXpath", ""),
    }


class BrowserElement:
    """浏览器元素操作类，提供网页元素的各种操作方法。"""

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        outputList=[
            atomicMg.param("wait_element", types="Bool"),
        ],
    )
    def wait_element(
        browser_obj: Browser,
        element_data: WebPick,
        ele_status: WaitElementForStatusFlag = WaitElementForStatusFlag.ElementExists,
        element_timeout: int = 10,
    ) -> bool:
        """等待元素出现或消失。"""
        app = element_data["elementData"]["app"] if element_data["elementData"]["app"] != "iexplore" else "ie"
        if app != browser_obj.browser_type.value:
            raise Exception(
                f"拾取元素类型需要跟浏览器类型保持一致！当前操作的浏览器为！{browser_obj.browser_type.value}"
            )
        timeout = element_timeout
        if timeout < 0:
            raise BaseException(
                PARAMETER_INVALID_FORMAT.format(timeout),
                f"等待时间不能小于0！{timeout}",
            )
        while timeout >= 0:
            start = time.time()

            # 获取状态
            try:
                if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                    element_exist = browser_obj.send_browser_extension(
                        browser_type=browser_obj.browser_type.value,
                        key="elementIsReady",
                        data=element_data["elementData"]["path"],
                    )
                else:
                    raise NotImplementedError()
            except Exception:
                element_exist = None

            # 判断是否提前结束
            if ele_status == WaitElementForStatusFlag.ElementExists and element_exist:
                return True
            elif ele_status == WaitElementForStatusFlag.ElementDisappears and not element_exist:
                return True
            else:
                # 重试
                time.sleep(0.3)
                use = time.time() - start
                timeout -= use
        return False

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param("simulate_flag", required=False),
            atomicMg.param(
                "assistive_key",
                dynamics=[
                    DynamicsItem(
                        key="$this.assistive_key.show",
                        expression="return $this.simulate_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "button_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
        ],
    )
    @wait_element_appear
    def click(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        simulate_flag: bool = False,
        assistive_key: ButtonForAssistiveKeyFlag = ButtonForAssistiveKeyFlag.Nothing,
        button_type: ButtonForClickTypeFlag = ButtonForClickTypeFlag.Left,
        element_timeout: int = 10,
    ):
        """点击"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        from rpagui.code.keyboard import Keyboard
        from rpagui.code.mouse import Mouse

        element = Locator.locator(element_data.get("elementData"))
        center = element.point()
        if assistive_key != ButtonForAssistiveKeyFlag.Nothing:
            Keyboard.key_down(assistive_key.value)

        if not simulate_flag:
            if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                # 发送给插件
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="clickElement",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {"buttonType": button_type.value},
                    },
                )
            else:
                raise NotImplementedError()

        else:
            smooth_move(center.x, center.y, duration=0.5)
            Mouse.click(
                x=center.x,
                y=center.y,
                clicks=2 if button_type == ButtonForClickTypeFlag.Double else 1,
                button=("left" if button_type != ButtonForClickTypeFlag.Right else "right"),
            )
        if assistive_key != ButtonForAssistiveKeyFlag.Nothing:
            Keyboard.key_up(assistive_key.value)

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param("simulate_flag", required=False),
            atomicMg.param(
                "focus_time",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.focus_time.show",
                        expression="return $this.simulate_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "fill_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            atomicMg.param(
                "write_gap_time",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.write_gap_time.show",
                        expression="return $this.simulate_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "fill_input",
                dynamics=[
                    DynamicsItem(
                        key="$this.fill_input.show",
                        expression=f"return $this.fill_type.value == '{FillInputForFillTypeFlag.Text.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "input_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
        ],
        outputList=[
            atomicMg.param("form_input", types="Str"),
        ],
    )
    @wait_element_appear
    def input(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        simulate_flag: bool = False,
        fill_type: FillInputForFillTypeFlag = FillInputForFillTypeFlag.Text,
        fill_input: str = "",
        element_timeout: int = 10,
        focus_time: float = 1000,
        write_gap_time: float = 0,
        input_type: FillInputForInputTypeFlag = FillInputForInputTypeFlag.Overwrite,
    ):
        """
        填写输入框(web)
        """
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if fill_type == FillInputForFillTypeFlag.Text:
            text = fill_input
        elif fill_type == FillInputForFillTypeFlag.Clipboard:
            from rpagui.code.clipboard import Clipboard

            text = Clipboard.paste()
        else:
            text = ""

        element = Locator.locator(element_data.get("elementData"))
        center = element.point()

        # js输入
        if not simulate_flag:
            if input_type == FillInputForInputTypeFlag.Append:
                origin_text = BrowserElement.element_text(
                    browser_obj=browser_obj,
                    element_data=element_data,
                    element_timeout=10,
                )
                if origin_text:
                    text = str(origin_text) + str(text)

            if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="inputElement",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {"inputText": text},
                    },
                )
            else:
                raise NotImplementedError()

        else:
            from rpagui.code.keyboard import Keyboard
            from rpagui.code.mouse import Mouse

            smooth_move(center.x, center.y, duration=0.4)
            Mouse.click(x=center.x, y=center.y)
            if input_type == FillInputForInputTypeFlag.Overwrite:
                # 覆盖输入
                Keyboard.hotkey("ctrl", "a")
                time.sleep(0.5)
                Keyboard.press("delete")
                time.sleep(0.5)
            # 焦点睡眠时间
            if focus_time < 0:
                raise BaseException(FOCUS_TIMEOUT_MUST_BE_POSITIVE, "焦点超时时间必须大于0")
            time.sleep(focus_time / 1000)
            if write_gap_time < 0:
                raise BaseException(KEY_PRESS_INTERVAL_MUST_BE_NON_NEGATIVE, "按键输入间隔必须大于等于0")
            write_gap_time = write_gap_time if write_gap_time > 0 else 0.03
            if fill_type == FillInputForFillTypeFlag.Text:
                for item in text:
                    Keyboard.write_char(item)
                    # pyautogui.write(item)
                    time.sleep(write_gap_time)
            elif fill_type == FillInputForFillTypeFlag.Clipboard:
                Clipboard.copy(data=text)
                Keyboard.hotkey("ctrl", "v")
        return text

    @staticmethod
    @get_default_browser
    @atomicMg.atomic("BrowserElement")
    @wait_element_appear
    def hover_over(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        element_timeout: int = 10,
    ):
        """
        鼠标悬停在元素上（web）
        """
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        element = Locator.locator(element_data.get("elementData"))
        element.move()

    @staticmethod
    @wait_element_appear
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("xpath_shot", types="Str"),
        ],
    )
    def screenshot(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        file_path: PATH = None,
        image_name: str = "",
        element_timeout: int = 10,
    ):
        """截图"""

        if not image_name.endswith((".png", ".jpg", ".jpeg")):
            image_name += ".jpg"
        path = os.path.join(file_path, image_name)
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="elementShot",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                },
                timeout=30,
            )
            if data:
                data = data.replace("data:image/jpeg;base64,", "")
            else:
                raise Exception("插件返回数据为空")
            with open(path, "wb") as f:
                f.write(base64.b64decode(data))
        else:
            element = Locator.locator(element_data.get("elementData"))
            rect = element.rect()
            from rpagui.code.screenshot import Screenshot

            Screenshot.screenshot(
                region=(rect.left, rect.top, rect.width(), rect.height()),
                file_path=path,
            )
        return path

    @staticmethod
    @wait_element_appear
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("position_shot", types="Str"),
        ],
    )
    def position_screenshot(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        file_path: PATH = None,
        image_name: str = "",
        element_timeout: int = 10,
    ):
        """元素位置截图"""
        if not image_name.endswith((".png", ".jpg", ".jpeg")):
            image_name += ".jpg"
        path = os.path.join(file_path, image_name)
        element = Locator.locator(element_data.get("elementData"))
        rect = element.rect()

        Screenshot.screenshot(region=(rect.left, rect.top, rect.width(), rect.height()), file_path=path)
        return path

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "scrollbar_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            atomicMg.param(
                "element_data",
                dynamics=[
                    DynamicsItem(
                        key="$this.element_data.show",
                        expression=f"return $this.scrollbar_type.value == '{ScrollbarType.CustomEle.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "element_timeout",
                dynamics=[
                    DynamicsItem(
                        key="$this.element_timeout.show",
                        expression=f"return $this.scrollbar_type.value == '{ScrollbarType.CustomEle.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "x_scroll_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.x_scroll_type.show",
                        expression=f"return $this.scroll_direction.value == '{ScrollDirection.Horizontal.value}'",
                    )
                ],
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            atomicMg.param(
                "y_scroll_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.y_scroll_type.show",
                        expression=f"return $this.scroll_direction.value == '{ScrollDirection.Vertical.value}'",
                    )
                ],
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            atomicMg.param(
                "x_custom_scroll_dis",
                dynamics=[
                    DynamicsItem(
                        key="$this.x_custom_scroll_dis.show",
                        expression=f"return $this.scroll_direction.value == '{ScrollDirection.Horizontal.value}' && $this.x_scroll_type.value == '{ScrollbarForXScrollTypeFlag.Defined.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "y_custom_scroll_dis",
                dynamics=[
                    DynamicsItem(
                        key="$this.y_custom_scroll_dis.show",
                        expression=f"return $this.scroll_direction.value == '{ScrollDirection.Vertical.value}' && $this.y_scroll_type.value == '{ScrollbarForYScrollTypeFlag.Defined.value}'",
                    )
                ],
            ),
        ],
    )
    @wait_element_appear
    def scroll(
        browser_obj: Browser = None,
        scrollbar_type: ScrollbarType = ScrollbarType.Window,
        element_data: WebPick = None,
        scroll_direction: ScrollDirection = ScrollDirection.Horizontal,
        x_scroll_type: ScrollbarForXScrollTypeFlag = ScrollbarForXScrollTypeFlag.Left,
        x_custom_scroll_dis: int = 0,
        y_scroll_type: ScrollbarForYScrollTypeFlag = ScrollbarForYScrollTypeFlag.Top,
        y_custom_scroll_dis: int = 0,
        element_timeout: int = 10,
    ):
        """滚动操作。"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            scroll_distance_x = ""
            scroll_distance_y = ""
            scroll_to = "top"
            scroll_axis = "y"
            if scroll_direction == ScrollDirection.Vertical:
                if y_scroll_type == ScrollbarForYScrollTypeFlag.Defined:
                    scroll_distance_y = y_custom_scroll_dis
                    scroll_to = "custom"
                elif y_scroll_type == ScrollbarForYScrollTypeFlag.Bottom:
                    scroll_distance_y = 99999
                    scroll_to = "bottom"
            else:
                scroll_to = "left"
                scroll_axis = "x"
                if x_scroll_type == ScrollbarForXScrollTypeFlag.Defined:
                    scroll_distance_x = x_custom_scroll_dis
                    scroll_to = "custom"
                elif x_scroll_type == ScrollbarForXScrollTypeFlag.Right:
                    scroll_distance_x = 99999
                    scroll_to = "right"

            if scrollbar_type == ScrollbarType.Window:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="scrollWindow",
                    data={
                        "atomConfig": {
                            "scrollX": scroll_distance_x,
                            "scrollY": scroll_distance_y,
                            "scrollBehavior": "auto",
                            "scrollTo": scroll_to,
                            "scrollAxis": scroll_axis,
                        }
                    },
                )
            else:
                # 自定义滚动条
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="scrollWindow",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {
                            "scrollX": scroll_distance_x,
                            "scrollY": scroll_distance_y,
                            "scrollBehavior": "auto",
                            "scrollTo": scroll_to,
                            "scrollAxis": scroll_axis,
                        },
                    },
                )
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic("BrowserElement")
    @wait_element_appear
    def scroll_into_view(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        element_timeout: int = 10,
    ):
        """滚动到元素可见位置。"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            _ = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="scrollIntoView",
                data=element_data["elementData"]["path"],
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "attribute_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.attribute_name.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeHasSelfTypeFlag.GetAttribute.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("get_similar_ele", types="List"),
        ],
    )
    @wait_element_appear
    def similar(
        browser_obj: Browser,
        element_data: WebPick,
        get_type: ElementGetAttributeHasSelfTypeFlag = ElementGetAttributeHasSelfTypeFlag.GetElement,
        attribute_name: str = "",
        element_timeout: int = 10,
    ) -> list:
        """
        获取相似元素列表
        """
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            # 获取相似元素的信息
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="elementFromSelect",
                data=element_data["elementData"]["path"],
            )
            # 遍历相似元素，将结果放入list
            if get_type == ElementGetAttributeHasSelfTypeFlag.GetElement:
                res_list = []
                for di in data:
                    res_list.append(
                        {
                            "elementData": {
                                "version": element_data["elementData"]["version"],
                                "type": element_data["elementData"]["type"],
                                "app": element_data["elementData"]["app"],
                                "picker_type": "ELEMENT",
                                "path": di,
                            }
                        }
                    )
                return res_list

            res_list = []
            for di in data:
                data = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="getElementAttrs",
                    data={
                        **di,  # 解包内部字典的内容
                        "atomConfig": {
                            "operation": str(list(ElementGetAttributeHasSelfTypeFlag).index(get_type) - 1),
                            "attrName": attribute_name,
                        },
                    },
                )
                res_list.append(data)
            return res_list
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        noAdvanced=True,
        inputList=[
            atomicMg.param(
                "attribute_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.attribute_name.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeHasSelfTypeFlag.GetAttribute.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("index", types="Int"),
            atomicMg.param("item", types="Any"),
        ],
    )
    @wait_element_appear
    def loop_similar(
        browser_obj: Browser,
        element_data: WebPick,
        get_type: ElementGetAttributeHasSelfTypeFlag = ElementGetAttributeHasSelfTypeFlag.GetElement,
        start: int = 0,
        end: int = -1,
        attribute_name: str = "",
        element_timeout: int = 10,
    ):
        """循环相似元素"""
        # 获取相似元素的信息
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:

            def get_iterator():
                count = 0
                similar_count = 0
                batch_size = 20
                while True:
                    data = browser_obj.send_browser_extension(
                        browser_type=browser_obj.browser_type.value,
                        key="getSimilarIterator",
                        data={
                            **element_data["elementData"]["path"],  # 解包内部字典的内容
                            "index": count,
                            "count": batch_size,
                        },
                    )
                    similar_count = data[0]["similarCount"]
                    if not data or len(data) <= 0:
                        break
                    for di in data:
                        if count < start:
                            count += 1
                            continue
                        if 0 < end <= count:
                            return
                        count += 1
                        if get_type == ElementGetAttributeHasSelfTypeFlag.GetElement:
                            di_wrapper = {
                                "elementData": {
                                    "version": element_data["elementData"]["version"],
                                    "type": element_data["elementData"]["type"],
                                    "app": element_data["elementData"]["app"],
                                    "picker_type": "ELEMENT",
                                    "path": di,
                                }
                            }
                            yield di_wrapper
                            continue

                        data = browser_obj.send_browser_extension(
                            browser_type=browser_obj.browser_type.value,
                            key="getElementAttrs",
                            data={
                                **di,  # 解包内部字典的内容
                                "atomConfig": {
                                    "operation": str(list(ElementGetAttributeHasSelfTypeFlag).index(get_type) - 1),
                                    "attrName": attribute_name,
                                },
                            },
                        )

                        yield data
                    if similar_count <= count:
                        break

            return get_iterator()
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        outputList=[
            atomicMg.param("data_pick", types="Str"),
        ],
    )
    @wait_element_appear
    def element_text(browser_obj: Browser, element_data: WebPick, element_timeout: int = 10) -> str:
        """
        获取元素文本内容
        """
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            handler = BrowserCore.get_browser_handler(browser_obj.browser_type)

            return browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getElementText",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                },
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic("BrowserElement")
    def slider_hover(
        browser_obj: Browser = None,
        slider_element: WebPick = None,
        progress_element: WebPick = None,
        percent_value: float = 0.0,
        drag_direction: ElementDragDirectionTypeFlag = ElementDragDirectionTypeFlag.Left,
        drag_type: ElementDragTypeFlag = ElementDragTypeFlag.Start,
        duration: float = 0.25,
    ):
        """滑块"""
        from rpagui.code.mouse import Mouse

        def html_drag(start_pos, end_pos, duration):
            """
            指定起始坐标以及结束坐标进行拖拽操作
            """
            smooth_move(start_pos[0], start_pos[1], duration=0.05)
            Mouse.down(x=start_pos[0], y=start_pos[1], button="left")
            logger.info(f"slider_hover start {start_pos}  end {end_pos}")
            smooth_move(end_pos[0], end_pos[1], duration=duration)
            time.sleep(0.05)
            Mouse.up(x=end_pos[0], y=end_pos[1], button="left")  # 在结束位置释放鼠标按钮
            time.sleep(0.05)

        percent_value = max(0.0, min(1.0, percent_value / 100))
        # 定位滑块和滑条元素
        # 滑块（要拖动的元素）
        element = Locator.locator(slider_element.get("elementData"))
        slider_center = element.point()

        # 滑条（滑块可移动的轨道）
        element = Locator.locator(progress_element.get("elementData"), scroll_into_view=False)
        progress_rect = element.rect()

        # 计算滑条的尺寸和位置
        progress_left = progress_rect.left
        progress_top = progress_rect.top
        progress_width = progress_rect.right - progress_rect.left
        progress_height = progress_rect.bottom - progress_rect.top

        # 记录滑块初始位置
        start_pos = [slider_center.x, slider_center.y]
        logger.info(f"滑块中心点: {start_pos}")
        logger.info(f"滑条位置和尺寸: [{progress_left}, {progress_top}, {progress_width}, {progress_height}]")

        # 根据拖拽方向判断是横向还是纵向
        is_horizontal = drag_direction in [
            ElementDragDirectionTypeFlag.Left,
            ElementDragDirectionTypeFlag.Right,
        ]
        logger.info(f"滑动方向: {'横向' if is_horizontal else '纵向'}, 具体方向: {drag_direction.value}")

        # 计算终点位置
        if is_horizontal:
            # 横向滑块
            if drag_type == ElementDragTypeFlag.Start:  # 从起点模式
                if drag_direction == ElementDragDirectionTypeFlag.Right:
                    # 向右滑动，直接使用百分比
                    target_x = progress_left + (progress_width * percent_value)
                else:  # 向左滑动
                    # 使用反向百分比（1-percent_value）
                    target_x = progress_left + (progress_width * (1 - percent_value))
                end_pos = [int(target_x), int(slider_center.y)]
            else:  # 相对当前位置模式
                # 计算移动距离
                move_distance = progress_width * percent_value
                if drag_direction == ElementDragDirectionTypeFlag.Left:
                    move_distance = -move_distance
                # 计算目标位置
                target_x = slider_center.x + move_distance
                # 确保不超出滑条范围
                target_x = max(progress_left, min(progress_left + progress_width, target_x))
                end_pos = [int(target_x), int(slider_center.y)]
        else:
            # 纵向滑块
            if drag_type == ElementDragTypeFlag.Start:  # 从起点模式
                if drag_direction == ElementDragDirectionTypeFlag.Down:
                    # 向下滑动，直接使用百分比
                    target_y = progress_top + (progress_height * percent_value)
                else:  # 向上滑动
                    # 使用反向百分比（1-percent_value）
                    target_y = progress_top + (progress_height * (1 - percent_value))
                end_pos = [int(slider_center.x), int(target_y)]
            else:  # 相对当前位置模式
                # 计算移动距离
                move_distance = progress_height * percent_value
                if drag_direction == ElementDragDirectionTypeFlag.Up:
                    move_distance = -move_distance
                # 计算目标位置
                target_y = slider_center.y + move_distance
                # 确保不超出滑条范围
                target_y = max(progress_top, min(progress_top + progress_height, target_y))
                end_pos = [int(slider_center.x), int(target_y)]

        logger.info(f"计算的终点位置: {end_pos}")
        html_drag(start_pos, end_pos, duration)

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[atomicMg.param("current_content", required=False)],
        outputList=[
            atomicMg.param("get_selected", types="List"),
        ],
    )
    @wait_element_appear
    def get_select(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        current_content: bool = True,
        element_timeout: int = 10,
    ):
        """获取下拉框选中值。"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getElementSelected",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                    "atomConfig": {
                        "option": "selected" if current_content else "_",
                    },
                },
            )

        else:
            raise NotImplementedError()
        return data

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        outputList=[
            atomicMg.param("get_checkbox_checked", types="Str"),
        ],
    )
    @wait_element_appear
    def get_checked(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        element_timeout: int = 10,
    ):
        """获取复选框选中状态。"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getElementChecked",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                },
            )

        else:
            raise NotImplementedError()
        return data

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "value",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.value.show",
                        expression=f"return ['{SelectionPartner.Contains.value}', '{SelectionPartner.Equal.value}'].includes($this.pattern.value)",
                    )
                ],
            ),
            atomicMg.param(
                "solution",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.solution.show",
                        expression=f"return $this.pattern.value == '{SelectionPartner.Index.value}'",
                    )
                ],
            ),
        ],
    )
    @wait_element_appear
    def set_select(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        pattern: SelectionPartner = SelectionPartner.Contains,
        value: str = "",
        solution: int = 0,
        element_timeout: int = 10,
    ):
        """设置下拉框选中值。"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            _ = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="setElementSelected",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                    "atomConfig": {
                        "value": value,
                        "pattern": pattern.value,
                        "indexValue": solution,
                    },
                },
            )

        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic("BrowserElement")
    @wait_element_appear
    def set_checked(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        checked_type: ElementCheckedTypeFlag = ElementCheckedTypeFlag.Checked,
        element_timeout: int = 10,
    ):
        """设置复选框选中状态。"""
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            _ = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="setElementChecked",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                    "atomConfig": {
                        "checked": checked_type == ElementCheckedTypeFlag.Checked,
                        "reverse": checked_type == ElementCheckedTypeFlag.Reversed,
                    },
                },
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "get_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_type.show",
                        expression=f"return $this.operation_type.value == '{ElementAttributeOpTypeFlag.Get.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "attribute_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.attribute_name.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetAttribute.value}' || ['{ElementAttributeOpTypeFlag.Set.value}', '{ElementAttributeOpTypeFlag.Del.value}'].includes($this.operation_type.value)",
                    )
                ],
            ),
            atomicMg.param(
                "position",
                dynamics=[
                    DynamicsItem(
                        key="$this.position.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetPosition.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "attribute_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.attribute_value.show",
                        expression=f"return $this.operation_type.value == '{ElementAttributeOpTypeFlag.Set.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param(
                "get_ele_attr",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_attr.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetAttribute.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_value",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_value.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetValue.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_html",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_html.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetHtml.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_link",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_link.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetLink.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_text",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_text.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetText.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_position",
                types="List",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_position.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetPosition.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "get_ele_selected",
                types="Bool",
                dynamics=[
                    DynamicsItem(
                        key="$this.get_ele_selected.show",
                        expression=f"return $this.get_type.value == '{ElementGetAttributeTypeFlag.GetSelection.value}'",
                    )
                ],
            ),
        ],
    )
    @wait_element_appear
    def element_operation(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        operation_type: ElementAttributeOpTypeFlag = ElementAttributeOpTypeFlag.Get,
        get_type: ElementGetAttributeTypeFlag = ElementGetAttributeTypeFlag.GetText,
        attribute_name: str = "",
        position: RelativePosition = RelativePosition.ScreenLeft,
        attribute_value: str = "",
        element_timeout: int = 10,
    ):
        """三个操作大类是候选，其他参数是候选出现后出现"""
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            if operation_type == ElementAttributeOpTypeFlag.Del:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="removeElementAttr",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {
                            "attrName": attribute_name,
                        },
                    },
                )
            elif operation_type == ElementAttributeOpTypeFlag.Get:
                data = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="getElementAttrs",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {
                            "attrName": attribute_name,
                            "operation": str(list(ElementGetAttributeTypeFlag).index(get_type)),
                        },
                    },
                )

                logger.info(f"获取元素属性: {data}")
                if get_type == ElementGetAttributeTypeFlag.GetPosition:
                    if position == RelativePosition.ScreenLeft:
                        top, left = BrowserCore.get_browser_point(browser_obj.browser_type)
                        return [
                            data["x"] + left,
                            data["y"] + top,
                            data["right"] + left,
                            data["bottom"] + top,
                        ]
                    # 返回的是列表
                    return [data["x"], data["y"], data["right"], data["bottom"]]
                else:
                    return data

            elif operation_type == ElementAttributeOpTypeFlag.Set:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="setElementAttr",
                    data={
                        **element_data["elementData"]["path"],  # 解包内部字典的内容
                        "atomConfig": {
                            "attrName": attribute_name,
                            "attrValue": attribute_value,
                        },
                    },
                )
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "excel_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.excel_path.show",
                        expression="return $this.to_excel.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("table_pick", types="List"),
        ],
    )
    @wait_element_appear
    def get_table(
        browser_obj: Browser,
        element_data: WebPick,
        to_excel: bool = False,  # 是否导出excel
        excel_path: str = None,  # excel路径
        element_timeout: int = 10,
    ):
        """
        获取表格内容
        """
        if not browser_obj:
            raise BaseException(
                PARAMETER_INVALID_FORMAT,
                "浏览器元素为空，请检查当前界面浏览器是否正常打开",
            )
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            handler = BrowserCore.get_browser_handler(browser_obj.browser_type)

            # 定位
            Locator.locator(element_data.get("elementData"))
            # 元素
            table_element = element_data["elementData"]

            table_data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getTableData",
                data={
                    **table_element["path"],  # 解包内部字典的内容
                },
            )
        else:
            raise NotImplementedError()

        # 判断table_data 存在 tbody
        if "tbody" in table_data:
            df = pd.DataFrame(table_data["tbody"])
            table_body = df.values.tolist()
            # 添加表头
            table_head = table_data["thead"]
            df.columns = table_data["thead"]
            table_list = table_body
            if to_excel:
                if excel_path is None:
                    excel_path = f"{table_element['name']}.xlsx"
                df.to_excel(excel_path, index=False)
            return [table_head] + table_list
        else:
            raise Exception(table_data["msg"])

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "batch_data",
                formType=AtomicFormTypeMeta(type=AtomicFormType.PICK.value, params={"use": "BATCH"}),
            ),
            # multi_page  为 True 时，page_element_data，page_count，page_interval参数必须存在
            atomicMg.param("multi_page", required=False),
            atomicMg.param(
                "page_count",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_count.show",
                        expression="return $this.multi_page.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "page_interval",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_interval.show",
                        expression="return $this.multi_page.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "element_data",
                dynamics=[
                    DynamicsItem(
                        key="$this.element_data.show",
                        expression="return $this.multi_page.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "simulate_flag",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.simulate_flag.show",
                        expression="return $this.multi_page.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "button_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            # to_excel 为 True 时，excel_path参数必须存在
            atomicMg.param(
                "excel_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.excel_path.show",
                        expression="return $this.to_excel.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".xlsx"],  # 在file_type为file有效 标识只要.txt的后缀文件
                        "defaultPath": "default.xlsx",  # 默认名称 只适用于 file
                    },
                ),
            ),
            atomicMg.param(
                "output_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RADIO.value),
            ),
            # 是否输出表头
            atomicMg.param("output_head", required=False),
        ],
        outputList=[
            atomicMg.param("table_pick", types="List"),
            atomicMg.param(
                "table_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.table_path.show",
                        expression="return $this.to_excel.value == true",
                    )
                ],
                types="Str",
            ),
        ],
    )
    @wait_element_appear
    def data_batch(
        browser_obj: Browser = None,  # 浏览器对象
        batch_data: WebPick = None,  # 批量抓取对象
        multi_page: bool = False,  # 是否翻页
        page_count: int = 1,  # 翻页次数
        page_interval: int = 1,  # 翻页间隔
        element_data: WebPick = None,  # 翻页按钮元素
        simulate_flag: bool = False,  # 翻页按钮元素模拟人工点击
        button_type: ButtonForClickTypeFlag = ButtonForClickTypeFlag.Left,
        to_excel: bool = False,  # 是否导出excel
        excel_path: str = None,  # excel路径
        element_timeout: int = 10,
        output_type: TablePickType = TablePickType.Row,
        output_head: bool = True,  # 是否输出表头
    ):
        """数据抓取（web）"""
        table_list = []
        batch_element = batch_data.get("elementData")  # 抓取对象
        table_element = batch_element["path"]  # 元素信息
        produce_type = table_element["produceType"]  # 抓取类型， produceType: table/similar
        for i in range(1, page_count + 1):
            # 获取表格内容, 二维数组
            if produce_type == "table":
                # 等待元素
                wait = BrowserElement.wait_element(
                    browser_obj=browser_obj,
                    element_data=batch_data,
                    ele_status=WaitElementForStatusFlag.ElementExists,
                    element_timeout=int(element_timeout),
                )
                if not wait:
                    raise BaseException(WEB_GET_ElE_ERROR.format("请检查抓取元素"), "浏览器元素未找到！")
                # 定位
                Locator.locator(batch_element)
                # 发送给插件
                response = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="tableDataBatch",
                    data=table_element,
                )
                # 打印 response
                # logger.info(f'table_element response: {response}')
                table_values = response["values"]
                table_list = page_values_merge(table_list, table_values, produce_type)
            else:
                # 相似元素对象
                similar_element = batch_element["path"]
                wait = BrowserElement.wait_element(
                    browser_obj=browser_obj,
                    element_data={
                        "elementData": {
                            "version": batch_element["version"],
                            "type": batch_element["type"],
                            "app": batch_element["app"],
                            "picker_type": "ELEMENT",
                            "path": similar_element,
                        }
                    },
                    ele_status=WaitElementForStatusFlag.ElementExists,
                    element_timeout=int(element_timeout),
                )
                if not wait:
                    raise BaseException(WEB_GET_ElE_ERROR.format("请检查抓取元素"), "浏览器元素未找到！")
                response = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="simalarListBatch",
                    data=similar_element,
                )
                # 打印 response
                # logger.info(f'similar_element response: {response}')
                similar_values = response["values"]
                table_list = page_values_merge(table_list, similar_values, produce_type)

            # 是否翻页
            if page_count > 1 and multi_page:
                # logger.info(f'翻页: {i} 页')
                # 点击翻页按钮元素,调用 上面的click 方法
                try:
                    BrowserElement.click(
                        browser_obj=browser_obj,
                        element_data=element_data,
                        simulate_flag=simulate_flag,
                        assistive_key=ButtonForAssistiveKeyFlag.Nothing,
                        button_type=button_type,
                        element_timeout=element_timeout,
                    )
                except Exception:
                    pass
                # 等待 page_interval 秒
                time.sleep(page_interval)

        # logger.info(f'表格数据: {table_list}')
        # 合并获取到的数据 到 table_element的 values 中
        data_formated = table_json_merge_values(data_json=table_element, values=table_list)
        # logger.info(f'表格数据格式化: {data_formated}')

        # 数据处理
        data_filtered = DataFilter(data_json=data_formated).get_filtered_data()
        # logger.info(f'表格数据过滤: {data_filtered}')

        # 得到过滤后的 table_df
        table_df_out = table_df_to_out(data_json=data_filtered)

        if to_excel:
            # 将table_list 转换为excel
            if excel_path is None:
                excel_path = f"{table_element['name']}.xlsx"
            table_df_out.to_excel(excel_path, index=False, header=output_head)
            # logger.info(f'表格数据已保存到 {excel_path}')
            table_path = excel_path
            if output_type == TablePickType.Row:
                if output_head:
                    return [table_df_out.columns.tolist()] + table_df_out.values.tolist(), table_path
                else:
                    return table_df_out.values.tolist(), table_path
            else:
                return table_df_out.to_dict(orient="list"), table_path

        # 返回表格数据 按行/列 返回
        if output_type == TablePickType.Row:
            if output_head:
                return [table_df_out.columns.tolist()] + table_df_out.values.tolist()
            else:
                return table_df_out.values.tolist()
        else:
            return table_df_out.to_dict(orient="list")

    # 根据xpath/cssSelector 生成元素对象
    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[atomicMg.param("locate_type", formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value))],
        outputList=[atomicMg.param("element_obj", types="Any")],
    )
    def create_element(
        browser_obj: Browser = None,  # 浏览器对象
        locate_type: LocateType = LocateType.Xpath,  # 定位方式 xpath / cssSelector
        locate_value: str = None,
    ):
        """
        根据xpath或cssSelector生成元素对象
        :param locate_type: 元素的定位方式
        :param locate_value: 元素的 xpath /cssSelector
        :return: Element对象
        """
        # 校验locate_value
        if not locate_value:
            raise BaseException(CODE_EMPTY, "定位值不能为空")

        # 发送给插件
        response = browser_obj.send_browser_extension(
            browser_type=browser_obj.browser_type.value,
            key="generateElement",
            data={"type": locate_type.value, "value": locate_value},
        )

        # 判断 response 是否是列表，遍历列表，添加元素属性
        if isinstance(response, list):
            element_obj = []
            for item in response:
                element_obj.append(
                    {
                        "elementData": {
                            "app": browser_obj.browser_type.value,
                            "type": "web",
                            "picker_type": "ELEMENT",
                            "version": "1",
                            "path": item,
                        }
                    }
                )
        else:
            element_obj = {
                "elementData": {
                    "app": browser_obj.browser_type.value,
                    "type": "web",
                    "picker_type": "ELEMENT",
                    "version": "1",
                    "path": response,
                }
            }
        return element_obj

    # 根据元素对象找到关联元素
    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        inputList=[
            atomicMg.param(
                "relative_type",
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
            ),
            atomicMg.param(
                "child_element_type",
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.child_element_type.show",
                        expression=f"return $this.relative_type.value == '{RelativeType.Child.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "sibling_element_type",
                formType=AtomicFormTypeMeta(AtomicFormType.SELECT.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.sibling_element_type.show",
                        expression=f"return $this.relative_type.value == '{RelativeType.Sibling.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "child_element_xpath",
                dynamics=[
                    DynamicsItem(
                        key="$this.child_element_xpath.show",
                        expression=f"return $this.child_element_type.value == '{ChildElementType.Xpath.value}' && $this.relative_type.value == '{RelativeType.Child.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "child_element_index",
                dynamics=[
                    DynamicsItem(
                        key="$this.child_element_index.show",
                        expression=f"return $this.child_element_type.value == '{ChildElementType.Index.value}' && $this.relative_type.value == '{RelativeType.Child.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("element_obj", types="Any")],
    )
    @wait_element_appear
    def get_relative_element(
        browser_obj: Browser = None,
        element_data: WebPick = None,
        relative_type: RelativeType = RelativeType.Child,
        child_element_type: ChildElementType = ChildElementType.All,
        child_element_xpath: str = None,
        child_element_index: int = 0,
        sibling_element_type: SiblingElementType = SiblingElementType.All,
        element_timeout: int = 10,
    ):
        """
        根据元素对象找到关联元素
        :param browser_obj: 浏览器对象
        :param element_data: 当前元素数据
        :param relative_type: 关联元素类型（子元素或兄弟元素）
        :param child_element_type: 子元素类型（全部、按XPath、按索引）
        :param child_element_xpath: 子元素XPath
        :param child_element_index: 子元素索引
        :param sibling_element_type: 兄弟元素类型（全部、前一个、后一个）
        :param element_timeout: 元素超时时间
        :return: 关联的元素对象
        """
        element_get_type = ""
        if relative_type == RelativeType.Child:
            element_get_type = child_element_type.value
        if relative_type == RelativeType.Sibling:
            element_get_type = sibling_element_type.value

        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            # 发送给插件获取关联元素
            response = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getRelativeElement",
                data={
                    **element_data["elementData"]["path"],  # 解包内部字典的内容
                    "relativeOptions": {
                        "relativeType": relative_type.value,
                        "index": child_element_index,
                        "xpath": child_element_xpath,
                        "elementGetType": element_get_type,
                    },
                },
            )
            # 判断response 是否是列表
            if isinstance(response, list):
                element_obj = []
                for item in response:
                    element_obj.append(
                        {
                            "elementData": {
                                "app": element_data["elementData"]["app"],
                                "version": element_data["elementData"]["version"],
                                "type": element_data["elementData"]["type"],
                                "picker_type": "ELEMENT",
                                "path": item,
                            }
                        }
                    )
            else:
                element_obj = {
                    "elementData": {
                        "app": element_data["elementData"]["app"],
                        "version": element_data["elementData"]["version"],
                        "type": element_data["elementData"]["type"],
                        "picker_type": "ELEMENT",
                        "path": response,
                    }
                }
            return element_obj
        else:
            raise NotImplementedError()

    @staticmethod
    @get_default_browser
    @atomicMg.atomic(
        "BrowserElement",
        outputList=[
            atomicMg.param("element_exist", types="Bool"),
        ],
    )
    def element_exist(
        browser_obj: Browser,
        element_data: WebPick,
    ) -> bool:
        """检查元素是否存在。"""
        app = element_data["elementData"]["app"] if element_data["elementData"]["app"] != "iexplore" else "ie"
        if app != browser_obj.browser_type.value:
            raise Exception(
                f"拾取元素类型需要跟浏览器类型保持一致！当前操作的浏览器为！{browser_obj.browser_type.value}"
            )
        element_exist = False
        try:
            if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                element_exist = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="elementIsRender",
                    data=element_data["elementData"]["path"],
                )
            else:
                raise NotImplementedError()
        except Exception:
            element_exist = False
        return element_exist
