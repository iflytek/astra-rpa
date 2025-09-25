from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("内容为空"))
FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件路径:{}有误，请输入正确的路径！"))
SAVE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("保存格式:{}有误，文件扩展名需为{}！"))
FILE_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件读取失败，请检查文件是否损坏！") + ": {}")
FILE_WRITE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件写入失败，请检查文件是否损坏！") + ": {}")
FILE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("文件拓展名缺失，请检查文件名称输入是否正确！") + ": {}"
)
FILE_DELETE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件删除失败") + ": {}")
PermissionError_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件：{}被占用，请关闭文件后重试"))
CMD_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("CMD命令:{}执行失败:{}"))

READ_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("当前文件格式：{}不支持读取，当前仅支持{}格式，请检查文件格式")
)
RENAME_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("新名称：{}和原名称一致，请检查重命名内容"))
ENCODE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr,
    _("当前文件编码格式({})与指定的解码类型({})发生冲突，请重新选择编码类型或者以二进制方式读取！"),
)

FOLDER_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("文件夹不存在，请检查文件夹路径是否正确！") + ": {}"
)
CONTENT_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取剪切板内容类型错误"))
FOLDER_DELETE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件夹删除失败") + ": {}")
SCREENSHOT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("截图保存失败") + ": {}")
SCREENLOCK_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("屏幕锁定失败") + ": {}")
