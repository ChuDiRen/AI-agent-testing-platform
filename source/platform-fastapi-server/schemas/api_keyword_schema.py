from pydantic import BaseModel
from typing import Optional

class ApiKeyWordQuery(BaseModel): # API关键字查询请求
    page: int = 1
    pageSize: int = 10
    name: Optional[str] = ""
    operation_type_id: Optional[int] = 0
    page_id: Optional[int] = 0

class ApiKeyWordCreate(BaseModel): # API关键字创建请求
    name: str
    keyword_desc: str
    operation_type_id: int
    keyword_fun_name: str
    keyword_value: str
    is_enabled: str

class ApiKeyWordUpdate(BaseModel): # API关键字更新请求
    id: int
    name: Optional[str] = None
    keyword_desc: Optional[str] = None
    operation_type_id: Optional[int] = None
    keyword_fun_name: Optional[str] = None
    keyword_value: Optional[str] = None
    is_enabled: Optional[str] = None

class KeywordFileRequest(BaseModel): # 关键字文件生成请求
    keyword_fun_name: str
    keyword_value: str

