from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

LLM_NO_RESPONSE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("大模型无返回结果，请重试") + ": {}")
