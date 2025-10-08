# Copyright (c) 2025 左岚. All rights reserved.
"""
测试用例服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Tuple, Optional
import copy

from ..models.case import ApiEngineCase
from ..schemas.case import CaseCreate, CaseUpdate


class CaseService:
    """用例服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_case(self, case_data: CaseCreate, created_by: int) -> ApiEngineCase:
        """创建用例"""
        case = ApiEngineCase(
            **case_data.model_dump(),
            created_by=created_by
        )
        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        return case
    
    async def get_case(self, case_id: int) -> Optional[ApiEngineCase]:
        """获取用例"""
        result = await self.db.execute(
            select(ApiEngineCase).where(ApiEngineCase.case_id == case_id)
        )
        return result.scalar_one_or_none()
    
    async def get_cases_by_suite(
        self,
        suite_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[ApiEngineCase], int]:
        """获取套件下的用例列表"""
        # 获取总数
        count_query = select(func.count(ApiEngineCase.case_id)).where(
            ApiEngineCase.suite_id == suite_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 获取数据
        query = select(ApiEngineCase).where(ApiEngineCase.suite_id == suite_id)
        query = query.order_by(ApiEngineCase.sort_order, ApiEngineCase.created_at)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        cases = list(result.scalars().all())
        
        return cases, total
    
    async def get_cases(
        self,
        page: int = 1,
        page_size: int = 20,
        suite_id: Optional[int] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[ApiEngineCase], int]:
        """获取用例列表"""
        query = select(ApiEngineCase)
        
        # 构建条件
        conditions = []
        if suite_id:
            conditions.append(ApiEngineCase.suite_id == suite_id)
        if keyword:
            conditions.append(
                (ApiEngineCase.name.like(f"%{keyword}%")) |
                (ApiEngineCase.description.like(f"%{keyword}%"))
            )
        if status:
            conditions.append(ApiEngineCase.status == status)
        
        if conditions:
            for condition in conditions:
                query = query.where(condition)
        
        # 获取总数
        count_query = select(func.count(ApiEngineCase.case_id))
        if conditions:
            for condition in conditions:
                count_query = count_query.where(condition)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 获取数据
        query = query.order_by(ApiEngineCase.sort_order, ApiEngineCase.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        cases = list(result.scalars().all())
        
        return cases, total
    
    async def update_case(self, case_id: int, case_data: CaseUpdate) -> Optional[ApiEngineCase]:
        """更新用例"""
        case = await self.get_case(case_id)
        if not case:
            return None
        
        for field, value in case_data.model_dump(exclude_unset=True).items():
            setattr(case, field, value)
        
        await self.db.commit()
        await self.db.refresh(case)
        return case
    
    async def delete_case(self, case_id: int) -> bool:
        """删除用例"""
        case = await self.get_case(case_id)
        if not case:
            return False
        
        await self.db.delete(case)
        await self.db.commit()
        return True
    
    async def clone_case(self, case_id: int, created_by: int) -> Optional[ApiEngineCase]:
        """克隆用例"""
        original_case = await self.get_case(case_id)
        if not original_case:
            return None
        
        # 创建副本
        case_data = {
            "suite_id": original_case.suite_id,
            "name": f"{original_case.name} (副本)",
            "description": original_case.description,
            "config_type": original_case.config_type,
            "config_data": copy.deepcopy(original_case.config_data) if original_case.config_data else None,
            "yaml_content": original_case.yaml_content,
            "sort_order": original_case.sort_order,
            "status": "draft",
            "tags": original_case.tags,
            "created_by": created_by
        }
        
        new_case = ApiEngineCase(**case_data)
        self.db.add(new_case)
        await self.db.commit()
        await self.db.refresh(new_case)
        
        return new_case
    
    async def import_from_yaml(
        self,
        suite_id: int,
        yaml_content: str,
        created_by: int
    ) -> ApiEngineCase:
        """从YAML导入用例"""
        import yaml
        
        # 解析YAML
        case_config = yaml.safe_load(yaml_content)
        
        case_data = {
            "suite_id": suite_id,
            "name": case_config.get("desc", "导入的用例"),
            "description": case_config.get("desc", ""),
            "config_type": "yaml",
            "config_data": None,
            "yaml_content": yaml_content,
            "sort_order": 0,
            "status": "draft",
            "created_by": created_by
        }
        
        case = ApiEngineCase(**case_data)
        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        
        return case

