import json
import time

from rpadialog import (
    ButtonType,
    DefaultButtonCN,
    FileType,
    InputType,
    OpenType,
    SelectType,
    TimeFormat,
    TimeType,
)
from rpadialog.dialog import Dialog


def demo_message_box():
    """演示消息对话框"""
    print("\n=== 1. 消息对话框演示 ===")
    dialog = Dialog()

    # 基础消息框
    print("显示基础消息框...")
    result = dialog.message_box(
        message_content="这是一个测试消息",
        button_type=ButtonType.CONFIRM_CANCEL,
        auto_check=True,
        default_button_cn=DefaultButtonCN.CANCEL,
        wait_time=3,
    )
    print(f"消息框结果: {result}")


def demo_input_box():
    """演示输入对话框"""
    print("\n=== 2. 输入对话框演示 ===")
    dialog = Dialog()

    # 文本输入框
    print("显示文本输入框...")
    result = dialog.input_box(
        input_type=InputType.TEXT,
        default_input_text="默认文本",
        input_title="请输入内容",
    )
    print(f"文本输入结果: {result}")

    # 密码输入框
    print("显示密码输入框...")
    result = dialog.input_box(
        input_type=InputType.PASSWORD,
        default_input_text="123456",
        input_title="请输入密码",
    )
    print(f"密码输入结果: {result}")


def demo_select_box():
    """演示选择对话框"""
    print("\n=== 3. 选择对话框演示 ===")
    dialog = Dialog()

    # 选项数据
    options = [
        {"rId": "option1", "value": "选项1"},
        {"rId": "option2", "value": "选项2"},
        {"rId": "option3", "value": "选项3"},
        {"rId": "option4", "value": "选项4"},
    ]

    # 单选
    print("显示单选对话框...")
    result = dialog.select_box(options=options, select_type=SelectType.SINGLE, options_title="请选择一个选项")
    print(f"单选结果: {result}")

    # 多选
    print("显示多选对话框...")
    result = dialog.select_box(options=options, select_type=SelectType.MULTI, options_title="请选择多个选项")
    print(f"多选结果: {result}")


def demo_time_box():
    """演示时间选择对话框"""
    print("\n=== 4. 时间选择对话框演示 ===")
    dialog = Dialog()

    # 单个时间选择
    print("显示时间选择对话框...")
    result = dialog.select_time_box(
        time_type=TimeType.TIME,
        time_format=TimeFormat.YEAR_MONTH_DAY_HOUR_MINUTE,
        input_title="请选择时间",
    )
    print(f"时间选择结果: {result}")

    # 时间范围选择
    print("显示时间范围选择对话框...")
    result = dialog.select_time_box(
        time_type=TimeType.TIME_RANGE,
        time_format=TimeFormat.YEAR_MONTH_DAY,
        input_title="请选择时间范围",
    )
    print(f"时间范围选择结果: {result}")


def demo_file_box():
    """演示文件选择对话框"""
    print("\n=== 5. 文件选择对话框演示 ===")
    dialog = Dialog()

    # 文件选择
    print("显示文件选择对话框...")
    result = dialog.select_file_box(
        open_type=OpenType.FILE,
        file_type=FileType.ALL,
        multiple_choice=False,
        select_title="请选择文件",
    )
    print(f"文件选择结果: {result}")

    # 文件夹选择
    print("显示文件夹选择对话框...")
    result = dialog.select_file_box(open_type=OpenType.FOLDER, select_title="请选择文件夹")
    print(f"文件夹选择结果: {result}")


