# Copyright (c) 2025 左岚. All rights reserved.
"""测试用例服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Tuple, Optional

from app.models.testcase import TestCase
from app.schemas.testcase import TestCaseCreate, TestCaseUpdate
from app.schemas.pagination import PaginationParams


class TestCaseService:
    """测试用例服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_testcase(self, testcase_data: TestCaseCreate, created_by: int) -> TestCase:
        """创建测试用例"""
        testcase = TestCase(
            **testcase_data.model_dump(),
            created_by=created_by
        )
        self.db.add(testcase)
        await self.db.commit()
        await self.db.refresh(testcase)
        return testcase
    
    async def get_testcase(self, testcase_id: int) -> Optional[TestCase]:
        """获取测试用例"""
        result = await self.db.execute(
            select(TestCase).where(TestCase.testcase_id == testcase_id)
        )
        return result.scalar_one_or_none()
    
    async def get_testcases_paginated(
        self,
        pagination: PaginationParams,
        test_type: Optional[str] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Tuple[List[TestCase], int]:
        """分页获取测试用例"""
        # 构建查询条件
        conditions = []
        if test_type:
            conditions.append(TestCase.test_type == test_type)
        if keyword:
            conditions.append(
                (TestCase.name.like(f"%{keyword}%")) |
                (TestCase.description.like(f"%{keyword}%"))
            )
        if status:
            conditions.append(TestCase.status == status)
        if priority:
            conditions.append(TestCase.priority == priority)
        
        # 查询总数
        count_query = select(func.count(TestCase.testcase_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 查询数据
        query = select(TestCase)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(TestCase.create_time.desc())
        query = query.offset(pagination.offset).limit(pagination.page_size)
        
        result = await self.db.execute(query)
        testcases = result.scalars().all()
        
        return list(testcases), total
    
    async def update_testcase(self, testcase_id: int, testcase_data: TestCaseUpdate) -> TestCase:
        """更新测试用例"""
        testcase = await self.get_testcase(testcase_id)
        if not testcase:
            raise ValueError("测试用例不存在")
        
        # 更新字段
        for field, value in testcase_data.model_dump(exclude_unset=True).items():
            setattr(testcase, field, value)
        
        await self.db.commit()
        await self.db.refresh(testcase)
        return testcase
    
    async def delete_testcase(self, testcase_id: int) -> bool:
        """删除测试用例"""
        testcase = await self.get_testcase(testcase_id)
        if not testcase:
            return False
        
        await self.db.delete(testcase)
        await self.db.commit()
        return True
    
    async def get_statistics(self, test_type: Optional[str] = None) -> dict:
        """获取统计信息"""
        conditions = []
        if test_type:
            conditions.append(TestCase.test_type == test_type)
        
        # 总数
        count_query = select(func.count(TestCase.testcase_id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 按状态统计
        status_query = select(
            TestCase.status,
            func.count(TestCase.testcase_id)
        ).group_by(TestCase.status)
        if conditions:
            status_query = status_query.where(and_(*conditions))
        status_result = await self.db.execute(status_query)
        status_stats = {row[0]: row[1] for row in status_result.fetchall()}
        
        # 按优先级统计
        priority_query = select(
            TestCase.priority,
            func.count(TestCase.testcase_id)
        ).group_by(TestCase.priority)
        if conditions:
            priority_query = priority_query.where(and_(*conditions))
        priority_result = await self.db.execute(priority_query)
        priority_stats = {row[0]: row[1] for row in priority_result.fetchall()}
        
        return {
            "total": total,
            "by_status": status_stats,
            "by_priority": priority_stats
        }

