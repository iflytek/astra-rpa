from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件路径有误，请输入正确的路径！") + ": {}")
PDF_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件读取失败，请检查文件是否损坏！") + ": {}")
PDF_PASSWORD_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件读取失败，请检查密码是否正确！") + ": {}")
