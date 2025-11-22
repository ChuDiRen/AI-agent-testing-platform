from pydantic import BaseModel
from typing import Optional

class OperationTypeQuery(BaseModel): # 操作类型查询请求
    page: int = 1
    pageSize: int = 10
    operation_type_name: Optional[str] = ""

class OperationTypeCreate(BaseModel): # 操作类型创建请求
    operation_type_name: str
    ex_fun_name: str

class OperationTypeUpdate(BaseModel): # 操作类型更新请求
    id: int
    operation_type_name: Optional[str] = None
    ex_fun_name: Optional[str] = None

