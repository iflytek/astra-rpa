import os
import shutil
import unittest
from unittest import TestCase

from rpadocx import (
    ApplicationType,
    CloseRangeType,
    CommentType,
    ConvertPageType,
    CursorPositionType,
    DeleteMode,
    FileType,
    InsertImgType,
    InsertionType,
    MoveDirectionType,
    MoveUpDownType,
    ReplaceMethodType,
    ReplaceType,
    RowAlignment,
    SaveFileType,
    SaveType,
    SearchTableType,
    SelectRangeType,
    SelectTextType,
    TableBehavior,
    UnderLineStyle,
    VerticalAlignment,
)
from rpadocx.docx import Docx


class TestDocx(TestCase):
    @classmethod
    def setUpClass(cls):
        current_dir = os.path.abspath(os.getcwd())
        cls.test_dir = os.path.join(current_dir, "docx_dir")
        if not os.path.exists(cls.test_dir):
            os.makedirs(cls.test_dir, exist_ok=True)
            print(f"已在以下目录创建 'docx_dir' 目录: {cls.test_dir}")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        self.docx = Docx()
        if os.path.exists(os.path.join(self.test_dir, "中文文档.docx")):
            self.docx_obj = self.docx.open_docx(
                file_path=os.path.join(self.test_dir, "中文文档.docx"),
                default_application=ApplicationType.WPS,
            )
        else:
            self.docx_obj, doc_path = self.docx.create_docx(
                file_path=self.test_dir,
                file_name="中文文档",
                default_application=ApplicationType.WPS,
            )

    def tearDown(self):
        if self.docx_obj:
            self.docx.close_docx(
                doc=self.docx_obj,
                close_range_flag=CloseRangeType.ONE,
                save_type=SaveType.SAVE,
            )

    @unittest.skip
    def test_create_docx(self):
        for file_name in ["test", "中文文档", "test@@_%^&word文档创建"]:
            doc_obj, doc_path = self.docx.create_docx(
                file_path=self.test_dir,
                file_name=file_name,
                default_application=ApplicationType.WPS,
            )
            self.assertEqual(os.path.exists(doc_path), True)

    @unittest.skip
    def test_open_docx(self):
        self.docx.open_docx(
            file_path=os.path.join(self.test_dir, "test"),
            default_application=ApplicationType.WPS,
        )

    def test_insert_docx(self):
        self.docx.insert_docx(
            doc=self.docx_obj,
            text="word文档中插入中文内容",
            enter_flag=False,
            bold_flag=True,
            italic_flag=True,
        )
        self.docx.insert_docx(
            doc=self.docx_obj,
            text="word文档中插入特殊符号#%……%*%#@……&",
            enter_flag=True,
            bold_flag=False,
            underline_flag=UnderLineStyle.LINE,
            font_size=16,
        )

    def test_read_docx(self):
        read_content = self.docx.read_docx(self.docx_obj)
        self.assertEqual(read_content, "word文档中插入中文内容\nword文档中插入特殊符号#%……%*%#@……&\n")

    def test_select(self):
        self.docx.select_text(doc=self.docx_obj, select_type=SelectTextType.ROW, r_start=1, r_end=3)

    def test_move_cursor(self):
        self.docx.get_cursor_position(
            doc=self.docx_obj,
            by=SelectTextType.ROW,
            r_idx=3,
            pos=CursorPositionType.HEAD,
        )
        self.docx.move_cursor(
            doc=self.docx_obj,
            direction=MoveDirectionType.DOWN,
            unitupdown=MoveUpDownType.ROW,
            distance=3,
        )
        url = r"http:\\www.microsoft.com"
        display = "微软"
        self.docx.insert_hyperlink(doc=self.docx_obj, url=url, display=display)

    def test_img(self):
        self.docx.insert_img(
            doc=self.docx_obj,
            img_from=InsertImgType.FILE,
            img_path=r"C:\Users\zyfan9\Pictures\1716231.png",
            scale=10,
        )

    def test_read_table(self):
        table_content_text = self.docx.read_table(doc=self.docx_obj, search_type=SearchTableType.TEXT, text="设置")
        print(table_content_text)
        table_content_idx = self.docx.read_table(doc=self.docx_obj, search_type=SearchTableType.IDX, idx=2)
        self.assertEqual(table_content_text, table_content_idx)

    def test_insert_table(self):
        table_content = [[1, 2, 3], [4, 5, 6], [7, 8, ""]]
        self.docx.insert_table(
            doc=self.docx_obj,
            table_content=table_content,
            table_behavior=TableBehavior.AUTO,
            alignment=RowAlignment.RIGHT,
            v_alignment=VerticalAlignment.BOTTOM,
            border=True,
            if_change_font=True,
            font_size=12,
            font_color=None,
            font_set=None,
            font_bold=False,
            font_italic=False,
            underline=UnderLineStyle.LINE,
        )
        self.assertEqual(
            self.docx.read_table(doc=self.docx_obj, search_type=SearchTableType.IDX, idx=1),
            [["1", "2", "3"], ["4", "5", "6"], ["7", "8", ""]],
        )

    def test_delete_docx(self):
        self.docx.delete(
            doc=self.docx_obj,
            delete_mode=DeleteMode.ALL,
            p_start=2,
            c_start=2,
            p_end=4,
            c_end=4,
        )

    def test_replace(self):
        self.docx.replace(
            doc=self.docx_obj,
            replace_type=ReplaceType.STR,
            origin_word="中文内容",
            new_word="apple",
            replace_method=ReplaceMethodType.ALL,
        )
        self.assertEqual(
            self.docx.read_docx(self.docx_obj),
            "word文档中插入apple\n微软word文档中插入特殊符号#%……%*%#@……&\n",
        )

    def test_comment(self):
        self.docx.create_comment(
            doc=self.docx_obj,
            paragraph_idx=1,
            start=1,
            end=3,
            comment="123123",
            comment_type=CommentType.POSITION,
        )
        self.docx.delete_comment(doc=self.docx_obj, delete_all=True)

    def test_convert(self):
        self.docx.convert_format(
            doc=self.docx_obj,
            output_path=r"C:\RPA",
            default_name=False,
            output_name="ababa",
            page_type=ConvertPageType.RANGE,
            page_start=1,
            page_end=2,
            output_file_type=FileType.PDF,
            save_type=SaveFileType.OVERWRITE,
        )
        self.assertTrue(os.path.exists(r"C:\RPA\ababa.pdf"))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDocx("test_delete_docx"))
    suite.addTest(TestDocx("test_insert_docx"))
    suite.addTest(TestDocx("test_read_docx"))
    return suite


def suite1():
    suite = unittest.TestSuite()
    suite.addTest(TestDocx("test_insert_table"))
    suite.addTest(TestDocx("test_read_table"))
    suite.addTest(TestDocx("test_img"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
