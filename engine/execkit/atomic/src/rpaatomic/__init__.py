from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union


class AtomicLevel(Enum):
    """原子能力-等级"""

    # 普通
    NORMAL = "normal"
    # 高级
    ADVANCED = "advanced"


class AtomicFormType(Enum):
    """原子能力-FormType"""

    # 切换
    SWITCH = "SWITCH"
    # 提示
    TIP = "TIP"
    # 选择框
    SELECT = "SELECT"
    # html5 RADIO
    RADIO = "RADIO"
    # html5 CHECKBOX
    CHECKBOX = "CHECKBOX"
    # 返回值
    RESULT = "RESULT"
    # 输入框
    INPUT = "INPUT"
    # 输入框+变量
    INPUT_VARIABLE = "INPUT_VARIABLE"
    # 输入框+变量+python
    INPUT_VARIABLE_PYTHON = "INPUT_VARIABLE_PYTHON"
    # 输入框+变量+python+时间
    INPUT_VARIABLE_PYTHON_DATETIME = "INPUT_VARIABLE_PYTHON_DATETIME"
    # 输入框+变量+python+文件
    INPUT_VARIABLE_PYTHON_FILE = "INPUT_VARIABLE_PYTHON_FILE"
    # 输入框+变量+颜色
    INPUT_VARIABLE_COLOR = "INPUT_VARIABLE_COLOR"
    # 输入框+变量+python+Excel工具
    INPUT_VARIABLE_PYTHON_EXCEL = "INPUT_VARIABLE_PYTHON_EXCEL"
    # 输入框+扩大输入框
    INPUT_PYTHON_TEXTAREAMODAL_VARIABLE = "INPUT_PYTHON_TEXTAREAMODAL_VARIABLE"
    # 拾取工具
    PICK = "PICK"

    # 读取键位工具（用于键盘输入）
    KEYBOARD = "KEYBOARD"
    # 鼠标点击获取位置（鼠标移动）
    MOUSEPOSITION = "MOUSEPOSITION"
    # CV九宫格选择器
    GRID = "GRID"
    # 滑块工具 【CV相似度匹配】
    SLIDER = "SLIDER"
    # 读取剪贴板 （目前用于邮件）
    CONTENTPASTE = "CONTENTPASTE"
    # 对话框预览 及 自定义按钮
    MODALBUTTON = "MODALBUTTON"
    # 日期时间选择框
    DEFAULTDATEPICKER = "DEFAULTDATEPICKER"
    # 日期时间段选择框
    RANGEDATEPICKER = "RANGEDATEPICKER"
    # 选择对话框选项组件
    OPTIONSLIST = "OPTIONSLIST"
    # 子流程参数
    PROCESS_PARAM = "PROCESS_PARAM"
    # 密码掩码控件
    DEFAULTPASSWORD = "DEFAULTPASSWORD"
    # 元素选择 + 自定义元素控件(目前用于合同原子能力) params:{"code":1} 1代表上半部 2代表下半部 3代表全部
    FACTOR_ELEMENT = "FACTORELEMENT"
    # js的参数
    SCRIPTPARAMS = "SCRIPTPARAMS"
    # 远程参数
    REMOTEPARAMS = "REMOTEPARAMS"
    # 卓越中心共享文件夹
    REMOTEFOLDERS = "REMOTEFOLDERS"


class AtomicFormTypeParam(Enum):
    PICK = {
        "use": "ELEMENT",  # ["ELEMENT", "WINDOW", "POINT", "CV"] 中的一个
    }
    INPUT_VARIABLE_PYTHON_FILE = {
        "file_type": "file",  # ["file", "files", "folder"] 中的一个
        "filters": [".txt"],  # 在file_type为file有效 标识只要.txt的后缀文件
        "defaultPath": "test.xls",  # 默认名称 只适用于 file
    }
    SELECT = {"filters": "Process"}  # ["Process", "PyModule"] 中的一个
    PROCESS_PARAM = {"linkage": "process"}  # xxx关联参数


