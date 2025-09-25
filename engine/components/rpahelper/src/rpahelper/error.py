from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

ELEMENT_FAIL_GET_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素获取异常") + ": {}")
SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误") + ": {}")
SPECIAL_PARSE_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("特殊元素处理异常") + ": {}")
