from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MenuQuery(BaseModel): # 菜单查询请求
    menu_name: Optional[str] = None # 菜单名称（模糊查询）
    type: Optional[str] = None # 类型（0菜单 1按钮）

class MenuCreate(BaseModel): # 菜单创建请求
    parent_id: int = 0
    menu_name: str
    path: Optional[str] = None
    component: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    type: str # 类型（0菜单 1按钮）
    order_num: int = 0

class MenuUpdate(BaseModel): # 菜单更新请求
    id: int
    parent_id: Optional[int] = None
    menu_name: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[str] = None
    order_num: Optional[int] = None

class MenuTree(BaseModel): # 菜单树节点
    id: int
    parent_id: int
    menu_name: str
    path: Optional[str] = None
    component: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    type: str
    order_num: int
    children: Optional[List['MenuTree']] = None
    
    class Config:
        from_attributes = True

MenuTree.model_rebuild() # 重建模型以支持自引用

