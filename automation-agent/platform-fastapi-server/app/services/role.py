"""
角色 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.services.base import CRUDBase
from app.models.role import Role
from app.models.user import User


class CRUDRole(CRUDBase[Role, dict, dict]):
    """角色 CRUD"""
    
    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Role]:
        """根据角色名称获取角色"""
        result = await db.execute(
            select(Role).filter(Role.name == name)
        )
        return result.scalars().first()
    
    async def get_multi_with_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """获取角色列表，包含用户数量"""
        # 使用子查询统计每个角色的用户数量
        subquery = (
            select(func.count(User.id))
            .where(User.id.in_(
                select(User.id)
                .join(UserRole, User.id == UserRole.user_id)
                .where(UserRole.role_id == Role.id)
            ))
            .label("user_count")
        )
        
        result = await db.execute(
            select(Role, subquery)
            .offset(skip)
            .limit(limit)
            .order_by(Role.id.desc())
        )
        return result.all()
    
    async def get_with_users_and_menus_and_apis(
        self,
        db: AsyncSession,
        role_id: int
    ) -> Optional[Role]:
        """获取角色及其关联的用户、菜单、API"""
        from app.models.user_role import UserRole
        from app.models.role_menu import RoleMenu
        from app.models.role_api import RoleApi
        from app.models.menu import Menu
        from app.models.api_resource import ApiResource
        
        result = await db.execute(
            select(Role)
            .options(
                selectinload(Role.users).selectinload(UserRole.user),
                selectinload(Role.menus).selectinload(RoleMenu.menu),
                selectinload(Role.apis).selectinload(RoleApi.api)
            )
            .where(Role.id == role_id)
        )
        return result.scalars().first()


# 创建全局实例
role = CRUDRole(Role)
