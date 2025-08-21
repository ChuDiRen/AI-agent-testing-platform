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
from app.repository.base_repository import BaseRepository
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
        existing_user = self.db.query(User).filter(User.USERNAME == username).first()
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
        return self.db.query(User).filter(User.USERNAME == username).first()

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
        
        if not verify_password(password, user.PASSWORD):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        # 更新最后登录时间
        user.update_last_login()
        self.user_repository.update(user)
        
        logger.info(f"User authenticated successfully: {username}")
        return user

    def update_user(self, user_id: int, email: str = None, mobile: str = None,
                   ssex: str = None, avatar: str = None, description: str = None) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            email: 邮箱
            mobile: 手机号
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
            email=email,
            mobile=mobile,
            ssex=ssex,
            avatar=avatar,
            description=description
        )
        
        updated_user = self.user_repository.update(user)
        logger.info(f"Updated user: {user_id}")
        return updated_user

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
        if not verify_password(old_password, user.PASSWORD):
            logger.warning(f"Invalid old password for user: {user_id}")
            return False
        
        # 设置新密码
        hashed_new_password = get_password_hash(new_password)
        user.change_password(hashed_new_password)
        
        self.user_repository.update(user)
        logger.info(f"Password changed for user: {user_id}")
        return True

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
        return [user for user in users if keyword.lower() in user.USERNAME.lower()]
