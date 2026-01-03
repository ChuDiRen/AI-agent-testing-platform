from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field


class RequestMethodEnum(str, Enum):
    """请求方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiInfo(SQLModel, table=True): # API接口信息表
    __tablename__ = "t_api_info"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='接口编号')
    project_id: Optional[int] = Field(default=None, description='项目ID', ge=1)
    environment_id: Optional[int] = Field(default=None, description='环境ID', ge=1)
    folder_id: int = Field(default=0, description='所属目录ID，0表示根目录', ge=0)
    api_name: Optional[str] = Field(default=None, max_length=255, description='接口名称')
    api_desc: Optional[str] = Field(default=None, max_length=1000, description='接口描述')
    request_method: Optional[str] = Field(default=None, max_length=10, description='请求方法')
    request_url: Optional[str] = Field(default=None, max_length=500, description='请求地址')
    request_params: Optional[str] = Field(default=None, description='URL参数')
    request_headers: Optional[str] = Field(default=None, description='请求头')
    debug_vars: Optional[str] = Field(default=None, description='调试参数')
    request_form_datas: Optional[str] = Field(default=None, description='form-data')
    request_www_form_datas: Optional[str] = Field(default=None, description='www-form-data')
    requests_json_data: Optional[str] = Field(default=None, description='json数据')
    request_files: Optional[str] = Field(default=None, description='json数据')
    sort_order: int = Field(default=0, description='排序顺序', ge=0)
    status: int = Field(default=1, description='状态：1-启用，0-禁用', ge=0, le=1)
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    
    class Config:
        """模型配置"""
        use_enum_values = True
        schema_extra = {
            "example": {
                "project_id": 1,
                "folder_id": 0,
                "api_name": "用户登录接口",
                "api_desc": "用于用户身份验证的登录接口",
                "request_method": "POST",
                "request_url": "/api/auth/login",
                "status": 1,
                "sort_order": 1
            }
        }
