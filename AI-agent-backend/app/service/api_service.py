"""
API Service - 完全按照5层架构实现
实现API接口管理的业务逻辑
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.logger import get_logger
from app.entity.api_endpoint import ApiEndpoint
from app.service.api_endpoint_service import ApiEndpointService

logger = get_logger(__name__)


class ApiService:
    """
    API Service类 - 封装ApiEndpointService
    提供API接口管理的业务逻辑处理
    """

    def __init__(self, db: Session):
        """
        初始化API Service

        Args:
            db: 数据库会话
        """
        self.db = db
        self.api_endpoint_service = ApiEndpointService(db)

    async def get_api_list(self, page: int = 1, page_size: int = 20, filters: dict = None) -> Tuple[List[ApiEndpoint], int]:
        """
        获取API列表（分页）- 使用ApiEndpointService

        Args:
            page: 页码
            page_size: 每页数量
            filters: 过滤条件

        Returns:
            (API列表, 总数量)
        """
        return await self.api_endpoint_service.get_api_endpoint_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

    async def get_api_by_path_method(self, path: str, method: str) -> Optional[ApiEndpoint]:
        """
        根据路径和方法获取API - 使用ApiEndpointService

        Args:
            path: API路径
            method: 请求方法

        Returns:
            API对象或None
        """
        return self.api_endpoint_service.get_api_endpoint_by_path_method(path, method)

    def get_api_by_id(self, api_id: int) -> Optional[ApiEndpoint]:
        """
        根据ID获取API - 使用ApiEndpointService

        Args:
            api_id: API ID

        Returns:
            API对象或None
        """
        return self.api_endpoint_service.get_api_endpoint_by_id(api_id)

    def create_api(self, path: str, method: str, description: str = None,
                   tags: str = None, is_active: bool = True) -> ApiEndpoint:
        """
        创建API - 使用ApiEndpointService

        Args:
            path: API路径
            method: 请求方法
            description: API描述
            tags: API标签
            is_active: 是否启用

        Returns:
            创建的API对象
        """
        return self.api_endpoint_service.create_api_endpoint(
            path=path,
            method=method,
            description=description,
            tags=tags
        )

    def delete_api(self, api_id: int) -> bool:
        """
        删除API - 使用ApiEndpointService

        Args:
            api_id: API ID

        Returns:
            是否删除成功
        """
        return self.api_endpoint_service.delete_api_endpoint(api_id)

    async def refresh_api_list(self) -> Tuple[int, int]:
        """
        刷新API列表（从路由中自动扫描）- 使用ApiEndpointService

        Returns:
            (新增数量, 更新数量)
        """
        return await self.api_endpoint_service.refresh_api_endpoints()

