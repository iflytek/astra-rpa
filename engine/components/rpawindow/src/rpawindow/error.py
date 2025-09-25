from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

PARAMETER_INVALID_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数异常") + ": {}")
WINDOW_NO_FIND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到目标窗口"))
WINDOW_SCROLL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("窗口滚动异常"))
WINDOW_SIZE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("目标窗口无法设置到指定大小"))
