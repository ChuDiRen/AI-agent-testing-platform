from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True): # 用户模型
    __tablename__ = "t_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=255, index=True, unique=True)
    password: str = Field(max_length=255)
    dept_id: Optional[int] = Field(default=None, index=True) # 部门ID
    email: Optional[str] = Field(default=None, max_length=128) # 邮箱
    mobile: Optional[str] = Field(default=None, max_length=20) # 联系电话
    status: str = Field(default="1", max_length=1) # 状态 0锁定 1有效
    ssex: Optional[str] = Field(default="2", max_length=1) # 性别 0男 1女 2保密
    avatar: Optional[str] = Field(default=None, max_length=500) # 头像URL
    description: Optional[str] = Field(default=None, max_length=500) # 描述
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间
    last_login_time: Optional[datetime] = None # 最近访问时间
