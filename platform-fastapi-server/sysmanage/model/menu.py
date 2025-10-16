from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Menu(SQLModel, table=True): # 菜单/权限模型
    __tablename__ = "t_menu"
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0, index=True) # 上级菜单ID，0表示顶级菜单
    menu_name: str = Field(max_length=50) # 菜单/按钮名称
    path: Optional[str] = Field(default=None, max_length=255) # 对应路由path
    component: Optional[str] = Field(default=None, max_length=255) # 对应路由组件
    perms: Optional[str] = Field(default=None, max_length=500) # 权限标识（如 user:add, user:view）
    icon: Optional[str] = Field(default=None, max_length=50) # 图标
    type: str = Field(max_length=1) # 类型（0菜单 1按钮）
    order_num: int = Field(default=0) # 排序
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间

