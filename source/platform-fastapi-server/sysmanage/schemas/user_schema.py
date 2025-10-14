from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserQuery(BaseModel): # 用户查询请求
    page: int = 1
    pageSize: int = 10

class UserCreate(BaseModel): # 用户创建请求
    username: str
    password: str

class UserUpdate(BaseModel): # 用户更新请求
    id: int
    username: Optional[str] = None
    password: Optional[str] = None

