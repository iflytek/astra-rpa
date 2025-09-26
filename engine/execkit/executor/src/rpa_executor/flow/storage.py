import base64
import json
import platform
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Optional

import requests
from rpaatomic import ReportTip

from rpa_executor.error import *
from rpa_executor.flow.syntax.token import TokenType
from rpa_executor.logger import logger
from rpa_executor.tools import recording_tool

common_advanced = [
    {
        "key": "__res_print__",
        "types": "Bool",
        "title": "打印输出变量值",
        "name": "__res_print__",
    },
    {
        "key": "__delay_before__",
        "types": "Float",
        "title": "执行前延迟(秒)",
        "name": "__delay_before__",
    },
    {
        "key": "__delay_after__",
        "types": "Float",
        "title": "执行后延迟(秒)",
        "name": "__delay_after__",
    },
    {
        "key": "__skip_err__",
        "types": "Str",
        "title": "执行异常时",
        "name": "__skip_err__",
    },
    {
        "key": "__retry_time__",
        "types": "Int",
        "title": "重试次数(次)",
        "name": "__retry_time__",
    },
    {
        "key": "__retry_interval__",
        "types": "Float",
        "title": "重试间隔(秒)",
        "name": "__retry_interval__",
    },
]


def merge_dicts(flow, full_flow):
    keep_level_1 = ["title", "src"]
    keep_level_2 = ["inputList", "outputList"]
    keep_level_3 = ["types", "title", "name", "need_parse", "show"]

    flow["inputList"] = flow.get("inputList", []) + flow.get("advanced", []) + flow.get("exception", [])
    flow["advanced"] = flow["exception"] = []
    if "inputList" not in full_flow:
        full_flow["inputList"] = []
    full_flow["inputList"] += common_advanced

    def merge_obj(keep_list: list, c1: dict, c2: dict):
        for k in keep_list:
            if k in c2:
                c1[k] = c2[k]

    merge_obj(keep_level_1, flow, full_flow)

    for v in keep_level_2:
        if v in flow:
            full_flow_dict = {}
            for v2 in full_flow.get(v, []):
                full_flow_dict[v2.get("key", "")] = v2
            for v3 in flow.get(v):
                if v3.get("key", "") and v3.get("key") in full_flow_dict:
                    merge_obj(keep_level_3, v3, full_flow_dict[v3.get("key")])

    # 一些特殊处理
    if "inputList" in flow:
        for i in flow["inputList"]:
            if "name" not in i:
                i["name"] = i.get("key", "")
            if "title" not in i:
                i["title"] = i.get("name", "")
            if "types" not in i:
                i["types"] = "Any"
    return flow


class Storage(ABC):
    @abstractmethod
    def process_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的流程列表"""
        pass

    @abstractmethod
    def process_json(self, project_id: str, process_id: str, mode: str, version: str = "") -> list:
        """获取流程json"""
        pass

    @abstractmethod
    def global_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的全局变量"""
        pass

    @abstractmethod
    def param_list(self, project_id: str, process_id: str, mode: str, version: str = "") -> list:
        """获取工程的参数"""
        pass

    @abstractmethod
    def element_detail(self, project_id: str, element_id: str, mode: str, version: str = "") -> dict:
        """获取工程的元素数据详情"""
        pass

    @abstractmethod
    def module_detail(self, project_id: str, module_id: str, mode: str, version: str = "") -> str:
        """获取脚本数据"""
        pass

    @abstractmethod
    def user_pip_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的用户pip依赖详情"""
        pass

    @abstractmethod
    def component_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取组件列表"""
        pass

    @abstractmethod
    def atomic_version_list(self) -> list:
        """检测原子能力版本"""
        pass

    @abstractmethod
    def report_status_upload(self, result: str, reason: str):
        """上报状态"""
        pass

    @abstractmethod
    def get_remote_var_key(self) -> str:
        """获取远程参数的加密密钥"""
        pass

    @abstractmethod
    def get_remote_var_value(self, key: str) -> dict:
        """获取远程参数的只"""
        pass


