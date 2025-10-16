from sqlmodel import SQLModel, Field
from typing import Optional

class UserRole(SQLModel, table=True): # 用户-角色关联表
    __tablename__ = "t_user_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True) # 用户ID
    role_id: int = Field(index=True) # 角色ID

