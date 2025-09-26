import os
from abc import ABC, abstractmethod
from functools import wraps

from docx import Document

from rpapdf import FileExistenceType, PictureType


class IPDFCore(ABC):
    @staticmethod
    def validate_path(param_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 通过参数名称获取参数值
                path = kwargs.get(param_name)

                # 如果参数值不存在，抛出异常
                if not os.path.exists(path):
                    raise ValueError(f"{param_name} 路径不存在")

                if not path.endswith(".pdf"):
                    raise ValueError(f"{param_name} 路径必须是.docx 或.doc 结尾")
                # 如果校验通过，调用原函数
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def parse_pages(page_str: str, total_pages: int):
        """
        PDF文件公共方法，解析页码参数
        解析输入参数成列表，如"1,3,5-8,12" -> [1,3,5,6,7,8,12]
        """
        page_str = page_str.replace("，", ",")  # 处理中文逗号
        page_str = page_str.replace(" ", "")  # 去除空格
        pages_range = page_str.split(",")
        page_nums = []
        for p_range in pages_range:
            if "-" in p_range:
                try:
                    start_ind = int(p_range.split("-")[0])
                    end_ind = int(p_range.split("-")[-1])
                except ValueError:
                    raise ValueError(f"页码{p_range}不符合规定！")
                if start_ind > end_ind:
                    start_ind, end_ind = end_ind, start_ind
                nums = list(range(start_ind, end_ind + 1))
                page_nums.extend(nums)
            else:
                try:
                    num = int(p_range)
                except ValueError:
                    raise ValueError(f"页码{p_range}不符合规定！")
                page_nums.append(num)
        result_page_nums = []
        for page_num in page_nums:
            if page_num > total_pages or page_num < 1:
                raise ValueError(f"页码{page_num}不符合规定！")
            result_page_nums.append(page_num - 1)
        return result_page_nums

    @staticmethod
    def write_text_to_word(text, word_path):
        """
        转化text列表为word文档
        """
        doc = Document()
        doc.add_paragraph(text)  # 将提取的文本添加到Word文档中
        doc.save(word_path)

    @staticmethod
    @abstractmethod
    def get_pages_num(file_path, pwd) -> int:
        pass

    @staticmethod
    @abstractmethod
    def get_page_text(file_path, pwd, page_range) -> list:
        pass

    @staticmethod
    @abstractmethod
    def get_images_in_page(file_path, pwd, page_range, save_dir) -> list:
        pass

    @staticmethod
    @abstractmethod
    def merge_pdf_files(file_path, pwd) -> str:
        pass

    @staticmethod
    @abstractmethod
    def extract_pdf_pages(
        file_path: str,
        pwd: str = "",
        save_dir: str = "",
        page_range: str = "",
        new_file_name: str = "",
        new_pwd: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.OVERWRITE,
    ) -> str:
        pass

    @staticmethod
    @abstractmethod
    def pdf_to_image(
        file_path: str,
        pwd: str = "",
        save_dir: str = "",
        page_range: str = "",
        image_type: PictureType = PictureType.PNG,
        prefix: str = "",
    ):
        pass
