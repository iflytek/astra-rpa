from enum import Enum
from typing import Optional

import requests as requests

from .. import APP, IElement, PickerDomain, PickerType, Point, Rect
from ..logger import logger
from ..utils.cv import screenshot
from ..utils.process import get_process_name


class WEBElement(IElement):
    def __init__(self, web_info: dict, left_top_point: Point, app: APP, root_path=None):
        self.web_info = web_info
        self.left_top_point = left_top_point
        self.app = app
        self.root_path = root_path

        self.__rect = None  # 缓存 rect

    def rect(self) -> Rect:
        if self.__rect is None:
            rect = self.web_info["rect"]
            left = rect["x"] + self.left_top_point.x
            top = rect["y"] + self.left_top_point.y
            right = rect["right"] + self.left_top_point.x
            bottom = rect["bottom"] + self.left_top_point.y
            self.__rect = Rect(left, top, right, bottom)
        return self.__rect

    def tag(self) -> str:
        return self.web_info.get("tag", "")

    def path(self, svc=None, strategy_svc=None) -> dict:
        res = {
            "version": "1",
            "type": PickerDomain.WEB.value,
            "app": self.app.value,
            "path": self.web_info,
            "img": {"self": screenshot(self.rect())},
            "uiapath": [self.root_path],
        }
        pick_type = strategy_svc.data.get("pick_type")
        if pick_type == PickerType.SIMILAR:
            similar_path = WEBPicker.get_similar_path(svc.route_port, strategy_svc)
            if similar_path:
                res["path"] = similar_path
                data_dict = strategy_svc.data.get("data", {})
                img_dict = data_dict.get("img", {})
                res["img"]["self"] = img_dict.get("self", "")
        if pick_type == PickerType.BATCH:
            batch_path = WEBPicker.get_batch_path(svc.route_port, strategy_svc, self)
            if batch_path:
                res["path"] = batch_path
        return res


class BizCode(Enum):
    OK = "0000"
    ServerErr = "5001"
    ElemErr = "5002"
    ExecErr = "5003"


class WEBPicker:
    @classmethod
    def get_similar_path(cls, route_port: int, strategy_svc) -> Optional[dict]:
        url = f"http://127.0.0.1:{route_port}/browser_connector/browser/transition"
        payload = {
            "browser_type": strategy_svc.app.value,
            "data": strategy_svc.data.get("data", {}).get("path", []),
            "key": "similarElement",
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            resp_json = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("Failed to request connector: %s", exc)
            raise RuntimeError("Connector communication failed") from exc

        code = resp_json.get("code", "")
        if code != BizCode.OK.value:
            logger.error("Error from connector: %s", response.text)
            raise RuntimeError("Connector communication error")

        try:
            web_info = resp_json["data"]["data"]
            logger.info("检查返回数据: %s", resp_json)
        except (KeyError, TypeError) as exc:
            logger.warning("出现异常 %s, 返回: %s", exc, resp_json)
            if resp_json.get("data", {}).get("code", "") != BizCode.OK.value:
                raise RuntimeError(resp_json.get("data", {}).get("msg", "插件查找相似元素出错"))
            return None

        if resp_json.get("data", {}).get("code", "") != BizCode.OK.value:
            raise RuntimeError(resp_json.get("data", {}).get("msg", "插件查找相似元素出错"))

        return web_info or None

    @classmethod
    def get_batch_path(cls, route_port, strategy_svc, curr_ele: "WEBElement") -> Optional[dict]:
        url = "http://127.0.0.1:{}/browser_connector/browser/transition".format(route_port)
        try:
            # 表头抓取
            batch_type = strategy_svc.data.get("data", {}).get("path", {}).get("batchType")
            if batch_type == "head":
                data = {
                    "browser_type": strategy_svc.app.value,
                    "data": curr_ele.web_info,
                    "key": "tableHeaderBatch",
                }
                response = requests.post(url, json=data, timeout=3)
                return response.json()["data"]["data"]
            # 补充相似元素
            if batch_type == "similarAdd":
                data = {
                    "browser_type": strategy_svc.app.value,
                    "data": strategy_svc.data.get("data", {}).get("path"),
                    "key": "similarBatch",
                }
                response = requests.post(url, json=data, timeout=3)
                return response.json()["data"]["data"]
            # 是否是表格
            data = {
                "browser_type": strategy_svc.app.value,
                "data": curr_ele.web_info,
                "key": "elementIsTable",
            }
            response = requests.post(url, json=data, timeout=3)
            res_data = response.json()["data"]["data"]
            is_table = res_data["isTable"]
            # is_table = True 直接抓取两种元素， False 继续执行
            if is_table and batch_type != "similar":  # 表格元素且不以相似元素拾取
                # 抓取表格数据
                tdb_data = {
                    "browser_type": strategy_svc.app.value,
                    "data": res_data,
                    "key": "tableDataBatch",
                }
                tdb_response = requests.post(url, json=tdb_data, timeout=3)
                # 抓取表格列数据
                tcdb_data = {
                    "browser_type": strategy_svc.app.value,
                    "data": res_data,
                    "key": "tableColumnDataBatch",
                }
                tcdb_response = requests.post(url, json=tcdb_data, timeout=3)
                # 整合两种数据
                table_res_data = {
                    "isTable": is_table,
                    "tableData": tdb_response.json()["data"]["data"],
                    "tableColumnData": tcdb_response.json()["data"]["data"],
                }
                return table_res_data
            else:  # 普通元素
                data = {
                    "browser_type": strategy_svc.app.value,
                    "data": res_data,
                    "key": "similarBatch",
                }
                response = requests.post(url, json=data, timeout=3)
                return response.json()["data"]["data"]
        except Exception as e:
            raise Exception("插件响应出错", e)

    @classmethod
    def get_element(
        cls, root_control, route_port, strategy_svc, left_top_point: Point, **kwargs
    ) -> Optional[WEBElement]:
        url = "http://127.0.0.1:{}/browser_connector/browser/transition".format(route_port)
        data = {
            "browser_type": strategy_svc.app.value,
            "data": {
                "x": strategy_svc.last_point.x - left_top_point.x,
                "y": strategy_svc.last_point.y - left_top_point.y,
            },
            "key": "getElement",
        }
        response = requests.post(url, json=data, timeout=10)
        data = response.json()
        code = data.get("code", "")
        if code != BizCode.OK.value:
            logger.error("error: get_element {}".format(response.text))
            return None

        try:
            web_info = response.json()["data"]["data"]
            if not web_info:
                return None
        except Exception as e:
            logger.info(f"get_element获取输出出现异常{e}")
            return None

        pid = root_control.ProcessId
        app_name = get_process_name(pid)

        prev_control = None  # 用于保存根节点的子节点
        # 向上遍历直到根节点
        while True:
            parent = root_control.GetParentControl()
            if not parent:
                break
            prev_control = root_control  # 保存当前节点，作为根节点的子节点
            root_control = parent  # 向上移动

        root_control = prev_control

        root_path = {
            "cls": root_control.ClassName,
            "name": root_control.Name,
            "app": app_name,
            "tag_name": "WindowControl",
            "checked": True,
        }

        return WEBElement(
            web_info=web_info,
            left_top_point=left_top_point,
            app=strategy_svc.app,
            root_path=root_path,
        )


web_picker = WEBPicker()
