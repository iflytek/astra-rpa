import logging
import math

import cv2
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class AnchorMatch:
    def __init__(self):
        pass

    def draw_dashed_rectangle(self, image, top_left, bottom_right, color, thickness, dash_length=10):
        x1, y1 = top_left
        x2, y2 = bottom_right

        for x in range(x1, x2, 2 * dash_length):
            cv2.line(image, (x, y1), (min(x + dash_length, x2), y1), color, thickness)
            cv2.line(image, (x, y2), (min(x + dash_length, x2), y2), color, thickness)
        for y in range(y1, y2, 2 * dash_length):
            cv2.line(image, (x1, y), (x1, min(y + dash_length, y2)), color, thickness)
            cv2.line(image, (x2, y), (x2, min(y + dash_length, y2)), color, thickness)

    @staticmethod
    def check_if_multiple_elements(image, element, match_similarity):
        if not isinstance(image, np.ndarray):
            image = np.array(image.convert("RGBA"))
        if not isinstance(element, np.ndarray):
            element = np.array(element.convert("RGBA"))
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if element is not None:
            small_gray = cv2.cvtColor(element, cv2.COLOR_RGB2GRAY)
            threshold = match_similarity  # Adjust this threshold if needed
            # 匹配目标位置
            result1 = cv2.matchTemplate(gray, small_gray, cv2.TM_CCOEFF_NORMED)
            loc1 = np.where(result1 >= threshold)
            count = len(loc1[0])
            print(f"匹配个数为：{count}")
        if count == 1:
            return True  # 标识元素唯一存在可匹配
        else:
            return False  # 标识元素不唯一或未匹配到
        # if count > 1:
        #     return 1
        # elif count < 1:
        #     return -1
        # else:
        #     return 0

    def _limit_roi_bounds(self, roi_top_left: tuple, roi_bottom_right: tuple, image_shape: tuple) -> tuple:
        """
        限制ROI的边界值在图像范围内

        Args:
            roi_top_left: (x, y) 左上角坐标
            roi_bottom_right: (x, y) 右下角坐标
            image_shape: 图像尺寸 (height, width, channels)

        Returns:
            (limited_top_left, limited_bottom_right)
        """
        img_height, img_width = image_shape[:2]

        # 限制x坐标
        x1 = max(0, min(roi_top_left[0], img_width - 1))
        x2 = max(0, min(roi_bottom_right[0], img_width - 1))

        # 限制y坐标
        y1 = max(0, min(roi_top_left[1], img_height - 1))
        y2 = max(0, min(roi_bottom_right[1], img_height - 1))

        # 确保右下角坐标大于左上角坐标
        x2 = max(x2, x1 + 1)
        y2 = max(y2, y1 + 1)

        return (x1, y1), (x2, y2)

    def process_image(
        self,
        image,
        element,
        anchor=None,
        center_coords_aim=None,
        center_coords_anchor=None,
        canny_flag=False,
        ratio=None,
        match_similarity=0.95,
        line_width_match=None,
        dash_color=None,
    ):
        """
        根据锚点找到目标
        Args:
            image (_type_): 屏幕截图
            element (_type_): 目标元素图片
            anchor (_type_, optional): 锚点元素图片. Defaults to None.
            center_coords_aim (_type_, optional): 目标元素坐标. Defaults to None.
            center_coords_anchor (_type_, optional): 锚点元素坐标. Defaults to None.
            ratio (_type_, optional): 屏幕缩放比例. Defaults to None.
            line_width_match (_type_, optional): 线宽. Defaults to None.
            dash_color (_type_, optional): 框线颜色. Defaults to None.

        Returns:
            _type_: 找到目标元素的屏幕截图
        """
        if dash_color is None:
            dash_color = "#00FF00"
        dash_color = dash_color.lstrip("#")
        color_bgr = tuple(int(dash_color[i : i + 2], 16) for i in (0, 2, 4))
        # 目标元素查找范围的框的颜色
        roi_color_bgr = tuple(int("ADD8E6"[i : i + 2], 16) for i in (2, 0, 4))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        element = np.array(element)
        element = cv2.cvtColor(element, cv2.COLOR_RGB2BGR)
        if anchor is not None:
            anchor = np.array(anchor)
            anchor = cv2.cvtColor(anchor, cv2.COLOR_RGB2BGR)

        # 获取长宽比例
        if ratio != "":
            rw, rh = float(ratio.split(",")[0]), float(ratio.split(",")[1])
        else:
            rw, rh = 1, 1

        # 确保锚点和锚点坐标都获取到
        logger.info(f"当前屏幕与原始比例为{rw},{rh}")
        if center_coords_anchor != "" and anchor is not None:
            # 提取并转换坐标
            aim_x, aim_y = map(int, center_coords_aim.split(","))
            anchor_x, anchor_y = map(int, center_coords_anchor.split(","))

            # 计算距离
            dis_x = (aim_x - anchor_x) * rw
            dis_y = (aim_y - anchor_y) * rh
            # dis_x = int((int(center_coords_aim.split(',')[0])-int(center_coords_anchor.split(',')[0]))*rw)
            # dis_y = int((int(center_coords_aim.split(',')[1])-int(center_coords_anchor.split(',')[1]))*rh)

        # 大图转灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if canny_flag:
            gray = cv2.Canny(gray, 50, 250)

        # 如果元素存在
        if element is not None:
            # 匹配目标位置,按照屏幕等比例缩放
            # w, h = int(element.shape[1]), int(element.shape[0])
            # w, h = int(w*rw), int(h*rh)
            w, h = int(element.shape[1] * rw), int(element.shape[0] * rh)
            element = cv2.resize(element, (w, h), interpolation=cv2.INTER_CUBIC)
            small_gray = cv2.cvtColor(element, cv2.COLOR_RGB2GRAY)
            if canny_flag:
                small_gray = cv2.Canny(small_gray, 50, 250)

            if anchor is not None:
                # 要求锚点在屏幕显示且唯一
                anchor_gray = cv2.cvtColor(anchor, cv2.COLOR_RGB2GRAY)
                anchor_threshold = match_similarity
                if canny_flag:
                    anchor_gray = cv2.Canny(anchor_gray, 50, 250)
                    anchor_threshold = 0.6
                aw, ah = int(anchor_gray.shape[1] * rw), int(anchor_gray.shape[0] * rh)

                anchor_gray = cv2.resize(anchor_gray, (aw, ah), interpolation=cv2.INTER_CUBIC)
                anchor_match_res = cv2.matchTemplate(gray, anchor_gray, cv2.TM_CCORR_NORMED)
                _, anchor_max_val, _, anchor_pos = cv2.minMaxLoc(anchor_match_res)

                # TODO 执行的时候锚点不存在了，需要处理逻辑，当执行的时候缩放导致锚点变化的情况
                logger.info(f"当前目标元素不唯一或置信度低，需要锚点，且锚点置信度为{anchor_max_val}")
                if anchor_max_val < anchor_threshold:
                    logger.info("屏幕上不存在锚点元素或者当前界面像素过低导致找不到锚点元素")
                    # gr.Info("屏幕上不存在锚点元素或者当前界面像素过低导致找不到锚点元素")

                roi_loc = (anchor_pos[0] + dis_x, anchor_pos[1] + dis_y)
                # 定义扩展因子，以简化计算
                expand_factor = 1 / 5
                # 计算ROI的顶点
                roi_top_left = (
                    math.ceil(roi_loc[0] - (w * expand_factor)),
                    math.ceil(roi_loc[1] - (h * expand_factor)),
                )
                roi_bottom_right = (
                    math.ceil(roi_loc[0] + w * (1 + expand_factor)),
                    math.ceil(roi_loc[1] + h * (1 + expand_factor)),
                )
                print(f"roi_top_left:{roi_top_left},roi_bottom_right:{roi_bottom_right}")
                roi_top_left, roi_bottom_right = self._limit_roi_bounds(roi_top_left, roi_bottom_right, image.shape)
                print(f"roi_top_left:{roi_top_left},roi_bottom_right:{roi_bottom_right}")
                self.draw_dashed_rectangle(
                    image,
                    roi_top_left,
                    roi_bottom_right,
                    roi_color_bgr,
                    line_width_match,
                )
                roi = gray[
                    roi_top_left[1] : roi_bottom_right[1],
                    roi_top_left[0] : roi_bottom_right[0],
                ]

                result_CCORR_top = cv2.matchTemplate(roi, small_gray, cv2.TM_CCORR_NORMED)
                result_CCOEFF_top = cv2.matchTemplate(roi, small_gray, cv2.TM_CCOEFF_NORMED)
                min_rr, max_rr, _, max_loc = cv2.minMaxLoc(result_CCORR_top)
                min_a, max_ccoeff_val, _, max_loc_ccoeff = cv2.minMaxLoc(result_CCOEFF_top)

                print("max_val:", max_ccoeff_val)
                # target_threshold = 0.85
                target_threshold = match_similarity
                if canny_flag:
                    target_threshold = 0.40
                if max_ccoeff_val >= target_threshold:
                    match_box = (
                        roi_top_left[0] + max_loc[0],
                        roi_top_left[1] + max_loc[1],
                        w,
                        h,
                    )
                    # self.draw_dashed_rectangle(image, (roi_top_left[0] + max_loc[0], roi_top_left[1] + max_loc[1]),
                    #                            (roi_top_left[0] + max_loc[0] + w, roi_top_left[1] + max_loc[1] + h),
                    #                            color_bgr, line_width_match)
                    print("元素已在锚点相对范围内匹配完成")

                else:
                    print("当前屏幕目标元素不存在或发生了变化")
                    match_box = None

            else:
                target_match_res = cv2.matchTemplate(gray, small_gray, cv2.TM_CCOEFF_NORMED)
                _, target_max_val, _, target_max_loc = cv2.minMaxLoc(target_match_res)
                print("target_max_val:", target_max_val)
                target_threshold = match_similarity
                if canny_flag:
                    target_threshold = 0.40
                if target_max_val >= target_threshold:
                    match_box = (target_max_loc[0], target_max_loc[1], w, h)
                    # self.draw_dashed_rectangle(image, target_max_loc, (target_max_loc[0] + w, target_max_loc[1] + h),
                    #                            color_bgr, line_width_match)
                    print("元素匹配完成")
                else:
                    print("当前屏幕目标元素不存在或发生了变化")
                    match_box = None
        else:
            return print("请选择目标元素")

        return image, match_box


if __name__ == "__main__":
    # cv_match()
    pass