@dataclass
class AtomicOption:
    """原子能力-参数-Option"""

    label: str
    value: Any

    def tojson(self, filtered_none=True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data


@dataclass
class DynamicsItem:
    key: str = ""
    expression: str = ""  # 表达式


@dataclass
class AtomicMeta:
    """原子能力-元数据"""

    # 缓存: 已经结束的不做处理
    __end__: bool = None
    # 是否有kwargs
    __has_kwargs__: bool = None

    # --核心--

    # 唯一值
    key: str = None
    # 名称
    title: str = None
    # 版本 1
    version: str = None
    # 后端映射代码位置
    src: str = None
    # 语义说明
    comment: str = None

    # 输入列表
    inputList: list = None
    # 输出列表
    outputList: list = None

    # --前端依赖--

    # 别名
    anotherName: str = None
    # Icon
    icon: str = None
    # 帮助手册
    helpManual: str = None
    # 无高级参数
    noAdvanced: bool = None

    # 原子能力支持的平台
    platform: str = None  # 默认只支持windows linux windows linux,windows

    def tojson(self, filtered_none=True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None and not k.startswith("_")}
        return data

    def init(self):
        if self.title and not self.anotherName:
            self.anotherName = self.title
        return self


@dataclass
class AtomicFormTypeMeta:
    """原子能力-FormType"""

    # 类型定义
    type: str = None  # AtomicFormType查看
    # 参数
    params: dict = None  # AtomicFormTypeParam查看

    def tojson(self, filtered_none=True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data


@dataclass
class AtomicParamMeta:
    """原子能力-输入输出Meta"""

    # 类型
    __annotation__: Any = None

    # --核心--

    # [必须]类型
    types: str = None
    # [必须]前端类型
    formType: AtomicFormTypeMeta = None
    # [必须]唯一值
    key: str = None
    # [必须]名称
    title: str = None
    # 后端映射名称
    name: str = None
    # 用户提示
    tip: str = None
    # 可选值
    options: list = None
    # 默认值
    default: Any = None
    # 值
    value: Any = None
    # 特殊解析
    need_parse: str = None

    # --前端依赖--

    # 等级
    level: AtomicLevel = None
    # 动态
    dynamics: List[DynamicsItem] = None
    # 链接方向
    direction: str = None
    # 是否必须(前提是要显示)
    required: bool = None
    # 是否只读
    readOnly: bool = None
    # 不能手动输入，只能选择
    noInput: bool = None
    # 发布时是否需要分享该参数(默认不需要)
    share: bool = None
    # 是否校验输入字符长度
    limitLength: list = None

    # 扩展值(特殊属性定义)
    exit: dict = None

    def tojson(self, filtered_none=True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None and not k.startswith("_")}
        return data

    def update(
        self,
        name: str = None,
        types: str = None,
        __annotation__: Any = None,
        formType: AtomicFormTypeMeta = None,
        default: Any = None,
        options: list = None,
        noInput: bool = None,
        required: Union[None, bool] = True,
    ):
        if self.name is None:
            self.name = name
        if self.types is None:
            self.types = types
        if self.__annotation__ is None:
            self.__annotation__ = __annotation__
        if self.formType is None:
            self.formType = formType
            if self.formType.type.startswith("INPUT"):
                self.value = [{"type": "str", "value": ""}]  # input开头的传递过来都是数组，做一个初始化操作
        if self.default is None:
            self.default = default
        if self.required is None:
            self.required = required
        if self.noInput is None:
            self.noInput = noInput
        if self.options is None:
            self.options = options
        return self


@dataclass
class TypesMeta:
    """类型-Meta"""

    # key
    key: str = None
    # src 源码位置
    src: str = None
    # 描述
    desc: str = None
    # version
    version: str = None
    # 场景
    channel: str = None
    # 描述
    template: str = None
    # 类型列表
    funcList: list = None


@dataclass
class TypeFuncMeta:
    """类型-快捷方法"""

    # key
    key: str = None
    # 方法描述
    funcDesc: str = None
    # 返回值类型
    resType: str = None
    # 返回值描述
    resDesc: str = None
    # src 源码如何使用
    useSrc: str = None


class ReportType(Enum):
    Code = "code"  # 流程的每一个原子额能力的日志打印
    Flow = "flow"  # 流程的日志打印
    User = "user"  # 用户的日志打印
    Tip = "tip"  # 提示日志打印
    Script = "script"  # 脚本中的日志打印


class ReportFlowStatus(Enum):
    INIT = "init"
    INIT_SUCCESS = "init_success"
    TASK_START = "task_start"
    TASK_END = "task_end"
    TASK_ERROR = "task_error"


class ReportCodeStatus(Enum):
    DEBUG_START = "debug_start"
    START = "start"
    RES = "res"
    ERROR = "error"
    SKIP = "skip"


class TimeFormatType(Enum):
    YMD = "%Y-%m-%d"
    YMD_HMS = "%Y-%m-%d %H:%M:%S"
    YMD_SHORT = "%Y-%m-%d"
    YMD_HM = "%Y-%m-%d %H:%M"
    YMD_HMS2 = "%Y-%m-%d %H:%M:%S"
    YMD_SLASH = "%Y/%m/%d"
    YMD_SLASH_HM = "%Y/%m/%d %H:%M"
    YMD_SLASH_HMS = "%Y/%m/%d %H:%M:%S"
    YMD_COMPACT = "%Y%m%d"
    HM = "%H:%M"
    HMS = "%H:%M:%S"
    WEEKDAY = "%w"
    DOY = "%j"
    ISO_WEEK = "%W"
    YMD_CN = "%Y年%m月%d日"
    YMD_CN_HM = "%Y年%m月%d日 %H:%M"
    YMD_CN_HMS = "%Y年%m月%d日 %H:%M:%S"


@dataclass
class ReportUser:
    log_type: ReportType = ReportType.User
    process: str = None
    process_id: str = None
    atomic: str = None
    line_id: str = ""
    line: int = 0
    msg_str: str = None


@dataclass
class ReportFlow:
    log_type: ReportType = ReportType.Flow
    max_line: int = 0
    status: ReportFlowStatus = ReportFlowStatus.INIT
    result: str = None  # 机器人状态 对应服务端上报状态 result
    data: Any = None  # 主流程的返回数据
    error_traceback: Any = None
    msg_str: str = None


@dataclass
class ReportTip:
    log_type: ReportType = ReportType.Tip
    msg_str: str = None


@dataclass
class ReportScript:
    log_type: ReportType = ReportType.Script
    msg_str: str = None


@dataclass
class ReportCode:
    log_type: ReportType = ReportType.Code
    process: str = None
    process_id: str = None
    atomic: str = None
    key: str = None
    line_id: str = ""
    line: int = 0
    status: ReportCodeStatus = ReportCodeStatus.RES
    error_traceback: Any = None
    msg_str: str = None
    debug_data: Any = None


class IgnoreException(Exception):
    pass
