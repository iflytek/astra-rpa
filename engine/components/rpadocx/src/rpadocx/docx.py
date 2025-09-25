import os
import platform
import sys
from typing import Tuple

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH
from rpaatomic.utils import FileExistenceType
from rpadocx import *
from rpadocx.core import IDocxCore
from rpadocx.docx_obj import DocxObj
from rpadocx.error import *

if sys.platform == "win32":
    from rpadocx.core_win import DocxCore
elif platform.system() == "Linux":
    from rpadocx.core_unix import DocxCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

DocxCore: IDocxCore = DocxCore()


class Docx:
    @staticmethod
    @IDocxCore.validate_path("file_path")
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("encoding", level=AtomicLevel.ADVANCED),
            atomicMg.param("open_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "open_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.open_pwd.show",
                        expression="return $this.open_pwd_flag.value == true",
                    )
                ],
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param("write_pwd_flag", level=AtomicLevel.ADVANCED),
            atomicMg.param(
                "write_pwd",
                dynamics=[
                    DynamicsItem(
                        key="$this.write_pwd.show",
                        expression="return $this.write_pwd_flag.value == true",
                    )
                ],
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("doc_obj", types="DocxObj"),
        ],
    )
    def open_docx(
        file_path: PATH = "",
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = True,
        encoding: EncodingType = EncodingType.UTF,
        open_pwd_flag: bool = False,
        open_pwd: str = "",
        write_pwd_flag: bool = False,
        write_pwd: str = "",
    ) -> DocxObj:
        if not open_pwd_flag:
            open_pwd = ""
        if not write_pwd_flag:
            write_pwd = ""
        try:
            doc_obj = DocxCore.open(
                file_path,
                default_application,
                visible_flag,
                encoding,
                open_pwd,
                write_pwd,
            )
            return DocxObj(doc_obj)
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(file_path),
                "打开文档失败，请检查文件路径是否正确！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param("doc", types="DocxObj"),
        ],
        outputList=[
            atomicMg.param("doc_data", types="Str"),
        ],
    )
    def read_docx(doc: DocxObj, select_range: SelectRangeType = SelectRangeType.ALL):
        if not doc:
            raise BaseException(DOC_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            doc_data = DocxCore.read(doc.obj, select_range)
            return doc_data
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("doc_obj", types="DocxObj"),
            atomicMg.param("doc_create_path", types="PATH"),
        ],
    )
    def create_docx(
        file_path: str = "",
        file_name: str = "",
        default_application: ApplicationType = ApplicationType.WORD,
        visible_flag: bool = True,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ) -> Tuple[DocxObj, PATH]:
        if not os.path.exists(file_path):
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )
        try:
            if file_name:
                file_name += ".docx"
            else:
                file_name = "新建Word文档.docx"
            doc_obj, doc_create_path = DocxCore.create(
                file_path,
                file_name,
                visible_flag,
                default_application,
                exist_handle_type,
            )
            return DocxObj(doc_obj), doc_create_path
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(file_path),
                "打开文档失败，请检查文件路径是否正确！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("save_file_path", types="PATH"),
        ],
    )
    def save_docx(
        doc: DocxObj,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        close_flag: bool = False,
    ):
        if not doc:
            raise BaseException(DOC_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            save_file_path = DocxCore.save(doc.obj, file_path, file_name, save_type, exist_handle_type, close_flag)
            return save_file_path
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(e),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type.value == '{}' && $this.close_range_flag.value == '{}'".format(
                            SaveType.SAVE_AS.value, CloseRangeType.ONE.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "pkill_flag",
                dynamics=[
                    DynamicsItem(
                        key="$this.pkill_flag.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ALL.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type.value == '{}' && $this.close_range_flag.value == '{}'".format(
                            SaveType.SAVE_AS.value, CloseRangeType.ONE.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def close_docx(
        doc: DocxObj,
        close_range_flag: CloseRangeType = CloseRangeType.ONE,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        pkill_flag: bool = False,
    ):
        if not doc:
            raise BaseException(DOC_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            DocxCore.close(
                doc.obj,
                file_path,
                file_name,
                save_type,
                exist_handle_type,
                close_range_flag,
                pkill_flag,
            )
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param("font_size", required=False),
            atomicMg.param("font_name", required=False),
            atomicMg.param(
                "font_color",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
                required=False,
            ),
        ],
        outputList=[],
    )
    def insert_docx(
        doc: DocxObj,
        text: str = "",
        enter_flag: bool = False,
        font_size: int = 12,
        bold_flag: bool = False,
        italic_flag: bool = False,
        underline_flag: UnderLineStyle = UnderLineStyle.DEFAULT,
        font_name: str = "宋体",
        font_color: str = "0,0,0",
    ):
        if not doc:
            raise BaseException(DOC_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            if not font_color:
                font_color = "0,0,0"
            text_format = {
                "font_size": font_size,
                "bold": bold_flag,
                "italic": italic_flag,
                "underline": underline_flag,
                "font_name": font_name,
                "font_color": font_color,  # 0,0,0
            }
            DocxCore.insert(doc.obj, text, enter_flag, text_format)
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "p_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_start.show",
                        expression="return $this.select_type.value == '{}'".format(SelectTextType.PARAGRAPH.value),
                    )
                ],
            ),
            atomicMg.param(
                "p_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_end.show",
                        expression="return $this.select_type.value == '{}'".format(SelectTextType.PARAGRAPH.value),
                    )
                ],
            ),
            atomicMg.param(
                "r_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_start.show",
                        expression="return $this.select_type.value == '{}'".format(SelectTextType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "r_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_end.show",
                        expression="return $this.select_type.value == '{}'".format(SelectTextType.ROW.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def select_text(
        doc: DocxObj,
        select_type: SelectTextType = SelectTextType.ALL,
        p_start: int = 1,
        p_end: int = 1,
        r_start: int = 1,
        r_end: int = 1,
    ):
        if not doc:
            raise BaseException(DOC_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        if p_start > p_end or r_start > r_end or not IDocxCore.are_positive_integers(p_start, p_end, r_start, r_end):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请正确输入起始行号或段落号！")
        try:
            DocxCore.select(doc.obj, select_type, p_start, p_end, r_start, r_end)
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "选中文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "content",
                dynamics=[
                    DynamicsItem(
                        key="$this.content.show",
                        expression="return $this.by.value == '{}'".format(CursorPointerType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "c_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_idx.show",
                        expression="return $this.by.value == '{}'".format(CursorPointerType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "p_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_idx.show",
                        expression="return $this.by.value == '{}'".format(CursorPointerType.PARAGRAPH.value),
                    )
                ],
            ),
            atomicMg.param(
                "r_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.r_idx.show",
                        expression="return $this.by.value == '{}'".format(CursorPointerType.ROW.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def get_cursor_position(
        doc: DocxObj,
        by: CursorPointerType = CursorPointerType.ALL,
        pos: CursorPositionType = CursorPositionType.HEAD,
        content: str = "",
        c_idx: int = 1,
        p_idx: int = 1,
        r_idx: int = 1,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if not IDocxCore.are_positive_integers(c_idx, p_idx, r_idx):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请输入正确的数值!")
        try:
            DocxCore.cursor_position(doc.obj, by, pos, content, c_idx, p_idx, r_idx)
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "定位光标位置失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "unitupdown",
                dynamics=[
                    DynamicsItem(
                        key="$this.unitupdown.show",
                        expression="return ['{}', '{}'].includes($this.direction.value)".format(
                            MoveDirectionType.UP.value, MoveDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "unitleftright",
                dynamics=[
                    DynamicsItem(
                        key="$this.unitleftright.show",
                        expression="return ['{}', '{}'].includes($this.direction.value)".format(
                            MoveDirectionType.LEFT.value, MoveDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def move_cursor(
        doc: DocxObj,
        direction: MoveDirectionType = MoveDirectionType.UP,
        unitupdown: MoveUpDownType = MoveUpDownType.ROW,
        unitleftright: MoveLeftRightType = MoveLeftRightType.CHARACTER,
        distance: int = 0,
        with_shift: bool = False,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if not IDocxCore.are_positive_integers(distance):
            raise BaseException(CONTENT_FORMAT_ERROR_FORMAT, "请输入正确的数值!")
        try:
            DocxCore.move_cursor(doc.obj, direction, unitupdown, unitleftright, distance, with_shift)
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "移动光标失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic("Docx", inputList=[], outputList=[])
    def insert_sep(doc: DocxObj, sep_type: InsertionType = InsertionType.PARAGRAPH):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            DocxCore.insert_sep(doc.obj, sep_type)
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "插入失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic("Docx", inputList=[], outputList=[])
    def insert_hyperlink(doc: DocxObj, url: str = "", display: str = ""):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        DocxCore.insert_hyperlink(doc.obj, url, display)

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "img_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.img_path.show",
                        expression="return $this.img_from.value == '{}'".format(InsertImgType.FILE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_img(
        doc: DocxObj,
        img_from: InsertImgType = InsertImgType.FILE,
        img_path: str = "",
        scale: int = 100,
        newline: bool = False,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        DocxCore.insert_img(doc.obj, img_from, img_path, scale, newline)

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "text",
                dynamics=[
                    DynamicsItem(
                        key="$this.text.show",
                        expression="return $this.search_type.value == '{}'".format(SearchTableType.TEXT.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("table_content", types="List"),
        ],
    )
    def read_table(
        doc: DocxObj,
        search_type: SearchTableType = SearchTableType.IDX,
        idx: int = 1,
        text: str = "",
    ) -> DocxObj:
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            table_content = DocxCore.read_table(doc.obj, search_type, idx, text)
            return table_content
        except Exception as e:
            print(e)
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "读取表格失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "font_size",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_size.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_color",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.font_color.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_set",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_set.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_bold",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_bold.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "font_italic",
                dynamics=[
                    DynamicsItem(
                        key="$this.font_italic.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "underline",
                dynamics=[
                    DynamicsItem(
                        key="$this.underline.show",
                        expression="return $this.if_change_font.value == true",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_table(
        doc: DocxObj,
        table_content: list = "",
        table_behavior: TableBehavior = TableBehavior.DEFAULT,
        alignment: RowAlignment = RowAlignment.LEFT,
        v_alignment: VerticalAlignment = VerticalAlignment.TOP,
        border: bool = True,
        if_change_font: bool = False,
        font_size=None,
        font_color=None,
        font_set=None,
        font_bold: bool = False,
        font_italic: bool = False,
        underline: UnderLineStyle = UnderLineStyle.DEFAULT,
        newline: bool = True,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            DocxCore.insert_table(
                doc.obj,
                table_content,
                table_behavior,
                alignment,
                v_alignment,
                border,
                if_change_font,
                font_size,
                font_color,
                font_set,
                font_bold,
                font_italic,
                underline,
                newline,
            )
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "插入表格失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "delete_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_str.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "str_delete_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.str_delete_all.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "delete_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_idx.show",
                        expression="return $this.str_delete_all.value == false && $this.delete_mode.value == '{}'".format(
                            DeleteMode.CONTENT.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "p_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_start.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.RANGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "p_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.p_end.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.RANGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "c_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_start.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.RANGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "c_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.c_end.show",
                        expression="return $this.delete_mode.value == '{}'".format(DeleteMode.RANGE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete(
        doc: DocxObj,
        delete_mode: DeleteMode = DeleteMode.ALL,
        delete_str: str = "",
        delete_idx: int = 0,
        str_delete_all: bool = False,
        p_start: int = 0,
        c_start: int = 0,
        p_end: int = 0,
        c_end: int = 0,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            DocxCore.delete(
                doc.obj,
                delete_mode,
                delete_str,
                delete_idx,
                str_delete_all,
                p_start,
                c_start,
                p_end,
                c_end,
            )
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "删除内容失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "new_word",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_word.show",
                        expression="return $this.replace_type.value == '{}'".format(ReplaceType.STR.value),
                    )
                ],
            ),
            atomicMg.param(
                "img_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.img_path.show",
                        expression="return $this.replace_type.value == '{}'".format(ReplaceType.IMG.value),
                    )
                ],
            ),
            atomicMg.param(
                "delete_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_idx.show",
                        expression="return $this.str_delete_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def replace(
        doc: DocxObj,
        origin_word: str = "",
        replace_type: ReplaceType = ReplaceType.STR,
        new_word: str = "",
        img_path: str = "",
        replace_method: ReplaceMethodType = ReplaceMethodType.ALL,
        ignore_case: bool = True,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            _ = DocxCore.replace(
                doc.obj,
                replace_type,
                origin_word,
                new_word,
                img_path,
                replace_method,
                ignore_case,
            )
        except Exception as e:
            raise BaseException(
                WORD_READ_ERROR_FORMAT.format(doc),
                "查找替换内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "paragraph_idx",
                dynamics=[
                    DynamicsItem(
                        key="$this.paragraph_idx.show",
                        expression="return $this.comment_type.value == '{}'".format(CommentType.POSITION.value),
                    )
                ],
            ),
            atomicMg.param(
                "start",
                dynamics=[
                    DynamicsItem(
                        key="$this.start.show",
                        expression="return $this.comment_type.value == '{}'".format(CommentType.POSITION.value),
                    )
                ],
            ),
            atomicMg.param(
                "end",
                dynamics=[
                    DynamicsItem(
                        key="$this.end.show",
                        expression="return $this.comment_type.value == '{}'".format(CommentType.POSITION.value),
                    )
                ],
            ),
            atomicMg.param(
                "target_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.target_str.show",
                        expression="return $this.comment_type.value == '{}'".format(CommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "comment_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_all.show",
                        expression="return $this.comment_type.value == '{}'".format(CommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "comment_index",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_index.show",
                        expression="return $this.comment_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def create_comment(
        doc: DocxObj,
        comment: str = "",
        comment_type: CommentType = CommentType.POSITION,
        paragraph_idx: int = 1,
        start: int = 1,
        end: int = 1,
        target_str: str = "",
        comment_all: bool = True,
        comment_index: int = 1,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            DocxCore.create_comment(
                doc.obj,
                paragraph_idx,
                start,
                end,
                comment,
                comment_type,
                target_str,
                comment_all,
                comment_index,
            )
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "创建批注失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "comment_index",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_index.show",
                        expression="return $this.delete_all.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete_comment(doc: DocxObj, delete_all: bool = False, comment_index: int = 1):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        try:
            DocxCore.delete_comment(doc.obj, comment_index, delete_all)
        except Exception as e:
            raise BaseException(WORD_READ_ERROR_FORMAT.format(doc), "删除批注失败，请检查文档是否打开！")

    @staticmethod
    @atomicMg.atomic(
        "Docx",
        inputList=[
            atomicMg.param(
                "output_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.output_name.show",
                        expression="return $this.default_name.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "page_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_type.show",
                        expression="return $this.output_file_type.value == '{}'".format(FileType.PDF.value),
                    )
                ],
            ),
            atomicMg.param(
                "page_start",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_start.show",
                        expression="return $this.page_type.value == '{}'".format(ConvertPageType.RANGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "page_end",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_end.show",
                        expression="return $this.page_type.value == '{}'".format(ConvertPageType.RANGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "output_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
        ],
        outputList=[],
    )
    def convert_format(
        doc: DocxObj,
        output_path: str = "",
        default_name: bool = True,
        output_name: str = None,
        page_type: ConvertPageType = ConvertPageType.ALL,
        output_file_type: FileType = FileType.PDF,
        page_start: int = 1,
        page_end: int = 1,
        save_type: SaveFileType = SaveFileType.WARN,
    ):
        if not doc:
            raise BaseException(
                DOC_NOT_EXIST_ERROR_FORMAT,
                "没有查找到Word对象，请检查输入的Word对象是否正确!",
            )
        if default_name:
            document_name = doc.obj.Name
            output_name, extension = os.path.splitext(document_name)

        try:
            if output_file_type == FileType.PDF:
                DocxCore.convert_to_pdf(
                    doc.obj,
                    output_path,
                    output_name,
                    page_type,
                    page_start,
                    page_end,
                    save_type,
                )
            elif output_file_type == FileType.TXT:
                DocxCore.convert_to_txt(doc.obj, output_path, output_name, save_type)
        except Exception as e:
            raise BaseException(
                FILENAME_ALREADY_EXIST_ERROR.format(output_name),
                "导出失败，文件名已存在！",
            )
