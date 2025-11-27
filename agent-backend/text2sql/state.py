"""
状态管理模块

定义SQL代理系统的状态结构，用于LangGraph图工作流
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from langgraph.graph import MessagesState


@dataclass
class SchemaInfo:
    """数据库Schema信息"""
    tables: List[Dict[str, Any]] = field(default_factory=list)
    columns: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    indexes: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tables": self.tables,
            "columns": self.columns,
            "relationships": self.relationships,
            "indexes": self.indexes
        }


@dataclass
class SQLValidationResult:
    """SQL验证结果"""
    is_valid: bool = False
    sql: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    performance_hints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "sql": self.sql,
            "errors": self.errors,
            "warnings": self.warnings,
            "security_issues": self.security_issues,
            "performance_hints": self.performance_hints
        }


@dataclass
class SQLExecutionResult:
    """SQL执行结果"""
    success: bool = False
    data: List[Dict[str, Any]] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    # 分页信息
    page: int = 1
    page_size: int = 100
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: bool = False
    has_prev: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "columns": self.columns,
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_count": self.total_count,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev
            }
        }


@dataclass
class ChartResult:
    """图表生成结果"""
    success: bool = False
    chart_type: str = ""
    chart_url: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "chart_type": self.chart_type,
            "chart_url": self.chart_url,
            "chart_config": self.chart_config,
            "error": self.error
        }


# 工作流阶段定义
WorkflowStage = Literal[
    "init",
    "schema_analysis",
    "sql_generation", 
    "sql_validation",
    "sql_execution",
    "chart_generation",
    "error_recovery",
    "completed",
    "failed"
]


class SQLMessageState(MessagesState):
    """SQL代理系统的消息状态
    
    继承自LangGraph的MessagesState，添加SQL处理相关的状态字段
    """
    # 数据库连接标识
    connection_id: int = 0
    
    # 查询分析结果
    query_analysis: Optional[Dict[str, Any]] = None
    
    # Schema信息
    schema_info: Optional[Dict[str, Any]] = None
    
    # 生成的SQL
    generated_sql: Optional[str] = None
    
    # 验证结果
    validation_result: Optional[Dict[str, Any]] = None
    
    # 执行结果
    execution_result: Optional[Dict[str, Any]] = None
    
    # 图表结果
    chart_result: Optional[Dict[str, Any]] = None
    
    # 重试计数
    retry_count: int = 0
    max_retries: int = 3
    
    # 当前阶段
    current_stage: WorkflowStage = "init"
    
    # 错误历史
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # 分页配置
    pagination: Optional[Dict[str, Any]] = None
    
    # 用户配置
    user_config: Optional[Dict[str, Any]] = None
