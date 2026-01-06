from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WebElementBase(BaseModel):
    """Web元素基础Schema"""
    name: str = Field(..., max_length=100, description='元素名称')
    description: Optional[str] = Field(None, max_length=500, description='元素描述')
    project_id: int = Field(..., description='项目ID')
    module: Optional[str] = Field(None, max_length=100, description='所属模块')
    locator_type: str = Field(..., max_length=20, description='定位器类型')
    locator_value: str = Field(..., max_length=500, description='定位器值')
    page_url: Optional[str] = Field(None, max_length=500, description='页面URL')
    frame_info: Optional[str] = Field(None, max_length=200, description='框架信息')
    wait_strategy: str = Field(default='implicit', max_length=20, description='等待策略')
    wait_timeout: int = Field(default=10, description='等待超时')
    is_dynamic: bool = Field(default=False, description='是否动态元素')
    backup_locator: Optional[str] = Field(None, max_length=500, description='备用定位器')
    status: str = Field(default='active', max_length=20, description='状态')


class WebElementCreate(WebElementBase):
    """创建Web元素Schema"""
    pass


class WebElementUpdate(BaseModel):
    """更新Web元素Schema"""
    name: Optional[str] = Field(None, max_length=100, description='元素名称')
    description: Optional[str] = Field(None, max_length=500, description='元素描述')
    module: Optional[str] = Field(None, max_length=100, description='所属模块')
    locator_type: Optional[str] = Field(None, max_length=20, description='定位器类型')
    locator_value: Optional[str] = Field(None, max_length=500, description='定位器值')
    page_url: Optional[str] = Field(None, max_length=500, description='页面URL')
    frame_info: Optional[str] = Field(None, max_length=200, description='框架信息')
    wait_strategy: Optional[str] = Field(None, max_length=20, description='等待策略')
    wait_timeout: Optional[int] = Field(None, description='等待超时')
    is_dynamic: Optional[bool] = Field(None, description='是否动态元素')
    backup_locator: Optional[str] = Field(None, max_length=500, description='备用定位器')
    status: Optional[str] = Field(None, max_length=20, description='状态')


class WebElementQuery(BaseModel):
    """查询Web元素Schema"""
    page: int = Field(default=1, description='页码')
    pageSize: int = Field(default=10, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    module: Optional[str] = Field(None, description='所属模块')
    name: Optional[str] = Field(None, description='元素名称')
    locator_type: Optional[str] = Field(None, description='定位器类型')
    status: Optional[str] = Field(None, description='状态')


class WebElementResponse(WebElementBase):
    """Web元素响应Schema"""
    id: int
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_by: Optional[int] = None

    class Config:
        from_attributes = True


class WebElementImport(BaseModel):
    """Web元素导入Schema"""
    project_id: int = Field(..., description='项目ID')
    overwrite: bool = Field(default=False, description='是否覆盖已存在的元素')
    elements: List[WebElementCreate] = Field(..., description='元素列表')


class WebElementExport(BaseModel):
    """Web元素导出Schema"""
    ids: Optional[List[int]] = Field(None, description='要导出的元素ID列表，为空则导出所有')
    format: str = Field(default='json', description='导出格式：json/csv/excel')


class ModuleElementList(BaseModel):
    """模块元素列表Schema"""
    module: str = Field(..., description='模块名称')
    elements: List[WebElementResponse] = Field(..., description='元素列表')


class BatchDeleteRequest(BaseModel):
    """批量删除请求Schema"""
    ids: List[int] = Field(..., description='ID列表')
