from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Menu(SQLModel, table=True): # 菜单/权限模型（参考RuoYi-Vue-Plus设计）
    __tablename__ = "t_menu"
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(default=0, index=True) # 上级菜单ID，0表示顶级菜单
    menu_name: str = Field(max_length=50) # 菜单/按钮名称
    path: Optional[str] = Field(default=None, max_length=255) # 对应路由path
    component: Optional[str] = Field(default=None, max_length=255) # 对应路由组件component
    query: Optional[str] = Field(default=None, max_length=255) # 路由参数
    perms: Optional[str] = Field(default=None, max_length=500) # 权限标识（如 system:user:add）
    icon: Optional[str] = Field(default=None, max_length=50) # 图标
    menu_type: str = Field(max_length=1, default='C') # 菜单类型（M目录 C菜单 F按钮）
    visible: str = Field(max_length=1, default='0') # 菜单状态（0显示 1隐藏）
    status: str = Field(max_length=1, default='0') # 菜单状态（0正常 1停用）
    is_cache: str = Field(max_length=1, default='0') # 是否缓存（0缓存 1不缓存）
    is_frame: str = Field(max_length=1, default='1') # 是否外链（0是 1否）
    order_num: int = Field(default=0) # 显示排序
    remark: Optional[str] = Field(default=None, max_length=500) # 备注
    create_time: Optional[datetime] = Field(default_factory=datetime.now) # 创建时间
    modify_time: Optional[datetime] = Field(default_factory=datetime.now) # 修改时间

