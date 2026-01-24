"""
API 测试用例信息 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.services.base import CRUDBase
from app.models.api_info_case import ApiInfoCase
from app.schemas.api_info_case import ApiInfoCaseCreate, ApiInfoCaseUpdate


class CRUDApiInfoCase(CRUDBase[ApiInfoCase, ApiInfoCaseCreate, ApiInfoCaseUpdate]):
    """API 测试用例信息 CRUD"""
    
    async def get_by_project_id(self, db: AsyncSession, *, project_id: int) -> List[ApiInfoCase]:
        """根据项目ID获取测试用例"""
        result = await db.execute(select(ApiInfoCase).where(ApiInfoCase.project_id == project_id))
        return result.scalars().all()
    
    async def get_by_module_id(self, db: AsyncSession, *, module_id: int) -> List[ApiInfoCase]:
        """根据模块ID获取测试用例"""
        result = await db.execute(select(ApiInfoCase).where(ApiInfoCase.module_id == module_id))
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, case_name: str) -> Optional[ApiInfoCase]:
        """根据用例名称获取测试用例"""
        result = await db.execute(select(ApiInfoCase).where(ApiInfoCase.case_name == case_name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        project_id: Optional[int] = None,
        case_name: Optional[str] = None
    ) -> tuple[List[ApiInfoCase], int]:
        """根据筛选条件获取测试用例列表"""
        query = select(ApiInfoCase)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiInfoCase.project_id == project_id)
        
        if case_name:
            query = query.where(ApiInfoCase.case_name.like(f"%{case_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


api_info_case_crud = CRUDApiInfoCase(ApiInfoCase)
