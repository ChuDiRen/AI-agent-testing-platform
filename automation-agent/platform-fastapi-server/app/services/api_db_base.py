"""
API 数据库基础配置 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.services.base import CRUDBase
from app.models.api_db_base import ApiDbBase
from app.schemas.api_db_base import ApiDbBaseCreate, ApiDbBaseUpdate


class CRUDApiDbBase(CRUDBase[ApiDbBase, ApiDbBaseCreate, ApiDbBaseUpdate]):
    """API 数据库基础配置 CRUD"""
    
    async def get_by_project_id(self, db: AsyncSession, *, project_id: int) -> List[ApiDbBase]:
        """根据项目ID获取数据库配置"""
        result = await db.execute(select(ApiDbBase).where(ApiDbBase.project_id == project_id))
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[ApiDbBase]:
        """根据连接名获取数据库配置"""
        result = await db.execute(select(ApiDbBase).where(ApiDbBase.name == name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        project_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> tuple[List[ApiDbBase], int]:
        """根据筛选条件获取数据库配置列表"""
        query = select(ApiDbBase)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiDbBase.project_id == project_id)
        
        if name:
            query = query.where(ApiDbBase.name.like(f"%{name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_db_base_crud = CRUDApiDbBase(ApiDbBase)
