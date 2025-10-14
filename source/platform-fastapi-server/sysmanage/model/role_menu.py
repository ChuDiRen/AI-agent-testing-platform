from sqlmodel import SQLModel, Field
from typing import Optional

class RoleMenu(SQLModel, table=True): # 角色-菜单关联表
    __tablename__ = "t_role_menu"
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(index=True) # 角色ID
    menu_id: int = Field(index=True) # 菜单ID

