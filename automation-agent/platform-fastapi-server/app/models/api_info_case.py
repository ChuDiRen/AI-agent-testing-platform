"""
API 测试用例信息模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiInfoCase(Base):
    """API 测试用例信息表"""
    __tablename__ = "t_api_info_case"
    
    id = Column(Integer, primary_key=True, comment='API用例编号', autoincrement=True)
    project_id = Column(Integer, comment='项目ID')
    module_id = Column(Integer, comment='模块ID')
    case_name = Column(String(255), comment='用例名称')
    case_desc = Column(String(255), comment='用例描述')
    param_data = Column(String(255), comment='调试变量')
    pre_request = Column(String(255), comment='执行前事件')
    post_request = Column(String(255), comment='执行后事件')
    debug_info = Column(String(255), comment='调试信息')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
