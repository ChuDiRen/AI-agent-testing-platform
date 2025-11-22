from typing import Optional

from pydantic import BaseModel


class ApiDbBaseQuery(BaseModel): # API数据库配置查询请求
    page: int = 1
    pageSize: int = 10
    project_id: Optional[int] = 0
    connect_name: Optional[str] = ""

class ApiDbBaseCreate(BaseModel): # API数据库配置创建请求
    project_id: int
    name: str
    ref_name: str
    db_type: str
    db_info: str
    is_enabled: str

class ApiDbBaseUpdate(BaseModel): # API数据库配置更新请求
    id: int
    project_id: Optional[int] = None
    name: Optional[str] = None
    ref_name: Optional[str] = None
    db_type: Optional[str] = None
    db_info: Optional[str] = None
    is_enabled: Optional[str] = None

