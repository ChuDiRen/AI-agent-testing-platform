from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Text


class WebCase(SQLModel, table=True):
    """Web用例表"""
    __tablename__ = "t_web_case"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='用例ID')
    name: str = Field(max_length=200, description='用例名称')
    description: Optional[str] = Field(default=None, max_length=1000, description='用例描述')
    project_id: int = Field(description='项目ID')
    folder_id: Optional[int] = Field(default=None, description='目录ID')
    priority: str = Field(default='medium', max_length=20, description='优先级：high/medium/low')
    status: str = Field(default='active', max_length=20, description='状态：active/inactive')
    tags: Optional[str] = Field(default=None, max_length=500, description='标签，逗号分隔')
    pre_condition: Optional[str] = Field(default=None, max_length=2000, description='前置条件')
    post_condition: Optional[str] = Field(default=None, max_length=2000, description='后置条件')
    steps: Optional[str] = Field(default=None, description='测试步骤JSON')
    content: Optional[str] = Field(default=None, description='YAML内容')
    file_type: str = Field(default='yaml', max_length=20, description='文件类型：yaml/excel')
    expected_result: Optional[str] = Field(default=None, max_length=2000, description='预期结果')
    author: Optional[str] = Field(default=None, max_length=100, description='作者')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_by: Optional[int] = Field(default=None, description='更新人ID')
    sort_order: int = Field(default=0, description='排序号')


class WebCaseFolder(SQLModel, table=True):
    """Web用例目录表"""
    __tablename__ = "t_web_case_folder"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='目录ID')
    name: str = Field(max_length=100, description='目录名称')
    project_id: int = Field(description='项目ID')
    parent_id: Optional[int] = Field(default=None, description='父目录ID')
    level: int = Field(default=1, description='层级')
    path: Optional[str] = Field(default=None, max_length=500, description='路径')
    description: Optional[str] = Field(default=None, max_length=500, description='描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
    create_by: Optional[int] = Field(default=None, description='创建人ID')
    update_by: Optional[int] = Field(default=None, description='更新人ID')
    sort_order: int = Field(default=0, description='排序号')
