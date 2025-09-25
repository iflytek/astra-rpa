from rpaexcel.core import IExcelCore


class ExcelCore(IExcelCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "linux {}".format(msg)
