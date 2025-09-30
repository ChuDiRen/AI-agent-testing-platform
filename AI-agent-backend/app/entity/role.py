# Copyright (c) 2025 左岚. All rights reserved.
"""
角色实体
严格按照博客t_role表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import BaseEntity


class Role(BaseEntity):
    """
    角色实体类 - 对应t_role表
    用于存储角色信息
    """
    __tablename__ = "role"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，没有别名
    
    # 角色名称 - 必填，最大10个字符
    role_name = Column(String(10), nullable=False, comment="角色名称")
    
    # 角色描述 - 可选，最大100个字符
    remark = Column(String(100), nullable=True, comment="角色描述")
    
    # 是否启用 - 必填，默认启用
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")
    
    # 创建时间 - 必填，默认当前时间
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    
    # 修改时间 - 可选，更新时自动设置
    modify_time = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 关联关系
    # 角色-用户关联（一个角色可以有多个用户）
    user_roles = relationship("UserRole", back_populates="role")

    # 角色-菜单关联（一个角色可以有多个菜单权限）
    role_menus = relationship("RoleMenu", back_populates="role")

    # 角色-API关联（一个角色可以有多个API权限）
    role_apis = relationship("RoleApi", back_populates="role")

    def __init__(self, role_name: str, remark: str = None, is_active: bool = True):
        """
        初始化角色
        
        Args:
            role_name: 角色名称
            remark: 角色描述
            is_active: 是否启用
        """
        self.role_name = role_name
        self.remark = remark
        self.is_active = is_active
        self.create_time = datetime.utcnow()

    def update_info(self, role_name: str = None, remark: str = None, is_active: bool = None):
        """
        更新角色信息
        
        Args:
            role_name: 新的角色名称
            remark: 新的角色描述
            is_active: 是否启用
        """
        if role_name is not None:
            self.role_name = role_name
        if remark is not None:
            self.remark = remark
        if is_active is not None:
            self.is_active = is_active
        self.modify_time = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            角色信息字典
        """
        return {
            "role_id": self.id,  # 修复：使用正确的属性名
            "role_name": self.role_name,
            "remark": self.remark,
            "is_active": self.is_active,
            "create_time": self.create_time.isoformat() if hasattr(self.create_time, 'isoformat') and self.create_time else str(self.create_time) if self.create_time else None,
            "modify_time": self.modify_time.isoformat() if hasattr(self.modify_time, 'isoformat') and self.modify_time else str(self.modify_time) if self.modify_time else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Role(role_id={self.id}, role_name='{self.role_name}')>"
