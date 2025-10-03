"""数据库模型包 - 完全按照博客 RBAC 表结构设计"""
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.department import Department
from app.models.user_role import t_user_role, UserRole
from app.models.role_menu import t_role_menu
from app.models.log import OperationLog
from app.models.permission import Permission

__all__ = [
    "User",
    "Role",
    "Menu",
    "Department",
    "t_user_role",
    "UserRole",
    "t_role_menu",
    "OperationLog",
    "Permission",
]
