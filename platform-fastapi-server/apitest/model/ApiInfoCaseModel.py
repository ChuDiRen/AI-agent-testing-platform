from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiInfoCase(SQLModel, table=True):
    """API用例信息表"""
    __tablename__ = "t_api_info_case"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='用例ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    case_name: str = Field(max_length=255, description='用例名称')
    case_desc: Optional[str] = Field(default=None, description='用例描述')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    modify_time: Optional[datetime] = Field(default_factory=datetime.now, description='修改时间')

