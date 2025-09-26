import os
import shutil
import tempfile
import unittest
from unittest import TestCase

from rpasystem import *
from rpasystem.clipboard import Clipboard


class TestClipboard(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        self.test_folder_path = os.path.join(self.temp_dir, "test_folder")

        # 创建测试文件和文件夹
        with open(self.test_file_path, "w") as f:
            f.write("测试文件内容")
        os.makedirs(self.test_folder_path, exist_ok=True)

        # 清空剪贴板，确保测试环境干净
        Clipboard.clear_clip()

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_copy_clip_message_success(self):
        """测试复制到剪贴板 - 文本消息成功"""
        test_message = "这是一个测试消息"

        # 复制消息到剪贴板
        Clipboard.copy_clip(content_type=ContentType.MSG, message=test_message)

        # 验证剪贴板内容
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, test_message)

    def test_copy_clip_message_empty(self):
        """测试复制到剪贴板 - 空消息"""
        with self.assertRaises(BaseException):
            Clipboard.copy_clip(content_type=ContentType.MSG, message="")

    def test_copy_clip_file_success(self):
        """测试复制到剪贴板 - 文件成功"""
        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=self.test_file_path)

        # 验证剪贴板中的文件路径
        result = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "test_file.txt")

    def test_copy_clip_file_not_exists(self):
        """测试复制到剪贴板 - 文件不存在"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.txt")
        with self.assertRaises(BaseException):
            Clipboard.copy_clip(content_type=ContentType.FILE, file_path=non_existent_file)

    def test_copy_clip_folder_success(self):
        """测试复制到剪贴板 - 文件夹成功"""
        # 复制文件夹到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FOLDER, folder_path=self.test_folder_path)

        # 验证剪贴板中的文件夹路径
        result = Clipboard.paste_clip(
            content_type=ContentType.FOLDER,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "test_folder")

    def test_copy_clip_folder_not_exists(self):
        """测试复制到剪贴板 - 文件夹不存在"""
        non_existent_folder = os.path.join(self.temp_dir, "non_existent_folder")
        with self.assertRaises(BaseException):
            Clipboard.copy_clip(content_type=ContentType.FOLDER, folder_path=non_existent_folder)

    def test_copy_clip_invalid_content_type(self):
        """测试复制到剪贴板 - 无效内容类型"""
        with self.assertRaises(NotImplementedError):
            Clipboard.copy_clip(content_type="invalid_type")

    def test_clear_clip_success(self):
        """测试清空剪贴板 - 成功"""
        # 先复制一些内容到剪贴板
        test_message = "测试消息"
        Clipboard.copy_clip(content_type=ContentType.MSG, message=test_message)

        # 验证剪贴板有内容
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, test_message)

        # 清空剪贴板
        Clipboard.clear_clip()

        # 验证剪贴板已清空
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, "")

    def test_paste_clip_message_success(self):
        """测试从剪贴板粘贴 - 文本消息成功"""
        expected_content = "粘贴的文本内容"

        # 复制内容到剪贴板
        Clipboard.copy_clip(content_type=ContentType.MSG, message=expected_content)

        # 从剪贴板粘贴
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, expected_content)

    def test_paste_clip_file_success(self):
        """测试从剪贴板粘贴 - 文件成功"""
        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=self.test_file_path)

        # 从剪贴板粘贴文件
        result = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "test_file.txt")

    def test_paste_clip_file_with_custom_name(self):
        """测试从剪贴板粘贴 - 文件带自定义名称"""
        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=self.test_file_path)

        # 从剪贴板粘贴文件，使用自定义名称
        result = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
            dst_file_name="custom_name",
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "custom_name.txt")

    def test_paste_clip_folder_success(self):
        """测试从剪贴板粘贴 - 文件夹成功"""
        # 复制文件夹到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FOLDER, folder_path=self.test_folder_path)

        # 从剪贴板粘贴文件夹
        result = Clipboard.paste_clip(
            content_type=ContentType.FOLDER,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "test_folder")

    def test_paste_clip_folder_with_custom_name(self):
        """测试从剪贴板粘贴 - 文件夹带自定义名称"""
        # 复制文件夹到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FOLDER, folder_path=self.test_folder_path)

        # 从剪贴板粘贴文件夹，使用自定义名称
        result = Clipboard.paste_clip(
            content_type=ContentType.FOLDER,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
            dst_folder_name="custom_folder_name",
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "custom_folder_name")

    def test_paste_clip_folder_not_exists_error(self):
        """测试从剪贴板粘贴 - 目标文件夹不存在且设置为错误"""
        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=self.test_file_path)

        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Clipboard.paste_clip(
                content_type=ContentType.FILE,
                dst_path=non_existent_dir,
                state_type=StateType.ERROR,
            )

    def test_paste_clip_folder_not_exists_create(self):
        """测试从剪贴板粘贴 - 目标文件夹不存在但自动创建"""
        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=self.test_file_path)

        new_dir = os.path.join(self.temp_dir, "new_dir")
        result = Clipboard.paste_clip(content_type=ContentType.FILE, dst_path=new_dir, state_type=StateType.CREATE)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.exists(new_dir))

    def test_paste_clip_invalid_content_type(self):
        """测试从剪贴板粘贴 - 无效内容类型"""
        with self.assertRaises(NotImplementedError):
            Clipboard.paste_clip(content_type="invalid_type")

    def test_copy_clip_message_with_special_characters(self):
        """测试复制到剪贴板 - 包含特殊字符的消息"""
        special_message = "测试消息：包含中文、英文、数字123和特殊符号！@#￥%"

        # 复制特殊字符消息到剪贴板
        Clipboard.copy_clip(content_type=ContentType.MSG, message=special_message)

        # 验证剪贴板内容
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, special_message)

    def test_copy_clip_multiple_files(self):
        """测试复制到剪贴板 - 多个文件"""
        # 创建多个测试文件
        files = ["file1.txt", "file2.txt", "file3.txt"]
        for file_name in files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write(f"content for {file_name}")

        # 测试复制第一个文件
        first_file = os.path.join(self.temp_dir, "file1.txt")
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=first_file)

        # 验证剪贴板中的文件
        result = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "file1.txt")

    def test_paste_clip_empty_content(self):
        """测试从剪贴板粘贴 - 空内容"""
        # 清空剪贴板
        Clipboard.clear_clip()

        # 验证剪贴板为空
        result = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(result, "")

    def test_copy_clip_file_with_spaces_in_path(self):
        """测试复制到剪贴板 - 路径包含空格的文件"""
        file_with_spaces = os.path.join(self.temp_dir, "file with spaces.txt")
        with open(file_with_spaces, "w") as f:
            f.write("content")

        # 复制包含空格的文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=file_with_spaces)

        # 验证剪贴板中的文件
        result = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "file with spaces.txt")

    def test_copy_clip_folder_with_spaces_in_path(self):
        """测试复制到剪贴板 - 路径包含空格的文件夹"""
        folder_with_spaces = os.path.join(self.temp_dir, "folder with spaces")
        os.makedirs(folder_with_spaces, exist_ok=True)

        # 复制包含空格的文件夹到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FOLDER, folder_path=folder_with_spaces)

        # 验证剪贴板中的文件夹
        result = Clipboard.paste_clip(
            content_type=ContentType.FOLDER,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), "folder with spaces")

    def test_copy_and_paste_cycle(self):
        """测试复制粘贴循环 - 确保数据完整性"""
        original_message = "原始测试消息"

        # 复制消息
        Clipboard.copy_clip(content_type=ContentType.MSG, message=original_message)

        # 粘贴并验证
        pasted_message = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(pasted_message, original_message)

        # 再次复制粘贴，确保剪贴板功能正常
        Clipboard.copy_clip(content_type=ContentType.MSG, message=pasted_message)
        final_message = Clipboard.paste_clip(content_type=ContentType.MSG)
        self.assertEqual(final_message, original_message)

    def test_file_content_integrity(self):
        """测试文件内容完整性"""
        original_content = "这是原始文件内容"

        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "content_test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(original_content)

        # 复制文件到剪贴板
        Clipboard.copy_clip(content_type=ContentType.FILE, file_path=test_file)

        # 粘贴文件
        pasted_file = Clipboard.paste_clip(
            content_type=ContentType.FILE,
            dst_path=self.temp_dir,
            state_type=StateType.ERROR,
        )

        # 验证文件内容
        with open(pasted_file, encoding="utf-8") as f:
            pasted_content = f.read()

        self.assertEqual(pasted_content, original_content)


if __name__ == "__main__":
    unittest.main()
