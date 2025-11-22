from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True): # 角色模型
    __tablename__ = "t_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(max_length=100, unique=True, index=True) # 角色名称
    remark: Optional[str] = Field(default=None, max_length=500) # 角色描述
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间

