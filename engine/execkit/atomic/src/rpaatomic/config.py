import os

from rpaatomic.error import *


class Config:
    """读取配置"""

    data: dict = {}
    default_value: dict = {}

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.set_config_file(os.path.join(script_dir, "config.yaml"))

    def set_config_file(self, url, file_type="yaml"):
        with open(url, encoding="utf-8") as yaml_file:
            if file_type == "yaml":
                import yaml

                try:
                    data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                except Exception as e:
                    raise BaseException(
                        CONFIG_LOAD_ERROR.format(yaml_file),
                        "配置文件加载出错 {}".format(e),
                    ) from e
            else:
                raise BaseException(
                    CONFIG_TYPE_ERROR.format(file_type),
                    "配置文件解析不支持该类型 {}".format(file_type),
                )

        if not data or not isinstance(data, dict):
            return

        for key, val in data.items():
            if key in self.data:
                self.data[key].update(val)
            else:
                self.data[key] = val

        # 设置默认值
        for key, val in data.items():
            if key not in self.default_value:
                continue
            for k, v in val.items():
                if key not in self.default_value:
                    continue
                for d, dv in self.default_value[key].items():
                    if v.get(d) is None or v.get(d) == "":
                        data[key][k][d] = dv

    def get(self, *args):
        data = self.data
        for key in args:
            if data is None:
                break
            data = data.get(key, None)
        return data


config = Config()
