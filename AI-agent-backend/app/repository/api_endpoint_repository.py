"""
API端点Repository
处理API端点相关的数据库操作
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.entity.api_endpoint import ApiEndpoint, ApiStatus
from app.repository.base import BaseRepository


class ApiEndpointRepository(BaseRepository[ApiEndpoint]):
    """
    API端点Repository类
    继承BaseRepository，提供API端点相关的数据库操作
    """

    def __init__(self, db: Session):
        super().__init__(db, ApiEndpoint)

    def find_by_path_and_method(self, path: str, method: str) -> Optional[ApiEndpoint]:
        """
        根据路径和方法查找API端点

        Args:
            path: API路径
            method: HTTP方法

        Returns:
            API端点实体或None
        """
        return self.db.query(ApiEndpoint).filter(
            and_(
                ApiEndpoint.path == path,
                ApiEndpoint.method == method.upper()
            )
        ).first()

    def find_by_module(self, module: str) -> List[ApiEndpoint]:
        """
        根据模块查找API端点列表

        Args:
            module: 模块名称

        Returns:
            API端点列表
        """
        return self.db.query(ApiEndpoint).filter(
            ApiEndpoint.module == module
        ).all()

    def find_by_permission(self, permission: str) -> List[ApiEndpoint]:
        """
        根据权限查找API端点列表

        Args:
            permission: 权限标识

        Returns:
            API端点列表
        """
        return self.db.query(ApiEndpoint).filter(
            ApiEndpoint.permission == permission
        ).all()

    def find_by_status(self, status: ApiStatus) -> List[ApiEndpoint]:
        """
        根据状态查找API端点列表

        Args:
            status: API状态

        Returns:
            API端点列表
        """
        return self.db.query(ApiEndpoint).filter(
            ApiEndpoint.status == status.value
        ).all()

    def search_apis(self, keyword: str = None, method: str = None, status: str = None,
                   module: str = None, permission: str = None, 
                   page: int = 1, size: int = 10) -> Tuple[List[ApiEndpoint], int]:
        """
        搜索API端点

        Args:
            keyword: 搜索关键词（匹配名称、路径、描述）
            method: HTTP方法筛选
            status: 状态筛选
            module: 模块筛选
            permission: 权限筛选
            page: 页码
            size: 每页数量

        Returns:
            (API端点列表, 总数量)
        """
        query = self.db.query(ApiEndpoint)

        # 关键词搜索
        if keyword:
            keyword_filter = or_(
                ApiEndpoint.name.ilike(f"%{keyword}%"),
                ApiEndpoint.path.ilike(f"%{keyword}%"),
                ApiEndpoint.description.ilike(f"%{keyword}%")
            )
            query = query.filter(keyword_filter)

        # 方法筛选
        if method:
            query = query.filter(ApiEndpoint.method == method.upper())

        # 状态筛选
        if status:
            query = query.filter(ApiEndpoint.status == status)

        # 模块筛选
        if module:
            query = query.filter(ApiEndpoint.module == module)

        # 权限筛选
        if permission:
            query = query.filter(ApiEndpoint.permission == permission)

        # 获取总数
        total = query.count()

        # 分页查询
        items = query.order_by(desc(ApiEndpoint.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()

        return items, total

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取API统计数据

        Returns:
            统计数据字典
        """
        # 基础统计
        total_apis = self.db.query(func.count(ApiEndpoint.id)).scalar() or 0
        active_apis = self.db.query(func.count(ApiEndpoint.id)).filter(
            ApiEndpoint.status == ApiStatus.ACTIVE.value
        ).scalar() or 0
        deprecated_apis = self.db.query(func.count(ApiEndpoint.id)).filter(
            ApiEndpoint.status == ApiStatus.DEPRECATED.value
        ).scalar() or 0
        maintenance_apis = self.db.query(func.count(ApiEndpoint.id)).filter(
            ApiEndpoint.status == ApiStatus.MAINTENANCE.value
        ).scalar() or 0

        # 今日调用统计（这里简化处理，实际应该有专门的调用日志表）
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # 总调用次数
        total_calls_today = self.db.query(func.sum(ApiEndpoint.total_calls)).filter(
            ApiEndpoint.last_called_at >= today_start
        ).scalar() or 0
        
        # 成功调用次数
        success_calls_today = self.db.query(func.sum(ApiEndpoint.success_calls)).filter(
            ApiEndpoint.last_called_at >= today_start
        ).scalar() or 0
        
        # 错误调用次数
        error_calls_today = total_calls_today - success_calls_today

        # 平均响应时间
        avg_response_time = self.db.query(func.avg(ApiEndpoint.avg_response_time)).scalar() or 0.0

        # 热门API（按调用次数排序）
        top_apis_query = self.db.query(
            ApiEndpoint.name,
            ApiEndpoint.path,
            ApiEndpoint.total_calls
        ).filter(
            ApiEndpoint.total_calls > 0
        ).order_by(desc(ApiEndpoint.total_calls)).limit(5)
        
        top_apis = [
            {
                "name": api.name,
                "path": api.path,
                "calls": api.total_calls
            }
            for api in top_apis_query.all()
        ]

        # 错误率高的API
        error_apis_query = self.db.query(ApiEndpoint).filter(
            and_(
                ApiEndpoint.total_calls > 0,
                ApiEndpoint.error_calls > 0
            )
        ).all()
        
        error_apis = []
        for api in error_apis_query:
            error_rate = (api.error_calls / api.total_calls) * 100
            if error_rate > 5:  # 错误率超过5%的API
                error_apis.append({
                    "name": api.name,
                    "path": api.path,
                    "error_rate": round(error_rate, 2)
                })
        
        # 按错误率排序
        error_apis.sort(key=lambda x: x["error_rate"], reverse=True)
        error_apis = error_apis[:5]  # 取前5个

        return {
            "total_apis": total_apis,
            "active_apis": active_apis,
            "deprecated_apis": deprecated_apis,
            "maintenance_apis": maintenance_apis,
            "total_calls_today": total_calls_today,
            "success_calls_today": success_calls_today,
            "error_calls_today": error_calls_today,
            "avg_response_time": round(avg_response_time, 2),
            "top_apis": top_apis,
            "error_apis": error_apis
        }

    def get_modules(self) -> List[str]:
        """
        获取所有模块列表

        Returns:
            模块名称列表
        """
        modules = self.db.query(ApiEndpoint.module).filter(
            ApiEndpoint.module.isnot(None)
        ).distinct().all()
        
        return [module[0] for module in modules if module[0]]

    def get_permissions(self) -> List[str]:
        """
        获取所有权限列表

        Returns:
            权限标识列表
        """
        permissions = self.db.query(ApiEndpoint.permission).filter(
            ApiEndpoint.permission.isnot(None)
        ).distinct().all()
        
        return [permission[0] for permission in permissions if permission[0]]

    def get_methods(self) -> List[str]:
        """
        获取所有HTTP方法列表

        Returns:
            HTTP方法列表
        """
        methods = self.db.query(ApiEndpoint.method).distinct().all()
        return [method[0] for method in methods if method[0]]

    def update_api_stats(self, api_id: int, success: bool, response_time: float) -> bool:
        """
        更新API统计数据

        Args:
            api_id: API端点ID
            success: 是否成功
            response_time: 响应时间

        Returns:
            是否更新成功
        """
        try:
            api = self.find_by_id(api_id)
            if api:
                api.update_stats(success, response_time)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False

    def batch_update_status(self, api_ids: List[int], status: ApiStatus) -> int:
        """
        批量更新API状态

        Args:
            api_ids: API端点ID列表
            status: 新状态

        Returns:
            更新的数量
        """
        try:
            updated_count = self.db.query(ApiEndpoint).filter(
                ApiEndpoint.id.in_(api_ids)
            ).update(
                {ApiEndpoint.status: status.value},
                synchronize_session=False
            )
            self.db.commit()
            return updated_count
        except Exception:
            self.db.rollback()
            return 0
