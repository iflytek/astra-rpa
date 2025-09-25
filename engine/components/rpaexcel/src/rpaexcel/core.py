import os
import re
import string
from abc import ABC, abstractmethod
from typing import Any

import psutil
from rpaexcel import FileExistenceType


class IExcelCore(ABC):
    XlHAlign_map = {
        "default": 1,
        "left-aligned": -4131,
        "center": -4108,
        "right-aligned": -4152,
        "padding": 5,
        "aligned_both_sides": -4130,
        "center_cross_column": 7,
        "distributed_align": -4117,
    }
    XlVAlign_map = {
        "up": -4160,
        "middle": -4108,
        "down": -4107,
        "aligned_both_sides": -4130,
        "distributed_align": -4117,
    }
    XlConsolidation_map = {
        "sum": -4157,
        "mean": -4106,
        "count": -4112,
        "min": -4139,
        "max": -4136,
        "var": -4164,
        "mul": -4149,
        "std": -4155,
        "countNum": -4113,
        "stdP": -4156,
        "varP": -4165,
    }

    @staticmethod
    def excel_is_exists():
        excel_flag, wps_flag = False, False
        pid_list = psutil.pids()
        for pid in pid_list:
            try:
                p = psutil.Process(pid)
                p_name = p.name().lower()
                if p_name == "excel.exe":
                    excel_flag = True
                elif p_name == "et.exe":
                    wps_flag = True
            except Exception as e:
                raise LookupError("Execl文件未打开")
        return excel_flag, wps_flag

    @staticmethod
    def _column_letter_to_number(column_letter):
        """将列字母转换为列号"""
        if column_letter.isdigit():
            column_number = int(column_letter)
            return column_number
        elif column_letter.isupper():
            column_number = 0
            for i in range(len(column_letter)):
                column_number += (ord(column_letter[i]) - ord("A") + 1) * (26 ** (len(column_letter) - i - 1))
            return column_number
        else:
            raise ValueError("列号异常，请输入大写字母或索引！")

    @staticmethod
    def _column_number_to_letter(column):
        """数字转成字母。"""
        if type(column) is not int:
            return column
        result_str = ""
        while not (column // 26 == 0 and column % 26 == 0):
            temp = 25
            if column % 26 == 0:
                result_str += chr(temp + 65)
            else:
                result_str += chr(column % 26 - 1 + 65)
            column //= 26
        return result_str[::-1]

    @staticmethod
    def _handle_row_input(row: Any, used_row: int):
        # 处理行号输入 可以输入数字或负数，负数表示从末尾开始计算
        # 支持负数
        if not row:
            return 1
        try:
            if int(row) < 0:
                row = used_row + 1 + int(row)
            else:
                row = int(row)
            return row
        except Exception as e:
            raise ValueError("行号输入异常，请输入数字或负数！")

    @staticmethod
    def _handle_column_input(col: str, used_col: int, digit_output: bool = True):
        if not col:
            return 1 if digit_output else "A"

        try:
            col = int(col)
            if col < 0:
                col = used_col + 1 + col
            if digit_output:
                return col
            else:
                col = IExcelCore._column_number_to_letter(col)
                return col
        except Exception as e:
            if digit_output:
                col = IExcelCore._column_letter_to_number(col)
            return col

    @staticmethod
    def _handle_multiple_inputs(inputs: str, used_row: int, used_col: int, is_row=True):
        # 处理多个列或行输入，比如A:B,C,-1

        inputs = inputs.replace("，", ",").replace("：", ":")
        inputs = inputs.split(",")
        result = []
        for index, element in enumerate(inputs):
            if element.find(":") != -1:
                left_element = element.split(":")[0]
                right_element = element.split(":")[1]
                if is_row:
                    left_element = IExcelCore._handle_row_input(left_element, used_row)
                    right_element = IExcelCore._handle_row_input(right_element, used_row)
                else:
                    left_element = IExcelCore._handle_column_input(element, used_col, True)
                    right_element = IExcelCore._handle_column_input(right_element, used_col, True)
                for i in range(left_element, right_element + 1):
                    result.append(i)
            else:
                if is_row:
                    result.append(IExcelCore._handle_row_input(element, used_row))
                else:
                    result.append(IExcelCore._handle_column_input(element, used_col, True))
        return result

    @staticmethod
    def _select_sheet(excel_obj, sheet_name):
        if not sheet_name:
            sheet_name = excel_obj.Worksheets(1).Name
        # 获取指定的工作表
        try:
            worksheet = excel_obj.Worksheets(sheet_name)
        except Exception as e:
            raise LookupError(f"未找到工作表: {sheet_name}. 错误信息: {e}")
        return worksheet

    @staticmethod
    def _check_color(color: str):
        if not color:
            return color
        if isinstance(color, str):
            color = color.split(",")
            try:
                color = [int(c.strip()) for c in color]
            except:
                raise ValueError("请输入正确的颜色格式！")
        if isinstance(color, list):
            if len(color) != 3:
                raise ValueError("请输入正确的颜色格式！")
            for rgb in color:
                if (not isinstance(rgb, int)) or rgb >= 256 or rgb < 0:
                    raise ValueError("请输入正确的颜色格式！")
        else:
            raise ValueError("请输入正确的颜色格式！")
        return color

    @staticmethod
    def _handle_used_range(address: str):
        # 处理带符号的used_range 比如 $A$1:$B$2
        # 当sheet完全没用过的时候，address是$A$1
        address_list = address.split(":")
        if len(address_list) == 1:
            starter = address_list[0]
            ender = address_list[0]
        else:
            starter = address_list[0]
            ender = address_list[1]
        if address.find("$") == -1:
            start_col = re.findall(r"[A-Z]+", starter)[0]
            start_row = re.findall(r"[0-9]+", starter)[0]
            end_col = re.findall(r"[A-Z]+", ender)[0]
            end_row = re.findall(r"[0-9]+", ender)[0]
        else:
            start_col = starter.split("$")[1]
            start_row = starter.split("$")[2]
            end_col = ender.split("$")[1]
            end_row = ender.split("$")[2]
        return [start_col, start_row, end_col, end_row]

    @staticmethod
    def _handle_cell_input(cell: str):
        # 处理单元格输入，比如A1
        cols = re.findall(r"[A-Z]+", cell)
        rows = re.findall(r"[0-9]+", cell)
        col = IExcelCore._column_letter_to_number(cols[0])
        return int(rows[0]), col

    @staticmethod
    def handle_existence(file_path, exist_type):
        # 文件存在时的处理方式
        if exist_type == FileExistenceType.OVERWRITE:
            # 覆盖已存在文件，直接返回文件路径
            # os.remove(file_path)
            return file_path
        elif exist_type == FileExistenceType.RENAME:
            if os.path.exists(file_path):
                full_file_name = os.path.basename(file_path)
                file_name, file_ext = os.path.splitext(full_file_name)
                count = 1
                while True:
                    new_full_file_name = f"{file_name}_{count}{file_ext}"
                    new_file_path = os.path.join(os.path.dirname(file_path), new_full_file_name)
                    if os.path.exists(new_file_path):
                        count += 1
                    else:
                        return new_file_path
            return file_path
        elif exist_type == FileExistenceType.CANCEL:
            if os.path.exists(file_path):
                return ""
            else:
                return file_path

    @staticmethod
    def get_column_names(start, end):
        column_names = []
        for i in range(start, end + 1):
            column_name = ""
            quotient = i
            while quotient > 0:
                remainder = (quotient - 1) % 26
                column_name = string.ascii_uppercase[remainder] + column_name
                quotient = (quotient - 1) // 26
            column_names.append(column_name)
        return column_names
