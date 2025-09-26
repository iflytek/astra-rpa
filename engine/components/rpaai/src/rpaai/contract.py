import ast

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH

from rpaai import InputType
from rpaai.api.llm import chat_prompt
from rpaai.prompt.contract import CONTRACT_FACTOR_DICT
from rpaai.utils.extract import FileExtractor


class ContractAI:
    @staticmethod
    @atomicMg.atomic(
        "ContractAI",
        inputList=[
            atomicMg.param(
                "contract_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.contract_path.show",
                        expression="return $this.contract_type.value == '{}'".format(InputType.FILE.value),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "contract_content",
                dynamics=[
                    DynamicsItem(
                        key="$this.contract_content.show",
                        expression="return $this.contract_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param(
                "custom_factors",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.FACTOR_ELEMENT.value,
                    params={
                        "code": 3,
                        "options": [
                            "合同名称",
                            "合同编号",
                            "合同签订日期",
                            "合同开始日期",
                            "合同结束日期",
                            "合同标的",
                            "标的数量",
                            "单价",
                            "税率",
                            "税额",
                            "合同总金额",
                            "付款方式",
                            "甲方",
                            "乙方",
                            "甲方开户行",
                            "甲方银行账号",
                            "乙方开户行",
                            "乙方银行账号",
                        ],
                    },
                ),
            ),
            atomicMg.param(
                "contract_validate",
                formType=AtomicFormTypeMeta(type=AtomicFormType.MODALBUTTON.value, params={"loading": False}),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("factor_result", types="Dict")],
    )
    def get_factors(
        contract_type: InputType = InputType.TEXT,
        contract_path: PATH = "",
        contract_content: str = "",
        custom_factors: str = "",
        contract_validate: str = "",
    ):
        if contract_type == InputType.FILE:
            contract_content = FileExtractor(contract_path).extract_text()

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

        params = {"factors": str(factors), "parsed_content": contract_content}
        reply = chat_prompt(prompt_type="contract", params=params)

        return reply
