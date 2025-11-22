from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiInfoCaseStep(SQLModel, table=True):
    """API用例步骤表"""
    __tablename__ = "t_api_info_case_step"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='步骤ID')
    case_info_id: int = Field(description='用例ID')
    run_order: int = Field(default=0, description='运行序号')
    step_desc: Optional[str] = Field(default=None, max_length=255, description='步骤描述')
    operation_type_id: Optional[int] = Field(default=None, description='操作类型ID（一级分类）')
    keyword_id: Optional[int] = Field(default=None, description='关键字ID（二级）')
    step_data: Optional[str] = Field(default=None, description='步骤数据JSON')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')

