"""
结果数据模型

定义查询结果和分页相关的数据模型
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import math


class QueryStatus(str, Enum):
    """查询状态"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class PaginationInfo:
    """分页信息"""
    page: int = 1
    page_size: int = 100
    total_count: Optional[int] = None
    
    @property
    def total_pages(self) -> Optional[int]:
        if self.total_count is None:
            return None
        return math.ceil(self.total_count / self.page_size)
    
    @property
    def has_next(self) -> bool:
        if self.total_pages is None:
            return False
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_count": self.total_count,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev
        }


@dataclass
class QueryResult:
    """查询结果"""
    status: QueryStatus = QueryStatus.SUCCESS
    data: List[Dict[str, Any]] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    sql: str = ""
    error: Optional[str] = None
    error_code: Optional[str] = None
    pagination: Optional[PaginationInfo] = None
    
    @property
    def success(self) -> bool:
        return self.status == QueryStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "status": self.status.value,
            "success": self.success,
            "data": self.data,
            "columns": self.columns,
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "sql": self.sql
        }
        
        if self.error:
            result["error"] = self.error
            result["error_code"] = self.error_code
            
        if self.pagination:
            result["pagination"] = self.pagination.to_dict()
            
        return result


@dataclass
class ChartData:
    """图表数据"""
    chart_type: str
    title: str
    x_axis: str
    y_axis: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chart_type": self.chart_type,
            "title": self.title,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "data": self.data,
            "options": self.options
        }


@dataclass
class QueryAnalysis:
    """查询分析结果"""
    intent: str = ""
    query_type: str = "select"  # select, aggregate, join, subquery
    relevant_tables: List[str] = field(default_factory=list)
    relevant_columns: Dict[str, List[str]] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)
    aggregations: List[str] = field(default_factory=list)
    ordering: List[str] = field(default_factory=list)
    grouping: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "query_type": self.query_type,
            "relevant_tables": self.relevant_tables,
            "relevant_columns": self.relevant_columns,
            "filters": self.filters,
            "aggregations": self.aggregations,
            "ordering": self.ordering,
            "grouping": self.grouping,
            "limit": self.limit
        }
