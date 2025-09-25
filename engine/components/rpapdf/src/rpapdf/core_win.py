import ast
import os

import pandas as pd
import pdfplumber
import pypdfium2
from pdfminer.pdfdocument import PDFPasswordIncorrect
from pypdf import PdfReader, PdfWriter
from rpaatomic.utils import FileExistenceType, handle_existence
from rpapdf import MergeType, PictureType, SelectRangeType
from rpapdf.core import IPDFCore
from rpapdf.error import *


class PDFCore(IPDFCore):
    @staticmethod
    def open_pdf(file_path: str, pwd: str = "") -> PdfReader:
        # 打开PDF文件
        reader = PdfReader(file_path)

        # 检查是否需要解锁
        if reader.is_encrypted:
            # 如果有密码，尝试解锁
            password_type = reader.decrypt(pwd)
            if password_type == 0:
                raise BaseException(PDF_PASSWORD_ERROR_FORMAT.format(pwd), "密码错误")

        return reader

    @staticmethod
    def get_pages_num(file_path: str, pwd: str = "") -> int:
        """
        获取PDF总页数，输出到数字类型变量；支持输入PDF文档加密密码
        """
        reader = PDFCore.open_pdf(file_path, pwd)
        # 获取页面数量
        num_pages = len(reader.pages)
        return num_pages

    @staticmethod
    def get_page_text(
        file_path: str,
        pwd: str = "",
        page_range: str = "",
        select_range: SelectRangeType = SelectRangeType.ALL,
    ) -> list:
        """
        获取PDF文本内容，输出到字符串类型变量；支持输入PDF文档加密密码
        """
        reader = PDFCore.open_pdf(file_path, pwd)
        if page_range and select_range == SelectRangeType.PART:
            page_nums = PDFCore.parse_pages(page_range, len(reader.pages))
        else:
            page_nums = [i for i in range(len(reader.pages))]
        page_text = []
        for page_num in page_nums:
            page = reader.pages[page_num]
            page_text.append(page.extract_text())
        return page_text

    @staticmethod
    def get_images_in_page(
        file_path: str,
        pwd: str = "",
        page_range: str = "",
        save_dir: str = "",
        image_type: PictureType = PictureType.PNG,
        prefix: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> list:
        """
        获取PDF页面图像，输出到图像文件；支持输入PDF文档加密密码
        """
        reader = PDFCore.open_pdf(file_path, pwd)
        image_paths = []
        if page_range:
            page_nums = PDFCore.parse_pages(page_range, len(reader.pages))
        else:
            page_nums = [i for i in range(len(reader.pages))]
        if not prefix:
            prefix = os.path.basename(file_path).split(".")[0]
        for page_num in page_nums:
            page = reader.pages[page_num]
            for count, image_file_object in enumerate(page.images):
                image_path = os.path.join(
                    save_dir,
                    f"{prefix}_page{page_num + 1}_{count + 1}.{image_type.value}",
                )
                image_path = handle_existence(image_path, exist_handle_type)
                if image_path:
                    image_paths.append(image_path)
                    with open(image_path, "wb") as fp:
                        fp.write(image_file_object.data)
        return image_paths

    @staticmethod
    def merge_pdf_files(
        merge_type: MergeType = MergeType.FOLDER,
        file_folder_path: str = "",
        files_path: str = "",
        save_dir: str = "",
        new_file_name: str = "",
        new_pwd: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        合并PDF文件，支持合并文件夹中的PDF文件，或者合并指定PDF文件；支持输入PDF文档加密密码
        """
        merger = PdfWriter()

        # 处理生成的文件名
        if not new_file_name:
            new_file_name = "合并文件.pdf"
        elif not new_file_name.endswith(".pdf"):
            new_file_name += ".pdf"
        new_file_path = os.path.join(save_dir, new_file_name)

        if merge_type == MergeType.FOLDER:
            # 合并文件夹中的PDF文件
            pdf_files = []
            for file in os.listdir(file_folder_path):  # 不遍历子文件夹，如果需要遍历子文件夹，则使用os.walk()
                if file.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(file_folder_path, file))
                    merger.append(os.path.join(file_folder_path, file))
        else:
            if isinstance(files_path, str):
                if files_path.startswith("[") and files_path.endswith("]"):
                    files_path = ast.literal_eval(files_path)
                else:
                    files_path = files_path.split(".pdf,")
                    for i in range(len(files_path)):
                        if i != len(files_path) - 1:
                            # 最后一项是正常路径
                            files_path[i] = files_path[i].strip() + ".pdf"
            elif not isinstance(files_path, list):
                raise BaseException(
                    FILE_PATH_ERROR_FORMAT.format(str(files_path)),
                    "PDF文件路径有误，请输入正确的路径",
                )

            # 合并指定PDF文件
            for file in files_path:
                if not os.path.exists(file):
                    raise BaseException(
                        FILE_PATH_ERROR_FORMAT.format(file),
                        "PDF文件路径有误，请输入正确的路径",
                    )
                merger.append(file)

        if new_pwd:
            merger.encrypt(new_pwd)  # user_password
        new_file_path = handle_existence(new_file_path, exist_handle_type)
        if new_file_path:
            merger.write(new_file_path)
        merger.close()

        return new_file_path

    @staticmethod
    def extract_pdf_pages(
        file_path: str,
        pwd: str = "",
        save_dir: str = "",
        page_range: str = "",
        new_file_name: str = "",
        new_pwd: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        提取PDF页面，支持输入PDF文档加密密码
        :param file_path:
        :param pwd:
        :param save_dir:
        :param page_range:
        :param new_file_name:
        :param new_pwd:
        :param exist_handle_type:
        :return:
        """
        reader = PDFCore.open_pdf(file_path, pwd)
        writer = PdfWriter()

        # 处理生成的文件名
        if not new_file_name:
            new_file_name = os.path.basename(file_path) + "_提取.pdf"
        elif not new_file_name.endswith(".pdf"):
            new_file_name += ".pdf"
        new_file_path = os.path.join(save_dir, new_file_name)

        if page_range:
            page_nums = PDFCore.parse_pages(page_range, len(reader.pages))
        else:
            page_nums = [i for i in range(len(reader.pages))]
        for page_num in page_nums:
            writer.add_page(reader.pages[page_num])
        if new_pwd:
            writer.encrypt(new_pwd)  # user_password
        new_file_path = handle_existence(new_file_path, exist_handle_type)
        if new_file_path:
            writer.write(new_file_path)
        writer.close()
        return new_file_path

    @staticmethod
    def extract_forms_from_pdf(
        file_path: str,
        pwd: str = "",
        page_range: str = "",
        combine_flag: bool = True,
        save_dir: str = "",
        new_file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        提取PDF中的表格，支持输入PDF文档加密密码，转成Excel文件
        :param file_path:
        :param pwd:
        :param page_range:
        :param combine_flag:
        :param save_dir:
        :param new_file_name:
        :param exist_handle_type:
        :return:
        """
        # 用pdfplumber读取PDF文件
        tables = []
        # 处理生成的文件名
        if not new_file_name:
            new_file_name = os.path.basename(file_path).split(".")[0] + ".xlsx"
        elif not new_file_name.endswith(".xlsx"):
            new_file_name += ".xlsx"
        new_file_path = os.path.join(save_dir, new_file_name)
        try:
            with pdfplumber.open(file_path, password=pwd) as pdf:
                if page_range:
                    page_nums = PDFCore.parse_pages(page_range, len(pdf.pages))
                else:
                    page_nums = [i for i in range(len(pdf.pages))]
                # 假设PDF中的表格位于第一页
                for page_num in page_nums:
                    page = pdf.pages[page_num]
                    # 使用.extract_table()找到并提取表格数据
                    raw_tables = page.extract_tables()  # 要替换成extract_tables
                    for table in raw_tables:
                        if table is not None:
                            tables.append(table)
        except PDFPasswordIncorrect:
            raise BaseException(
                PDF_PASSWORD_ERROR_FORMAT.format(pwd),
                "PDF文件路径有误，请输入正确的路径",
            )

        # 将提取的表格数据转换为pandas DataFrame
        if len(tables) == 0:
            raise Exception("所选页面没有表格")
        dfs = []

        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            dfs.append(df)

        new_file_path = handle_existence(new_file_path, exist_handle_type)
        if not new_file_path:
            return ""

        if combine_flag:
            # 合并所有DataFrame
            try:
                result_df = pd.concat(dfs, ignore_index=True)
                result_df.to_excel(new_file_path, index=False)
            except pd.errors.InvalidIndexError:
                raise ValueError("无法拼接多表，建议将【是否合并】设置为否")
        else:
            # 将dfs中的df输出到各个sheet中
            with pd.ExcelWriter(new_file_path) as writer:
                for index in range(1, len(dfs) + 1):
                    dfs[index - 1].to_excel(writer, index=False, sheet_name="Sheet{}".format(str(index)))

        return new_file_path

    @staticmethod
    def pdf_to_image(
        file_path: str,
        pwd: str = "",
        save_dir: str = "",
        page_range: str = "",
        image_type: PictureType = PictureType.PNG,
        prefix: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """
        PDF转换为图像，支持输入PDF文档加密密码
        :param file_path:
        :param pwd:
        :param save_dir:
        :param page_range:
        :param image_type:
        :param prefix:
        :param exist_handle_type:
        :return:
        """

        pdf_obj = pypdfium2.PdfDocument(input=file_path, password=pwd)
        if page_range:
            page_nums = PDFCore.parse_pages(page_range, len(pdf_obj))
        else:
            page_nums = [i for i in range(len(pdf_obj))]
        if not prefix:
            prefix = os.path.basename(file_path).split(".")[0]
        for page_num in page_nums:
            page = pdf_obj[page_num]
            bitmap = page.render(
                scale=300 / 72,  # set resolution to 300 DPI
                rotation=0,  # no additional rotation
                # ... further rendering options
            )
            pil_image = bitmap.to_pil()
            # 保存为文件
            image_path = os.path.join(save_dir, f"{prefix}_{page_num + 1}.{image_type.value}")
            image_path = handle_existence(image_path, exist_handle_type)
            if image_path:
                pil_image.save(image_path, quality=95)
