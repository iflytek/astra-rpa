import os
import re
from abc import ABC
from functools import wraps

from rpadocx.error import FILE_PATH_ERROR_FORMAT


class IDocxCore(ABC):
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

                if not (path.endswith(".docx") or path.endswith(".doc") or path.endswith(".wps")):
                    raise ValueError(f"{param_name} 路径必须是.docx 或.doc或.wps 结尾")
                # 如果校验通过，调用原函数
                return func(*args, **kwargs)

            return wrapper

        return decorator

    # 判断是否为正整数，并将浮点数化为整型
    @staticmethod
    def are_positive_integers(*values):
        for value in values:
            if isinstance(value, float):
                value = int(value)
            if not isinstance(value, int):
                return False
            if value <= 0:
                return False
        return True

    @staticmethod
    def _extract_table_content(table):
        # 提取表格内容并返回为列表，同时清理不可见字符
        table_content = []
        row_cnt = 1
        while row_cnt <= table.Rows.Count:
            row = table.Rows(row_cnt)
            cell_cnt = 1
            row_content = []
            while cell_cnt <= row.Cells.Count:
                cell = row.Cells(cell_cnt)
                cell_text = re.sub(r"[\x00-\x1F\x7F]", "", cell.Range.Text).strip()
                row_content.append(cell_text)
                cell_cnt += 1
            table_content.append(row_content)
            row_cnt += 1
        return table_content

    @staticmethod
    def check_file_in_path(file_path, file_name):
        # 检查文件路径是否存在
        if not os.path.exists(file_path):
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_path),
                "填写的路径有误，请输入正确的路径！",
            )

        full_file_path = os.path.join(file_path, file_name)
        # 检查指定文件名是否在文件路径中
        if os.path.exists(full_file_path):
            return True
        else:
            return False