class HttpStorage(Storage):
    def __init__(self, gateway_port: str = None, svc=None):
        self.svc = svc
        self.gateway_port = gateway_port
        self.cache_script_code = {}
        self.cache_element = {}
        self.cache_atomic_version = {}
        self.cache_remote_var_key = None
        self.cache_remote_var = {}

    def __http__(
        self,
        shot_url: str,
        params: Optional[dict],
        data: Optional[dict],
        meta: str = "post",
        has_code=True,
    ) -> Any:
        """post 请求"""
        cookies = {}
        logger.debug("请求开始 {}:{}:{}".format(shot_url, params, data))
        if meta == "post":
            response = requests.post(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url),
                json=data,
                cookies=cookies,
                params=params,
            )
        else:
            response = requests.get(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url),
                cookies=cookies,
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

        logger.debug("请求结束 {}:{}".format(shot_url, json_data))

        if has_code:
            if json_data.get("code") != BizCode.OK.value and json_data.get("code") != "000000":
                msg = json_data.get("message", "")
                raise BaseException(SERVER_ERROR_FORMAT.format(msg), "服务器错误{}".format(json_data))
            return json_data.get("data", {})
        else:
            return json_data

    def process_json_full(self, atom_list: list) -> list:
        if len(atom_list) == 0:
            return []

        res = self.__http__(
            "/api/robot/atom/getByVersionList",
            None,
            {
                "atomList": atom_list,
            },
        )
        return res

    def process_last_json_full(self, atom_list: list) -> list:
        if len(atom_list) == 0:
            return []
        res = self.__http__(
            "/api/robot/atom/getLatestAtomsByList",
            None,
            {
                "atomKeyList": atom_list,
            },
        )
        return res

    def process_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的流程列表"""

        params = {
            "robotId": project_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)

        return self.__http__("/api/robot/process/name-list", params, None)

    def process_json(self, project_id: str, process_id: str, mode: str, version: str = "") -> list:
        """获取流程json"""

        data = {
            "robotId": project_id,
            "processId": process_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/process/process-json", None, data)
        try:
            flow_list = json.loads(res)
        except Exception as e:
            raise BaseException(ENGINEERING_DATA_ERROR, "工程数据异常 {}".format(e))

        # 对flow_list做进一步处理
        atom_list = {}
        atom_key_list = []
        for flow in flow_list:
            if flow.get("key").startswith(TokenType.Component.value):
                continue
            atom_list["{}-{}".format(flow.get("key"), flow.get("version"))] = {
                "key": flow.get("key"),
                "version": flow.get("version"),
            }
            atom_key_list.append(flow.get("key"))

        last_full = self.process_last_json_full(atom_key_list)
        last_full_dict = {}
        for f in last_full:
            f = f.get("atomContent", "")
            if f:
                f = json.loads(f)
            last_full_dict[f.get("key")] = f.get("src")

        full = self.process_json_full(list(atom_list.values()))
        full_dict = {}
        for f in full:
            if f:
                f = json.loads(f)
            f["inputList"] = f.get("inputList", [])
            if "src" in f:
                f["src"] = last_full_dict.get(f.get("key"), f["src"])
            full_dict["{}-{}".format(f.get("key"), f.get("version"))] = f

        for k, flow in enumerate(flow_list):
            full_item = {}
            if "{}-{}".format(flow.get("key"), flow.get("version")) in full_dict:
                full_item = full_dict["{}-{}".format(flow.get("key"), flow.get("version"))]
            flow_list[k] = merge_dicts(flow, full_item)
        return flow_list

    def global_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的全局变量"""

        params = {
            "robotId": project_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)

        return self.__http__("/api/robot/global/all", params, None)

    def param_list(self, project_id: str, process_id: str, mode: str, version: str = "") -> list:
        """运行参数列表"""

        data = {
            "robotId": project_id,
            "processId": process_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/param/all", None, data)
        if res and isinstance(res, str):
            res = json.loads(res)
        return res

    def element_detail(self, project_id: str, element_id: str, mode: str, version: str = "") -> dict:
        """获取工程的元素数据详情"""
        if element_id in self.cache_element:
            return self.cache_element[element_id]
        params = {
            "robotId": project_id,
            "elementId": element_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)

        res = self.__http__("/api/robot/element/detail", params, None)
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
                    image_base64 = self.__http__(image_url, None, None, "get")
                else:
                    image_base64 = ""
                if parent_image_url and not parent_image_url.endswith("fileId="):
                    parent_image_base64 = self.__http__(parent_image_url, None, None, "get")
                else:
                    parent_image_base64 = ""
                element_data["img"]["self"] = image_base64
                element_data["img"]["parent"] = parent_image_base64
                res.update({"elementData": json.dumps(element_data, ensure_ascii=False)})
        self.cache_element[element_id] = res
        return res

    def module_detail(self, project_id: str, module_id: str, mode: str, version: str = "") -> str:
        if module_id in self.cache_script_code:
            return self.cache_script_code[module_id]

        data = {
            "robotId": project_id,
            "moduleId": module_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/module/open", None, data)
        if not (res and res.get("moduleContent", "")):
            raise BaseException(MODULE_FAIL_GET_FORMAL.format(module_id), "模块获取异常 为空")

        module = res.get("moduleContent", "")
        self.cache_element[module_id] = res
        return module

    def user_pip_list(self, project_id: str, mode: str, version: str = "") -> list:
        data = {
            "robotId": project_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        return self.__http__("/api/robot/require/list", None, data)

    def component_list(self, project_id: str, mode: str, version: str = "") -> list:
        params = {
            "robotId": project_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)
        return self.__http__("/api/robot/component-robot-use/component-use", None, params, meta="post")

    def atomic_version_list(self) -> dict:
        if self.cache_atomic_version:
            return self.cache_atomic_version
        plat = ""
        if platform.system() == "Linux":
            plat = "linux"
        res = self.__http__(
            "/api/rpa_update/v2/rpa_atom/pip_version?platform={}".format(plat),
            None,
            None,
            "get",
            False,
        )
        self.cache_atomic_version = res
        return res

    def report_status_upload(self, result: str, reason: str):
        """废弃：迁移到了scheduler中做上报，现在这里处理关系信息"""

        # 关闭日志
        if self.svc.recording_config.get("enable", False):
            if result == "fail":
                self.svc.report.info(ReportTip(msg_str=VIDEO_RECORDING_WAIT))
                recording_tool.close(False)
            elif result in ["success", "cancel"]:
                self.svc.report.info(ReportTip(msg_str=VIDEO_RECORDING_WAIT))
                recording_tool.close(True)
            elif result == "execute":
                pass

    def get_remote_var_key(self) -> str:
        if self.cache_remote_var_key is not None:
            return self.cache_remote_var_key

        res = self.__http__("/api/robot/robot-shared-var/shared-var-key", None, None, "get", True)
        self.cache_remote_var_key = res.get("key", "")
        return self.cache_remote_var_key

    def get_remote_var_value(self, key: str) -> dict:
        if key in self.cache_remote_var:
            return self.cache_remote_var[key]

        res = self.__http__(
            "/api/robot/robot-shared-var/get-batch-shared-var",
            None,
            {"ids": [key]},
            "post",
            True,
        )
        if res:
            self.cache_remote_var[key] = res[0]
        else:
            self.cache_remote_var[key] = None
        return self.cache_remote_var[key]
