import time
from typing import List, Union

from locator import ILocator
from locator.locator import locator
from rpaatomic.types import WinPick
from rpaframe.logger.logger import logger
from rpawinele.core import IWinEleCore
from rpawinele.error import *


class WinEleCore(IWinEleCore):
    @staticmethod
    def find(pick: WinPick, wait_time: float = 10.0) -> Union["ILocator", List["ILocator"]]:
        """
        find 查找 handle
        """
        # 防止重复获取
        if pick.locator is not None:
            return pick.locator

        res = None
        while wait_time >= 0:
            start = time.time()
            try:
                res = locator.locator(pick.get("elementData"))
                if isinstance(res, list):
                    break
                window_control = res.control()
                if window_control:
                    break
            except Exception as e:
                logger.warning("WinEleCore find error: {}".format(e))
                pass
            time.sleep(0.5)
            wait_time = wait_time - (time.time() - start)
        if wait_time < 0:
            raise BaseException(ELEMENT_NO_FOUND, "等待后未找到元素！")
        return res
