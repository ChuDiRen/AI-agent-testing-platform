from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 查询Schema
class ApiGroupQuery(BaseModel):
    project_id: Optional[int] = None
    group_name: Optional[str] = None

# 创建Schema
class ApiGroupCreate(BaseModel):
    project_id: int
    group_name: str
    group_desc: Optional[str] = None
    parent_id: int = 0
    order_num: int = 0

# 更新Schema
class ApiGroupUpdate(BaseModel):
    id: int
    group_name: Optional[str] = None
    group_desc: Optional[str] = None
    parent_id: Optional[int] = None
    order_num: Optional[int] = None

# 树形结构Schema
class ApiGroupTree(BaseModel):
    id: int
    project_id: int
    group_name: str
    group_desc: Optional[str] = None
    parent_id: int
    order_num: int
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    children: Optional[List['ApiGroupTree']] = []

# 响应Schema
class ApiGroupResponse(BaseModel):
    id: int
    project_id: int
    group_name: str
    group_desc: Optional[str] = None
    parent_id: int
    order_num: int
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
