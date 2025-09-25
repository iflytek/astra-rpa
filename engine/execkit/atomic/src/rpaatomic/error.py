from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

TYPE_KIND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("类型错误") + ": {}")

CONFIG_LOAD_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("配置文件加载出错") + ": {}")
CONFIG_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("配置文件解析不支持该类型") + ": {}")

REQUIRED_PARAM_MISSING: ErrorCode = ErrorCode(BizCode.LocalErr, _("缺少必填参数") + ": {}")
PARAM_ARGS_NO_SUPPORT_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数不支持args") + ": {}")

PARAM_REQUIRED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数({})必填"))
PARAM_VALUE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("({})参数的值错误{}"))
PARAM_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("({})的值类型错误{}"))
PARAM_CONVERT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("({})的值转换成{}失败，原始值:{}"))
PARAM_VERIFY_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("({})参数验证失败: {}"))

VALUE_IS_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("({})参数值不能为空"))

ReportStartMsgFormat = _("{} 执行第{}条指令 [{}]")
ReportCodeError = _("执行错误")
ReportCodeSkip = _("执行错误跳过")
ReportCodeRetry = _("执行错误重试")
