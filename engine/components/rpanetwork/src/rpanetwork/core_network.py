import json
import os

import requests
from rpanetwork.utils import is_json


class NetworkCore:
    @staticmethod
    def post_request(
        url: str = "",
        header: str = "",
        body: str = "",
        files: str = "",
        timeout: int = 60,
    ):
        file_arr = []
        headers = json.loads(header) if header else {}

        json_body = None
        if body:
            if is_json(body):
                json_body = json.loads(body)
                body = None
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"

        if files:
            files = json.loads(files)
            for key in files:
                value = files[key]
                basename = os.path.basename(value)
                with open(value, "rb") as f:
                    file_arr.append((key, (basename, f, "application/octet-stream")))

        try:
            res = requests.post(
                url=url,
                headers=headers,
                data=body,
                json=json_body,
                files=file_arr,
                timeout=timeout,
            )
            return res.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def get_request(url: str = "", header: str = "", timeout: int = 60):
        headers = json.loads(header) if header else {}

        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def connect_request(url: str = "", header: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60
        # 处理请求头
        headers = json.loads(header) if header else {}

        try:
            # 使用 requests.Session() 创建一个会话
            with requests.Session() as session:
                # 准备请求
                req = requests.Request("CONNECT", url, headers=headers)
                prepped = session.prepare_request(req)

                # 发送请求
                response = session.send(prepped, timeout=timeout)

                return response.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def head_request(url: str, header: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60

        # 处理请求头
        headers = json.loads(header) if header else {}

        try:
            # 发送 HEAD 请求
            response = requests.head(url, headers=headers, timeout=timeout)

            # 返回响应头
            return response.headers
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def put_request(url: str = "", header: str = "", body: str = "", timeout: int = 60):
        if timeout == "" or timeout is None:
            timeout = 60

        if header:
            header = json.loads(header)
        else:
            header = {}

        json_body = None
        if body:
            if is_json(body):
                json_body = json.loads(body)
            else:
                header["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            res = requests.put(url=url, headers=header, data=body, json=json_body, timeout=timeout)
            return res.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def delete_request(url: str, header: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60

        # 处理请求头
        headers = json.loads(header) if header else {}

        try:
            # 发送 DELETE 请求
            response = requests.delete(url, headers=headers, timeout=timeout)

            # 返回响应状态码和内容
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def options_request(url: str, header: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60

        # 处理请求头
        headers = json.loads(header) if header else {}

        try:
            # 发送 OPTIONS 请求
            response = requests.options(url, headers=headers, timeout=timeout)

            # 返回支持的请求方法和其他相关信息
            return response.headers.get("Allow")
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def trace_request(url: str, header: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60

        # 处理请求头
        headers = json.loads(header) if header else {}

        try:
            # 发送 TRACE 请求
            response = requests.request("TRACE", url, headers=headers, timeout=timeout)
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def patch_request(url: str = "", header: str = "", body: str = "", timeout: int = 60):
        # 设置默认超时时间
        timeout = timeout or 60

        headers = json.loads(header) if header else {}

        json_body = None
        if body:
            if is_json(body):
                json_body = json.loads(body)
                body = None
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            # 发送 PATCH 请求
            response = requests.patch(url, data=body, headers=headers, json=json_body, timeout=timeout)
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    @staticmethod
    def http_download(url: str = "", dst_path: str = ""):
        with requests.get(url=url, stream=True) as response:
            response.raise_for_status()
            with open(dst_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        return dst_path
