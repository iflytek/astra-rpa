from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

WINDOW_NO_FIND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("找不到窗口，请检查窗口是否已关闭！") + ": {}")
WINDOW_SCROLL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("窗口滚动失败，请检查窗口是否已关闭！") + ": {}")
ELEMENT_NO_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到元素"))
PATH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("拾取或保存路径有误"))
UNPICKABLE: ErrorCode = ErrorCode(BizCode.LocalErr, _("拾取元素不支持该拾取类型"))
