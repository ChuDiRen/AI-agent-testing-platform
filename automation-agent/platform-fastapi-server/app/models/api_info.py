"""
API 信息模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiInfo(Base):
    """API 信息表"""
    __tablename__ = "t_api_info"
    
    project_id = Column(Integer, ForeignKey('t_api_project.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目ID')
    module_id = Column(Integer, nullable=True, index=True, comment='模块ID')
    api_name = Column(String(100), nullable=False, comment='接口名称')
    request_method = Column(String(10), nullable=False, index=True, comment='请求方法(GET/POST/PUT/DELETE等)')
    request_url = Column(String(500), nullable=False, comment='请求地址')
    request_params = Column(JSON, nullable=True, comment='URL参数(JSON格式)')
    request_headers = Column(JSON, nullable=True, comment='请求头(JSON格式)')
    debug_vars = Column(JSON, nullable=True, comment='调试参数(JSON格式)')
    request_body_type = Column(String(20), nullable=True, comment='请求体类型(form-data/json/www-form/files)')
    request_body = Column(JSON, nullable=True, comment='请求体数据(JSON格式)')
    
    # 关系
    project = relationship("ApiProject", backref="api_infos")
    
    __table_args__ = (
        Index('idx_api_info_project_module', 'project_id', 'module_id'),
        Index('idx_api_info_project_method', 'project_id', 'request_method'),
        {'comment': 'API信息表'}
    )
