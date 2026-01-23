"""
部门 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.dept import Dept


class CRUDDept(CRUDBase[Dept, dict, dict]):
    """部门 CRUD"""
    
    async def get_tree(
        self,
        db: AsyncSession,
        parent_id: int = 0,
        is_deleted: Optional[bool] = False
    ) -> List[Dept]:
        """获取部门树"""
        query = select(Dept).where(Dept.parent_id == parent_id)
        
        if is_deleted is not None:
            query = query.where(Dept.is_deleted == is_deleted)
        
        query = query.order_by(Dept.order.asc())
        
        result = await db.execute(query)
        depts = result.scalars().all()
        
        # 递归获取子部门
        for dept in depts:
            dept.children = await self.get_tree(db, dept.id, is_deleted)
        
        return depts
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dept]:
        """获取所有部门"""
        result = await db.execute(
            select(Dept)
            .where(Dept.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(Dept.order.asc())
        )
        return result.scalars().all()
    
    async def get_children(
        self,
        db: AsyncSession,
        parent_id: int
    ) -> List[Dept]:
        """获取子部门"""
        result = await db.execute(
            select(Dept)
            .where(Dept.parent_id == parent_id)
            .where(Dept.is_deleted == False)
            .order_by(Dept.order.asc())
        )
        return result.scalars().all()
    
    async def has_children(
        self,
        db: AsyncSession,
        parent_id: int
    ) -> bool:
        """检查是否有子部门"""
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(Dept.id))
            .where(Dept.parent_id == parent_id)
            .where(Dept.is_deleted == False)
        )
        count = result.scalar()
        return count > 0


# 创建全局实例
dept = CRUDDept(Dept)
