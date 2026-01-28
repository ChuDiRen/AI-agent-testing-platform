"""
API 元数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, JSON
from app.db.base import Base


class ApiMeta(Base):
    """API 元数据表"""
    __tablename__ = "t_api_meta"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=True, index=True, comment='项目ID')
    module_id = Column(Integer, nullable=True, index=True, comment='模块ID')
    api_name = Column(String(100), nullable=True, comment='接口名称')
    request_method = Column(String(10), nullable=True, comment='请求方法')
    request_url = Column(String(500), nullable=True, comment='请求地址')
    request_params = Column(JSON, nullable=True, comment='URL参数')
    request_headers = Column(JSON, nullable=True, comment='请求头')
    debug_vars = Column(JSON, nullable=True, comment='调试参数')
    request_body_type = Column(String(20), nullable=True, comment='请求体类型')
    request_body = Column(JSON, nullable=True, comment='请求体数据')
    
    __table_args__ = (
        Index('idx_api_meta_project', 'project_id'),
        {'comment': 'API元数据表'}
    )
