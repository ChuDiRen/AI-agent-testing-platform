"""
日志中间件
记录HTTP请求和响应日志
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_logger
from app.utils.helpers import get_client_ip

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件类
    记录HTTP请求和响应的详细信息
    """
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        """
        初始化日志中间件
        
        Args:
            app: FastAPI应用
            log_requests: 是否记录请求日志
            log_responses: 是否记录响应日志
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理HTTP请求和响应
        
        Args:
            request: HTTP请求
            call_next: 下一个处理函数
            
        Returns:
            HTTP响应
        """
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        request_info = await self._extract_request_info(request)
        
        # 记录请求日志
        if self.log_requests:
            self._log_request(request_info)
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url}",
                extra={
                    "request_info": request_info,
                    "error": str(e),
                    "process_time": process_time
                }
            )
            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 获取响应信息
        response_info = self._extract_response_info(response, process_time)
        
        # 记录响应日志
        if self.log_responses:
            self._log_response(request_info, response_info)
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    async def _extract_request_info(self, request: Request) -> dict:
        """
        提取请求信息
        
        Args:
            request: HTTP请求
            
        Returns:
            请求信息字典
        """
        # 获取客户端IP
        client_ip = get_client_ip(request)
        
        # 获取用户代理
        user_agent = request.headers.get("User-Agent", "")
        
        # 获取请求ID（如果有）
        request_id = request.headers.get("X-Request-ID", "")
        
        # 获取认证信息
        authorization = request.headers.get("Authorization", "")
        has_auth = bool(authorization)
        
        # 获取内容类型
        content_type = request.headers.get("Content-Type", "")
        
        # 获取请求体大小
        content_length = request.headers.get("Content-Length", "0")
        
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_id": request_id,
            "has_auth": has_auth,
            "content_type": content_type,
            "content_length": content_length,
            "headers": dict(request.headers)
        }
        
        # 记录请求体（仅对特定内容类型）
        if (content_type.startswith("application/json") and 
            request.method in ["POST", "PUT", "PATCH"]):
            try:
                body = await request.body()
                if body:
                    # 限制日志中的请求体大小
                    if len(body) <= 1024:  # 1KB
                        request_info["body"] = body.decode("utf-8")
                    else:
                        request_info["body"] = f"<body too large: {len(body)} bytes>"
            except Exception as e:
                request_info["body_error"] = str(e)
        
        return request_info
    
    def _extract_response_info(self, response: Response, process_time: float) -> dict:
        """
        提取响应信息
        
        Args:
            response: HTTP响应
            process_time: 处理时间
            
        Returns:
            响应信息字典
        """
        response_info = {
            "status_code": response.status_code,
            "process_time": process_time,
            "headers": dict(response.headers)
        }
        
        # 获取响应体大小
        content_length = response.headers.get("Content-Length")
        if content_length:
            response_info["content_length"] = content_length
        
        return response_info
    
    def _log_request(self, request_info: dict) -> None:
        """
        记录请求日志
        
        Args:
            request_info: 请求信息
        """
        # 过滤敏感信息
        filtered_info = self._filter_sensitive_data(request_info.copy())
        
        logger.info(
            f"Request: {request_info['method']} {request_info['path']}",
            extra={"request": filtered_info}
        )
    
    def _log_response(self, request_info: dict, response_info: dict) -> None:
        """
        记录响应日志
        
        Args:
            request_info: 请求信息
            response_info: 响应信息
        """
        # 确定日志级别
        status_code = response_info["status_code"]
        if status_code >= 500:
            log_level = "error"
        elif status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
        
        # 记录日志
        log_message = (
            f"Response: {request_info['method']} {request_info['path']} "
            f"-> {status_code} ({response_info['process_time']:.3f}s)"
        )
        
        log_data = {
            "request": self._filter_sensitive_data(request_info.copy()),
            "response": response_info
        }
        
        getattr(logger, log_level)(log_message, extra=log_data)
    
    def _filter_sensitive_data(self, data: dict) -> dict:
        """
        过滤敏感数据
        
        Args:
            data: 原始数据
            
        Returns:
            过滤后的数据
        """
        sensitive_fields = [
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "password", "token", "secret", "key"
        ]
        
        # 过滤请求头中的敏感信息
        if "headers" in data:
            filtered_headers = {}
            for key, value in data["headers"].items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    filtered_headers[key] = "***FILTERED***"
                else:
                    filtered_headers[key] = value
            data["headers"] = filtered_headers
        
        # 过滤请求体中的敏感信息
        if "body" in data and isinstance(data["body"], str):
            try:
                body_data = json.loads(data["body"])
                if isinstance(body_data, dict):
                    for field in sensitive_fields:
                        if field in body_data:
                            body_data[field] = "***FILTERED***"
                    data["body"] = json.dumps(body_data)
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，保持原样
                pass
        
        return data


def create_logging_middleware(log_requests: bool = True, log_responses: bool = True) -> LoggingMiddleware:
    """
    创建日志中间件实例
    
    Args:
        log_requests: 是否记录请求日志
        log_responses: 是否记录响应日志
        
    Returns:
        日志中间件实例
    """
    return LoggingMiddleware(None, log_requests, log_responses)


# 导出日志中间件
__all__ = ["LoggingMiddleware", "create_logging_middleware"]
