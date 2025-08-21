"""
用户实体
定义用户相关的数据库模型
"""

from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from .base import BaseEntity


class User(BaseEntity):
    """
    用户实体类
    定义用户的基本信息和行为
    """
    __tablename__ = "users"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, comment="手机号")
    
    # 认证信息
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_superuser = Column(Boolean, default=False, comment="是否超级用户")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    
    # 个人信息
    full_name = Column(String(100), comment="全名")
    avatar = Column(String(255), comment="头像URL")
    bio = Column(Text, comment="个人简介")
    
    # 时间信息
    last_login_at = Column(DateTime, comment="最后登录时间")
    password_changed_at = Column(DateTime, default=datetime.utcnow, comment="密码修改时间")
    
    # 关联关系（示例）
    # roles = relationship("UserRole", back_populates="user")
    # profiles = relationship("UserProfile", back_populates="user")

    def validate(self) -> bool:
        """
        验证用户数据的有效性
        """
        if not self.username or len(self.username) < 3:
            return False
        if not self.email or "@" not in self.email:
            return False
        if self.phone and len(self.phone) < 10:
            return False
        return True

    def before_save(self) -> None:
        """
        保存前的处理
        """
        super().before_save()
        # 确保邮箱和用户名为小写
        if self.email:
            self.email = self.email.lower()
        if self.username:
            self.username = self.username.lower()

    def update_last_login(self) -> None:
        """
        更新最后登录时间
        """
        self.last_login_at = datetime.utcnow()

    def change_password(self, new_hashed_password: str) -> None:
        """
        修改密码
        """
        self.hashed_password = new_hashed_password
        self.password_changed_at = datetime.utcnow()

    def activate(self) -> None:
        """
        激活用户
        """
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """
        停用用户
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def verify(self) -> None:
        """
        验证用户
        """
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def is_admin(self) -> bool:
        """
        检查是否为管理员
        """
        return self.is_superuser

    def can_login(self) -> bool:
        """
        检查是否可以登录
        """
        return self.is_active and not self.is_soft_deleted()

    def get_display_name(self) -> str:
        """
        获取显示名称
        """
        return self.full_name or self.username

    def to_dict_safe(self) -> dict:
        """
        安全的字典转换（不包含敏感信息）
        """
        data = self.to_dict()
        # 移除敏感字段
        data.pop('hashed_password', None)
        return data

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
