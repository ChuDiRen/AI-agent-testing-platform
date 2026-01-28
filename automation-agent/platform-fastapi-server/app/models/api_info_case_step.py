"""
API 测试用例步骤信息模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiInfoCaseStep(Base):
    """API 测试用例步骤信息表"""
    __tablename__ = "t_api_info_step"
    
    api_case_id = Column(Integer, ForeignKey('t_api_info_case.id', ondelete='CASCADE'), nullable=False, index=True, comment='用例ID')
    keyword_id = Column(Integer, ForeignKey('t_api_keyword.id', ondelete='SET NULL'), nullable=True, index=True, comment='关键字方法ID')
    step_order = Column(Integer, nullable=False, default=0, comment='步骤顺序')
    step_desc = Column(String(255), nullable=True, comment='步骤描述')
    step_params = Column(JSON, nullable=True, comment='步骤参数(JSON格式)')
    ref_variable = Column(String(255), nullable=True, comment='引用变量')
    
    # 关系
    test_case = relationship("ApiInfoCase", backref="steps")
    keyword = relationship("ApiKeyWord", backref="used_steps")
    
    __table_args__ = (
        Index('idx_step_case_order', 'api_case_id', 'step_order'),
        {'comment': 'API测试用例步骤表'}
    )
