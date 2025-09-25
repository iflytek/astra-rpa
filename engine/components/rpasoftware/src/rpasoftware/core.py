from abc import ABC, abstractmethod


class ISoftwareCore(ABC):
    @staticmethod
    @abstractmethod
    def get_app_path(app_name: str = "") -> str:
        pass
