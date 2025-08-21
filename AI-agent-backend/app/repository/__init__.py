# Copyright (c) 2025 左岚. All rights reserved.
# Repository Layer - 数据访问层
# 职责：封装所有数据库操作，提供CRUD方法，处理数据库连接和事务

from .base import BaseRepository
from .base_repository import BaseRepository as RBACBaseRepository
from .department_repository import DepartmentRepository
from .indicator_parameter_repository import IndicatorParameterRepository
from .menu_repository import MenuRepository
from .role_menu_repository import RoleMenuRepository
from .role_repository import RoleRepository
from .user_role_repository import UserRoleRepository

__all__ = [
    "BaseRepository",
    "RBACBaseRepository",
    "RoleRepository",
    "MenuRepository",
    "DepartmentRepository",
    "UserRoleRepository",
    "RoleMenuRepository",
    "IndicatorParameterRepository"
]
