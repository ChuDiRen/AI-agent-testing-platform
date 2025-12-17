"""
接口目录模型
支持多级目录结构，接口分组管理
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiFolder(SQLModel, table=True):
    """接口目录表"""
    __tablename__ = "t_api_folder"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='目录ID')
    project_id: int = Field(description='所属项目ID')
    parent_id: int = Field(default=0, description='父目录ID，0表示根目录')
    folder_name: str = Field(max_length=255, description='目录名称')
    folder_desc: Optional[str] = Field(default=None, max_length=500, description='目录描述')
    folder_icon: Optional[str] = Field(default=None, max_length=100, description='目录图标')
    sort_order: int = Field(default=0, description='排序顺序')
    is_expanded: int = Field(default=1, description='是否展开(1是/0否)')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
