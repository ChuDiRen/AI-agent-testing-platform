# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC用户Service
实现用户相关的RBAC业务逻辑
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.security import get_password_hash, verify_password
from app.entity.role import Role
from app.entity.user import User
from app.repository.base import BaseRepository
from app.repository.role_repository import RoleRepository
from app.repository.user_role_repository import UserRoleRepository

logger = get_logger(__name__)


class RBACUserService:
    """
    RBAC用户Service类
    提供用户相关的RBAC业务逻辑处理
    """

    def __init__(self, db: Session):
        """
        初始化RBAC用户Service
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.user_repository = BaseRepository(db, User)
        self.user_role_repository = UserRoleRepository(db)
        self.role_repository = RoleRepository(db)

    def create_user(self, username: str, password: str, email: str = None,
                   mobile: str = None, dept_id: int = None, ssex: str = None,
                   avatar: str = None, description: str = None) -> User:
        """
        创建用户
        
        Args:
            username: 用户名
            password: 明文密码
            email: 邮箱
            mobile: 手机号
            dept_id: 部门ID
            ssex: 性别，'0'男 '1'女 '2'保密
            avatar: 头像
            description: 描述
            
        Returns:
            创建的用户对象
            
        Raises:
            ValueError: 用户名已存在
        """
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError(f"用户名 '{username}' 已存在")
        
        # 加密密码
        hashed_password = get_password_hash(password)
        
        # 创建用户
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            mobile=mobile,
            dept_id=dept_id,
            ssex=ssex,
            avatar=avatar,
            description=description
        )
        
        created_user = self.user_repository.create(user)
        logger.info(f"Created user: {username}")
        return created_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        return self.user_repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.username == username).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 明文密码
            
        Returns:
            认证成功的用户对象或None
        """
        user = self.get_user_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        if not user.is_active():
            logger.warning(f"User is locked: {username}")
            return None
        
        if not verify_password(password, user.password):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        # 更新最后登录时间
        user.update_last_login()
        # 直接提交数据库会话，因为user对象已经被修改
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User authenticated successfully: {username}")
        return user

    def update_user(self, user_id: int, username: str = None, email: str = None, mobile: str = None,
                   dept_id: int = None, status: str = None, ssex: str = None, avatar: str = None, description: str = None) -> Optional[User]:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱
            mobile: 手机号
            dept_id: 部门ID
            status: 状态
            ssex: 性别
            avatar: 头像
            description: 描述

        Returns:
            更新后的用户对象或None
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return None

        # 更新用户信息
        user.update_info(
            username=username,
            email=email,
            mobile=mobile,
            dept_id=dept_id,
            status=status,
            ssex=ssex,
            avatar=avatar,
            description=description
        )

        # 提交更改到数据库
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated user: {user_id}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            是否修改成功
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False
        
        # 验证旧密码
        if not verify_password(old_password, user.password):
            logger.warning(f"Invalid old password for user: {user_id}")
            return False
        
        # 设置新密码
        hashed_new_password = get_password_hash(new_password)
        user.change_password(hashed_new_password)
        
        self.user_repository.update(user)
        logger.info(f"Password changed for user: {user_id}")
        return True

    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        try:
            # 检查用户是否存在
            user = self.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found with id: {user_id}")
                return False
            
            # 先删除用户角色关联
            self.user_role_repository.delete_by_user_id(user_id)
            
            # 删除用户
            self.user_repository.delete(user_id)
            
            self.db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False

    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        管理员重置用户密码（无需旧密码）
        
        Args:
            user_id: 用户ID
            new_password: 新密码
            
        Returns:
            是否重置成功
        """
        try:
            logger.info(f"Starting password reset for user: {user_id}")
            # 查找用户 - 使用id字段而不是user_id
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found with id: {user_id}")
                return False
            
            logger.info(f"Found user: {user.username}, current password hash length: {len(user.password) if user.password else 'None'}")
            
            # 直接设置新密码（管理员权限，无需验证旧密码）
            hashed_new_password = get_password_hash(new_password)
            logger.info(f"Generated new password hash length: {len(hashed_new_password)}")
            
            user.change_password(hashed_new_password)
            logger.info(f"Password updated in entity for user: {user_id}")
            
            # 提交数据库更改
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Password reset completed successfully for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error in reset_password for user {user_id}: {str(e)}")
            return False

    def lock_user(self, user_id: int) -> bool:
        """
        锁定用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否锁定成功
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False
        
        user.lock_user()
        self.user_repository.update(user)
        
        logger.info(f"User locked: {user_id}")
        return True

    def unlock_user(self, user_id: int) -> bool:
        """
        解锁用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否解锁成功
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            return False
        
        user.unlock_user()
        self.user_repository.update(user)
        
        logger.info(f"User unlocked: {user_id}")
        return True

    def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_ids: 角色ID列表
            
        Returns:
            是否分配成功
        """
        try:
            # 检查用户是否存在
            user = self.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found with id: {user_id}")
                return False
            
            # 检查所有角色是否存在
            for role_id in role_ids:
                role = self.role_repository.get_by_id(role_id)
                if not role:
                    logger.warning(f"Role not found with id: {role_id}")
                    return False
            
            # 分配角色
            self.user_role_repository.assign_roles_to_user(user_id, role_ids)
            self.db.commit()
            
            logger.info(f"Assigned {len(role_ids)} roles to user: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning roles to user {user_id}: {str(e)}")
            return False

    def get_user_roles(self, user_id: int) -> List[Role]:
        """
        获取用户的角色列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            角色列表
        """
        return self.user_role_repository.get_roles_by_user_id(user_id)

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        获取用户的权限标识列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            权限标识列表
        """
        from app.service.menu_service import MenuService
        
        menu_service = MenuService(self.db)
        return menu_service.get_user_permissions(user_id)

    def has_permission(self, user_id: int, permission: str) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            user_id: 用户ID
            permission: 权限标识
            
        Returns:
            是否有权限
        """
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions

    def get_all_users(self) -> List[User]:
        """
        获取所有用户
        
        Returns:
            用户列表
        """
        return self.user_repository.get_all()

    def search_users(self, keyword: str) -> List[User]:
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的用户列表
        """
        # 这里可以根据用户名、邮箱等字段搜索
        # 简化实现，只按用户名搜索
        users = self.user_repository.get_all()
        return [user for user in users if keyword.lower() in user.username.lower()]

    def get_role_menus(self, role_id: int):
        """
        获取角色的菜单权限
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色菜单关联列表
        """
        from app.repository.role_menu_repository import RoleMenuRepository
        role_menu_repository = RoleMenuRepository(self.db)
        return role_menu_repository.get_menus_by_role_id(role_id)

    def get_menus_by_ids(self, menu_ids: List[int]):
        """
        根据菜单ID列表获取菜单
        
        Args:
            menu_ids: 菜单ID列表
            
        Returns:
            菜单列表
        """
        from app.entity.menu import Menu
        return self.db.query(Menu).filter(Menu.id.in_(menu_ids)).all()  # 修复：使用正确的属性名

    def get_all_menus(self):
        """
        获取所有菜单
        
        Returns:
            菜单列表
        """
        from app.entity.menu import Menu
        return self.db.query(Menu).all()

    def get_users_by_role(self, role_id: int):
        """
        获取拥有指定角色的用户
        
        Args:
            role_id: 角色ID
            
        Returns:
            用户角色关联列表
        """
        return self.user_role_repository.get_users_by_role_id(role_id)

    def assign_role_to_user(self, user_id: int, role_id: int) -> bool:
        """
        为用户分配单个角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            是否分配成功
        """
        try:
            self.user_role_repository.assign_role_to_user(user_id, role_id)
            self.db.commit()
            logger.info(f"Assigned role {role_id} to user {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error assigning role to user: {str(e)}")
            return False

    def clear_user_roles(self, user_id: int) -> bool:
        """
        清除用户的所有角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否清除成功
        """
        try:
            self.user_role_repository.remove_all_roles_from_user(user_id)
            self.db.commit()
            logger.info(f"Cleared all roles for user {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing user roles: {str(e)}")
            return False
