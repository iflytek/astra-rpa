from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH
from rpaopenapi import utils
from rpaopenapi.core_iflytek import OpenapiIflytek
from rpaopenapi.error import *


class OpenApi:
    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".xlsx", ".xls", ".csv"],
                        "defaultPath": "未命名.xls",
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("id_card", types="List")],
    )
    def id_card(
        is_multi: bool = True,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "id_card",
    ) -> list:
        header_dict = {
            "Address": "地址",
            "Birthday": "出生日期",
            "Gender": "性别",
            "ID": "公民身份号码",
            "Issuing-authority": "签发机关",
            "Name": "姓名",
            "Nation": "民族",
            "Validity-period": "有效期限",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.template_ocr(
            header_dict,
            files,
            "id_card",
            "https://api.xf-yun.com/v1/private/s5ccecfce",
            "s5ccecfce",
        )
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".xlsx", ".xls", ".csv"],
                        "defaultPath": "未命名.xls",
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("business_license", types="List")],
    )
    def business_license(
        is_multi: bool = True,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "business_license",
    ):
        header_dict = {
            "Business-scope": "经营范围",
            "Code": "统一社会信用代码",
            "Company-name": "名称",
            "Corporate-residence": "住所",
            "Date": "成立日期",
            "Formation": "类型",
            "Operating-period": "营业期限",
            "Paid-in-capital": "实缴资本",
            "Registered-capital": "注册资本",
            "Registration-number": "注册编号",
            "Type": "类型",
            "owner-name": "法定代表人",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.template_ocr(
            header_dict,
            files,
            "bus_license",
            "https://api.xf-yun.com/v1/private/sff4ea3cf",
            "sff4ea3cf",
        )
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                        "defaultPath": "未命名.xls",
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file", "filters": [".xlsx", ".xls", ".csv"]},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("vat_invoice", types="List")],
    )
    def vat_invoice(
        is_multi: bool = True,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "vat_invoice",
    ) -> list:
        header_dict = {
            "check-code": "验证码",
            "cryptographic-area": "密码区",
            "unit-price": "单价",
            "vat-invoice-daima": "发票代码",
            "vat-invoice-daima-right-side": "发票代码-右侧",
            "vat-invoice-goods-list": "货物或应税劳务、服务名称",
            "vat-invoice-haoma": "发票号码",
            "vat-invoice-haoma-right-side": "发票号码-右侧",
            "vat-invoice-issue-date": "开票日期",
            "vat-invoice-payer-addr-tell": "购买方地址电话",
            "vat-invoice-payer-bank-account": "购买方开户行及账号",
            "vat-invoice-payer-name": "购买方名称",
            "vat-invoice-price-list": "金额",
            "vat-invoice-rate-payer-id": "购买方纳税人识别号",
            "vat-invoice-seller-addr-tell": "销售方地址、电话",
            "vat-invoice-seller-bank-account": "销售方开户行及账号",
            "vat-invoice-seller-id": "销售方纳税识别号",
            "vat-invoice-seller-name": "销售方名称",
            "vat-invoice-tax-list": "税额",
            "vat-invoice-tax-rate-list": "税率",
            "vat-invoice-tax-total": "税额合计",
            "vat-invoice-total": "金额合计",
            "vat-invoice-total-cover-tax": "价税合计",
            "vat-invoice-total-cover-tax-digits": "价税合计小写",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.template_ocr(
            header_dict,
            files,
            "vat_invoice",
            "https://api.xf-yun.com/v1/private/s824758f1",
            "s824758f1",
        )
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".xlsx", ".xls", ".csv"],
                        "defaultPath": "未命名.xls",
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("train_ticket", types="List")],
    )
    def train_ticket(
        is_multi: bool = True,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "train_ticket",
    ) -> list:
        header_dict = {
            "Number1": "票号",
            "Ticket-check": "检票口",
            "Station-From": "起始站",
            "Number2-Train": "车次",
            "Station-To": "目的站",
            "Date": "发车日期",
            "Time": "开车时间",
            "Seat": "座位号",
            "Number3-Amount": "票价",
            "Seat-type": "座位类型",
            "Number4-Identity": "身份证号码",
            "Name": "乘车人姓名",
            "Number5": "条码数字",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.template_ocr(
            header_dict,
            files,
            "train_ticket",
            "https://api.xf-yun.com/v1/private/s19cfe728",
            "s19cfe728",
        )
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".xlsx", ".xls", ".csv"],
                        "defaultPath": "未命名.xls",
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("taxi_ticket", types="List")],
    )
    def taxi_ticket(
        is_multi: bool = True,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "taxi_ticket",
    ) -> list:
        header_dict = {
            "Plate-number": "车牌号",
            "Date": "日期",
            "Time": "上下车时间",
            "Number3_price": "单价",
            "Number4_mileage": "里程",
            "Number5_amount": "金额",
            "Number2_code": "号码",
            "Number1_code": "代码",
            "unknown_type": "未知类型",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.template_ocr(
            header_dict,
            files,
            "taxi_ticket",
            "https://api.xf-yun.com/v1/private/sb6db0171",
            "sb6db0171",
        )
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res

    @staticmethod
    @atomicMg.atomic(
        "OpenApi",
        inputList=[
            atomicMg.param(
                "src_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "file",
                        "filters": [".jpeg", ".jpg", ".png", ".gif", ".bmp"],
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_file.show",
                        expression="return $this.is_multi.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "src_dir",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "folder",  # ["file", "files", "folder"] 中的一个
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.src_dir.show",
                        expression="return $this.is_multi.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "dst_file",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={
                        "file_type": "folder",  # ["file", "files", "folder"] 中的一个
                    },
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.dst_file.show",
                        expression="return $this.is_save.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("common_ocr", types="List")],
    )
    def common_ocr(
        is_multi: bool = False,
        src_file: PATH = "",
        src_dir: PATH = "",
        is_save: bool = True,
        dst_file: PATH = "",
        dst_file_name: str = "common_ocr",
    ) -> list:
        header_dict = {
            "Context": "图文识别结果",
        }

        src_file = src_file if not is_multi else src_dir
        files = utils.generate_src_files(src_file)
        if len(files) == 0:
            raise BaseException(IMAGE_EMPTY, "图片路径不存在或格式错误")

        res = OpenapiIflytek.common_ocr(header_dict, files)
        if is_save:
            utils.write_to_excel(dst_file, dst_file_name, header_dict, res)
        return res
