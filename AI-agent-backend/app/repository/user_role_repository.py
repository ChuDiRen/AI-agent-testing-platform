# Copyright (c) 2025 左岚. All rights reserved.
"""
用户角色关联Repository
实现用户角色关联相关的数据访问操作
"""

from typing import List

from sqlalchemy.orm import Session

from app.entity.role import Role
from app.entity.user_role import UserRole
from app.repository.base import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    """
    用户角色关联Repository类
    提供用户角色关联相关的数据库操作方法
    """

    def __init__(self, db: Session):
        """
        初始化用户角色关联Repository
        
        Args:
            db: 数据库会话
        """
        super().__init__(db, UserRole)

    def get_by_user_id(self, user_id: int) -> List[UserRole]:
        """
        根据用户ID查询用户角色关联
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户角色关联列表
        """
        return self.db.query(UserRole).filter(UserRole.user_id == user_id).all()

    def get_by_role_id(self, role_id: int) -> List[UserRole]:
        """
        根据角色ID查询用户角色关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            用户角色关联列表
        """
        return self.db.query(UserRole).filter(UserRole.role_id == role_id).all()

    def get_roles_by_user_id(self, user_id: int) -> List[Role]:
        """
        根据用户ID获取用户的所有角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            角色列表
        """
        return self.db.query(Role).join(
            UserRole, Role.role_id == UserRole.role_id
        ).filter(UserRole.user_id == user_id).all()

    def exists(self, user_id: int, role_id: int) -> bool:
        """
        检查用户角色关联是否存在
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            True表示存在，False表示不存在
        """
        return self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first() is not None

    def delete_by_user_id(self, user_id: int) -> int:
        """
        删除用户的所有角色关联
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(UserRole).filter(UserRole.user_id == user_id).count()
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        return count

    def delete_by_role_id(self, role_id: int) -> int:
        """
        删除角色的所有用户关联
        
        Args:
            role_id: 角色ID
            
        Returns:
            删除的记录数
        """
        count = self.db.query(UserRole).filter(UserRole.role_id == role_id).count()
        self.db.query(UserRole).filter(UserRole.role_id == role_id).delete()
        return count

    def delete_specific(self, user_id: int, role_id: int) -> bool:
        """
        删除特定的用户角色关联
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            True表示删除成功，False表示记录不存在
        """
        result = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).delete()
        return result > 0

    def assign_roles_to_user(self, user_id: int, role_ids: List[int]) -> None:
        """
        为用户分配角色（先清除原有角色，再分配新角色）
        
        Args:
            user_id: 用户ID
            role_ids: 角色ID列表
        """
        # 先删除用户的所有角色
        self.delete_by_user_id(user_id)
        
        # 分配新角色
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)

    def add_role_to_user(self, user_id: int, role_id: int) -> bool:
        """
        为用户添加角色（如果不存在的话）
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            True表示添加成功，False表示已存在
        """
        if self.exists(user_id, role_id):
            return False
        
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        return True
