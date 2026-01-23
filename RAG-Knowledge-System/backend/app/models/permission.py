"""
权限模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Permission(SQLModel, table=True):
    """权限表"""

    __tablename__ = "sys_permission"

    id: Optional[int] = Field(default=None, primary_key=True, description="权限ID")
    name: str = Field(max_length=100, description="权限名称")
    code: str = Field(max_length=100, unique=True, description="权限编码")
    type: str = Field(max_length=20, description="权限类型：menu/api")
    resource: str = Field(max_length=200, description="资源（菜单路径/API路径）")
    action: Optional[str] = Field(default=None, max_length=50, description="操作（GET/POST/PUT/DELETE）")
    description: Optional[str] = Field(default=None, max_length=200, description="权限描述")
    status: int = Field(default=1, description="状态：1启用 0禁用")
    sort: int = Field(default=0, description="排序")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
