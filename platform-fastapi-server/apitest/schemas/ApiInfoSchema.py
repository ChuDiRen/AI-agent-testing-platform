from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

from ..model.ApiInfoModel import RequestMethodEnum


# 查询Schema
class ApiInfoQuery(BaseModel):
    """API信息查询参数"""
    page: int = Field(default=1, ge=1, description='页码')
    pageSize: int = Field(default=10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(default=None, ge=1, description='项目ID')
    folder_id: Optional[int] = Field(default=None, ge=0, description='目录ID')
    api_name: Optional[str] = Field(default=None, max_length=255, description='接口名称')
    request_method: Optional[str] = Field(default=None, description='请求方法')
    status: Optional[int] = Field(default=None, ge=0, le=1, description='状态')
    
    @validator('request_method')
    def validate_request_method(cls, v):
        """验证请求方法"""
        if v is not None and v not in [method.value for method in RequestMethodEnum]:
            raise ValueError('请求方法必须是有效的HTTP方法')
        return v
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "page": 1,
                "pageSize": 10,
                "project_id": 1,
                "folder_id": 0,
                "api_name": "用户",
                "request_method": "POST",
                "status": 1
            }
        }

# 创建Schema
class ApiInfoCreate(BaseModel):
    """创建API信息"""
    project_id: Optional[int] = Field(default=None, ge=1, description='项目ID')
    folder_id: Optional[int] = Field(default=0, ge=0, description='目录ID')
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
    sort_order: int = Field(default=0, ge=0, description='排序顺序')
    status: int = Field(default=1, ge=0, le=1, description='状态：1-启用，0-禁用')
    
    @validator('request_method')
    def validate_request_method(cls, v):
        """验证请求方法"""
        if v is not None and v not in [method.value for method in RequestMethodEnum]:
            raise ValueError('请求方法必须是有效的HTTP方法')
        return v
    
    class Config:
        """Schema配置"""
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

# 更新Schema
class ApiInfoUpdate(BaseModel):
    """更新API信息"""
    id: int = Field(..., ge=1, description='API信息ID')
    project_id: Optional[int] = Field(default=None, ge=1, description='项目ID')
    folder_id: Optional[int] = Field(default=None, ge=0, description='目录ID')
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
    sort_order: Optional[int] = Field(default=None, ge=0, description='排序顺序')
    status: Optional[int] = Field(default=None, ge=0, le=1, description='状态：1-启用，0-禁用')
    
    @validator('request_method')
    def validate_request_method(cls, v):
        """验证请求方法"""
        if v is not None and v not in [method.value for method in RequestMethodEnum]:
            raise ValueError('请求方法必须是有效的HTTP方法')
        return v
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "id": 1,
                "api_name": "用户登录接口（更新）",
                "api_desc": "更新后的接口描述",
                "status": 1,
                "sort_order": 2
            }
        }

# 测试执行Schema
class ApiTestExecute(BaseModel):
    """API测试执行参数"""
    api_info_id: int = Field(..., ge=1, description='API信息ID')
    test_name: Optional[str] = Field(default=None, max_length=255, description='测试名称')
    context_vars: Optional[dict] = Field(default=None, description='上下文变量')
    pre_script: Optional[str] = Field(default=None, description='前置脚本')
    post_script: Optional[str] = Field(default=None, description='后置脚本')
    assertions: Optional[list] = Field(default=None, description='断言配置')
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "api_info_id": 1,
                "test_name": "用户登录测试",
                "context_vars": {"username": "testuser", "password": "testpass"},
                "pre_script": "print('开始测试')",
                "post_script": "print('测试完成')",
                "assertions": [{"type": "status_code", "value": 200}]
            }
        }

# 响应Schema
class ApiInfoResponse(BaseModel):
    """API信息响应数据"""
    id: int = Field(..., description='接口编号')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    environment_id: Optional[int] = Field(default=None, description='环境ID')
    folder_id: int = Field(default=0, description='目录ID')
    api_name: Optional[str] = Field(default=None, description='接口名称')
    api_desc: Optional[str] = Field(default=None, description='接口描述')
    request_method: Optional[str] = Field(default=None, description='请求方法')
    request_url: Optional[str] = Field(default=None, description='请求地址')
    request_params: Optional[str] = Field(default=None, description='URL参数')
    request_headers: Optional[str] = Field(default=None, description='请求头')
    debug_vars: Optional[str] = Field(default=None, description='调试参数')
    request_form_datas: Optional[str] = Field(default=None, description='form-data')
    request_www_form_datas: Optional[str] = Field(default=None, description='www-form-data')
    requests_json_data: Optional[str] = Field(default=None, description='json数据')
    request_files: Optional[str] = Field(default=None, description='json数据')
    sort_order: int = Field(default=0, description='排序顺序')
    status: int = Field(default=1, description='状态')
    create_time: datetime = Field(default_factory=datetime.now, description='创建时间')
    update_time: datetime = Field(default_factory=datetime.now, description='更新时间')
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "folder_id": 0,
                "api_name": "用户登录接口",
                "api_desc": "用于用户身份验证的登录接口",
                "request_method": "POST",
                "request_url": "/api/auth/login",
                "status": 1,
                "sort_order": 1,
                "create_time": "2024-01-01T00:00:00",
                "update_time": "2024-01-01T00:00:00"
            }
        }

# 接口调试请求Schema
class ApiDebugRequest(BaseModel):
    """接口调试请求"""
    request_method: str = Field(..., max_length=10, description='请求方法')
    request_url: str = Field(..., max_length=500, description='请求URL')
    request_params: Optional[list] = Field(default=None, description='URL参数')
    request_headers: Optional[list] = Field(default=None, description='请求头')
    request_form_datas: Optional[list] = Field(default=None, description='form-data参数')
    request_www_form_datas: Optional[list] = Field(default=None, description='x-www-form-urlencoded参数')
    requests_json_data: Optional[str] = Field(default=None, description='JSON请求体')
    request_files: Optional[list] = Field(default=None, description='文件上传参数')
    debug_vars: Optional[list] = Field(default=None, description='调试变量')
    timeout: Optional[int] = Field(default=30, ge=1, le=300, description='超时时间（秒）')
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "request_method": "POST",
                "request_url": "/api/auth/login",
                "request_headers": [{"key": "Content-Type", "value": "application/json"}],
                "requests_json_data": '{"username": "test", "password": "123456"}',
                "timeout": 30
            }
        }

# 接口调试响应Schema
class ApiDebugResponse(BaseModel):
    """接口调试响应"""
    success: bool = Field(..., description='是否成功')
    status_code: Optional[int] = Field(default=None, ge=100, le=599, description='HTTP状态码')
    response_time: Optional[float] = Field(default=None, ge=0, description='响应时间（毫秒）')
    response_headers: Optional[dict] = Field(default=None, description='响应头')
    response_body: Optional[str] = Field(default=None, description='响应体')
    request_url: Optional[str] = Field(default=None, max_length=500, description='实际请求URL')
    request_method: Optional[str] = Field(default=None, max_length=10, description='实际请求方法')
    request_headers: Optional[dict] = Field(default=None, description='实际请求头')
    request_body: Optional[str] = Field(default=None, description='实际请求体')
    error_message: Optional[str] = Field(default=None, description='错误信息')
    
    class Config:
        """Schema配置"""
        schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "response_time": 150.5,
                "response_headers": {"Content-Type": "application/json"},
                "response_body": '{"code": 200, "message": "success"}',
                "request_url": "/api/auth/login",
                "request_method": "POST"
            }
        }
