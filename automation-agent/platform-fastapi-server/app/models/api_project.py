"""
API 项目模型
"""
from sqlalchemy import Column, String
from app.db.base import Base


class ApiProject(Base):
    """API 项目表"""
    __tablename__ = "t_api_project"
    
    project_name = Column(String(255), comment='项目名称')
    project_desc = Column(String(500), comment='项目描述')
