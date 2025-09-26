import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpaemail.email import Email


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Email, version=get_version())
    atomicMg.meta()
