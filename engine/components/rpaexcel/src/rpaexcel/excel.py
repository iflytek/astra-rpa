import ast
import os
import platform
import sys

import psutil
import win32com
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH

from rpaexcel import *
from rpaexcel.core import IExcelCore
from rpaexcel.error import *
from rpaexcel.excel_obj import ExcelObj

if sys.platform == "win32":
    from rpaexcel.core_win.core_win import ExcelCore
    from rpaexcel.core_win.sheet import SheetCore

    SheetCore: IExcelCore = SheetCore()
elif platform.system() == "Linux":
    from rpaexcel.core_unix import ExcelCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

ExcelCore: IExcelCore = ExcelCore()


class Excel:
    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [".xlsx", ".xls"], "file_type": "file"},
                ),
            ),
            atomicMg.param("password", level=AtomicLevel.ADVANCED, required=False),
        ],
        outputList=[
            atomicMg.param("open_excel_obj", types="ExcelObj"),
        ],
    )
    def open_excel(
        file_path: PATH = "",
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = True,
        password: str = "",
        update_links: bool = True,
    ) -> ExcelObj:
        if not os.path.exists(file_path):
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_path),
                "填写的文件路径有误，请输入正确的路径！",
            )
        open_excel_obj = ExcelCore.open(file_path, default_application, visible_flag, password, update_links)
        return ExcelObj(open_excel_obj, file_path)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[],
        outputList=[
            atomicMg.param("get_excel_obj", types="ExcelObj"),
        ],
    )
    def get_excel(file_name) -> ExcelObj:
        get_excel_obj = ExcelCore.get_exist_excel(file_name)
        return ExcelObj(get_excel_obj, "")

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("password", required=False, level=AtomicLevel.ADVANCED),
        ],
        outputList=[
            atomicMg.param("create_excel_obj", types="ExcelObj"),
            atomicMg.param("excel_path", types="Str"),
        ],
    )
    def create_excel(
        file_path: str = "",
        file_name: str = "",
        default_application: ApplicationType = ApplicationType.EXCEL,
        visible_flag: bool = True,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        password: str = "",
    ) -> tuple[ExcelObj, str]:
        if not os.path.exists(file_path):
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )
        if file_name:
            file_name += ".xlsx"
        else:
            file_name = "新建Excel文档.xlsx"
        create_excel_obj, excel_path = ExcelCore.create(
            file_path,
            file_name,
            default_application,
            visible_flag,
            exist_handle_type,
            password,
        )
        return (
            ExcelObj(create_excel_obj, os.path.join(file_path, file_name)),
            excel_path,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
                required=False,
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
                required=False,
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
        outputList=[],
    )
    def save_excel(
        excel: ExcelObj,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        close_flag: bool = False,
    ):
        if not excel:
            raise BaseException(EXCEL_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
        try:
            ExcelCore.save(
                excel.obj,
                file_path,
                file_name,
                save_type,
                exist_handle_type,
                close_flag,
            )
        except Exception as e:
            raise BaseException(
                EXCEL_READ_ERROR_FORMAT.format(excel),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "excel",
                dynamics=[
                    DynamicsItem(
                        key="$this.excel.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
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
                "save_type_one",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type_one.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_type_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type_all.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ALL.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type_one.value == '{}' && $this.close_range_flag.value == '{}'".format(
                            SaveType.SAVE_AS.value, CloseRangeType.ONE.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type_one.value == '{}'".format(SaveType.SAVE_AS.value),
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
    def close_excel(
        close_range_flag: CloseRangeType = CloseRangeType.ONE,
        excel: ExcelObj = None,
        save_type_one: SaveType = SaveType.SAVE,
        save_type_all: SaveType_ALL = SaveType_ALL.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        pkill_flag: bool = False,
    ):
        """
        关闭Excel文件
        :param excel: Excel对象，当close_range_flag为ONE时必填
        :param close_range_flag: 关闭范围类型（单个/所有）
        :param save_type_one: 单个文件保存类型（保存/另存为/不保存）
        :param save_type_all: 所有文件保存类型（保存/不保存）
        :param file_path: 保存路径
        :param file_name: 保存文件名
        :param exist_handle_type: 文件存在处理方式
        :param pkill_flag: 是否强制结束进程
        :return: None
        """
        try:
            if close_range_flag == CloseRangeType.ALL:
                # 获取所有打开的Excel进程
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        if proc.info["name"].lower() in ["excel.exe", "et.exe"]:
                            # 获取Excel应用程序实例
                            excel_app = win32com.client.GetObject(Class="Excel.Application")
                            # 根据save_type_all处理所有工作簿
                            for workbook in excel_app.Workbooks:
                                if save_type_all == SaveType_ALL.SAVE:
                                    workbook.Save()
                                # SAVE_NONE 不做任何保存操作
                            # 关闭工作簿
                            workbook.Close(SaveChanges=False)
                            # 退出Excel应用程序
                            excel_app.Quit()
                            # 如果设置了强制结束进程
                            if pkill_flag:
                                proc.kill()
                    except Exception as e:
                        print(f"关闭Excel进程时出错: {e}")
                return None
            else:
                # 关闭单个Excel文件
                if not excel:
                    raise BaseException(EXCEL_NOT_EXIST_ERROR_FORMAT, "文档不存在，请先打开文档！")
                try:
                    ExcelCore.close(
                        excel.obj,
                        close_range_flag,
                        save_type_one,
                        file_path,
                        file_name,
                        exist_handle_type,
                        pkill_flag,
                    )
                except Exception as e:
                    raise BaseException(
                        EXCEL_READ_ERROR_FORMAT.format(excel),
                        "读取文档内容失败，请检查文档是否打开！",
                    )
        except Exception as e:
            raise BaseException(
                EXCEL_READ_ERROR_FORMAT.format(excel),
                "读取文档内容失败，请检查文档是否打开！",
            )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("start_row", required=False),
            atomicMg.param("start_col", required=False),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[],
    )
    def edit_excel(
        excel: ExcelObj,
        edit_range: EditRangeType = EditRangeType.ROW,
        sheet_name: str = "",
        start_col: str = "A",
        start_row: str = "1",
        value: str = "",
    ) -> ExcelObj:
        if not isinstance(value, list):
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                try:
                    value = ast.literal_eval(value)
                except:
                    raise BaseException(
                        INPUT_DATA_ERROR_FORMAT.format(value),
                        "填写的列表格式有误，注意是否输入了中文字符！",
                    )
            else:
                value = [value]
        if edit_range == EditRangeType.AREA and not isinstance(value, list):
            value = [value]
        ExcelCore.edit(excel.obj, start_col, start_row, sheet_name, edit_range, value)
        return excel

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "column",
                dynamics=[
                    DynamicsItem(
                        key="$this.column.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("read_excel_contents", types="Any"),
        ],
    )
    def read_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        read_range: ReadRangeType = ReadRangeType.CELL,
        start_col: str = "",
        end_col: str = "",
        cell: str = "",
        row: int = 1,
        column: str = "",
        start_row: int = 1,
        end_row: int = 1,
        read_display: bool = True,
        trim_spaces: bool = False,
        replace_none: bool = True,
    ):
        read_excel_contents = ExcelCore.read(
            excel.obj,
            sheet_name,
            start_col,
            end_col,
            read_range,
            cell,
            row,
            column,
            start_row,
            end_row,
            read_display,
            trim_spaces,
            replace_none,
        )
        return read_excel_contents

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_position.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param("col_width", required=False),
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "bg_color",
                required=False,
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
            ),
            atomicMg.param(
                "font_color",
                required=False,
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
            ),
            atomicMg.param("font_size", required=False),
            atomicMg.param(
                "numberformat_other",
                dynamics=[
                    DynamicsItem(
                        key="$this.numberformat_other.show",
                        expression="return $this.numberformat.value == '{}'".format(NumberFormatType.CUSTOM.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "auto_row_height",
                dynamics=[
                    DynamicsItem(
                        key="$this.auto_row_height.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "auto_column_width",
                dynamics=[
                    DynamicsItem(
                        key="$this.auto_column_width.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def design_cell_type(
        excel: ExcelObj,
        sheet_name: str = "",
        design_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        range_position: str = "",
        col: str = "",
        row: str = "",
        col_width: str = "",
        bg_color: str = "",
        font_color: str = "",
        font_type: FontType = FontType.NO_CHANGE,
        font_name: FontNameType = FontNameType.NO_CHANGE,
        font_size: int = 11,
        numberformat: NumberFormatType = NumberFormatType.NO_CHANGE,
        numberformat_other: str = "",
        horizontal_align: HorizontalAlign = HorizontalAlign.NO_CHANGE,
        vertical_align: VerticalAlign = VerticalAlign.NO_CHANGE,
        wrap_text: bool = True,
        auto_row_height: bool = False,
        auto_column_width: bool = False,
    ):
        ExcelCore.cell_type(
            excel.obj,
            cell_position,
            range_position,
            col_width,
            col,
            row,
            bg_color,
            font_color,
            font_type,
            sheet_name,
            font_name,
            font_size,
            numberformat,
            numberformat_other,
            design_type,
            horizontal_align,
            vertical_align,
            wrap_text,
            auto_row_height,
            auto_column_width,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_position.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("copy_excel_contents", types="Str"),
        ],
    )
    def copy_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        copy_range_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "A1",
        row: str = "",
        col: str = "",
        range_position: str = "A1:B5",
    ):
        copy_excel_contents = ExcelCore.copy(
            excel.obj,
            cell_position,
            row,
            col,
            copy_range_type,
            sheet_name,
            range_position,
        )
        return copy_excel_contents

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[],
    )
    def paste_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        paste_type: PasteType = PasteType.ALL,
        start_location: str = "A1",
        skip_blanks: bool = False,
        transpose: bool = False,
    ):
        ExcelCore.paste(excel.obj, start_location, sheet_name, paste_type, skip_blanks, transpose)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "coordinate",
                dynamics=[
                    DynamicsItem(
                        key="$this.coordinate.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "data_region",
                dynamics=[
                    DynamicsItem(
                        key="$this.data_region.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.direction.show",
                        expression="return ['{}', '{}'].includes($this.delete_range_excel.value)".format(
                            ReadRangeType.CELL.value, ReadRangeType.AREA.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete_excel_cell(
        excel: ExcelObj,
        sheet_name: str = "",
        delete_range_excel: ReadRangeType = ReadRangeType.CELL,
        coordinate: str = "",
        row: str = "",
        col: str = "",
        data_region: str = "",
        direction: DeleteCellDirection = DeleteCellDirection.LOWER_MOVE_UP,
    ):
        ExcelCore.delete_cell(
            excel.obj,
            coordinate,
            row,
            col,
            delete_range_excel,
            data_region,
            sheet_name,
            direction,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "data_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.data_range.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def clear_excel_content(
        excel: ExcelObj,
        sheet_name: str,
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_location: str = "",
        row: str = "",
        col: str = "",
        data_range: str = "A1:B5",
        clear_type: ClearType = ClearType.CONTENT,
    ):
        ExcelCore.clear_content(
            excel.obj,
            sheet_name,
            cell_location,
            select_type,
            row,
            col,
            data_range,
            clear_type,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "row_direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.row_direction.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "col_direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.col_direction.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "insert_num",
                dynamics=[
                    DynamicsItem(
                        key="$this.insert_num.show",
                        expression="return $this.blank_rows.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "insert_content",
                dynamics=[
                    DynamicsItem(
                        key="$this.insert_content.show",
                        expression="return $this.blank_rows.value == false",
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_excel_row_or_column(
        excel: ExcelObj,
        sheet_name: str = "",
        insert_type: EnhancedInsertType = EnhancedInsertType.ROW,
        row: int = 1,
        row_direction: RowDirectionType = RowDirectionType.LOWER,
        col: int = 1,
        col_direction: ColumnDirectionType = ColumnDirectionType.RIGHT,
        blank_rows: bool = False,
        insert_num: int = 1,
        insert_content: str = "",
    ):
        ExcelCore.insert_row_or_column(
            excel.obj,
            sheet_name,
            insert_type,
            row,
            row_direction,
            col,
            col_direction,
            blank_rows,
            insert_num,
            insert_content,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.get_col_type.value == '{}'".format(ColumnType.ONE_COLUMN.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("excel_row_num", types="Int"),
        ],
    )
    def get_excel_row_num(
        excel,
        sheet_name: str = "",
        get_col_type: ColumnType = ColumnType.ALL,
        col: str = "",
    ):
        """
        获取sheet的行数
        :param excel:
        :param sheet_name:
        :param get_col_type:
        :param col:
        :return:
        """
        row_num = ExcelCore.get_row_num(excel.obj, sheet_name, get_col_type, col)
        return row_num

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.get_row_type.value == '{}'".format(RowType.ONE_ROW.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("excel_col_num", types="Int"),
        ],
    )
    def get_excel_col_num(
        excel: ExcelObj,
        sheet_name: str = "",
        get_row_type: RowType = RowType.ALL,
        row: str = "",
        output_type: ColumnOutputType = ColumnOutputType.NUMBER,
    ):
        col_num = ExcelCore.get_col_num(excel.obj, sheet_name, get_row_type, row, output_type)
        return col_num

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_first_available_row", types="Int"),
        ],
    )
    def get_excel_first_available_row(excel: ExcelObj, sheet_name: str = ""):
        first_available_row = ExcelCore.get_first_available_row(excel.obj, sheet_name)
        return first_available_row

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_first_available_col", types="Any"),
        ],
    )
    def get_excel_first_available_col(
        excel: ExcelObj,
        sheet_name: str = "",
        output_type: ColumnOutputType = ColumnOutputType.LETTER,
    ):
        first_available_col = ExcelCore.get_first_available_column(excel.obj, sheet_name, output_type)
        # 如果 output_type 是 LETTER 且返回值是数字，则转换为字母列号
        if output_type == ColumnOutputType.LETTER and isinstance(first_available_col, int):
            # 将数字列号转换为字母列号 (1->A, 2->B, ..., 26->Z, 27->AA, ...)
            col_num = first_available_col
            letter = ""
            while col_num > 0:
                col_num -= 1  # 调整为0-based索引
                letter = chr(ord("A") + col_num % 26) + letter
                col_num //= 26
            first_available_col = letter

        return first_available_col

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.ROW.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.ROW.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.COLUMN.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.COLUMN.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("key", types="Str"),
            atomicMg.param("value", types="Any"),
        ],
    )
    # TODO 暂时以返回所有迭代的列表实现，后续考虑返回迭代器
    def loop_excel_content(
        excel,
        sheet_name: str = "",
        select_type: SearchRangeType = SearchRangeType.ROW,
        start_row: str = "1",
        end_row: str = "-1",
        start_col: str = "A",
        end_col: str = "-1",
        real_text: bool = False,
        cell_strip: bool = False,
    ):
        """
        循环Excel内容
        :param excel:
        :param sheet_name:
        :param select_type:1:循环行，2:循环列 3: 循环区域 4: 循环已使用
        :param start_row: 行
        :param end_row: 行
        :param start_col: 列
        :param end_col: 列
        :param real_text  是否返回所见内容
        :param cell_strip  是否去除前后空格以及换行符
        """
        loop_excel_list = ExcelCore.loop_content(
            excel.obj,
            sheet_name,
            select_type,
            start_row,
            end_row,
            start_col,
            end_col,
            real_text,
            cell_strip,
        )
        return loop_excel_list

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_cell_color", types="Str"),
        ],
    )
    def excel_get_cell_color(excel: ExcelObj, coordinate: str, sheet_name: str = ""):
        get_cell_color = ExcelCore.get_cell_color(excel.obj, coordinate, sheet_name)
        return get_cell_color

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "merge_cell_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.merge_cell_range.show",
                        expression="return $this.job_type.value == '{}'".format(MergeOrSplitType.MERGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "split_cell_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.split_cell_range.show",
                        expression="return $this.job_type.value == '{}'".format(MergeOrSplitType.SPLIT.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def merge_split_excel_cell(
        excel: ExcelObj,
        sheet_name: str,
        job_type: MergeOrSplitType = MergeOrSplitType.MERGE,
        merge_cell_range: str = "A1:B2",
        split_cell_range: str = "A1:B2",
    ):
        ExcelCore.merge_split(excel.obj, sheet_name, merge_cell_range, split_cell_range, job_type)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "relative_sheet_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.relative_sheet_name.show",
                        expression="return $this.insert_type.value == '{}' || $this.insert_type.value == '{}'".format(
                            SheetInsertType.BEFORE.value, SheetInsertType.AFTER.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def add_excel_worksheet(
        excel: ExcelObj,
        sheet_name: str,
        insert_type: SheetInsertType = SheetInsertType.FIRST,
        relative_sheet_name: str = "",
    ):
        SheetCore.create_worksheet(excel.obj, sheet_name, insert_type, relative_sheet_name)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "move_to_sheet",
                dynamics=[
                    DynamicsItem(
                        key="$this.move_to_sheet.show",
                        expression="return ['{}', '{}'].includes($this.move_type.value)".format(
                            MoveSheetType.MOVE_AFTER.value,
                            MoveSheetType.MOVE_BEFORE.value,
                        ),
                    )
                ],
            )
        ],
        outputList=[],
    )
    def move_excel_worksheet(
        excel: ExcelObj,
        move_type: MoveSheetType = MoveSheetType.MOVE_AFTER,
        move_sheet: str = "",
        move_to_sheet: str = "",
    ):
        SheetCore.move_worksheet(excel.obj, move_sheet, move_to_sheet, move_type)

    @staticmethod
    @atomicMg.atomic("Excel", inputList=[], outputList=[])
    def delete_excel_worksheet(excel: ExcelObj, del_sheet_name: str):
        SheetCore.delete_worksheet(excel.obj, del_sheet_name)

    @staticmethod
    @atomicMg.atomic("Excel", inputList=[], outputList=[])
    def rename_excel_worksheet(excel: ExcelObj, source_sheet_name: str, new_sheet_name: str):
        SheetCore.rename_worksheet(excel.obj, source_sheet_name, new_sheet_name)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "other_excel_obj",
                dynamics=[
                    DynamicsItem(
                        key="$this.other_excel_obj.show",
                        expression="return $this.copy_type.value == '{}'".format(CopySheetType.OTHER_WORKBOOK.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def copy_excel_worksheet(
        excel: ExcelObj,
        source_sheet_name: str,
        new_sheet_name: str,
        location: CopySheetLocationType = CopySheetLocationType.LAST,
        copy_type: CopySheetType = CopySheetType.CURRENT_WORKBOOK,
        other_excel_obj: ExcelObj = "",
        is_cover: bool = False,
    ):
        SheetCore.copy_worksheet(
            excel.obj,
            source_sheet_name,
            new_sheet_name,
            location,
            copy_type,
            other_excel_obj,
            is_cover,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[],
        outputList=[
            atomicMg.param("sheet_names", types="Str"),
        ],
    )
    def get_excel_worksheet_names(excel: ExcelObj, sheet_range: SheetRangeType = SheetRangeType.ACTIVATED):
        sheet_names = ExcelCore.get_worksheet_names(excel.obj, sheet_range)
        return sheet_names

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "sheet_name",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.sheet_name.show",
                        expression="return $this.lookup_range_excel.value == '{}'".format(SearchSheetType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "replace_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.replace_str.show",
                        expression="return $this.replace_flag.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("search_excel_result", types="Dict")],
    )
    def search_and_replace_excel_content(
        excel: ExcelObj,
        find_str: str,
        replace_flag: bool = False,
        replace_str: str = "",
        lookup_range_excel: SearchSheetType = SearchSheetType.ALL,
        sheet_name: str = "",
        search_range: SearchRangeType = SearchRangeType.ALL,
        row: str = "",
        col: str = "",
        start_row: str = "",
        end_row: str = "",
        start_col: str = "",
        end_col: str = "",
        exact_match: bool = False,
        case_flag: bool = False,
        match_range: MatchCountType = MatchCountType.ALL,
        output_type: SearchResultType = SearchResultType.CELL,
    ):
        """
        查找字符串在excel的位置。并提供替换能力
        :param excel: excel对象
        :param find_str: 查找的字段
        :param replace_flag: 是否替换 1-是、0-否，默认值：0-否
        :param replace_str: 要替换的字符串，默认值：''
        :param lookup_range_excel: 查找范围（文件中）全局：1 单个sheet： 0
        :param sheet_name:
        :param search_range: 查找范围（sheet中） 0-已编辑区域、1-行、2-列、3-指定区域，默认值：0-已编辑区域
        :param row: 行号，默认值：''
        :param col: 列号，默认值：''
        :param start_row: 起始行号，默认值：''
        :param end_row: 结束行号，默认值：''
        :param start_col: 起始列号，默认值：''
        :param end_col: 结束列号，默认值：''
        :param exact_match: 是否精确匹配 1-是、0-否，默认值：0-否
        :param match_range: 0-所有项、1-第一个，默认值：0-所有项
        :param case_flag: 是否区分大小写 1-是、0-否，默认值：0-否
        :param output_type: 0-所在列名，行号、1-所在单元格，默认值：0-所在列名
        :return:
        """
        if isinstance(find_str, complex):
            find_str = str(find_str)
        search_excel_result = ExcelCore.search(
            excel.obj,
            find_str,
            replace_flag,
            replace_str,
            lookup_range_excel,
            sheet_name,
            search_range,
            row,
            col,
            start_row,
            end_row,
            start_col,
            end_col,
            exact_match,
            match_range,
            case_flag,
            output_type,
        )
        return search_excel_result

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "pic_height",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_height.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.NUMBER.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_width",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_width.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.NUMBER.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_scale",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_scale.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.SCALE.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[],
    )
    def insert_pic(
        excel: ExcelObj,
        sheet_name: str,
        insert_pos: str,
        pic_path: str,
        pic_size_type: ImageSizeType = ImageSizeType.AUTO,
        pic_height: int = 300,
        pic_width: int = 400,
        pic_scale: float = 1.0,
    ):
        ExcelCore.insert_pic(
            excel.obj,
            sheet_name,
            insert_pos,
            pic_path,
            pic_size_type,
            pic_height,
            pic_width,
            pic_scale,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_formula(
        excel: ExcelObj,
        sheet_name: str = "",
        insert_direction: InsertFormulaDirectionType = InsertFormulaDirectionType.DOWN,
        col: str = "",
        start_row: str = "1",
        end_row: str = "-1",
        row: str = "",
        start_col: str = "A",
        end_col: str = "-1",
        formula: str = "",
    ):
        """
        插入公式
        insert_direction: 插入方向 0向下1向右，默认0向下
        """
        ExcelCore.insert_formula(
            excel.obj,
            sheet_name,
            insert_direction,
            col,
            start_row,
            end_row,
            row,
            start_col,
            end_col,
            formula,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.POSITION.value),
                    )
                ],
            ),
            atomicMg.param(
                "find_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.find_str.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "sheet_name",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.sheet_name.show",
                        expression="return $this.comment_range.value == '{}' || $this.comment_type.value == '{}'".format(
                            SearchSheetType.ONE.value, CreateCommentType.POSITION.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "comment_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_range.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "comment_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_all.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def create_excel_comment(
        excel: ExcelObj,
        comment_type: CreateCommentType = CreateCommentType.POSITION,
        comment: str = "",
        sheet_name: str = "",
        cell_position: str = "",
        comment_range: SearchSheetType = SearchSheetType.ONE,
        find_str: str = "",
        comment_all: bool = False,
    ):
        """
        新建批注。
        :param excel: excel对象
        :param comment: 批注内容
        :param cell_position: 批注单元格位置
        :param sheet_name: 工作表名称
        :param comment_type: 批注方式 "0"：指定位置批注  "1"：指定内容批注
        :param find_str: 待批注内容
        :param comment_range: 批注范围 "0":指定工作表  "1"：工作簿
        :param comment_all: 是否批注所有内容
        """
        ExcelCore.create_comment(
            excel.obj,
            comment,
            sheet_name,
            cell_position,
            comment_type,
            comment_range,
            find_str,
            comment_all,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.delete_all.value == false",
                    )
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[],
    )
    def delete_excel_comment(
        excel: ExcelObj,
        delete_all: bool = False,
        sheet_name: str = "",
        cell_position: str = "",
    ):
        """
        删除excel中的批注。
        :param excel: excel对象
        :param cell_position: 单元格位置
        :param sheet_name:
        :param delete_all:
        """
        ExcelCore.delete_comment(excel.obj, cell_position, sheet_name, delete_all)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_text_to_number(
        excel_obj: ExcelObj,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        """
        Excel 文本转数值格式
        :param excel_obj: excel对象
        :param sheet_name: 工作表名称
        :param select_type: 0单元格, 1整行/多行, 2整列/多列 3.指定区域 4.已使用区域
        :param cell_position: 单元格位置
        :param row: 行号
        :param col: 列号
        :param range_location: 区域位置
        """
        ExcelCore.text_to_number(
            excel_obj.obj,
            sheet_name,
            select_type,
            cell_position,
            row,
            col,
            range_location,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_number_to_text(
        excel_obj: ExcelObj,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        """
        Excel 数值转文本格式
        :param excel_obj: excel对象
        :param sheet_name: 工作表名称
        :param cell_position: 单元格位置
        :param row: 行号
        :param col: 列号
        :param range_location: 区域位置
        :param select_type: 0单元格, 1整行/多行, 2整列/多列 3.指定区域 4.已使用区域
        """
        ExcelCore.number_to_text(
            excel_obj.obj,
            sheet_name,
            select_type,
            cell_position,
            row,
            col,
            range_location,
        )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "width",
                dynamics=[
                    DynamicsItem(
                        key="$this.width.show",
                        expression="return $this.set_type.value == '{}'".format(SetType.VALUE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_set_col_width(
        excel_obj: ExcelObj,
        sheet_name: str,
        set_type: SetType = SetType.AUTO,
        col: str = "",
        width: str = "",
    ):
        """
        设置指定列宽。
        :param excel_obj:
        :param sheet_name:
        :param set_type:设置方式 指定列宽,自动调整
        :param col: 指定列号
        :param width:指定列宽(0-255)
        """
        if width == "" and set_type == SetType.VALUE:
            try:
                width = float(width)
                assert width > 0
                assert width <= 255
            except:
                raise ValueError("输入列宽有误，请检查！")
        ExcelCore.set_col_width(excel_obj.obj, sheet_name, set_type, col, width)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "height",
                dynamics=[
                    DynamicsItem(
                        key="$this.height.show",
                        expression="return $this.set_type.value == '{}'".format(SetType.VALUE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_set_row_height(
        excel_obj: ExcelObj,
        sheet_name: str,
        set_type: SetType = SetType.AUTO,
        row: str = "",
        height: str = "",
    ):
        """
        设置指定行高。
        :param excel_obj:
        :param sheet_name:
        :param set_type:设置方式 指定列宽,自动调整
        :param row: 指定行号
        :param height:指定行高(0-409.5)
        """
        if height == "" and set_type == SetType.VALUE:
            try:
                height = float(height)
                assert height > 0
                assert height <= 409.5
            except:
                raise ValueError("输入行高有误，请检查！")
        ExcelCore.set_row_height(excel_obj.obj, sheet_name, set_type, row, height)

    @staticmethod
    def filter_col_logic_excel(
        excel: ExcelObj,
        sheet_name: str,
        logic_text: dict,
        out_column: str = "",
        show_column_name: bool = True,
        del_filtered_rows: bool = False,
    ):
        ExcelCore.filter_col_logic(
            excel.obj,
            sheet_name,
            logic_text,
            out_column,
            show_column_name,
            del_filtered_rows,
        )

    @staticmethod
    def create_excel_pivot_table(
        excel: ExcelObj,
        source_sheet: str,
        source_range: str,
        pivot_sheet: str,
        pivot_start_cell: str,
        pivot_table_name: str,
        rows_fields: list,
        columns_fields: list,
        values_fields: list,
        filter_fields: list,
    ):
        new_excel = ExcelCore.create_pivot_table(
            excel.obj,
            source_sheet,
            source_range,
            pivot_sheet,
            pivot_start_cell,
            pivot_table_name,
            rows_fields,
            columns_fields,
            values_fields,
            filter_fields,
        )
        return new_excel

    @staticmethod
    def excel_wildcard_search(
        excel: ExcelObj,
        pattern,
        lookup_column_or_row,
        return_column_or_row,
        sheet_name,
        search_range="0",
        lookup_range_begin=0,
        lookup_range_end=0,
        case_sensitive=False,
    ):
        result = ExcelCore.wildcard_search(
            excel.obj,
            pattern,
            lookup_column_or_row,
            return_column_or_row,
            sheet_name,
            search_range,
            lookup_range_begin,
            lookup_range_end,
            case_sensitive,
        )
        return result

    @staticmethod
    def excel_interval_search(
        excel: ExcelObj,
        interval_begin,
        interval_end,
        lookup_column_or_row,
        return_column_or_row,
        sheet_name,
        search_range: str = "0",
        lookup_range_begin: int = 0,
        lookup_range_end: int = 0,
        default="Not Found",
    ):
        result = ExcelCore.interval_search(
            excel.obj,
            interval_begin,
            interval_end,
            lookup_column_or_row,
            return_column_or_row,
            sheet_name,
            search_range,
            lookup_range_begin,
            lookup_range_end,
            default,
        )
        return result

    @staticmethod
    def excel_xlookup(
        excel: ExcelObj,
        lookup_value,
        lookup_column_or_row,
        return_column_or_row,
        sheet_name,
        search_range: str = "0",
        lookup_range_begin: int = 0,
        lookup_range_end: int = 0,
        lookup_value2: str = "",
        lookup_column_or_row2: str = "",
        default="Not Found",
    ):
        result = ExcelCore.xlookup(
            excel.obj,
            lookup_value,
            lookup_column_or_row,
            return_column_or_row,
            sheet_name,
            search_range,
            lookup_range_begin,
            lookup_range_end,
            lookup_value2,
            lookup_column_or_row2,
            default,
        )
        return result
