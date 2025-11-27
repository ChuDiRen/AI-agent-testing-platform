"""
API请求/响应模型

定义FastAPI的Pydantic模型
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="自然语言查询")
    connection_id: int = Field(default=0, description="数据库连接ID")
    thread_id: Optional[str] = Field(default=None, description="会话线程ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    stream: bool = Field(default=False, description="是否流式输出")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "查询所有用户",
                "connection_id": 0,
                "stream": False
            }
        }


class PaginationRequest(BaseModel):
    """分页请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=100, ge=1, le=1000, description="每页大小")


class QueryWithPaginationRequest(QueryRequest):
    """带分页的查询请求"""
    pagination: Optional[PaginationRequest] = None


class PaginationInfo(BaseModel):
    """分页信息"""
    page: int
    page_size: int
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    has_next: bool = False
    has_prev: bool = False


class QueryResult(BaseModel):
    """查询结果"""
    success: bool
    data: List[Dict[str, Any]] = []
    columns: List[str] = []
    row_count: int = 0
    sql: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    pagination: Optional[PaginationInfo] = None


class ChartConfig(BaseModel):
    """图表配置"""
    chart_type: str
    title: str
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class ChartRequest(BaseModel):
    """图表生成请求"""
    data: List[Dict[str, Any]]
    columns: List[str]
    chart_type: Optional[str] = None
    title: Optional[str] = "Chart"


class ChartResponse(BaseModel):
    """图表响应"""
    success: bool
    chart_config: Optional[ChartConfig] = None
    error: Optional[str] = None


class ConnectionConfig(BaseModel):
    """数据库连接配置"""
    db_type: str = Field(..., description="数据库类型: mysql, postgresql, sqlite等")
    host: str = Field(default="localhost")
    port: int = Field(default=3306)
    database: str = Field(...)
    username: str = Field(default="")
    password: str = Field(default="")


class ConnectionResponse(BaseModel):
    """连接响应"""
    connection_id: int
    success: bool
    message: str


class SchemaInfo(BaseModel):
    """Schema信息"""
    tables: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]] = []


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "0.1.0"
    services: Dict[str, bool] = {}


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class StreamEvent(BaseModel):
    """流事件"""
    event: str
    data: Dict[str, Any]
    agent: Optional[str] = None
    timestamp: Optional[float] = None
