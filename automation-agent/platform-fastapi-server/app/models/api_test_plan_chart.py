"""
API 测试计划图表模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.base import Base
from datetime import datetime


class ApiTestPlanChart(Base):
    """API 测试计划图表表"""
    __tablename__ = "t_api_test_plan_chart"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, comment='项目ID')
    chart_name = Column(String(255), comment='图表名称')
    chart_type = Column(String(255), comment='图表类型')
    chart_data = Column(Text, comment='图表数据')
    chart_config = Column(Text, comment='图表配置')
    create_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')
