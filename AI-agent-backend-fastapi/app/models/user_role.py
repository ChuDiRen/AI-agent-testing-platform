"""用户角色关联表模型 - 完全按照博客 t_user_role 表结构设计"""
from sqlalchemy import Table, Column, BigInteger, ForeignKey
from app.core.database import Base

# 关联表定义（用于多对多关系）
t_user_role = Table(
    't_user_role',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('t_user.user_id'), nullable=False, comment="用户ID"),
    Column('role_id', BigInteger, ForeignKey('t_role.role_id'), nullable=False, comment="角色ID"),
)


class UserRole(Base):
    """用户角色关联类 - 用于ORM操作"""
    __tablename__ = "t_user_role"
    __table_args__ = {'extend_existing': True}  # 允许扩展已存在的表

    user_id = Column(BigInteger, ForeignKey('t_user.user_id'), primary_key=True, comment="用户ID")
    role_id = Column(BigInteger, ForeignKey('t_role.role_id'), primary_key=True, comment="角色ID")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
