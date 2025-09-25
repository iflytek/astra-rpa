import base64
import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Optional

import requests
from rpahelper.error import *


class Storage(ABC):
    @abstractmethod
    def global_list(self, project_id: str) -> list:
        """获取工程的全局变量"""
        pass

    @abstractmethod
    def element_detail(self, project_id: str, element_id: str) -> dict:
        """获取工程的元素数据详情"""
        pass


class HttpStorage(Storage):
    def __init__(self, gateway_port: str = None):
        self.gateway_port = gateway_port
        self.cache_element = {}
        self.cache_atomic_version = {}

    def __http__(
        self,
        shot_url: str,
        params: Optional[dict],
        data: Optional[dict],
        meta: str = "post",
    ) -> Any:
        """post 请求"""
        if meta == "post":
            response = requests.post(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url),
                json=data,
                params=params,
            )
        else:
            response = requests.get(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url),
                params=params,
            )
        if response.status_code != 200:
            raise BaseException(
                SERVER_ERROR_FORMAT.format(response.status_code),
                "服务器错误{}".format(response.status_code),
            )
        try:
            json_data = response.json()
        except JSONDecodeError:
            base64_encoded_data = base64.b64encode(response.content).decode("utf-8")
            return base64_encoded_data

        if json_data.get("code") != "0000" and json_data.get("code") != "000000":
            msg = json_data.get("message", "")
            raise BaseException(SERVER_ERROR_FORMAT.format(msg), "服务器错误{}".format(json_data))
        return json_data.get("data", {})

    def global_list(self, project_id: str) -> list:
        """获取工程的全局变量"""
        res = self.__http__("/api/robot/global/all", {"robotId": project_id}, None)
        if not res:
            return []
        return res

    def element_detail(self, project_id: str, element_id: str) -> dict:
        """获取工程的元素数据详情"""
        if element_id in self.cache_element:
            return self.cache_element[element_id]
        res = self.__http__(
            "/api/robot/element/detail",
            {"robotId": project_id, "elementId": element_id},
            None,
        )
        if not res:
            raise BaseException(ELEMENT_FAIL_GET_FORMAL.format(element_id), "元素获取异常 为空")

        # 处理元素的图片URL，将其转为base64编码保存到elementData中
        if res.get("imageUrl") or res.get("parentImageUrl"):
            element_data = json.loads(res.get("elementData"))
            if element_data.get("type", "web") == "web":
                # web不做处理
                pass
            else:
                # 只用处理桌面元素
                image_url = res.get("imageUrl", "")
                parent_image_url = res.get("parentImageUrl")
                if not image_url.endswith("fileId="):
                    image_base64 = self.__http__("/" + image_url, None, None, "get")
                else:
                    image_base64 = ""
                if parent_image_url and not parent_image_url.endswith("fileId="):
                    parent_image_base64 = self.__http__("/" + parent_image_url, None, None, "get")
                else:
                    parent_image_base64 = ""
                element_data["img"]["self"] = image_base64
                element_data["img"]["parent"] = parent_image_base64
                res.update({"elementData": json.dumps(element_data)})
        self.cache_element[element_id] = res
        return res
