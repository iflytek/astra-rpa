import mimetypes
import os

import requests

mimetypes.add_type("text/markdown", ".md")


class Dify:
    base_url = "https://api.dify.ai/v1/"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            # "Content-Type": "application/json"
        }

    def upload_file(self, file_path, user):
        upload_url = self.base_url + "files/upload"

        try:
            print("上传文件中...")
            mime_type, _ = mimetypes.guess_type(file_path)

            file_extension = os.path.splitext(file_path)[1].replace(".", "").upper()
            with open(file_path, "rb") as file:
                files = {
                    "file": (
                        os.path.basename(file_path),
                        file,
                        mime_type,
                    )  # 确保文件以适当的MIME类型上传
                }
                data = {"user": user, "type": file_extension}  # 设置文件类型为扩展名

                response = requests.post(upload_url, headers=self.headers, files=files, data=data)
                if response.status_code == 201:  # 201 表示创建成功
                    print("文件上传成功")
                    return response.json().get("id")  # 获取上传的文件 ID
                else:
                    print(f"文件上传失败，状态码: {response.status_code}")
                    return None
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None

    def run_workflow(
        self,
        user,
        variable_name,
        file_flag,
        variable_value,
        file_type,
        response_mode="blocking",
    ):
        workflow_url = self.base_url + "workflows/run"
        if file_flag:
            template = {
                "transfer_method": "local_file",
                "upload_file_id": variable_value,
                "type": file_type,
            }
        else:
            template = variable_value

        data = {
            "inputs": {variable_name: template},
            "response_mode": response_mode,
            "user": user,
        }

        try:
            print("运行工作流...")
            response = requests.post(workflow_url, headers=self.headers, json=data)
            if response.status_code == 200:
                print("工作流执行成功")
                return response.json()
            else:
                print(f"工作流执行失败，状态码: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"Failed to execute workflow, status code: {response.status_code}",
                }
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return {"status": "error", "message": str(e)}


# 使用示例

# file_path = r"C:\Users\zyzhou23.IFLYTEK\Downloads\写出好的代码 -经验篇.md"
# user = "drbruce"
#
# test_dify = Dify("app-MgbOPD6ZYA6mSyip1w4h74wU")
#
# # 上传文件
# file_id = test_dify.upload_file(file_path, user)
# #file_id = "a17f9f77-4eb9-461b-a62c-1f302c806187"
# if file_id:
#     # 文件上传成功，继续运行工作流
#     result = test_dify.run_workflow(user, "input_files", True, file_id, "document")
#     print(result)
# else:
#     print("文件上传失败，无法执行工作流")
