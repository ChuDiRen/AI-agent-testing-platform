"""
环境管理Schema
"""
from pydantic import BaseModel
from typing import Optional, List


class ApiEnvironmentQuery(BaseModel):
    """环境查询参数"""
    page: int = 1
    pageSize: int = 10
    project_id: Optional[int] = None
    env_name: Optional[str] = None
    env_code: Optional[str] = None
    is_enabled: Optional[int] = None


class ApiEnvironmentCreate(BaseModel):
    """创建环境"""
    project_id: int
    env_name: str
    env_code: str
    base_url: Optional[str] = None
    env_variables: Optional[str] = None
    env_headers: Optional[str] = None
    is_default: int = 0
    is_enabled: int = 1
    sort_order: int = 0


class ApiEnvironmentUpdate(BaseModel):
    """更新环境"""
    id: int
    project_id: Optional[int] = None
    env_name: Optional[str] = None
    env_code: Optional[str] = None
    base_url: Optional[str] = None
    env_variables: Optional[str] = None
    env_headers: Optional[str] = None
    is_default: Optional[int] = None
    is_enabled: Optional[int] = None
    sort_order: Optional[int] = None


class EnvironmentVariable(BaseModel):
    """环境变量项"""
    key: str
    value: str
    description: Optional[str] = None
    is_enabled: int = 1


class EnvironmentHeader(BaseModel):
    """全局请求头项"""
    key: str
    value: str
    description: Optional[str] = None
    is_enabled: int = 1


class ApiEnvironmentCopy(BaseModel):
    """复制环境"""
    source_id: int
    new_env_name: str
    new_env_code: str
