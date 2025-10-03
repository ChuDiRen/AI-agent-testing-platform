"""部门相关的 Pydantic 模式"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    """部门基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="部门名称")
    parent_id: int = Field(0, description="上级部门ID，0表示顶级部门")
    order_num: Optional[int] = Field(None, description="排序")


class DepartmentCreate(DepartmentBase):
    """部门创建模型"""
    pass


class DepartmentUpdate(BaseModel):
    """部门更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="部门名称")
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    order_num: Optional[int] = Field(None, description="排序")


class DepartmentResponse(DepartmentBase):
    """部门响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

