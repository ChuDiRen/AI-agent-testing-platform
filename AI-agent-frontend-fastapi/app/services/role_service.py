"""角色服务"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository


class RoleService:
    """角色服务类"""
    
    def __init__(self, db: AsyncSession):
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.db = db
    
    async def create_role(self, role_data: RoleCreate) -> Role:
        """创建角色"""
        # 检查角色代码是否已存在
        existing_role = await self.role_repo.get_by_code(role_data.code)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色代码已存在"
            )
        
        # 创建角色
        new_role = Role(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description
        )
        
        # 关联权限
        if role_data.permission_ids:
            permissions = await self.permission_repo.get_by_ids(role_data.permission_ids)
            new_role.permissions = permissions
        
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
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 更新字段
        if role_data.name is not None:
            role.name = role_data.name
        
        if role_data.code is not None:
            # 检查代码是否重复
            existing_role = await self.role_repo.get_by_code(role_data.code)
            if existing_role and existing_role.id != role_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="角色代码已被使用"
                )
            role.code = role_data.code
        
        if role_data.description is not None:
            role.description = role_data.description
        
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        
        # 更新权限关联
        if role_data.permission_ids is not None:
            permissions = await self.permission_repo.get_by_ids(role_data.permission_ids)
            role.permissions = permissions
        
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

