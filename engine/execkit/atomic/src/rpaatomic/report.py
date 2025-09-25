from abc import ABC, abstractmethod
from typing import Optional


class IReport(ABC):
    @abstractmethod
    def info(self, message):
        pass

    @abstractmethod
    def warning(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass


class SimpleReport(IReport):
    def __init__(self):
        self.code: Optional[IReport] = None

    def set_code(self, code: Optional[IReport]):
        self.code = code

    def info(self, message):
        if self.code:
            self.code.info(message)
        else:
            print(f"[S INFO] {message}")

    def warning(self, message):
        if self.code:
            self.code.warning(message)
        else:
            print(f"[S WARN] {message}")

    def error(self, message):
        if self.code:
            self.code.error(message)
        else:
            print(f"[S ERRO] {message}")


report = SimpleReport()
