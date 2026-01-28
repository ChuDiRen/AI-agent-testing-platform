"""
API 测试计划图表模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiTestPlanChart(Base):
    """API 测试计划图表表"""
    __tablename__ = "t_api_test_plan_chart"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目ID')
    chart_name = Column(String(100), nullable=False, comment='图表名称')
    chart_type = Column(String(50), nullable=False, index=True, comment='图表类型(line/bar/pie等)')
    chart_data = Column(JSON, nullable=True, comment='图表数据(JSON格式)')
    chart_config = Column(JSON, nullable=True, comment='图表配置(JSON格式)')
    
    # 关系
    project = relationship("ApiProject", backref="charts")
    
    __table_args__ = (
        Index('idx_chart_project_type', 'project_id', 'chart_type'),
        {'comment': 'API测试计划图表表'}
    )
