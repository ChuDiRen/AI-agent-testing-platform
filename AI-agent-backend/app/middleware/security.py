# Copyright (c) 2025 左岚. All rights reserved.
"""
安全中间件
提供安全相关的中间件功能
"""

import time
import hashlib
from typing import Dict, Set
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 基础安全头
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
        }
        
        # HTTPS相关头（仅在启用HTTPS时添加）
        if settings.ENABLE_HTTPS or settings.is_production:
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # 增强的CSP策略
        csp_policy = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # 开发环境允许内联脚本
            "style-src 'self' 'unsafe-inline'",  # 允许内联样式
            "img-src 'self' data: https:",  # 允许图片从安全源加载
            "font-src 'self' https:",  # 允许字体从安全源加载
            "connect-src 'self' https: wss:",  # 允许API和WebSocket连接
            "media-src 'self'",
            "object-src 'none'",  # 禁止插件
            "base-uri 'self'",  # 限制base标签
            "form-action 'self'",  # 限制表单提交
            "frame-ancestors 'none'"  # 防止被嵌入iframe
        ]
        
        # 生产环境使用更严格的CSP
        if settings.is_production:
            csp_policy = [
                "default-src 'self'",
                "script-src 'self'",  # 生产环境禁止内联脚本
                "style-src 'self'",
                "img-src 'self' data: https:",
                "font-src 'self' https:",
                "connect-src 'self' https:",
                "media-src 'self'",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "frame-ancestors 'none'",
                "upgrade-insecure-requests"  # 强制HTTPS
            ]
        
        security_headers["Content-Security-Policy"] = "; ".join(csp_policy)
        
        # 添加请求ID用于追踪
        if "X-Request-ID" not in response.headers:
            import uuid
            response.headers["X-Request-ID"] = str(uuid.uuid4())
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        self.blocked_ips: Set[str] = set()
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """检查是否超过速率限制"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > minute_ago
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查请求数量
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return True
        
        # 记录当前请求
        self.requests[client_ip].append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        # 检查是否在黑名单中
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "IP已被封禁",
                    "error_code": "IP_BLOCKED"
                }
            )
        
        # 检查速率限制
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "请求过于频繁，请稍后再试",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            )
        
        return await call_next(request)
    
    def block_ip(self, ip: str):
        """封禁IP"""
        self.blocked_ips.add(ip)
        logger.info(f"Blocked IP: {ip}")
    
    def unblock_ip(self, ip: str):
        """解封IP"""
        self.blocked_ips.discard(ip)
        logger.info(f"Unblocked IP: {ip}")


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """请求验证中间件"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
        self.suspicious_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "eval(",
            "document.cookie",
            "window.location"
        ]
    
    def _check_suspicious_content(self, content: str) -> bool:
        """检查可疑内容"""
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in self.suspicious_patterns)
    
    async def dispatch(self, request: Request, call_next):
        # 检查请求大小
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request too large: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "message": "请求体过大",
                    "error_code": "REQUEST_TOO_LARGE"
                }
            )
        
        # 检查URL中的可疑内容
        url_str = str(request.url)
        if self._check_suspicious_content(url_str):
            logger.warning(f"Suspicious URL detected: {url_str}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "请求包含可疑内容",
                    "error_code": "SUSPICIOUS_REQUEST"
                }
            )
        
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(f"Suspicious User-Agent: {user_agent}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "无效的User-Agent",
                    "error_code": "INVALID_USER_AGENT"
                }
            )
        
        return await call_next(request)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF保护中间件"""
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or settings.SECRET_KEY
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
    
    def _generate_csrf_token(self, session_id: str) -> str:
        """生成CSRF令牌"""
        data = f"{session_id}:{self.secret_key}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _validate_csrf_token(self, token: str, session_id: str) -> bool:
        """验证CSRF令牌"""
        try:
            # 简单验证，实际应用中应该更复杂
            expected_token = self._generate_csrf_token(session_id)
            return token == expected_token
        except Exception:
            return False
    
    async def dispatch(self, request: Request, call_next):
        # 安全方法不需要CSRF保护
        if request.method in self.safe_methods:
            return await call_next(request)
        
        # 检查CSRF令牌
        csrf_token = request.headers.get("X-CSRF-Token")
        session_id = request.headers.get("X-Session-ID", "")
        
        if not csrf_token or not self._validate_csrf_token(csrf_token, session_id):
            logger.warning(f"CSRF token validation failed for {request.url}")
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "message": "CSRF令牌验证失败",
                    "error_code": "CSRF_TOKEN_INVALID"
                }
            )
        
        return await call_next(request)


# 导出中间件
__all__ = [
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware", 
    "RequestValidationMiddleware",
    "CSRFProtectionMiddleware"
]
