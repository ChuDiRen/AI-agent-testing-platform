from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiMeta(SQLModel, table=True): # API元数据表
    __tablename__ = "t_api_meta"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(description='项目ID')
    mate_name: Optional[str] = Field(default=None, max_length=255)
    object_url: Optional[str] = Field(default=None, max_length=255)
    file_type: Optional[str] = Field(default=None, max_length=255)
    create_time: Optional[datetime] = None