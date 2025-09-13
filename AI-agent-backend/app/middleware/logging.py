# Copyright (c) 2025 左岚. All rights reserved.
"""
日志中间件
记录HTTP请求和响应日志，支持文件和数据库双重记录
"""

import json
import time
import traceback
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.log_config import log_config_manager
from app.utils.helpers import get_client_ip
from app.db.session import SessionLocal
from app.service.log_service import LogService

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件类
    记录HTTP请求和响应的详细信息，支持文件和数据库双重记录
    """

    def __init__(self, app, log_requests: bool = True, log_responses: bool = True,
                 log_to_db: bool = True):
        """
        初始化日志中间件

        Args:
            app: FastAPI应用
            log_requests: 是否记录请求日志
            log_responses: 是否记录响应日志
            log_to_db: 是否记录到数据库
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_to_db = log_to_db
    
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
            error_info = {
                "status_code": 500,
                "process_time": process_time,
                "error": str(e),
                "stack_trace": traceback.format_exc()
            }

            logger.error(
                f"Request failed: {request.method} {request.url}",
                extra={
                    "request_info": request_info,
                    "error": str(e),
                    "process_time": process_time
                }
            )

            # 记录错误到数据库
            if self.log_to_db:
                await self._log_error_to_database(request_info, error_info)

            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 获取响应信息
        response_info = self._extract_response_info(response, process_time)
        
        # 记录响应日志
        if self.log_responses:
            self._log_response(request_info, response_info)

        # 根据配置决定是否记录到数据库
        if self.log_to_db and log_config_manager.should_log_to_db("INFO"):
            await self._log_to_database(request_info, response_info)

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
        
        # 记录请求体信息（不读取实际内容以避免消耗body）
        if (content_type.startswith("application/json") and
            request.method in ["POST", "PUT", "PATCH"]):
            try:
                # 只记录content-length，不读取实际body内容
                content_length = request.headers.get("content-length")
                if content_length:
                    request_info["content_length"] = content_length
                    request_info["has_body"] = True
                else:
                    request_info["has_body"] = False
            except Exception as e:
                request_info["body_info_error"] = str(e)
        
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
        
        # 根据配置决定是否记录到文件
        if log_config_manager.should_log_to_file("INFO"):
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
        sensitive_fields = log_config_manager.get_sensitive_fields()
        
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

    async def _log_to_database(self, request_info: dict, response_info: dict) -> None:
        """
        将日志记录到数据库

        Args:
            request_info: 请求信息
            response_info: 响应信息
        """
        try:
            # 跳过健康检查和静态资源请求
            if self._should_skip_logging(request_info["path"]):
                return

            db: Session = SessionLocal()
            try:
                log_service = LogService(db)

                # 确定日志级别
                status_code = response_info["status_code"]
                if status_code >= 500:
                    level = "ERROR"
                elif status_code >= 400:
                    level = "WARNING"
                else:
                    level = "INFO"

                # 构建日志消息
                message = f"{request_info['method']} {request_info['path']} -> {status_code}"

                # 构建详细信息
                details = {
                    "request": self._filter_sensitive_data(request_info.copy()),
                    "response": response_info
                }

                # 创建日志记录
                log_service.create_log(
                    level=level,
                    module="http_middleware",
                    message=message,
                    ip_address=request_info.get("client_ip"),
                    user_agent=request_info.get("user_agent"),
                    request_method=request_info.get("method"),
                    request_url=request_info.get("url"),
                    details=json.dumps(details, ensure_ascii=False)
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Failed to log to database: {str(e)}")

    async def _log_error_to_database(self, request_info: dict, error_info: dict) -> None:
        """
        将错误日志记录到数据库

        Args:
            request_info: 请求信息
            error_info: 错误信息
        """
        try:
            db: Session = SessionLocal()
            try:
                log_service = LogService(db)

                # 构建错误消息
                message = f"Request failed: {request_info['method']} {request_info['path']}"

                # 构建详细信息
                details = {
                    "request": self._filter_sensitive_data(request_info.copy()),
                    "error": error_info
                }

                # 创建错误日志记录
                log_service.create_log(
                    level="ERROR",
                    module="http_middleware",
                    message=message,
                    ip_address=request_info.get("client_ip"),
                    user_agent=request_info.get("user_agent"),
                    request_method=request_info.get("method"),
                    request_url=request_info.get("url"),
                    details=json.dumps(details, ensure_ascii=False),
                    stack_trace=error_info.get("stack_trace")
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Failed to log error to database: {str(e)}")

    def _should_skip_logging(self, path: str) -> bool:
        """
        判断是否应该跳过日志记录

        Args:
            path: 请求路径

        Returns:
            是否跳过
        """
        return log_config_manager.should_skip_path(path)


def create_logging_middleware(log_requests: bool = True, log_responses: bool = True,
                            log_to_db: bool = True) -> LoggingMiddleware:
    """
    创建日志中间件实例

    Args:
        log_requests: 是否记录请求日志
        log_responses: 是否记录响应日志
        log_to_db: 是否记录到数据库

    Returns:
        日志中间件实例
    """
    return LoggingMiddleware(None, log_requests, log_responses, log_to_db)


# 导出日志中间件
__all__ = ["LoggingMiddleware", "create_logging_middleware"]
