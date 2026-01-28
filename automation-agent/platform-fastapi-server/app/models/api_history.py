"""
API 历史记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, SmallInteger, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiHistory(Base):
    """API 历史记录表"""
    __tablename__ = "t_api_history"
    
    collection_id = Column(Integer, ForeignKey('t_api_collection_info.id', ondelete='SET NULL'), nullable=True, index=True, comment='集合信息ID')
    executor_id = Column(Integer, ForeignKey('t_user.id', ondelete='SET NULL'), nullable=True, index=True, comment='执行人ID')
    start_time = Column(DateTime, nullable=True, comment='开始时间')
    end_time = Column(DateTime, nullable=True, comment='结束时间')
    duration = Column(Integer, nullable=True, comment='耗时(毫秒)')
    total_count = Column(Integer, nullable=False, default=0, comment='总用例数')
    pass_count = Column(Integer, nullable=False, default=0, comment='通过数')
    fail_count = Column(Integer, nullable=False, default=0, comment='失败数')
    skip_count = Column(Integer, nullable=False, default=0, comment='跳过数')
    status = Column(SmallInteger, nullable=False, default=0, index=True, comment='状态(0执行中/1完成/2失败/3取消)')
    history_desc = Column(String(255), nullable=True, comment='运行记录简述')
    history_detail = Column(JSON, nullable=True, comment='运行详细记录(JSON格式)')
    
    # 关系
    collection = relationship("ApiCollectionInfo", backref="histories")
    executor = relationship("User", backref="executed_histories")
    
    __table_args__ = (
        Index('idx_history_collection_status', 'collection_id', 'status'),
        Index('idx_history_executor', 'executor_id'),
        Index('idx_history_created', 'created_at'),
        {'comment': 'API执行历史表'}
    )
