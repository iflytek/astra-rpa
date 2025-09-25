from typing import TYPE_CHECKING, Optional

from .. import WEB_CLASS_NAMES, IElement, Point
from ..engines.uia_picker import UIAOperate
from ..engines.web_picker import web_picker
from .types import StrategySvc

# 使用TYPE_CHECKING避免循环导入
if TYPE_CHECKING:
    from ..svc import ServiceContext


def web_default_strategy(service: "ServiceContext", strategy_svc: StrategySvc, cache=None) -> Optional[IElement]:
    """默认策略"""
    if cache:
        is_document, menu_top, menu_left, hwnd = cache
    else:
        web_control_result = UIAOperate().get_web_control(strategy_svc.start_control, WEB_CLASS_NAMES[strategy_svc.app])
        is_document, menu_top, menu_left, hwnd = web_control_result
    if not is_document:
        return None
    ele = web_picker.get_element(
        root_control=strategy_svc.start_control,
        route_port=service.route_port,
        strategy_svc=strategy_svc,
        left_top_point=Point(menu_left, menu_top),
    )
    return ele
