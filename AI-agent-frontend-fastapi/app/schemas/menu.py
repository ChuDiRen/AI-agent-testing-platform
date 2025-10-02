"""菜单数据验证模型 - 对应 t_menu 表"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    """菜单基础模型"""
    parent_id: int = Field(..., description="上级菜单ID")
    menu_name: str = Field(..., max_length=50, description="菜单/按钮名称")
    path: Optional[str] = Field(None, max_length=255, description="对应路由path")
    component: Optional[str] = Field(None, max_length=255, description="对应路由组件component")
    perms: Optional[str] = Field(None, max_length=50, description="权限标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    type: str = Field(..., max_length=2, description="类型 0菜单 1按钮")
    order_num: Optional[float] = Field(None, description="排序")


class MenuCreate(MenuBase):
    """创建菜单"""
    pass


class MenuUpdate(BaseModel):
    """更新菜单"""
    parent_id: Optional[int] = None
    menu_name: Optional[str] = Field(None, max_length=50)
    path: Optional[str] = Field(None, max_length=255)
    component: Optional[str] = Field(None, max_length=255)
    perms: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = Field(None, max_length=2)
    order_num: Optional[float] = None


class MenuResponse(MenuBase):
    """菜单响应模型"""
    menu_id: int
    create_time: datetime
    modify_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class MenuTree(MenuResponse):
    """菜单树结构"""
    children: list['MenuTree'] = []

    class Config:
        from_attributes = True

