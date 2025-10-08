# Copyright (c) 2025 左岚. All rights reserved.
"""
测试套件服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Tuple, Optional

from ..models.suite import ApiEngineSuite
from ..schemas.suite import SuiteCreate, SuiteUpdate


class SuiteService:
    """套件服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_suite(self, suite_data: SuiteCreate, created_by: int) -> ApiEngineSuite:
        """创建套件"""
        suite = ApiEngineSuite(
            **suite_data.model_dump(),
            created_by=created_by
        )
        self.db.add(suite)
        await self.db.commit()
        await self.db.refresh(suite)
        return suite
    
    async def get_suite(self, suite_id: int) -> Optional[ApiEngineSuite]:
        """获取套件"""
        result = await self.db.execute(
            select(ApiEngineSuite).where(ApiEngineSuite.suite_id == suite_id)
        )
        return result.scalar_one_or_none()
    
    async def get_suites(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None
    ) -> Tuple[List[ApiEngineSuite], int]:
        """获取套件列表"""
        # 构建查询
        query = select(ApiEngineSuite)
        
        if keyword:
            query = query.where(
                (ApiEngineSuite.name.like(f"%{keyword}%")) |
                (ApiEngineSuite.description.like(f"%{keyword}%"))
            )
        
        # 获取总数
        count_query = select(func.count(ApiEngineSuite.suite_id))
        if keyword:
            count_query = count_query.where(
                (ApiEngineSuite.name.like(f"%{keyword}%")) |
                (ApiEngineSuite.description.like(f"%{keyword}%"))
            )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 获取数据
        query = query.order_by(ApiEngineSuite.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        suites = list(result.scalars().all())
        
        return suites, total
    
    async def update_suite(self, suite_id: int, suite_data: SuiteUpdate) -> Optional[ApiEngineSuite]:
        """更新套件"""
        suite = await self.get_suite(suite_id)
        if not suite:
            return None
        
        for field, value in suite_data.model_dump(exclude_unset=True).items():
            setattr(suite, field, value)
        
        await self.db.commit()
        await self.db.refresh(suite)
        return suite
    
    async def delete_suite(self, suite_id: int) -> bool:
        """删除套件"""
        suite = await self.get_suite(suite_id)
        if not suite:
            return False
        
        await self.db.delete(suite)
        await self.db.commit()
        return True

