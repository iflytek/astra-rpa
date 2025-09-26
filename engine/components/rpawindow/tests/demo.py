import time

from rpawindow.core import WindowExistType, WindowSizeType
from rpawindow.window import Window


def demo():
    """演示核心原子能力"""
    print("🚀 开始演示 RPA Windows 元素操作核心能力...")
    print("用户请先打开一个 此电脑 窗口")
    print("=" * 60)

    # 创建测试用的WinPick对象
    test_pick = {"elementData": {"path": [{"name": "此电脑 - 文件资源管理器", "cls": "CabinetWClass"}]}}

    try:
        # exist方法
        Window.exist(pick=test_pick, check_type=WindowExistType.EXIST, wait_time=0)
        time.sleep(1)
        # top方法
        Window.top(pick=test_pick)
        time.sleep(1)
        # set_size方法
        Window.set_size(pick=test_pick, size_type=WindowSizeType.MAX, width=0, height=0)
        time.sleep(1)
        Window.set_size(pick=test_pick, size_type=WindowSizeType.CUSTOM, width=200, height=200)
        time.sleep(1)
        Window.set_size(pick=test_pick, size_type=WindowSizeType.MIN, width=0, height=0)
        time.sleep(1)
        Window.set_size(pick=test_pick, size_type=WindowSizeType.CUSTOM, width=400, height=400)
        time.sleep(1)
        Window.set_size(pick=test_pick, size_type=WindowSizeType.MAX, width=0, height=0)
        time.sleep(1)
        Window.set_size(pick=test_pick, size_type=WindowSizeType.MIN, width=0, height=0)
        time.sleep(1)
        # close方法
        Window.close(pick=test_pick)
        print("演示完成")
    except Exception as e:
        print(f"演示出现异常: {e}")


if __name__ == "__main__":
    demo()
