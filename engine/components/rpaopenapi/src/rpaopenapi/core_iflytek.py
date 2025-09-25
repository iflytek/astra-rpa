import base64
import hashlib
import hmac
import json
import os
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import requests
from rpaopenapi.error import *

APPId = ""
APISecret = ""
APIKey = ""


class OcrRequests:
    """OCR请求封装"""

    @staticmethod
    def __parse_url__(url: str):
        """解析url"""

        st = url.index("://")
        host = url[st + 3 :]
        schema = url[: st + 3]
        ed = host.index("/")
        if ed <= 0:
            raise Exception("invalid request url:" + url)
        path = host[ed:]
        host = host[:ed]
        return host, path, schema

    @staticmethod
    def __assemble_ws_auth_url__(url: str, method="POST", api_key="", api_secret=""):
        """加密token"""

        host, path, schema = OcrRequests.__parse_url__(url)

        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        signature_sha = hmac.new(
            api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding="utf-8")
        authorization_origin = 'api_key="%s", algorithm="%s", headers="%s", signature="%s"' % (
            api_key,
            "hmac-sha256",
            "host date request-line",
            signature_sha,
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(encoding="utf-8")
        values = {"host": host, "date": date, "authorization": authorization}
        return url + "?" + urlencode(values)

    @staticmethod
    def request(method, url, **kwargs):
        """请求"""
        request_url = OcrRequests.__assemble_ws_auth_url__(url, "POST", APIKey, APISecret)
        return requests.request(method, request_url, **kwargs)


class OpenapiIflytek:
    """iflytek开放平台"""

    @staticmethod
    def template_ocr(header_dict: dict, files: list, type_code: str, url: str, key_name: str) -> list:
        results = []
        for image in files:
            with open(image, "rb") as f:
                image_bytes = f.read()
                image_info = base64.b64encode(image_bytes)
            suffix = os.path.splitext(image)[1].lstrip(".").lower()
            # 请求数据准备
            body = {
                "header": {"app_id": APPId, "status": 3},
                "parameter": {
                    key_name: {
                        "result": {
                            "encoding": "utf8",
                            "compress": "raw",
                            "format": "json",
                        },
                        "template_list": type_code,
                    }
                },
                "payload": {
                    f"{key_name}_data_1": {
                        "encoding": suffix,
                        "image": str(image_info, "UTF-8"),
                        "status": 3,
                    }
                },
            }
            headers = {
                "content-type": "application/json",
                "host": "api.xf-yun.com",
                "app_id": APPId,
            }
            # 发起请求
            ret = OcrRequests.request("POST", url, data=json.dumps(body), headers=headers)

            # 请求结果处理
            if ret.status_code != 200:
                raise BaseException(AI_SERVER_ERROR, "ai服务器无响应或错误 {}".format(ret))
            text = (
                base64.b64decode(ret.json()["payload"]["result"]["text"])
                .decode()
                .replace(" ", "")
                .replace("\n", "")
                .replace("\t", "")
                .strip()
            )
            if not text.endswith("}"):
                reverse_text = text[::-1]
                ind = reverse_text.find("}")
                real_ind = len(text) - ind
                text = text[:real_ind]
            ret_dict = json.loads(text)
            if ret_dict["error_code"] != 0:
                raise BaseException(
                    AI_REQ_ERROR_FORMAT.format(ret_dict["error_msg"]),
                    "ai服务请求异常 {}".format(ret_dict["error_msg"]),
                )
            if ret_dict["object_list"][0]["error_code"] != 0:
                raise BaseException(
                    AI_REQ_ERROR_FORMAT.format(ret_dict["object_list"][0]["error_msg"]),
                    "ai服务请求异常 {}".format(ret_dict["object_list"][0]["error_msg"]),
                )
            result_info = {}
            for region in ret_dict["object_list"][0]["region_list"]:
                key = region["text_block_list"][0]["key"]
                if not header_dict.get(key):
                    continue
                if region["text_block_list"][0]["value"]:
                    result_info[header_dict[key]] = region["text_block_list"][0]["value"]
            results.append(result_info)
        return results

    @staticmethod
    def common_ocr(header_dict: dict, files: list) -> list:
        results = []
        for image in files:
            with open(image, "rb") as f:
                image_bytes = f.read()
                image_info = base64.b64encode(image_bytes)
            suffix = os.path.splitext(image)[1].lstrip(".").lower()
            # 请求数据准备
            body = {"encoding": suffix, "image": str(image_info, "UTF-8"), "status": 3}
            url = "http://127.0.0.1:8003/api/rpa-ai-service/ocr/general"
            headers = {"content-type": "application/json"}
            # 发起请求
            ret = requests.request("POST", url, data=json.dumps(body), headers=headers)

            # 请求结果处理
            if ret.status_code != 200:
                raise BaseException(AI_SERVER_ERROR, "ai服务器无响应或错误 {}".format(ret))

            ret_dict = json.loads(base64.b64decode(ret.json()["payload"]["result"]["text"]).decode())
            content = OpenapiIflytek.__analyse_ocr_result__(ret_dict)
            ocr_result = {"Context": content}
            json_result = {}
            for k, v in ocr_result.items():
                if not header_dict.get(k):
                    continue
                json_result[header_dict[k]] = v
            results.append(json_result)
        return results

    @staticmethod
    def __analyse_ocr_result__(data: dict) -> str:
        """
        解析ocr返回的数据
        """
        try:
            lines = data["pages"][0]["lines"]
        except Exception:
            return ""
        # 处理单元格行数据，算出距离原点的位置并重组数据
        content = ""
        y = 0
        first = True
        for line in lines:
            if line.get("words") and line.get("coord"):
                # 如果两次line的y差值小于10，则认为是一行数据
                if not (y - 10 < line["coord"][0]["y"] < y + 10) and first is False:
                    content += "\n"
                for word in line["words"]:
                    content += word.get("content", "")
                first = False
                y = line["coord"][0]["y"]
        return content
