import os.path
from typing import Any

from rpaatomic.error import PARAM_VERIFY_ERROR_FORMAT
from rpaatomic.types import typesMg

from rpaexcel.error import *


class ExcelObj:
    """Excel对象"""

    def __init__(self, obj: Any, path: str = ""):
        self.obj = obj
        self.path = os.path.abspath(path)

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, ExcelObj):
            return value
        raise BaseException(
            PARAM_VERIFY_ERROR_FORMAT.format(name, value),
            "{}参数验证失败{}".format(name, value),
        )

    def get_active_sheet(self) -> object:
        active_sheet = self.obj.ActiveSheet
        return active_sheet

    @typesMg.shortcut("ExcelObj", res_type="Str")
    def get_full_name(self) -> str:
        return self.path

    @typesMg.shortcut("ExcelObj", res_type="Int")
    def get_row_count(self) -> int:
        ws_obj = self.get_active_sheet()
        used_col = ws_obj.Cells.SpecialCells(11).Column
        used_row = ws_obj.Cells.SpecialCells(11).Row
        return used_row

    @typesMg.shortcut("ExcelObj", res_type="Int")
    def get_first_free_row(self) -> int:
        ws = self.get_active_sheet()
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
