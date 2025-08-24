# Copyright (c) 2025 左岚. All rights reserved.
"""
角色实体
严格按照博客t_role表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .base import BaseEntity


class Role(BaseEntity):
    """
    角色实体类 - 对应t_role表
    用于存储角色信息
    """
    __tablename__ = "role"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 角色ID - 主键，自增
    role_id = Column(Integer, primary_key=True, comment="角色ID")
    
    # 角色名称 - 必填，最大10个字符
    role_name = Column(String(10), nullable=False, comment="角色名称")
    
    # 角色描述 - 可选，最大100个字符
    remark = Column(String(100), nullable=True, comment="角色描述")
    
    # 创建时间 - 必填，默认当前时间
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    
    # 修改时间 - 可选，更新时自动设置
    modify_time = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 关联关系
    # 角色-用户关联（一个角色可以有多个用户）
    user_roles = relationship("UserRole", back_populates="role")
    
    # 角色-菜单关联（一个角色可以有多个菜单权限）
    role_menus = relationship("RoleMenu", back_populates="role")

    def __init__(self, role_name: str, remark: str = None):
        """
        初始化角色
        
        Args:
            role_name: 角色名称
            remark: 角色描述
        """
        self.role_name = role_name
        self.remark = remark
        self.create_time = datetime.utcnow()

    def update_info(self, role_name: str = None, remark: str = None):
        """
        更新角色信息
        
        Args:
            role_name: 新的角色名称
            remark: 新的角色描述
        """
        if role_name is not None:
            self.role_name = role_name
        if remark is not None:
            self.remark = remark
        self.modify_time = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            角色信息字典
        """
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "modify_time": self.modify_time.isoformat() if self.modify_time else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Role(role_id={self.role_id}, role_name='{self.role_name}')>"
