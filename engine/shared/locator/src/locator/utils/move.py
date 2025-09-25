import math
import random
import time

import pyautogui
import uiautomation as auto

pyautogui.FAILSAFE = False


def generate_smooth_path(start_x, start_y, end_x, end_y, duration=1.0):
    """生成平滑移动路径(三次贝塞尔曲线变体)"""
    num_points = max(30, int(duration * 60))

    # 生成中间控制点（确保方向一致性）
    dx = end_x - start_x
    dy = end_y - start_y
    dist = math.hypot(dx, dy)

    ctrl1 = (
        start_x + dx * 0.3 + random.uniform(-dist * 0.1, dist * 0.1),
        start_y + dy * 0.3 + random.uniform(-dist * 0.1, dist * 0.1),
    )
    ctrl2 = (
        start_x + dx * 0.7 + random.uniform(-dist * 0.1, dist * 0.1),
        start_y + dy * 0.7 + random.uniform(-dist * 0.1, dist * 0.1),
    )

    path = []
    for t in (i / num_points for i in range(num_points + 1)):
        # 三次贝塞尔公式
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * ctrl1[0] + 3 * (1 - t) * t**2 * ctrl2[0] + t**3 * end_x
        y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * ctrl1[1] + 3 * (1 - t) * t**2 * ctrl2[1] + t**3 * end_y
        path.append((int(x), int(y)))
    return path


def smooth_move(end_x, end_y, duration=0.4):
    # 解决鼠标在副屏的问题
    p_x, p_y = auto.GetCursorPos()
    sc_w, sc_h = pyautogui.size()
    if p_x > sc_w or p_y > sc_h:
        pyautogui.moveTo(sc_w // 2, sc_h // 2)

    start_x, start_y = pyautogui.position()
    path = generate_smooth_path(start_x, start_y, end_x, end_y, duration)

    def ease(t):
        return t * t * (3 - 2 * t)  # 平滑加速减速

    # 时间分配
    total_points = len(path)
    time_per_point = duration / total_points

    # 执行移动
    start_time = time.time()

    path_len = len(path)

    for i, (x, y) in enumerate(path):
        if i != (path_len - 1):
            # 计算动态时间间隔
            ideal_time = start_time + ease(i / total_points) * duration
            actual_time = time.time()

            # 跳过延迟过大的帧
            if actual_time > ideal_time + time_per_point * 0.5:
                continue

            # 精确时间控制
            sleep_time = max(0, ideal_time - actual_time - 0.001)
            if sleep_time > 0:
                time.sleep(sleep_time)

            # 添加微小随机扰动（幅度更小）
            x += random.randint(-1, 1)
            y += random.randint(-1, 1)
        # 移动鼠标
        pyautogui.moveTo(x, y)
