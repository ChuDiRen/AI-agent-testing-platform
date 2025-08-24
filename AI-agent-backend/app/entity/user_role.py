# Copyright (c) 2025 左岚. All rights reserved.
"""
用户角色关联实体
严格按照博客t_user_role表结构设计
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseEntity


class UserRole(BaseEntity):
    """
    用户角色关联实体类 - 对应t_user_role表
    用于关联用户和角色表，实现多对多关系
    """
    __tablename__ = "user_role"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 用户ID - 外键，关联用户表
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True, comment="用户ID")

    # 角色ID - 外键，关联角色表
    role_id = Column(Integer, ForeignKey('role.role_id'), primary_key=True, comment="角色ID")

    # 关联关系
    # 关联到用户实体
    user = relationship("User", back_populates="user_roles")
    
    # 关联到角色实体
    role = relationship("Role", back_populates="user_roles")

    def __init__(self, user_id: int, role_id: int):
        """
        初始化用户角色关联
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
        """
        self.user_id = user_id
        self.role_id = role_id

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            用户角色关联信息字典
        """
        return {
            "user_id": self.user_id,
            "role_id": self.role_id
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
