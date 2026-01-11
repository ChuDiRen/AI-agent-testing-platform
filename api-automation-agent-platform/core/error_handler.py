"""
统一错误处理系统 - 错误分类、处理和恢复

职责：
- 错误类型枚举和分类
- 统一的错误响应数据模型
- 错误处理中间件
- 错误恢复策略
- 错误日志和监控
"""
from typing import Any, Dict, List, Optional, Union, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import traceback
import functools
import asyncio
from contextlib import asynccontextmanager

from core.logging_config import get_logger

logger = get_logger(__name__)


class ErrorType(str, Enum):
    """错误类型枚举"""
    # 网络相关错误
    NETWORK_ERROR = "network_error"
    CONNECTION_TIMEOUT = "connection_timeout"
    DNS_RESOLUTION_ERROR = "dns_resolution_error"
    
    # 认证相关错误
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    TOKEN_EXPIRED = "token_expired"
    
    # API相关错误
    API_NOT_FOUND = "api_not_found"
    API_RESPONSE_ERROR = "api_response_error"
    API_RATE_LIMIT = "api_rate_limit"
    API_TIMEOUT = "api_timeout"
    
    # 数据相关错误
    DATA_PARSING_ERROR = "data_parsing_error"
    DATA_VALIDATION_ERROR = "data_validation_error"
    DATA_FORMAT_ERROR = "data_format_error"
    
    # 测试相关错误
    ASSERTION_ERROR = "assertion_error"
    TEST_EXECUTION_ERROR = "test_execution_error"
    TEST_TIMEOUT = "test_timeout"
    
    # 系统相关错误
    SYSTEM_ERROR = "system_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CONFIGURATION_ERROR = "configuration_error"
    
    # 业务逻辑错误
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    VALIDATION_ERROR = "validation_error"
    CONSTRAINT_VIOLATION = "constraint_violation"
    
    # 未知错误
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(str, Enum):
    """错误严重程度枚举"""
    CRITICAL = "critical"    # 关键错误，系统不可用
    HIGH = "high"           # 高级错误，主要功能受影响
    MEDIUM = "medium"       # 中级错误，部分功能受影响
    LOW = "low"            # 低级错误，轻微影响
    INFO = "info"          # 信息级别，非错误


class ErrorCategory(str, Enum):
    """错误类别枚举"""
    INFRASTRUCTURE = "infrastructure"    # 基础设施错误
    APPLICATION = "application"         # 应用程序错误
    BUSINESS = "business"               # 业务逻辑错误
    INTEGRATION = "integration"         # 集成错误
    DATA = "data"                      # 数据错误
    SECURITY = "security"              # 安全错误


@dataclass
class ErrorContext:
    """错误上下文信息"""
    component: str = ""
    operation: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorResponse:
    """统一的错误响应数据模型"""
    error_id: str
    error_type: ErrorType
    error_category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    context: ErrorContext = field(default_factory=ErrorContext)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    resolved: bool = False
    resolved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type.value,
            "error_category": self.error_category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "context": {
                "component": self.context.component,
                "operation": self.context.operation,
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "metadata": self.context.metadata
            },
            "timestamp": self.timestamp,
            "stack_trace": self.stack_trace,
            "recovery_suggestions": self.recovery_suggestions,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at
        }


