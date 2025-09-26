import os.path
import sys

from rpaai.agent import Agent
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
print(os.path.dirname(os.path.abspath(__file__)))

import toml
from rpaai.chat import ChatAI
from rpaai.contract import ContractAI
from rpaai.document import DocumentAI
from rpaai.recruit import RecruitAI


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.default_value["atomic"] = {
        "icon": "icon-list-math-operation",
    }
    config.set_config_file("config.yaml")
    atomicMg.register(ChatAI, version=get_version())
    atomicMg.register(DocumentAI, version=get_version())
    atomicMg.register(Agent, version=get_version())
    atomicMg.register(RecruitAI, version=get_version())
    atomicMg.register(ContractAI, version=get_version())
    atomicMg.meta()
