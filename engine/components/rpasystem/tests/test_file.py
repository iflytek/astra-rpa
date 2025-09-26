import os
import shutil
import tempfile
import unittest
from unittest import TestCase, mock

from rpasystem import *
from rpasystem.file import File


class TestFile(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        self.test_content = "这是一个测试文件内容"

        # 创建测试文件
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(self.test_content)

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_file_exist_exist_type(self):
        """测试文件存在性检查 - 存在类型"""
        result = File.file_exist(file_path=self.test_file_path, exist_type=ExistType.EXIST)
        self.assertTrue(result)

    def test_file_exist_not_exist_type(self):
        """测试文件存在性检查 - 不存在类型"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.txt")
        result = File.file_exist(file_path=non_existent_file, exist_type=ExistType.NOT_EXIST)
        self.assertTrue(result)

    def test_file_exist_invalid_type(self):
        """测试文件存在性检查 - 无效类型"""
        with self.assertRaises(NotImplementedError):
            File.file_exist(file_path=self.test_file_path, exist_type="invalid_type")

    def test_file_create_success(self):
        """测试文件创建 - 成功情况"""
        new_file_name = "new_file.txt"
        result = File.file_create(
            dst_path=self.temp_dir,
            file_name=new_file_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_file_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_file_create_folder_not_exists(self):
        """测试文件创建 - 目标文件夹不存在"""
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            File.file_create(dst_path=non_existent_dir, file_name="test.txt")

    def test_file_create_overwrite_existing(self):
        """测试文件创建 - 覆盖已存在文件"""
        # 先创建一个文件
        existing_file = os.path.join(self.temp_dir, "existing.txt")
        with open(existing_file, "w") as f:
            f.write("原始内容")

        result = File.file_create(
            dst_path=self.temp_dir,
            file_name="existing.txt",
            exist_options=OptionType.OVERWRITE,
        )
        self.assertEqual(result, existing_file)
        # 检查文件是否被清空
        with open(existing_file) as f:
            content = f.read()
        self.assertEqual(content, "")

    def test_file_delete_success(self):
        """测试文件删除 - 成功情况"""
        result = File.file_delete(file_path=self.test_file_path, delete_options=DeleteType.DELETE)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_file_delete_file_not_exists(self):
        """测试文件删除 - 文件不存在"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.txt")
        with self.assertRaises(BaseException):
            File.file_delete(file_path=non_existent_file)

    @mock.patch("send2trash.send2trash")
    def test_file_delete_trash(self, mock_send2trash):
        """测试文件删除 - 移入回收站"""
        result = File.file_delete(file_path=self.test_file_path, delete_options=DeleteType.TRASH)
        self.assertTrue(result)
        mock_send2trash.assert_called_once_with(self.test_file_path)

    def test_file_copy_success(self):
        """测试文件复制 - 成功情况"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        result = File.file_copy(
            file_path=self.test_file_path,
            target_path=target_dir,
            state_type=StateType.ERROR,
            file_name="",
            copy_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, "test_file.txt")
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_file_copy_source_not_exists(self):
        """测试文件复制 - 源文件不存在"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.txt")
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        with self.assertRaises(BaseException):
            File.file_copy(file_path=non_existent_file, target_path=target_dir)

    def test_file_write_append(self):
        """测试文件写入 - 追加模式"""
        content = "追加的内容"
        result = File.file_write(
            file_path=self.test_file_path,
            file_option=StateType.ERROR,
            msg=content,
            write_type=WriteType.APPEND,
        )
        self.assertEqual(result, self.test_file_path)

        with open(self.test_file_path, encoding="utf-8") as f:
            final_content = f.read()
        self.assertEqual(final_content, self.test_content + content)

    def test_file_write_overwrite(self):
        """测试文件写入 - 覆盖模式"""
        content = "覆盖的内容"
        result = File.file_write(
            file_path=self.test_file_path,
            file_option=StateType.ERROR,
            msg=content,
            write_type=WriteType.OVERWRITE,
        )
        self.assertEqual(result, self.test_file_path)

        with open(self.test_file_path, encoding="utf-8") as f:
            final_content = f.read()
        self.assertEqual(final_content, content)

    def test_file_read_all(self):
        """测试文件读取 - 全部内容"""
        result = File.file_read(file_path=self.test_file_path, read_type=ReadType.ALL)
        self.assertEqual(result, self.test_content)

    def test_file_read_lines(self):
        """测试文件读取 - 按行读取"""
        # 创建多行文件
        multi_line_content = "第一行\n第二行\n第三行"
        multi_line_file = os.path.join(self.temp_dir, "multi_line.txt")
        with open(multi_line_file, "w", encoding="utf-8") as f:
            f.write(multi_line_content)

        result = File.file_read(file_path=multi_line_file, read_type=ReadType.List)
        expected_lines = ["第一行", "第二行", "第三行"]
        self.assertEqual(result, expected_lines)

    def test_file_move_success(self):
        """测试文件移动 - 成功情况"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        result = File.file_move(
            file_path=self.test_file_path,
            target_folder=target_dir,
            state_type=StateType.ERROR,
            file_name="",
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, "test_file.txt")
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_file_rename_success(self):
        """测试文件重命名 - 成功情况"""
        new_name = "renamed_file"
        result = File.file_rename(
            file_path=self.test_file_path,
            new_name=new_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, "{}.txt".format(new_name))
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_file_search_fuzzy(self):
        """测试文件搜索 - 模糊搜索"""
        # 创建多个测试文件
        files = ["test1.txt", "test2.txt", "other.txt"]
        for file_name in files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("content")

        result = File.file_search(folder_path=self.temp_dir, find_type=SearchType.FUZZY, search_pattern="test")
        self.assertGreaterEqual(len(result), 2)

    def test_file_search_exact(self):
        """测试文件搜索 - 精确搜索"""
        result = File.file_search(
            folder_path=self.temp_dir,
            find_type=SearchType.EXACT,
            search_pattern="test_file.txt",
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(any("test_file.txt" in str(item) for item in result))

    def test_file_wait_status_created(self):
        """测试文件等待状态 - 创建状态"""
        # 创建一个新文件来测试等待
        wait_file = os.path.join(self.temp_dir, "wait_file.txt")
        with open(wait_file, "w") as f:
            f.write("content")

        result = File.file_wait_status(file_path=wait_file, status_type=StatusType.CREATED, wait_time=1)
        self.assertTrue(result)

    def test_file_info_all(self):
        """测试获取文件信息 - 全部信息"""
        result = File.file_info(file_path=self.test_file_path, info_type=InfoType.ALL)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("size", result)
        self.assertIn("abs_path", result)

    def test_get_file_list(self):
        """测试获取文件列表"""
        # 创建多个文件
        files = ["file1.txt", "file2.txt", "file3.txt"]
        for file_name in files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write("content")

        result = File.get_file_list(
            folder_path=self.temp_dir,
            traverse_subfolder=TraverseType.NO,
            output_type=OutputType.LIST,
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)  # 包括test_file.txt


if __name__ == "__main__":
    unittest.main()
