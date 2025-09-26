import time

from rpaatomic.types import WinPick
from rpaatomic.utils import FileExistenceType
from rpawinele import MouseClickButton, MouseClickType
from rpawinele.core_win import WinEleCore
from rpawinele.winele import WinEle


def demo():
    """演示核心原子能力"""
    print("🚀 开始演示 RPA Winele 元素操作核心能力...")
    print("=" * 60)

    # 创建测试用的WinPick对象
    test_pick_data = {
        "elementData": {
            "version": "1",
            "type": "uia",
            "app": "explorer",
            "path": [
                {
                    "cls": "Progman",
                    "name": "Program Manager",
                    "tag_name": "PaneControl",
                    "index": 13,
                    "value": None,
                },
                {
                    "cls": "SHELLDLL_DefView",
                    "name": "",
                    "tag_name": "PaneControl",
                    "index": 0,
                    "value": None,
                },
                {
                    "cls": "SysListView32",
                    "name": "桌面",
                    "tag_name": "ListControl",
                    "index": 0,
                    "value": None,
                },
                {
                    "cls": "",
                    "name": "此电脑",
                    "tag_name": "ListItemControl",
                    "index": 0,
                    "value": None,
                },
            ],
            "img": {"self": ""},
            "picker_type": "ELEMENT",
        }
    }

    test_pick = WinPick(test_pick_data)

    print("📋 演示内容:")
    print("1. 元素查找 (find)")
    print("2. 元素点击 (click_element)")
    print("3. 元素悬停 (hover_element)")
    print("4. 元素截图 (screenshot_element)")
    print("5. 性能测试")
    print("=" * 60)

    try:
        # 1. 元素查找演示
        print("\n🔍 1. 元素查找演示")
        print("-" * 30)

        start_time = time.time()
        locator = WinEleCore.find(pick=test_pick, wait_time=5.0)
        find_time = time.time() - start_time

        if locator:
            point = locator.point()
            print("✅ 元素查找成功!")
            print(f"   执行时间: {find_time:.3f}秒")
            print(f"   元素位置: ({point.x}, {point.y})")

            # 获取元素矩形信息
            rect = locator.rect()
            print(f"   元素大小: {rect.width()} x {rect.height()}")
        else:
            print("❌ 元素查找失败")
            return

        # 2. 元素点击演示
        print("\n🖱️ 2. 元素点击演示")
        print("-" * 30)

        # 左键单击
        print("   执行左键单击...")
        start_time = time.time()
        WinEle.click_element(
            pick=test_pick,
            click_button=MouseClickButton.LEFT,
            click_type=MouseClickType.CLICK,
            wait_time=5.0,
        )
        click_time = time.time() - start_time
        print(f"✅ 左键单击完成 - 耗时: {click_time:.3f}秒")

        # 3. 元素悬停演示
        print("\n🖱️ 3. 元素悬停演示")
        print("-" * 30)

        start_time = time.time()
        WinEle.hover_element(pick=test_pick, wait_time=5.0)
        hover_time = time.time() - start_time
        print(f"✅ 元素悬停完成 - 耗时: {hover_time:.3f}秒")

        # 4. 元素截图演示
        print("\n📸 4. 元素截图演示")
        print("-" * 30)

        start_time = time.time()
        WinEle.screenshot_element(
            pick=test_pick,
            file_path="./",
            file_name="demo_screenshot",
            exist_type=FileExistenceType.OVERWRITE,
        )
        screenshot_time = time.time() - start_time
        print(f"✅ 元素截图完成 - 耗时: {screenshot_time:.3f}秒")
        print("   截图保存路径: ./demo_screenshot.png")

        # 5. 性能测试演示
        print("\n⚡ 5. 性能测试演示")
        print("-" * 30)

        test_iterations = 3
        execution_times = []

        print(f"   执行 {test_iterations} 次元素查找性能测试...")

        for i in range(test_iterations):
            start_time = time.time()
            try:
                locator = WinEleCore.find(pick=test_pick, wait_time=3.0)
                point = locator.point()
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                print(f"   第 {i + 1} 次: {execution_time:.3f}秒")
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   第 {i + 1} 次: {execution_time:.3f}秒 - 失败: {str(e)}")

        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)

            print("\n📊 性能测试结果:")
            print(f"   平均执行时间: {avg_time:.3f}秒")
            print(f"   最快执行时间: {min_time:.3f}秒")
            print(f"   最慢执行时间: {max_time:.3f}秒")
            print(f"   执行次数: {len(execution_times)}")

            if avg_time < 3.0:
                print("✅ 性能表现良好")
            else:
                print("⚠️ 性能需要优化")

        print("\n🎉 所有演示完成!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 演示过程中出现异常: {e}")
        print("   这可能是由于目标元素不存在或系统环境问题")
        print("   请确保桌面上有'此电脑'元素，或者修改测试元素")


if __name__ == "__main__":
    demo()
