"""
API资源 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import CRUDBase
from app.models.api_resource import ApiResource


class CRUDApiResource(CRUDBase[ApiResource, dict, dict]):
    """API资源 CRUD"""
    
    async def get_by_path_and_method(
        self,
        db: AsyncSession,
        path: str,
        method: str
    ) -> Optional[ApiResource]:
        """根据路径和方法获取API"""
        result = await db.execute(
            select(ApiResource).where(
                and_(ApiResource.path == path, ApiResource.method == method)
            )
        )
        return result.scalars().first()
    
    async def get_multi_by_tag(
        self,
        db: AsyncSession,
        tag: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ApiResource]:
        """根据标签获取API列表"""
        result = await db.execute(
            select(ApiResource)
            .where(ApiResource.tags.like(f"%{tag}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_page(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        path: Optional[str] = None,
        method: Optional[str] = None,
        tags: Optional[str] = None
    ) -> tuple[List[ApiResource], int]:
        """分页查询API资源"""
        query = select(ApiResource)
        
        # 条件过滤
        if path:
            query = query.where(ApiResource.path.like(f"%{path}%"))
        if method:
            query = query.where(ApiResource.method == method.upper())
        if tags:
            query = query.where(ApiResource.tags.like(f"%{tags}%"))
        
        # 获取总数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取数据
        result = await db.execute(
            query.offset(skip).limit(limit).order_by(ApiResource.id.desc())
        )
        items = result.scalars().all()
        
        return items, total
    
    async def create_batch(
        self,
        db: AsyncSession,
        api_list: List[dict]
    ) -> List[ApiResource]:
        """批量创建API"""
        db_objs = [ApiResource(**api) for api in api_list]
        db.add_all(db_objs)
        await db.commit()
        return db_objs


# 创建全局实例
api_resource = CRUDApiResource(ApiResource)
