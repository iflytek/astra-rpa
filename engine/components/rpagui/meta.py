import toml
from rpaatomic.atomic import atomicMg
from rpaatomic.config import config
from rpagui.gui_key import GuiKeyBoard
from rpagui.gui_mouse import GuiMouse


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(GuiKeyBoard, group_key="Gui", version=get_version())
    atomicMg.register(GuiMouse, group_key="Gui", version=get_version())
    atomicMg.meta()
