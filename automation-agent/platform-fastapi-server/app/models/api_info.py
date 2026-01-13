"""
API 信息模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base


class ApiInfo(Base):
    """API 信息表"""
    __tablename__ = "t_api_info"
    
    project_id = Column(Integer, comment='项目ID')
    module_id = Column(Integer, comment='模块ID')
    api_name = Column(String(255), comment='接口名称')
    request_method = Column(String(255), comment='请求方法')
    request_url = Column(String(255), comment='请求地址')
    request_params = Column(String(255), comment='URL参数')
    request_headers = Column(Text, comment='请求头')
    debug_vars = Column(Text, comment='调试参数')
    request_form_datas = Column(String(255), comment='form-data')
    request_www_form_datas = Column(String(255), comment='www-form-data')
    requests_json_data = Column(String(255), comment='json数据')
    request_files = Column(String(255), comment='文件列表')
