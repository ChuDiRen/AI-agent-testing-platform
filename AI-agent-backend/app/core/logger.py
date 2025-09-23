"""
日志配置模块
使用loguru进行日志管理
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from loguru import logger

from app.core.config import settings


def setup_logging():
    """
    设置日志配置
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 确保日志目录存在
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 为避免多进程冲突，在日志文件名中包含进程ID
    log_file_path = Path(settings.LOG_FILE)
    process_log_file = log_file_path.parent / f"{log_file_path.stem}_{os.getpid()}{log_file_path.suffix}"
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 添加文件处理器
    logger.add(
        str(process_log_file),
        format=file_format,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
        enqueue=True,  # 使用队列避免多进程冲突
        catch=True     # 捕获日志记录过程中的异常
    )
    
    # 添加错误日志文件处理器
    error_log_file = str(Path(settings.LOG_FILE).parent / f"error_{os.getpid()}.log")
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
        enqueue=True,  # 使用队列避免多进程冲突
        catch=True     # 捕获日志记录过程中的异常
    )


def get_logger(name: str = None):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    if name:
        return logger.bind(name=name)
    return logger


def get_access_logger():
    """获取访问日志记录器"""
    return logger.bind(type="access")


def get_audit_logger():
    """获取审计日志记录器"""
    return logger.bind(type="audit")


def get_performance_logger():
    """获取性能日志记录器"""
    return logger.bind(type="performance")


def log_request(method: str, url: str, status_code: int, 
                response_time: float, user_id: int = None, 
                user_agent: str = None, ip: str = None):
    """
    记录HTTP请求访问日志
    """
    access_logger = get_access_logger()
    access_logger.info(
        "HTTP Request",
        method=method,
        url=url,
        status_code=status_code,
        response_time_ms=round(response_time * 1000, 2),
        user_id=user_id,
        user_agent=user_agent,
        client_ip=ip
    )


def log_audit(action: str, resource: str, user_id: int, 
              user_name: str = None, details: Dict[str, Any] = None,
              ip: str = None, success: bool = True):
    """
    记录审计日志
    """
    audit_logger = get_audit_logger()
    audit_logger.info(
        "Audit Log",
        action=action,
        resource=resource,
        user_id=user_id,
        user_name=user_name,
        details=details or {},
        client_ip=ip,
        success=success,
        timestamp=datetime.utcnow().isoformat()
    )


def log_performance(operation: str, duration: float, 
                   details: Dict[str, Any] = None):
    """
    记录性能日志
    """
    if settings.is_production:
        perf_logger = get_performance_logger()
        perf_logger.info(
            "Performance Log",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            details=details or {}
        )


def log_security_event(event_type: str, severity: str, 
                      details: Dict[str, Any] = None,
                      ip: str = None, user_id: int = None):
    """
    记录安全事件
    """
    security_logger = logger.bind(type="security")
    security_logger.warning(
        f"Security Event: {event_type}",
        event_type=event_type,
        severity=severity,
        details=details or {},
        client_ip=ip,
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat()
    )


class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, **context):
        self.context = context
        self.token = None
    
    def __enter__(self):
        self.token = logger.contextualize(**self.context)
        return self.token
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            self.token.__exit__(exc_type, exc_val, exc_tb)


# 便捷上下文管理器
def with_context(**context):
    """创建带上下文的日志"""
    return LogContext(**context)


# 初始化日志配置
setup_logging()

# 记录应用启动
logger.info(
    "Logging system initialized",
    log_level=settings.LOG_LEVEL,
    environment=settings.ENVIRONMENT,
    debug_mode=settings.DEBUG
)

# 导出日志记录器
__all__ = [
    "get_logger", "logger", "get_access_logger", "get_audit_logger", 
    "get_performance_logger", "log_request", "log_audit", "log_performance",
    "log_security_event", "with_context", "LogContext"
]
