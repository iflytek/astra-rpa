import base64
import random
import re
import time
from io import BytesIO

import pyautogui
import requests
from locator import smooth_move
from rpaatomic.logger import logger
from src.rpaverifycode import ElementGetAttributeTypeFlag

from rpaverifycode import VerifyCodeConfig


class VerifyCodeCore:
    @staticmethod
    def get_api_result(api_type: str, pic_element_base64: str, **kwargs):
        data = {
            "image": pic_element_base64,
            "type": api_type,
        }
        if kwargs.get("direction"):
            data["direction"] = kwargs.get("direction")

        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(VerifyCodeConfig.url, headers=headers, json=data).json()
        result = response["data"]["data"]
        return result

    @staticmethod
    def get_base64_screenshot(left, top, width, height):
        # 截取指定区域的屏幕
        screenshot = pyautogui.screenshot(region=(int(left), int(top), int(width), int(height)))
        buffer = BytesIO()
        screenshot.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return image_base64

    @staticmethod
    def html_drag_plus(start_pos, end_pos):
        """
        指定起始坐标以及结束坐标进行拖拽操作
        """
        start_pos = (start_pos.x, start_pos.y)
        smooth_move(*start_pos, duration=0.5)
        pyautogui.mouseDown(*start_pos, button="left")
        time.sleep(0.5)
        # 为了绕过轨迹验证
        distance = end_pos[0] - start_pos[0]
        pos_1 = [start_pos[0] + distance * 0.7, end_pos[1] + 10]
        smooth_move(*pos_1, duration=random.choice([0.2, 0.4, 0.6]))
        pos_1 = [start_pos[0] + distance * 0.8, end_pos[1] + 10]
        smooth_move(*pos_1, duration=random.choice([0.2, 0.4, 0.61]))
        pos_1 = [start_pos[0] + distance * 1.2, end_pos[1] + 10]
        smooth_move(*pos_1, duration=random.choice([0.2, 0.4, 0.6]))
        smooth_move(*end_pos, duration=0.2)
        pyautogui.mouseUp(*end_pos, button="left")

    @staticmethod
    def get_margin_left(browser_obj, element):
        from rpabrowser.browser_element import BrowserElement

        style = BrowserElement.element_operation(
            browser_obj=browser_obj,
            element_data=element,
            get_type=ElementGetAttributeTypeFlag.GetAttribute,
            attribute_name="style",
        )
        # margin-top: 46px; display: block; margin-left: 0px;
        match = re.search(r"margin-left:\s*([-+]?\d*\.?\d+)px", style)
        if match:
            margin_left_value = match.group(1)  # 提取捕获组中的值
            logger.info(f"找到的 margin-left 值: {margin_left_value} px")
            return margin_left_value
        else:
            match = re.search(r"left:\s*([-+]?\d*\.?\d+)px", style)
            if match:
                margin_left_value = match.group(1)  # 提取捕获组中的值
                logger.info(f"找到的 left 值: {margin_left_value} px")
                return margin_left_value
            else:
                logger.info("未找到 margin-left / left 属性。")
                raise Exception("未找到 margin-left / left属性。请尝试重新拾取。")
