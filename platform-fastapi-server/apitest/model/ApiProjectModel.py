from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiProject(SQLModel, table=True): # API项目表
    __tablename__ = "t_api_project"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str = Field(max_length=255, description='项目名称')
    project_desc: str = Field(max_length=255, description='项目描述')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')