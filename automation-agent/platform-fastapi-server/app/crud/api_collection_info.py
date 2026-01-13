"""
API 集合信息 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.api_collection_info import ApiCollectionInfo
from app.schemas.api_collection_info import ApiCollectionInfoCreate, ApiCollectionInfoUpdate


class CRUDApiCollectionInfo(CRUDBase[ApiCollectionInfo, ApiCollectionInfoCreate, ApiCollectionInfoUpdate]):
    """API 集合信息 CRUD"""
    
    async def get_by_project_id(self, db: AsyncSession, *, project_id: int) -> List[ApiCollectionInfo]:
        """根据项目ID获取集合信息"""
        result = await db.execute(select(ApiCollectionInfo).where(ApiCollectionInfo.project_id == project_id))
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, collection_name: str) -> Optional[ApiCollectionInfo]:
        """根据集合名称获取集合信息"""
        result = await db.execute(select(ApiCollectionInfo).where(ApiCollectionInfo.collection_name == collection_name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        project_id: Optional[int] = None,
        collection_name: Optional[str] = None
    ) -> tuple[List[ApiCollectionInfo], int]:
        """根据筛选条件获取集合信息列表"""
        query = select(ApiCollectionInfo)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiCollectionInfo.project_id == project_id)
        
        if collection_name:
            query = query.where(ApiCollectionInfo.collection_name.like(f"%{collection_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_collection_info_crud = CRUDApiCollectionInfo(ApiCollectionInfo)
