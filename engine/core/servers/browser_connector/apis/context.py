from dataclasses import dataclass
from typing import Union

from browser_connector.config import Config


@dataclass
class ServiceContext:
    config: Union[type[Config], None]

    def set_config(self, conf: type[Config]):
        self.config = conf


def gen_svc() -> ServiceContext:
    """
    生成svc
    """
    # 其他公共服务的初始化操作 比如数据库连接，redis连接，主要是为了保证单例，又比单例好
    return ServiceContext(
        config=None,
    )


def get_svc() -> ServiceContext:
    """
    获取全局svc
    """
    return _svc


_svc = gen_svc()
