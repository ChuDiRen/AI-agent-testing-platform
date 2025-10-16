from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiInfo(SQLModel, table=True): # API接口信息表
    __tablename__ = "t_api_info"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='接口编号')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    api_name: Optional[str] = Field(default=None, max_length=255, description='接口名称')
    request_method: Optional[str] = Field(default=None, max_length=255, description='请求方法')
    request_url: Optional[str] = Field(default=None, max_length=255, description='请求地址')
    request_params: Optional[str] = Field(default=None, description='URL参数')
    request_headers: Optional[str] = Field(default=None, description='请求头')
    debug_vars: Optional[str] = Field(default=None, description='调试参数')
    request_form_datas: Optional[str] = Field(default=None, description='form-data')
    request_www_form_datas: Optional[str] = Field(default=None, description='www-form-data')
    requests_json_data: Optional[str] = Field(default=None, description='json数据')
    request_files: Optional[str] = Field(default=None, description='json数据')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
