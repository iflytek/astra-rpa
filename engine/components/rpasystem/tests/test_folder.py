import os
import shutil
import tempfile
import unittest
from unittest import TestCase, mock

from rpasystem import *
from rpasystem.folder import Folder


class TestFolder(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_folder_path = os.path.join(self.temp_dir, "test_folder")
        self.test_content = "测试文件内容"

        # 创建测试文件夹
        os.makedirs(self.test_folder_path, exist_ok=True)

        # 在测试文件夹中创建一些文件
        for i in range(3):
            file_path = os.path.join(self.test_folder_path, f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"文件 {i} 的内容")

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_folder_exist_exist_type(self):
        """测试文件夹存在性检查 - 存在类型"""
        result = Folder.folder_exist(folder_path=self.test_folder_path, exist_type=ExistType.EXIST)
        self.assertTrue(result)

    def test_folder_exist_not_exist_type(self):
        """测试文件夹存在性检查 - 不存在类型"""
        non_existent_folder = os.path.join(self.temp_dir, "non_existent")
        result = Folder.folder_exist(folder_path=non_existent_folder, exist_type=ExistType.NOT_EXIST)
        self.assertTrue(result)

    def test_folder_exist_invalid_type(self):
        """测试文件夹存在性检查 - 无效类型"""
        with self.assertRaises(NotImplementedError):
            Folder.folder_exist(folder_path=self.test_folder_path, exist_type="invalid_type")

    @mock.patch("rpasystem.folder.open_folder")
    def test_folder_open_success(self, mock_open_folder):
        """测试打开文件夹 - 成功"""
        Folder.folder_open(folder_path=self.test_folder_path)
        mock_open_folder.assert_called_once_with(self.test_folder_path)

    def test_folder_open_not_exists(self):
        """测试打开文件夹 - 文件夹不存在"""
        non_existent_folder = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Folder.folder_open(folder_path=non_existent_folder)

    def test_folder_create_success(self):
        """测试文件夹创建 - 成功情况"""
        new_folder_name = "new_folder"
        result = Folder.folder_create(
            target_path=self.temp_dir,
            folder_name=new_folder_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_folder_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_folder_create_target_not_exists(self):
        """测试文件夹创建 - 目标路径不存在"""
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Folder.folder_create(target_path=non_existent_dir, folder_name="test_folder")

    def test_folder_create_overwrite_existing(self):
        """测试文件夹创建 - 覆盖已存在文件夹"""
        # 先创建一个文件夹
        existing_folder = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_folder, exist_ok=True)

        # 在文件夹中创建一些文件
        with open(os.path.join(existing_folder, "test.txt"), "w") as f:
            f.write("原始内容")

        result = Folder.folder_create(
            target_path=self.temp_dir,
            folder_name="existing",
            exist_options=OptionType.OVERWRITE,
        )
        self.assertEqual(result, existing_folder)
        # 检查文件夹是否被清空
        self.assertFalse(os.path.exists(os.path.join(existing_folder, "test.txt")))

    def test_folder_create_skip_existing(self):
        """测试文件夹创建 - 跳过已存在文件夹"""
        existing_folder = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_folder, exist_ok=True)

        result = Folder.folder_create(
            target_path=self.temp_dir,
            folder_name="existing",
            exist_options=OptionType.SKIP,
        )
        self.assertEqual(result, existing_folder)

    def test_folder_delete_success(self):
        """测试文件夹删除 - 成功情况"""
        result = Folder.folder_delete(folder_path=self.test_folder_path, delete_options=DeleteType.DELETE)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(self.test_folder_path))

    def test_folder_delete_folder_not_exists(self):
        """测试文件夹删除 - 文件夹不存在"""
        non_existent_folder = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Folder.folder_delete(folder_path=non_existent_folder)

    @mock.patch("send2trash.send2trash")
    def test_folder_delete_trash(self, mock_send2trash):
        """测试文件夹删除 - 移入回收站"""
        result = Folder.folder_delete(folder_path=self.test_folder_path, delete_options=DeleteType.TRASH)
        self.assertTrue(result)
        mock_send2trash.assert_called_once_with(self.test_folder_path)

    def test_folder_copy_success(self):
        """测试文件夹复制 - 成功情况"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        result = Folder.folder_copy(
            source_path=self.test_folder_path,
            target_path=target_dir,
            state_type=StateType.ERROR,
            folder_name="",
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, "test_folder")
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_folder_copy_source_not_exists(self):
        """测试文件夹复制 - 源文件夹不存在"""
        non_existent_folder = os.path.join(self.temp_dir, "non_existent")
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        with self.assertRaises(BaseException):
            Folder.folder_copy(source_path=non_existent_folder, target_path=target_dir)

    def test_folder_copy_with_custom_name(self):
        """测试文件夹复制 - 自定义名称"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)
        custom_name = "custom_folder"

        result = Folder.folder_copy(
            source_path=self.test_folder_path,
            target_path=target_dir,
            state_type=StateType.ERROR,
            folder_name=custom_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, custom_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_folder_move_success(self):
        """测试文件夹移动 - 成功情况"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        result = Folder.folder_move(
            folder_path=self.test_folder_path,
            target_folder=target_dir,
            state_type=StateType.ERROR,
            folder_name="",
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, "test_folder")
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_folder_path))

    def test_folder_move_with_custom_name(self):
        """测试文件夹移动 - 自定义名称"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)
        custom_name = "moved_folder"

        result = Folder.folder_move(
            folder_path=self.test_folder_path,
            target_folder=target_dir,
            state_type=StateType.ERROR,
            folder_name=custom_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(target_dir, custom_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_folder_path))

    def test_folder_rename_success(self):
        """测试文件夹重命名 - 成功情况"""
        new_name = "renamed_folder"
        result = Folder.folder_rename(
            folder_path=self.test_folder_path,
            new_name=new_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.test_folder_path))

    def test_folder_rename_with_custom_name(self):
        """测试文件夹重命名 - 自定义名称"""
        new_name = "custom_renamed_folder"
        result = Folder.folder_rename(
            folder_path=self.test_folder_path,
            new_name=new_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_name)
        self.assertEqual(result, expected_path)
        self.assertTrue(os.path.exists(expected_path))

    def test_folder_clear_success(self):
        """测试文件夹清空 - 成功情况"""
        # 在测试文件夹中创建一些文件和子文件夹
        sub_folder = os.path.join(self.test_folder_path, "sub_folder")
        os.makedirs(sub_folder, exist_ok=True)

        for i in range(3):
            file_path = os.path.join(self.test_folder_path, f"clear_file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"文件 {i} 的内容")

        result = Folder.folder_clear(folder_path=self.test_folder_path)
        self.assertTrue(result)

        # 检查文件夹是否被清空
        files = os.listdir(self.test_folder_path)
        self.assertEqual(len(files), 0)

    def test_folder_clear_empty_folder(self):
        """测试文件夹清空 - 空文件夹"""
        empty_folder = os.path.join(self.temp_dir, "empty_folder")
        os.makedirs(empty_folder, exist_ok=True)

        result = Folder.folder_clear(folder_path=empty_folder)
        self.assertTrue(result)

    def test_get_folder_list_basic(self):
        """测试获取文件夹列表 - 基本功能"""
        # 创建多个子文件夹
        sub_folders = ["sub1", "sub2", "sub3"]
        for folder_name in sub_folders:
            folder_path = os.path.join(self.test_folder_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

        result = Folder.get_folder_list(
            folder_path=self.test_folder_path,
            traverse_subfolder=TraverseType.NO,
            output_type=OutputType.LIST,
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  # 3个子文件夹

    def test_get_folder_list_with_traverse(self):
        """测试获取文件夹列表 - 遍历子文件夹"""
        # 创建嵌套文件夹结构
        sub_folder = os.path.join(self.test_folder_path, "sub_folder")
        os.makedirs(sub_folder, exist_ok=True)

        nested_folder = os.path.join(sub_folder, "nested_folder")
        os.makedirs(nested_folder, exist_ok=True)

        result = Folder.get_folder_list(
            folder_path=self.test_folder_path,
            traverse_subfolder=TraverseType.YES,
            output_type=OutputType.LIST,
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)  # 应该包含子文件夹

    def test_get_folder_list_excel_output(self):
        """测试获取文件夹列表 - Excel输出"""
        # 创建测试文件夹
        test_folders = ["folder1", "folder2", "folder3"]
        for folder_name in test_folders:
            folder_path = os.path.join(self.test_folder_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

        excel_path = os.path.join(self.temp_dir, "excel_output")
        os.makedirs(excel_path, exist_ok=True)

        result = Folder.get_folder_list(
            folder_path=self.test_folder_path,
            traverse_subfolder=TraverseType.NO,
            output_type=OutputType.EXCEL,
            excel_path=excel_path,
            state_type=StateType.ERROR,
            excel_name="folders.xlsx",
        )
        self.assertIsInstance(result, list)

    def test_get_folder_list_with_sorting(self):
        """测试获取文件夹列表 - 带排序"""
        # 创建测试文件夹
        test_folders = ["folder1", "folder2", "folder3"]
        for folder_name in test_folders:
            folder_path = os.path.join(self.test_folder_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

        result = Folder.get_folder_list(
            folder_path=self.test_folder_path,
            traverse_subfolder=TraverseType.NO,
            output_type=OutputType.LIST,
            sort_method=SortMethod.NONE,
            sort_type=SortType.ASCENDING,
        )
        self.assertIsInstance(result, list)

    def test_folder_create_generate_option(self):
        """测试文件夹创建 - 生成选项"""
        # 先创建一个文件夹
        existing_folder = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_folder, exist_ok=True)

        result = Folder.folder_create(
            target_path=self.temp_dir,
            folder_name="existing",
            exist_options=OptionType.GENERATE,
        )
        # 应该生成一个新的文件夹名称
        self.assertNotEqual(result, existing_folder)
        self.assertTrue(os.path.exists(result))

    def test_folder_copy_overwrite_option(self):
        """测试文件夹复制 - 覆盖选项"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        # 先创建一个目标文件夹
        existing_target = os.path.join(target_dir, "test_folder")
        os.makedirs(existing_target, exist_ok=True)

        result = Folder.folder_copy(
            source_path=self.test_folder_path,
            target_path=target_dir,
            state_type=StateType.ERROR,
            folder_name="",
            exist_options=OptionType.OVERWRITE,
        )
        self.assertEqual(result, existing_target)

    def test_folder_copy_skip_option(self):
        """测试文件夹复制 - 跳过选项"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        # 先创建一个目标文件夹
        existing_target = os.path.join(target_dir, "test_folder")
        os.makedirs(existing_target, exist_ok=True)

        result = Folder.folder_copy(
            source_path=self.test_folder_path,
            target_path=target_dir,
            state_type=StateType.ERROR,
            folder_name="",
            exist_options=OptionType.SKIP,
        )
        self.assertEqual(result, existing_target)

    def test_folder_move_overwrite_option(self):
        """测试文件夹移动 - 覆盖选项"""
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        # 先创建一个目标文件夹
        existing_target = os.path.join(target_dir, "test_folder")
        os.makedirs(existing_target, exist_ok=True)

        result = Folder.folder_move(
            folder_path=self.test_folder_path,
            target_folder=target_dir,
            state_type=StateType.ERROR,
            folder_name="",
            exist_options=OptionType.OVERWRITE,
        )
        self.assertEqual(result, existing_target)

    def test_folder_rename_overwrite_option(self):
        """测试文件夹重命名 - 覆盖选项"""
        # 先创建一个同名文件夹
        existing_folder = os.path.join(self.temp_dir, "renamed_folder")
        os.makedirs(existing_folder, exist_ok=True)

        result = Folder.folder_rename(
            folder_path=self.test_folder_path,
            new_name="renamed_folder",
            exist_options=OptionType.OVERWRITE,
        )
        self.assertEqual(result, existing_folder)

    def test_folder_rename_skip_option(self):
        """测试文件夹重命名 - 跳过选项"""
        # 先创建一个同名文件夹
        existing_folder = os.path.join(self.temp_dir, "renamed_folder")
        os.makedirs(existing_folder, exist_ok=True)

        result = Folder.folder_rename(
            folder_path=self.test_folder_path,
            new_name="renamed_folder",
            exist_options=OptionType.SKIP,
        )
        self.assertEqual(result, existing_folder)

    def test_folder_with_special_characters(self):
        """测试文件夹操作 - 包含特殊字符的文件夹名"""
        special_folder_name = "测试文件夹：包含中文、英文、数字123和特殊符号！@#￥%"
        special_folder_path = os.path.join(self.temp_dir, special_folder_name)
        os.makedirs(special_folder_path, exist_ok=True)

        # 测试存在性检查
        result = Folder.folder_exist(folder_path=special_folder_path, exist_type=ExistType.EXIST)
        self.assertTrue(result)

        # 测试重命名
        new_name = "重命名后的文件夹"
        result = Folder.folder_rename(
            folder_path=special_folder_path,
            new_name=new_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_name)
        self.assertEqual(result, expected_path)

    def test_folder_with_spaces_in_name(self):
        """测试文件夹操作 - 包含空格的文件夹名"""
        folder_with_spaces = os.path.join(self.temp_dir, "folder with spaces")
        os.makedirs(folder_with_spaces, exist_ok=True)

        # 测试存在性检查
        result = Folder.folder_exist(folder_path=folder_with_spaces, exist_type=ExistType.EXIST)
        self.assertTrue(result)

        # 测试重命名
        new_name = "folder without spaces"
        result = Folder.folder_rename(
            folder_path=folder_with_spaces,
            new_name=new_name,
            exist_options=OptionType.GENERATE,
        )
        expected_path = os.path.join(self.temp_dir, new_name)
        self.assertEqual(result, expected_path)


if __name__ == "__main__":
    unittest.main()
