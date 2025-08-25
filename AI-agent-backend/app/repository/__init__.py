# Copyright (c) 2025 左岚. All rights reserved.
# Repository Layer - 数据访问层
# 职责：封装所有数据库操作，提供CRUD方法，处理数据库连接和事务

from .audit_log_repository import AuditLogRepository
from .base import BaseRepository
from .data_permission_repository import DataPermissionRepository
from .department_repository import DepartmentRepository
from .menu_repository import MenuRepository
from .role_menu_repository import RoleMenuRepository
from .role_repository import RoleRepository
from .user_role_repository import UserRoleRepository

__all__ = [
    "BaseRepository",
    "RoleRepository",
    "MenuRepository",
    "DepartmentRepository",
    "UserRoleRepository",
    "RoleMenuRepository",
    "AuditLogRepository",
    "DataPermissionRepository"
]
