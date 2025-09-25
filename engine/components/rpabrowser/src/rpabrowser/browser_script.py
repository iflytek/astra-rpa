"""浏览器脚本模块，提供浏览器脚本执行功能。"""

import platform
import sys

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH, WebPick

from rpabrowser import CHROME_LIKE_BROWSERS, InputType
from rpabrowser.browser import Browser
from rpabrowser.browser_element import CodeChromeBuilder
from rpabrowser.core.core import IBrowserCore
from rpabrowser.error import CODE_EMPTY, CODE_NO_MAIN_FUNC

if sys.platform == "win32":
    from rpabrowser.core.core_win import BrowserCore
elif platform.system() == "Linux":
    from rpabrowser.core.core_unix import BrowserCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

BrowserCore: IBrowserCore = BrowserCore()


class BrowserScript:
    """浏览器脚本执行类。"""

    @staticmethod
    @atomicMg.atomic(
        "BrowserScript",
        inputList=[
            atomicMg.param(
                "content",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_PYTHON_TEXTAREAMODAL_VARIABLE.value,
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.content.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.Content.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".js"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.input_type.value == '{}'".format(InputType.File.value),
                    )
                ],
            ),
            atomicMg.param(
                "params",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SCRIPTPARAMS.value),
                need_parse="json_str",
                required=False,
            ),
            atomicMg.param("element_data", required=False),
            atomicMg.param("iframe_url", required=False),
        ],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def js_run(
        browser_obj: Browser,
        input_type: InputType = InputType.Content,
        content: str = "",
        file_path: PATH = "",
        params: list = None,
        element_data: WebPick = None,
        iframe_url: str = "",
    ):
        """运行JavaScript脚本。"""
        if input_type == InputType.File:
            with open(file_path, encoding="utf8") as f:
                content = f.read()
        if not content:
            raise BaseException(
                CODE_EMPTY,
                f"脚本数据为空 {input_type} {content} {file_path}",
            )
        if "function main" not in content:
            raise BaseException(CODE_NO_MAIN_FUNC, "代码中必须包含main函数")
        is_await = False
        if "await function main" in content:
            is_await = True
        if params:
            for p in params:
                extend_js_str = "var "
                extend_js_str = extend_js_str + p.get("varName") + "=" + f'"{p.get("varValue")}"' + ";"
                content = extend_js_str + content
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            js_op = content + CodeChromeBuilder.eval_js_code(is_await)
            data_param = {
                "code": js_op,
            }
            if element_data:
                data_param = {
                    "code": js_op,
                    **element_data["elementData"]["path"],
                }
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="runJS",
                data=data_param,
            )
        else:
            raise NotImplementedError()
        return data
