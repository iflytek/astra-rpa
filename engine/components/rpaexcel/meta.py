import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpaatomic.types import typesMg
from rpaexcel.excel import Excel
from rpaexcel.excel_obj import ExcelObj


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Excel, version=get_version())
    atomicMg.meta()

    config.set_config_file("config_type.yaml")
    typesMg.register_types(ExcelObj, version=get_version(), channel="global", template="Excel对象")
    typesMg.meta()
