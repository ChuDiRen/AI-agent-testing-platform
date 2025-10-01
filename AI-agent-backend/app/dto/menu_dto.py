"""
菜单DTO
定义菜单相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator


class MenuIdRequest(BaseModel):
    """
    菜单ID请求DTO
    """
    menu_id: int = Field(..., description="菜单ID")

    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": 1
            }
        }


class MenuSearchRequest(BaseModel):
    """
    菜单搜索请求DTO
    """
    keyword: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否启用")

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "系统管理",
                "is_active": True
            }
        }


class MenuCreateRequest(BaseModel):
    """创建菜单请求"""
    name: str = Field(..., description="菜单名称")
    parent_id: int = Field(default=0, description="父菜单ID")
    path: Optional[str] = Field(None, description="菜单路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="菜单图标")
    order_num: int = Field(default=0, description="排序号")
    redirect: Optional[str] = Field(None, description="重定向路径")
    is_visible: bool = Field(default=True, description="是否可见")
    keep_alive: bool = Field(default=False, description="是否缓存")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "用户管理",
                "parent_id": 1,
                "path": "/system/user",
                "component": "/system/user/index",
                "icon": "mdi:account",
                "order_num": 1,
                "redirect": None,
                "is_visible": True,
                "keep_alive": False
            }
        }


class MenuUpdateRequest(BaseModel):
    """更新菜单请求"""
    id: int = Field(..., description="菜单ID")
    name: str = Field(..., description="菜单名称")
    parent_id: int = Field(default=0, description="父菜单ID")
    path: Optional[str] = Field(None, description="菜单路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, description="菜单图标")
    order_num: int = Field(default=0, description="排序号")
    redirect: Optional[str] = Field(None, description="重定向路径")
    is_visible: bool = Field(default=True, description="是否可见")
    keep_alive: bool = Field(default=False, description="是否缓存")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "用户管理",
                "parent_id": 1,
                "path": "/system/user",
                "component": "/system/user/index",
                "icon": "mdi:account",
                "order_num": 1,
                "redirect": None,
                "is_visible": True,
                "keep_alive": False
            }
        }


class MenuDeleteRequest(BaseModel):
    """
    删除菜单请求DTO
    """
    menu_id: int = Field(..., description="菜单ID")

    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": 1
            }
        }


class UserMenuRequest(BaseModel):
    """
    用户菜单请求DTO
    """
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1
            }
        }


class MenuCreateRequest(BaseModel):
    """
    创建菜单请求DTO
    """
    parent_id: int = Field(..., description="上级菜单ID，0表示顶级菜单")
    menu_name: str = Field(..., min_length=1, max_length=50, description="菜单/按钮名称")
    menu_type: str = Field(..., pattern="^[01]$", description="类型：0菜单 1按钮")
    path: Optional[str] = Field(None, max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="路由组件")
    perms: Optional[str] = Field(None, max_length=50, description="权限标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    order_num: Optional[float] = Field(None, description="排序号")
    is_active: bool = Field(default=True, description="是否启用")

    @validator('menu_type')
    def validate_menu_type(cls, v):
        if v not in ['0', '1']:
            raise ValueError('菜单类型必须是 0(菜单) 或 1(按钮)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "parent_id": 0,
                "menu_name": "系统管理",
                "menu_type": "0",
                "path": "/system",
                "component": "Layout",
                "perms": None,
                "icon": "el-icon-set-up",
                "order_num": 1
            }
        }


class MenuUpdateRequest(BaseModel):
    """
    更新菜单请求DTO
    """
    menu_id: int = Field(..., description="菜单ID")
    menu_name: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单/按钮名称")
    path: Optional[str] = Field(None, max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="路由组件")
    perms: Optional[str] = Field(None, max_length=50, description="权限标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    order_num: Optional[float] = Field(None, description="排序号")
    is_active: Optional[bool] = Field(None, description="是否启用")

    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": 1,
                "menu_name": "系统管理",
                "path": "/system",
                "component": "Layout",
                "perms": None,
                "icon": "el-icon-set-up",
                "order_num": 1
            }
        }


class MenuResponse(BaseModel):
    """
    菜单响应DTO
    """
    menu_id: int = Field(..., description="菜单ID")
    parent_id: int = Field(..., description="上级菜单ID")
    menu_name: str = Field(..., description="菜单/按钮名称")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="路由组件")
    perms: Optional[str] = Field(None, description="权限标识")
    icon: Optional[str] = Field(None, description="图标")
    menu_type: str = Field(..., description="类型：0菜单 1按钮")
    order_num: Optional[float] = Field(None, description="排序号")
    is_active: bool = Field(default=True, description="是否启用")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    modify_time: Optional[datetime] = Field(None, description="修改时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "menu_id": 1,
                "parent_id": 0,
                "menu_name": "系统管理",
                "path": "/system",
                "component": "Layout",
                "perms": None,
                "icon": "el-icon-set-up",
                "menu_type": "0",
                "order_num": 1,
                "create_time": "2025-01-01T00:00:00",
                "modify_time": "2025-01-01T00:00:00"
            }
        }


class MenuTreeNode(BaseModel):
    """
    菜单树节点DTO
    """
    menu_id: int = Field(..., description="菜单ID")
    parent_id: int = Field(..., description="上级菜单ID")
    menu_name: str = Field(..., description="菜单/按钮名称")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="路由组件")
    perms: Optional[str] = Field(None, description="权限标识")
    icon: Optional[str] = Field(None, description="图标")
    menu_type: str = Field(..., description="类型：0菜单 1按钮")
    order_num: Optional[float] = Field(None, description="排序号")
    is_active: bool = Field(default=True, description="是否启用")
    children: List['MenuTreeNode'] = Field(default=[], description="子菜单列表")

    class Config:
        from_attributes = True


class MenuTreeResponse(BaseModel):
    """
    菜单树响应DTO
    """
    tree: List[MenuTreeNode] = Field(..., description="菜单树")

    class Config:
        json_schema_extra = {
            "example": {
                "tree": [
                    {
                        "menu_id": 1,
                        "parent_id": 0,
                        "menu_name": "系统管理",
                        "path": "/system",
                        "component": "Layout",
                        "perms": None,
                        "icon": "el-icon-set-up",
                        "menu_type": "0",
                        "order_num": 1,
                        "children": [
                            {
                                "menu_id": 2,
                                "parent_id": 1,
                                "menu_name": "用户管理",
                                "path": "/system/user",
                                "component": "system/user/Index",
                                "perms": "user:view",
                                "icon": "",
                                "menu_type": "0",
                                "order_num": 1,
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }


class UserMenuResponse(BaseModel):
    """
    用户菜单响应DTO
    """
    menus: List[MenuTreeNode] = Field(..., description="用户可访问的菜单列表")
    permissions: List[str] = Field(..., description="用户权限标识列表")

    class Config:
        json_schema_extra = {
            "example": {
                "menus": [
                    {
                        "menu_id": 1,
                        "parent_id": 0,
                        "menu_name": "系统管理",
                        "path": "/system",
                        "component": "Layout",
                        "perms": None,
                        "icon": "el-icon-set-up",
                        "menu_type": "0",
                        "order_num": 1,
                        "children": []
                    }
                ],
                "permissions": ["user:view", "user:add", "user:update", "user:delete"]
            }
        }


class UserMenuTreeNode(BaseModel):
    """
    用户菜单树节点DTO - 用于动态路由
    """
    id: int = Field(..., description="菜单ID")
    name: str = Field(..., description="路由名称")
    path: str = Field(..., description="路由路径")
    component: Optional[str] = Field(None, description="路由组件路径")
    redirect: Optional[str] = Field(None, description="重定向路径")
    meta: 'MenuMeta' = Field(..., description="路由元信息")
    children: List['UserMenuTreeNode'] = Field(default_factory=list, description="子路由列表")

    class Config:
        from_attributes = True


class MenuMeta(BaseModel):
    """
    菜单元信息DTO
    """
    title: str = Field(..., description="菜单标题")
    icon: Optional[str] = Field(None, description="菜单图标")
    order: Optional[float] = Field(None, description="排序号")
    hidden: bool = Field(default=False, description="是否隐藏")
    keepAlive: bool = Field(default=False, description="是否缓存")
    permission: Optional[str] = Field(None, description="权限标识")

    class Config:
        from_attributes = True


class UserMenuTreeResponse(BaseModel):
    """
    用户菜单树响应DTO - 用于动态路由
    """
    routes: List[UserMenuTreeNode] = Field(..., description="用户可访问的路由树")
    permissions: List[str] = Field(..., description="用户权限标识列表")

    class Config:
        json_schema_extra = {
            "example": {
                "routes": [
                    {
                        "id": 1,
                        "name": "System",
                        "path": "/system",
                        "component": "Layout",
                        "redirect": "/system/user",
                        "meta": {
                            "title": "系统管理",
                            "icon": "Setting",
                            "order": 1,
                            "hidden": False,
                            "keepAlive": False,
                            "permission": None
                        },
                        "children": [
                            {
                                "id": 2,
                                "name": "User",
                                "path": "/system/user",
                                "component": "system/user/Index",
                                "meta": {
                                    "title": "用户管理",
                                    "icon": "User",
                                    "order": 1,
                                    "hidden": False,
                                    "keepAlive": True,
                                    "permission": "user:view"
                                },
                                "children": []
                            }
                        ]
                    }
                ],
                "permissions": ["user:view", "user:add", "user:update", "user:delete"]
            }
        }


# 更新前向引用
MenuTreeNode.model_rebuild()
UserMenuTreeNode.model_rebuild()
MenuMeta.model_rebuild()