def demo_custom_box():
    """演示自定义对话框"""
    print("\n=== 6. 自定义对话框演示 ===")
    dialog = Dialog()

    # 简单的自定义对话框配置
    design_interface = {
        "value": {
            "mode": "window",
            "title": "自定义对话框",
            "buttonType": "confirm_cancel",
            "formList": [
                {
                    "id": "bh723493861163077",
                    "dialogFormType": "INPUT",
                    "dialogFormName": "输入框",
                    "configKeys": [
                        "label",
                        "placeholder",
                        "defaultValue",
                        "bind",
                        "required",
                    ],
                    "label": "输入框",
                    "placeholder": "请输入文本内容",
                    "defaultValue": "",
                    "bind": "input_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                },
                {
                    "id": "bh723493864857669",
                    "dialogFormType": "PASSWORD",
                    "dialogFormName": "密码框",
                    "configKeys": [
                        "label",
                        "placeholder",
                        "defaultValue",
                        "bind",
                        "required",
                    ],
                    "label": "密码框",
                    "placeholder": "请输入密码",
                    "defaultValue": {
                        "formType": {"type": "DEFAULTPASSWORD"},
                        "key": "defaultValue",
                        "title": "默认值",
                        "placeholder": "请输入默认值",
                        "default": "",
                        "limitLength": [4, 16],
                        "value": "",
                    },
                    "bind": "password_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                },
                {
                    "id": "bh723493868687429",
                    "dialogFormType": "DATEPICKER",
                    "dialogFormName": "日期时间",
                    "configKeys": [
                        "label",
                        "format",
                        "defaultValue",
                        "bind",
                        "required",
                    ],
                    "label": "日期时间",
                    "format": {
                        "formType": {"type": "SELECT"},
                        "key": "time_format_select",
                        "title": "时间格式",
                        "options": [
                            {"label": "年-月-日", "value": "YYYY-MM-DD"},
                            {"label": "年-月-日 时:分", "value": "YYYY-MM-DD HH:mm"},
                            {
                                "label": "年-月-日 时:分:秒",
                                "value": "YYYY-MM-DD HH:mm:ss",
                            },
                            {"label": "年/月/日", "value": "YYYY/MM/DD"},
                            {"label": "年/月/日 时:分", "value": "YYYY/MM/DD HH:mm"},
                            {
                                "label": "年/月/日 时:分:秒",
                                "value": "YYYY/MM/DD HH:mm:ss",
                            },
                        ],
                        "default": "YYYY-MM-DD",
                        "required": False,
                        "value": "YYYY-MM-DD",
                    },
                    "defaultValue": {
                        "formType": {
                            "type": "DEFAULTDATEPICKER",
                            "params": {"format": "YYYY-MM-DD"},
                        },
                        "key": "default_time",
                        "title": "默认时间",
                        "default": "",
                        "value": "",
                    },
                    "bind": "datepicker_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "DATEPICKER_LINK",
                },
                {
                    "id": "bh723493871927365",
                    "dialogFormType": "PATH_INPUT",
                    "dialogFormName": "文件选择",
                    "configKeys": [
                        "label",
                        "selectType",
                        "filter",
                        "placeholder",
                        "defaultPath",
                        "bind",
                        "required",
                    ],
                    "label": "文件选择",
                    "selectType": {
                        "formType": {"type": "RADIO"},
                        "key": "file_type",
                        "title": "选择类型",
                        "options": [
                            {"label": "文件", "value": "file"},
                            {"label": "文件夹", "value": "folder"},
                        ],
                        "default": "file",
                        "value": "file",
                    },
                    "filter": {
                        "formType": {"type": "SELECT"},
                        "key": "file_filter_select",
                        "title": "文件类型",
                        "options": [
                            {"label": "所有文件", "value": "*"},
                            {"label": "Excel文件", "value": ".xls,.xlsx"},
                            {"label": "Word文件", "value": ".doc,.docx"},
                            {"label": "文本文件", "value": ".txt"},
                            {"label": "图像文件", "value": ".png,.jpg,.bmp"},
                            {"label": "PPT文件", "value": ".ppt,.pptx"},
                            {"label": "压缩文件", "value": ".zip,.rar"},
                        ],
                        "default": "*",
                        "value": "*",
                    },
                    "placeholder": "请选择文件",
                    "defaultPath": "",
                    "bind": "path_input_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "PATH_INPUT_LINK",
                },
                {
                    "id": "bh723493874372677",
                    "dialogFormType": "RADIO_GROUP",
                    "dialogFormName": "单选框",
                    "configKeys": [
                        "label",
                        "options",
                        "defaultValue",
                        "direction",
                        "bind",
                        "required",
                    ],
                    "label": "单选框",
                    "options": {
                        "formType": {"type": "OPTIONSLIST"},
                        "key": "options",
                        "title": "选项",
                        "default": [],
                        "required": True,
                        "value": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                    },
                    "defaultValue": {
                        "formType": {"type": "SELECT"},
                        "key": "default_option_single_select",
                        "title": "默认值",
                        "options": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                        "allowReverse": True,
                        "default": "",
                        "value": "",
                    },
                    "direction": {
                        "formType": {"type": "RADIO"},
                        "key": "direction",
                        "title": "排列方向",
                        "options": [
                            {"label": "横向排列", "value": "horizontal"},
                            {"label": "纵向排列", "value": "vertical"},
                        ],
                        "default": "horizontal",
                        "value": "horizontal",
                    },
                    "bind": "radio_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "OPTIONS_SINGLE_LINK",
                },
                {
                    "id": "bh723493876883525",
                    "dialogFormType": "CHECKBOX_GROUP",
                    "dialogFormName": "复选框",
                    "configKeys": [
                        "label",
                        "options",
                        "defaultValue",
                        "direction",
                        "bind",
                        "required",
                    ],
                    "label": "复选框",
                    "options": {
                        "formType": {"type": "OPTIONSLIST"},
                        "key": "options",
                        "title": "选项",
                        "default": [],
                        "required": True,
                        "value": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                    },
                    "defaultValue": {
                        "formType": {"type": "SELECT", "params": {"multiple": True}},
                        "key": "default_option_multi_select",
                        "title": "默认值",
                        "options": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                        "allowReverse": False,
                        "default": [],
                        "value": [],
                    },
                    "direction": {
                        "formType": {"type": "RADIO"},
                        "key": "direction",
                        "title": "排列方向",
                        "options": [
                            {"label": "横向排列", "value": "horizontal"},
                            {"label": "纵向排列", "value": "vertical"},
                        ],
                        "default": "horizontal",
                        "value": "horizontal",
                    },
                    "bind": "check_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "OPTIONS_MULTI_LINK",
                },
                {
                    "id": "bh723493880770629",
                    "dialogFormType": "SINGLE_SELECT",
                    "dialogFormName": "单选下拉框",
                    "configKeys": [
                        "label",
                        "options",
                        "placeholder",
                        "defaultValue",
                        "bind",
                        "required",
                    ],
                    "label": "单选下拉框",
                    "options": {
                        "formType": {"type": "OPTIONSLIST"},
                        "key": "options",
                        "title": "选项",
                        "default": [],
                        "required": True,
                        "value": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                    },
                    "placeholder": "请选择一项",
                    "defaultValue": {
                        "formType": {"type": "SELECT"},
                        "key": "default_option_single_select",
                        "title": "默认值",
                        "options": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                        "allowReverse": True,
                        "default": "",
                        "value": "",
                    },
                    "bind": "single_select_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "OPTIONS_SINGLE_LINK",
                },
                {
                    "id": "bh723493883248709",
                    "dialogFormType": "MULTI_SELECT",
                    "dialogFormName": "多选下拉框",
                    "configKeys": [
                        "label",
                        "options",
                        "placeholder",
                        "defaultValue",
                        "bind",
                        "required",
                    ],
                    "label": "多选下拉框",
                    "options": {
                        "formType": {"type": "OPTIONSLIST"},
                        "key": "options",
                        "title": "选项",
                        "default": [],
                        "required": True,
                        "value": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                    },
                    "placeholder": "请选择一项或多项",
                    "defaultValue": {
                        "formType": {"type": "SELECT", "params": {"multiple": True}},
                        "key": "default_option_multi_select",
                        "title": "默认值",
                        "options": [{"rId": "fEoiXZ3OXOuEKLh_M6wgL", "value": "选项1"}],
                        "allowReverse": False,
                        "default": [],
                        "value": [],
                    },
                    "bind": "multi_select_box_1",
                    "required": {
                        "formType": {"type": "CHECKBOX"},
                        "title": "设置该表单控件为必填",
                        "options": [
                            {"label": "是", "value": True},
                            {"label": "否", "value": False},
                        ],
                        "default": False,
                        "required": False,
                        "value": False,
                    },
                    "conditionalFnKey": "OPTIONS_MULTI_LINK",
                },
                {
                    "id": "bh723493886017605",
                    "dialogFormType": "TEXT_DESC",
                    "dialogFormName": "文本",
                    "configKeys": [
                        "fontFamily",
                        "fontSize",
                        "fontStyle",
                        "textContent",
                    ],
                    "fontFamily": {
                        "formType": {"type": "SELECT"},
                        "key": "fontFamily",
                        "title": "字体",
                        "options": [
                            {"label": "微软雅黑", "value": "msyh"},
                            {"label": "宋体", "value": "simsun"},
                            {"label": "黑体", "value": "simhei"},
                            {"label": "仿宋", "value": "simfang"},
                            {"label": "Times New Roman", "value": "times"},
                            {"label": "楷体", "value": "KaiTi"},
                            {"label": "隶书", "value": "LiShu"},
                            {"label": "新宋体", "value": "NSimSun"},
                            {"label": "幼圆", "value": "YouYuan"},
                            {"label": "Arial", "value": "Arial"},
                            {
                                "label": "Microsoft JhengHei",
                                "value": "MicrosoftJhengHei",
                            },
                            {"label": "Calibri", "value": "Calibri"},
                        ],
                        "default": "msyh",
                        "required": False,
                        "value": "msyh",
                    },
                    "fontSize": {
                        "formType": {"type": "FONTSIZENUMBER"},
                        "key": "fontSize",
                        "title": "字号",
                        "min": 12,
                        "max": 72,
                        "step": 2,
                        "default": 12,
                        "required": True,
                        "value": 12,
                    },
                    "fontStyle": {
                        "formType": {"type": "CHECKBOXGROUP"},
                        "key": "fontStyle",
                        "title": "字体属性",
                        "options": [
                            {"label": "加粗", "value": "bold"},
                            {"label": "斜体", "value": "italic"},
                            {"label": "下划线", "value": "underline"},
                        ],
                        "default": [],
                        "value": [],
                    },
                    "textContent": "文本描述",
                },
            ],
            "table_required": False,
        }
    }
    print("显示自定义对话框...")
    result = dialog.custom_box(design_interface=design_interface, auto_check=True, wait_time=10)
    print(f"自定义对话框结果: {result}")


def main():
    """主函数 - 运行所有演示"""
    print("=" * 50)
    print("RPA Dialog 功能演示")
    print("=" * 50)

    try:
        # 运行所有演示
        demo_message_box()
        demo_input_box()
        demo_select_box()
        demo_time_box()
        demo_file_box()
        demo_custom_box()
        print("\n" + "=" * 50)
        print("所有演示完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        print("请检查环境配置和依赖项")


if __name__ == "__main__":
    main()
