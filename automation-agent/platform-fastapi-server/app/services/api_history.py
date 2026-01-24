"""
API 历史记录信息 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.services.base import CRUDBase
from app.models.api_history import ApiHistory
from app.schemas.api_history import ApiHistoryCreate, ApiHistoryUpdate


class CRUDApiHistory(CRUDBase[ApiHistory, ApiHistoryCreate, ApiHistoryUpdate]):
    """API 历史记录信息 CRUD"""
    
    async def get_by_collection_info_id(self, db: AsyncSession, *, collection_info_id: int) -> List[ApiHistory]:
        """根据集合信息ID获取历史记录"""
        result = await db.execute(select(ApiHistory).where(ApiHistory.collection_info_id == collection_info_id))
        return result.scalars().all()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        collection_info_id: Optional[int] = None,
        history_desc: Optional[str] = None
    ) -> tuple[List[ApiHistory], int]:
        """根据筛选条件获取历史记录列表"""
        query = select(ApiHistory)
        
        # 添加筛选条件
        if collection_info_id:
            query = query.where(ApiHistory.collection_info_id == collection_info_id)
        
        if history_desc:
            query = query.where(ApiHistory.history_desc.like(f"%{history_desc}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_history_crud = CRUDApiHistory(ApiHistory)
