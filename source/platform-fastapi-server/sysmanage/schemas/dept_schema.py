from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DeptQuery(BaseModel): # 部门查询请求
    dept_name: Optional[str] = None # 部门名称（模糊查询）

class DeptCreate(BaseModel): # 部门创建请求
    parent_id: int = 0
    dept_name: str
    order_num: int = 0

class DeptUpdate(BaseModel): # 部门更新请求
    dept_id: int
    parent_id: Optional[int] = None
    dept_name: Optional[str] = None
    order_num: Optional[int] = None

class DeptTree(BaseModel): # 部门树节点
    dept_id: int
    parent_id: int
    dept_name: str
    order_num: int
    children: Optional[List['DeptTree']] = None
    
    class Config:
        from_attributes = True

DeptTree.model_rebuild() # 重建模型以支持自引用

