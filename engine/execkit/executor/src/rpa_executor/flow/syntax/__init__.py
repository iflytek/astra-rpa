from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from rpa_executor.flow.syntax.environment import Environment
from rpa_executor.flow.syntax.token import Token


class Job(ABC):
    @abstractmethod
    def init(self, t: Token, cache_dir: str):
        pass

    @abstractmethod
    def download(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, t: Token, svc, env: Environment, params: dict = None) -> Any:
        pass


@dataclass
class InputParam:
    types: str
    key: str
    value: Any
    # 是否需要执行
    need_eval: bool
    # 特殊处理处理
    special: str = None


@dataclass
class OutputParam:
    types: str
    value: str
    special: str = None
