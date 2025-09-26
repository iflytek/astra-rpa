import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpaatomic.types import typesMg
from rpabrowser.browser import Browser
from rpabrowser.browser_element import BrowserElement
from rpabrowser.browser_script import BrowserScript
from rpabrowser.browser_software import BrowserSoftware


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    # config.default_value["atomic"] = {
    #     "icon": "icon-list-math-operation",
    # }
    config.set_config_file("config.yaml")
    atomicMg.register(BrowserElement, version=get_version())
    atomicMg.register(BrowserSoftware, version=get_version())
    atomicMg.register(BrowserScript, version=get_version())
    atomicMg.meta()

    config.set_config_file("config_type.yaml")
    typesMg.register_types(Browser, version=get_version(), channel="global", template="Browser对象")
    typesMg.meta()
