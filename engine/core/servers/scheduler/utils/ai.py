import ast
from enum import Enum
from typing import Any

import requests
import sseclient


class InputType(Enum):
    FILE = "file"
    TEXT = "text"


CONTRACT_COMMON_PROMPT = """
作为一名合同文件解析专家，你的任务是从用户提供的**合同文件内容**中，逐一精准提取用户指定的**提取要素**，并按照要求输出结果。请严格遵循**任务要求**和**输出格式**。

=====================
### **提取要素**：

请从合同文件中提取以下所有要素的信息：

{factors}

=====================
### **任务要求**：

1. *逐项匹配*：对于每个要素，请在合同文件内容中进行逐一匹配，并直接提取原文信息；
2. *严格来源*：所有要素信息必须直接源自合同文件原文，请勿进行任何归纳、总结或推理；
3. *重复出现*：如果某要素在合同文件中多次重复出现相同内容，仅提取一处即可；
4. *多处匹配*：如果某要素对应信息包含合同文件中不同位置的多处内容，请将不同位置的内容拼接成一个字符串，并使用中文逗号 `，`进行分隔；
5. *无匹配时*：若某要素在合同文件中未找到对应信息，请将该要素的值设置为空字符串 `""`；
6. *仅返回结果*：请勿添加任何解释性文字、评论或无关内容。

=====================
### **合同文件内容**：

以下是用户提供的合同文件内容，请按照**任务要求**给出提取结果：

{parsed_content}

=====================
### **输出格式**：

请严格按照以下 JSON 格式返回结果，确保字段名与要素一一对应，且仅包含提取的内容：

{
  "要素1名称": ["要素1原文信息1"，"要素1原文信息2"],
  "要素2名称": "要素2原文信息",
  "要素3名称": "",
  ...
}

"""

CONTRACT_FACTOR_DICT = {
    "合同名称": "反映合同内容和性质的完整标题或名称",
    "合同编号": "合同的唯一识别编码",
    "合同签订日期": "双方正式签署合同的日期",
    "合同开始日期": "合同正式生效或开始履行的日期",
    "合同结束日期": "合同有效期结束或某一阶段履行结束的最后日期",
    "合同标的": "合同交易对象的完整名称，比如货物、服务、物料等",
    "标的数量": "交易数量及单位，需明确计量方式",
    "单价": "单位商品/服务的价格及币种",
    "税率": "适用于合同货物或服务的税收比率，如增值税率",
    "税额": "依据税率计算出的具体税款金额",
    "合同总金额": "交易总价，需明确币种及是否含税",
    "付款方式": "结算方式，合同中指明的资金支付渠道及形式",
    "甲方": "合同发起方/需求方/买房，即承担采购、委托、发包或托运等任务的一方，也可以理解为发包人/委托人/托运方",
    "乙方": "合同接收方/服务提供者/卖方，即承担供货、施工、设计、监理、运输或其他服务的一方，也可以理解为承包人/设计人/监理人/被委托人/承运方",
    "甲方开户行": "合同发起方（甲方）的完整开户行名称",
    "甲方银行账号": "合同发起方（甲方）用于付款的具体银行账号",
    "乙方开户行": "合同接收方（乙方）的完整开户行名称",
    "乙方银行账号": "合同接收方（乙方）用于收款的具体银行账号",
}


def extract_pdf(path: str) -> str:
    """
    提取 pdf 文本内容

    :param path:
    :return:
    """
    import pypdf

    pdf_reader = pypdf.PdfReader(path)
    return "\n".join([pdf_reader.pages[page_num].extract_text() for page_num in range(len(pdf_reader.pages))])


def extract_docx(path: str) -> str:
    """
    提取 docx 文本内容

    :param path:
    :return:
    """
    try:
        from docx import Document as d_doc
    except Exception:
        raise Exception(
            "Docx package depend on Python 3.x version,"
            "Which compatible with most of OS and file generate by support Microsoft Office 2007"
            "if import error, please execute `pip install python-docx`"
        )
    document = d_doc(path)
    return "\n\n".join([para.text for para in document.paragraphs])


def chat_sse(inputs: Any, route_port: int):
    url = "http://127.0.0.1:8003/api/rpaai/chat"
    response = requests.post(url, json=inputs, stream=True)
    if response.status_code == 200:
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event:
                yield event.data
    else:
        pass


def get_factors(
    contract_type: InputType = InputType.TEXT,
    contract_path: str = "",
    contract_content: str = "",
    custom_factors: str = "",
    contract_validate: str = "",
    route_port: int = 8003,
):
    if contract_type == InputType.FILE:
        file_extension = contract_path.split(".")[-1]
        if file_extension == "pdf":
            contract_content = extract_pdf(contract_path)
        elif file_extension in ["docx", "doc"]:
            contract_content = extract_docx(contract_path)
        elif file_extension == "txt":
            contract_content = open(contract_path).read()
        else:
            raise ValueError("不支持的文件扩展类型: " + file_extension)
    try:
        custom_factors = ast.literal_eval(custom_factors)
    except:
        raise ValueError("custom_factors 格式错误，请检查")
    preset_factors = custom_factors.get("preset", [])
    custom_factors = custom_factors.get("custom", [])

    factors = []
    for factor in preset_factors:
        factors.append({"要素名": factor, "要素描述": CONTRACT_FACTOR_DICT[factor]})
    for factor in custom_factors:
        factors.append(
            {
                "要素名": factor["name"],
                "要素描述": factor.get("desc", ""),
                "要素实例": factor.get("example", ""),
            }
        )

    system_input = "你是一名合同文件解析专家，你擅长从用户提供的**合同文件内容**中，逐一精准提取用户指定的**提取要素**，并按照要求输出结果。你会严格遵循**任务要求**和**输出格式**。"
    user_input = CONTRACT_COMMON_PROMPT.replace("{factors}", str(factors)).replace("{parsed_content}", contract_content)

    inputs = [
        {"role": "user", "content": user_input},
        {"role": "system", "content": system_input},
    ]
    s = []
    for i in chat_sse(inputs, route_port):
        content = i.split("<$start>")[1].split("<$end>")[0]
        if content == "start" or content == "end":
            continue
        s.append(content)
    reply = "".join(s)

    return reply
