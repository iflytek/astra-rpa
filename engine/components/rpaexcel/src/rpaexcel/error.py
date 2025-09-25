from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件路径有误，请输入正确的路径！") + ": {}")
EXCEL_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件读取失败，请检查文件是否损坏！") + ": {}")
EXCEL_NOT_EXIST_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Excel未打开，请先打开Excel文件！") + ": {}")
EXCEL_UNAVAILABLE_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("Excel不可用，请检查Excel是否已被占用！") + ": {}"
)
INPUT_DATA_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入数据有误，请检查输入数据！") + ": {}")
