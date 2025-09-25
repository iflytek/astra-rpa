import ast
import os
import re
import subprocess
import time
import traceback
import winreg
from typing import Tuple

import numpy as np
import win32clipboard as cv
import win32com.client
from win32api import RGB

excel_constants = win32com.client.constants

from rpaatomic.logger import logger
from rpaexcel import (
    ApplicationType,
    ClearType,
    CloseRangeType,
    ColumnDirectionType,
    ColumnOutputType,
    ColumnType,
    CopySheetLocationType,
    CopySheetType,
    CreateCommentType,
    DeleteCellDirection,
    EditRangeType,
    EnhancedInsertType,
    FileExistenceType,
    FontNameType,
    FontType,
    HorizontalAlign,
    ImageSizeType,
    InsertFormulaDirectionType,
    MatchCountType,
    MergeOrSplitType,
    MoveSheetType,
    NumberFormatType,
    PasteType,
    ReadRangeType,
    RowDirectionType,
    RowType,
    SaveType,
    SearchRangeType,
    SearchResultType,
    SearchSheetType,
    SetType,
    SheetRangeType,
    VerticalAlign,
)
from rpaexcel.core import IExcelCore
from rpaexcel.error import *


class ExcelCore(IExcelCore):
    excel_obj = None

    @staticmethod
    def _create_app(params: str):
        try:
            excel_obj = win32com.client.gencache.EnsureDispatch(params)
            # excel_obj = win32com.client.Dispatch(params)
            return excel_obj
        except Exception as err:
            try:
                excel_obj = win32com.client.Dispatch(params)
                return excel_obj
            except Exception as err:
                logger.debug(f"创建Excel对象失败：{params}")

    @staticmethod
    def get_default_excel_app():
        try:
            # 打开HKEY_CLASSES_ROOT\Excel.Sheet.12\shell\open\command键
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Excel.Sheet.12\shell\open\command")
            # 获取默认值
            default_value, _ = winreg.QueryValueEx(key, None)
            winreg.CloseKey(key)

            # 检查默认值中是否包含"wps"或"excel"
            if "et.exe" in default_value.lower():
                return ApplicationType.WPS
            elif "excel.exe" in default_value.lower():
                return ApplicationType.EXCEL
        except FileNotFoundError:
            # 未找到注册表信息，默认使用Excel
            return ApplicationType.EXCEL

    @classmethod
    def init_excel_app(cls, default_application: ApplicationType = ApplicationType.DEFAULT):
        # excel_flag, wps_flag = cls.excel_is_exists()
        if default_application == ApplicationType.DEFAULT:
            default_application = cls.get_default_excel_app()
            if default_application == ApplicationType.WPS:
                keys = ["Ket.Application", "et.Application", "Excel.Application"]
            elif default_application == ApplicationType.EXCEL:
                keys = ["Excel.Application", "Ket.Application", "et.Application"]
        elif default_application == ApplicationType.WPS:
            keys = ["Ket.Application", "et.Application"]
        elif default_application == ApplicationType.EXCEL:
            keys = ["Excel.Application"]

        for key in keys:
            try:
                cls.excel_obj = cls._create_app(key)
                if cls.excel_obj:
                    return cls.excel_obj
            except:
                pass
            continue
        raise Exception("未检测到wps和office注册表信息！")

    @staticmethod
    def get_worksheet_names(excel: object, sheet_range: SheetRangeType = SheetRangeType.ACTIVATED):
        """
        sheet_range: "0":当前sheet页名称; "1":所有sheet页名称
        return:返回所有sheet名
        """
        try:
            if sheet_range == SheetRangeType.ALL:
                sheet_names = [sheet.Name for sheet in excel.Sheets]
            else:
                sheet_names = excel.ActiveSheet.Name
            return sheet_names
        except Exception as err:
            raise err

    @classmethod
    def create(
        cls,
        file_path: str = "",
        file_name: str = "",
        default_application: ApplicationType = ApplicationType.EXCEL,
        visible_flag: bool = True,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        password: str = "",
    ) -> Tuple[object, str]:
        """
        Excel - 文档操作 - 创建
        """
        cls.init_excel_app(default_application)
        cls.excel_obj.Visible = visible_flag
        new_file_path = os.path.join(file_path, file_name)
        new_file_path = cls.handle_existence(new_file_path, exist_handle_type)
        workbook = cls.excel_obj.Workbooks.Add()
        cls.excel_obj.DisplayAlerts = False
        if new_file_path:
            try:
                workbook.SaveAs(
                    Filename=new_file_path,
                    ReadOnlyRecommended=False,
                    ConflictResolution=2,
                    Password=password,
                )
            except:
                raise BaseException(EXCEL_UNAVAILABLE_ERROR_FORMAT.format(new_file_path), "")
        cls.excel_obj.DisplayAlerts = True
        cls.excel_obj.ScreenUpdating = True

        # 新增逻辑：不可见时释放资源
        if not visible_flag:
            workbook.Close(SaveChanges=False)
            cls.excel_obj.Quit()

        return workbook, new_file_path

    @staticmethod
    def _excel_save(excel, file_path, file_name, save_type, exist_handle_type):
        if save_type == SaveType.SAVE_AS and file_path:
            file_suffix = "." + excel.Name.split(".")[-1]
            if not file_name:
                file_name = excel.Name.split(".")[0]
            dst_file = os.path.join(file_path, file_name + file_suffix)
            new_file_path = ExcelCore.handle_existence(dst_file, exist_handle_type)
            excel.SaveAs(Filename=new_file_path)
        elif save_type == SaveType.SAVE:
            excel.Save()
        return

    @classmethod
    def open(
        cls,
        file_path: str = "",
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = True,
        password: str = "",
        update_links: bool = True,
    ) -> object:
        """
        打开Excel文件
        :param file_path: Excel文件路径
        :param default_application: 默认打开的应用
        :param visible_flag: 是否可见
        :param password: 打开文件所需密码
        :param update_links: 是否更新依赖外部数据
        :return: Excel对象-
        """
        # 尝试打开Excel文件
        if cls.excel_obj is None:
            cls.init_excel_app(default_application)
            cls.excel_obj.Visible = visible_flag
        cls.excel_obj.ScreenUpdating = True
        cls.excel_obj.DisplayAlerts = False
        if file_path:
            excel = cls.excel_obj.Workbooks.Open(
                Filename=file_path,
                UpdateLinks=update_links,
                Password=password,
                ReadOnly=False,
                Format=None,
            )
        else:
            raise LookupError("没有输入路径，请检查输入的Excel路径是否正确!")
        cls.excel_obj.ScreenUpdating = True
        cls.excel_obj.DisplayAlerts = True
        return excel

    @staticmethod
    def _get_excel_obj(xl, file_name):
        work_books_count = xl.Workbooks.Count
        if work_books_count == 0:
            raise LookupError("不存在已打开的excel文件:{0}".format(file_name))
        else:
            for i in range(1, work_books_count + 1):
                excel_obj = xl.Workbooks(i)
                try:
                    excel_obj.Activate()
                except Exception as e:
                    raise BaseException(
                        EXCEL_UNAVAILABLE_ERROR_FORMAT.format(file_name),
                        "检查手动占用了Excel文件",
                    )
                name = excel_obj.Name
                if name.find(file_name) >= 0:
                    return excel_obj
            return None

    @staticmethod
    def _get_ws_obj(excel, sheet_name: str = ""):
        """
        获取工作表对象。
        :param sheet_name: sheet
        :return: ws_obj
        """
        sheet_names = [sheet.Name for sheet in excel.Sheets]
        try:
            sheet_name = int(sheet_name)
            if str(sheet_name) in sheet_names:
                return excel.Worksheets(sheet_name)
            elif sheet_name < 1 or sheet_name > len(sheet_names):
                raise ValueError("输入的sheet名称不存在")
            else:
                return excel.Worksheets(excel.Sheets(sheet_name).Name)
        except ValueError:
            if sheet_name == "":
                return excel.Worksheets(excel.Sheets(1).Name)
            elif sheet_name not in sheet_names:
                raise ValueError("输入的sheet名称不存在")
        return excel.Worksheets(sheet_name)

    @classmethod
    def get_exist_excel(cls, file_name):
        """
        连接到已经打开的excel
        """
        excel_obj_list = []
        excel_flag, wps_flag = cls.excel_is_exists()
        if not excel_flag and not wps_flag:
            raise Exception("未检测到wps或office打开！")
        if wps_flag:
            keys = ["Ket.Application", "et.Application"]
            for key in keys:
                try:
                    xl = win32com.client.gencache.EnsureDispatch(key)
                    break
                except Exception as e:
                    raise Exception("dispatch wps时报错了：{}".format(e))
            else:
                raise LookupError("启动wps的application失败")
            excel_obj = cls._get_excel_obj(xl, file_name)
            if excel_obj is not None:
                excel_obj_list.append(excel_obj)
        if excel_flag:
            xl = win32com.client.gencache.EnsureDispatch("Excel.Application")
            excel_obj = cls._get_excel_obj(xl, file_name)
            if excel_obj is not None:
                excel_obj_list.append(excel_obj)
        if len(excel_obj_list) == 1:
            return excel_obj_list[0]
        elif len(excel_obj_list) == 2:
            raise Exception("检测到对象：{}在WPS/Office中打开,需关闭其中一个".format(file_name))
        else:
            raise Exception("不存在已打开的Excel文件:{0}".format(file_name))

    @classmethod
    def save(
        cls,
        excel: object,
        file_path: str = "",
        file_name: str = "",
        save_type=SaveType.SAVE,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        close_flag: bool = False,
    ) -> object:
        """Word - 文档操作 - 保存"""
        cls._excel_save(excel, file_path, file_name, save_type, exist_handle_type)
        if close_flag:
            excel.Close(SaveChanges=0)

    @classmethod
    def close(
        cls,
        excel: object = None,
        close_range_flag: CloseRangeType = CloseRangeType.ONE,
        save_type=SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        pkill_flag: bool = False,
    ):
        cls._excel_save(excel, file_path, file_name, save_type, exist_handle_type)
        if close_range_flag == CloseRangeType.ALL:
            if pkill_flag:
                try:
                    cls.excel_obj.Quit()
                    os.system("taskkill /f /im et.EXE")
                    os.system("taskkill /f /im EXCEL.EXE")
                except Exception as e:
                    cls.excel_obj.Quit()
            else:
                cls.excel_obj.Quit()
            cls.excel_obj = None
        else:
            # cls._excel_save(excel, file_path, file_name, save_type, exist_handle_type)
            try:
                excel.Close(SaveChanges=0)
            except Exception as e:
                raise e

    @classmethod
    def _close_process(cls):
        if cls.excel_obj.Path.lower().find("et") >= 0:
            proc = subprocess.Popen(
                ["TaskKill", "/F", "/t", "/im", "et.exe"],
                bufsize=-1,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.communicate(timeout=10)
            proc.kill()
        else:
            proc = subprocess.Popen(
                ["TaskKill", "/F", "/t", "/im", "EXCEL.EXE"],
                bufsize=-1,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.communicate(timeout=10)
            proc.kill()

    @classmethod
    def read(
        cls,
        excel: object,
        sheet_name: str = "",
        start_col: str = "",
        end_col: str = "",
        read_range: ReadRangeType = ReadRangeType.CELL,
        cell: str = "",
        row: int = 1,
        column: str = "",
        start_row: int = 1,
        end_row: int = 1,
        read_display: bool = True,
        trim_spaces: bool = False,
        replace_none: bool = True,
    ) -> object:
        """
        读取Excel内容
        :param excel: Excel对象
        :param sheet_name: 工作表名称
        :param read_range: 读取的范围（如“A1:C3”）
        :param cell: 单元格位置（如“A1”）
        :param row: 行号
        :param column: 列号
        :param start_col
        :param end_col
        :param start_row
        :param end_row
        :param read_display: 是否读取单元格显示的内容
        :param trim_spaces: 是否清除单元格前后空格
        :param replace_none: 是否替换None为空字符串
        :return: 返回读取的内容，字符串或列表
        """
        worksheet = IExcelCore._select_sheet(excel, sheet_name)

        # 读取内容的初始化
        content = None
        used_range = worksheet.UsedRange
        used_col = worksheet.Cells.SpecialCells(11).Column
        used_row = worksheet.Cells.SpecialCells(11).Row

        # 处理读取范围
        start_col = ExcelCore._handle_column_input(start_col, used_range.Columns.Count, True)
        end_col = ExcelCore._handle_column_input(end_col, used_range.Columns.Count, True)
        start_row = ExcelCore._handle_row_input(start_row, used_range.Rows.Count)
        end_row = ExcelCore._handle_row_input(end_row, used_range.Rows.Count)

        if read_range == ReadRangeType.CELL:
            content = worksheet.Range(cell).Text if read_display else worksheet.Range(cell).Value
        elif read_range == ReadRangeType.ROW:
            content = (
                [worksheet.Cells(row, col).Text for col in range(1, used_col + 1)]
                if read_display
                else [worksheet.Cells(row, col).Value for col in range(1, used_col + 1)]
            )
        elif read_range == ReadRangeType.COLUMN:
            content = (
                [worksheet.Cells(row, column).Text for row in range(1, used_row + 1)]
                if read_display
                else [worksheet.Cells(row, column).Value for row in range(1, used_row + 1)]
            )
        elif read_range == ReadRangeType.AREA:
            content = (
                [
                    [worksheet.Cells(row, col).Text for col in range(start_col, end_col + 1)]
                    for row in range(start_row, end_row + 1)
                ]
                if read_display
                else [
                    [worksheet.Cells(row, col).Value for col in range(start_col, end_col + 1)]
                    for row in range(start_row, end_row + 1)
                ]
            )
        elif read_range == ReadRangeType.ALL:
            content = (
                [[worksheet.Cells(row, col).Text for col in range(1, used_col + 1)] for row in range(1, used_row + 1)]
                if read_display
                else [
                    [worksheet.Cells(row, col).Value for col in range(1, used_col + 1)]
                    for row in range(1, used_row + 1)
                ]
            )

        if trim_spaces:
            if isinstance(content, str):
                content = content.strip()
            elif read_range == ReadRangeType.ROW or read_range == ReadRangeType.COLUMN:
                for n in range(len(content)):
                    if isinstance(content[n], str):
                        content[n] = content[n].strip()
            else:
                for row in content:
                    for n in range(len(row)):
                        if isinstance(row[n], str):
                            row[n] = row[n].strip()

        if replace_none:
            if isinstance(content, str):
                content = content if content is not None else ""
            elif isinstance(content, list):
                for n in range(len(content)):
                    if content[n] is None:
                        content[n] = ""
                    elif isinstance(content[n], list):
                        for m in range(len(content[n])):
                            if content[n][m] is None:
                                content[n][m] = ""
            else:
                content = content if content is not None else ""  # 如果是单个值且为 None，替换为空字符串

        return content

    @classmethod
    def edit(
        cls,
        excel: object,
        start_col: str = "",
        start_row: str = "",
        sheet_name: str = "",
        edit_range: EditRangeType = EditRangeType.ROW,
        value: list = [],
    ):
        """
        编辑Excel文件中的单元格
        :param sheet_name: 要编辑的工作表名称
        :param excel
        :param start_col
        :param edit_range
        :param start_row
        :param value: 要写入的值
        :return: 编辑后的Excel对象
        """
        worksheet = cls._select_sheet(excel, sheet_name)

        # 处理为数字格式
        used_range = worksheet.UsedRange
        start_col = cls._handle_column_input(start_col, used_range.Columns.Count, True)
        start_row = cls._handle_row_input(start_row, used_range.Rows.Count)

        if edit_range == EditRangeType.ROW:
            for n in range(len(value)):
                worksheet.Cells(start_row, start_col + n).Value = value[n]
        elif edit_range == EditRangeType.COLUMN:
            for n in range(len(value)):
                worksheet.Cells(start_row + n, start_col).Value = value[n]
        elif edit_range == EditRangeType.AREA:
            for row in value:
                for n in range(len(row)):
                    worksheet.Cells(start_row, start_col + n).Value = row[n]
                start_row += 1
        elif edit_range == EditRangeType.CELL:
            worksheet.Cells(start_row, start_col).Value = value[0]

    @classmethod
    def cell_type(
        cls,
        excel: object,
        cell_position: str = "",
        range_position: str = "",
        col_width: str = "",
        col: str = "",
        row: str = "",
        bg_color: str = "",
        font_color: str = "",
        font_type: FontType = FontType.NORMAL,
        sheet_name: str = "",
        font_name: FontNameType = FontNameType.SONGTI.value,
        font_size: int = 11,
        number_format: NumberFormatType = NumberFormatType.GENERAL,
        number_format_other: str = "",
        design_type: ReadRangeType = ReadRangeType.CELL,
        horizontal_align: HorizontalAlign = HorizontalAlign.DEFAULT,
        vertical_align: VerticalAlign = VerticalAlign.MIDDLE,
        wrap_text: bool = True,
        auto_row_height: bool = False,
        auto_column_width: bool = False,
    ):
        """
        设置单元格格式.
        :param excel:
        :param cell_position:
        :param col_width:
        :param range_position:
        :param bg_color:
        :param font_color:
        :param font_type:
        :param sheet_name:
        :param font_name:
        :param font_size:
        :param numberformat 数字格式
        :param numberformat_other 其他数字格式
        :param design_type: 0单元格, 1整行/多行, 2整列/多列 3.指定区域 4.已使用区域
        :param horizontal_align: 0默认常规、1左对齐、2水平居中、3右对齐、4填充、5两端对齐、6跨列居中、7分散对齐
        :param vertical_align: 0-靠上、1-居中、2-靠下、3-两端对齐、4-分散对齐
        :param wrap_text: 0否 1是 默认1
        :param auto_row_height: 0否 1是 默认0
        :param auto_column_width: 0否 1是 默认0
        :return:
        """
        bg_color = cls._check_color(bg_color)
        font_color = cls._check_color(font_color)

        if not sheet_name:
            sheet_name = excel.Sheets(1).Name
        ws = cls._get_ws_obj(excel, sheet_name)

        cell_positions = []
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        data_range = ws.UsedRange
        if design_type == ReadRangeType.CELL:
            if cell_position == "":
                raise ValueError("操作区域不能为空")
            cell_positions.append(cell_position)

        elif design_type == ReadRangeType.ROW:  # 行
            if row == "":
                raise ValueError("操作区域不能为空")
            col = cls._column_number_to_letter(used_col)
            if type(row) is int:
                cell_positions.append("A{}:{}{}".format(row, col, row))
            else:
                row = row.replace("，", ",")
                if row.find(":") != -1:
                    row = row.split(":")
                    for index in range(len(row)):
                        row[index] = cls._handle_row_input(row[index], used_row)
                    cell_positions.append("A{}:{}{}".format(row[0], col, row[1]))
                elif row.find(",") != -1:
                    row = row.split(",")
                    for index in range(len(row)):
                        row[index] = cls._handle_row_input(row[index], used_row)
                        cell_positions.append("A{}:{}{}".format(row[index], col, row[index]))
                else:
                    row = cls._handle_row_input(row, used_row)
                    cell_positions.append("A{}:{}{}".format(row, col, row))

        elif design_type == ReadRangeType.COLUMN:  # 列
            if col == "":
                raise ValueError("操作区域不能为空")
            used_row = ws.Cells.SpecialCells(11).Row
            if type(col) is int:
                cell_position = "{}1:{}{}".format(col, col, used_row)
                cell_positions.append(cell_position)
            else:
                col = col.replace("，", ",")
                if col.find(":") != -1:
                    col = col.split(":")
                    for index in range(len(col)):
                        col[index] = cls._handle_column_input(col[index], used_col)
                    cell_positions.append("{}1:{}{}".format(col[0], col[1], used_row))
                elif col.find(",") != -1:
                    col = col.split(",")
                    for index in range(len(col)):
                        col[index] = cls._handle_column_input(col[index], used_col)
                        cell_positions.append("{}1:{}{}".format(col[index], col[index], used_row))
                else:
                    col = cls._handle_column_input(col, used_col)
                    cell_position = "{}1:{}{}".format(col, col, used_row)
                    cell_positions.append(cell_position)

        elif design_type == ReadRangeType.AREA:  # 指定区域
            data_range_handle = cls._handle_used_range(range_position)
            cell_position = "{}{}:{}{}".format(
                data_range_handle[0],
                data_range_handle[1],
                data_range_handle[2],
                data_range_handle[3],
            )
            cell_positions.append(cell_position)

        elif design_type == ReadRangeType.ALL:  # 已使用区域
            data_range_handle = cls._handle_used_range(data_range.Address)
            cell_position = "{}{}:{}{}".format(
                data_range_handle[0],
                data_range_handle[1],
                data_range_handle[2],
                data_range_handle[3],
            )
            cell_positions.append(cell_position)

        for cell_position in cell_positions:
            if col_width:
                ws.Range(cell_position).ColumnWidth = col_width

            if font_color:
                ws.Range(cell_position).Font.Color = RGB(
                    font_color[0],
                    font_color[1],
                    font_color[2],
                )
            else:
                ws.Range(cell_position).Font.Color = RGB(0, 0, 0)

            if bg_color:
                bg_color = tuple(bg_color)
                ws.Range(cell_position).Interior.Color = RGB(
                    bg_color[0],
                    bg_color[1],
                    bg_color[2],
                )
            else:
                ws.Range(cell_position).Interior.ColorIndex = 0

            if font_name != FontNameType.NO_CHANGE:
                ws.Range(cell_position).Font.Name = font_name
            if font_size:
                ws.Range(cell_position).Font.Size = font_size

            if font_type == FontType.BOLD:
                ws.Range(cell_position).Font.Bold = True
            elif font_type == FontType.ITALIC:
                ws.Range(cell_position).Font.Italic = True
            elif font_type == FontType.BOLD_ITALIC:
                ws.Range(cell_position).Font.Bold = True
                ws.Range(cell_position).Font.Italic = True
            elif font_type == FontType.NORMAL:
                ws.Range(cell_position).Font.Bold = False
                ws.Range(cell_position).Font.Italic = False

            # 自动换行
            ws.Range(cell_position).WrapText = True if wrap_text is True else False
            # 对齐原则
            if horizontal_align != HorizontalAlign.NO_CHANGE:
                ws.Range(cell_position).HorizontalAlignment = cls.XlHAlign_map.get(horizontal_align.value)
            if vertical_align != VerticalAlign.NO_CHANGE:
                ws.Range(cell_position).VerticalAlignment = cls.XlVAlign_map.get(vertical_align.value)

            # 自适应列宽/行高
            if design_type == ReadRangeType.ROW and auto_row_height:
                ws.Range(cell_position).Rows.AutoFit()
            if design_type == ReadRangeType.COLUMN and auto_column_width:
                ws.Range(cell_position).Columns.AutoFit()

            if number_format != NumberFormatType.NO_CHANGE:
                if number_format == NumberFormatType.CUSTOM:
                    number_format = number_format_other
                else:
                    number_format = number_format.value
                ws.Range(cell_position).NumberFormat = number_format

    @classmethod
    def copy(
        cls,
        excel: object,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        copy_range_excel=ReadRangeType.CELL,
        sheet_name: str = "",
        range_location: str = "",
    ):
        """
        Copy 单元格对象。
        :param excel: excel 对象
        :param cell_position 单元格位置坐标
        :param row: 行
        :param col: 列
        :param range_location: 区域
        :param copy_range_excel: 0 单元格， 1 整行 2整列 3 区域
        :param sheet_name: sheet name
        :return: 字符串
        """

        ws_obj = cls._get_ws_obj(excel, sheet_name)
        if copy_range_excel == ReadRangeType.CELL:
            row, col = cls._handle_cell_input(cell_position)
            row = int(row)
            col = int(col)
            try:
                copy_obj = ws_obj.Cells(row, col).Copy()
            except ValueError as _:
                range_str = "{}{}".format(col, row)
                copy_obj = ws_obj.Range(range_str).Copy()
        elif copy_range_excel == ReadRangeType.ROW:
            used_col = ws_obj.Cells.SpecialCells(11).Column
            copy_obj = ws_obj.Range(
                ws_obj.Cells(row, 1),
                ws_obj.Cells(row, used_col),
            ).Copy()
        elif copy_range_excel == ReadRangeType.COLUMN:
            try:
                col = int(col)
            except ValueError as _:
                col = col
            used_row = ws_obj.Cells.SpecialCells(11).Row
            copy_obj = ws_obj.Range(
                ws_obj.Cells(1, col),
                ws_obj.Cells(used_row, col),
            ).Copy()
        elif copy_range_excel == ReadRangeType.AREA:
            range_location = cls.range_location_supply(range_location, ws_obj)
            copy_obj = ws_obj.Range(range_location).Copy()
        elif copy_range_excel == ReadRangeType.ALL:
            copy_obj = ws_obj.UsedRange.Copy()
        else:
            raise TypeError("错误的类型，仅支持按单元格，按行，按列。")
        # 获取剪切板的值
        try:
            # 这个先屏蔽报错，不影响执行
            data = cls.get_clipboard()
        except Exception as e:
            data = ""
        return data

    @staticmethod
    def range_location_supply(data_region, ws):
        try:
            if not re.findall("\d", data_region):
                if ":" in data_region:
                    used_row = ws.Cells.SpecialCells(11).Row
                    columns_list = data_region.split(":")
                    if len(columns_list) == 2:
                        data_region = f"{columns_list[0]}1:{columns_list[1]}{used_row}"
        except Exception:
            pass
        return data_region

    @staticmethod
    def get_clipboard():
        """
        目的：获取剪切板的内容，并且返回，以unicode-text的形式
        """
        try:
            cv.OpenClipboard()
            data = cv.GetClipboardData(cv.CF_UNICODETEXT)
            return data
        finally:
            try:
                cv.CloseClipboard()
            except:
                pass

    @classmethod
    def paste(
        cls,
        excel: object,
        start_location: str = "",
        sheet_name: str = "",
        paste_type: PasteType = PasteType.ALL,
        skip_blanks=False,
        transpose=False,
    ):
        """
        excel粘贴功能,当前前端仅支持两种paste_type
        :param excel: excel对象
        :param start_location: 粘贴的起始位置
        :param sheet_name: sheet name
        :param paste_type: 粘贴方式
        :param skip_blanks:是否将剪贴板上区域中的空白单元格粘贴到目标区域
        :param transpose:是否粘贴区域时转置行和列
        """

        paste_type_conf = {  # 粘贴方式
            "all": -4104,  # 默认全部
            "value_and_format": 12,  # 值和数字格式
            "format": -4122,  # 仅格式
            "exclude_frame": 7,  # 边框除外
            "col_width_only": 8,  # 仅列宽
            "formula_only": -4123,  # 仅公式
            "formula_and_format": 11,  # 公式和数字格式,
            "paste_value": -4163,  # 粘贴值
        }
        try:
            sheet_names = cls.get_worksheet_names(excel)
            if excel is None:
                raise ValueError("输入变量，excel对象未选择")
            if sheet_name != "" and sheet_name not in sheet_names:
                raise ValueError("输入的sheet名称不存在")
            sl = re.findall(r"[A-Z]+[0-9]+", str(start_location))
            if not len(sl):
                raise ValueError("起始位置格式错误，样例：A1")
            ws_obj = cls._get_ws_obj(excel, sheet_name)
            range_obj = ws_obj.Range(start_location)
            paste_type_value = paste_type_conf[paste_type.value]
            range_obj.PasteSpecial(
                Paste=paste_type_value,
                SkipBlanks=bool(skip_blanks),
                Transpose=bool(transpose),
            )
        except ValueError as v_err:
            raise v_err
        except Exception as err:
            raise Exception("粘贴失败，其他异常，请查看日志")
        return excel

    @classmethod
    def delete_cell(
        cls,
        excel: object,
        coordinate: str,
        row: str = "",
        col: str = "",
        delete_range_excel=ReadRangeType.CELL,
        data_region: str = "",
        sheet_name: str = "",
        direction: DeleteCellDirection = DeleteCellDirection.LOWER_MOVE_UP,
    ):
        """
        excel删除内容
        :param excel: excel对象
        :param coordinate: 单元格位置坐标
        :param row: 行号
        :param col: 列号
        :param delete_range_excel: 删除方式 0：删除单元格 1：删除整行 2：删除整列 3:区域
        :param data_region: 区域
        :param sheet_name: sheet_name
        :param direction: 合并方式 0：下方单元格上移 1：右方单元格左移
        """
        ws = cls._get_ws_obj(excel, sheet_name)
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        if delete_range_excel == ReadRangeType.CELL:
            row, col = cls._handle_cell_input(coordinate)
            content = ws.Cells(row, col)
            if direction == DeleteCellDirection.LOWER_MOVE_UP:
                content.Delete(Shift=-4162)
            elif direction == DeleteCellDirection.RIGHT_MOVE_LEFT:
                content.Delete(Shift=-4159)

        elif delete_range_excel == ReadRangeType.ROW:
            rows = cls._handle_multiple_inputs(row, used_col, used_row, True)
            rows.sort(reverse=True)
            for item in rows:
                ws.Rows(item).Delete()

        elif delete_range_excel == ReadRangeType.COLUMN:
            cols = cls._handle_multiple_inputs(col, used_col, used_row, False)
            cols.sort(reverse=True)
            for item in cols:
                ws.Columns(item).Delete()

        elif delete_range_excel == ReadRangeType.AREA:
            # data_region = cls.range_location_supply(data_region, ws)
            content = ws.Range(data_region)
            if direction == 0:
                content.Delete(Shift=-4162)
            elif direction == 1:
                content.Delete(Shift=-4159)

        elif delete_range_excel == ReadRangeType.ALL:
            ws.Cells.ClearContents()
        else:
            raise TypeError("错误的类型，仅支持按单元格，按行，按列删除。")
        return excel

    @classmethod
    def clear_content(
        cls,
        excel: object,
        sheet_name: str = "",
        cell_location: str = "",
        select_type=ReadRangeType.CELL,
        row: str = "",
        col: str = "",
        data_range: str = "",
        clear_type=ClearType.CONTENT,
    ):
        """
        清空单元格或区域内容
        excel_obj:excel对象
        sheet_name:sheet名
        range_index:单元格及范围
        select_type:0:读取单元格，1:读取整行，2:读取整列 3: 读取区域 4: 读取全部
        row:
        col:
        clear_type: 清除方式 0 清除内容 1 清除格式 2 清除全部
        """

        def range_clear(_ws_range, _clear_type):
            if _clear_type == ClearType.CONTENT:
                _ws_range.ClearContents()
            elif _clear_type == ClearType.STYLE:
                _ws_range.ClearFormats()
            elif _clear_type == ClearType.ALL:
                _ws_range.ClearFormats()
                _ws_range.Clear()

        try:
            ws = cls._get_ws_obj(excel, sheet_name)
            used_col = ws.Cells.SpecialCells(11).Column
            used_row = ws.Cells.SpecialCells(11).Row

            if select_type == ReadRangeType.CELL:
                ws_range = ws.Range(cell_location)
            elif select_type == ReadRangeType.AREA:
                ws_range = ws.Range(data_range)
            elif select_type == ReadRangeType.ALL:
                ws_range = ws.UsedRange
            elif select_type == ReadRangeType.ROW:
                rows = cls._handle_multiple_inputs(row, used_col, used_row, True)
                rows.sort(reverse=True)
                for item in row:
                    range_clear(ws.Rows(item), clear_type)
                return excel
            elif select_type == ReadRangeType.COLUMN:
                cols = cls._handle_multiple_inputs(col, used_col, used_row, False)
                cols.sort(reverse=True)
                for item in col:
                    range_clear(ws.Columns(item), clear_type)
                return excel
            range_clear(ws_range, clear_type)
            return excel
        except Exception as err:
            if "无法对合并单元格执行此操作" in str(err):
                raise ValueError("当前单元格区域存在合并单元格情况，无法清空内容，重新输入最大合并区域")
            else:
                raise err

    @classmethod
    def insert_row_or_column(
        cls,
        excel: object,
        sheet_name: str,
        insert_type: EnhancedInsertType = EnhancedInsertType.ROW,
        row: int = 1,
        row_direction: RowDirectionType = RowDirectionType.LOWER,
        col: int = 1,
        col_direction: ColumnDirectionType = ColumnDirectionType.RIGHT,
        blank_rows: bool = False,
        insert_num: int = 1,
        insert_content: str = "",
    ):
        """
        根据单元格区域插入行列,根据insert_location是单元格还是区域可批量插入多行
        excel_obj:sheet对象
        sheet_name：sheet名
        insert_type： 0-指定行号插入行、1-指定列号插入列，2-行追加输入，3-列追加输入；默認 0-插入行
        insert_num: 插入的行数或列数
        row_direction: 0-向上，1-向下，默认值：1-向下
        col_direction: 0-向左，1-向右，默认值：1-向右
        """
        # 测试用
        # insert_content = '[[1, 2, 3], ["asddd", "dasd", "123231"]]'
        # insert_type = '1'
        # row = "-2"
        # row_direction = "0"
        # col = "-2"
        # col_direction = "0"
        # insert_num = '2'
        try:
            ws_obj = cls._get_ws_obj(excel, sheet_name=sheet_name)
            used_row = ws_obj.Cells.SpecialCells(11).Row
            used_col = ws_obj.Cells.SpecialCells(11).Column

            if not blank_rows:
                if not isinstance(insert_content, list):
                    try:
                        insert_content = ast.literal_eval(insert_content)
                    except SyntaxError as e:
                        raise BaseException(INPUT_DATA_ERROR_FORMAT.format(e), "")

                if not isinstance(insert_content[0], list):
                    insert_content = [insert_content]

                insert_num = len(insert_content)

            if insert_type == EnhancedInsertType.ADD_ROWS:
                row = used_row
                row_direction = RowDirectionType.LOWER
            elif insert_type == EnhancedInsertType.ADD_COLUMNS:
                col = used_col
                col_direction = ColumnDirectionType.RIGHT

            if insert_type in [
                EnhancedInsertType.ROW,
                EnhancedInsertType.ADD_ROWS,
            ]:  # 插入行
                row = cls._handle_row_input(row, used_row)
                if row_direction == RowDirectionType.UPPER:  # 向上
                    for _ in range(insert_num):
                        range_obj = ws_obj.Range(
                            "A{}:{}{}".format(
                                str(row),
                                cls._column_number_to_letter(used_col),
                                str(row),
                            )
                        )
                        range_obj.EntireRow.Insert(Shift=-4162)
                if row_direction == RowDirectionType.LOWER:  # 向下
                    for _ in range(insert_num):
                        range_obj = ws_obj.Range(
                            "A{}:{}{}".format(
                                str(row + 1),
                                cls._column_number_to_letter(used_col),
                                str(row + 1),
                            )
                        )
                        # range_obj.EntireRow.Insert(Shift=-4121) 理论上有对应的shift数值，但是经过测试似乎不行
                        range_obj.EntireRow.Insert(Shift=-4162)
                    row = row + 1
                if not blank_rows:
                    cls.edit(excel, "", row, sheet_name, EditRangeType.AREA, insert_content)

            elif insert_type in [
                EnhancedInsertType.COLUMN,
                EnhancedInsertType.ADD_COLUMNS,
            ]:
                col = cls._handle_column_input(col, used_col, True)
                new_col = col
                for _ in range(insert_num):
                    if col_direction == ColumnDirectionType.LEFT:  # 左
                        col_letter = cls._column_number_to_letter(col)
                        range_obj = ws_obj.Range("{}1:{}{}".format(col_letter, col_letter, used_row))
                        range_obj.EntireColumn.Insert(Shift=-4159)
                    if col_direction == ColumnDirectionType.RIGHT:  # 右
                        new_col = cls._column_number_to_letter(col + 1)
                        range_obj = ws_obj.Range("{}1:{}{}".format(new_col, new_col, used_row))
                        # range_obj.EntireColumn.Insert(Shift=-4161) 理论上有对应的shift数值，但是经过测试似乎不行
                        range_obj.EntireColumn.Insert(Shift=-4159)
                row = 1
                col = new_col
                if not blank_rows:
                    max_length = max(len(sublist) for sublist in insert_content)
                    filled_list = [sublist + [""] * (max_length - len(sublist)) for sublist in insert_content]
                    # 反转列表前补空白
                    np_array = np.array(filled_list)
                    insert_content = np.transpose(np_array).tolist()
                    cls.edit(excel, col, "", sheet_name, EditRangeType.AREA, insert_content)

        except Exception as err:
            raise err

    @classmethod
    def get_first_available_row(cls, excel: object, sheet_name: str = ""):
        ws = cls._get_ws_obj(excel, sheet_name)
        used_cell = ws.Cells.SpecialCells(11).Address.replace("$", "")

        used_range = ws.Range("A1:{}".format(used_cell))
        data = used_range.Value  # 将使用区域的数据读入数组；如果表太大，可能会导致内存溢出

        rows_count = ws.Cells.SpecialCells(11).Row
        cols_count = ws.Cells.SpecialCells(11).Column

        for row in range(0, rows_count - 1):
            is_empty = True
            for col in range(0, cols_count - 1):
                if data[row][col] not in [None, ""]:
                    is_empty = False
                    break  # 找到非空单元格，退出内层循环
            if is_empty:
                return row + 1

        return rows_count + 1  # 如果所有行都为空，返回正常结果

    @classmethod
    def get_first_available_column(
        cls,
        excel: object,
        sheet_name: str = "",
        output_type: ColumnOutputType = ColumnOutputType.LETTER,
    ):
        ws = cls._get_ws_obj(excel, sheet_name)
        used_cell = ws.Cells.SpecialCells(11).Address.replace("$", "")

        used_range = ws.Range("A1:{}".format(used_cell))
        data = used_range.Value  # 将使用区域的数据读入数组；如果表太大，可能会导致内存溢出

        rows_count = ws.Cells.SpecialCells(11).Row
        cols_count = ws.Cells.SpecialCells(11).Column

        for col in range(0, cols_count - 1):
            is_empty = True
            for row in range(0, rows_count - 1):
                if data[row][col] not in [None, ""]:
                    is_empty = False
                    break  # 找到非空单元格，退出内层循环
            if is_empty:
                if output_type == ColumnOutputType.LETTER:
                    return cls._column_number_to_letter(col + 1)
                else:
                    return col + 1

        return cols_count + 1  # 如果所有行都为空，返回正常结果

    @classmethod
    def get_row_num(
        cls,
        excel,
        sheet_name: str = "",
        get_col_type: ColumnType = ColumnType.ALL,
        col: str = "",
    ):
        ws_obj = cls._get_ws_obj(excel, sheet_name)
        used_col = ws_obj.Cells.SpecialCells(11).Column
        used_row = ws_obj.Cells.SpecialCells(11).Row
        if get_col_type == ColumnType.ALL:
            return used_row
        elif get_col_type == ColumnType.ONE_COLUMN:
            col = cls._handle_column_input(col, used_col, True)
            rows = [cell.Value for cell in ws_obj.Range(ws_obj.Cells(1, col), ws_obj.Cells(used_row, col)).Cells]
            for index in range(len(rows) - 1, -1, -1):
                if rows[index] not in [None, ""]:
                    return index + 1
            return 0

    @classmethod
    def get_col_num(
        cls,
        excel,
        sheet_name: str = "",
        get_row_type: RowType = RowType.ALL,
        row: str = "",
        output_type: ColumnOutputType = ColumnOutputType.NUMBER,
    ):
        """
        read_range: 读取范围：0-整个sheet、1-指定行，默认值：0-整个sheet
        row: 行号，支持负数
        output_type:  输出列数格式：0-数字、1-字母，默认值：0-数字型
        """
        result_col = 0
        ws_obj = cls._get_ws_obj(excel, sheet_name)
        used_col = ws_obj.Cells.SpecialCells(11).Column
        used_row = ws_obj.Cells.SpecialCells(11).Row
        if get_row_type == RowType.ALL:
            result_col = used_col
        elif get_row_type == RowType.ONE_ROW:
            row = cls._handle_row_input(row, used_row)
            columns = [cell.Value for cell in ws_obj.Range(ws_obj.Cells(row, 1), ws_obj.Cells(row, used_col)).Cells]
            for index in range(len(columns) - 1, -1, -1):
                if columns[index] not in [None, ""]:
                    result_col = index + 1
                    break
        if output_type == ColumnOutputType.NUMBER:
            return result_col
        elif output_type == ColumnOutputType.LETTER:
            return cls._column_number_to_letter(result_col)

    @classmethod
    def get_cell_color(cls, excel: object, coordinate: str, sheet_name: str = ""):
        ws = cls._get_ws_obj(excel, sheet_name)
        color_num = ws.Range(coordinate).Interior.Color
        color_list = [
            int(color_num) % pow(2, 8),
            int(int(color_num) / pow(2, 8)) % pow(2, 8),
            int(int(color_num) / pow(2, 16)),
        ]
        color_str = ",".join([str(i) for i in color_list])
        return color_str

    @classmethod
    def merge_split(
        cls,
        excel: object,
        sheet_name: str,
        merge_cell_range: str = "",
        split_cell_range: str = "",
        job_type: MergeOrSplitType = MergeOrSplitType.MERGE,
    ):
        """
        拆分合并单元格
        :param excel:
        :param sheet_name:
        :param merge_cell_range:
        :param split_cell_range:
        :param job_type: merge-split
        :return:
        """
        ws_obj = cls._get_ws_obj(excel, sheet_name=sheet_name)
        excel.Application.DisplayAlerts = False
        if job_type == MergeOrSplitType.MERGE:
            range_obj = ws_obj.Range(merge_cell_range)
            range_obj.Merge()
        else:
            range_obj = ws_obj.Range(split_cell_range)
            range_obj.UnMerge()
        excel.Application.DisplayAlerts = True

    @classmethod
    def search(
        cls,
        excel,
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
        match_range: MatchCountType = MatchCountType.ALL,
        case_flag: bool = False,
        output_type: SearchResultType = SearchResultType.CELL,
    ):
        if lookup_range_excel == SearchSheetType.ALL:
            sheet_list = cls.get_worksheet_names(excel, SheetRangeType.ALL)
        else:
            sheet_list = [sheet_name]
        contents = dict()
        for name in sheet_list:
            res = cls._search_sheet(
                excel,
                find_str,
                replace_flag,
                replace_str,
                name,
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
            )
            contents[name] = cls._format_search_res(res, output_type)
        if lookup_range_excel == SearchSheetType.ONE:
            return contents[sheet_name]
        else:
            return contents

    @staticmethod
    def _format_search_res(contents, output_type):
        # output_type: 0 - 所在列名，行号、1 - 所在单元格，默认值：0 - 所在列名，行号
        for i in range(len(contents)):
            content = contents[i]
            if output_type == SearchResultType.CELL:
                value = content["col"] + content["row"]
            elif output_type == SearchResultType.COL_AND_ROW:
                value = [content["col"], content["row"]]
            contents[i] = value
        return contents

    @classmethod
    def _search_sheet(
        cls,
        excel,
        find_str,
        replace_flag,
        replace_str,
        sheet_name: str = "",
        search_range: SearchRangeType = SearchRangeType.ALL,
        row: str = "",
        col: str = "",
        start_row: str = "",
        end_row: str = "",
        start_col: str = "",
        end_col: str = "",
        exact_match: bool = False,
        match_range: MatchCountType = MatchCountType.ALL,
        case_flag: bool = False,
    ):
        """
        查找一个sheet中的字符串。
        :param excel: excel对象
        :param find_str: 查找的字段
        :param sheet_name:
        :param search_range: 查找范围（sheet中） 0-已编辑区域、1-行、2-列、3-指定区域，默认值：0-已编辑区域
        :param exact_match: 是否精确匹配 1-是、0-否，默认值：0-否
        :param match_range: 0-所有项、1-第一个，默认值：0-所有项
        :return:
        :return:
        """
        ws = cls._get_ws_obj(excel, sheet_name)
        used_row = ws.Cells.SpecialCells(11).Row
        used_col = ws.Cells.SpecialCells(11).Column
        data_range = ws.UsedRange
        cell_positions = []

        if search_range == SearchRangeType.ALL:
            data_range_handle = cls._handle_used_range(data_range.Address)
            cell_position = "{}{}:{}{}".format(
                data_range_handle[0],
                data_range_handle[1],
                data_range_handle[2],
                data_range_handle[3],
            )
            cell_positions.append(cell_position)

        elif search_range == SearchRangeType.ROW:
            rows = cls._handle_multiple_inputs(row, used_row, used_col, True)
            for extract_row in rows:
                cell_positions.append(
                    "A{}:{}{}".format(extract_row, cls._column_number_to_letter(used_col), extract_row)
                )

        elif search_range == SearchRangeType.COLUMN:
            cols = cls._handle_multiple_inputs(col, used_row, used_col, False)
            for extract_col in cols:
                cell_positions.append(
                    "{}1:{}{}".format(
                        cls._column_number_to_letter(extract_col),
                        cls._column_number_to_letter(extract_col),
                        used_row,
                    )
                )

        elif search_range == SearchRangeType.AREA:
            start_row = cls._handle_row_input(start_row, used_row)
            end_row = cls._handle_row_input(end_row, used_row)
            start_col = cls._handle_column_input(start_col, used_col)
            end_col = cls._handle_column_input(end_col, used_col)
            cell_positions.append(ws.Range("{}{}:{}{}".format(start_col, start_row, end_col, end_row)))

        positions = set()
        for cell_position in cell_positions:
            look_at = excel_constants.xlWhole if exact_match else excel_constants.xlPart
            found_cell = ws.Range(cell_position).Find(
                find_str,
                LookAt=look_at,
                LookIn=excel_constants.xlValues,
                MatchCase=1 if case_flag else 0,
            )

            if found_cell is not None:
                first_address = found_cell.Address
                logger.info(f"找到值 '{find_str}' 在单元格: {found_cell.Address}")
                positions.add(first_address)

                if replace_flag:
                    found_cell.Value = str(found_cell.Value).replace(find_str, replace_str)
                    # 这里用.Value容易报错

                if match_range == MatchCountType.ALL:
                    # 继续查找下一个匹配项
                    while True:
                        found_cell = ws.Range(cell_position).FindNext(found_cell)
                        if found_cell is None or found_cell.Address == first_address:
                            break
                        logger.info(f"找到值 '{find_str}' 在单元格: {found_cell.Address}")
                        positions.add(found_cell.Address)
                        if replace_flag:
                            found_cell.Value = str(found_cell.Value).replace(find_str, replace_str)
            else:
                logger.info(f"未找到值 '{find_str}'")

        res = list()
        for single in positions:
            position_info = dict()
            position_info["row"] = single.split("$")[2]
            position_info["col"] = single.split("$")[1]
            res.append(position_info)
        return res

    @classmethod
    def insert_pic(
        cls,
        excel,
        sheet_name: str,
        insert_pos: str,
        image_path: str,
        pic_size_type: ImageSizeType,
        pic_height: int,
        pic_width: int,
        pic_scale: float,
    ):
        """
        选取位置插入图片。
        :param excel:
        :param sheet_name:
        :param insert_pos:
        :param image_path: 图片的地址
        :param pic_size_type:
        :param pic_height:设置图片的高度
        :param pic_width: 图片的宽度
        :param pic_scale: 图片的缩放比例
        :return:
        """
        from PIL import Image

        # 获取起始位置
        ws_obj = cls._get_ws_obj(excel, sheet_name=sheet_name)

        # 插入图片到指定单元格
        cell_range = ws_obj.Range(insert_pos)  # 指定单元格

        # 插入图片
        picture = ws_obj.Pictures().Insert(image_path)

        shape = picture.ShapeRange.Item(1)
        shape.LockAspectRatio = False

        image = Image.open(image_path)
        # 获取图片的宽度和高度
        width, height = image.size

        if pic_size_type == ImageSizeType.SCALE:
            picture.Width = width * pic_scale  # 设置图片宽度
            picture.Height = height * pic_scale  # 设置图片高度
        elif pic_size_type == ImageSizeType.NUMBER:
            picture.Width = pic_width  # 设置图片宽度
            picture.Height = pic_height  # 设置图片高度
        elif pic_size_type == ImageSizeType.AUTO:
            picture.Width = cell_range.Width  # 设置图片宽度
            picture.Height = cell_range.Height  # 设置图片高度
        # 设置图片的位置和大小
        picture.Left = cell_range.Left
        picture.Top = cell_range.Top

    @classmethod
    def loop_content(
        cls,
        excel_obj,
        sheet_name: str = "",
        select_type: SearchRangeType = SearchRangeType.ROW,
        start_row: str = "",
        end_row: str = "",
        start_col: str = "",
        end_col: str = "",
        real_text: bool = False,
        cell_strip: bool = False,
    ):
        # select_type:1:循环行，2:循环列 3: 循环区域 4: 循环已使用
        ws = cls._get_ws_obj(excel_obj, sheet_name)
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        used_col_letter = cls._column_number_to_letter(used_col)

        if select_type == SearchRangeType.ROW or select_type == SearchRangeType.AREA:
            start_row = cls._handle_row_input(start_row, used_row)
            end_row = cls._handle_row_input(end_row, used_row)

        if select_type == SearchRangeType.COLUMN or select_type == select_type == SearchRangeType.AREA:
            start_col = cls._handle_column_input(start_col, used_col, False)
            end_col = cls._handle_column_input(end_col, used_col, False)

        if select_type == SearchRangeType.ROW:
            start_col = "A"
            end_col = used_col_letter
            data_region = f"{start_col}{start_row}:{end_col}{end_row}"
        elif select_type == SearchRangeType.COLUMN:
            start_row = "1"
            end_row = used_row
            data_region = f"{start_col}{start_row}:{end_col}{end_row}"
        elif select_type == SearchRangeType.AREA:
            data_region = f"{start_col}{start_row}:{end_col}{end_row}"
        elif select_type == SearchRangeType.ALL:
            start_col = "A"
            start_row = "1"
            end_col = used_col_letter
            end_row = used_row
            data_region = f"{start_col}{start_row}:{end_col}{end_row}"

        try:
            content = ws.Range(data_region).Value
            if content is None:
                return {}
        except Exception as e:
            raise Exception("请输入正确的区域信息，如A1:B2")

        if real_text:
            content = []
            for row in ws.Range(data_region).Rows:
                content.append([item.Text for item in row.Cells])

        if cell_strip:
            temp_content = []
            for row in content:
                temp_row = []
                for element in row:
                    if isinstance(element, str):
                        temp_row.append(element.strip().replace("\n", ""))
                    else:
                        temp_row.append(element)
                temp_content.append(temp_row)
            content = temp_content

        if content:
            # 修复：仅单个单元格A1有值时, 包裹[]
            if not isinstance(content, (list, tuple)):
                content = [[content]]
            if select_type == SearchRangeType.COLUMN:
                content = [list(item) for item in zip(*content)]
                headers = cls.get_column_names(
                    cls._column_letter_to_number(start_col),
                    cls._column_letter_to_number(end_col),
                )
                content = dict(zip(headers, content))
            else:
                content = [list(item) for item in content]
                row_index = [i for i in range(int(start_row), int(end_row) + 1)]
                content = dict(zip(row_index, content))
            logger.info(f"获取到的内容（最终结果）：{content}")
        return content

    @classmethod
    def insert_formula(
        cls,
        excel,
        sheet_name: str = "",
        insert_direction: InsertFormulaDirectionType = InsertFormulaDirectionType.DOWN,
        col: str = "",
        start_row: str = "1",
        end_row: str = "-1",
        row: str = "",
        start_col: str = "",
        end_col: str = "-1",
        formula: str = "",
    ):
        ws_obj = cls._get_ws_obj(excel, sheet_name)
        used_row = ws_obj.Cells.SpecialCells(11).Row
        used_col = ws_obj.Cells.SpecialCells(11).Column

        if insert_direction == InsertFormulaDirectionType.DOWN:
            col = cls._handle_column_input(col, used_col, False)
            start_row = cls._handle_row_input(start_row, used_row)
            end_row = cls._handle_row_input(end_row, used_row)
            starter = ws_obj.Range("{}{}".format(col, str(start_row)))
            starter.Value = formula
            starter.AutoFill(
                ws_obj.Range("{}{}:{}{}".format(col, str(start_row), col, str(end_row))),
                0,
            )

        if insert_direction == InsertFormulaDirectionType.RIGHT:
            start_col = cls._handle_column_input(start_col, used_col, False)
            end_col = cls._handle_column_input(end_col, used_col, False)
            row = cls._handle_row_input(row, used_row)
            starter = ws_obj.Range("{}{}".format(start_col, str(row)))
            starter.Value = formula
            starter.AutoFill(
                ws_obj.Range("{}{}:{}{}".format(start_col, str(row), end_col, str(row))),
                0,
            )

    @classmethod
    def create_comment(
        cls,
        excel: object,
        comment: str,
        sheet_name: str = "",
        cell_position: str = "",
        comment_type: CreateCommentType = CreateCommentType.POSITION,
        comment_range: SearchSheetType = SearchSheetType.ONE,
        find_str: str = "",
        comment_all: bool = False,
    ):
        if comment_type == CreateCommentType.POSITION:
            ws = cls._get_ws_obj(excel, sheet_name)
            content = ws.Range(cell_position)
            if not content.Comment:
                content.AddComment()
            content.Comment.Text(comment)
        elif comment_type == CreateCommentType.CONTENT:
            count = 0
            search_result = cls.search(
                excel,
                find_str,
                False,
                "",
                comment_range,
                sheet_name,
                SearchRangeType.ALL,
                "",
                "",
                "",
                "",
                "",
                "",
                True,
                MatchCountType.ALL,
                False,
                SearchResultType.CELL,
            )
            if isinstance(search_result, list) and comment_range == SearchSheetType.ONE:
                ws = cls._get_ws_obj(excel, sheet_name)
                for i in range(len(search_result)):
                    content = ws.Range(search_result[i])
                    if not content.Comment:
                        content.AddComment()
                    content.Comment.Text(comment)
                    count += 1
                    if count == 1 and not comment_all:
                        break
            elif isinstance(search_result, dict) and comment_range == SearchSheetType.ALL:
                for sheet_name, positions in search_result.items():
                    ws = cls._get_ws_obj(excel, sheet_name)
                    for i in range(len(positions)):
                        content = ws.Range(positions[i])
                        if not content.Comment:
                            content.AddComment()
                        content.Comment.Text(comment)
                        count += 1
                        if count == 1 and not comment_all:
                            break

    @classmethod
    def delete_comment(
        cls,
        excel,
        cell_position: str = "",
        sheet_name: str = "",
        delete_all: bool = False,
    ):
        ws = cls._get_ws_obj(excel, sheet_name=sheet_name)
        if delete_all:
            if ws.Comments.Count > 0:
                for index in range(1, ws.Comments.Count + 1):
                    # 删除注意他的Item是动态的，所以每次删除第一个就可以了
                    ws.Comments.Item(1).Delete()
            else:
                raise ValueError("不存在批注")
        else:
            range_obj = ws.Range(cell_position)
            if range_obj.Comment:
                range_obj.ClearComments()
            else:
                raise ValueError("不存在批注")

    @classmethod
    def filter_col_logic(
        cls,
        excel: object,
        sheet_name: str,
        logic_text: dict,
        out_column: str = "",
        show_column_name: str = "1",
        del_filtered_rows: str = "0",
    ):
        """Excel 筛选
        out_column: 指定输出列
        show_column_name: 是否保留列名 0否1是 默认1是
        del_filtered_rows: 是否删除筛选行 0否1是 默认0否
        """
        ws = cls._get_ws_obj(excel, sheet_name)
        data_range = ws.UsedRange

        op_and = list(logic_text.keys())[0]
        for logic_one in logic_text[op_and]:
            op_and_or = list(logic_one.keys())[0]
            logic_1 = logic_one[op_and_or]
            field = cls._column_letter_to_number(list(logic_1[0].values())[0][0])
            op_1 = list(logic_1[0].keys())[0]
            condition_1 = list(logic_1[0].values())[0][1]
            criteria1 = cls.handle_op(op_1, condition_1)
            if len(logic_1) == 1:
                data_range.AutoFilter(Field=field, Criteria1=criteria1)
            elif len(logic_1) == 2:
                if op_and_or == "and":
                    operator = 1
                elif op_and_or == "or":
                    operator = 2
                else:
                    raise ValueError("筛选逻辑不支持")
                op_2 = list(logic_1[1].keys())[0]
                condition_2 = list(logic_1[1].values())[0][1]
                criteria2 = cls.handle_op(op_2, condition_2)
                data_range.AutoFilter(
                    Field=field,
                    Criteria1=criteria1,
                    Operator=operator,
                    Criteria2=criteria2,
                )
            else:
                raise ValueError("筛选逻辑不支持")

        filtered_range = ws.AutoFilter.Range.SpecialCells(12)

        filtered_data = []
        for row in filtered_range.Rows:
            row_data = [cell.Text for cell in row.Cells]
            filtered_data.append(row_data)
        if out_column == "":
            output_data = filtered_data
        else:
            output_columns = out_column.split(",") if len(out_column) > 1 else [out_column]
            output_column_indexes = [
                cls._column_letter_to_number(output_column) - 1 for output_column in output_columns
            ]
            output_data = [[row[i] for i in output_column_indexes] for row in filtered_data]
        if show_column_name == "0":
            output_data = output_data[1:]
        if del_filtered_rows == "1":
            cls.excel_app = cls.init_excel_app()
            cls.excel_app.DisplayAlerts = False
            filtered_range.Rows("2:" + str(data_range.Rows.Count)).Delete()
            cls.excel_app.DisplayAlerts = True
        return output_data

    @staticmethod
    def handle_op(op, condition):
        """处理子条件关系"""
        op_map = {
            "==": f"{condition}",
            "!=": f"<>{condition}*",
            "contains": f"*{condition}*",
            "not_contains": f"<>*{condition}*",
            "startswith": f"*{condition}",
            "not_startswith": f"<>*{condition}",
            "endswith": f"{condition}*",
            "not_endswith": f"<>{condition}*",
            "isnull": "",
            "notnull": "<>",
        }
        if op in [">", "<", ">=", "<="]:
            criteria = f"{op}{condition}"
        elif op in [
            "==",
            "!=",
            "contains",
            "not_contains",
            "startswith",
            "not_startswith",
            "endswith",
            "not_endswith",
            "isnull",
            "notnull",
        ]:
            criteria = op_map.get(op)
        else:
            raise ValueError("筛选逻辑不支持")
        return criteria

    @classmethod
    def text_to_number(
        cls,
        excel_obj: object,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        ws = cls._get_ws_obj(excel_obj, sheet_name)
        cell_positions = []
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        data_range = ws.UsedRange

        if select_type == ReadRangeType.ALL:
            data_range_handle = cls._handle_used_range(data_range.Address)
            cell_position = "{}{}:{}{}".format(
                data_range_handle[0],
                data_range_handle[1],
                data_range_handle[2],
                data_range_handle[3],
            )
            cell_positions.append(cell_position)

        elif select_type == ReadRangeType.ROW:
            rows = cls._handle_multiple_inputs(row, used_row, used_col, True)
            for extract_row in rows:
                cell_positions.append(
                    "A{}:{}{}".format(extract_row, cls._column_number_to_letter(used_col), extract_row)
                )

        elif select_type == ReadRangeType.COLUMN:
            cols = cls._handle_multiple_inputs(col, used_row, used_col, False)
            for extract_col in cols:
                cell_positions.append(
                    "{}1:{}{}".format(
                        cls._column_number_to_letter(extract_col),
                        cls._column_number_to_letter(extract_col),
                        used_row,
                    )
                )

        elif select_type == ReadRangeType.AREA:
            cell_positions.append(range_location)

        elif select_type == ReadRangeType.CELL:
            cell_positions.append(cell_position)

        empty_cell = "{}{}".format(cls._column_number_to_letter(used_col), used_row + 1)
        for cell_position in cell_positions:
            for item in ws.Range(cell_position).Cells:
                item_address = item.Address.replace("$", "")
                if ws.Range(item_address).Value in ["", None]:
                    continue
                ws.Range(item_address).NumberFormat = "G/通用格式"
                ws.Range(empty_cell).Value = "=VALUE({})".format(item_address)
                if ws.Range(empty_cell).Value != -2146826273.0:
                    item.Value = ws.Range(empty_cell).Value
        ws.Range(empty_cell).Value = None

    @classmethod
    def number_to_text(
        cls,
        excel_obj: object,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        ws = cls._get_ws_obj(excel_obj, sheet_name)
        cell_positions = []
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        data_range = ws.UsedRange

        if select_type == ReadRangeType.ALL:
            data_range_handle = cls._handle_used_range(data_range.Address)
            cell_position = "{}{}:{}{}".format(
                data_range_handle[0],
                data_range_handle[1],
                data_range_handle[2],
                data_range_handle[3],
            )
            cell_positions.append(cell_position)

        elif select_type == ReadRangeType.ROW:
            rows = cls._handle_multiple_inputs(row, used_row, used_col, True)
            for extract_row in rows:
                cell_positions.append(
                    "A{}:{}{}".format(extract_row, cls._column_number_to_letter(used_col), extract_row)
                )

        elif select_type == ReadRangeType.COLUMN:
            cols = cls._handle_multiple_inputs(col, used_row, used_col, False)
            for extract_col in cols:
                cell_positions.append(
                    "{}1:{}{}".format(
                        cls._column_number_to_letter(extract_col),
                        cls._column_number_to_letter(extract_col),
                        used_row,
                    )
                )

        elif select_type == ReadRangeType.AREA:
            cell_positions.append(range_location)

        elif select_type == ReadRangeType.CELL:
            cell_positions.append(cell_position)

        for cell_position in cell_positions:
            for item in ws.Range(cell_position).Cells:
                item_address = item.Address.replace("$", "")
                cell_value = item.Value
                if not isinstance(cell_value, str):
                    ws.Range(item_address).NumberFormat = "@"
                    ws.Range(item_address).Value = ws.Range(item_address).Text

    @classmethod
    def set_col_width(cls, excel_obj, sheet_name: str, set_type: SetType, col: str, width: float):
        ws = cls._get_ws_obj(excel_obj, sheet_name)
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        col_list = cls._handle_multiple_inputs(col, used_row, used_col, False)

        if set_type == SetType.VALUE:  # 指定列宽
            for col in col_list:
                ws.Columns(col).ColumnWidth = width
        elif set_type == SetType.AUTO:  # 自动调整
            for col in col_list:
                ws.Columns(col).AutoFit()

    @classmethod
    def set_row_height(cls, excel_obj, sheet_name: str, set_type: SetType, row: str, height: float):
        ws = cls._get_ws_obj(excel_obj, sheet_name)
        used_col = ws.Cells.SpecialCells(11).Column
        used_row = ws.Cells.SpecialCells(11).Row
        row_list = cls._handle_multiple_inputs(row, used_row, used_col, True)

        if set_type == SetType.VALUE:  # 指定行高
            for row in row_list:
                ws.Rows(row).RowHeight = height
        elif set_type == SetType.AUTO:  # 自动调整
            for row in row_list:
                ws.Rows(row).AutoFit()

    @classmethod
    def create_pivot_table(
        cls,
        excel,
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
        func_dict = {
            "sum": excel_constants.xlSum,
            "count": excel_constants.xlCount,
            "average": excel_constants.xlAverage,
            "max": excel_constants.xlMax,
            "min": excel_constants.xlMin,
            "product": excel_constants.xlProduct,
            "countNums": excel_constants.xlCountNums,
            "stDev": excel_constants.xlStDev,
            "stDevP": excel_constants.xlStDevP,
            "var": excel_constants.xlVar,
            "varP": excel_constants.xlVarP,
        }

        try:
            # Get the source worksheet and range
            src_ws = excel.Worksheets(source_sheet)
            src_range = src_ws.Range(source_range)

            rows_fields = cls.process_fields(src_ws, rows_fields)
            columns_fields = cls.process_fields(src_ws, columns_fields)
            values_fields = [
                {
                    "name": cls.process_fields(src_ws, [field_info["name"]])[0],
                    "function": field_info.get("function", "sum"),
                }
                for field_info in values_fields
            ]
            filter_fields = cls.process_fields(src_ws, filter_fields)

            # Get the pivot worksheet
            print(f"Accessing/Adding the pivot worksheet: {pivot_sheet}")
            pvt_ws, pivot_table = cls.get_or_create_sheet_and_pivot_table(
                excel, pivot_sheet, pivot_start_cell, pivot_table_name, src_range
            )

            # Determine field orientation constants
            row_orientation = excel_constants.xlRowField
            column_orientation = excel_constants.xlColumnField
            page_orientation = excel_constants.xlPageField
            data_orientation = excel_constants.xlDataField

            # Set up Rows, Columns, and Filters
            cls.add_fields_to_pivot(rows_fields, row_orientation, pivot_table)
            cls.add_fields_to_pivot(columns_fields, column_orientation, pivot_table)
            cls.add_fields_to_pivot(filter_fields, page_orientation, pivot_table)

            # Set up Data Fields with the selected function
            if values_fields:
                for field_info in values_fields:
                    field_name = field_info["name"]
                    aggregate_function = field_info.get("function", "sum").lower()  # 默认为'sum'
                    function_code = func_dict.get(aggregate_function, excel_constants.xlSum)  # 获取对应的Excel函数

                    try:
                        pivot_field = pivot_table.PivotFields(field_name)
                        pivot_table.AddDataField(
                            pivot_field,
                            f"{aggregate_function.upper()} of {field_name}",
                            function_code,
                        )
                    except Exception as e:
                        print(f"Error adding field '{field_name}' with function '{aggregate_function}': {e}")
                        continue

            print("Pivot table created successfully.")
            return pivot_table

        except Exception as e:
            print("Failed to create pivot table.")
            print("Error: ", str(e))
            print("Traceback: ", traceback.format_exc())

            return None

    @staticmethod
    def get_or_create_sheet_and_pivot_table(excel_obj, pivot_sheet, pivot_start_cell, pivot_table_name, src_range):
        try:
            pvt_ws = excel_obj.Worksheets(pivot_sheet)
        except Exception as e:
            pvt_ws = excel_obj.Worksheets.Add()
            pvt_ws.Name = pivot_sheet

        pivot_cache = excel_obj.PivotCaches().Create(
            SourceType=win32com.client.constants.xlDatabase, SourceData=src_range
        )
        pivot_table = pivot_cache.CreatePivotTable(
            TableDestination=pvt_ws.Range(pivot_start_cell), TableName=pivot_table_name
        )
        return pvt_ws, pivot_table

    @staticmethod
    def add_fields_to_pivot(fields_list, orientation, pivot_table):
        for i, field_name in enumerate(fields_list, start=1):
            field = pivot_table.PivotFields(field_name)
            field.Orientation = orientation
            field.Position = i

    @classmethod
    def process_fields(cls, worksheet, fields):
        # Convert field input which may be column labels, numbers or names, to names
        field_names = []
        for field in fields:
            if isinstance(field, str) and len(field) == 1 and field.isalpha():
                # Field is a column label like 'A', 'B', etc.
                index = cls._column_letter_to_number(field)
                field_name = cls.get_field_name_from_index(worksheet, index)
                field_names.append(field_name)
            elif isinstance(field, int) and field > 0:
                # Field is a 1-based column index
                field_name = cls.get_field_name_from_index(worksheet, field)
                field_names.append(field_name)
            elif isinstance(field, str):
                # Field is assumed to be a name
                field_names.append(field)
            else:
                raise ValueError(f"Invalid field input: {field}")
        return field_names

    @classmethod
    def get_field_name_from_index(cls, worksheet, index):
        # Get the field (column) name from a 1-based index
        return worksheet.Cells(1, index).Value

    @classmethod
    def transfer_to_list(cls, values):
        if not isinstance(values, list):
            values = values.replace("，", ",")
            if values.startswith("[") and values.endswith("]"):
                values = ast.literal_eval(values) if values else []
            else:
                values = values.split(",") if values else []
        return values

    @classmethod
    def process_field(cls, worksheet, fields):
        field_names = []
        for field in fields:
            if isinstance(field, str) and len(field) == 1 and field.isalpha():
                field = cls._column_letter_to_number(field)
            elif isinstance(field, int) and field > 0:
                field = field
            elif isinstance(field, str):
                field = cls.get_column_index_by_name(worksheet, field)
            else:
                raise ValueError(f"Invalid field input: {field}")
            field_names.append(field)
        if len(field_names) == 1:
            return field_names[0]
        else:
            return field_names

    @classmethod
    def get_column_index_by_name(cls, worksheet, column_name):
        for col_index in range(1, worksheet.UsedRange.Columns.Count + 1):
            cell_value = worksheet.Cells(1, col_index).Text
            if cell_value is not None and str(cell_value).strip().lower() == column_name.strip().lower():
                return col_index
        raise ValueError(f"Column name '{column_name}' not found.")

    @classmethod
    def process_field_to_index(cls, worksheet, field):
        # Convert field input which may be column labels, numbers or names, to index
        if isinstance(field, str) and len(field) == 1 and field.isalpha():
            # Field is a column label like 'A', 'B', etc.
            field = cls._column_letter_to_number(field)
        elif isinstance(field, int) and field > 0:
            # Field is a 1-based column index
            field = field
        elif isinstance(field, str):
            # Field is assumed to be a name
            field = cls.get_column_index_by_name(worksheet, field)
        else:
            raise ValueError(f"Invalid field input: {field}")
        return field
