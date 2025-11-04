from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiPlanCase(SQLModel, table=True):
    """测试计划用例关联表"""
    __tablename__ = "t_api_plan_case"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='关联ID')
    plan_id: int = Field(description='测试计划ID')
    case_info_id: int = Field(description='用例ID')
    run_order: int = Field(default=0, description='执行顺序')
    ddt_data: Optional[str] = Field(default=None, description='数据驱动JSON（数组格式）')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')

