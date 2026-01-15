from typing import Optional, List

from pydantic import BaseModel, Field


class MenuQuery(BaseModel): # 菜单查询请求（参考RuoYi-Vue-Plus）
    menu_name: Optional[str] = None # 菜单名称（模糊查询）
    visible: Optional[str] = None # 菜单状态（0显示 1隐藏）
    status: Optional[str] = None # 菜单状态（0正常 1停用）

class MenuCreate(BaseModel): # 菜单创建请求（参考RuoYi-Vue-Plus）
    parent_id: int = 0
    menu_name: str = Field(..., description="菜单名称", max_length=50)
    path: Optional[str] = Field(None, description="路由地址", max_length=200)
    component: Optional[str] = Field(None, description="组件路径", max_length=255)
    query: Optional[str] = Field(None, description="路由参数", max_length=255)
    perms: Optional[str] = Field(None, description="权限标识", max_length=100)
    icon: Optional[str] = Field(None, description="菜单图标", max_length=100)
    menu_type: str = Field('C', description="菜单类型（M目录 C菜单 F按钮）")
    visible: str = Field('0', description="显示状态（0显示 1隐藏）")
    status: str = Field('0', description="菜单状态（0正常 1停用）")
    is_cache: str = Field('0', description="是否缓存（0缓存 1不缓存）")
    is_frame: str = Field('1', description="是否外链（0是 1否）")
    order_num: int = Field(0, description="显示顺序")
    remark: Optional[str] = Field(None, description="备注", max_length=500)

class MenuUpdate(BaseModel): # 菜单更新请求（参考RuoYi-Vue-Plus）
    id: int
    parent_id: Optional[int] = None
    menu_name: Optional[str] = Field(None, max_length=50)
    path: Optional[str] = Field(None, max_length=200)
    component: Optional[str] = Field(None, max_length=255)
    query: Optional[str] = Field(None, max_length=255)
    perms: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=100)
    menu_type: Optional[str] = None
    visible: Optional[str] = None
    status: Optional[str] = None
    is_cache: Optional[str] = None
    is_frame: Optional[str] = None
    order_num: Optional[int] = None
    remark: Optional[str] = Field(None, max_length=500)

class MenuTree(BaseModel): # 菜单树节点（参考RuoYi-Vue-Plus）
    id: int
    parent_id: int
    menu_name: str
    path: Optional[str] = None
    component: Optional[str] = None
    query: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    menu_type: str
    visible: str
    status: str
    is_cache: str
    is_frame: str
    order_num: int
    remark: Optional[str] = None
    children: Optional[List['MenuTree']] = None
    
    class Config:
        from_attributes = True

MenuTree.model_rebuild() # 重建模型以支持自引用

