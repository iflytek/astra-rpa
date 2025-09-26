import toml
from rpaatomic.config import config
from rpaatomic.types import *


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config_type.yaml")

    typesMg.register_types(PATH, version=get_version(), channel="global", template="C://Users")
    typesMg.register_types(DIRPATH, version=get_version(), channel="global", template="C://Users")
    typesMg.register_types(Date, version=get_version(), channel="global", template="2025-01-10 17:00:00")
    typesMg.register_types(
        URL,
        version=get_version(),
        channel="global",
        template="https://www.iflytek.com/",
    )
    typesMg.register_types(Pick, version=get_version(), channel="", template="字典.")
    typesMg.register_types(WebPick, version=get_version(), channel="global", template="字典.")
    typesMg.register_types(WinPick, version=get_version(), channel="global", template="字典.")
    typesMg.register_types(IMGPick, version=get_version(), channel="global", template="字典.")
    typesMg.register_types(FeishuBaseInstance, version=get_version(), channel="", template="字典.")
    typesMg.register_types(DialogResult, version=get_version(), channel="", template="JSON字符串.")
    typesMg.register_types(Password, version=get_version(), channel="global", template="******")
    typesMg.meta()
