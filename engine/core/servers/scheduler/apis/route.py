from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..apis.connector import executor, picker, terminal, tools, ws
from ..core.lsp.routes import router as lsp_router
from ..core.svc import get_svc


def handler(app: FastAPI):
    # 添加全局中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 绑定tools路由
    app.include_router(tools.router, prefix="", tags=["tools"], dependencies=[Depends(get_svc)])

    # 绑定终端
    app.include_router(
        terminal.router,
        prefix="/terminal",
        tags=["terminal"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定执行器路由
    app.include_router(
        executor.router,
        prefix="/executor",
        tags=["executor"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定执行器路由
    app.include_router(
        picker.router,
        prefix="/picker",
        tags=["picker"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定全局ws
    app.include_router(ws.router, prefix="/ws", tags=["ws"], dependencies=[Depends(get_svc)])

    # 绑定lsp路由
    app.include_router(lsp_router, prefix="/lsp", tags=["lsp"], dependencies=[Depends(get_svc)])
