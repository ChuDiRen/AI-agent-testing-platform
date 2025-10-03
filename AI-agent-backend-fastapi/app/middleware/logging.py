"""请求日志中间件"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.log import OperationLog


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # 获取当前用户信息（如果已认证）
        user_id = None
        username = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
            username = request.state.user.username
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录日志到数据库（异步）
        if not path.startswith("/docs") and not path.startswith("/openapi"):
            try:
                async with AsyncSessionLocal() as db:
                    log = OperationLog(
                        user_id=user_id,
                        username=username,
                        action=f"{method} {path}",
                        method=method,
                        path=path,
                        ip_address=client_host,
                        user_agent=user_agent,
                        response_status=response.status_code
                    )
                    db.add(log)
                    await db.commit()
            except Exception as e:
                print(f"Failed to log request: {e}")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

