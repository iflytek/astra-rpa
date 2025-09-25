from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

EXE_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("指定窗口运行路径不存在,请检查路径信息") + ": {}")
