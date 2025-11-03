"""
自定义中间件
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from .logger import Logger
import uuid
import time


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    请求追踪中间件
    为每个请求生成或获取 trace_id，并在响应头中返回
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求，注入 trace_id
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            Response: 响应对象
        """
        # 从请求头获取 trace_id，如果没有则生成新的
        trace_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
        
        # 设置到 contextvars 中
        Logger.set_trace_id(trace_id)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger = Logger.get_logger(__name__)
        logger.info(f"请求开始: {request.method} {request.url.path}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 在响应头中添加 trace_id
            response.headers['X-Trace-ID'] = trace_id
            
            # 计算请求处理时间
            process_time = time.time() - start_time
            response.headers['X-Process-Time'] = str(process_time)
            
            # 记录请求完成信息
            logger.info(
                f"请求完成: {request.method} {request.url.path} - "
                f"状态码: {response.status_code} - 耗时: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # 记录异常
            logger.error(f"请求处理异常: {request.method} {request.url.path} - {e}", exc_info=True)
            raise
        finally:
            # 清除 trace_id（可选，contextvars 会自动处理上下文隔离）
            # Logger.clear_trace_id()
            pass


class CORSHeaderMiddleware(BaseHTTPMiddleware):
    """
    CORS 头部中间件（如果需要自定义 CORS 处理）
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加自定义 CORS 头部
        response.headers['Access-Control-Expose-Headers'] = 'X-Trace-ID, X-Process-Time'
        
        return response

