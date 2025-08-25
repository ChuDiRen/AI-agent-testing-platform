# Copyright (c) 2025 左岚. All rights reserved.
"""
角色菜单关联实体
严格按照博客t_role_menu表结构设计
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseEntity


class RoleMenu(BaseEntity):
    """
    角色菜单关联实体类 - 对应t_role_menu表
    用于关联角色和菜单表，实现多对多关系
    """
    __tablename__ = "role_menu"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 主键ID - 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 角色ID - 外键，关联角色表
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, comment="角色ID")

    # 菜单/按钮ID - 外键，关联菜单表
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False, comment="菜单/按钮ID")

    # 关联关系
    # 关联到角色实体
    role = relationship("Role", back_populates="role_menus")
    
    # 关联到菜单实体
    menu = relationship("Menu", back_populates="role_menus")

    def __init__(self, role_id: int, menu_id: int):
        """
        初始化角色菜单关联
        
        Args:
            role_id: 角色ID
            menu_id: 菜单ID
        """
        self.role_id = role_id
        self.menu_id = menu_id

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            角色菜单关联信息字典
        """
        return {
            "role_id": self.role_id,
            "menu_id": self.menu_id
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<RoleMenu(role_id={self.role_id}, menu_id={self.menu_id})>"
