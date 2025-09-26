import pyautogui
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg

from rpagui import (
    BtnModel,
    BtnType,
    ControlType,
    Direction,
    MoveType,
    ScrollType,
    Speed,
    WindowType,
)
from rpagui.code.keyboard import Keyboard
from rpagui.code.mouse import Mouse
from rpagui.error import *


class GuiMouse:
    @staticmethod
    @atomicMg.atomic("Gui", inputList=[atomicMg.param("ctrl_type", level=AtomicLevel.ADVANCED.value)])
    def mouse(
        btn_type: BtnType = BtnType.LEFT,
        btn_model: BtnModel = BtnModel.CLICK,
        ctrl_type: ControlType = ControlType.EMPTY,
    ):
        """
        鼠标点击
        :param btn_type: 鼠标按键类型   LEFT:左键，RIGHT:右键，MIDDLE:中键
        :param btn_model: 鼠标按键模式  Click:单击, DoubleClick:双击, Down:按下, Up:松开
        :param ctrl_type: 辅助按键类型  无/Ctrl/Alt/Shift/Win/Shape
        """
        # 按下辅助按键
        if ctrl_type != ControlType.EMPTY:
            Keyboard.key_down(ctrl_type.value)
        try:
            if btn_model == BtnModel.CLICK:
                Mouse.click(None, None, 1, 0, btn_type.value)
            elif btn_model == BtnModel.DOUBLE_CLICK:
                Mouse.click(None, None, 2, 0, btn_type.value)
            elif btn_model == BtnModel.DOWN:
                Mouse.down(None, None, btn_type.value)
            elif btn_model == BtnModel.UP:
                Mouse.up(None, None, btn_type.value)
            else:
                raise NotImplementedError()
        finally:
            # 松开辅助按键
            if ctrl_type != ControlType.EMPTY:
                Keyboard.key_up(ctrl_type.value)

    @staticmethod
    @atomicMg.atomic(
        "Gui",
        inputList=[
            atomicMg.param(
                "times",
                dynamics=[
                    DynamicsItem(
                        key="$this.times.show",
                        expression="return $this.scroll_type.value == '{}'".format(ScrollType.TIME.value),
                    )
                ],
            ),
            atomicMg.param(
                "scroll_px",
                dynamics=[
                    DynamicsItem(
                        key="$this.scroll_px.show",
                        expression="return $this.scroll_type.value == '{}'".format(ScrollType.PX.value),
                    )
                ],
            ),
            atomicMg.param(
                "ctrl_type",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.ctrl_type.show",
                        expression="return ['{}', '{}'].includes($this.scroll_type.value)".format(
                            ScrollType.PX.value, ScrollType.TIME.value
                        ),
                    )
                ],
            ),
        ],
    )
    def mouse_wheel(
        scroll_type: ScrollType = ScrollType.TIME,
        times: int = 1,
        scroll_px: int = 120,
        direction: Direction = Direction.DOWN,
        ctrl_type: ControlType = ControlType.EMPTY,
    ):
        """
        鼠标滚轮
        :param scroll_type: 滚轮类型  次数/像素
        :param times: 滚轮次数
        :param scroll_px: 滚轮像素
        :param direction: 滚轮方向      上/下
        :param ctrl_type: 辅助按键类型  无/Ctrl/Alt/Shift/Win/Shape
        """
        if not isinstance(scroll_type, ScrollType):
            raise ValueError("Invalid scroll_type")
        if not isinstance(direction, Direction):
            raise ValueError("Invalid direction")
        if not isinstance(ctrl_type, ControlType):
            raise ValueError("Invalid ctrl_type")

        if scroll_type == ScrollType.TIME:
            scroll_px = 120
        elif scroll_type == ScrollType.PX:
            times = 1
        else:
            raise NotImplementedError()

        reversal = -1 if direction == Direction.DOWN else 1

        if ctrl_type != ControlType.EMPTY:
            Keyboard.key_down(ctrl_type.value)
        try:
            for _ in range(times):
                try:
                    Mouse.scroll(scroll_px * reversal)
                except Exception as e:
                    raise BaseException(
                        SCROLL_FAILURE,
                        "滑轮滚动过程中失败, 请检查环境是否出现异常 {}".format(e),
                    )
        finally:
            # 松开辅助按键
            if ctrl_type != ControlType.EMPTY:
                Keyboard.key_up(ctrl_type.value)

    @staticmethod
    @atomicMg.atomic(
        "Gui",
        inputList=[
            atomicMg.param(
                "window_position",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.window_position.show",
                        expression="return $this.window_type.value == '{}'".format(WindowType.ACTIVE_WINDOW.value),
                    )
                ],
            ),
            atomicMg.param(
                "get_mouse_position",
                formType=AtomicFormTypeMeta(type=AtomicFormType.MOUSEPOSITION.value, params={"size": "middle"}),
                required=False,
            ),
            atomicMg.param(
                "position_x",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "position_y",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "move_speed",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.move_speed.show",
                        expression="return ['{}', '{}'].includes($this.move_type.value)".format(
                            MoveType.LINEAR.value, MoveType.SIMULATION.value
                        ),
                    )
                ],
            ),
        ],
    )
    def mouse_move(
        window_type: WindowType = WindowType.FULL_SCREEN,
        window_position: list = None,
        get_mouse_position: str = "",
        position_x: int = None,
        position_y: int = None,
        move_type: MoveType = MoveType.LINEAR,
        move_speed: Speed = Speed.NORMAL,
    ):
        """
        :param window_type: 窗口类型  全屏/活动窗口
        :param window_position: 激活窗口左上角坐标
        :param position_x: 移动终点位置x坐标
        :param position_y: 移动终点位置y坐标
        :param move_speed: 移动速度    高/中/低
        :param move_type: 移动方式     LINEAR:线性移动，SIMULATION:模拟移动，TELEPORTATION:瞬移
        """
        if window_type == WindowType.ACTIVE_WINDOW and window_position is not None:
            position_x = window_position[0] + position_x
            position_y = window_position[1] + position_y

        screen_weight, screen_height = Mouse.screen_size()
        if position_x < 0 or position_x > screen_weight or position_y < 0 or position_y > screen_height:
            raise BaseException(REGION_ERROR, "坐标参数不合法！")

        # Get current mouse position
        current_x, current_y = Mouse.position()

        if move_type == MoveType.LINEAR:
            duration = Mouse.calculate_movement_duration(current_x, current_y, position_x, position_y, move_speed)
            Mouse.move(position_x, position_y, duration=duration, tween=pyautogui.linear)
        elif move_type == MoveType.SIMULATION:
            duration = Mouse.calculate_movement_duration(current_x, current_y, position_x, position_y, move_speed)
            Mouse.move_simulate(position_x, position_y, duration=duration, tween=pyautogui.easeInOutQuad)
        elif move_type == MoveType.TELEPORTATION:
            Mouse.move(position_x, position_y, duration=0)
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "Gui",
        inputList=[
            atomicMg.param(
                "start_pos_x",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "start_pos_y",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "end_pos_x",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "end_pos_y",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param(
                "move_speed",
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.move_speed.show",
                        expression="return ['{}', '{}'].includes($this.move_type.value)".format(
                            MoveType.LINEAR.value, MoveType.SIMULATION.value
                        ),
                    )
                ],
            ),
            atomicMg.param("ctrl_type", level=AtomicLevel.ADVANCED.value),
        ],
    )
    def mouse_drag(
        start_pos_x: int = None,
        start_pos_y: int = None,
        end_pos_x: int = None,
        end_pos_y: int = None,
        btn_type: BtnType = BtnType.LEFT,
        move_type: MoveType = MoveType.LINEAR,
        move_speed: Speed = Speed.NORMAL,
        ctrl_type: ControlType = ControlType.EMPTY,
    ):
        """
        鼠标拖拽
        :param start_pos_x: 起始位置x
        :param start_pos_y: 起始位置y
        :param end_pos_x: 结束位置x
        :param end_pos_y: 结束位置y
        :param btn_type: 按键类型        LEFT:左键，RIGHT:右键，MIDDLE:中键
        :param move_type: 移动类型       LINEAR:线性移动，SIMULATION:模拟移动，TELEPORTATION:瞬移
        :param move_speed: 移动速度      高/中/低
        :param ctrl_type: 键盘辅助按键   无/Ctrl/Alt/Shift/Win/Shape

        :return: None
        """
        screen_weight, screen_height = Mouse.screen_size()
        if (
            start_pos_x < 0
            or start_pos_x > screen_weight
            or start_pos_y < 0
            or start_pos_y > screen_height
            or end_pos_x < 0
            or end_pos_x > screen_weight
            or end_pos_y < 0
            or end_pos_y > screen_height
        ):
            raise BaseException(REGION_ERROR, "坐标参数不合法！")

        if ctrl_type != ControlType.EMPTY:
            Keyboard.key_down(ctrl_type.value)
        try:
            Mouse.down(x=start_pos_x, y=start_pos_y, button=btn_type.value)
            if move_type == MoveType.LINEAR:
                duration = Mouse.calculate_movement_duration(start_pos_x, start_pos_y, end_pos_x, end_pos_y, move_speed)
                Mouse.move(x=end_pos_x, y=end_pos_y, duration=duration, tween=pyautogui.linear)
            elif move_type == MoveType.SIMULATION:
                duration = Mouse.calculate_movement_duration(start_pos_x, start_pos_y, end_pos_x, end_pos_y, move_speed)
                Mouse.move_simulate(
                    x=end_pos_x,
                    y=end_pos_y,
                    duration=duration,
                    tween=pyautogui.easeInOutQuad,
                )
            elif move_type == MoveType.TELEPORTATION:
                Mouse.move(x=end_pos_x, y=end_pos_y, duration=0)
            else:
                raise NotImplementedError()
            Mouse.up(button=btn_type.value)
        finally:
            if ctrl_type != ControlType.EMPTY:
                Keyboard.key_up(ctrl_type.value)

    @staticmethod
    @atomicMg.atomic(
        "Gui",
        outputList=[
            atomicMg.param(
                "point_x",
                types="Int",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RESULT.value),
            ),
            atomicMg.param(
                "point_y",
                types="Int",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RESULT.value),
            ),
        ],
    )
    def mouse_position() -> (int, int):
        """获取鼠标位置"""
        point_x, point_y = Mouse.position()
        return point_x, point_y
