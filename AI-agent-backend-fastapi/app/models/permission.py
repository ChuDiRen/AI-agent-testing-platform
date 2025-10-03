"""权限数据库模型"""
from sqlalchemy import Column, BigInteger, String, DateTime, CHAR
from datetime import datetime
from app.core.database import Base


class Permission(Base):
    """权限表模型"""
    __tablename__ = "t_permission"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="权限ID")
    code = Column(String(50), nullable=False, unique=True, comment="权限代码")
    name = Column(String(100), nullable=False, comment="权限名称")
    description = Column(String(200), nullable=True, comment="权限描述")
    resource = Column(String(200), nullable=True, comment="资源路径")
    action = Column(String(50), nullable=True, comment="操作动作")
    status = Column(CHAR(1), nullable=False, default='1', comment="状态 0禁用 1启用")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    modify_time = Column(DateTime, nullable=True, comment="修改时间")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, name={self.name})>"
