from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiInfoGroup(SQLModel, table=True): # API接口分组表
    __tablename__ = "t_api_info_group"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='分组编号')
    project_id: int = Field(description='项目ID')
    group_name: str = Field(max_length=255, description='分组名称')
    group_desc: Optional[str] = Field(default=None, max_length=500, description='分组描述')
    parent_id: int = Field(default=0, description='父分组ID，0表示顶级分组')
    order_num: int = Field(default=0, description='排序')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')
