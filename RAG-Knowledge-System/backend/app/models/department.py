"""
部门模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Department(SQLModel, table=True):
    """部门表"""

    __tablename__ = "sys_department"

    id: Optional[int] = Field(default=None, primary_key=True, description="部门ID")
    name: str = Field(max_length=100, description="部门名称")
    code: str = Field(max_length=50, unique=True, description="部门编码")
    parent_id: Optional[int] = Field(default=None, foreign_key="sys_department.id", description="父部门ID")
    sort: int = Field(default=0, description="排序")
    status: int = Field(default=1, description="状态：1启用 0禁用")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
