"""
DTO层基类
定义数据传输对象的基础结构
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, List, Generic, TypeVar

from pydantic import BaseModel, Field, validator

# 定义泛型类型变量
T = TypeVar('T')


class BaseRequest(BaseModel):
    """
    请求DTO基类
    所有请求数据传输对象都应该继承此类
    """
    
    class Config:
        # 允许使用字段别名
        validate_by_name = True
        # 验证赋值
        validate_assignment = True
        # 使用枚举值
        use_enum_values = True
        # JSON编码器
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class BaseResponse(BaseModel):
    """
    响应DTO基类
    所有响应数据传输对象都应该继承此类
    """
    
    class Config:
        # 允许使用字段别名
        validate_by_name = True
        # 从ORM模式创建
        from_attributes = True
        # JSON编码器
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PaginationRequest(BaseRequest):
    """
    分页请求DTO
    """
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页大小，最大100")
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v > 100:
            raise ValueError('Page size cannot exceed 100')
        return v
    
    @property
    def skip(self) -> int:
        """计算跳过的记录数"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.page_size


class PaginationResponse(BaseResponse):
    """
    分页响应DTO
    """
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    @classmethod
    def create(cls, page: int, page_size: int, total: int) -> "PaginationResponse":
        """
        创建分页响应对象
        
        Args:
            page: 当前页码
            page_size: 每页大小
            total: 总记录数
            
        Returns:
            分页响应对象
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class SortOrder(str, Enum):
    """排序方向枚举"""
    ASC = "asc"
    DESC = "desc"


class SortRequest(BaseRequest):
    """
    排序请求DTO
    """
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: SortOrder = Field(default=SortOrder.ASC, description="排序方向")


class SearchRequest(PaginationRequest, SortRequest):
    """
    搜索请求DTO
    """
    keyword: Optional[str] = Field(default=None, min_length=1, max_length=100, description="搜索关键词")
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ApiResponse(BaseResponse, Generic[T]):
    """
    统一API响应格式
    """
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success") -> "ApiResponse":
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            成功响应对象
        """
        return cls(
            success=True,
            message=message,
            data=data
        )
    
    @classmethod
    def error_response(cls, message: str, error_code: Optional[str] = None, 
                      data: Any = None) -> "ApiResponse":
        """
        创建错误响应
        
        Args:
            message: 错误消息
            error_code: 错误代码
            data: 错误数据
            
        Returns:
            错误响应对象
        """
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            data=data
        )


class PaginatedResponse(BaseResponse):
    """
    分页数据响应DTO
    """
    items: List[Any] = Field(description="数据列表")
    pagination: PaginationResponse = Field(description="分页信息")
    
    @classmethod
    def create(cls, items: List[Any], page: int, page_size: int, total: int) -> "PaginatedResponse":
        """
        创建分页数据响应
        
        Args:
            items: 数据列表
            page: 当前页码
            page_size: 每页大小
            total: 总记录数
            
        Returns:
            分页数据响应对象
        """
        pagination = PaginationResponse.create(page, page_size, total)
        
        return cls(
            items=items,
            pagination=pagination
        )


class IdRequest(BaseRequest):
    """
    ID请求DTO
    """
    id: int = Field(ge=1, description="实体ID")


class IdsRequest(BaseRequest):
    """
    多个ID请求DTO
    """
    ids: List[int] = Field(min_items=1, max_items=100, description="实体ID列表")
    
    @validator('ids')
    def validate_ids(cls, v):
        # 去重并排序
        return sorted(list(set(v)))


class StatusRequest(BaseRequest):
    """
    状态请求DTO
    """
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_deleted: Optional[bool] = Field(default=None, description="是否删除")


class DateRangeRequest(BaseRequest):
    """
    日期范围请求DTO
    """
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('End date must be after start date')
        return v


class BulkOperationRequest(BaseRequest):
    """
    批量操作请求DTO
    """
    ids: List[int] = Field(min_items=1, max_items=100, description="要操作的ID列表")
    operation: str = Field(description="操作类型")
    
    @validator('ids')
    def validate_ids(cls, v):
        return sorted(list(set(v)))


class BulkOperationResponse(BaseResponse):
    """
    批量操作响应DTO
    """
    total: int = Field(description="总数量")
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    failed_ids: List[int] = Field(default_factory=list, description="失败的ID列表")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.success_count / self.total if self.total > 0 else 0.0


# 导出所有基础DTO类
__all__ = [
    "BaseRequest",
    "BaseResponse", 
    "PaginationRequest",
    "PaginationResponse",
    "SortOrder",
    "SortRequest",
    "SearchRequest",
    "ApiResponse",
    "PaginatedResponse",
    "IdRequest",
    "IdsRequest",
    "StatusRequest",
    "DateRangeRequest",
    "BulkOperationRequest",
    "BulkOperationResponse",
]
