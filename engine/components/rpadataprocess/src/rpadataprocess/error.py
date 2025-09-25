from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

VALUE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入数据类型有误，无法设置为变量") + ": {}")
INVALID_REGEX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的正则表达式有误") + ": {}")
INVALID_NUMBER_RANGE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数字范围有误") + ": {}")
INVALID_NUMBER_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数字格式有误") + ": {}")
INVALID_LIST_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的列表格式有误") + ": {}")
INVALID_DICT_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的字典格式有误") + ": {}")
INVALID_INDEX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的索引值有误") + ": {}")
INVALID_MATH_EXPRESSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数学表达式有误") + ": {}")
