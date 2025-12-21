from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class ApiInfoCase(SQLModel, table=True):
    """API用例信息表"""
    __tablename__ = "t_api_info_case"
    
    id: Optional[int] = Field(default=None, primary_key=True, description='用例ID')
    project_id: Optional[int] = Field(default=None, description='项目ID')
    api_id: Optional[int] = Field(default=None, description='关联的接口ID')
    case_name: str = Field(max_length=255, description='用例名称')
    case_desc: Optional[str] = Field(default=None, description='用例描述')
    context_config: Optional[str] = Field(default=None, description='全局配置JSON（调试变量）')
    ddts: Optional[str] = Field(default=None, description='数据驱动JSON')
    pre_request: Optional[str] = Field(default=None, description='执行前事件脚本（Python代码）')
    post_request: Optional[str] = Field(default=None, description='执行后事件脚本（Python代码）')
    debug_info: Optional[str] = Field(default=None, description='调试信息')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, description='更新时间')

