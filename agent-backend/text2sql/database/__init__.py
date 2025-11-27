"""
数据库管理模块

提供多数据库支持和统一的操作接口
"""

from text2sql.database.db_manager import DatabaseManager, DatabaseConfig
from text2sql.database.pagination import PaginationHandler

__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "PaginationHandler"
]
