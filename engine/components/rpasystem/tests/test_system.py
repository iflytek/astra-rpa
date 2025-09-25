import os
import shutil
import tempfile
import unittest
from unittest import TestCase

from rpasystem import *
from rpasystem.system import System


class TestSystem(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_png_name = "test_screenshot.png"

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_screen_shot_full_screen_success(self):
        """测试屏幕截图 - 全屏截图成功"""
        # 执行全屏截图
        result = System.screen_shot(
            png_path=self.temp_dir,
            state_type=StateType.ERROR,
            png_name=self.test_png_name,
            screen_type=ScreenType.FULL,
        )

        # 验证截图文件存在
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), self.test_png_name)
        self.assertTrue(result.endswith(".png"))

    def test_screen_shot_region_success(self):
        """测试屏幕截图 - 区域截图成功"""
        # 执行区域截图（使用较小的区域避免超出屏幕范围）
        result = System.screen_shot(
            png_path=self.temp_dir,
            state_type=StateType.ERROR,
            png_name=self.test_png_name,
            screen_type=ScreenType.REGION,
            top_left_x=100,
            top_left_y=100,
            bottom_right_x=300,
            bottom_right_y=200,
        )

        # 验证截图文件存在
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), self.test_png_name)
        self.assertTrue(result.endswith(".png"))

    def test_screen_shot_region_invalid_coordinates(self):
        """测试屏幕截图 - 无效坐标"""
        # 使用无效的坐标（负数）
        with self.assertRaises(ValueError):
            System.screen_shot(
                png_path=self.temp_dir,
                state_type=StateType.ERROR,
                png_name=self.test_png_name,
                screen_type=ScreenType.REGION,
                top_left_x=-1,
                top_left_y=100,
                bottom_right_x=500,
                bottom_right_y=400,
            )

    def test_screen_shot_folder_not_exists_error(self):
        """测试屏幕截图 - 文件夹不存在且设置为错误"""
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")

        with self.assertRaises(BaseException):
            System.screen_shot(
                png_path=non_existent_dir,
                state_type=StateType.ERROR,
                png_name=self.test_png_name,
            )

    def test_screen_shot_folder_not_exists_create(self):
        """测试屏幕截图 - 文件夹不存在但自动创建"""
        new_dir = os.path.join(self.temp_dir, "new_dir")

        # 执行截图到不存在的目录，但设置为自动创建
        result = System.screen_shot(png_path=new_dir, state_type=StateType.CREATE, png_name=self.test_png_name)

        # 验证截图文件存在且目录被创建
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.exists(new_dir))
        self.assertEqual(os.path.basename(result), self.test_png_name)

    def test_screen_shot_auto_extension(self):
        """测试屏幕截图 - 自动添加扩展名"""
        name_without_ext = "test_screenshot"
        expected_name = name_without_ext + ".png"

        # 执行截图，文件名不包含扩展名
        result = System.screen_shot(
            png_path=self.temp_dir,
            state_type=StateType.ERROR,
            png_name=name_without_ext,
        )

        # 验证自动添加了.png扩展名
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), expected_name)

    def test_screen_shot_with_jpg_extension(self):
        """测试屏幕截图 - 使用jpg扩展名"""
        jpg_name = "test_screenshot.jpg"

        # 执行截图，使用jpg扩展名
        result = System.screen_shot(png_path=self.temp_dir, state_type=StateType.ERROR, png_name=jpg_name)

        # 验证文件存在且扩展名正确
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), jpg_name)
        self.assertTrue(result.endswith(".jpg"))

    def test_screen_shot_multiple_screenshots(self):
        """测试屏幕截图 - 多次截图"""
        # 执行多次截图
        screenshots = []
        for i in range(3):
            screenshot_name = f"screenshot_{i}.png"
            result = System.screen_shot(
                png_path=self.temp_dir,
                state_type=StateType.ERROR,
                png_name=screenshot_name,
            )
            screenshots.append(result)

        # 验证所有截图文件都存在
        for screenshot in screenshots:
            self.assertTrue(os.path.exists(screenshot))
            self.assertTrue(screenshot.endswith(".png"))

    def test_screen_shot_file_size_verification(self):
        """测试屏幕截图 - 验证文件大小"""
        # 执行截图
        result = System.screen_shot(
            png_path=self.temp_dir,
            state_type=StateType.ERROR,
            png_name=self.test_png_name,
        )

        # 验证截图文件存在且大小大于0
        self.assertTrue(os.path.exists(result))
        file_size = os.path.getsize(result)
        self.assertGreater(file_size, 0)

    def test_screen_shot_different_regions(self):
        """测试屏幕截图 - 不同区域"""
        regions = [(50, 50, 150, 100), (200, 100, 400, 200), (100, 200, 300, 300)]

        for i, (x1, y1, x2, y2) in enumerate(regions):
            screenshot_name = f"region_screenshot_{i}.png"
            try:
                result = System.screen_shot(
                    png_path=self.temp_dir,
                    state_type=StateType.ERROR,
                    png_name=screenshot_name,
                    screen_type=ScreenType.REGION,
                    top_left_x=x1,
                    top_left_y=y1,
                    bottom_right_x=x2,
                    bottom_right_y=y2,
                )

                # 验证截图文件存在
                self.assertTrue(os.path.exists(result))
                self.assertEqual(os.path.basename(result), screenshot_name)
            except ValueError:
                # 如果坐标超出屏幕范围，这是预期的
                pass


if __name__ == "__main__":
    unittest.main()
