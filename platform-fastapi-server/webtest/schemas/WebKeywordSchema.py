from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class WebKeywordParam(BaseModel):
    """Web关键字参数Schema"""
    name: str = Field(..., description='参数名称')
    type: str = Field(..., description='参数类型')
    required: bool = Field(default=True, description='是否必需')
    default_value: Optional[str] = Field(None, description='默认值')
    description: Optional[str] = Field(None, description='参数描述')


class WebKeywordBase(BaseModel):
    """Web关键字基础Schema"""
    name: str = Field(..., max_length=100, description='关键字名称')
    display_name: str = Field(..., max_length=100, description='显示名称')
    description: Optional[str] = Field(None, max_length=500, description='关键字描述')
    category: Literal['action', 'assertion', 'util'] = Field(default='action', description='分类')
    params: Optional[List[WebKeywordParam]] = Field(default=[], description='参数定义')
    return_type: Optional[str] = Field(None, max_length=100, description='返回类型')
    code_template: str = Field(..., description='代码模板')
    python_code: Optional[str] = Field(None, description='Python实现代码')
    is_builtin: bool = Field(default=False, description='是否内置关键字')
    is_active: bool = Field(default=True, description='是否启用')
    author: Optional[str] = Field(None, max_length=100, description='作者')
    version: str = Field(default='1.0', max_length=20, description='版本号')


class WebKeywordCreate(WebKeywordBase):
    """创建Web关键字Schema"""
    pass


class WebKeywordUpdate(BaseModel):
    """更新Web关键字Schema"""
    display_name: Optional[str] = Field(None, max_length=100, description='显示名称')
    description: Optional[str] = Field(None, max_length=500, description='关键字描述')
    category: Optional[Literal['action', 'assertion', 'util']] = Field(None, description='分类')
    params: Optional[List[WebKeywordParam]] = Field(None, description='参数定义')
    return_type: Optional[str] = Field(None, max_length=100, description='返回类型')
    code_template: Optional[str] = Field(None, description='代码模板')
    python_code: Optional[str] = Field(None, description='Python实现代码')
    author: Optional[str] = Field(None, max_length=100, description='作者')
    version: Optional[str] = Field(None, max_length=20, description='版本号')


class WebKeywordQuery(BaseModel):
    """查询Web关键字Schema"""
    page: int = Field(default=1, description='页码')
    pageSize: int = Field(default=10, description='每页数量')
    name: Optional[str] = Field(None, description='关键字名称')
    category: Optional[str] = Field(None, description='分类')
    is_builtin: Optional[bool] = Field(None, description='是否内置关键字')
    is_active: Optional[bool] = Field(None, description='是否启用')
    author: Optional[str] = Field(None, description='作者')


class WebKeywordResponse(WebKeywordBase):
    """Web关键字响应Schema"""
    id: int
    is_builtin: bool
    is_active: bool
    usage_count: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_by: Optional[int] = None

    class Config:
        from_attributes = True


class WebKeywordGenerateRequest(BaseModel):
    """Web关键字文件生成请求Schema"""
    keyword_ids: List[int] = Field(..., description='关键字ID列表')
    file_format: Literal['python', 'java', 'javascript'] = Field(default='python', description='文件格式')
    include_builtin: bool = Field(default=False, description='是否包含内置关键字')


class WebKeywordGenerateResponse(BaseModel):
    """Web关键字文件生成响应Schema"""
    file_name: str
    file_content: str
    file_size: int
    generate_time: datetime


class WebKeywordImport(BaseModel):
    """Web关键字导入Schema"""
    overwrite: bool = Field(default=False, description='是否覆盖已存在的关键字')
    keywords: List[WebKeywordCreate] = Field(..., description='关键字列表')


class WebKeywordExport(BaseModel):
    """Web关键字导出Schema"""
    ids: Optional[List[int]] = Field(None, description='要导出的关键字ID列表，为空则导出所有')
    format: str = Field(default='json', description='导出格式：json/csv/excel')
    include_code: bool = Field(default=True, description='是否包含代码')


class WebKeywordValidation(BaseModel):
    """Web关键字验证Schema"""
    keyword_id: int
    code: str
    validation_result: Literal['valid', 'invalid', 'error']
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class WebKeywordTestRequest(BaseModel):
    """Web关键字测试请求Schema"""
    keyword_id: int
    test_params: Dict[str, Any] = Field(default={}, description='测试参数')
    browser_type: str = Field(default='chrome', description='测试浏览器')


class WebKeywordTestResponse(BaseModel):
    """Web关键字测试响应Schema"""
    keyword_id: int
    test_result: Literal['passed', 'failed', 'error']
    execution_time: float
    error_message: Optional[str] = None
    return_value: Optional[Any] = None
    screenshot_path: Optional[str] = None
