# -*- coding: utf-8 -*-
"""
自定义异常类和异常处理规范

✅ P2修复: 规范化异常处理,避免过于宽泛的Exception捕获
"""
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


# ==================== 自定义异常基类 ====================

class PlatformBaseException(Exception):
    """平台基础异常类"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


# ==================== 业务异常 ====================

class BusinessException(PlatformBaseException):
    """业务逻辑异常 - 可恢复的业务错误"""
    pass


class ValidationException(BusinessException):
    """数据验证异常"""
    pass


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    pass


class PermissionDeniedException(BusinessException):
    """权限拒绝异常"""
    pass


class DuplicateResourceException(BusinessException):
    """资源重复异常"""
    pass


# ==================== 技术异常 ====================

class TechnicalException(PlatformBaseException):
    """技术异常 - 系统级错误"""
    pass


class DatabaseException(TechnicalException):
    """数据库异常"""
    pass


class ExternalServiceException(TechnicalException):
    """外部服务异常"""
    pass


class ConfigurationException(TechnicalException):
    """配置异常"""
    pass


class QueueException(TechnicalException):
    """消息队列异常"""
    pass


# ==================== 异常处理工具函数 ====================

def handle_exception(exc: Exception, default_message: str = "操作失败") -> dict:
    """
    统一异常处理
    
    Args:
        exc: 异常对象
        default_message: 默认错误消息
        
    Returns:
        错误响应字典
    """
    # 业务异常 - 记录警告级别日志
    if isinstance(exc, BusinessException):
        logger.warning(f"业务异常: {exc.message}", exc_info=False)
        return {
            "success": False,
            "message": exc.message,
            "code": exc.code
        }
    
    # 技术异常 - 记录错误级别日志
    if isinstance(exc, TechnicalException):
        logger.error(f"技术异常: {exc.message}", exc_info=True)
        return {
            "success": False,
            "message": "系统错误,请稍后重试",
            "code": exc.code
        }
    
    # 未知异常 - 记录严重级别日志
    logger.critical(f"未知异常: {str(exc)}", exc_info=True)
    return {
        "success": False,
        "message": default_message,
        "code": "INTERNAL_ERROR"
    }


# ==================== 异常处理装饰器 ====================

def exception_handler(default_message: str = "操作失败"):
    """
    异常处理装饰器
    
    使用示例:
        @exception_handler("用户创建失败")
        def create_user(data):
            # 业务逻辑
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BusinessException as e:
                logger.warning(f"业务异常 [{func.__name__}]: {e.message}")
                raise
            except TechnicalException as e:
                logger.error(f"技术异常 [{func.__name__}]: {e.message}", exc_info=True)
                raise
            except Exception as e:
                logger.critical(f"未知异常 [{func.__name__}]: {str(e)}", exc_info=True)
                raise TechnicalException(default_message, details=str(e))
        return wrapper
    return decorator


# ==================== 异常处理最佳实践 ====================

"""
异常处理规范:

1. 分层捕获异常:
   ✅ 正确:
   try:
       # 业务逻辑
   except ValueError as e:
       # 处理特定的值错误
   except SQLAlchemyError as e:
       # 处理数据库错误
   except Exception as e:
       # 处理未知错误
   
   ❌ 错误:
   try:
       # 业务逻辑
   except Exception as e:
       # 一刀切

2. 记录完整堆栈:
   ✅ 正确:
   logger.error(f"操作失败: {e}", exc_info=True)
   
   ❌ 错误:
   logger.error(f"操作失败: {e}")

3. 不暴露内部错误:
   ✅ 正确:
   return {"success": False, "message": "操作失败,请稍后重试"}
   
   ❌ 错误:
   return {"success": False, "message": str(e)}  # 可能暴露敏感信息

4. 使用自定义异常:
   ✅ 正确:
   if not user:
       raise ResourceNotFoundException("用户不存在")
   
   ❌ 错误:
   if not user:
       raise Exception("用户不存在")

5. 异常传播:
   - 业务层: 抛出业务异常
   - 服务层: 转换为技术异常
   - 控制层: 捕获并转换为HTTP响应
"""
