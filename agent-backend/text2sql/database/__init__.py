"""
数据库管理模块

提供多数据库支持和统一的操作接口
"""

from .db_manager import DatabaseManager, DatabaseConfig, setup_chinook, register_connection
from .pagination import PaginationHandler

__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "PaginationHandler",
    "setup_chinook",
    "register_connection",
]
