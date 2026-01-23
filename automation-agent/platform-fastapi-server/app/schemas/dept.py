"""
部门 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class DeptBase(BaseModel):
    """部门基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="部门名称")
    desc: Optional[str] = Field(None, max_length=200, description="部门描述")
    parent_id: int = Field(0, description="父部门ID")
    order: int = Field(0, description="排序号")


class DeptCreate(DeptBase):
    """创建部门"""
    pass


class DeptUpdate(DeptBase):
    """更新部门"""
    pass


class DeptResponse(DeptBase):
    """部门响应模型"""
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    children: List[Any] = Field(default_factory=list, description="子部门")
    
    class Config:
        from_attributes = True
