"""
自定义FastAPI服务器

二次开发扩展层，封装LangGraph API
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router
from ..config import get_config
from ..database.db_manager import close_all_connections
from ..memory.manager import get_memory_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("Text2SQL API Server starting...")
    
    # 初始化配置
    config = get_config()
    
    # 初始化记忆管理器
    memory_manager = get_memory_manager()
    
    yield
    
    # 关闭时
    print("Text2SQL API Server shutting down...")
    
    # 关闭所有数据库连接
    close_all_connections()
    
    # 关闭记忆管理器
    memory_manager.close()


def create_app(
    title: str = "Text2SQL API",
    version: str = "0.1.0",
    debug: bool = False
) -> FastAPI:
    """创建FastAPI应用
    
    Args:
        title: API标题
        version: API版本
        debug: 是否开启调试模式
        
    Returns:
        FastAPI应用实例
    """
    app = FastAPI(
        title=title,
        version=version,
        description="智能自然语言到SQL转换API",
        lifespan=lifespan,
        debug=debug
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(router)
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    # 根路由
    @app.get("/")
    async def root():
        return {
            "name": title,
            "version": version,
            "docs": "/docs"
        }
    
    # 健康检查（根级别）
    @app.get("/ok")
    async def ok():
        return {"ok": True}
    
    return app


# 创建默认应用实例
app = create_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False
):
    """运行服务器
    
    Args:
        host: 主机地址
        port: 端口
        reload: 是否启用热重载
    """
    import uvicorn
    
    uvicorn.run(
        "text2sql.api.server:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    run_server(reload=True)
