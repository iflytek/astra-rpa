import platform
import sys

from rpaatomic.src.rpaatomic.atomic import atomicMg

from rpademo.src.rpademo import ReportLevelType
from rpademo.src.rpademo.core import IDemoCore
from rpademo.src.rpademo.error import *

if sys.platform == "win32":
    from rpademo.src.rpademo.core_win import DemoCore
elif platform.system() == "Linux":
    from rpademo.src.rpademo.core_unix import DemoCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

DemoCore: IDemoCore = DemoCore()


class Demo:
    @staticmethod
    @atomicMg.atomic("Demo", outputList=[atomicMg.param("msg", types="Str")])
    def print(print_type: ReportLevelType = ReportLevelType.INFO, print_msg: str = "") -> str:
        # 核心的代码最好放入到Core中
        # 好处:
        # 1. 屏蔽系统差异
        # 2. 抽象隔离,后续代码变动只用实现抽象实现
        # 3. 责任清晰，该文件只做对外原子能力的描述暴露(有很多废弃字段)
        # 4. 原子能力相互调用可以直接调用Core(优点2)，而尽量不调用原子能力(优点3，废弃字段)
        msg = DemoCore.print(print_msg)
        if not msg:
            # BaseException 第一个字段 暴露给用户的 需要翻译，第二个字段是 暴露给开发者的 日志信息 不需要翻译
            raise BaseException(MSG_EMPTY_FORMAT.format(msg), "消息为空 {}".format(print_msg))

        # 简单逻辑
        return "[{}] {}".format(print_type.value, msg)

    @staticmethod
    @atomicMg.atomic("Demo", outputList=[atomicMg.param("result", types="Str")])
    def create_txt_file(file_path: str, content: str = "helloworld") -> str:
        """
        在指定路径创建txt文件并写入内容，然后打开文件

        Args:
            file_path: 文件路径
            content: 要写入的内容，默认为"helloworld"

        Returns:
            操作结果信息
        """
        if not file_path:
            raise BaseException("文件路径不能为空", "文件路径参数为空")

        if not file_path.lower().endswith(".txt"):
            file_path += ".txt"

        # 调用核心实现
        result = DemoCore.create_and_open_txt(file_path, content)
        return result
