from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WebCaseStep(BaseModel):
    """Web用例步骤Schema"""
    step_no: int = Field(..., description='步骤序号')
    action: str = Field(..., description='动作类型')
    element_name: Optional[str] = Field(None, description='元素名称')
    locator_type: Optional[str] = Field(None, description='定位器类型')
    locator_value: Optional[str] = Field(None, description='定位器值')
    input_value: Optional[str] = Field(None, description='输入值')
    expected_result: Optional[str] = Field(None, description='预期结果')
    wait_time: Optional[int] = Field(None, description='等待时间')
    description: Optional[str] = Field(None, description='步骤描述')


class WebCaseBase(BaseModel):
    """Web用例基础Schema"""
    name: str = Field(..., max_length=200, description='用例名称')
    description: Optional[str] = Field(None, max_length=1000, description='用例描述')
    project_id: int = Field(..., description='项目ID')
    folder_id: Optional[int] = Field(None, description='目录ID')
    priority: str = Field(default='medium', max_length=20, description='优先级')
    status: str = Field(default='active', max_length=20, description='状态')
    tags: Optional[str] = Field(None, max_length=500, description='标签')
    pre_condition: Optional[str] = Field(None, max_length=2000, description='前置条件')
    post_condition: Optional[str] = Field(None, max_length=2000, description='后置条件')
    expected_result: Optional[str] = Field(None, max_length=2000, description='预期结果')
    content: Optional[str] = Field(None, description='YAML内容')
    file_type: str = Field(default='yaml', max_length=20, description='文件类型')
    author: Optional[str] = Field(None, max_length=100, description='作者')
    sort_order: int = Field(default=0, description='排序号')


class WebCaseCreate(WebCaseBase):
    """创建Web用例Schema"""
    steps: List[WebCaseStep] = Field(default=[], description='测试步骤')


class WebCaseUpdate(BaseModel):
    """更新Web用例Schema"""
    name: Optional[str] = Field(None, max_length=200, description='用例名称')
    description: Optional[str] = Field(None, max_length=1000, description='用例描述')
    folder_id: Optional[int] = Field(None, description='目录ID')
    priority: Optional[str] = Field(None, max_length=20, description='优先级')
    status: Optional[str] = Field(None, max_length=20, description='状态')
    tags: Optional[str] = Field(None, max_length=500, description='标签')
    pre_condition: Optional[str] = Field(None, max_length=2000, description='前置条件')
    post_condition: Optional[str] = Field(None, max_length=2000, description='后置条件')
    expected_result: Optional[str] = Field(None, max_length=2000, description='预期结果')
    content: Optional[str] = Field(None, description='YAML内容')
    file_type: Optional[str] = Field(None, max_length=20, description='文件类型')
    author: Optional[str] = Field(None, max_length=100, description='作者')
    sort_order: Optional[int] = Field(None, description='排序号')
    steps: Optional[List[WebCaseStep]] = Field(None, description='测试步骤')


class WebCaseQuery(BaseModel):
    """查询Web用例Schema"""
    page: int = Field(default=1, description='页码')
    pageSize: int = Field(default=10, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    folder_id: Optional[int] = Field(None, description='目录ID')
    name: Optional[str] = Field(None, description='用例名称')
    status: Optional[str] = Field(None, description='状态')
    priority: Optional[str] = Field(None, description='优先级')
    author: Optional[str] = Field(None, description='作者')
    tags: Optional[str] = Field(None, description='标签')


class WebCaseResponse(WebCaseBase):
    """Web用例响应Schema"""
    id: int
    steps: Optional[List[WebCaseStep]] = []
    content: Optional[str] = None
    file_type: str = 'yaml'
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_by: Optional[int] = None

    class Config:
        from_attributes = True


class WebCaseFolderBase(BaseModel):
    """Web用例目录基础Schema"""
    name: str = Field(..., max_length=100, description='目录名称')
    project_id: int = Field(..., description='项目ID')
    parent_id: Optional[int] = Field(None, description='父目录ID')
    description: Optional[str] = Field(None, max_length=500, description='描述')
    sort_order: int = Field(default=0, description='排序号')


class WebCaseFolderCreate(WebCaseFolderBase):
    """创建Web用例目录Schema"""
    pass


class WebCaseFolderUpdate(BaseModel):
    """更新Web用例目录Schema"""
    name: Optional[str] = Field(None, max_length=100, description='目录名称')
    parent_id: Optional[int] = Field(None, description='父目录ID')
    description: Optional[str] = Field(None, max_length=500, description='描述')
    sort_order: Optional[int] = Field(None, description='排序号')


class WebCaseFolderResponse(WebCaseFolderBase):
    """Web用例目录响应Schema"""
    id: int
    level: int
    path: Optional[str] = None
    children_count: int = 0
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    create_by: Optional[int] = None
    update_by: Optional[int] = None

    class Config:
        from_attributes = True


class WebCaseTreeNode(BaseModel):
    """Web用例树节点Schema"""
    id: int
    name: str
    type: str = Field(..., description='类型：folder/case')
    parent_id: Optional[int] = None
    level: int = 1
    project_id: int
    children: List['WebCaseTreeNode'] = []
    case_info: Optional[WebCaseResponse] = None
    folder_info: Optional[WebCaseFolderResponse] = None

    class Config:
        from_attributes = True


# 解决前向引用
WebCaseTreeNode.model_rebuild()


class BatchDeleteRequest(BaseModel):
    """批量删除请求Schema"""
    ids: List[int] = Field(..., description='ID列表')


class XMindImportRequest(BaseModel):
    """XMind导入请求Schema"""
    project_id: int = Field(..., description='项目ID')
    folder_id: Optional[int] = Field(None, description='目标目录ID')
    overwrite: bool = Field(default=False, description='是否覆盖已存在的用例')
