"""
Controller层基类
提供通用的HTTP请求处理功能
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse, PaginationRequest, PaginatedResponse
from app.service.base import BaseService
from app.utils.exceptions import (
    BaseAPIException,
    ValidationException,
    BusinessException,
    NotFoundException
)

# 定义泛型类型
ServiceType = TypeVar("ServiceType", bound=BaseService)

logger = get_logger(__name__)


class BaseController:
    """
    Controller基类
    提供通用的HTTP请求处理方法
    """

    def __init__(self, service_class: Type[ServiceType]):
        """
        初始化Controller
        
        Args:
            service_class: Service类
        """
        self.service_class = service_class

    def get_service(self, db: Session = Depends(get_db)) -> ServiceType:
        """
        获取Service实例
        
        Args:
            db: 数据库会话
            
        Returns:
            Service实例
        """
        # 这里需要子类实现具体的Service实例化逻辑
        raise NotImplementedError("Subclasses must implement get_service method")

    async def handle_request(self, operation, *args, **kwargs) -> ApiResponse:
        """
        统一处理请求
        
        Args:
            operation: 要执行的操作函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            API响应对象
        """
        try:
            result = await operation(*args, **kwargs) if hasattr(operation, '__call__') else operation
            
            if result is None:
                return ApiResponse.success_response(message="Operation completed successfully")
            
            return ApiResponse.success_response(data=result)
            
        except BaseAPIException as e:
            logger.warning(f"API exception: {e.detail}")
            raise e
        except ValidationException as e:
            logger.warning(f"Validation exception: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.detail
            )
        except BusinessException as e:
            logger.warning(f"Business exception: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.detail
            )
        except NotFoundException as e:
            logger.warning(f"Not found exception: {e.detail}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.detail
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    def create_success_response(self, data: Any = None, message: str = "Success") -> ApiResponse:
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            成功响应对象
        """
        return ApiResponse.success_response(data=data, message=message)

    def create_error_response(self, message: str, error_code: Optional[str] = None) -> ApiResponse:
        """
        创建错误响应
        
        Args:
            message: 错误消息
            error_code: 错误代码
            
        Returns:
            错误响应对象
        """
        return ApiResponse.error_response(message=message, error_code=error_code)

    def create_paginated_response(self, items: List[Any], pagination: PaginationRequest, 
                                 total: int) -> PaginatedResponse:
        """
        创建分页响应
        
        Args:
            items: 数据列表
            pagination: 分页请求
            total: 总记录数
            
        Returns:
            分页响应对象
        """
        return PaginatedResponse.create(items, pagination.page, pagination.page_size, total)

    def validate_id(self, entity_id: int, entity_name: str = "Entity") -> None:
        """
        验证ID参数
        
        Args:
            entity_id: 实体ID
            entity_name: 实体名称
            
        Raises:
            ValidationException: ID验证失败
        """
        if entity_id is None or entity_id <= 0:
            raise ValidationException(f"Invalid {entity_name.lower()} ID: {entity_id}")

    def validate_pagination(self, pagination: PaginationRequest) -> None:
        """
        验证分页参数
        
        Args:
            pagination: 分页请求对象
            
        Raises:
            ValidationException: 分页参数验证失败
        """
        if pagination.page < 1:
            raise ValidationException("Page number must be greater than 0")
        
        if pagination.page_size < 1 or pagination.page_size > 100:
            raise ValidationException("Page size must be between 1 and 100")

    def log_request(self, endpoint: str, params: Dict[str, Any] = None) -> None:
        """
        记录请求日志
        
        Args:
            endpoint: 端点名称
            params: 请求参数
        """
        logger.info(f"Request to {endpoint}", extra={"params": params})

    def log_response(self, endpoint: str, response_data: Any = None) -> None:
        """
        记录响应日志
        
        Args:
            endpoint: 端点名称
            response_data: 响应数据
        """
        logger.info(f"Response from {endpoint}", extra={"response": response_data})

    def extract_user_id_from_token(self, token: str) -> Optional[int]:
        """
        从令牌中提取用户ID
        
        Args:
            token: JWT令牌
            
        Returns:
            用户ID或None
        """
        from app.core.security import get_user_id_from_token
        return get_user_id_from_token(token)

    def check_permission(self, user_id: int, permission: str) -> bool:
        """
        检查用户权限
        
        Args:
            user_id: 用户ID
            permission: 权限名称
            
        Returns:
            是否有权限
        """
        # 这里可以实现具体的权限检查逻辑
        # 暂时返回True，实际项目中需要根据业务需求实现
        return True

    def require_permission(self, user_id: int, permission: str) -> None:
        """
        要求用户具有特定权限
        
        Args:
            user_id: 用户ID
            permission: 权限名称
            
        Raises:
            HTTPException: 权限不足异常
        """
        if not self.check_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )

    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理输入数据
        
        Args:
            data: 输入数据字典
            
        Returns:
            清理后的数据字典
        """
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # 清理字符串：去除首尾空白，防止XSS等
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized

    def format_error_details(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        格式化错误详情
        
        Args:
            errors: 错误列表
            
        Returns:
            格式化后的错误详情
        """
        return {
            "errors": errors,
            "error_count": len(errors),
            "timestamp": "2023-01-01T00:00:00Z"  # 实际应该使用当前时间
        }

    def build_filter_conditions(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建过滤条件
        
        Args:
            filters: 过滤器字典
            
        Returns:
            处理后的过滤条件
        """
        conditions = {}
        for key, value in filters.items():
            if value is not None:
                conditions[key] = value
        return conditions

    def handle_bulk_operation_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理批量操作结果
        
        Args:
            results: 操作结果列表
            
        Returns:
            汇总的操作结果
        """
        total = len(results)
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = total - success_count
        
        return {
            "total": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": success_count / total if total > 0 else 0.0,
            "results": results
        }


# 导出基类
__all__ = ["BaseController"]
