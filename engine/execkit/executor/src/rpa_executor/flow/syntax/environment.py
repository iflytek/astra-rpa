import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class EnvBizTypes(Enum):
    Env = "Env"  # 环境变量
    Global = "Global"  # 全局变量(用户定义)
    Flow = "Flow"  # 流变量(原子能力)
    Other = "Other"  # 其他(非原子能力返回值的流变量，...)


@dataclass
class EnvItem:
    biz_types: EnvBizTypes = EnvBizTypes.Other
    types: str = "Any"
    project_id: str = ""
    key: str = ""
    value: Any = None
    ext: dict = None


class Environment:
    def __init__(self, outer: "Environment" = None):
        self.lock = threading.Lock()
        self.store: dict[str, EnvItem] = {}
        self.g_store: dict[str, EnvItem] = {}
        self.outer: Environment = outer

    def in_global(self, project_id, key: str) -> bool:
        """判断是否是全局变量"""
        k = "{}_{}".format(project_id, key)
        if k in self.g_store:
            return True

    def get_global(self, project_id):
        res = {value.key: value for _, value in self.g_store.items() if value.project_id == project_id}
        return res

    def getitem(self, project_id, name: str) -> Optional[EnvItem]:
        if name in self.store:
            return self.store[name]
        if self.outer:
            return self.outer.getitem(project_id, name)
        else:
            if self.in_global(project_id, name):
                k = "{}_{}".format(project_id, name)
                return self.g_store[k]
        return None

    def setitem(self, project_id, name: str, val: EnvItem) -> None:
        with self.lock:
            # 只能设置当前的
            if val.biz_types in [EnvBizTypes.Env, EnvBizTypes.Global]:
                val.project_id = project_id
                k = "{}_{}".format(project_id, name)
                self.g_store[k] = val
            else:
                self.store[name] = val

    def delitem(self, name: str) -> None:
        # 只能删除当前的
        if name in self.store:
            del self.store[name]

    def to_dict(self, project_id, first_time=True) -> dict:
        """变量转换成 eval 可识别的dict"""

        result = {key: value.value for key, value in self.store.items()}
        if self.outer:
            outer_dict = self.outer.to_dict(project_id, False)
            outer_dict.update(result)
            result = outer_dict
        if first_time:
            g_result = {value.key: value.value for _, value in self.g_store.items() if value.project_id == project_id}
            g_result.update(result)
            result = g_result
        return result

    def to_json_dict(self, project_id, first_time=True) -> dict:
        """变量转换成 前端展示的内容"""

        result = {
            key: {"value": str(value.value), "types": value.types}
            for key, value in self.store.items()
            if not key.startswith("_") and value.biz_types in [EnvBizTypes.Global, EnvBizTypes.Flow]
        }
        if self.outer:
            outer_dict = self.outer.to_dict(project_id, False)
            outer_dict.update(result)
            result = outer_dict
        if first_time:
            g_result = {
                value.key: {"value": str(value.value), "types": value.types}
                for _, value in self.g_store.items()
                if not value.key.startswith("_")
                and value.biz_types in [EnvBizTypes.Global, EnvBizTypes.Flow]
                and value.project_id == project_id
            }
            g_result.update(result)
            result = g_result
        return result

    def sync_with_dict(self, project_id, other_dict: dict, biz_types=EnvBizTypes.Other) -> None:
        """将eval执行后的dict 更新到全局里面"""

        current_dict = self.to_dict(project_id)
        diff = {
            key: other_dict[key]
            for key in other_dict
            if key not in current_dict or other_dict[key] != current_dict[key]
        }
        for key, value in diff.items():
            res = self.getitem(project_id, key)
            if res:
                res.value = value
            else:
                self.setitem(
                    project_id,
                    key,
                    EnvItem(biz_types=biz_types, types="Any", key=key, value=True),
                )

    def new_enclose_environment(self) -> "Environment":
        """创建一个局部的环境"""

        env = Environment()
        env.outer = self
        env.g_store = self.g_store
        return env

    def new_process_environment(self) -> "Environment":
        """创意一个import的环境"""

        env = Environment()
        env.outer = None
        env.g_store = self.g_store
        return env
