"""
API 集合详情模型
"""
from sqlalchemy import Column, Integer, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiCollectionDetail(Base):
    """API 集合详情表"""
    __tablename__ = "t_api_collection_detail"
    
    collection_id = Column(Integer, ForeignKey('t_api_collection_info.id', ondelete='CASCADE'), nullable=False, index=True, comment='集合信息ID')
    api_case_id = Column(Integer, ForeignKey('t_api_info_case.id', ondelete='CASCADE'), nullable=False, index=True, comment='测试用例ID')
    run_order = Column(Integer, nullable=False, default=0, comment='执行顺序')
    is_enabled = Column(Boolean, nullable=False, default=True, comment='是否启用')
    
    # 关系
    collection = relationship("ApiCollectionInfo", backref="details")
    test_case = relationship("ApiInfoCase", backref="collection_details")
    
    __table_args__ = (
        UniqueConstraint('collection_id', 'api_case_id', name='uq_collection_case'),
        Index('idx_detail_collection_order', 'collection_id', 'run_order'),
        {'comment': 'API集合详情表'}
    )
