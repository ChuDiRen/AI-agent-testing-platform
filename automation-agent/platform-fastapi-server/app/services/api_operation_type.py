"""
API 操作类型管理 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.services.base import CRUDBase
from app.models.api_operation_type import ApiOperationType
from app.schemas.api_operation_type import ApiOperationTypeCreate, ApiOperationTypeUpdate


class CRUDApiOperationType(CRUDBase[ApiOperationType, ApiOperationTypeCreate, ApiOperationTypeUpdate]):
    """API 操作类型管理 CRUD"""
    
    async def get_by_name(self, db: AsyncSession, *, operation_type_name: str) -> Optional[ApiOperationType]:
        """根据操作类型名称获取操作类型"""
        result = await db.execute(select(ApiOperationType).where(ApiOperationType.operation_type_name == operation_type_name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        operation_type_name: Optional[str] = None
    ) -> tuple[List[ApiOperationType], int]:
        """根据筛选条件获取操作类型列表"""
        query = select(ApiOperationType)
        
        # 添加筛选条件
        if operation_type_name:
            query = query.where(ApiOperationType.operation_type_name.like(f"%{operation_type_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_operation_type_crud = CRUDApiOperationType(ApiOperationType)
