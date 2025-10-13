from pydantic import BaseModel, Field
from typing import Optional

class ApiMetaQuery(BaseModel): # API元数据查询请求
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    mate_name: Optional[str] = Field(default=None, description="元数据名称")
    object_url: Optional[str] = Field(default=None, description="对象URL")
    file_type: Optional[str] = Field(default=None, description="文件类型")
    project_id: Optional[int] = Field(default=None, description="项目ID")

class ApiMetaUpdate(BaseModel): # API元数据更新请求
    id: int
    mate_name: Optional[str] = None
    object_url: Optional[str] = None
    file_type: Optional[str] = None

