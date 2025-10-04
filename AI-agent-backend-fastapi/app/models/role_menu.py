"""角色菜单关联表模型 - 完全按照博客 t_role_menu 表结构设计"""
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.core.database import Base

t_role_menu = Table(
    't_role_menu',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('t_role.role_id'), nullable=False, comment="角色ID"),  # SQLite使用INTEGER
    Column('menu_id', Integer, ForeignKey('t_menu.menu_id'), nullable=False, comment="菜单/按钮ID"),  # SQLite使用INTEGER
)

