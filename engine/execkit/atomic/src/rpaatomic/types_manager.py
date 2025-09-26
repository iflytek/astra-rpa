import json
from functools import wraps
from typing import Any

from rpaatomic import TypeFuncMeta, TypesMeta
from rpaatomic.config import config


class TypesManager:
    def __init__(self):
        self.register_dict: dict = {}
        self.shortcut_dict: dict = {}

    def register_types(
        self,
        cls: Any,
        group_key: str = None,
        desc: str = None,
        version: str = "1",
        **kwargs,
    ):
        """注入到类型"""
        # group_key
        if not group_key:
            group_key = cls.__name__
        # desc
        if not desc:
            desc = cls.__name__
        # src
        src = "{}.{}()".format(cls.__module__, cls.__name__)
        if cls.__module__ == "rpaatomic.types":
            src = ""
        self.register_dict[group_key] = TypesMeta(key=group_key, desc=desc, src=src, version=version, **kwargs).__dict__

    def shortcut(
        self,
        group_key: str,
        res_type: str,
        func_desc: str = None,
        res_desc: str = None,
        src: str = None,
    ):
        """快捷方法"""

        def real_shortcut(func):
            nonlocal group_key, res_type, func_desc, res_desc, src
            # key
            key = "{}.{}".format(group_key, func.__name__)
            # func_desc
            if not func_desc:
                func_desc = func.__name__
            # src
            if not src:
                src = r"@{}.{}()".format("{self:self}", func.__name__)
            self.shortcut_dict[key] = TypeFuncMeta(
                key=key,
                funcDesc=func_desc,
                resType=res_type,
                resDesc=res_desc,
                useSrc=src,
            ).__dict__

            @wraps(func)
            def wrapper(*args, **war_kwargs):
                return func(*args, **war_kwargs)

            wrapper.__tag_key__ = "shortcut"  # 标记
            return wrapper

        return real_shortcut

    def json(self):
        """meta_type.json"""

        json_data = config.get("types")

        temp_register_dict = {}
        for k, v in self.register_dict.items():
            temp_register_dict[k] = v
            if k in json_data:
                if json_data[k].get("key", None):
                    temp_register_dict[k]["key"] = json_data[k].get("key", None)
                if json_data[k].get("src", None):
                    temp_register_dict[k]["src"] = json_data[k].get("src", None)
                if json_data[k].get("desc", None):
                    temp_register_dict[k]["desc"] = json_data[k].get("desc", None)
                if json_data[k].get("version", None):
                    temp_register_dict[k]["version"] = json_data[k].get("version", None)
            if temp_register_dict[k].get("funcList", None) is None:
                temp_register_dict[k]["funcList"] = []

        for k, v in self.shortcut_dict.items():
            group_key = v.get("key", "").split(".")[0]
            if group_key not in temp_register_dict:
                continue

            if v.get("resDesc", None) is None:
                v["resDesc"] = json_data.get(v["resType"], {}).get("desc", None)
            if group_key in json_data:
                oldList = json_data[group_key].get("funcList", [])
            else:
                oldList = []
            has = False
            for ok, ov in enumerate(oldList):
                if v.get("key", None) == ov.get("key", None) and v.get("key", None) is not None:
                    has = True
                    v.update(ov)
                    temp_register_dict[group_key]["funcList"].insert(ok, v)
                    break
            if not has:
                temp_register_dict[group_key]["funcList"].append(v)
        return json.dumps(temp_register_dict, ensure_ascii=False)

    def meta(self):
        data = self.json()
        file = "meta_type.json"
        with open(file, "w", encoding="utf-8") as file:
            file.write(data)
        return file
