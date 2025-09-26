import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpasystem.clipboard import Clipboard
from rpasystem.compress import Compress
from rpasystem.file import File
from rpasystem.folder import Folder
from rpasystem.process import Process
from rpasystem.system import System


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Clipboard, group_key="System", version=get_version())
    atomicMg.register(Compress, group_key="System", version=get_version())
    atomicMg.register(File, group_key="File", version=get_version())
    atomicMg.register(Folder, group_key="Folder", version=get_version())
    atomicMg.register(Process, group_key="System", version=get_version())
    atomicMg.register(System, group_key="System", version=get_version())
    atomicMg.meta()
