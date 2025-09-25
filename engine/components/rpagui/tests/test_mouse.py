import os
import sys

print(os.path.dirname((os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest import TestCase

from rpagui import BtnModel, BtnType, Direction, KeyboardType, ScrollType
from rpagui.gui import Gui, Mouse


class TestMouse(TestCase):
    def test_position(self):
        print(Mouse.position())

    def test_mouse_position(self):
        print(Gui.mouse_position())

    def test_move(self):
        Mouse.move(233, 233, 0.1)


class TestKeyboard(TestCase):
    def test_input(self):
        gui = Gui()
        gui.keyboard(keyboard_type=KeyboardType.CLIP)


# test_mou = TestMouse()
# test_mou.test_mouse_position()
# print(dir(ShortcutType))

test_key = TestKeyboard()
test_key.test_input()
