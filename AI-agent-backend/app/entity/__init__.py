# Copyright (c) 2025 左岚. All rights reserved.
# Entity Layer - 数据库实体层
# 职责：定义数据库表结构，提供实体对象与字典的转换方法

from .base import BaseEntity
from .department import Department
from .menu import Menu
from .role import Role
from .role_menu import RoleMenu
from .user import User
from .user_role import UserRole

__all__ = [
    "BaseEntity",
    "User",
    "Role",
    "Menu",
    "Department",
    "UserRole",
    "RoleMenu"
]
