"""
用户模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """用户表"""

    __tablename__ = "sys_user"

    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID")
    username: str = Field(max_length=50, unique=True, index=True, description="用户名")
    password_hash: str = Field(max_length=255, description="密码哈希")
    email: str = Field(max_length=100, unique=True, index=True, description="邮箱")
    full_name: Optional[str] = Field(default=None, max_length=100, description="全名")
    is_superuser: bool = Field(default=False, description="是否超级管理员")
    is_active: bool = Field(default=True, description="是否激活")
    status: int = Field(default=1, description="状态：1启用 0禁用")
    role_id: Optional[int] = Field(default=None, foreign_key="sys_role.id", description="角色ID")
    dept_id: Optional[int] = Field(default=None, foreign_key="sys_department.id", description="部门ID")
    phone: Optional[str] = Field(default=None, max_length=20, description="电话号码")
    avatar: Optional[str] = Field(default=None, max_length=255, description="头像URL")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
