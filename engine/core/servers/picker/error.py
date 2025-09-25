from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误") + ": {}")
CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{} 参数异常"))
TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取超时")
TIMEOUT_LAG: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取卡顿超过15s，请退出编辑器后重新进入")
NO_WEB_INFO: ErrorCode = ErrorCode(BizCode.LocalErr, "缺乏元素的web信息")
