"""角色数据库模型 - 完全按照博客 t_role 表结构设计"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(Base):
    """角色表模型 - 对应博客 t_role 表"""
    __tablename__ = "t_role"

    role_id = Column(Integer, primary_key=True, autoincrement=True, comment="角色ID")  # SQLite使用INTEGER支持自增
    role_name = Column(String(10), nullable=False, comment="角色名称")
    remark = Column(String(100), nullable=True, comment="角色描述")
    create_time = Column(DateTime, nullable=False, comment="创建时间")
    modify_time = Column(DateTime, nullable=True, comment="修改时间")
    
    # 关联关系
    users = relationship("User", secondary="t_user_role", back_populates="roles")
    menus = relationship("Menu", secondary="t_role_menu", back_populates="roles")
    
    def __repr__(self):
        return f"<Role(role_id={self.role_id}, role_name={self.role_name})>"

