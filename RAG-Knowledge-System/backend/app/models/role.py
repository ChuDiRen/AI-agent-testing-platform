"""
角色模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Role(SQLModel, table=True):
    """角色表"""

    __tablename__ = "sys_role"

    id: Optional[int] = Field(default=None, primary_key=True, description="角色ID")
    name: str = Field(max_length=50, unique=True, description="角色名称")
    code: str = Field(max_length=50, unique=True, description="角色编码")
    description: Optional[str] = Field(default=None, max_length=200, description="角色描述")
    status: int = Field(default=1, description="状态：1启用 0禁用")
    sort: int = Field(default=0, description="排序")
    is_system: bool = Field(default=False, description="是否系统角色")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
