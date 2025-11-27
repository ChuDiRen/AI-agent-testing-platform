"""
分页数据模型

专门用于处理分页相关的逻辑
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Generic
import math

T = TypeVar('T')


@dataclass
class PaginationConfig:
    """分页配置"""
    page: int = 1
    page_size: int = 100
    max_page_size: int = 1000
    
    def __post_init__(self):
        # 验证和调整参数
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 100
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    def to_sql_clause(self) -> str:
        """生成SQL分页子句"""
        return f"LIMIT {self.page_size} OFFSET {self.offset}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset
        }


@dataclass
class PaginatedResult(Generic[T]):
    """分页结果"""
    items: List[T]
    page: int
    page_size: int
    total_count: int
    
    @property
    def total_pages(self) -> int:
        return math.ceil(self.total_count / self.page_size) if self.page_size > 0 else 0
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def is_first_page(self) -> bool:
        return self.page == 1
    
    @property
    def is_last_page(self) -> bool:
        return self.page >= self.total_pages
    
    @property
    def item_count(self) -> int:
        return len(self.items)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_count": self.total_count,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
                "item_count": self.item_count
            }
        }


def add_pagination_to_sql(sql: str, pagination: PaginationConfig) -> str:
    """为SQL添加分页子句
    
    Args:
        sql: 原始SQL语句
        pagination: 分页配置
        
    Returns:
        添加分页后的SQL语句
    """
    # 移除末尾的分号
    sql = sql.strip().rstrip(';')
    
    # 检查是否已经有LIMIT子句
    sql_upper = sql.upper()
    if 'LIMIT' in sql_upper:
        # 已有LIMIT，不重复添加
        return sql + ';'
    
    return f"{sql} {pagination.to_sql_clause()};"


def get_count_sql(sql: str) -> str:
    """生成计数SQL
    
    Args:
        sql: 原始SELECT语句
        
    Returns:
        COUNT(*)查询语句
    """
    sql = sql.strip().rstrip(';')
    
    # 移除ORDER BY子句（COUNT不需要排序）
    sql_upper = sql.upper()
    order_pos = sql_upper.rfind('ORDER BY')
    if order_pos > 0:
        # 检查ORDER BY是否在子查询中
        # 简单处理：只移除最外层的ORDER BY
        bracket_count = sql_upper[order_pos:].count('(') - sql_upper[order_pos:].count(')')
        if bracket_count == 0:
            sql = sql[:order_pos].strip()
    
    # 移除LIMIT子句
    limit_pos = sql_upper.rfind('LIMIT')
    if limit_pos > 0:
        bracket_count = sql_upper[limit_pos:].count('(') - sql_upper[limit_pos:].count(')')
        if bracket_count == 0:
            sql = sql[:limit_pos].strip()
    
    return f"SELECT COUNT(*) as total_count FROM ({sql}) as count_subquery;"
