"""
API 集合信息模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiCollectionInfo(Base):
    """API 集合信息表"""
    __tablename__ = "t_api_collection_info"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目ID')
    collection_name = Column(String(100), nullable=False, comment='测试集合名称')
    collection_desc = Column(String(500), nullable=True, comment='测试集合描述')
    collection_env = Column(JSON, nullable=True, comment='测试集合全局变量(JSON格式)')
    status = Column(SmallInteger, nullable=False, default=1, index=True, comment='状态(1启用/0禁用)')
    
    # 关系
    project = relationship("ApiProject", backref="collections")
    
    __table_args__ = (
        Index('idx_collection_project_status', 'project_id', 'status'),
        {'comment': 'API测试集合表'}
    )
