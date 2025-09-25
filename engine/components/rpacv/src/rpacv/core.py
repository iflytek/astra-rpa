import base64
import io

import cv2
import numpy as np
import pyautogui
from PIL import Image
from rpacv.cv_match import AnchorMatch

desktop_filepath = "desktop.png"
desktop_filepath_match = "desktop_filepath_match.png"


class CvCore:
    def __init__(self):
        pyautogui.FAILSAFE = False

    @staticmethod
    def get_img(img_path):
        return cv2.imread(img_path)

    @staticmethod
    def get_gray_img(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def match_imgs(input_data=None, match_similarity=0.95, canny_flag=False):
        match = AnchorMatch()
        data = input_data.get("elementData")

        # data = input_data
        target_img = CvCore.base64_to_image(data["img"]["self"])
        center_coords_aim = f"{data['pos']['self_x']},{data['pos']['self_y']}"

        if data["img"]["parent"]:
            anchor_img = CvCore.base64_to_image(data["img"]["parent"])
            center_coords_anchor = f"{data['pos']['parent_x']},{data['pos']['parent_y']}"
        else:
            anchor_img = None
            center_coords_anchor = ""

        match_img = pyautogui.screenshot(region=None)
        match_img.save(desktop_filepath_match)
        ratio_w = match_img.width / data["sr"]["screen_w"]
        ratio_h = match_img.height / data["sr"]["screen_h"]
        ratio = f"{ratio_w},{ratio_h}"
        match_img = np.array(match_img)

        out_img, match_box = match.process_image(
            match_img,
            target_img,
            anchor_img,
            center_coords_aim=center_coords_aim,
            center_coords_anchor=center_coords_anchor,
            canny_flag=canny_flag,
            ratio=ratio,
            match_similarity=match_similarity,
        )
        cv2.imwrite(desktop_filepath, out_img)
        return match_box

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
    def screenshot(region=None):
        """
        根据指定位置截图
        :param region: [top, left, bottom, right]
        :param file_path: 存储文件位置
        :return:
        """
        return pyautogui.screenshot(region=region)

    @staticmethod
    def get_region_position(target_rect, specified_position, horizontal_offset, vertical_offset):
        """
        获取指定位置的坐标
        :param target_rect: 目标元素的边框坐标
        :param specified_position: 指定位置编码
        :param horizontal_offset: 横向偏移
        :param vertical_offset: 纵向偏移
        :return: 指定的坐标位置
        """
        x, y, w, h = target_rect
        region_weight = w // 3
        region_height = h // 3
        row = (specified_position - 1) // 3
        col = (specified_position - 1) % 3
        center_x = x + col * region_weight + region_weight // 2
        center_y = y + row * region_height + region_height // 2
        if horizontal_offset or vertical_offset:
            target_x = center_x + horizontal_offset
            target_y = center_y + vertical_offset
            target_x = max(
                x + col * region_weight,
                min(target_x, x + (col + 1) * region_weight - 1),
            )
            target_y = max(
                y + row * region_height,
                min(target_y, y + (row + 1) * region_height - 1),
            )
            return target_x, target_y
        return center_x, center_y
