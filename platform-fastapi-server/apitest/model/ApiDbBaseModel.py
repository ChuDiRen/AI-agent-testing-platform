from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiDbBase(SQLModel, table=True): # API数据库配置表
    __tablename__ = "t_api_database"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(description='项目ID')
    name: str = Field(max_length=255, description='连接名')
    ref_name: str = Field(max_length=255, description='引用变量')
    db_type: str = Field(max_length=255, description='数据库类型')
    db_info: str = Field(max_length=255, description='数据库连接信息')
    is_enabled: str = Field(max_length=255, description='是否启用')
    create_time: Optional[datetime] = None