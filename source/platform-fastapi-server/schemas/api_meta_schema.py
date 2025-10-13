from pydantic import BaseModel
from typing import Optional

class ApiMetaQuery(BaseModel): # API元数据查询请求
    page: int = 1
    pageSize: int = 10
    mate_name: Optional[str] = ""
    object_url: Optional[str] = ""
    file_type: Optional[str] = ""
    project_id: Optional[int] = 0

class ApiMetaUpdate(BaseModel): # API元数据更新请求
    id: int
    mate_name: Optional[str] = None
    object_url: Optional[str] = None
    file_type: Optional[str] = None

