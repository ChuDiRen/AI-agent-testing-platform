"""
API 项目管理 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.services.base import CRUDBase
from app.models.api_project import ApiProject
from app.schemas.api_project import ApiProjectCreate, ApiProjectUpdate


class CRUDApiProject(CRUDBase[ApiProject, ApiProjectCreate, ApiProjectUpdate]):
    """API 项目管理 CRUD"""
    
    async def get_by_name(self, db: AsyncSession, *, project_name: str) -> Optional[ApiProject]:
        """根据项目名称获取项目"""
        result = await db.execute(select(ApiProject).where(ApiProject.project_name == project_name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        project_name: Optional[str] = None
    ) -> tuple[List[ApiProject], int]:
        """根据筛选条件获取项目列表"""
        query = select(ApiProject)
        
        # 添加筛选条件
        if project_name:
            query = query.where(ApiProject.project_name.like(f"%{project_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_project_crud = CRUDApiProject(ApiProject)
