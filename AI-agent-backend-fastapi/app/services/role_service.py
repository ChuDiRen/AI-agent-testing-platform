"""角色服务"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.repositories.role_repository import RoleRepository


class RoleService:
    """角色服务类"""

    def __init__(self, db: AsyncSession):
        self.role_repo = RoleRepository(db)
        self.db = db
    
    async def create_role(self, role_data: RoleCreate) -> Role:
        """创建角色"""
        from datetime import datetime

        # 检查角色名称是否已存在
        existing_role = await self.role_repo.get_by_name(role_data.role_name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )

        # 创建角色
        new_role = Role(
            role_name=role_data.role_name,
            remark=role_data.remark,
            create_time=datetime.now()
        )

        return await self.role_repo.create(new_role)
    
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        return role
    
    async def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取所有角色"""
        return await self.role_repo.get_all(skip=skip, limit=limit)
    
    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """更新角色"""
        from datetime import datetime

        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )

        # 更新字段
        if role_data.role_name is not None:
            # 检查名称是否重复
            existing_role = await self.role_repo.get_by_name(role_data.role_name)
            if existing_role and existing_role.role_id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色名称已被使用"
                )
            role.role_name = role_data.role_name

        if role_data.remark is not None:
            role.remark = role_data.remark

        role.modify_time = datetime.now()

        return await self.role_repo.update(role)
    
    async def delete_role(self, role_id: int) -> None:
        """删除角色"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        await self.role_repo.delete(role)

