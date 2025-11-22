from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiCollectionInfo(SQLModel, table=True):
    """API测试集合表"""
    __tablename__ = "t_api_collection_info"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='计划ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    plan_name: str = Field(max_length=255, description='计划名称')
    plan_desc: Optional[str] = Field(default=None, description='计划描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    modify_time: Optional[datetime] = Field(default_factory=datetime.now, description='修改时间')

