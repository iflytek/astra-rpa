from abc import ABC, abstractmethod


class IClipBoardCore(ABC):
    @staticmethod
    @abstractmethod
    def copy_str_clip(data: str = ""):
        pass

    @staticmethod
    @abstractmethod
    def copy_file_clip(file_path: str = ""):
        pass

    @staticmethod
    @abstractmethod
    def paste_str_clip() -> str:
        pass

    @staticmethod
    @abstractmethod
    def paste_file_clip() -> str:
        pass

    @staticmethod
    @abstractmethod
    def paste_html_clip() -> str:
        pass

    @staticmethod
    @abstractmethod
    def clear_clip():
        pass
