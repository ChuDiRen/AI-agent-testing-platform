# Copyright (c) 2025 左岚. All rights reserved.
"""
API端点Service
处理API端点相关的业务逻辑
"""

import math
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.entity.api_endpoint import ApiEndpoint, ApiStatus, ApiMethod
from app.repository.api_endpoint_repository import ApiEndpointRepository
from app.dto.api_endpoint_dto import (
    ApiEndpointCreateRequest,
    ApiEndpointUpdateRequest,
    ApiEndpointQueryRequest,
    ApiEndpointResponse,
    ApiEndpointListResponse,
    ApiStatisticsResponse
)
from app.service.base import BaseService
from app.utils.exceptions import BusinessException


class ApiEndpointService(BaseService):
    """
    API端点Service类
    处理API端点相关的业务逻辑
    """

    def __init__(self, db: Session):
        self.db = db  # 添加db属性
        self.api_repository = ApiEndpointRepository(db)
        super().__init__(self.api_repository)  # 传递repository给BaseService

    def create_api_endpoint(self, request: ApiEndpointCreateRequest, created_by_id: int) -> ApiEndpointResponse:
        """
        创建API端点

        Args:
            request: 创建请求DTO
            created_by_id: 创建者ID

        Returns:
            API端点响应DTO

        Raises:
            BusinessException: 业务异常
        """
        # 验证HTTP方法
        if request.method.upper() not in [method.value for method in ApiMethod]:
            raise BusinessException(f"不支持的HTTP方法: {request.method}")

        # 检查API路径和方法是否已存在
        existing_api = self.api_repository.find_by_path_and_method(request.path, request.method)
        if existing_api:
            raise BusinessException(f"API端点已存在: {request.method} {request.path}")

        # 创建API端点实体
        api_endpoint = ApiEndpoint(
            path=request.path,
            method=request.method.upper(),
            name=request.name,
            description=request.description,
            module=request.module,
            permission=request.permission,
            version=request.version,
            request_example=request.request_example,
            response_example=request.response_example,
            created_by_id=created_by_id
        )

        # 保存到数据库
        saved_api = self.api_repository.create(api_endpoint)
        
        return self._convert_to_response(saved_api)

    def update_api_endpoint(self, api_id: int, request: ApiEndpointUpdateRequest) -> ApiEndpointResponse:
        """
        更新API端点

        Args:
            api_id: API端点ID
            request: 更新请求DTO

        Returns:
            API端点响应DTO

        Raises:
            BusinessException: 业务异常
        """
        # 查找API端点
        api_endpoint = self.api_repository.find_by_id(api_id)
        if not api_endpoint:
            raise BusinessException(f"API端点不存在: {api_id}")

        # 更新字段
        if request.name is not None:
            api_endpoint.name = request.name
        if request.description is not None:
            api_endpoint.description = request.description
        if request.status is not None:
            # 验证状态值
            if request.status not in [status.value for status in ApiStatus]:
                raise BusinessException(f"无效的API状态: {request.status}")
            api_endpoint.status = request.status
        if request.module is not None:
            api_endpoint.module = request.module
        if request.permission is not None:
            api_endpoint.permission = request.permission
        if request.version is not None:
            api_endpoint.version = request.version
        if request.request_example is not None:
            api_endpoint.request_example = request.request_example
        if request.response_example is not None:
            api_endpoint.response_example = request.response_example

        # 保存更新
        updated_api = self.api_repository.update(api_endpoint)
        
        return self._convert_to_response(updated_api)

    def delete_api_endpoint(self, api_id: int) -> bool:
        """
        删除API端点

        Args:
            api_id: API端点ID

        Returns:
            是否删除成功

        Raises:
            BusinessException: 业务异常
        """
        # 查找API端点
        api_endpoint = self.api_repository.find_by_id(api_id)
        if not api_endpoint:
            raise BusinessException(f"API端点不存在: {api_id}")

        # 检查是否可以删除（例如：是否有调用记录）
        if api_endpoint.total_calls > 0:
            # 如果有调用记录，建议设置为废弃状态而不是删除
            raise BusinessException("该API端点有调用记录，建议设置为废弃状态而不是删除")

        # 删除API端点
        return self.api_repository.delete(api_endpoint)

    def get_api_endpoint(self, api_id: int) -> ApiEndpointResponse:
        """
        获取API端点详情

        Args:
            api_id: API端点ID

        Returns:
            API端点响应DTO

        Raises:
            BusinessException: 业务异常
        """
        api_endpoint = self.api_repository.find_by_id(api_id)
        if not api_endpoint:
            raise BusinessException(f"API端点不存在: {api_id}")

        return self._convert_to_response(api_endpoint)

    def get_api_endpoints(self, request: ApiEndpointQueryRequest) -> ApiEndpointListResponse:
        """
        获取API端点列表

        Args:
            request: 查询请求DTO

        Returns:
            API端点列表响应DTO
        """
        # 搜索API端点
        items, total = self.api_repository.search_apis(
            keyword=request.keyword,
            method=request.method,
            status=request.status,
            module=request.module,
            permission=request.permission,
            page=request.page,
            size=request.size
        )

        # 转换为响应DTO
        api_responses = [self._convert_to_response(api) for api in items]

        # 计算总页数
        pages = math.ceil(total / request.size) if total > 0 else 0

        return ApiEndpointListResponse(
            items=api_responses,
            total=total,
            page=request.page,
            size=request.size,
            pages=pages
        )

    def get_api_statistics(self) -> ApiStatisticsResponse:
        """
        获取API统计数据

        Returns:
            API统计响应DTO
        """
        stats = self.api_repository.get_statistics()
        
        return ApiStatisticsResponse(**stats)

    def get_modules(self) -> List[str]:
        """
        获取所有模块列表

        Returns:
            模块名称列表
        """
        return self.api_repository.get_modules()

    def get_permissions(self) -> List[str]:
        """
        获取所有权限列表

        Returns:
            权限标识列表
        """
        return self.api_repository.get_permissions()

    def get_methods(self) -> List[str]:
        """
        获取所有HTTP方法列表

        Returns:
            HTTP方法列表
        """
        return self.api_repository.get_methods()

    def update_api_stats(self, path: str, method: str, success: bool, response_time: float) -> bool:
        """
        更新API统计数据

        Args:
            path: API路径
            method: HTTP方法
            success: 是否成功
            response_time: 响应时间

        Returns:
            是否更新成功
        """
        api_endpoint = self.api_repository.find_by_path_and_method(path, method)
        if api_endpoint:
            return self.api_repository.update_api_stats(api_endpoint.id, success, response_time)
        return False

    def batch_update_status(self, api_ids: List[int], status: str) -> int:
        """
        批量更新API状态

        Args:
            api_ids: API端点ID列表
            status: 新状态

        Returns:
            更新的数量

        Raises:
            BusinessException: 业务异常
        """
        # 验证状态值
        if status not in [s.value for s in ApiStatus]:
            raise BusinessException(f"无效的API状态: {status}")

        api_status = ApiStatus(status)
        return self.api_repository.batch_update_status(api_ids, api_status)

    def sync_api_endpoints_from_routes(self, created_by_id: int) -> Dict[str, Any]:
        """
        从路由同步API端点（扫描现有路由并自动创建API端点记录）

        Args:
            created_by_id: 创建者ID

        Returns:
            同步结果统计
        """
        # 这里可以实现从FastAPI路由自动扫描API端点的逻辑
        # 暂时返回模拟数据
        return {
            "total_scanned": 0,
            "new_created": 0,
            "updated": 0,
            "skipped": 0
        }

    def _convert_to_response(self, api_endpoint: ApiEndpoint) -> ApiEndpointResponse:
        """
        将API端点实体转换为响应DTO

        Args:
            api_endpoint: API端点实体

        Returns:
            API端点响应DTO
        """
        return ApiEndpointResponse(
            id=api_endpoint.id,
            path=api_endpoint.path,
            method=api_endpoint.method,
            name=api_endpoint.name,
            description=api_endpoint.description,
            status=api_endpoint.status,
            module=api_endpoint.module,
            permission=api_endpoint.permission,
            version=api_endpoint.version,
            request_example=api_endpoint.request_example,
            response_example=api_endpoint.response_example,
            total_calls=api_endpoint.total_calls,
            success_calls=api_endpoint.success_calls,
            error_calls=api_endpoint.error_calls,
            success_rate=api_endpoint.get_success_rate(),
            avg_response_time=api_endpoint.avg_response_time,
            max_response_time=api_endpoint.max_response_time,
            min_response_time=api_endpoint.min_response_time,
            last_called_at=api_endpoint.last_called_at.isoformat() if api_endpoint.last_called_at else None,
            created_at=api_endpoint.created_at.isoformat() if api_endpoint.created_at else None,
            updated_at=api_endpoint.updated_at.isoformat() if api_endpoint.updated_at else None,
            created_by_id=api_endpoint.created_by_id
        )
