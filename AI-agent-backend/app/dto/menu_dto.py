# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单DTO
定义菜单相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator


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
    menu_name: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单/按钮名称")
    path: Optional[str] = Field(None, max_length=255, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="路由组件")
    perms: Optional[str] = Field(None, max_length=50, description="权限标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    order_num: Optional[float] = Field(None, description="排序号")

    class Config:
        json_schema_extra = {
            "example": {
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


# 更新前向引用
MenuTreeNode.model_rebuild()
