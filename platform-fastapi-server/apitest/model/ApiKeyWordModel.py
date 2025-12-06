from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import SQLModel, Field


class ApiKeyWord(SQLModel, table=True): # API关键字表
    __tablename__ = "t_api_keyword"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, description='关键字名称')
    keyword_desc: str = Field(default="", sa_column=Column(Text), description='关键字描述(JSON格式的参数定义)')
    operation_type_id: int = Field(description='操作类型ID')
    keyword_fun_name: str = Field(max_length=255, description='方法名')
    keyword_value: str = Field(default="", sa_column=Column(Text), description='方法体代码')
    is_enabled: str = Field(max_length=10, default="1", description='是否启用: 1-启用, 0-禁用')
    plugin_id: Optional[int] = Field(default=None, description='关联的执行引擎插件ID')
    plugin_code: Optional[str] = Field(default=None, max_length=50, description='关联的执行引擎插件代码')
    category: Optional[str] = Field(default=None, max_length=100, description='关键字分类')
    create_time: Optional[datetime] = None