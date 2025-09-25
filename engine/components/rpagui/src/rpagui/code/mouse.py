import random
import time

import pyautogui
from rpagui import Speed

speed_to_int = {Speed.SLOW: 0.5, Speed.NORMAL: 1, Speed.FAST: 2}


class Mouse:
    def __int__(self):
        pyautogui.FAILSAFE = False

    @staticmethod
    def calculate_movement_duration(start_x: int, start_y: int, end_x: int, end_y: int, speed: Speed) -> float:
        """
        根据距离和速度计算移动所需时间。
        """
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        base_speed = 1000
        speed_multiplier = speed_to_int[speed]
        duration = distance / (base_speed * speed_multiplier)
        return max(0.1, duration)

    @staticmethod
    def position() -> (int, int):
        """
        鼠标位置
        """

        point = pyautogui.position()
        return point.x, point.y

    @staticmethod
    def move(x=None, y=None, duration: float = 0.0, tween=pyautogui.linear) -> None:
        """
        鼠标移动
        """
        return pyautogui.moveTo(x=x, y=y, duration=duration, tween=tween)

    @staticmethod
    def move_simulate(x=None, y=None, duration: float = 0.0, tween=pyautogui.linear) -> None:
        """
        鼠标模拟人工移动方式
        """
        start_x, start_y = Mouse.position()
        # 计算移动距离
        distance = ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5

        # 根据距离动态调整步数，减少步数以提高流畅度
        if distance < 300:
            steps = 1
        elif distance < 800:
            steps = 2
        else:
            steps = 3

        # 计算每步的时间间隔
        interval = duration / steps

        # 生成随机的缓动参数，使每次移动的曲线都不同
        ease_param = random.uniform(1.5, 2.5)  # 减小参数范围，使移动更平滑

        # 添加随机的起始延迟，模拟人类反应时间
        time.sleep(random.uniform(0.02, 0.05))  # 减少延迟时间

        # 分步移动
        for i in range(steps):
            t = i / steps
            # 使用改进的缓动函数，使移动更自然
            ease_t = t**ease_param / (t**ease_param + (1 - t) ** ease_param)

            # 计算当前步骤的目标位置
            new_x = start_x + (x - start_x) * ease_t
            new_y = start_y + (y - start_y) * ease_t

            # 添加微小的随机偏移，模拟手部抖动，但减小抖动范围
            if i < steps - 1:  # 最后一步不添加抖动
                new_x += random.uniform(-1, 1)
                new_y += random.uniform(-1, 1)

            # 使用pyautogui的moveTo函数，但减少调用次数
            pyautogui.moveTo(new_x, new_y, duration=interval, tween=pyautogui.easeInOutQuad)

        # 确保最终位置准确
        Mouse.move(x=x, y=y)

    @staticmethod
    def click(
        x=None,
        y=None,
        clicks=1,
        interval=0.0,
        button=pyautogui.PRIMARY,
        duration=0.0,
        tween=pyautogui.linear,
    ) -> None:
        """
        鼠标点击
        """
        return pyautogui.click(
            x=x,
            y=y,
            clicks=clicks,
            interval=interval,
            button=button,
            duration=duration,
            tween=tween,
        )

    @staticmethod
    def down(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        """
        鼠标按键
        """
        return pyautogui.mouseDown(x=x, y=y, button=button, duration=duration, tween=tween)

    @staticmethod
    def up(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        """
        鼠标松键
        """
        return pyautogui.mouseUp(x=x, y=y, button=button, duration=duration, tween=tween)

    @staticmethod
    def scroll(clicks, x=None, y=None):
        """
        鼠标滚动
        """
        return pyautogui.scroll(clicks=clicks, x=x, y=y)

    @staticmethod
    def screen_size() -> (int, int):
        """
        获取屏幕大小
        """
        return pyautogui.size()
