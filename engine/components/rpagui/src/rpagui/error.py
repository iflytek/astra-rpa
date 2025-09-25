from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

KEYBOARD_MSG_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("键盘输入为空，请检查输入内容"))
DRIVE_ERROR: ErrorCode = ErrorCode(
    BizCode.LocalErr,
    _(
        "驱动:{}未安装成功，若安装过驱动，请重启电脑使驱动生效；\n若未安装驱动，请前往插件安装界面安装驱动，并重启电脑，使驱动生效！"
    ),
)
DRIVE_INPUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("驱动输入没有管理员权限，输入失败"))
KEY_INPUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("模拟键盘按键输入失败，请检查输入内容"))
SCROLL_FAILURE: ErrorCode = ErrorCode(BizCode.LocalErr, _("滑轮滚动过程中失败, 请检查环境是否出现异常"))
CLIP_PASTE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("剪切板中未获取到有效输入信息，请重新输入！"))
GHOST_DRIVE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("设备不存在或未连接,请检查设备连接"))
REGION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数不合法，请检查指定参数范围是否小于0或超出屏幕边界"))
