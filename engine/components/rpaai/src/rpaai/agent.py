from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH

from rpaai import DifyFileTypes
from rpaai.api.dify import Dify
from rpaai.api.xcagent import xcAgent


class Agent:
    @staticmethod
    @atomicMg.atomic(
        "Agent",
        inputList=[
            atomicMg.param("user", types="Str"),
            atomicMg.param("app_token", types="Str"),
            atomicMg.param(
                "variable_value",
                dynamics=[
                    DynamicsItem(
                        key="$this.variable_value.show",
                        expression="return $this.file_flag.value == false",
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "file_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_type.show",
                        expression="return $this.file_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("dify_result", types="Str")],
    )
    def call_dify(
        user: str,
        app_token: str,
        file_flag: bool = False,
        variable_name: str = "",
        variable_value: str = "",
        file_path: PATH = "",
        file_type: DifyFileTypes = DifyFileTypes.DOCUMENT,
    ):
        # 使用示例

        # file_path = r"C:\Users\zyzhou23.IFLYTEK\Downloads\写出好的代码 -经验篇.md"
        # user = "drbruce"
        # dify = Dify("app-MgbOPD6ZYA6mSyip1w4h74wU")

        dify = Dify(app_token)
        file_id = None
        # 上传文件
        if file_flag:
            file_id = dify.upload_file(file_path, user)
        # file_id = "a17f9f77-4eb9-461b-a62c-1f302c806187"
        if file_id:
            # 文件上传成功，继续运行工作流
            # result = dify.run_workflow(user, "input_files", True, file_id, "document")
            result = dify.run_workflow(user, variable_name, file_flag, file_id, file_type.value)
            print(result)
        else:
            result = dify.run_workflow(user, variable_name, file_flag, variable_value, file_type.value)
            print(result)
        return result

    @staticmethod
    @atomicMg.atomic(
        "Agent",
        inputList=[
            atomicMg.param("app_key", types="Str"),
            atomicMg.param("app_secret", types="Str"),
            atomicMg.param("flow_id", types="Str"),
            atomicMg.param(
                "input_value",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT.value),
            ),
        ],
        outputList=[atomicMg.param("xcagent_result", types="Str")],
    )
    def call_xcagent(api_key: str, api_secret: str, flow_id: str, input_value: str = ""):
        # def call_xcagent(api_key: str, api_secret: str, file_flag: bool = False, variable_name: str = "",
        #                  variable_value: str = "",
        #                  file_path: PATH = "", file_type: DifyFileTypes = DifyFileTypes.DOCUMENT):

        xcagent = xcAgent(api_key, api_secret)
        xcagent_result = xcagent.run_flow(flow_id, input_value)
        return xcagent_result
