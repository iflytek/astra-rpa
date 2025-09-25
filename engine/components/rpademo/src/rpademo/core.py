from abc import ABC, abstractmethod


class IDemoCore(ABC):
    @staticmethod
    @abstractmethod
    def print(msg: str = "") -> str:
        pass

    @staticmethod
    @abstractmethod
    def create_and_open_txt(file_path: str, content: str = "helloworld") -> str:
        """
        在指定路径创建txt文件并写入内容，然后打开文件

        Args:
            file_path: 文件路径
            content: 要写入的内容，默认为"helloworld"

        Returns:
            操作结果信息
        """
        pass
