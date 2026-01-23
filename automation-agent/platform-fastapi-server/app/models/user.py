"""
用户模型
扩展后的用户表，支持RBAC权限系统
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import bcrypt
from datetime import datetime


class User(Base):
    """用户表"""
    __tablename__ = "t_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment='主键ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    alias = Column(String(50), nullable=True, comment='用户昵称/别名')
    password = Column(String(255), nullable=False, comment='密码（bcrypt加密）')
    email = Column(String(100), nullable=True, comment='邮箱')
    phone = Column(String(20), nullable=True, comment='手机号')
    is_active = Column(Boolean, default=True, nullable=False, comment='是否激活')
    is_superuser = Column(Boolean, default=False, nullable=False, comment='是否超级管理员')
    dept_id = Column(Integer, ForeignKey('t_dept.id'), nullable=True, comment='所属部门ID')
    last_login = Column(DateTime, nullable=True, comment='最后登录时间')
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    
    # 关系
    dept = relationship("Dept", back_populates="users", foreign_keys="User.dept_id")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """设置密码（加密）"""
        self.password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password.encode("utf-8")
        )
