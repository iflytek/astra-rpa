import copy
import os
import time
from typing import List, Tuple

import cv2
import numpy as np


class ImageDetector(object):
    """
    用于图像处理和目标检测的类，使用OpenCV库。

    属性:
        img_path (str): 要处理的图像文件路径。
        original_img (np.ndarray): 原始图像。
        gray_img (np.ndarray): 灰度图像。
    """

    def __init__(self, img_path: str = ""):
        """初始化ImageDetector类实例。

        :param img_path: 要处理的图像的文件路径。
        """
        if img_path:
            self.img_path = img_path
            self.original_img, self.gray_img = self.get_image(img_path)

    @staticmethod
    def get_image(img_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        读取并返回图像及其灰度版本。

        :param img_path: 图像的文件路径。
        :return: 原始图像和灰度图像。
        """

        img = cv2.imread(img_path)
        gray_pic = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img, gray_pic

    def get_image_from_gradio(self, img):
        self.original_img = img
        self.gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def compute_canny_edge(grey: np.ndarray) -> np.ndarray:
        """
        计算图像的Canny算子梯度。
        对比Sobel算子，Canny算子能够检测到更细节的部分

        :param blurred: 经过高斯模糊的图像。
        :return: 二值Canny梯度图像，0或255。
        """
        edges = cv2.Canny(grey, 100, 150)
        # 100,200适用于黑色边界框

        return edges

    @staticmethod
    def compute_sobel_gradient(blurred: np.ndarray) -> np.ndarray:
        """
        计算图像的Sobel梯度。

        :param blurred: 经过高斯模糊的图像。
        :return: Sobel梯度图像。
        """

        grad_x = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0)
        grad_y = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=0, dy=1)
        gradient = cv2.subtract(grad_x, grad_y)
        gradient = cv2.convertScaleAbs(gradient)
        return gradient

    @staticmethod
    def apply_threshold_and_blur(gradient: np.ndarray) -> np.ndarray:
        """
        对图像梯度应用阈值处理和模糊处理。
        主要针对sobel算子进行阈值处理

        :param gradient: 梯度图像。
        :return: 经过阈值处理和模糊处理的图像。
        """

        ##阈值影响模型对边框的可检测性，大于75无法检测到灰框
        _, thresh = cv2.threshold(gradient, 75, 255, cv2.THRESH_BINARY)

        return thresh

    @staticmethod
    def apply_adaptive_threshold(edge: np.ndarray) -> np.ndarray:
        """
        自适应阈值筛选

        基本上没有用……
        """
        thresh = cv2.adaptiveThreshold(
            edge, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        return thresh

    @staticmethod
    def apply_morphology(thresh: np.ndarray) -> np.ndarray:
        """
        对图像应用形态学变换。

        :param thresh: 阈值处理后的图像。
        :return: 形态学变换后的图像。
        """

        closed = cv2.dilate(thresh, (3, 3), iterations=3)
        return closed

    @staticmethod
    def compute_iou(box1: List[int], box2: List[int]) -> float:
        """
        计算两个边界框的交并比（IoU）。

        :param box1: 第一个边界框的坐标和尺寸（x, y, 宽度, 高度）。
        :param box2: 第二个边界框的坐标和尺寸。
        :return: 两个边界框的交并比（IoU）。
        """

        x1min, y1min = box1[0], box1[1]
        x1max, y1max = box1[0] + box1[2], box1[1] + box1[3]
        s1 = box1[2] * box1[3]
        x2min, y2min = box2[0], box2[1]
        x2max, y2max = box2[0] + box2[2], box2[1] + box2[3]
        s2 = box2[2] * box2[3]

        xmin = np.maximum(x1min, x2min)
        ymin = np.maximum(y1min, y2min)
        xmax = np.minimum(x1max, x2max)
        ymax = np.minimum(y1max, y2max)
        inter_h = np.maximum(ymax - ymin, 0.0)
        inter_w = np.maximum(xmax - xmin, 0.0)

        intersection = inter_h * inter_w
        union = s1 + s2 - intersection
        iou = intersection / union

        return iou

    def fill_hole(self, masker):

        _, mask = cv2.threshold(masker, 30, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        areas = [cv2.contourArea(contour) for contour in contours]

        # fill in small holes
        for idx, area in enumerate(areas):
            # only fill in contours which have area smaller than 400
            if area < 200:
                x, y, w, h = cv2.boundingRect(contours[idx])
                mask[y : y + h, x : x + w] = 255
        return mask

    @staticmethod
    def apply_nms(
        boxes: List[List[int]], iou_threshold: float = 0.3
    ) -> List[List[int]]:
        """
        对边界框应用非极大值抑制（NMS）。

        :param boxes: 边界框列表。
        :param iou_threshold: IoU阈值，用于确定是否抑制。
        :return: 经过NMS处理后的边界框列表。
        """
        if not boxes:
            return []

        ##排序算法以边界框的宽度为标准降序排列
        boxes = sorted(boxes, key=lambda x: x[2], reverse=False)
        print(boxes)
        keep_boxes = []

        while boxes:
            base_box = boxes.pop()
            keep_boxes.append(base_box)

            for box in boxes[:]:
                ##设置合适的阈值对交并比大的边界框进行筛选
                iou = ImageDetector.compute_iou(base_box, box)
                if iou > 0 and (iou >= iou_threshold or iou < 0.0003):
                    boxes.remove(box)

        return keep_boxes

    def draw_dashed_rectangle(
        self, top_left, bottom_right, color, thickness, dash_length=5
    ):
        x1, y1 = top_left
        x2, y2 = bottom_right
        for x in range(x1, x2, 2 * dash_length):
            cv2.line(
                self.output_img,
                (x, y1),
                (min(x + dash_length, x2), y1),
                color,
                thickness,
            )
            cv2.line(
                self.output_img,
                (x, y2),
                (min(x + dash_length, x2), y2),
                color,
                thickness,
            )
        for y in range(y1, y2, 2 * dash_length):
            cv2.line(
                self.output_img,
                (x1, y),
                (x1, min(y + dash_length, y2)),
                color,
                thickness,
            )
            cv2.line(
                self.output_img,
                (x2, y),
                (x2, min(y + dash_length, y2)),
                color,
                thickness,
            )

    def preprocess_stage(self, gradient, is_adaptive):

        if is_adaptive:
            thresh = self.apply_adaptive_threshold(gradient)
        else:
            thresh = self.apply_threshold_and_blur(gradient)

        closed = self.apply_morphology(thresh)
        contours = self.fill_hole(closed)
        contours, _ = cv2.findContours(
            contours, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS
        )

        return contours

    def detect_objects(self, dash_color, line_width):
        """
        检测图像中的对象，并返回带有检测到的对象的原始图像和边界框列表。

        :return: 带有检测到的对象的原始图像和边界框列表。
                 每个边界框以 ((左上角x, 左上角y), (右下角x, 右下角y)) 的格式表示。
        """

        start_time = time.time()
        blurred = cv2.GaussianBlur(self.gray_img, (3, 3), 0)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        kernel1 = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        # 计算边缘梯度
        canny_gradient = self.compute_canny_edge(sharpened)
        sobel_gradient = self.compute_sobel_gradient(sharpened)

        ## Step1 前景检测，筛选
        _, fore_g = cv2.threshold(
            canny_gradient, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        kernel = np.ones((3, 3), np.uint8)
        # 膨胀函数
        fore_g = cv2.dilate(fore_g, kernel, iterations=2)
        _, fore_markers = cv2.connectedComponents(fore_g)
        fore_markers = fore_markers.astype(np.uint8)
        fore_contours, _ = cv2.findContours(
            fore_markers.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        ## Step2 Sobel算子检测常规边框
        sobel_contours = self.preprocess_stage(sobel_gradient, False)

        ## Step3 Canny算子检测细节内容
        canny_contours = self.preprocess_stage(canny_gradient, False)

        ## 边框筛选
        fore_boxes = [
            (x, y, w, h)
            for x, y, w, h in (cv2.boundingRect(contour) for contour in fore_contours)
            if (w * h) > 50
            and (h / w) < 10
            and (w * h) / (self.original_img.shape[0] * self.original_img.shape[1])
            < 0.2
        ]

        sobel_boxes = [
            (x, y, w, h)
            for x, y, w, h in (cv2.boundingRect(contour) for contour in sobel_contours)
            if (w * h) > 50
            and (h / w) < 10
            and (w * h) / (self.original_img.shape[0] * self.original_img.shape[1])
            < 0.2
        ]

        canny_boxes = [
            (x, y, w, h)
            for x, y, w, h in (cv2.boundingRect(contour) for contour in canny_contours)
            if ((w * h) > 20 and (w * h) <= 50)
            or ((w * h) > 200 and (w * h) <= 350)
            and (h / w) < 10
            and (w * h) / (self.original_img.shape[0] * self.original_img.shape[1])
            < 0.2
        ]

        self.output_img = copy.deepcopy(self.original_img)
        ## 边框融合&非极大值抑制
        all_boxes = fore_boxes + sobel_boxes
        selected_boxes = self.apply_nms(all_boxes)

        boxes_with_coordinates = []

        if dash_color is None:
            dash_color = "#00FF00"
        dash_color = dash_color.lstrip("#")

        dash_color = tuple(int(dash_color[i : i + 2], 16) for i in (0, 2, 4))

        # dash_color = self.qcolor_to_bgr(dash_color)

        for box in selected_boxes:
            x, y, w, h = box
            boxes_with_coordinates.append(box)
            self.draw_dashed_rectangle(
                (x, y), (x + w, y + h), dash_color, line_width, 5
            )
        selected_boxes = selected_boxes
        # + self.detect_ocr_text(line_width)

        end_time = time.time()
        print(end_time - start_time)
        return self.output_img, selected_boxes

    def show_or_save_image(self, save_path: str = None, show_image: bool = True):
        """
        显示或保存检测到对象的图像。

        :param save_path: (可选) 图像保存的文件路径。仅在 show_image 为 False 时使用。
        :param show_image: 控制是显示图像还是保存到文件。默认为 True，即显示图像。
        """
        if show_image:
            cv2.imwrite("output.png", self.output_img)
            cv2.imshow("Detected Objects", self.output_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        else:
            if save_path is None:
                raise ValueError("必须提供 save_path 参数以保存图像。")

            if not os.path.isdir(os.path.dirname(save_path)):
                raise Exception(f"错误：路径 '{save_path}' 无效或不存在。")

            try:
                cv2.imwrite(save_path, self.original_img)
            except Exception as e:
                raise Exception(f"保存图像时发生错误：{e}")



