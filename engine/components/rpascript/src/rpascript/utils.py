from typing import Optional

import requests
from rpaatomic.types import Any
from rpascript.error import *


def http_post(shot_url: str, gateway_port: str, data: Optional[dict]) -> Any:
    """post 请求"""

    response = requests.post("http://127.0.0.1:{}{}".format(gateway_port, shot_url), json=data)
    if response.status_code != 200:
        raise BaseException(
            SERVER_ERROR_FORMAT.format(response.status_code),
            "服务器错误{}".format(response.status_code),
        )
    json_data = response.json()
    if json_data.get("code") != BizCode.OK.value and json_data.get("code") != "000000":
        raise BaseException(
            SERVER_ERROR_FORMAT.format(json_data.get("message", "")),
            "服务器错误{}".format(json_data),
        )
    return json_data.get("data", {})
