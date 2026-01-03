from typing import Optional

from pydantic import BaseModel, Field


class ApiKeyWordQuery(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    name: Optional[str] = Field(default=None, description="关键字名称")
    operation_type_id: Optional[int] = Field(default=None, description="操作类型ID")
    page_id: Optional[int] = Field(default=None, description="页面ID")

class ApiKeyWordCreate(BaseModel):
    name: str
    keyword_desc: str
    operation_type_id: int
    keyword_fun_name: str
    keyword_value: str
    is_enabled: str
    category: Optional[str] = None

class ApiKeyWordUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    keyword_desc: Optional[str] = None
    operation_type_id: Optional[int] = None
    keyword_fun_name: Optional[str] = None
    keyword_value: Optional[str] = None
    is_enabled: Optional[str] = None
    category: Optional[str] = None

class KeywordFileRequest(BaseModel): # 关键字文件生成请求
    keyword_fun_name: str
    keyword_value: str

