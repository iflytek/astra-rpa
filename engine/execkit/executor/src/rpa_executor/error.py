import re
from functools import wraps

from rpaatomic import IgnoreException
from rpaframe.error.error import BaseException, BizCode, ErrorCode
from rpaframe.i18n.i18n import _

from rpa_executor.flow.syntax.event import CloseError

INDEX_ERROR = IndexError

BaseException = BaseException

ReportFlowInit = _("开始初始化...")
ReportFlowInitSuccess = _("初始化完成")
ReportFlowTaskStart = _("开始执行")
ReportFlowTaskEnd = _("执行结束")
ReportFlowTaskEndUserClose = _("执行结束，用户主动关闭")
ReportFlowTaskError = _("执行错误")
ReportStartMsgFormat = _("{} 执行第{}条指令 [{}]")
ReportDebugStartMsgFormat = _("{} 开始调试第{}条指令 [{}]")
ReportCodeSkip = _("执行错误跳过")
ReportCodeError = _("执行错误")
BreakSyntaxError = _("break和continue语句必须在循环中使用")
NO_ATOMIC_FORMAT = _("检查{}原子能力是否合法")
GLOBAL_PARAM_NAME_FORMAT = _("全局变量{}")
FLOW_PARAM_NAME_FORMAT = _("全局变量{}")

DOWNLOAD_ATOMIC_FORMAT = _("{}动态下载中...")
DOWNLOAD_ATOMIC_SUCCESS_FORMAT = _("{}下载完成")

VIDEO_RECORDING_WAIT = _("录屏数据处理中，可能时间较长，请稍等")

CODE_OK: ErrorCode = ErrorCode(BizCode.OK, "ok", 200)
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误") + ": {}")
CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"))
TASK_RUNNING_CANNOT_EXECUTE: ErrorCode = ErrorCode(BizCode.LocalErr, _("已有任务正在执行，‌当前任务无法执行"))
SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误") + ": {}")
ENGINEERING_DATA_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("工程数据异常"))
RECURSIVE_CALL_MAX_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("加载子流程超过{}上限，可能是循环引用"))
RECURSIVE_CALL: ErrorCode = ErrorCode(BizCode.LocalErr, _("循环引用"))
SYNTAX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("语法错误") + ": {}")
CONDITION_ILLEGAL_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("条件解析非法") + ": {}")
ELEMENT_FAIL_GET_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素获取异常") + ": {}")
REMOTE_VARIABLE_FAIL_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("远程参数获取异常") + ": {}")
MODULE_FAIL_GET_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("模块获取异常") + ": {}")
SPECIAL_PARSE_FORMAL: ErrorCode = ErrorCode(BizCode.LocalErr, _("特殊元素处理异常") + ": {}")
CHILD_PROCESS_PARAM_NOT_VALID: ErrorCode = ErrorCode(BizCode.LocalErr, _("子流程参数不合法"))
TYPE_KIND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("类型错误") + ": {}")
VALUE_NOT_PARSE: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数解析失败"))


def python_base_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NameError as e:
            error_str = str(e)
            name_error_translations = [
                (r"name '(.+)' is not defined", "未定义的名称 '{}'"),
            ]
            for pattern, translation in name_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except TypeError as e:
            type_error_translations = [
                (
                    r"unsupported operand type\(s\) for ([^:]+): '(.+)' and '(.+)'",
                    "对于运算符 '{}' 不支持的操作数类型: '{}' 和 '{}'",
                ),
                (
                    r'can only concatenate ([^(]+) \(not \"([^"]+)\"\) to ([^(]+)',
                    "只能将 '{}' (而不是 '{}') 与 '{}' 连接",
                ),
                (r"'(.+)' object is not subscriptable", "'{}' 对象不支持索引操作"),
                (r"'(.+)' object is not callable", "'{}' 对象不可调用"),
                (r"'(.+)' object is not iterable", "'{}' 对象不是可迭代的"),
                (
                    r"([^()]+)\(\) missing (\d+) required positional argument(s)?",
                    "函数 '{}' 缺少 {} 个位置参数",
                ),
                (
                    r"([^()]+)\(\) takes (\d+) positional argument(?:s)? but (\d+) (was|were) given",
                    "函数 '{}' 需要 {} 个位置参数，但给出了 {} 个",
                ),
                (
                    r"([^()]+)\(\) got an unexpected keyword argument '(.+)'",
                    "函数 '{}' 收到未预期的关键字参数 '{}'",
                ),
                (r"unhashable type: '(.+)'", "无法哈希的类型: '{}'"),
            ]

            error_str = str(e)
            for pattern, translation in type_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except IndexError as e:
            index_error_translations = [
                (r"list index out of range", "列表索引超出范围"),
                (r"tuple index out of range", "元组索引超出范围"),
                (r"string index out of range", "字符串索引超出范围"),
            ]
            error_str = str(e)
            for pattern, translation in index_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except KeyError as e:
            key_error_translations = [
                (r"'(.+)'", "字典中不存在键 '{}'"),
            ]
            error_str = str(e)
            for pattern, translation in key_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except ValueError as e:
            value_error_translations = [
                (
                    r"invalid literal for int\(\) with base 10: '(.+)'",
                    "无效的字面量 '{}' 不能转换为整数",
                ),
                (
                    r"could not convert string to float: '(.+)'",
                    "无效的字面量 '{}' 不能转换为浮点数",
                ),
            ]
            error_str = str(e)
            for pattern, translation in value_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except AttributeError as e:
            attribute_error_translations = [
                (r"(.+) object has no attribute '(.+)'", "{} 对象没有属性 '{}'"),
            ]
            error_str = str(e)
            for pattern, translation in attribute_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except ZeroDivisionError as e:
            error_str = "除零错误,除数不能为零"
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except ImportError as e:
            import_error_translations = [
                (r"cannot import name '(.+)' from '(.+)'", "无法从 '{}' 导入名称 '{}'"),
                (r"No module named '(.+)'", "没有名为 '{}' 的模块"),
            ]
            error_str = str(e)
            for pattern, translation in import_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except SyntaxError as e:
            error_str = f"语法错误, 文件名: '{e.filename}', 行号: {e.lineno}, 列号: {e.offset}, 代码行: {repr(e.text)}"
            raise BaseException(ERROR_FORMAT.format(error_str), error_str) from e
        except CloseError as e:
            raise e
        except IgnoreException as e:
            raise e
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            else:
                raise e

    return wrapper
