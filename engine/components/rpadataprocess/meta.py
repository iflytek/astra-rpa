import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpadataprocess.data import DataProcess
from rpadataprocess.dataconvert import DataConvertProcess
from rpadataprocess.dict import DictProcess
from rpadataprocess.list import ListProcess
from rpadataprocess.math import MathProcess
from rpadataprocess.string import StringProcess
from rpadataprocess.time import TimeProcess


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(DataProcess, version=get_version())
    atomicMg.register(StringProcess, version=get_version())
    atomicMg.register(ListProcess, version=get_version())
    atomicMg.register(DictProcess, version=get_version())
    atomicMg.register(MathProcess, version=get_version())
    atomicMg.register(DataConvertProcess, version=get_version())
    atomicMg.register(TimeProcess, version=get_version())
    atomicMg.meta()
