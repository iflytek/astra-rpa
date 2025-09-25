from rpaframe import _
from rpaframe.error.error import BaseException, BizCode, ErrorCode

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
HTTP_DOWNLOAD_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("HTTP下载失败，错误：{}"))

FTP_CONNECTION_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("连接到FTP服务器失败，请检查服务器地址：{}及端口号：{}")
)
FTP_LOGIN_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("登陆到FTP失败，请检查用户名：{}和密码：{}"))
FTP_CLOSE_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("FTP连接关闭失败，详细信息：{}"))
FTP_STATUS_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("连接出现错误，请检查FTP是否已断开连接：{}"))
FTP_DELETE_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("FTP文件删除失败：{}"))
FTP_RENAME_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("FTP文件/文件夹重命名失败：{}"))
FTP_CREATE_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("FTP目录创建失败：{},请检查FTP连接"))
FTP_UPLOAD_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{}上传失败，请检查FTP连接"))
FTP_DOWNLOAD_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{}下载失败，请检查FTP连接"))

FILE_EXIST_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件：{}不存在或格式错误，请检查文件路径信息"))
FOLDER_EXIST_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件夹：{}不存在，请检查文件夹路径信息"))

FILE_NAME_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入文件名称：{}扩展名缺失，请检查输入内容"))
FOLDER_NAME_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入文件夹名称：{}有误，请检查输入内容"))
