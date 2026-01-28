"""
API 关键字模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiKeyWord(Base):
    """API 关键字表"""
    __tablename__ = "t_api_keyword"
    
    name = Column(String(100), nullable=False, comment='关键字名称')
    keyword_desc = Column(String(255), nullable=True, comment='关键字描述')
    operation_type_id = Column(Integer, ForeignKey('t_api_operation_type.id', ondelete='SET NULL'), nullable=True, index=True, comment='操作类型ID')
    keyword_fun_name = Column(String(100), nullable=False, comment='方法名')
    keyword_value = Column(Text, nullable=True, comment='方法体')
    is_enabled = Column(Boolean, nullable=False, default=True, index=True, comment='是否启用')
    page_id = Column(Integer, nullable=True, index=True, comment='页面ID')
    
    # 关系
    operation_type = relationship("ApiOperationType", backref="keywords")
    
    __table_args__ = (
        Index('idx_keyword_type_enabled', 'operation_type_id', 'is_enabled'),
        Index('idx_keyword_page', 'page_id'),
        {'comment': 'API关键字表'}
    )
