"""
API中间件

提供鉴权、日志等中间件
"""

import time
import uuid
from typing import Callable, Optional
from functools import wraps

from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware


# HTTP Bearer认证
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app, api_keys: list[str] = None, skip_paths: list[str] = None):
        """初始化认证中间件
        
        Args:
            app: FastAPI应用
            api_keys: 有效的API密钥列表
            skip_paths: 跳过认证的路径列表
        """
        super().__init__(app)
        self.api_keys = set(api_keys or [])
        self.skip_paths = skip_paths or ["/", "/ok", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过特定路径
        if any(request.url.path.startswith(p) for p in self.skip_paths):
            return await call_next(request)
        
        # 如果没有配置API密钥，跳过认证
        if not self.api_keys:
            return await call_next(request)
        
        # 检查Authorization头
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token in self.api_keys:
                return await call_next(request)
        
        # 检查X-API-Key头
        api_key = request.headers.get("X-API-Key", "")
        if api_key in self.api_keys:
            return await call_next(request)
        
        return Response(
            content='{"error": "Unauthorized", "error_code": "AUTH_REQUIRED"}',
            status_code=401,
            media_type="application/json"
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # 添加请求ID到state
        request.state.request_id = request_id
        
        # 记录请求
        print(f"[{request_id}] {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # 记录响应时间
        duration = (time.time() - start_time) * 1000
        print(f"[{request_id}] {response.status_code} ({duration:.2f}ms)")
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, list[float]] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用API Key
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"key:{api_key[:8]}"
        
        # 否则使用IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def _cleanup(self, client_id: str):
        """清理过期记录"""
        cutoff = time.time() - 60
        if client_id in self._requests:
            self._requests[client_id] = [
                t for t in self._requests[client_id] if t > cutoff
            ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_id = self._get_client_id(request)
        
        self._cleanup(client_id)
        
        # 检查限流
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        if len(self._requests[client_id]) >= self.requests_per_minute:
            return Response(
                content='{"error": "Rate limit exceeded", "error_code": "RATE_LIMITED"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        
        # 记录请求
        self._requests[client_id].append(time.time())
        
        response = await call_next(request)
        
        # 添加限流信息到响应头
        remaining = self.requests_per_minute - len(self._requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


# 依赖注入：验证API Key
async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """验证API Key依赖
    
    用法:
        @app.get("/protected")
        async def protected_route(api_key: str = Depends(verify_api_key)):
            ...
    """
    if credentials is None:
        return None
    return credentials.credentials


def require_api_key(valid_keys: list[str]):
    """要求API Key的装饰器工厂
    
    用法:
        @app.get("/protected")
        @require_api_key(["key1", "key2"])
        async def protected_route():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request:
                api_key = request.headers.get("X-API-Key", "")
                auth = request.headers.get("Authorization", "")
                
                if api_key in valid_keys:
                    return await func(*args, **kwargs)
                if auth.startswith("Bearer ") and auth[7:] in valid_keys:
                    return await func(*args, **kwargs)
            
            raise HTTPException(status_code=401, detail="Invalid API key")
        return wrapper
    return decorator
