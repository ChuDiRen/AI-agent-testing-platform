"""
审计日志模型
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Numeric
from app.db.base import Base
from datetime import datetime


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = "t_audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('t_user.id'), nullable=True, comment='用户ID')
    username = Column(String(50), nullable=True, comment='用户名（冗余字段，便于查询）')
    module = Column(String(50), nullable=True, comment='模块名称（如 user, role, menu）')
    summary = Column(String(200), nullable=True, comment='操作摘要')
    method = Column(String(10), nullable=True, comment='HTTP方法')
    path = Column(String(500), nullable=True, comment='请求路径')
    status = Column(Integer, default=0, nullable=False, comment='响应状态码')
    response_time = Column(Numeric(10, 2), nullable=True, comment='响应时间（毫秒）')
    request_args = Column(JSON, nullable=True, comment='请求参数（JSON格式）')
    response_body = Column(JSON, nullable=True, comment='响应体（JSON格式）')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
