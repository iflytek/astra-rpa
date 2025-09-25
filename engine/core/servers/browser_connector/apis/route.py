from browser_connector.apis import ws_route
from browser_connector.apis.browser.v1 import browser
from browser_connector.apis.context import get_svc
from browser_connector.apis.response import http_base_exception, http_exception
from browser_connector.error import BaseException
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


def handler(app: FastAPI):
    # 添加全局错误处理
    app.add_exception_handler(BaseException, http_base_exception)
    app.add_exception_handler(Exception, http_exception)

    # 添加全局中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 绑定websocket路由
    app.include_router(ws_route.router, prefix="/ws", tags=["ws"], dependencies=[Depends(get_svc)])

    # 绑定http路由
    app.include_router(
        browser.router,
        prefix="/browser",
        tags=["browser"],
        dependencies=[Depends(get_svc)],
    )
