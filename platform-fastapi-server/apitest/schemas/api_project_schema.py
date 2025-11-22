from typing import Optional

from pydantic import BaseModel


class ApiProjectQuery(BaseModel): # API项目查询请求
    page: int = 1
    pageSize: int = 10

class ApiProjectCreate(BaseModel): # API项目创建请求
    project_name: str
    project_desc: str

class ApiProjectUpdate(BaseModel): # API项目更新请求
    id: int
    project_name: Optional[str] = None
    project_desc: Optional[str] = None

