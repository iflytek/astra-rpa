import os
import platform
import sys
from unittest import TestCase

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(project_root)
sys.path.insert(0, project_root)

from rpademo.src.rpademo import ReportLevelType
from rpademo.src.rpademo.demo import Demo


class TestDemo(TestCase):
    def test_print(self):
        demo = Demo()
        res = demo.print(print_type=ReportLevelType.INFO, print_msg="hello")
        print(res)
        if sys.platform == "win32":
            self.assertEqual(res, "[info] win hello")
        elif platform.system() == "Linux":
            self.assertEqual(res, "[info] linux hello")

    def test_file_create(self):
        demo = Demo()
        res = demo.create_txt_file(file_path=r"C:\\1.txt", content="Hello World! 这是一个测试文件。")
        print(res)


if __name__ == "__main__":
    TestDemo().test_print()
    TestDemo().test_file_create()
