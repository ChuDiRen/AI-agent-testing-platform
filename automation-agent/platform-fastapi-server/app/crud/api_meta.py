"""
API 元数据管理 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.api_meta import ApiMeta
from app.schemas.api_meta import ApiMetaCreate, ApiMetaUpdate


class CRUDApiMeta(CRUDBase[ApiMeta, ApiMetaCreate, ApiMetaUpdate]):
    """API 元数据管理 CRUD"""
    
    async def get_by_project_id(self, db: AsyncSession, *, project_id: int) -> List[ApiMeta]:
        """根据项目ID获取元数据"""
        result = await db.execute(select(ApiMeta).where(ApiMeta.project_id == project_id))
        return result.scalars().all()
    
    async def get_by_module_id(self, db: AsyncSession, *, module_id: int) -> List[ApiMeta]:
        """根据模块ID获取元数据"""
        result = await db.execute(select(ApiMeta).where(ApiMeta.module_id == module_id))
        return result.scalars().all()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        project_id: Optional[int] = None,
        module_id: Optional[int] = None,
        api_name: Optional[str] = None
    ) -> tuple[List[ApiMeta], int]:
        """根据筛选条件获取元数据列表"""
        query = select(ApiMeta)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiMeta.project_id == project_id)
        
        if module_id:
            query = query.where(ApiMeta.module_id == module_id)
        
        if api_name:
            query = query.where(ApiMeta.api_name.like(f"%{api_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_meta_crud = CRUDApiMeta(ApiMeta)
