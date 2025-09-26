import os
import platform
import sys
from typing import Any

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.utils import FileExistenceType, handle_existence

from rpapdf import MergeType, PictureType, SelectRangeType, TextSaveType
from rpapdf.core import IPDFCore
from rpapdf.error import *

if sys.platform == "win32":
    from rpapdf.core_win import PDFCore
elif platform.system() == "Linux":
    from rpapdf.core_unix import PDFCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

PDFCore: IPDFCore = PDFCore()


# file_type : "file", "folder", "files"


class PDF:
    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("password", required=False, level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("pdf_pages_num", types="Int")],
    )
    def get_pages_num(file_path: str = "", password: str = "") -> int:
        """
        获取PDF文件的页数
        :param file_path:
        :param password:
        :return:
        """
        return PDFCore.get_pages_num(file_path, password)

    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": []},
                ),
            ),
            atomicMg.param("password", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "page_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_range.show",
                        expression="return $this.select_range.value == '{}'".format(SelectRangeType.PART.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_dir",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_dir.show",
                        expression="return ['{}', '{}', '{}'].includes($this.text_save_type.value)".format(
                            TextSaveType.TXT.value,
                            TextSaveType.WORD_AND_TXT.value,
                            TextSaveType.WORD.value,
                        ),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "save_file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_file_name.show",
                        expression="return ['{}', '{}', '{}'].includes($this.text_save_type.value)".format(
                            TextSaveType.TXT.value,
                            TextSaveType.WORD_AND_TXT.value,
                            TextSaveType.WORD.value,
                        ),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "exist_handle_type",
                level=AtomicLevel.ADVANCED,
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return ['{}', '{}', '{}'].includes($this.text_save_type.value)".format(
                            TextSaveType.TXT.value,
                            TextSaveType.WORD_AND_TXT.value,
                            TextSaveType.WORD.value,
                        ),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("pdf_text", types="Any")],
    )
    def get_pdf_text(
        file_path: str = "",
        password: str = "",
        select_range: SelectRangeType = SelectRangeType.ALL,
        page_range: str = "",
        text_save_type: TextSaveType = TextSaveType.NONE,
        save_dir: str = "",
        save_file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> Any:
        """
        获取PDF文件的文本内容
        :param file_path:
        :param file_path:
        :param password:
        :param select_range:
        :param page_range:
        :param text_save_type:
        :param save_dir:
        :param save_file_name:
        :param exist_handle_type:
        :return:
        """
        pdf_text = PDFCore.get_page_text(file_path, password, page_range, select_range)
        if text_save_type != TextSaveType.NONE:
            pdf_text_str = "\n".join(pdf_text)

            # 配置保存路径
            if not save_file_name:
                word_save_file_name = os.path.basename(file_path).split(".")[0] + ".docx"
                txt_save_file_name = os.path.basename(file_path).split(".")[0] + ".txt"
            else:
                word_save_file_name = save_file_name + ".docx"
                txt_save_file_name = save_file_name + ".txt"

            if text_save_type == TextSaveType.WORD or text_save_type == TextSaveType.WORD_AND_TXT:
                word_file_path = os.path.join(save_dir, word_save_file_name)
                word_file_path = handle_existence(word_file_path, exist_handle_type)
                if word_file_path:
                    PDFCore.write_text_to_word(pdf_text_str, word_file_path)
            if text_save_type == TextSaveType.TXT or text_save_type == TextSaveType.WORD_AND_TXT:
                txt_file_path = os.path.join(save_dir, txt_save_file_name)
                txt_file_path = handle_existence(txt_file_path, exist_handle_type)
                if txt_file_path:
                    with open(txt_file_path, "w", encoding="utf-8") as f:
                        f.write(pdf_text_str)

        return pdf_text

    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("pwd", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "page_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_range.show",
                        expression="return $this.select_range.value == '{}'".format(SelectRangeType.PART.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "save_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("prefix", required=False),
            atomicMg.param("exist_handle_type", level=AtomicLevel.ADVANCED),
        ],
        outputList=[],
    )
    def get_pdf_images(
        file_path: str = "",
        pwd: str = "",
        select_range: SelectRangeType = SelectRangeType.ALL,
        page_range: str = "",
        image_type: PictureType = PictureType.PNG,
        save_dir: str = "",
        prefix: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> list:
        """
        获取PDF文件里的图片
        :param file_path: PDF文件路径
        :param pwd: PDF文件密码（如果有）
        :param select_range: 选择范围（例如："ALL"或"PART"）
        :param page_range: 页面范围（例如："1-5"或"1,3,5"）
        :param save_dir: 图片保存路径
        :param image_type: 图片类型（例如："png"或"jpeg"）
        :param prefix: 图片文件名前缀
        :param exist_handle_type: 文件存在处理类型
        :return: 包含图片数据的列表
        """
        if select_range == SelectRangeType.PART:
            page_range = ""
        return PDFCore.get_images_in_page(file_path, pwd, page_range, save_dir, image_type, prefix, exist_handle_type)

    @staticmethod
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_folder_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_folder_path.show",
                        expression="return $this.merge_type.value == '{}'".format(MergeType.FOLDER.value),
                    )
                ],
            ),
            atomicMg.param(
                "files_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "files"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.files_path.show",
                        expression="return $this.merge_type.value == '{}'".format(MergeType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("new_file_name", required=False),
            atomicMg.param("new_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "new_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_pwd.show",
                        expression="return $this.new_pwd_flag.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
            ),
            atomicMg.param("exist_handle_type", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("pdf_merge_file_path", types="Str")],
    )
    def merge_pdf_files(
        merge_type: MergeType = MergeType.FOLDER,
        file_folder_path: str = "",
        files_path: str = "",
        save_dir: str = "",
        new_file_name: str = "",
        new_pwd_flag: bool = False,
        new_pwd: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        合并多个PDF文件
        :param merge_type: 文件合并类型（文件夹或文件）
        :param file_folder_path: 文件夹路径
        :param files_path: 文件路径
        :param save_dir: 保存路径
        :param new_file_name: 合并后的文件名
        :param new_pwd_flag: 是否设置新密码
        :param new_pwd: 新密码
        :param exist_handle_type: 文件存在处理类型
        :return: 合并后的文件路径
        """
        if file_folder_path and (not os.path.exists(file_folder_path)):
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_folder_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )
        if not new_pwd_flag:
            new_pwd = ""
        pdf_merge_file_path = PDFCore.merge_pdf_files(
            merge_type,
            file_folder_path,
            files_path,
            save_dir,
            new_file_name,
            new_pwd,
            exist_handle_type,
        )

        return pdf_merge_file_path

    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("pwd", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param("page_range", types="Str"),
            atomicMg.param(
                "save_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("new_file_name", required=False),
            atomicMg.param("new_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "new_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_pwd.show",
                        expression="return $this.new_pwd_flag.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param("exist_handle_type", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("extract_file_path", types="Str")],
    )
    def extract_pdf_file(
        file_path: str = "",
        pwd: str = "",
        page_range: str = "",
        save_dir: str = "",
        new_file_name: str = "",
        new_pwd_flag: bool = False,
        new_pwd: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        抽取PDF文件部分页面，组成新的PDF文件
        """
        if not new_pwd_flag:
            new_pwd = ""
        extract_file_path = PDFCore.extract_pdf_pages(
            file_path,
            pwd,
            save_dir,
            page_range,
            new_file_name,
            new_pwd,
            exist_handle_type,
        )
        return extract_file_path

    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("pwd", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "page_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_range.show",
                        expression="return $this.select_range.value == '{}'".format(SelectRangeType.PART.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("new_file_name", required=False),
            atomicMg.param("exist_handle_type", level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("forms_file_path", types="Str")],
    )
    def extract_forms_from_pdf(
        file_path: str,
        pwd: str = "",
        select_range: SelectRangeType = SelectRangeType.ALL,
        page_range: str = "",
        combine_flag: bool = True,
        save_dir: str = "",
        new_file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> str:
        """
        提取PDF中的表格
        :param file_path:
        :param pwd:
        :param select_range:
        :param page_range:
        :param combine_flag:
        :param save_dir:
        :param new_file_name:
        :param exist_handle_type:
        :return:
        """
        if select_range == SelectRangeType.PART:
            page_range = ""
        forms_file_path = PDFCore.extract_forms_from_pdf(
            file_path,
            pwd,
            page_range,
            combine_flag,
            save_dir,
            new_file_name,
            exist_handle_type,
        )
        return forms_file_path

    @staticmethod
    @IPDFCore.validate_path("file_path")
    @atomicMg.atomic(
        "PDF",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("pwd", required=False, level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "page_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_range.show",
                        expression="return $this.select_range.value == '{}'".format(SelectRangeType.PART.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("prefix", required=False),
            atomicMg.param("exist_handle_type", level=AtomicLevel.ADVANCED),
        ],
        outputList=[],
    )
    def convert_pdf_to_img(
        file_path: str,
        pwd: str = "",
        image_type: PictureType = PictureType.PNG,
        select_range: SelectRangeType = SelectRangeType.ALL,
        page_range: str = "",
        save_dir: str = "",
        prefix: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """
        将PDF文件转换为图片文件
        :param file_path:
        :param pwd:
        :param image_type:
        :param select_range:
        :param page_range:
        :param save_dir:
        :param prefix:
        :param exist_handle_type:
        :return:
        """
        if select_range == SelectRangeType.ALL:
            page_range = ""
        PDFCore.pdf_to_image(file_path, pwd, save_dir, page_range, image_type, prefix, exist_handle_type)
