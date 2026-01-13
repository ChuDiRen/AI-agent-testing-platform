"""
API 信息 Schema 模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class ApiInfoBase(BaseModel):
    """API 信息基础模型"""
    project_id: int = Field(..., description="项目ID")
    module_id: Optional[int] = None
    api_name: str = Field(..., description="接口名称")
    request_method: str = Field(..., description="请求方法")
    request_url: str = Field(..., description="请求地址")


class ApiInfoCreate(ApiInfoBase):
    """创建 API 信息"""
    request_params: Optional[str] = None
    request_headers: Optional[str] = None
    debug_vars: Optional[str] = None
    request_form_datas: Optional[str] = None
    request_www_form_datas: Optional[str] = None
    requests_json_data: Optional[str] = None
    request_files: Optional[str] = None


class ApiInfoUpdate(BaseModel):
    """更新 API 信息"""
    api_name: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    request_params: Optional[str] = None
    request_headers: Optional[str] = None


class ApiInfoResponse(ApiInfoBase):
    """API 信息响应模型"""
    id: int
    create_time: str
    
    class Config:
        from_attributes = True


class ApiInfoQuery(BaseModel):
    """API 信息查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    api_name: Optional[str] = None
