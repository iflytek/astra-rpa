from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
CV_MATCH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未匹配到目标元素，请检查当前界面或降低匹配相似度后重试"))
SPECIFIC_POSITION_ERROR = ErrorCode(BizCode.LocalErr, _("未指定点击位置，请检查参数设置"))
MOUSE_CLICK_ERROR = ErrorCode(BizCode.LocalErr, _("鼠标点击失败"))
MOUSE_HOVER_ERROR = ErrorCode(BizCode.LocalErr, _("鼠标悬停失败"))
CV_INPUT_ERROR = ErrorCode(BizCode.LocalErr, _("输入文本失败"))
TARGET_EXISTS_ERROR = ErrorCode(BizCode.LocalErr, _("当前界面目标元素不存在"))
