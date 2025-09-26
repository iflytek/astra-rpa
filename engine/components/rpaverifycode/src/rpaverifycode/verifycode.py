import time

import pyautogui
from locator import smooth_move
from locator.locator import locator
from rpaatomic import DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import WebPick
from rpabrowser.browser import Browser
from rpabrowser.browser_element import BrowserElement
from rpaframe.logger.logger import logger

from rpaverifycode import HintPosition, PictureCodeType
from rpaverifycode.core import VerifyCodeCore
from rpaverifycode.error import *

VerifyCodeCore = VerifyCodeCore()
Locator = locator


class VerifyCode:
    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "input_box",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_box.show",
                        expression="return  $this.input_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("code_result", types="Str"),
        ],
    )
    def picture_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        code_type: PictureCodeType = PictureCodeType.GENERAL1234,
        input_flag: bool = False,
        input_box: WebPick = None,
    ) -> str:
        element = Locator.locator(picture_pick.get("elementData"))
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        code_result = VerifyCodeCore.get_api_result(api_type=code_type.value, pic_element_base64=image_base64)
        logger.info("验证码返回值: {}".format(code_result))
        if not code_result:
            raise BaseException(MSG_EMPTY_FORMAT, "")

        if input_flag:
            BrowserElement.input(browser_obj=browser_obj, element_data=input_box, fill_input=code_result)

        return code_result

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[
            atomicMg.param(
                "move_pic_pick",
                dynamics=[
                    DynamicsItem(
                        key="$this.move_pic_pick.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "mini_step",
                dynamics=[
                    DynamicsItem(
                        key="$this.mini_step.show",
                        expression="return  $this.unmatched_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("drag_distance", types="Int")],
    )
    def slider_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        slider_pick: WebPick = None,
        unmatched_flag: bool = False,
        move_pic_pick: WebPick = None,
        mini_step: int = 5,
    ) -> int:
        element = Locator.locator(picture_pick.get("elementData"))
        rect = element.rect()
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())
        drag_distance = int(VerifyCodeCore.get_api_result(api_type="22222", pic_element_base64=image_base64))
        logger.info("验证码返回值: {}".format(drag_distance))
        if not drag_distance:
            raise BaseException(MSG_EMPTY_FORMAT, "")

        slider_element = Locator.locator(slider_pick.get("elementData"))
        start_pos = slider_element.point()
        if not unmatched_flag:
            end_pos = (start_pos.x + drag_distance, start_pos.y)
            VerifyCodeCore.html_drag_plus(start_pos, end_pos)

        else:
            smooth_move(start_pos.x, start_pos.y, duration=0.5)
            pyautogui.mouseDown()
            smooth_move(start_pos.x + drag_distance * 0.85, start_pos.y, duration=0.5)
            time.sleep(0.5)
            delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
            logger.info(delta)
            while abs(delta) > mini_step:
                if delta > 0:
                    smooth_move(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x + mini_step, start_pos.y, duration=0.5)
                else:
                    smooth_move(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                    # pyautogui.moveTo(pyautogui.position().x - mini_step, start_pos.y, duration=0.5)
                time.sleep(0.5)
                delta = drag_distance - round(float(VerifyCodeCore.get_margin_left(browser_obj, move_pic_pick)))
                logger.info(delta)
            # 释放滑块
            pyautogui.mouseUp()

        return drag_distance

    @staticmethod
    @atomicMg.atomic(
        "VerifyCode",
        inputList=[],
        outputList=[atomicMg.param("click_positions", types="List")],
    )
    def click_code(
        browser_obj: Browser = None,
        picture_pick: WebPick = None,
        hint_position: HintPosition = HintPosition.BOTTOM,
    ):
        element = Locator.locator(picture_pick.get("elementData"))
        rect = element.rect()
        logger.info("rect: {}".format(rect))
        image_base64 = VerifyCodeCore.get_base64_screenshot(rect.left, rect.top, rect.width(), rect.height())

        # 86,94|255,62|170,92
        click_result = VerifyCodeCore.get_api_result(
            api_type="30332",
            pic_element_base64=image_base64,
            direction=hint_position.value,
        )
        logger.info("验证码返回值: {}".format(click_result))
        if not click_result:
            raise BaseException(MSG_EMPTY_FORMAT, "")
        click_positions = click_result.split("|")
        click_positions = [tuple(map(int, pos.split(","))) for pos in click_positions]

        # 开始点击
        for pos in click_positions:
            pos = (pos[0] + rect.left, pos[1] + rect.top)
            smooth_move(*pos, duration=0.5)
            pyautogui.click()
            time.sleep(0.5)

        return click_positions
