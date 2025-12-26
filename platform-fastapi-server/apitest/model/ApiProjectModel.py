from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiProject(SQLModel, table=True): # API项目表
    __tablename__ = "t_api_project"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='项目编号')
    project_name: str = Field(max_length=255, description='项目名称', min_length=1)
    project_desc: Optional[str] = Field(default=None, max_length=500, description='项目描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    
    class Config:
        """模型配置"""
        schema_extra = {
            "example": {
                "project_name": "测试项目",
                "project_desc": "这是一个API测试项目"
            }
        }