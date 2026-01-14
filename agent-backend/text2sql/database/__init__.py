"""
数据库管理模块 - 纯异步实现

提供多数据库支持和统一的操作接口
"""

from .db_manager import DatabaseManager, DatabaseConfig, register_connection
from .pagination import PaginationHandler
from .setup import setup_chinook

__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "PaginationHandler",
    "setup_chinook",
    "register_connection",
]
