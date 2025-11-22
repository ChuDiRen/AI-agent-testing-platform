from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiKeyWord(SQLModel, table=True): # API关键字表
    __tablename__ = "t_api_keyword"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, description='关键字名称')
    keyword_desc: str = Field(max_length=255, description='关键字描述')
    operation_type_id: int = Field(description='操作类型ID')
    keyword_fun_name: str = Field(max_length=255, description='方法名')
    keyword_value: str = Field(max_length=255, description='方法体')
    is_enabled: str = Field(max_length=255, description='是否启动')
    create_time: Optional[datetime] = None