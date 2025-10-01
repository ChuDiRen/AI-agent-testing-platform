# Copyright (c) 2025 左岚. All rights reserved.
"""
角色API关联实体
按照role_menu表结构设计，用于角色和API的多对多关联
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseEntity


class RoleApi(BaseEntity):
    """
    角色API关联实体类 - 对应t_role_api表
    用于关联角色和API表，实现多对多关系
    """
    __tablename__ = "role_api"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 主键ID - 自增主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 角色ID - 外键，关联角色表
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, comment="角色ID")

    # API ID - 外键，关联API表
    api_id = Column(Integer, ForeignKey('api_endpoint.id'), nullable=False, comment="API ID")

    # 关联关系
    # 关联到角色实体
    role = relationship("Role", back_populates="role_apis")

    # 关联到API实体
    api = relationship("ApiEndpoint", back_populates="role_apis")

    def __init__(self, role_id: int, api_id: int):
        """
        初始化角色API关联
        
        Args:
            role_id: 角色ID
            api_id: API ID
        """
        self.role_id = role_id
        self.api_id = api_id

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            角色API关联信息字典
        """
        return {
            "role_id": self.role_id,
            "api_id": self.api_id
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<RoleApi(role_id={self.role_id}, api_id={self.api_id})>"
