import base64
import io
import json
import os
from abc import ABC, abstractmethod

import cv2
import numpy as np
import pyautogui
import requests
from cv_picker.core.cv_match import AnchorMatch
from PIL import Image

current_directory = os.getcwd()
match_filepath = os.path.join(current_directory, "imgs", "match_img.png")


class IRectHandler(ABC):
    @staticmethod
    @abstractmethod
    def get_foreground_window_rect():
        pass


class IPickCore(ABC):
    @staticmethod
    @abstractmethod
    def get_mouse_position():
        pass

    @staticmethod
    def image_to_base64(img):
        """
        将图像转为base64
        :param img: 输入图像
        :return:
        """
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")  # convert to bytes
        img_byte_arr = img_byte_arr.getvalue()  # convert bytes to base64
        return base64.b64encode(img_byte_arr).decode("utf-8")

    @staticmethod
    def get_img(rect, desktop):
        """
        获取元素图像
        :param rect:
        :param desktop:
        :return:
        """
        return desktop.crop(rect)

    @staticmethod
    def json_res(target_img, target_rect, anchor_img, anchor_rect, screen):
        """
        返回拾取到的目标元素及锚点元素的json结果
        :param target_img:
        :param target_rect:
        :param anchor_img:
        :param anchor_rect:
        :return:
        """

        def encode_image(image):
            return IPickCore.image_to_base64(image) if image else ""

        def get_position(rect, index):
            return rect[index] if rect else ""

        res = {
            "version": "1",
            "type": "cv",
            "app": "",
            "path": "",
            "img": {
                "self": encode_image(target_img),
                "parent": encode_image(anchor_img),
            },
            "pos": {
                "self_x": get_position(target_rect, 0),
                "self_y": get_position(target_rect, 1),
                "parent_x": get_position(anchor_rect, 0),
                "parent_y": get_position(anchor_rect, 1),
            },
            "sr": {"screen_w": screen.width, "screen_h": screen.height},
            "picker_type": "ELEMENT",
        }

        if not (target_img or anchor_img or target_rect or anchor_rect):
            return None

        return json.dumps(res, ensure_ascii=False)

    @staticmethod
    def base64_to_image(base64_str):
        if not base64_str:
            return None

        try:
            # 解码 base64 字符串
            image_data = base64.b64decode(base64_str)
            # 将字节数据转换为图像
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            print(f"Error converting base64 to image: {e}")
            return None

    @staticmethod
    def get_url(input_url, remote_addr):
        print("请求开始 {}{}".format(remote_addr, input_url))
        try:
            response = requests.get(f"{remote_addr}{input_url}")
            response.raise_for_status()  # 自动抛出HTTP错误
        except requests.exceptions.RequestException as e:
            raise Exception(f"服务器错误: {e}")
        print(response.content)
        base64_encoded_data = base64.b64encode(response.content).decode("utf-8")
        return base64_encoded_data

    @staticmethod
    def match_imgs(data, remote_addr, canny_flag=False):
        match = AnchorMatch()

        target = data["img"]["self"]
        anchor = data["img"]["parent"]
        match_similarity = data.get("similarity", 0.60)

        if target.startswith("/api"):
            target = IPickCore.get_url(target, remote_addr)
            print("获取到目标url的base64为：{}".format(target))

        target_img = IPickCore.base64_to_image(target)
        center_coords_aim = f"{data['pos']['self_x']},{data['pos']['self_y']}"

        if anchor:
            if target.startswith("/api"):
                anchor = IPickCore.get_url(anchor, remote_addr)
                print("获取到锚点url的base64为：{}".format(anchor))
            anchor_img = IPickCore.base64_to_image(anchor)
            center_coords_anchor = f"{data['pos']['parent_x']},{data['pos']['parent_y']}"
        else:
            anchor_img = None
            center_coords_anchor = ""

        match_img = pyautogui.screenshot(region=None)
        match_img.save(match_filepath)
        ratio_w = match_img.width / data["sr"]["screen_w"]
        ratio_h = match_img.height / data["sr"]["screen_h"]
        ratio = f"{ratio_w},{ratio_h}"
        match_img = np.array(match_img)
        try:
            _, match_box = match.process_image(
                match_img,
                target_img,
                anchor_img,
                center_coords_aim=center_coords_aim,
                center_coords_anchor=center_coords_anchor,
                canny_flag=canny_flag,
                ratio=ratio,
                match_similarity=match_similarity,
            )
        except cv2.error as e:
            raise ValueError("图像匹配报错，请检查图像")
        return match_box
