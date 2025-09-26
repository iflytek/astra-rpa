import time
from unittest import TestCase

from rpagui import (
    BtnModel,
    BtnType,
    ControlType,
    Direction,
    KeyboardType,
    MoveType,
    ScrollType,
    Speed,
    WindowType,
)
from rpagui.gui import Gui


class TestMouse(TestCase):
    def test_mouse_position(self):
        position = Gui.mouse_position()
        print(position)
        print(type(position))

    def test_move(self):
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=150, position_y=150, move_speed=Speed.SLOW, move_type=MoveType.LINEAR)
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=324, position_y=150, move_speed=Speed.NORMAL, move_type=MoveType.LINEAR)
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=500, position_y=150, move_speed=Speed.FAST, move_type=MoveType.LINEAR)

        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN,  position_x=895, position_y=150, move_speed=Speed.FAST, move_type=MoveType.SIMULATION)
        Gui.mouse_move(
            window_type=WindowType.FULL_SCREEN,
            position_x=100,
            position_y=100,
            move_speed=Speed.NORMAL,
            move_type=MoveType.SIMULATION,
        )
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=500, position_y=150, move_speed=Speed.SLOW, move_type=MoveType.SIMULATION)

        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=150, position_y=150, move_speed=Speed.SLOW, move_type=MoveType.TELEPORTATION)
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=324, position_y=150, move_speed=Speed.NORMAL, move_type=MoveType.TELEPORTATION)
        # Gui.mouse_move(window_type=WindowType.FULL_SCREEN, position_x=500, position_y=150, move_speed=Speed.FAST, move_type=MoveType.TELEPORTATION)

    def test_click(self):
        Gui.mouse(
            btn_type=BtnType.LEFT,
            btn_model=BtnModel.DOUBLE_CLICK,
            ctrl_type=ControlType.WIN,
        )
        print("鼠标左键双击")
        time.sleep(2)

        Gui.mouse(btn_type=BtnType.RIGHT, btn_model=BtnModel.DOWN, ctrl_type=ControlType.EMPTY)
        print("鼠标右键按下")
        time.sleep(2)
        Gui.mouse(btn_type=BtnType.RIGHT, btn_model=BtnModel.UP, ctrl_type=ControlType.EMPTY)
        print("鼠标右键释放")
        time.sleep(2)

        Gui.mouse(btn_type=BtnType.LEFT, btn_model=BtnModel.CLICK, ctrl_type=ControlType.EMPTY)

        Gui.mouse(
            btn_type=BtnType.MIDDLE,
            btn_model=BtnModel.DOWN,
            ctrl_type=ControlType.EMPTY,
        )
        print("鼠标中键按下")
        time.sleep(2)
        Gui.mouse(btn_type=BtnType.MIDDLE, btn_model=BtnModel.UP, ctrl_type=ControlType.EMPTY)
        print("鼠标中键释放")
        time.sleep(2)

        Gui.mouse(
            btn_type=BtnType.RIGHT,
            btn_model=BtnModel.DOUBLE_CLICK,
            ctrl_type=ControlType.EMPTY,
        )
        print("鼠标右键双击")

    def test_scroll(self):
        Gui.mouse_wheel(
            scroll_type=ScrollType.TIME,
            direction=Direction.UP,
            ctrl_type=ControlType.EMPTY,
        )
        time.sleep(2)
        Gui.mouse_wheel(
            scroll_type=ScrollType.TIME,
            direction=Direction.DOWN,
            ctrl_type=ControlType.EMPTY,
        )
        time.sleep(2)
        Gui.mouse_wheel(
            scroll_type=ScrollType.TIME,
            direction=Direction.DOWN,
            ctrl_type=ControlType.SHIFT,
        )
        time.sleep(2)
        Gui.mouse_wheel(
            scroll_type=ScrollType.TIME,
            direction=Direction.UP,
            ctrl_type=ControlType.SHIFT,
        )

    def test_drag(self):
        Gui.mouse_drag(
            start_pos_x=150,
            start_pos_y=200,
            end_pos_x=200,
            end_pos_y=200,
            btn_type=BtnType.LEFT,
            move_speed=Speed.NORMAL,
            move_type=MoveType.LINEAR,
            ctrl_type=ControlType.EMPTY,
        )

        # Gui.mouse_drag(start_pos_x=150, start_pos_y=200, end_pos_x=400, end_pos_y=200, btn_type=BtnType.LEFT, move_speed=Speed.NORMAL, move_type=MoveType.SIMULATION, ctrl_type=ControlType.EMPTY)

        # Gui.mouse_drag(start_pos_x=150, start_pos_y=200, end_pos_x=200, end_pos_y=200, btn_type=BtnType.LEFT, move_speed=Speed.NORMAL, move_type=MoveType.TELEPORTATION)


class TestKeyboard(TestCase):
    def test_input(self):
        gui = Gui()
        # gui.keyboard(keyboard_type = KeyboardType.NORMAL, message="&#   ￥W……&￥#……#￥%换行和空格", simulate_flag=Simulate_flag.YES, interval=0.1)
        # gui.keyboard(keyboard_type = KeyboardType.NORMAL, message="change获取中文内容", simulate_flag=Simulate_flag.NO, interval=0.5)
        # gui.keyboard(keyboard_type = KeyboardType.KEY, keys_str="ctrl, v", simulate_flag=True, interval=0.1)
        # clipboard.Clipboard.clear()
        # gui.keyboard(keyboard_type = KeyboardType.CLIP)
        # print(clipboard.Clipboard.get())
        gui.keyboard(
            keyboard_type=KeyboardType.DRIVER,
            message="dewf241531@%#%!#!#&*()",
            interval=0.1,
        )
        # gui.keyboard(keyboard_type=KeyboardType.DRIVER, message="dewf2415", interval=0.1)
