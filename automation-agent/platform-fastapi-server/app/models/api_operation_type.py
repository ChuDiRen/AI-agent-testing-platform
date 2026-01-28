"""
API 操作类型模型
"""
from sqlalchemy import Column, String, Boolean, Text, Index
from app.db.base import Base


class ApiOperationType(Base):
    """API 操作类型表"""
    __tablename__ = "t_api_operation_type"
    
    operation_type_name = Column(String(50), nullable=False, unique=True, comment='操作类型名称')
    operation_type_desc = Column(String(255), nullable=True, comment='操作类型描述')
    operation_type_fun_name = Column(String(100), nullable=True, comment='方法名')
    operation_type_value = Column(Text, nullable=True, comment='方法体')
    is_enabled = Column(Boolean, nullable=False, default=True, index=True, comment='是否启用')
    
    __table_args__ = (
        Index('idx_operation_type_enabled', 'is_enabled'),
        {'comment': 'API操作类型表'}
    )
