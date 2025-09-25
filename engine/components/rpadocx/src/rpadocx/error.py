from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word文件路径有误，请输入正确的路径！") + ": {}")
WORD_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word文件读取失败，请检查文件是否损坏！") + ": {}")
DOC_NOT_EXIST_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word未打开，请先打开Word文件！") + ": {}")
WORD_INIT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word初始化失败，请检查Word是否安装正确！") + ": {}")
CONTENT_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("请检查输入是否正确！") + ": {}")
PASTE_CLIPBOARD_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请检查剪贴板是否存在内容！") + ": {}")
WORD_TABLE_EXIST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("表格不存在") + ": {}")
FILENAME_ALREADY_EXIST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件名已存在") + ": {}")
