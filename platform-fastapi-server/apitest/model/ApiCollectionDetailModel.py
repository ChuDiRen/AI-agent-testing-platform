from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import SQLModel, Field


class ApiCollectionDetail(SQLModel, table=True):
    """测试集合详情表"""
    __tablename__ = "t_api_collection_detail"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='关联ID')
    collection_info_id: int = Field(description='测试集合ID')
    case_info_id: int = Field(description='用例ID')
    run_order: int = Field(default=0, description='执行顺序')
    ddt_data: Optional[str] = Field(default=None, sa_column=Column(Text), description='数据驱动JSON（数组格式）')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')

