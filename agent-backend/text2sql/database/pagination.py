"""
分页处理模块

提供SQL分页处理和结果分页功能
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re


@dataclass
class PaginationConfig:
    """分页配置"""
    page: int = 1
    page_size: int = 100
    max_page_size: int = 1000
    
    def __post_init__(self):
        """验证和调整参数"""
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 100
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size
    
    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.page_size
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset
        }


class PaginationHandler:
    """分页处理器
    
    处理SQL分页和结果分页
    """
    
    # LIMIT/OFFSET正则表达式
    LIMIT_PATTERN = re.compile(
        r'\bLIMIT\s+\d+(\s+OFFSET\s+\d+)?',
        re.IGNORECASE
    )
    
    def __init__(self, default_page_size: int = 100, max_page_size: int = 1000):
        """初始化分页处理器
        
        Args:
            default_page_size: 默认每页大小
            max_page_size: 最大每页大小
        """
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size
        
    def has_pagination(self, sql: str) -> bool:
        """检查SQL是否已有分页子句
        
        Args:
            sql: SQL语句
            
        Returns:
            是否包含LIMIT子句
        """
        return bool(self.LIMIT_PATTERN.search(sql))
    
    def remove_pagination(self, sql: str) -> str:
        """移除SQL中的分页子句
        
        Args:
            sql: SQL语句
            
        Returns:
            移除分页后的SQL
        """
        return self.LIMIT_PATTERN.sub('', sql).strip().rstrip(';')
    
    def add_pagination(
        self, 
        sql: str, 
        page: int = 1, 
        page_size: Optional[int] = None
    ) -> str:
        """为SQL添加分页子句
        
        Args:
            sql: SQL语句
            page: 页码
            page_size: 每页大小
            
        Returns:
            添加分页后的SQL
        """
        if page_size is None:
            page_size = self.default_page_size
        
        # 限制page_size
        page_size = min(page_size, self.max_page_size)
        
        # 移除已有的分页
        sql = self.remove_pagination(sql)
        
        # 计算offset
        offset = (page - 1) * page_size
        
        return f"{sql} LIMIT {page_size} OFFSET {offset};"
    
    def generate_count_sql(self, sql: str) -> str:
        """生成计数SQL
        
        Args:
            sql: 原始SELECT语句
            
        Returns:
            COUNT(*)查询语句
        """
        # 移除分页
        sql = self.remove_pagination(sql)
        
        # 移除ORDER BY（计数不需要排序）
        order_pattern = re.compile(
            r'\bORDER\s+BY\s+[^;]+',
            re.IGNORECASE
        )
        sql = order_pattern.sub('', sql).strip()
        
        return f"SELECT COUNT(*) as total_count FROM ({sql}) as count_subquery;"
    
    def paginate_results(
        self,
        results: List[Dict[str, Any]],
        page: int = 1,
        page_size: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """对结果进行分页
        
        在内存中对已获取的结果进行分页（适用于小数据集）
        
        Args:
            results: 结果列表
            page: 页码
            page_size: 每页大小
            
        Returns:
            (分页后的结果, 分页元数据)
        """
        if page_size is None:
            page_size = self.default_page_size
            
        page_size = min(page_size, self.max_page_size)
        
        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        # 边界检查
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
            
        # 计算切片范围
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated = results[start:end]
        
        metadata = {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "item_count": len(paginated)
        }
        
        return paginated, metadata
    
    def create_pagination_response(
        self,
        data: List[Dict[str, Any]],
        page: int,
        page_size: int,
        total_count: int
    ) -> Dict[str, Any]:
        """创建分页响应
        
        Args:
            data: 当前页数据
            page: 页码
            page_size: 每页大小
            total_count: 总记录数
            
        Returns:
            标准分页响应
        """
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0
        
        return {
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }


# 默认分页处理器
_handler: Optional[PaginationHandler] = None


def get_pagination_handler() -> PaginationHandler:
    """获取全局分页处理器"""
    global _handler
    if _handler is None:
        _handler = PaginationHandler()
    return _handler


def add_pagination_to_sql(
    sql: str, 
    page: int = 1, 
    page_size: int = 100
) -> str:
    """为SQL添加分页的便捷函数"""
    return get_pagination_handler().add_pagination(sql, page, page_size)


def get_count_sql(sql: str) -> str:
    """生成计数SQL的便捷函数"""
    return get_pagination_handler().generate_count_sql(sql)
