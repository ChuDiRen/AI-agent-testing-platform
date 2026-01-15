from typing import Optional, List

from pydantic import BaseModel


class RoleQuery(BaseModel): # 角色查询请求
    page: int = 1
    pageSize: int = 10
    role_name: Optional[str] = None # 角色名称（模糊查询）

class RoleCreate(BaseModel): # 角色创建请求
    role_name: str
    remark: Optional[str] = None

class RoleUpdate(BaseModel): # 角色更新请求
    id: int
    role_name: Optional[str] = None
    remark: Optional[str] = None

class RoleMenuAssign(BaseModel): # 角色分配菜单权限
    id: int
    menu_ids: List[int] # 菜单ID列表

class RoleCopy(BaseModel): # 角色复制请求
    source_role_id: int  # 源角色ID
    role_name: str  # 新角色名称
    role_key: str  # 新角色标识
    remark: Optional[str] = None  # 新角色描述

class BatchRoleDelete(BaseModel): # 批量删除角色
    role_ids: List[int]

