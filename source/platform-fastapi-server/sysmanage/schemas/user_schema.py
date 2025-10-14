from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserQuery(BaseModel): # 用户查询请求
    page: int = 1
    pageSize: int = 10
    username: Optional[str] = None # 用户名（模糊查询）
    dept_id: Optional[int] = None # 部门ID
    status: Optional[str] = None # 状态

class UserCreate(BaseModel): # 用户创建请求
    username: str
    password: str
    dept_id: Optional[int] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    status: str = "1"
    ssex: Optional[str] = "2"
    avatar: Optional[str] = None
    description: Optional[str] = None

class UserUpdate(BaseModel): # 用户更新请求
    id: int
    username: Optional[str] = None
    password: Optional[str] = None
    dept_id: Optional[int] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    status: Optional[str] = None
    ssex: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None

class UserRoleAssign(BaseModel): # 用户分配角色
    user_id: int
    role_ids: List[int] # 角色ID列表

class UserStatusUpdate(BaseModel): # 用户状态更新
    id: int
    status: str # 0锁定 1有效

