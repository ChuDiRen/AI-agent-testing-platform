"""
菜单 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class MenuBase(BaseModel):
    """菜单基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="菜单名称")
    menu_type: str = Field("menu", description="菜单类型（menu=菜单，directory=目录）")
    icon: Optional[str] = Field(None, max_length=50, description="菜单图标")
    path: str = Field(..., max_length=200, description="路由路径")
    component: Optional[str] = Field(None, max_length=200, description="组件路径")
    order: int = Field(0, description="排序号")
    parent_id: int = Field(0, description="父菜单ID")
    is_hidden: bool = Field(False, description="是否隐藏")
    keepalive: bool = Field(True, description="是否缓存")
    redirect: Optional[str] = Field(None, max_length=200, description="重定向路径")


class MenuCreate(MenuBase):
    """创建菜单"""
    pass


class MenuUpdate(MenuBase):
    """更新菜单"""
    pass


class MenuResponse(MenuBase):
    """菜单响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    children: List[Any] = Field(default_factory=list, description="子菜单")
    
    class Config:
        from_attributes = True
