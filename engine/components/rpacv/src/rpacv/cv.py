import random
import time

import pyautogui
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import IMGPick
from rpagui import MoveType, Simulate_flag, Speed
from rpagui.code.clipboard import Clipboard
from rpagui.code.keyboard import Keyboard
from rpagui.code.mouse import Mouse
from rpagui.error import CLIP_PASTE_ERROR, REGION_ERROR

from rpacv import *
from rpacv.core import CvCore
from rpacv.error import *

# 定义输入法的语言代码
ENGLISH = 0x0409  # 英文（美国）
CHINESE = 0x0804  # 中文（简体，中国）
speed_to_int = {Speed.SLOW: 2, Speed.NORMAL: 1, Speed.FAST: 0.5}


class CV:
    @staticmethod
    @atomicMg.atomic(
        "CV",
        inputList=[
            atomicMg.param(
                "input_data",
                formType=AtomicFormTypeMeta(AtomicFormType.PICK.value, params={"use": "CV"}),
                noInput=True,
            ),
            atomicMg.param("btn_type", required=False),
            atomicMg.param("btn_model", required=False),
            atomicMg.param("click_position", required=False),
            atomicMg.param(
                "specified_position",
                required=False,
                formType=AtomicFormTypeMeta(AtomicFormType.GRID.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.specified_position.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "horizontal_move",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.horizontal_move.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "vertical_move",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.vertical_move.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
            atomicMg.param(
                "match_similarity",
                formType=AtomicFormTypeMeta(AtomicFormType.SLIDER.value),
                required=False,
            ),
            atomicMg.param("move_type", level=AtomicLevel.ADVANCED.value, required=False),
            atomicMg.param(
                "move_speed",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.move_speed.show",
                        expression="return ['{}','{}'].includes($this.move_type.value)".format(
                            MoveType.LINEAR.value, MoveType.SIMULATION.value
                        ),
                    )
                ],
                required=False,
            ),
        ],
        outputList=[],
    )
    def cv_click(
        input_data: IMGPick,
        btn_type: BtnType = BtnType.LEFT,
        btn_model: BtnModel = BtnModel.CLICK,
        click_position: PositionType = PositionType.CENTER,
        specified_position=5,
        horizontal_move: int = 0,
        vertical_move: int = 0,
        match_similarity: float = 0.95,
        move_type: MoveType = MoveType.LINEAR,
        move_speed: Speed = Speed.NORMAL,
        wait_time: int = 10,
    ):
        """
        鼠标点击图片
        :param input_data: 目标图像
        :param btn_type: 鼠标按键
        :param btn_model: 点击方式
        :param click_position: 点击位置
        :param specified_position: 指定位置
        :param horizontal_move: 横向平移
        :param vertical_move: 纵向平移
        :param match_similarity: 匹配相似度
        :param wait_time: 等待时间
        :return: 空
        """
        start_time = time.time()
        while True:
            target_rect = CvCore.match_imgs(input_data=input_data, match_similarity=match_similarity)
            if target_rect is not None:
                try:
                    if click_position == PositionType.CENTER:
                        target_x = target_rect[0] + target_rect[2] // 2
                        target_y = target_rect[1] + target_rect[3] // 2
                    elif click_position == PositionType.RANDOM:
                        target_x = target_rect[0] + random.randint(0, target_rect[2])
                        target_y = target_rect[1] + random.randint(0, target_rect[3])
                    elif click_position == PositionType.SPECIFIC:
                        position = specified_position
                        if position is None:
                            raise BaseException(SPECIFIC_POSITION_ERROR, "未指定点击位置，请检查参数")
                        # 按照指定位置计算点击位置
                        target_x, target_y = CvCore.get_region_position(
                            target_rect, position, horizontal_move, vertical_move
                        )
                    else:
                        raise NotImplementedError()

                    screen_weight, screen_height = Mouse.screen_size()
                    if target_x < 0 or target_x > screen_weight or target_y < 0 or target_y > screen_height:
                        raise BaseException(REGION_ERROR, "坐标参数不合法！")

                    if move_type == MoveType.LINEAR:
                        Mouse.move(
                            target_x,
                            target_y,
                            duration=speed_to_int[move_speed],
                            tween=pyautogui.linear,
                        )
                    elif move_type == MoveType.SIMULATION:
                        Mouse.move_simulate(
                            target_x,
                            target_y,
                            duration=speed_to_int[move_speed],
                            tween=pyautogui.easeInOutQuad,
                        )
                    elif move_type == MoveType.TELEPORTATION:
                        Mouse.move(target_x, target_y, duration=0)
                    else:
                        raise NotImplementedError()

                    if btn_model == BtnModel.CLICK:
                        Mouse.click(None, None, 1, 0, btn_type.value)
                    elif btn_model == BtnModel.DOUBLE_CLICK:
                        Mouse.click(None, None, 2, 0, btn_type.value)
                    else:
                        raise NotImplementedError()

                    return True
                except Exception as e:
                    raise BaseException(MOUSE_CLICK_ERROR, "鼠标点击失败")
            else:
                if time.time() - start_time > wait_time:
                    break
                else:
                    time.sleep(0.1)

        raise BaseException(CV_MATCH_ERROR, "超时未匹配到目标元素，请检查当前界面或降低匹配相似度重试")

    @staticmethod
    @atomicMg.atomic(
        "CV",
        inputList=[
            atomicMg.param(
                "input_data",
                formType=AtomicFormTypeMeta(AtomicFormType.PICK.value, params={"use": "CV"}),
                noInput=True,
            ),
            atomicMg.param("click_position", required=False),
            atomicMg.param(
                "specified_position",
                formType=AtomicFormTypeMeta(AtomicFormType.GRID.value),
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.specified_position.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "horizontal_move",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.horizontal_move.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "vertical_move",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.vertical_move.show",
                        expression="return $this.click_position.value == '{}'".format(PositionType.SPECIFIC.value),
                    )
                ],
            ),
            atomicMg.param(
                "match_similarity",
                formType=AtomicFormTypeMeta(AtomicFormType.SLIDER.value),
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
            atomicMg.param("move_type", level=AtomicLevel.ADVANCED.value, required=False),
            atomicMg.param(
                "move_speed",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.move_speed.show",
                        expression="return ['{}','{}'].includes($this.move_type.value)".format(
                            MoveType.LINEAR.value, MoveType.SIMULATION.value
                        ),
                    )
                ],
                required=False,
            ),
        ],
        outputList=[],
    )
    def hover_image(
        input_data: IMGPick,
        click_position: PositionType = PositionType.CENTER,
        specified_position=5,
        horizontal_move: int = 0,
        vertical_move: int = 0,
        match_similarity: float = 0.95,
        move_type: MoveType = MoveType.LINEAR,
        move_speed: Speed = Speed.NORMAL,
        wait_time: int = 10,
    ):
        """
        鼠标悬浮在图像上
        :param input_data: 目标图像
        :param click_position: 点击位置
        :param specified_position: 指定位置
        :param horizontal_move: 横向平移
        :param vertical_move: 纵向平移
        :param match_similarity: 匹配相似度
        :param wait_time: 等待时间
        :return: 空
        """
        start_time = time.time()
        while True:
            target_rect = CvCore.match_imgs(input_data, match_similarity)
            if target_rect is not None:
                try:
                    if click_position == PositionType.CENTER:
                        target_x = target_rect[0] + target_rect[2] // 2
                        target_y = target_rect[1] + target_rect[3] // 2
                    elif click_position == PositionType.RANDOM:
                        target_x = target_rect[0] + random.randint(0, target_rect[2])
                        target_y = target_rect[1] + random.randint(0, target_rect[3])
                    elif click_position == PositionType.SPECIFIC:
                        position = specified_position
                        if position is None:
                            raise BaseException(SPECIFIC_POSITION_ERROR, "未指定点击位置，请检查参数")
                        # 按照指定位置计算点击位置
                        target_x, target_y = CvCore.get_region_position(
                            target_rect, position, horizontal_move, vertical_move
                        )
                    else:
                        raise NotImplementedError()

                    screen_weight, screen_height = Mouse.screen_size()
                    if target_x < 0 or target_x > screen_weight or target_y < 0 or target_y > screen_height:
                        raise BaseException(REGION_ERROR, "坐标参数不合法！")

                    if move_type == MoveType.LINEAR:
                        Mouse.move(
                            target_x,
                            target_y,
                            duration=speed_to_int[move_speed],
                            tween=pyautogui.linear,
                        )
                    elif move_type == MoveType.SIMULATION:
                        Mouse.move_simulate(
                            target_x,
                            target_y,
                            duration=speed_to_int[move_speed],
                            tween=pyautogui.easeInOutQuad,
                        )
                    elif move_type == MoveType.TELEPORTATION:
                        Mouse.move(target_x, target_y, duration=0)
                    else:
                        raise NotImplementedError()

                    return True
                except Exception as e:
                    raise BaseException(MOUSE_HOVER_ERROR, "鼠标悬停失败")
            else:
                if time.time() - start_time > wait_time:
                    break
                else:
                    time.sleep(0.1)

        raise BaseException(CV_MATCH_ERROR, "超时未匹配到目标元素，请检查当前界面或降低匹配相似度重试")

    @staticmethod
    @atomicMg.atomic(
        "CV",
        inputList=[
            atomicMg.param(
                "input_data",
                formType=AtomicFormTypeMeta(AtomicFormType.PICK.value, params={"use": "CV"}),
                noInput=True,
            ),
            atomicMg.param("exist_type", required=False),
            atomicMg.param(
                "match_similarity",
                formType=AtomicFormTypeMeta(AtomicFormType.SLIDER.value),
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
        ],
    )
    def is_image_exist(
        input_data: IMGPick,
        exist_type: ExistType = ExistType.EXIST,
        match_similarity: float = 0.95,
        wait_time: int = 10,
    ):
        """
        判断图像是否存在
        :param input_data: 目标图像
        :param exist_type: 判断类型
        :param match_similarity: 匹配相似度
        :param wait_time: 等待时间
        :return: 图像是否存在的结果
        """
        start_time = time.time()

        while True:
            target_rect = CvCore.match_imgs(input_data, match_similarity)

            if exist_type == ExistType.EXIST:
                if target_rect is not None:
                    return True
            elif exist_type == ExistType.NOT_EXIST:
                if target_rect is None:
                    return True
            else:
                raise NotImplementedError()

            if time.time() - start_time > wait_time:
                break

            time.sleep(0.5)

        return False

    # @staticmethod
    # @atomicMg.atomic("CV")
    # def is_image_exist_end():
    #     pass

    @staticmethod
    @atomicMg.atomic(
        "CV",
        inputList=[
            atomicMg.param(
                "input_data",
                formType=AtomicFormTypeMeta(AtomicFormType.PICK.value, params={"use": "CV"}),
                noInput=True,
            ),
            atomicMg.param("wait_type", required=False),
            atomicMg.param("wait_time", types="Int", required=False),
            atomicMg.param(
                "match_similarity",
                formType=AtomicFormTypeMeta(AtomicFormType.SLIDER.value),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("image_wait_result", types="Bool")],
    )
    def wait_image(
        input_data: IMGPick,
        wait_type: WaitType = WaitType.APPEAR,
        wait_time: int = 10,
        match_similarity: float = 0.95,
    ):
        """
        等待图像出现或消失
        :param input_data: 目标图像
        :param wait_type: 等待类型
        :param wait_time: 超时时间
        :param match_similarity: 匹配相似度
        :return: 等待结果
        """
        start_time = time.time()

        if wait_type == WaitType.DISAPPEAR:
            target_rect = CvCore.match_imgs(input_data, match_similarity)
            if not target_rect:
                raise BaseException(TARGET_EXISTS_ERROR, "当前界面元素不存在，无法判断消失状态")

        while True:
            target_rect = CvCore.match_imgs(input_data, match_similarity)

            if wait_type == WaitType.APPEAR:
                if target_rect is not None:
                    return True
            elif wait_type == WaitType.DISAPPEAR:
                if target_rect is None:
                    return True
            else:
                raise NotImplementedError()

            if time.time() - start_time > wait_time:
                break

            time.sleep(0.5)

        return False

    @staticmethod
    @atomicMg.atomic(
        "CV",
        inputList=[
            atomicMg.param(
                "input_data",
                formType=AtomicFormTypeMeta(AtomicFormType.PICK.value, params={"use": "CV"}),
                noInput=True,
            ),
            atomicMg.param("input_type", required=False),
            atomicMg.param(
                "input_content",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.input_content.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param(
                "simulate_flag",
                formType=AtomicFormTypeMeta(AtomicFormType.SWITCH.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.simulate_flag.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "interval",
                types="Float",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.interval.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param("wait_time", types="Int", required=False),
            atomicMg.param(
                "match_similarity",
                formType=AtomicFormTypeMeta(AtomicFormType.SLIDER.value),
                required=False,
            ),
        ],
        outputList=[],
    )
    def image_input(
        input_data: IMGPick,
        input_type: InputType = InputType.TEXT,
        input_content: str = None,
        simulate_flag: Simulate_flag = Simulate_flag.YES,
        interval: float = 0.1,
        match_similarity: float = 0.95,
        wait_time: int = 10,
    ):
        """
        图像输入框输入
        :param input_data: 目标图像
        :param input_type: 输入类型
        :param input_content: 输入内容
        :param simulate_flag: 是否模拟输入
        :param interval: 模拟输入间隔
        :param wait_time: 等待时间
        :param match_similarity: 匹配相似度
        """
        start_time = time.time()
        while True:
            target_rect = CvCore.match_imgs(input_data, match_similarity)
            if target_rect is not None:
                try:
                    Mouse.click(
                        x=target_rect[0] + target_rect[2] / 2,
                        y=target_rect[1] + target_rect[3] / 2,
                    )
                    if input_type == InputType.TEXT:
                        message = str(input_content)
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
                    elif input_type == InputType.CLIP:
                        msg = Clipboard.paste()
                        if not msg:
                            raise BaseException(CLIP_PASTE_ERROR, "Clip is empty.")
                        else:
                            Keyboard.hotkey("ctrl", "v")
                            Clipboard.clear()
                    else:
                        raise NotImplementedError()

                    return True
                except Exception as e:
                    raise BaseException(CV_INPUT_ERROR, "输入失败，请检查输入信息")
            else:
                if time.time() - start_time > wait_time:
                    break
                else:
                    time.sleep(0.5)

        raise BaseException(CV_MATCH_ERROR, "超时未匹配到目标元素，请检查当前界面或降低匹配相似度重试")
