import os
import shutil
import tempfile
import unittest
from unittest import TestCase

from rpasystem import *
from rpasystem.compress import Compress


class TestCompress(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        self.test_folder_path = os.path.join(self.temp_dir, "test_folder")
        self.compress_dir = os.path.join(self.temp_dir, "compress_output")

        # 创建测试文件和文件夹
        with open(self.test_file_path, "w") as f:
            f.write("测试文件内容")
        os.makedirs(self.test_folder_path, exist_ok=True)

        # 在测试文件夹中创建一些文件
        for i in range(3):
            file_path = os.path.join(self.test_folder_path, f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"文件 {i} 的内容")

        os.makedirs(self.compress_dir, exist_ok=True)

    def tearDown(self):
        """测试后的清理工作"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_compress_file_success(self):
        """测试压缩 - 单个文件成功"""
        # 压缩单个文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))
        self.assertEqual(os.path.basename(result), "test_file.zip")

        # 验证压缩文件内容
        self._verify_zip_content(result, ["test_file.txt"])

    def test_compress_folder_success(self):
        """测试压缩 - 文件夹成功"""
        # 压缩文件夹
        result = Compress.compress(
            file_type=FileFolderType.FOLDER,
            folder_path=self.test_folder_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))
        self.assertEqual(os.path.basename(result), "test_folder.zip")

        # 验证压缩文件内容
        expected_files = [
            "test_folder/file_0.txt",
            "test_folder/file_1.txt",
            "test_folder/file_2.txt",
        ]
        self._verify_zip_content(result, expected_files)

    def test_compress_both_success(self):
        """测试压缩 - 文件和文件夹成功"""
        # 压缩文件和文件夹
        result = Compress.compress(
            file_type=FileFolderType.BOTH,
            file_path=self.test_file_path,
            folder_path=self.test_folder_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

        # 验证压缩文件内容
        expected_files = [
            "test_file.txt",
            "test_folder/file_0.txt",
            "test_folder/file_1.txt",
            "test_folder/file_2.txt",
        ]
        self._verify_zip_content(result, expected_files)

    def test_compress_file_empty_path(self):
        """测试压缩 - 文件路径为空"""
        with self.assertRaises(ValueError):
            Compress.compress(
                file_type=FileFolderType.FILE,
                file_path="",
                compress_dir=self.compress_dir,
            )

    def test_compress_folder_empty_path(self):
        """测试压缩 - 文件夹路径为空"""
        with self.assertRaises(ValueError):
            Compress.compress(
                file_type=FileFolderType.FOLDER,
                folder_path="",
                compress_dir=self.compress_dir,
            )

    def test_compress_both_empty_paths(self):
        """测试压缩 - 文件和文件夹路径都为空"""
        with self.assertRaises(ValueError):
            Compress.compress(
                file_type=FileFolderType.BOTH,
                file_path="",
                folder_path="",
                compress_dir=self.compress_dir,
            )

    def test_compress_with_password(self):
        """测试压缩 - 带密码"""
        password = "test_password"

        # 压缩文件并设置密码
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
            pwd=password,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

        # 验证带密码的压缩文件可以正常解压
        extract_dir = os.path.join(self.temp_dir, "extract_test")
        os.makedirs(extract_dir, exist_ok=True)

        uncompress_result = Compress.uncompress(
            source_path=result,
            target_path=extract_dir,
            status_type=StateType.ERROR,
            pwd=password,
        )

        # 验证解压结果
        self.assertTrue(os.path.exists(uncompress_result))
        extracted_file = os.path.join(extract_dir, "test_file.txt")
        self.assertTrue(os.path.exists(extracted_file))

    def test_compress_with_custom_name(self):
        """测试压缩 - 自定义压缩包名称"""
        custom_name = "custom_archive"

        # 压缩文件并使用自定义名称
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
            compress_name=custom_name,
        )

        # 验证压缩文件存在且名称正确
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.basename(result), f"{custom_name}.zip")

    def test_compress_folder_not_exists_error(self):
        """测试压缩 - 目标文件夹不存在且设置为错误"""
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Compress.compress(
                file_type=FileFolderType.FILE,
                file_path=self.test_file_path,
                compress_dir=non_existent_dir,
                state_type=StateType.ERROR,
            )

    def test_compress_folder_not_exists_create(self):
        """测试压缩 - 目标文件夹不存在但自动创建"""
        new_dir = os.path.join(self.temp_dir, "new_compress_dir")

        # 压缩文件到不存在的目录，但设置为自动创建
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=new_dir,
            state_type=StateType.CREATE,
        )

        # 验证压缩文件存在且目录被创建
        self.assertTrue(os.path.exists(result))
        self.assertTrue(os.path.exists(new_dir))

    def test_compress_invalid_save_type(self):
        """测试压缩 - 无效的保存类型"""
        with self.assertRaises(NotImplementedError):
            Compress.compress(
                file_type=FileFolderType.FILE,
                file_path=self.test_file_path,
                compress_dir=self.compress_dir,
                state_type=StateType.ERROR,
                save_type="invalid_type",
            )

    def test_uncompress_success(self):
        """测试解压 - 成功"""
        # 先创建一个真实的压缩文件
        test_file = os.path.join(self.temp_dir, "test_content.txt")
        with open(test_file, "w") as f:
            f.write("测试内容")

        # 使用压缩方法创建zip文件
        zip_path = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=test_file,
            compress_dir=self.temp_dir,
            state_type=StateType.ERROR,
        )

        # 解压文件
        result = Compress.uncompress(
            source_path=zip_path,
            target_path=self.compress_dir,
            status_type=StateType.ERROR,
        )

        # 验证解压结果
        self.assertTrue(os.path.exists(result))
        self.assertEqual(result, os.path.abspath(self.compress_dir))

        # 验证解压后的文件内容
        extracted_file = os.path.join(self.compress_dir, "test_content.txt")
        self.assertTrue(os.path.exists(extracted_file))
        with open(extracted_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "测试内容")

    def test_uncompress_source_not_exists(self):
        """测试解压 - 源文件不存在"""
        non_existent_zip = os.path.join(self.temp_dir, "non_existent.zip")
        with self.assertRaises(BaseException):
            Compress.uncompress(
                source_path=non_existent_zip,
                target_path=self.compress_dir,
                status_type=StateType.ERROR,
            )

    def test_uncompress_with_password(self):
        """测试解压 - 带密码"""
        password = "test_password"

        # 先创建一个带密码的压缩文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
            pwd=password,
        )

        # 解压带密码的文件
        extract_dir = os.path.join(self.temp_dir, "extract_with_pwd")
        os.makedirs(extract_dir, exist_ok=True)

        uncompress_result = Compress.uncompress(
            source_path=result,
            target_path=extract_dir,
            status_type=StateType.ERROR,
            pwd=password,
        )

        # 验证解压结果
        self.assertTrue(os.path.exists(uncompress_result))
        extracted_file = os.path.join(extract_dir, "test_file.txt")
        self.assertTrue(os.path.exists(extracted_file))

    def test_uncompress_target_not_exists_create(self):
        """测试解压 - 目标文件夹不存在但自动创建"""
        # 先创建一个压缩文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 解压到不存在的目录，但设置为自动创建
        new_dir = os.path.join(self.temp_dir, "new_extract_dir")
        uncompress_result = Compress.uncompress(source_path=result, target_path=new_dir, status_type=StateType.CREATE)

        # 验证解压结果和目录创建
        self.assertTrue(os.path.exists(uncompress_result))
        self.assertTrue(os.path.exists(new_dir))

    def test_uncompress_target_not_exists_error(self):
        """测试解压 - 目标文件夹不存在且设置为错误"""
        # 先创建一个压缩文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        with self.assertRaises(BaseException):
            Compress.uncompress(
                source_path=result,
                target_path=non_existent_dir,
                status_type=StateType.ERROR,
            )

    def test_uncompress_invalid_save_type(self):
        """测试解压 - 无效的保存类型"""
        # 先创建一个压缩文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=self.test_file_path,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        with self.assertRaises(NotImplementedError):
            Compress.uncompress(
                source_path=result,
                target_path=self.compress_dir,
                status_type=StateType.ERROR,
                save_type="invalid_type",
            )

    def test_compress_multiple_files(self):
        """测试压缩 - 多个文件"""
        # 创建多个测试文件
        files = ["file1.txt", "file2.txt", "file3.txt"]
        file_paths = []
        for file_name in files:
            file_path = os.path.join(self.temp_dir, file_name)
            with open(file_path, "w") as f:
                f.write(f"content for {file_name}")
            file_paths.append(file_path)

        file_path_str = ",".join(file_paths)

        # 压缩多个文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=file_path_str,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

        # 验证压缩文件内容
        self._verify_zip_content(result, files)

    def test_compress_multiple_folders(self):
        """测试压缩 - 多个文件夹"""
        # 创建多个测试文件夹
        folders = ["folder1", "folder2", "folder3"]
        folder_paths = []
        for folder_name in folders:
            folder_path = os.path.join(self.temp_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # 在每个文件夹中创建一些文件
            for i in range(2):
                file_path = os.path.join(folder_path, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content for {folder_name} file {i}")

            folder_paths.append(folder_path)

        folder_path_str = ",".join(folder_paths)

        # 压缩多个文件夹
        result = Compress.compress(
            file_type=FileFolderType.FOLDER,
            folder_path=folder_path_str,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

    def test_compress_and_uncompress_cycle(self):
        """测试压缩解压循环 - 确保数据完整性"""
        original_content = "原始测试内容"

        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "cycle_test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(original_content)

        # 压缩文件
        compress_result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=test_file,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(compress_result))

        # 解压文件
        extract_dir = os.path.join(self.temp_dir, "cycle_extract")
        os.makedirs(extract_dir, exist_ok=True)

        uncompress_result = Compress.uncompress(
            source_path=compress_result,
            target_path=extract_dir,
            status_type=StateType.ERROR,
        )

        # 验证解压结果
        self.assertTrue(os.path.exists(uncompress_result))

        # 验证解压后的文件内容
        extracted_file = os.path.join(extract_dir, "cycle_test.txt")
        self.assertTrue(os.path.exists(extracted_file))

        with open(extracted_file, "r", encoding="utf-8") as f:
            extracted_content = f.read()

        self.assertEqual(extracted_content, original_content)

    def test_compress_with_special_characters(self):
        """测试压缩 - 包含特殊字符的文件名"""
        special_file = os.path.join(self.temp_dir, "测试文件：包含中文、英文、数字123和特殊符号！@#￥%.txt")
        with open(special_file, "w", encoding="utf-8") as f:
            f.write("特殊字符文件内容")

        # 压缩包含特殊字符的文件
        result = Compress.compress(
            file_type=FileFolderType.FILE,
            file_path=special_file,
            compress_dir=self.compress_dir,
            state_type=StateType.ERROR,
        )

        # 验证压缩文件存在
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))

    def _verify_zip_content(self, zip_path, expected_files):
        """验证压缩文件内容"""
        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zip_file:
            file_list = zip_file.namelist()

            # 验证所有期望的文件都在压缩包中
            for expected_file in expected_files:
                self.assertIn(expected_file, file_list)


if __name__ == "__main__":
    unittest.main()
