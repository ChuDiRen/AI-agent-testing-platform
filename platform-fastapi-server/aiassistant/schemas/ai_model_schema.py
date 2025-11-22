from typing import Optional

from pydantic import BaseModel


# 分页查询Schema
class AiModelQuery(BaseModel):
    page: int = 1 # 页码
    pageSize: int = 20 # 每页条数
    provider: Optional[str] = None # 提供商
    is_enabled: Optional[bool] = None # 是否启用


# 创建Schema
class AiModelCreate(BaseModel):
    model_name: str # 模型名称
    model_code: str # 模型代码
    provider: str # 提供商
    api_url: str # API地址
    api_key: str # API Key
    is_enabled: bool = True # 是否启用
    description: Optional[str] = None # 描述


# 更新Schema
class AiModelUpdate(BaseModel):
    id: int # ID
    model_name: Optional[str] = None # 模型名称
    model_code: Optional[str] = None # 模型代码
    provider: Optional[str] = None # 提供商
    api_url: Optional[str] = None # API地址
    api_key: Optional[str] = None # API Key
    is_enabled: Optional[bool] = None # 是否启用
    description: Optional[str] = None # 描述
