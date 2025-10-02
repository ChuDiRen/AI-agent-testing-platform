"""部门业务逻辑层"""
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    """部门服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dept_repo = DepartmentRepository(db)
    
    async def create_department(self, dept_data: DepartmentCreate) -> Department:
        """创建部门"""
        dept = Department(
            **dept_data.model_dump(),
            create_time=datetime.now()
        )
        return await self.dept_repo.create(dept)
    
    async def get_department_by_id(self, dept_id: int) -> Department:
        """根据ID获取部门"""
        dept = await self.dept_repo.get_by_id(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="部门不存在")
        return dept
    
    async def get_all_departments(self, skip: int = 0, limit: int = 100) -> List[Department]:
        """获取所有部门"""
        return await self.dept_repo.get_all(skip=skip, limit=limit)
    
    async def update_department(self, dept_id: int, dept_data: DepartmentUpdate) -> Department:
        """更新部门"""
        dept = await self.get_department_by_id(dept_id)
        
        update_data = dept_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dept, field, value)
        
        dept.modify_time = datetime.now()
        return await self.dept_repo.update(dept)
    
    async def delete_department(self, dept_id: int) -> bool:
        """删除部门"""
        # 检查是否有子部门
        children = await self.dept_repo.get_by_parent_id(dept_id)
        if children:
            raise HTTPException(status_code=400, detail="存在子部门，无法删除")
        
        return await self.dept_repo.delete(dept_id)

