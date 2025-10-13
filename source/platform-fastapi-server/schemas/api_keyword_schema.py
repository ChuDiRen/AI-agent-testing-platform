from pydantic import BaseModel, Field
from typing import Optional

class ApiKeyWordQuery(BaseModel): # API关键字查询请求
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    name: Optional[str] = Field(default=None, description="关键字名称")
    operation_type_id: Optional[int] = Field(default=None, description="操作类型ID")
    page_id: Optional[int] = Field(default=None, description="页面ID")

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

