"""
API 测试用例步骤信息模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base
from datetime import datetime


class ApiInfoCaseStep(Base):
    """API 测试用例步骤信息表"""
    __tablename__ = "t_api_info_step"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_case_info_id = Column(Integer, comment='用例的ID')
    key_word_id = Column(Integer, comment='关键字方法ID')
    step_desc = Column(String(255), comment='步骤描述')
    ref_variable = Column(String(255), comment='引用变量')
    run_order = Column(Integer, comment='步骤的顺序')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
