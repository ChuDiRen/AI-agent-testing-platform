"""
API 关键字管理 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.api_keyword import ApiKeyWord
from app.schemas.api_keyword import ApiKeyWordCreate, ApiKeyWordUpdate


class CRUDApiKeyWord(CRUDBase[ApiKeyWord, ApiKeyWordCreate, ApiKeyWordUpdate]):
    """API 关键字管理 CRUD"""
    
    async def get_by_operation_type_id(self, db: AsyncSession, *, operation_type_id: int) -> List[ApiKeyWord]:
        """根据操作类型ID获取关键字"""
        result = await db.execute(select(ApiKeyWord).where(ApiKeyWord.operation_type_id == operation_type_id))
        return result.scalars().all()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        name: Optional[str] = None,
        operation_type_id: Optional[int] = None,
        page_id: Optional[int] = None
    ) -> tuple[List[ApiKeyWord], int]:
        """根据筛选条件获取关键字列表"""
        query = select(ApiKeyWord)
        
        # 添加筛选条件
        if name:
            query = query.where(ApiKeyWord.name.like(f"%{name}%"))
        
        if operation_type_id:
            query = query.where(ApiKeyWord.operation_type_id == operation_type_id)
        
        if page_id:
            query = query.where(ApiKeyWord.page_id == page_id)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_keyword_crud = CRUDApiKeyWord(ApiKeyWord)