class ErrorHandler:
    """
    统一错误处理器
    
    提供错误分类、处理、恢复和监控功能。
    """

    def __init__(self):
        """初始化错误处理器"""
        self.error_handlers: Dict[ErrorType, Callable] = {}
        self.recovery_strategies: Dict[ErrorType, Callable] = {}
        self.error_history: List[ErrorResponse] = []
        self.error_stats: Dict[str, int] = {}
        
        # 注册默认错误处理器
        self._register_default_handlers()
        
        logger.info("错误处理器初始化完成")

    def _register_default_handlers(self):
        """注册默认错误处理器"""
        # 网络错误处理器
        self.register_handler(ErrorType.NETWORK_ERROR, self._handle_network_error)
        self.register_handler(ErrorType.CONNECTION_TIMEOUT, self._handle_timeout_error)
        
        # 认证错误处理器
        self.register_handler(ErrorType.AUTHENTICATION_ERROR, self._handle_auth_error)
        self.register_handler(ErrorType.TOKEN_EXPIRED, self._handle_token_expired)
        
        # API错误处理器
        self.register_handler(ErrorType.API_NOT_FOUND, self._handle_api_not_found)
        self.register_handler(ErrorType.API_RESPONSE_ERROR, self._handle_api_response_error)
        
        # 数据错误处理器
        self.register_handler(ErrorType.DATA_PARSING_ERROR, self._handle_data_parsing_error)
        self.register_handler(ErrorType.DATA_VALIDATION_ERROR, self._handle_data_validation_error)
        
        # 测试错误处理器
        self.register_handler(ErrorType.ASSERTION_ERROR, self._handle_assertion_error)
        self.register_handler(ErrorType.TEST_EXECUTION_ERROR, self._handle_test_execution_error)

    def register_handler(self, error_type: ErrorType, handler: Callable):
        """注册错误处理器"""
        self.error_handlers[error_type] = handler
        logger.debug(f"注册错误处理器: {error_type.value}")

    def register_recovery_strategy(self, error_type: ErrorType, strategy: Callable):
        """注册错误恢复策略"""
        self.recovery_strategies[error_type] = strategy
        logger.debug(f"注册恢复策略: {error_type.value}")

    def categorize_error(self, exception: Exception, context: ErrorContext) -> ErrorType:
        """根据异常和上下文对错误进行分类"""
        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()
        
        # 网络相关错误
        if any(keyword in error_message for keyword in ["connection", "network", "timeout"]):
            if "timeout" in error_message:
                return ErrorType.CONNECTION_TIMEOUT
            return ErrorType.NETWORK_ERROR
        
        # 认证相关错误
        if any(keyword in error_message for keyword in ["auth", "unauthorized", "forbidden"]):
            if "token" in error_message or "expired" in error_message:
                return ErrorType.TOKEN_EXPIRED
            return ErrorType.AUTHENTICATION_ERROR
        
        # API相关错误
        if any(keyword in error_message for keyword in ["404", "not found", "api"]):
            return ErrorType.API_NOT_FOUND
        if any(keyword in error_message for keyword in ["500", "502", "503", "server error"]):
            return ErrorType.API_RESPONSE_ERROR
        
        # 数据相关错误
        if any(keyword in error_message for keyword in ["json", "parse", "parsing"]):
            return ErrorType.DATA_PARSING_ERROR
        if any(keyword in error_message for keyword in ["validation", "validate"]):
            return ErrorType.DATA_VALIDATION_ERROR
        
        # 测试相关错误
        if any(keyword in error_message for keyword in ["assertion", "expect"]):
            return ErrorType.ASSERTION_ERROR
        if any(keyword in error_message for keyword in ["test", "execution"]):
            return ErrorType.TEST_EXECUTION_ERROR
        
        # 系统错误
        if any(keyword in error_message for keyword in ["system", "resource", "memory"]):
            return ErrorType.SYSTEM_ERROR
        
        return ErrorType.UNKNOWN_ERROR

    def determine_severity(self, error_type: ErrorType, context: ErrorContext) -> ErrorSeverity:
        """确定错误严重程度"""
        # 根据错误类型和上下文确定严重程度
        high_severity_types = [
            ErrorType.SYSTEM_ERROR,
            ErrorType.AUTHENTICATION_ERROR,
            ErrorType.RESOURCE_EXHAUSTED
        ]
        
        medium_severity_types = [
            ErrorType.API_RESPONSE_ERROR,
            ErrorType.DATA_VALIDATION_ERROR,
            ErrorType.TEST_EXECUTION_ERROR
        ]
        
        if error_type in high_severity_types:
            return ErrorSeverity.HIGH
        elif error_type in medium_severity_types:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def determine_category(self, error_type: ErrorType, context: ErrorContext) -> ErrorCategory:
        """确定错误类别"""
        category_mapping = {
            ErrorType.NETWORK_ERROR: ErrorCategory.INFRASTRUCTURE,
            ErrorType.CONNECTION_TIMEOUT: ErrorCategory.INFRASTRUCTURE,
            ErrorType.AUTHENTICATION_ERROR: ErrorCategory.SECURITY,
            ErrorType.AUTHORIZATION_ERROR: ErrorCategory.SECURITY,
            ErrorType.API_NOT_FOUND: ErrorCategory.APPLICATION,
            ErrorType.API_RESPONSE_ERROR: ErrorCategory.APPLICATION,
            ErrorType.DATA_PARSING_ERROR: ErrorCategory.DATA,
            ErrorType.DATA_VALIDATION_ERROR: ErrorCategory.DATA,
            ErrorType.ASSERTION_ERROR: ErrorCategory.APPLICATION,
            ErrorType.TEST_EXECUTION_ERROR: ErrorCategory.APPLICATION,
            ErrorType.SYSTEM_ERROR: ErrorCategory.INFRASTRUCTURE,
            ErrorType.BUSINESS_LOGIC_ERROR: ErrorCategory.BUSINESS
        }
        
        return category_mapping.get(error_type, ErrorCategory.APPLICATION)

    def create_error_response(
        self,
        exception: Exception,
        context: ErrorContext,
        include_stack_trace: bool = True
    ) -> ErrorResponse:
        """创建错误响应"""
        # 分类错误
        error_type = self.categorize_error(exception, context)
        severity = self.determine_severity(error_type, context)
        error_category = self.determine_category(error_type, context)
        
        # 生成恢复建议
        recovery_suggestions = self._generate_recovery_suggestions(error_type, exception)
        
        # 创建错误响应
        error_response = ErrorResponse(
            error_id=str(uuid.uuid4()),
            error_type=error_type,
            error_category=error_category,
            severity=severity,
            message=str(exception),
            details={
                "exception_type": type(exception).__name__,
                "exception_module": type(exception).__module__
            },
            context=context,
            stack_trace=traceback.format_exc() if include_stack_trace else None,
            recovery_suggestions=recovery_suggestions
        )
        
        # 记录错误
        self._record_error(error_response)
        
        return error_response

    def handle_error(
        self,
        exception: Exception,
        context: ErrorContext,
        retry_on_failure: bool = True
    ) -> Optional[ErrorResponse]:
        """处理错误"""
        try:
            # 创建错误响应
            error_response = self.create_error_response(exception, context)
            
            # 调用注册的处理器
            handler = self.error_handlers.get(error_response.error_type)
            if handler:
                try:
                    handler(error_response, context)
                except Exception as handler_error:
                    logger.error(f"错误处理器执行失败: {handler_error}", exc_info=handler_error)
            
            # 尝试恢复
            if retry_on_failure and error_response.retry_count < error_response.max_retries:
                recovery_result = self._attempt_recovery(error_response, context)
                if recovery_result:
                    error_response.resolved = True
                    error_response.resolved_at = datetime.utcnow().isoformat()
                    logger.info(f"错误恢复成功: {error_response.error_id}")
                    return None  # 错误已恢复
            
            # 记录处理结果
            logger.error(
                f"错误处理: {error_response.error_type.value} - {error_response.message}",
                extra={
                    "error_id": error_response.error_id,
                    "severity": error_response.severity.value,
                    "category": error_response.error_category.value
                }
            )
            
            return error_response
            
        except Exception as e:
            logger.error(f"错误处理器内部异常: {e}", exc_info=e)
            return None

    def _attempt_recovery(self, error_response: ErrorResponse, context: ErrorContext) -> bool:
        """尝试错误恢复"""
        try:
            recovery_strategy = self.recovery_strategies.get(error_response.error_type)
            if recovery_strategy:
                error_response.retry_count += 1
                result = recovery_strategy(error_response, context)
                return result
            return False
            
        except Exception as e:
            logger.error(f"错误恢复失败: {e}", exc_info=e)
            return False

    def _generate_recovery_suggestions(self, error_type: ErrorType, exception: Exception) -> List[str]:
        """生成错误恢复建议"""
        suggestions_map = {
            ErrorType.NETWORK_ERROR: [
                "检查网络连接",
                "验证服务可用性",
                "重试请求"
            ],
            ErrorType.CONNECTION_TIMEOUT: [
                "增加超时时间",
                "检查网络延迟",
                "重试连接"
            ],
            ErrorType.AUTHENTICATION_ERROR: [
                "验证认证凭据",
                "刷新访问令牌",
                "检查权限配置"
            ],
            ErrorType.TOKEN_EXPIRED: [
                "刷新访问令牌",
                "重新进行身份验证",
                "检查令牌过期时间"
            ],
            ErrorType.API_NOT_FOUND: [
                "验证API端点URL",
                "检查API版本",
                "更新API文档"
            ],
            ErrorType.API_RESPONSE_ERROR: [
                "检查API响应格式",
                "验证请求参数",
                "重试请求"
            ],
            ErrorType.DATA_PARSING_ERROR: [
                "检查数据格式",
                "验证JSON结构",
                "更新解析逻辑"
            ],
            ErrorType.DATA_VALIDATION_ERROR: [
                "验证输入数据",
                "检查数据约束",
                "更新验证规则"
            ],
            ErrorType.ASSERTION_ERROR: [
                "更新断言条件",
                "验证期望值",
                "检查实际响应"
            ],
            ErrorType.TEST_EXECUTION_ERROR: [
                "检查测试环境",
                "验证测试数据",
                "重试测试执行"
            ]
        }
        
        return suggestions_map.get(error_type, [
            "检查错误日志获取更多信息",
            "联系技术支持团队",
            "重试操作"
        ])

    def _record_error(self, error_response: ErrorResponse):
        """记录错误到历史"""
        self.error_history.append(error_response)
        
        # 更新错误统计
        error_key = f"{error_response.error_type.value}_{error_response.severity.value}"
        self.error_stats[error_key] = self.error_stats.get(error_key, 0) + 1
        
        # 保持历史记录在合理范围内
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]  # 保留最近500条

    # 默认错误处理器实现
    def _handle_network_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理网络错误"""
        logger.warning(f"网络错误处理: {error_response.message}")
        # 可以添加网络重试逻辑

    def _handle_timeout_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理超时错误"""
        logger.warning(f"超时错误处理: {error_response.message}")
        # 可以添加超时重试逻辑

    def _handle_auth_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理认证错误"""
        logger.warning(f"认证错误处理: {error_response.message}")
        # 可以添加认证刷新逻辑

    def _handle_token_expired(self, error_response: ErrorResponse, context: ErrorContext):
        """处理令牌过期错误"""
        logger.warning(f"令牌过期错误处理: {error_response.message}")
        # 可以添加令牌刷新逻辑

    def _handle_api_not_found(self, error_response: ErrorResponse, context: ErrorContext):
        """处理API未找到错误"""
        logger.warning(f"API未找到错误处理: {error_response.message}")

    def _handle_api_response_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理API响应错误"""
        logger.warning(f"API响应错误处理: {error_response.message}")

    def _handle_data_parsing_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理数据解析错误"""
        logger.warning(f"数据解析错误处理: {error_response.message}")

    def _handle_data_validation_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理数据验证错误"""
        logger.warning(f"数据验证错误处理: {error_response.message}")

    def _handle_assertion_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理断言错误"""
        logger.warning(f"断言错误处理: {error_response.message}")

    def _handle_test_execution_error(self, error_response: ErrorResponse, context: ErrorContext):
        """处理测试执行错误"""
        logger.warning(f"测试执行错误处理: {error_response.message}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return {
            "total_errors": len(self.error_history),
            "error_stats": self.error_stats.copy(),
            "recent_errors": len([e for e in self.error_history if 
                               datetime.fromisoformat(e.timestamp) > datetime.utcnow().replace(hour=0, minute=0, second=0)]),
            "unresolved_errors": len([e for e in self.error_history if not e.resolved])
        }

    def get_error_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取错误历史"""
        return [error.to_dict() for error in self.error_history[-limit:]]

    def clear_error_history(self):
        """清空错误历史"""
        self.error_history.clear()
        self.error_stats.clear()
        logger.info("错误历史已清空")


# 装饰器函数
def error_handler_decorator(component: str = "", operation: str = ""):
    """错误处理装饰器"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            context = ErrorContext(component=component, operation=operation)
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_response = error_handler.handle_error(e, context)
                if error_response:
                    # 根据错误严重程度决定是否重新抛出
                    if error_response.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                        raise
                return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            context = ErrorContext(component=component, operation=operation)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_response = error_handler.handle_error(e, context)
                if error_response:
                    # 根据错误严重程度决定是否重新抛出
                    if error_response.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                        raise
                return None
        
        # 根据函数类型返回适当的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 上下文管理器
@asynccontextmanager
async def error_context(component: str, operation: str, **kwargs):
    """错误处理上下文管理器"""
    error_handler = get_error_handler()
    context = ErrorContext(component=component, operation=operation, **kwargs)
    
    try:
        yield context
    except Exception as e:
        error_handler.handle_error(e, context)
        raise


# 全局错误处理器实例
_error_handler_instance: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器实例"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance


def create_error_handler() -> ErrorHandler:
    """创建新的错误处理器实例"""
    return ErrorHandler()
