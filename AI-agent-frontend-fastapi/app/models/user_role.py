"""用户角色关联表模型 - 完全按照博客 t_user_role 表结构设计"""
from sqlalchemy import Table, Column, BigInteger
from app.core.database import Base

t_user_role = Table(
    't_user_role',
    Base.metadata,
    Column('user_id', BigInteger, nullable=False, comment="用户ID"),
    Column('role_id', BigInteger, nullable=False, comment="角色ID"),
)
