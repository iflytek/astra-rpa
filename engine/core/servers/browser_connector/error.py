from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

CODE_OK: ErrorCode = ErrorCode(BizCode.OK, "ok", 200)
CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"), 200)
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误") + ": {}", 200)
PARAMETER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误") + ": {}", 200)
