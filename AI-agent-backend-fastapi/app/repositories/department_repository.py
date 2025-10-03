"""部门数据访问层"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.department import Department


class DepartmentRepository:
    """部门仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, dept: Department) -> Department:
        """创建部门"""
        self.db.add(dept)
        await self.db.commit()
        await self.db.refresh(dept)
        return dept
    
    async def get_by_id(self, dept_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        result = await self.db.execute(
            select(Department).where(Department.dept_id == dept_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Department]:
        """获取所有部门"""
        result = await self.db.execute(
            select(Department).offset(skip).limit(limit).order_by(Department.order_num)
        )
        return list(result.scalars().all())
    
    async def get_by_parent_id(self, parent_id: int) -> List[Department]:
        """根据父级ID获取部门"""
        result = await self.db.execute(
            select(Department).where(Department.parent_id == parent_id).order_by(Department.order_num)
        )
        return list(result.scalars().all())
    
    async def update(self, dept: Department) -> Department:
        """更新部门"""
        await self.db.commit()
        await self.db.refresh(dept)
        return dept
    
    async def delete(self, dept_id: int) -> bool:
        """删除部门"""
        result = await self.db.execute(
            delete(Department).where(Department.dept_id == dept_id)
        )
        await self.db.commit()
        return result.rowcount > 0

