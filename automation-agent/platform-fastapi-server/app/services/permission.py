"""
权限查询服务
提供用户权限查询相关的数据库操作
"""
from typing import List, Optional, Set
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.api_resource import ApiResource
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu
from app.models.role_api import RoleApi


class PermissionService:
    """权限查询服务"""
    
    @staticmethod
    async def get_user_roles(
        db: AsyncSession,
        user_id: int
    ) -> List[Role]:
        """获取用户的所有角色"""
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_menus(
        db: AsyncSession,
        user_id: int,
        include_hidden: bool = False
    ) -> List[Menu]:
        """获取用户有权访问的菜单"""
        from sqlalchemy import or_
        
        # 超级管理员拥有所有菜单
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalars().first()
        
        if user and user.is_superuser:
            query = select(Menu)
            if not include_hidden:
                query = query.where(Menu.is_hidden == False)
        else:
            # 普通用户只能访问角色关联的菜单
            query = (
                select(Menu)
                .join(RoleMenu, Menu.id == RoleMenu.menu_id)
                .join(UserRole, RoleMenu.role_id == UserRole.role_id)
                .where(UserRole.user_id == user_id)
            )
            if not include_hidden:
                query = query.where(Menu.is_hidden == False)
        
        query = query.order_by(Menu.order.asc())
        
        result = await db.execute(query)
        menus = result.scalars().all()
        
        # 构建菜单树
        menu_dict = {menu.id: menu for menu in menus}
        root_menus = []
        
        for menu in menus:
            menu_dict[menu.id] = menu
            if menu.parent_id == 0:
                root_menus.append(menu)
        
        # 建立父子关系
        for menu in menus:
            if menu.parent_id != 0 and menu.parent_id in menu_dict:
                parent = menu_dict[menu.parent_id]
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(menu)
        
        return root_menus
    
    @staticmethod
    async def get_user_apis(
        db: AsyncSession,
        user_id: int
    ) -> List[ApiResource]:
        """获取用户有权访问的API"""
        # 超级管理员拥有所有API
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalars().first()
        
        if user and user.is_superuser:
            result = await db.execute(
                select(ApiResource)
            )
            return result.scalars().all()
        
        # 普通用户只能访问角色关联的API
        result = await db.execute(
            select(ApiResource)
            .distinct()
            .join(RoleApi, ApiResource.id == RoleApi.api_id)
            .join(UserRole, RoleApi.role_id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_api_permissions(
        db: AsyncSession,
        user_id: int
    ) -> Set[str]:
        """获取用户的API权限标识集合（格式：method+path）"""
        apis = await PermissionService.get_user_apis(db, user_id)
        
        # 生成权限标识：小写方法 + 路径
        permissions = {
            f"{api.method.lower()}{api.path}"
            for api in apis
        }
        
        return permissions
    
    @staticmethod
    async def check_menu_permission(
        db: AsyncSession,
        user_id: int,
        menu_path: str
    ) -> bool:
        """检查用户是否有权访问菜单"""
        from sqlalchemy import exists
        
        # 超级管理员拥有所有权限
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalars().first()
        if user and user.is_superuser:
            return True
        
        # 检查用户角色是否关联该菜单
        result = await db.execute(
            select(exists().where(
                and_(
                    UserRole.user_id == user_id,
                    RoleMenu.role_id == UserRole.role_id,
                    Menu.id == RoleMenu.menu_id,
                    Menu.path == menu_path
                )
            ))
        )
        return result.scalar() or False
    
    @staticmethod
    async def check_api_permission(
        db: AsyncSession,
        user_id: int,
        api_path: str,
        api_method: str
    ) -> bool:
        """检查用户是否有权访问API"""
        from sqlalchemy import exists
        
        # 超级管理员拥有所有权限
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalars().first()
        if user and user.is_superuser:
            return True
        
        # 检查用户角色是否关联该API
        result = await db.execute(
            select(exists().where(
                and_(
                    UserRole.user_id == user_id,
                    RoleApi.role_id == UserRole.role_id,
                    ApiResource.id == RoleApi.api_id,
                    ApiResource.path == api_path,
                    ApiResource.method == api_method.upper()
                )
            ))
        )
        return result.scalar() or False


# 创建全局实例
permission = PermissionService()
