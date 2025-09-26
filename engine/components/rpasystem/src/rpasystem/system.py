import os

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg

from rpasystem import *
from rpasystem.core.screenshot_core import ScreenShotCore
from rpasystem.error import *
from rpasystem.utils import folder_is_exists

ScreenShotCore = ScreenShotCore()


class System:
    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param(
                "png_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param("state_type", required=False),
            atomicMg.param("png_name", types="Str", required=True),
            atomicMg.param(
                "top_left_x",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.top_left_x.show",
                        expression="return $this.screen_type.value == '{}'".format(ScreenType.REGION.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "top_left_y",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.top_left_y.show",
                        expression="return $this.screen_type.value == '{}'".format(ScreenType.REGION.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "bottom_right_x",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.bottom_right_x.show",
                        expression="return $this.screen_type.value == '{}'".format(ScreenType.REGION.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "bottom_right_y",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                dynamics=[
                    DynamicsItem(
                        key="$this.bottom_right_y.show",
                        expression="return $this.screen_type.value == '{}'".format(ScreenType.REGION.value),
                    )
                ],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("screenshot_path", types="Str"),
        ],
    )
    def screen_shot(
        png_path: str = "",
        state_type: StateType = StateType.ERROR,
        png_name: str = "",
        screen_type: ScreenType = ScreenType.FULL,
        top_left_x: int = 0,
        top_left_y: int = 0,
        bottom_right_x: int = 0,
        bottom_right_y: int = 0,
    ):
        """
        屏幕截图
        """
        if not folder_is_exists(png_path):
            if state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_PATH_ERROR_FORMAT.format(png_path),
                    "指定保存路径不存在，请检查路径信息",
                )
            elif state_type == StateType.CREATE:
                os.makedirs(png_path, exist_ok=True)
            else:
                raise NotImplementedError()

        if not (os.path.splitext(png_name)[1] == ".png" or os.path.splitext(png_name)[1] == ".jpg"):
            png_name = png_name + ".png"
        screenshot_path = os.path.join(png_path, png_name)
        if screen_type == ScreenType.FULL:
            try:
                ScreenShotCore.screenshot(file_path=screenshot_path)
            except Exception as e:
                raise BaseException(SCREENSHOT_ERROR_FORMAT.format(e), "{e}")
        elif screen_type == ScreenType.REGION:
            screen_width, screen_height = ScreenShotCore.screen_size()
            if (
                top_left_x < 0
                or top_left_y < 0
                or bottom_right_x < 0
                or bottom_right_y < 0
                or top_left_x > screen_width
                or top_left_y > screen_height
                or bottom_right_x > screen_width
                or bottom_right_y > screen_height
            ):
                raise ValueError(
                    "输入坐标{}，{}，{}，{}须大于0且在屏幕范围[{}*{}]内".format(
                        top_left_x,
                        top_left_y,
                        bottom_right_x,
                        bottom_right_y,
                        screen_width,
                        screen_height,
                    )
                )
            region = (
                top_left_x,
                top_left_y,
                bottom_right_x - top_left_x,
                bottom_right_y - top_left_y,
            )
            try:
                ScreenShotCore.screenshot(region=region, file_path=screenshot_path)
            except Exception as e:
                raise BaseException(SCREENSHOT_ERROR_FORMAT.format(e), "{e}")
        return screenshot_path

    @staticmethod
    @atomicMg.atomic(
        "System",
        outputList=[
            atomicMg.param("screen_lock_result", types="Bool"),
        ],
    )
    def screen_lock():
        raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param("user_name", required=False),
            atomicMg.param("pwd_type", required=False),
            atomicMg.param(
                "password_text",
                dynamics=[
                    DynamicsItem(
                        key="$this.password_text.show",
                        expression="return $this.pwd_type.value == '{}'".format(PwdType.PASSWORD.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "password_rsa",
                dynamics=[
                    DynamicsItem(
                        key="$this.password_rsa.show",
                        expression="return $this.pwd_type.value == '{}'".format(PwdType.RSA.value),
                    )
                ],
                required=True,
            ),
        ],
        outputList=[atomicMg.param("screen_unlock_result", types="Bool")],
    )
    def screen_unlock(
        user_name: str = "",
        pwd_type: PwdType = PwdType.PASSWORD,
        password_text: str = "",
        password_rsa: str = "",
    ):
        raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param("file_type"),
            atomicMg.param("batch_print"),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.batch_print.value == '{}'".format(BatchType.SINGLE.value),
                    )
                ],
            ),
            atomicMg.param(
                "folder_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.folder_path.show",
                        expression="return $this.batch_print.value == '{}'".format(BatchType.BATCH.value),
                    )
                ],
            ),
            atomicMg.param("printer_type"),  # 打印设置  系统设置和自定义设置
            atomicMg.param("printer_name", required=False),
            atomicMg.param(
                "paper_size",
                dynamics=[
                    DynamicsItem(
                        key="$this.paper_size.show",
                        expression="return $this.printer_type.value == '{}'".format(PrinterType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "page_weight",
                types="Float",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_weight.show",
                        expression="return $this.paper_size.value == '{}'".format(PaperType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "page_height",
                types="Float",
                dynamics=[
                    DynamicsItem(
                        key="$this.page_height.show",
                        expression="return $this.paper_size.value == '{}'".format(PaperType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "print_num",
                dynamics=[
                    DynamicsItem(
                        key="$this.print_num.show",
                        expression="return $this.printer_type.value == '{}'".format(PrinterType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "orientation_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.orientation_type.show",
                        expression="return $this.printer_type.value == '{}'".format(PrinterType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "scale",
                dynamics=[
                    DynamicsItem(
                        key="$this.scale.show",
                        expression="return $this.printer_type.value == '{}'".format(PrinterType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "margin_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.margin_type.show",
                        expression="return $this.printer_type.value == '{}'".format(PrinterType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "left_margin",
                dynamics=[
                    DynamicsItem(
                        key="$this.left_margin.show",
                        expression="return $this.margin_type.value == '{}'".format(MarginType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "right_margin",
                dynamics=[
                    DynamicsItem(
                        key="$this.right_margin.show",
                        expression="return $this.margin_type.value == '{}'".format(MarginType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "top_margin",
                dynamics=[
                    DynamicsItem(
                        key="$this.top_margin.show",
                        expression="return $this.margin_type.value == '{}'".format(MarginType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "bottom_margin",
                dynamics=[
                    DynamicsItem(
                        key="$this.bottom_margin.show",
                        expression="return $this.margin_type.value == '{}'".format(MarginType.CUSTOM.value),
                    )
                ],
            ),
            atomicMg.param(
                "page",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.page.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.EXCEL.value),
                    )
                ],
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("printer_status", types="List"),
        ],
    )
    def printer(
        file_type: FileType = FileType.WORD,
        batch_print: BatchType = BatchType.SINGLE,
        file_path: str = "",
        folder_path: str = "",
        printer_type: PrinterType = PrinterType.DEFAULT,
        printer_name: str = "",
        paper_size: PaperType = PaperType.A4,
        page_weight: str = "",
        page_height: str = "",
        print_num: int = 1,
        orientation_type: OrientationType = OrientationType.VERTICAL,
        scale: int = 100,
        margin_type: MarginType = MarginType.DEFAULT,
        left_margin: float = 10,
        top_margin: float = 9.5,
        right_margin: float = 10,
        bottom_margin: float = 9.5,
        page: str = "",
    ):
        raise NotImplementedError()
