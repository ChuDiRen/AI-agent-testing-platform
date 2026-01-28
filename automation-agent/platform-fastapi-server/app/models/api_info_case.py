"""
API 测试用例信息模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiInfoCase(Base):
    """API 测试用例信息表"""
    __tablename__ = "t_api_info_case"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目ID')
    module_id = Column(Integer, nullable=True, index=True, comment='模块ID')
    api_info_id = Column(Integer, ForeignKey('t_api_info.id', ondelete='SET NULL'), nullable=True, index=True, comment='关联API信息ID')
    case_name = Column(String(100), nullable=False, comment='用例名称')
    case_desc = Column(String(500), nullable=True, comment='用例描述')
    priority = Column(SmallInteger, nullable=False, default=2, index=True, comment='优先级(1高/2中/3低)')
    status = Column(SmallInteger, nullable=False, default=1, index=True, comment='状态(1启用/0禁用)')
    param_data = Column(JSON, nullable=True, comment='调试变量(JSON格式)')
    pre_request = Column(JSON, nullable=True, comment='执行前事件(JSON格式)')
    post_request = Column(JSON, nullable=True, comment='执行后事件(JSON格式)')
    assertions = Column(JSON, nullable=True, comment='断言配置(JSON格式)')
    debug_info = Column(JSON, nullable=True, comment='调试信息(JSON格式)')
    
    # 关系
    project = relationship("ApiProject", backref="test_cases")
    api_info = relationship("ApiInfo", backref="test_cases")
    
    __table_args__ = (
        Index('idx_case_project_module', 'project_id', 'module_id'),
        Index('idx_case_project_status', 'project_id', 'status'),
        Index('idx_case_priority_status', 'priority', 'status'),
        {'comment': 'API测试用例表'}
    )
